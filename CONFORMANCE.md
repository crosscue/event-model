# Crosscue Event Model Core 0.1 Conformance

Conformance is intentionally layered because JSON Schema cannot validate all event semantics.

## 1. Conformance claims

An implementation MAY claim one or more of:

```text
Crosscue Event Model Core 0.1 Producer
Crosscue Event Model Core 0.1 Consumer
Crosscue Event Model Core Vocabulary 0.1 Producer
Crosscue Event Model Mobility Profile 0.1 Producer
Crosscue Event Model Mobility Profile 0.1 Consumer
Crosscue Event Model Network Profile 0.1 Producer
Crosscue Event Model Network Profile 0.1 Consumer
```

A claim SHOULD identify the implementation version and the exact specification/profile version used.

## 2. Core Producer

A Core Producer MUST:

1. emit events valid against `schema/crosscue-event.schema.json`;
2. obey semantic MUST/MUST NOT rules in `SPECIFICATION.md`;
3. emit `xq_version = "0.1"`;
4. provide stable event IDs;
5. provide polarity in `{-1,0,1}`;
6. provide `unit` whenever `magnitude` is supplied;
7. use qualified semantic identifiers for modality, feature, action and supplied state;
8. provide `subject` when `object` is supplied;
9. ensure `end_time >= event_time`;
10. emit valid JSON numbers only;
11. not use `context` to redefine Core semantics.

## 3. Core Vocabulary Producer

A producer additionally claiming Core Vocabulary conformance MUST:

- use registered `xq:` terms according to their registry definitions;
- obey required polarity/state bindings for registered compositions;
- not present private meanings as registered Core semantics.

Example: `xq:presence` + `xq:enter` requires:

```text
state    xq:present
polarity +1
```

## 4. Core Consumer

A Core Consumer MUST:

1. parse Core-valid events;
2. preserve zero polarity as meaningful;
3. preserve event-class distinctions;
4. tolerate unknown qualified semantic identifiers;
5. tolerate unknown `context` fields;
6. tolerate unknown provenance extension fields;
7. preserve unknown fields inside extensible objects when claiming lossless transformation;
8. avoid treating unknown qualified terms as if they were registered Core terms.

## 5. Relational structure

Relational structure is not an event class.

`object` implies `subject`, and the event retains its epistemic class (`observation`, `derived`, `assessment`, etc.).

## 6. Source-reported status

Core `state` is semantic state, not an automatic copy of source-native status. Producers MUST follow the source-reported-status rule in `SPECIFICATION.md` Section 18.1.

This rule is not generically machine-detectable: a validator cannot know whether a state was independently derived, profile-mapped, validated, or merely copied from source data. Domain profiles and producer conformance tests SHOULD therefore include explicit fixtures for any source-native status mappings they permit.

## 7. Structural versus semantic validation

Structural validation is performed by JSON Schema.

Semantic validation additionally covers rules such as:

- interval ordering;
- Core vocabulary composition bindings;
- profile-specific event mappings;
- profile eventization thresholds;
- effective eventizer parameter provenance;
- collection-level ID uniqueness.

Therefore this event may pass general structural shape checks yet fail semantic conformance:

```json
{
  "feature": "xq:presence",
  "action": "xq:enter",
  "state": "xq:present",
  "polarity": -1
}
```

## 8. Packaged fixtures

The repository contains:

```text
conformance/valid/
conformance/invalid/
conformance/manifest.json
```

The invalid suite includes at least:

- missing required field;
- polarity outside range;
- magnitude without unit;
- object without subject;
- invalid latitude;
- confidence outside range;
- unqualified semantic identifier;
- `end_time` before `event_time`;
- semantically wrong Core polarity binding;
- missing Mobility eventizer parameters;
- DWELL below threshold;
- STAY at/above threshold;
- non-finite/non-JSON number;
- duplicate IDs in an event collection.

## 9. Reference validator

Install:

```bash
python -m pip install -r requirements-dev.txt
```

Run all fixtures:

```bash
python tools/validate.py --fixtures
```

Validate a specific event or collection:

```bash
python tools/validate.py path/to/event.json
```

The reference validator is informative executable tooling for Core 0.1. Conforming implementations MAY use any technology that produces equivalent validation results.

## 10. Profile fixtures

A profile MUST add deterministic fixtures for semantic mappings it defines.

The Mobility Profile covers the source event semantics:

```text
START
STAY
DWELL
LEAVE
ENTER
GAP
DISCONTINUITY
END
```

## 11. Serialization equivalence

Byte-equivalent JSON is not required unless a test explicitly defines canonical bytes.

Whitespace and member ordering are insignificant. JSON and JSONL examples should be semantically equivalent after parsing.


## 11. Network Profile fixtures

Network Profile 0.1 adds deterministic positive and negative fixtures for:

- `xq:network` + `xq.net:profile-0.1`;
- reuse of Core `xq:observed`;
- device/interface/address/endpoint/service separation;
- ARP first-observed binding derivation;
- DNS query temporal purity;
- DNS alias versus address resolution;
- endpoint-versus-service semantics;
- explicit scoped presence;
- relationship evidence directionality and first-observed temporal purity;
- single/multiple observation-point rules;
- deterministic application-stack canonicalization.

Profile-specific validation is dispatched by the reference validator according to the explicit `profile` claim.
