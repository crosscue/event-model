#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0.

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA_PATH = ROOT / "schema" / "crosscue-event.schema.json"
COLLECTION_SCHEMA_PATH = ROOT / "schema" / "crosscue-event-collection.schema.json"
CORE_VOCAB_PATH = ROOT / "vocabulary" / "xq-core-vocabulary.json"
MOB_VOCAB_PATH = ROOT / "profiles" / "xq-mob-vocabulary.json"
MANIFEST_PATH = ROOT / "conformance" / "manifest.json"

OFFSET_RE = re.compile(r"(?:Z|[+-]\d{2}:\d{2})$")
MOB_PROFILE = "xq.mob:profile-0.1"
MOB_REQUIRED_PARAMETERS = {
    "geohash_precision",
    "move_radius_m",
    "dwell_threshold_s",
    "gap_threshold_s",
    "max_speed_mps",
    "max_jump_m",
    "confirm_moves",
    "confirm_window_s",
    "walk_max_speed_mps",
    "walk_max_jump_m",
}
MOB_MAPPINGS = {
    ("xq:track", "xq:start"): "START",
    ("xq:track", "xq:end"): "END",
    ("xq:presence", "xq:enter"): "ENTER",
    ("xq:presence", "xq:leave"): "LEAVE",
    ("xq:presence", "xq.mob:stay"): "STAY",
    ("xq:presence", "xq.mob:dwell"): "DWELL",
    ("xq:observation", "xq:gap"): "GAP",
    ("xq:trajectory", "xq:discontinuity"): "DISCONTINUITY",
}


def strict_json(path: Path):
    def reject_constant(value):
        raise ValueError(f"non-finite/non-JSON numeric token {value!r}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    if not OFFSET_RE.search(value):
        raise ValueError("date-time must carry an explicit UTC offset or Z")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def composition_index():
    idx = {}
    for path in (CORE_VOCAB_PATH, MOB_VOCAB_PATH):
        doc = load_json(path)
        for composition in doc.get("compositions", []):
            idx[(composition["feature"], composition["action"])] = composition
    return idx


COMPOSITIONS = composition_index()


def term_index():
    idx = {}
    for path in (CORE_VOCAB_PATH, MOB_VOCAB_PATH):
        doc = load_json(path)
        for term in doc.get("terms", []):
            idx[term["id"]] = term
    return idx


TERMS = term_index()
SEMANTIC_FIELD_KINDS = {
    "modality": "modality",
    "feature": "feature",
    "action": "action",
    "state": "state",
}


def semantic_event_errors(event):
    errors = []

    for field, expected_kind in SEMANTIC_FIELD_KINDS.items():
        value = event.get(field)
        if not isinstance(value, str):
            continue
        if value.startswith("xq:") or value.startswith("xq.mob:"):
            term = TERMS.get(value)
            if term is None:
                errors.append(f"{field}: unregistered Crosscue semantic identifier {value}")
            elif term.get("kind") != expected_kind:
                errors.append(
                    f"{field}: {value} is registered as kind {term.get('kind')}, expected {expected_kind}"
                )

    for field in ("event_time", "end_time", "observed_time"):
        if field in event:
            try:
                parse_time(event[field])
            except Exception as exc:
                errors.append(f"{field}: {exc}")

    if "event_time" in event and "end_time" in event:
        try:
            if parse_time(event["end_time"]) < parse_time(event["event_time"]):
                errors.append("end_time precedes event_time")
        except Exception:
            pass

    binding = COMPOSITIONS.get((event.get("feature"), event.get("action")))
    if binding:
        if event.get("polarity") != binding.get("required_polarity"):
            errors.append(
                f"{binding['id']} requires polarity {binding.get('required_polarity')}"
            )
        if "required_state" in binding and event.get("state") != binding["required_state"]:
            errors.append(f"{binding['id']} requires state {binding['required_state']}")
        if "required_unit" in binding and event.get("unit") != binding["required_unit"]:
            errors.append(f"{binding['id']} requires unit {binding['required_unit']}")

    if event.get("profile") == MOB_PROFILE:
        if event.get("modality") != "xq:mobility":
            errors.append("Mobility Profile requires modality xq:mobility")
        if event.get("class") != "transition":
            errors.append("Mobility Profile 0.1 eventizer events require class transition")
        mapping = MOB_MAPPINGS.get((event.get("feature"), event.get("action")))
        if mapping is None:
            errors.append("feature/action pair is not defined by Mobility Profile 0.1")
        else:
            source_event = event.get("context", {}).get("source_event")
            if source_event is not None and source_event != mapping:
                errors.append(f"context.source_event {source_event!r} conflicts with profile mapping {mapping}")

        provenance = event.get("provenance") or {}
        if not provenance.get("producer"):
            errors.append("Mobility Profile requires provenance.producer")
        if not provenance.get("producer_version"):
            errors.append("Mobility Profile requires provenance.producer_version")
        params = provenance.get("parameters")
        if not isinstance(params, dict):
            errors.append("Mobility Profile requires provenance.parameters")
        else:
            missing = sorted(MOB_REQUIRED_PARAMETERS - set(params))
            if missing:
                errors.append("Mobility Profile missing eventizer parameters: " + ", ".join(missing))

        action = event.get("action")
        if action in {"xq.mob:stay", "xq.mob:dwell"}:
            if "end_time" not in event:
                errors.append("STAY/DWELL requires end_time")
            if "magnitude" not in event or event.get("unit") != "s":
                errors.append("STAY/DWELL requires duration magnitude in seconds")
            if "end_time" in event and "event_time" in event and "magnitude" in event:
                try:
                    duration = (parse_time(event["end_time"]) - parse_time(event["event_time"])).total_seconds()
                    if abs(float(event["magnitude"]) - duration) > 1e-9:
                        errors.append("STAY/DWELL magnitude must equal end_time - event_time in seconds")
                    if isinstance(params, dict) and "dwell_threshold_s" in params:
                        threshold = float(params["dwell_threshold_s"])
                        if action == "xq.mob:dwell" and duration < threshold:
                            errors.append("DWELL duration is below dwell_threshold_s")
                        if action == "xq.mob:stay" and duration >= threshold:
                            errors.append("STAY duration meets/exceeds dwell_threshold_s and should be DWELL")
                except Exception:
                    pass
        elif action == "xq:gap":
            if "magnitude" not in event or event.get("unit") != "s":
                errors.append("Mobility GAP requires gap duration magnitude in seconds")
        elif action == "xq:discontinuity":
            if "magnitude" not in event or event.get("unit") != "m":
                errors.append("Mobility DISCONTINUITY requires jump distance magnitude in metres")

    return errors


def build_validators():
    event_schema = load_json(EVENT_SCHEMA_PATH)
    collection_schema = load_json(COLLECTION_SCHEMA_PATH)
    # Validate the collection envelope here and validate each embedded event
    # separately with EVENT_VALIDATOR. This keeps the reference validator free
    # of schema-URI resolution behavior while the published schema retains its
    # normal relative $ref.
    collection_schema["properties"]["events"]["items"] = {}
    event_validator = Draft202012Validator(event_schema, format_checker=FormatChecker())
    collection_validator = Draft202012Validator(collection_schema, format_checker=FormatChecker())
    return event_validator, collection_validator


EVENT_VALIDATOR, COLLECTION_VALIDATOR = build_validators()


def validate_document(document):
    errors = []
    if isinstance(document, dict) and document.get("type") == "event_collection":
        errors.extend(str(e) for e in COLLECTION_VALIDATOR.iter_errors(document))
        ids = []
        for i, event in enumerate(document.get("events", [])):
            for err in EVENT_VALIDATOR.iter_errors(event):
                errors.append(f"events[{i}]: {err.message}")
            for err in semantic_event_errors(event):
                errors.append(f"events[{i}]: {err}")
            if isinstance(event, dict) and "id" in event:
                ids.append(event["id"])
        if len(ids) != len(set(ids)):
            errors.append("event_collection contains duplicate event ids")
        return errors

    if not isinstance(document, dict):
        return ["document is neither a Core Event object nor an event_collection object"]
    errors.extend(e.message for e in EVENT_VALIDATOR.iter_errors(document))
    errors.extend(semantic_event_errors(document))
    return errors


def validate_path(path: Path):
    try:
        document = strict_json(path)
    except Exception as exc:
        return [f"JSON parse error: {exc}"]
    return validate_document(document)


def run_manifest():
    manifest = load_json(MANIFEST_PATH)
    root = MANIFEST_PATH.parent
    failed = 0
    total = 0
    for rel in manifest["valid"]:
        total += 1
        path = root / rel
        errs = validate_path(path)
        if errs:
            failed += 1
            print(f"FAIL expected valid: {rel}")
            for err in errs:
                print(f"  - {err}")
        else:
            print(f"PASS valid: {rel}")
    for rel in manifest["invalid"]:
        total += 1
        path = root / rel
        errs = validate_path(path)
        if not errs:
            failed += 1
            print(f"FAIL expected invalid: {rel}")
        else:
            print(f"PASS invalid: {rel} ({errs[0]})")
    print(f"\n{total - failed}/{total} conformance fixtures behaved as expected")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description="Validate Crosscue Event Model Core 0.1 JSON and conformance fixtures.")
    parser.add_argument("paths", nargs="*", type=Path, help="JSON event/collection files to validate")
    parser.add_argument("--fixtures", action="store_true", help="run the packaged valid/invalid conformance suite")
    args = parser.parse_args()

    if args.fixtures:
        return run_manifest()
    if not args.paths:
        parser.error("provide JSON paths or --fixtures")

    failed = 0
    for path in args.paths:
        errs = validate_path(path)
        if errs:
            failed += 1
            print(f"INVALID {path}")
            for err in errs:
                print(f"  - {err}")
        else:
            print(f"VALID {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
