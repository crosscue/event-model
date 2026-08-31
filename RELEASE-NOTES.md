# Crosscue Event Model Core 0.1.0 — Release notes

**Release date:** 2026-08-31  
**Wire version:** `xq_version = "0.1"`  
**Status:** Initial public release; experimental specification

## Scope

This release publishes the frozen 0.1 Core together with the Mobility Profile 0.1, schemas, semantic registries, synthetic examples, conformance fixtures and reference validator.

The Crosscue Event Model is a semantic intermediate representation. It is not presented as an industry standard, does not replace source-native formats, and does not imply external endorsement or adoption.

## 0.1 compatibility freeze

Version 0.1.0 freezes the following for the 0.1.x line:

- Core JSON field meanings and structural contract;
- the meanings of existing registered `xq:` terms;
- existing Core composition polarity/state/unit bindings;
- `xq_version = "0.1"`.

Patch releases may correct editorial or validator defects and add tests or non-normative examples that clarify existing semantics. Incompatible Core changes, or changes that alter the meaning of existing registered terms, belong in a later Core version and require an explicit wire-version decision where applicable.

Profiles version independently. Domain discoveries SHOULD be expressed through profiles, provenance or `context` before changing Core.

## Included namespaces

Only these Crosscue namespaces are allocated in 0.1.0:

```text
xq:       Core vocabulary
xq.mob:   Mobility Profile 0.1
```

The coarse Core modalities `xq:ais`, `xq:ads-b`, `xq:rf` and `xq:imagery` do not allocate corresponding profile namespaces.

## Reference validation

Run:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate.py --fixtures
```

The suite includes positive and negative structural/semantic fixtures, including Mobility threshold/provenance cases and cross-domain semantic examples.

## Licence

All repository materials are licensed under the Apache License, Version 2.0. See `LICENSE`.
