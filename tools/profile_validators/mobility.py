# Licensed under the Apache License, Version 2.0.

PROFILE_ID = "xq.mob:profile-0.1"
REQUIRED_PARAMETERS = {
    "geohash_precision", "move_radius_m", "dwell_threshold_s", "gap_threshold_s",
    "max_speed_mps", "max_jump_m", "confirm_moves", "confirm_window_s",
    "walk_max_speed_mps", "walk_max_jump_m",
}
MAPPINGS = {
    ("xq:track", "xq:start"): "START",
    ("xq:track", "xq:end"): "END",
    ("xq:presence", "xq:enter"): "ENTER",
    ("xq:presence", "xq:leave"): "LEAVE",
    ("xq:presence", "xq.mob:stay"): "STAY",
    ("xq:presence", "xq.mob:dwell"): "DWELL",
    ("xq:observation", "xq:gap"): "GAP",
    ("xq:trajectory", "xq:discontinuity"): "DISCONTINUITY",
}

def validate(event, parse_time):
    errors=[]
    if event.get("modality") != "xq:mobility": errors.append("Mobility Profile requires modality xq:mobility")
    if event.get("class") != "transition": errors.append("Mobility Profile 0.1 eventizer events require class transition")
    mapping=MAPPINGS.get((event.get("feature"), event.get("action")))
    if mapping is None: errors.append("feature/action pair is not defined by Mobility Profile 0.1")
    else:
        source_event=(event.get("context") or {}).get("source_event")
        if source_event is not None and source_event != mapping:
            errors.append(f"context.source_event {source_event!r} conflicts with profile mapping {mapping}")
    provenance=event.get("provenance") or {}
    if not provenance.get("producer"): errors.append("Mobility Profile requires provenance.producer")
    if not provenance.get("producer_version"): errors.append("Mobility Profile requires provenance.producer_version")
    params=provenance.get("parameters")
    if not isinstance(params,dict): errors.append("Mobility Profile requires provenance.parameters")
    else:
        missing=sorted(REQUIRED_PARAMETERS-set(params))
        if missing: errors.append("Mobility Profile missing eventizer parameters: "+", ".join(missing))
    action=event.get("action")
    if action in {"xq.mob:stay","xq.mob:dwell"}:
        if "end_time" not in event: errors.append("STAY/DWELL requires end_time")
        if "magnitude" not in event or event.get("unit") != "s": errors.append("STAY/DWELL requires duration magnitude in seconds")
        if "end_time" in event and "event_time" in event and "magnitude" in event:
            try:
                duration=(parse_time(event["end_time"])-parse_time(event["event_time"])).total_seconds()
                if abs(float(event["magnitude"])-duration)>1e-9: errors.append("STAY/DWELL magnitude must equal end_time - event_time in seconds")
                if isinstance(params,dict) and "dwell_threshold_s" in params:
                    threshold=float(params["dwell_threshold_s"])
                    if action=="xq.mob:dwell" and duration<threshold: errors.append("DWELL duration is below dwell_threshold_s")
                    if action=="xq.mob:stay" and duration>=threshold: errors.append("STAY duration meets/exceeds dwell_threshold_s and should be DWELL")
            except Exception: pass
    elif action=="xq:gap":
        if "magnitude" not in event or event.get("unit")!="s": errors.append("Mobility GAP requires gap duration magnitude in seconds")
    elif action=="xq:discontinuity":
        if "magnitude" not in event or event.get("unit")!="m": errors.append("Mobility DISCONTINUITY requires jump distance magnitude in metres")
    return errors
