# Licensed under the Apache License, Version 2.0.

import math
import re

PROFILE_ID = "xq.space:profile-0.1"
RESIDUAL = "xq.space:consistency_residual"
IDENTITY = "xq.space:identity_hypothesis"
CAUSE = "xq.space:cause_hypothesis"


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(event, parse_time):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def obj(value, path):
        if not isinstance(value, dict):
            errors.append(f"{path} must be an object")
            return {}
        return value

    def timestamp(value, path):
        try:
            if not isinstance(value, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value
            ):
                raise ValueError("expected RFC 3339 UTC with Z")
            return parse_time(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
            return None

    def strings(value):
        return isinstance(value, list) and bool(value) and all(_text(v) for v in value)

    feature = event.get("feature")
    require(feature in (RESIDUAL, IDENTITY, CAUSE), "Space draft requires one of its three feature types")
    require(event.get("modality") == "xq.space:orbital", "Space draft requires modality xq.space:orbital")
    require(_text(event.get("subject")), "Space draft requires subject")
    require(event.get("polarity") == 0, "Space draft requires polarity 0")
    for key in ("state", "end_time"):
        require(key not in event, f"Space draft does not use {key}")
    event_time = timestamp(event.get("event_time"), "event_time")
    if "observed_time" in event:
        timestamp(event["observed_time"], "observed_time")
    ctx = obj(event.get("context"), "context")
    prov = obj(event.get("provenance"), "provenance")
    for key in ("producer", "producer_version", "method"):
        require(_text(prov.get(key)), f"Space draft requires provenance.{key}")
    require(strings(prov.get("parents")) or strings(prov.get("source_records")),
            "Space draft requires evidence in provenance.parents or source_records")

    if feature == RESIDUAL:
        require(event.get("class") == "derived", "Space residual requires class derived")
        require(event.get("action") == "xq:observed", "Space residual requires action xq:observed")
        require(bool(re.fullmatch(r"norad:[1-9][0-9]*", str(event.get("subject", "")))),
                "Space residual requires a catalogue-scoped norad subject")
        for key in ("object", "confidence", "location"):
            require(key not in event, f"Space residual must omit {key}")
        magnitude = event.get("magnitude")
        require(_number(magnitude) and magnitude >= 0, "Space residual requires non-negative finite magnitude")
        require(event.get("unit") == "km", "Space residual requires unit km")
        reporting = timestamp(ctx.get("reporting_epoch"), "context.reporting_epoch")
        window = obj(ctx.get("observation_window"), "context.observation_window")
        start = timestamp(window.get("start"), "context.observation_window.start")
        end = timestamp(window.get("end"), "context.observation_window.end")
        duration = window.get("duration_hours")
        require(_number(duration) and duration > 0, "Space observation window requires positive duration_hours")
        if reporting is not None and event_time is not None:
            require(reporting == event_time, "Space event_time must equal reporting_epoch")
        if end is not None and reporting is not None:
            require(end == reporting, "Space observation window end must equal reporting_epoch")
        if start is not None and end is not None:
            require(start < end, "Space observation window must have start before end")
            if _number(duration):
                require(abs((end - start).total_seconds() - duration * 3600) <= 0.002,
                        "Space observation window duration disagrees with timestamps")

        method = obj(prov.get("xq.space:method"), "provenance[xq.space:method]")
        for key in ("name", "version", "maturity"):
            require(_text(method.get(key)), f"Space residual requires analytical method {key}")
        if method.get("name") == "sgp4_consistency" and method.get("version") == "0.2":
            require(method.get("maturity") == "experimental", "sgp4_consistency 0.2 must remain experimental")
        inputs = obj(prov.get("xq.space:inputs"), "provenance[xq.space:inputs]")
        input_ids = []
        source_records = prov.get("source_records")
        for side in ("earlier", "later"):
            item = obj(inputs.get(side), f"Space {side} input")
            for key in ("id", "source", "representation"):
                require(_text(item.get(key)), f"Space {side} input requires {key}")
            input_ids.append(item.get("id"))
            require(isinstance(source_records, list) and item.get("id") in source_records,
                    f"Space {side} input id must appear in source_records")
            if item.get("reconstructed") is not None:
                require(isinstance(item["reconstructed"], bool), f"Space {side} reconstructed must be boolean or null")
        require(input_ids[0] != input_ids[1], "Space earlier and later input IDs must differ")
        obj(ctx.get("quality_flags"), "context.quality_flags")

        residuals = obj(ctx["residuals"], "context.residuals") if "residuals" in ctx else {}
        components = [residuals.get(k) for k in ("radial_km", "in_track_km", "cross_track_km")]
        for key in ("velocity_km_s", "radial_km", "in_track_km", "cross_track_km"):
            value = residuals.get(key)
            if value is not None:
                require(_number(value), f"context.residuals.{key} must be finite or null")
        velocity = residuals.get("velocity_km_s")
        if _number(velocity):
            require(velocity >= 0, "Velocity residual norm must be non-negative")
        if all(_number(v) for v in components) and _number(magnitude):
            require(math.isclose(math.hypot(*components), magnitude, rel_tol=1e-6, abs_tol=1e-6),
                    "RTN component norm must agree with magnitude")
        if "element_changes" in ctx:
            changes = obj(ctx["element_changes"], "context.element_changes")
            for key in ("semi_major_axis_km", "inclination_deg", "eccentricity", "mean_motion_rev_per_day"):
                if changes.get(key) is not None:
                    require(_number(changes[key]), f"context.element_changes.{key} must be finite or null")
        if "heuristic" in ctx:
            heuristic = obj(ctx["heuristic"], "context.heuristic")
            require(heuristic.get("calibrated") is False, "Space residual heuristic must have calibrated false")
            score = heuristic.get("score")
            if score is not None:
                require(_number(score) and score >= 0, "Heuristic score must be non-negative and finite")
            for key in ("severity", "detection_tier"):
                if heuristic.get(key) is not None:
                    require(heuristic[key] in ("low", "medium", "high"), f"Invalid heuristic {key}")
            if heuristic.get("severity") is not None and heuristic.get("detection_tier") is not None:
                require(heuristic["severity"] == heuristic["detection_tier"], "Heuristic tier aliases must agree")
        if ctx.get("calibration") is not None:
            cal = obj(ctx["calibration"], "context.calibration")
            for key in ("rolling_baseline", "robust_deviation", "percentile"):
                if cal.get(key) is not None:
                    require(_number(cal[key]), f"Calibration {key} must be finite or null")
            if _number(cal.get("rolling_baseline")):
                require(cal["rolling_baseline"] >= 0, "Calibration baseline must be non-negative")
            if _number(cal.get("percentile")):
                require(0 <= cal["percentile"] <= 100, "Calibration percentile must be in [0,100]")
            if any(cal.get(k) is not None for k in ("rolling_baseline", "robust_deviation", "percentile")):
                for key in ("population", "window", "version"):
                    require(_text(cal.get(key)), f"Calibration statistics require {key}")
                count = cal.get("sample_count")
                require(isinstance(count, int) and not isinstance(count, bool) and count >= 0,
                        "Calibration statistics require non-negative integer sample_count")
        if "source_record" in ctx:
            source = obj(ctx["source_record"], "context.source_record")
            for key in ("created_at", "superseded_at", "event_time"):
                if source.get(key) is not None:
                    timestamp(source[key], f"context.source_record.{key}")

    elif feature in (IDENTITY, CAUSE):
        require(event.get("class") == "assessment", "Space hypothesis requires class assessment")
        require(event.get("action") == "xq.space:assessed", "Space hypothesis requires action xq.space:assessed")
        for key in ("magnitude", "unit"):
            require(key not in event, f"Space hypothesis must omit {key}")
        assessment = obj(ctx.get("assessment"), "context.assessment")
        for key in ("statement", "rationale", "limitations"):
            require(_text(assessment.get(key)), f"Space hypothesis requires assessment.{key}")
        if "confidence" in event:
            require(_text(assessment.get("confidence_basis")), "Space hypothesis confidence requires confidence_basis")
        if feature == IDENTITY:
            require(_text(event.get("object")) and event.get("object") != event.get("subject"),
                    "Identity hypothesis requires a distinct candidate object")
        else:
            require("object" not in event, "Cause hypothesis must omit object")
            require(strings(assessment.get("alternatives")), "Cause hypothesis requires competing alternatives")
    return errors
