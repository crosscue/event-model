#!/usr/bin/env python3
# Licensed under the Apache License, Version 2.0.

import argparse, json, re, sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from profile_validators import VALIDATORS

ROOT=Path(__file__).resolve().parents[1]
EVENT_SCHEMA_PATH=ROOT/"schema"/"crosscue-event.schema.json"
COLLECTION_SCHEMA_PATH=ROOT/"schema"/"crosscue-event-collection.schema.json"
CORE_VOCAB_PATH=ROOT/"vocabulary"/"xq-core-vocabulary.json"
PROFILE_VOCAB_GLOB="xq-*-vocabulary.json"
MANIFEST_PATH=ROOT/"conformance"/"manifest.json"
OFFSET_RE=re.compile(r"(?:Z|[+-]\d{2}:\d{2})$")
SEMANTIC_FIELD_KINDS={"modality":"modality","feature":"feature","action":"action","state":"state"}

def strict_json(path):
    def reject_constant(v): raise ValueError(f"non-finite/non-JSON numeric token {v!r}")
    return json.loads(path.read_text(encoding="utf-8"),parse_constant=reject_constant)

def load_json(path): return json.loads(path.read_text(encoding="utf-8"))

def parse_time(value):
    if not OFFSET_RE.search(value): raise ValueError("date-time must carry an explicit UTC offset or Z")
    return datetime.fromisoformat(value[:-1]+"+00:00" if value.endswith("Z") else value)

def vocabulary_paths():
    return [CORE_VOCAB_PATH] + sorted((ROOT/"profiles").glob(PROFILE_VOCAB_GLOB))

def indexes():
    terms,comps={},{}
    for path in vocabulary_paths():
        doc=load_json(path)
        for term in doc.get("terms",[]):
            if term["id"] in terms: raise RuntimeError(f"duplicate vocabulary term {term['id']} in {path}")
            terms[term["id"]]=term
        for comp in doc.get("compositions",[]):
            key=(comp["feature"],comp["action"])
            if key in comps: raise RuntimeError(f"duplicate composition {key} in {path}")
            comps[key]=comp
    return terms,comps
TERMS,COMPOSITIONS=indexes()

def semantic_event_errors(event):
    errors=[]
    for field,kind in SEMANTIC_FIELD_KINDS.items():
        value=event.get(field)
        if not isinstance(value,str): continue
        if value.startswith("xq:") or value.startswith("xq."):
            term=TERMS.get(value)
            if term is None: errors.append(f"{field}: unregistered Crosscue semantic identifier {value}")
            elif term.get("kind")!=kind: errors.append(f"{field}: {value} is registered as kind {term.get('kind')}, expected {kind}")
    for field in ("event_time","end_time","observed_time"):
        if field in event:
            try: parse_time(event[field])
            except Exception as exc: errors.append(f"{field}: {exc}")
    if "event_time" in event and "end_time" in event:
        try:
            if parse_time(event["end_time"])<parse_time(event["event_time"]): errors.append("end_time precedes event_time")
        except Exception: pass
    binding=COMPOSITIONS.get((event.get("feature"),event.get("action")))
    if binding:
        if event.get("polarity")!=binding.get("required_polarity"): errors.append(f"{binding['id']} requires polarity {binding.get('required_polarity')}")
        if "required_state" in binding and event.get("state")!=binding["required_state"]: errors.append(f"{binding['id']} requires state {binding['required_state']}")
        if "required_unit" in binding and event.get("unit")!=binding["required_unit"]: errors.append(f"{binding['id']} requires unit {binding['required_unit']}")
    profile=event.get("profile")
    if profile in VALIDATORS: errors.extend(VALIDATORS[profile](event,parse_time))
    return errors

def build_validators():
    event_schema=load_json(EVENT_SCHEMA_PATH); collection_schema=load_json(COLLECTION_SCHEMA_PATH)
    collection_schema["properties"]["events"]["items"]={}
    return (Draft202012Validator(event_schema,format_checker=FormatChecker()), Draft202012Validator(collection_schema,format_checker=FormatChecker()))
EVENT_VALIDATOR,COLLECTION_VALIDATOR=build_validators()

def validate_document(document):
    errors=[]
    if isinstance(document,dict) and document.get("type")=="event_collection":
        errors.extend(str(e) for e in COLLECTION_VALIDATOR.iter_errors(document)); ids=[]
        for i,event in enumerate(document.get("events",[])):
            for err in EVENT_VALIDATOR.iter_errors(event): errors.append(f"events[{i}]: {err.message}")
            for err in semantic_event_errors(event): errors.append(f"events[{i}]: {err}")
            if isinstance(event,dict) and "id" in event: ids.append(event["id"])
        if len(ids)!=len(set(ids)): errors.append("event_collection contains duplicate event ids")
        return errors
    if not isinstance(document,dict): return ["document is neither a Core Event object nor an event_collection object"]
    errors.extend(e.message for e in EVENT_VALIDATOR.iter_errors(document)); errors.extend(semantic_event_errors(document)); return errors

def validate_path(path):
    try: return validate_document(strict_json(path))
    except Exception as exc: return [f"JSON parse error: {exc}"]

def run_manifest():
    manifest=load_json(MANIFEST_PATH); root=MANIFEST_PATH.parent; failed=total=0
    for rel in manifest["valid"]:
        total+=1; errs=validate_path(root/rel)
        if errs:
            failed+=1; print(f"FAIL expected valid: {rel}"); [print(f"  - {e}") for e in errs]
        else: print(f"PASS valid: {rel}")
    for rel in manifest["invalid"]:
        total+=1; errs=validate_path(root/rel)
        if not errs: failed+=1; print(f"FAIL expected invalid: {rel}")
        else: print(f"PASS invalid: {rel} ({errs[0]})")
    print(f"\n{total-failed}/{total} conformance fixtures behaved as expected"); return 1 if failed else 0

def main():
    p=argparse.ArgumentParser(description="Validate Crosscue Event Model Core 0.1 and published profile JSON.")
    p.add_argument("paths",nargs="*",type=Path); p.add_argument("--fixtures",action="store_true"); a=p.parse_args()
    if a.fixtures: return run_manifest()
    if not a.paths: p.error("provide JSON paths or --fixtures")
    failed=0
    for path in a.paths:
        errs=validate_path(path)
        if errs:
            failed+=1; print(f"INVALID {path}"); [print(f"  - {e}") for e in errs]
        else: print(f"VALID {path}")
    return 1 if failed else 0
if __name__=="__main__": sys.exit(main())
