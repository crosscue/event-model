# Crosscue Event Model

**Core 0.1.1 — Network Profile Release**

The **Crosscue Event Model** is a small semantic intermediate representation for temporally anchored observations, state transitions, derived facts, fusion results, and analytical assessments across heterogeneous data sources.

The public name is **Crosscue Event Model**. The technical semantic namespace used on the wire is **`xq:`**.

A typical Core event looks like:

```json
{
  "xq_version": "0.1",
  "id": "evt:demo-001",
  "event_time": "2026-08-30T08:20:00Z",
  "source": "synthetic-mobility",
  "modality": "xq:mobility",
  "class": "transition",
  "profile": "xq.mob:profile-0.1",
  "subject": "device:demo-a",
  "feature": "xq:presence",
  "action": "xq:enter",
  "state": "xq:present",
  "polarity": 1
}
```

The intended architectural position is:

```text
source-native data
      ↓
domain adapters / eventizers
      ↓
Crosscue Event Model Core Events
      ↓
correlation / fusion / analytics
      ↓
derived Core Events + analytical projections
```

The model deliberately does **not** replace source-native schemas such as AIS, ADS-B, RF metadata, imagery products, or mobility observations. It provides a common temporal/semantic layer above them.

## Status

This is an **experimental specification**, not an industry standard and not evidence of external endorsement or adoption.

Core 0.1 has now been exercised through two materially different published profiles: Mobility Profile 0.1 and Network Profile 0.1. Non-normative semantic examples for AIS, ADS-B, RF and imagery continue to stress the Core vocabulary without pretending those profiles already exist.

**Core 0.1 is frozen for the 0.1.x release line.** Existing Core fields, registered `xq:` term meanings, and registered Core composition bindings will not be changed incompatibly within 0.1.x. Lessons from materially different profiles are expected to inform a future 0.2 rather than silently redefine 0.1 semantics.

## Safety, privacy and dual use

The Crosscue Event Model can make temporal, spatial, entity and cross-source correlation easier. That is analytically useful, but it can also increase the sensitivity of data and derived products.

Implementers are responsible for appropriate legal authority, data minimisation, access controls, retention, audit, redaction, and handling of sensitive or personally identifying information. Pseudonymisation does not necessarily prevent re-identification when location and time are sufficiently distinctive.

The `markings` field is an opaque transport mechanism for deployment-specific handling labels. **It is not a security model, classification system, access-control mechanism, or policy engine.**

Examples in this repository are synthetic. Contributors MUST NOT submit customer data, operational intelligence, personal mobility traces, or other sensitive datasets as public fixtures.

See [`SECURITY.md`](SECURITY.md) and [`WHAT-THIS-IS-NOT.md`](WHAT-THIS-IS-NOT.md).

## Start here

- [`SPECIFICATION.md`](SPECIFICATION.md) — normative Core 0.1 specification.
- [`schema/crosscue-event.schema.json`](schema/crosscue-event.schema.json) — Draft 2020-12 structural schema.
- [`schema/crosscue-event-collection.schema.json`](schema/crosscue-event-collection.schema.json) — optional small collection envelope.
- [`NAMESPACES.md`](NAMESPACES.md) — `xq:` and extension namespace rules.
- [`vocabulary/xq-core-vocabulary.json`](vocabulary/xq-core-vocabulary.json) — Core term registry and semantic bindings.
- [`CONFORMANCE.md`](CONFORMANCE.md) — structural, semantic and profile conformance.
- [`conformance/`](conformance/) — executable positive and negative fixtures.
- [`tools/validate.py`](tools/validate.py) — reference fixture/event validator.
- [`profiles/crosscue-mobility-0.1.md`](profiles/crosscue-mobility-0.1.md) — first domain profile.
- [`profiles/xq-mob-vocabulary.json`](profiles/xq-mob-vocabulary.json) — Mobility-specific vocabulary.
- [`profiles/crosscue-network-0.1.md`](profiles/crosscue-network-0.1.md) — Network Profile 0.1.
- [`profiles/xq-net-vocabulary.json`](profiles/xq-net-vocabulary.json) — Network-specific vocabulary.
- [`examples/network-profile-0.1-events.json`](examples/network-profile-0.1-events.json) — synthetic Network Profile examples.
- [`examples/crosscue-core-events.json`](examples/crosscue-core-events.json) — synthetic event examples.
- [`examples/SEMANTIC-EXAMPLES.md`](examples/SEMANTIC-EXAMPLES.md) — mobility/AdTech, Network, AIS, ADS-B, RF and exploratory imagery mappings.
- [`MIGRATION.md`](MIGRATION.md) — migration from the exploratory CLI object and earlier draft naming.
- [`RELEASE-NOTES.md`](RELEASE-NOTES.md) — 0.1.1 release scope and compatibility notes.

## Namespaces

These namespaces are allocated by this release:

```text
xq:       Core vocabulary
xq.mob:   Mobility Profile 0.1
xq.net:   Network Profile 0.1
```

Future profile prefixes are allocated only when a corresponding official profile is published. For example, an RF profile might later allocate `xq.rf:`, but it is **not** allocated by Core 0.1.1.

Third parties should use a namespace they control, for example:

```text
org.example:signal
uk.example.sensor:mode
```

## Event class is epistemic, not relational

Core 0.1 uses these event classes:

```text
observation
normalized_observation
transition
derived
fusion
assessment
```

Relational structure is expressed orthogonally through `subject` and `object`. Production method such as manual, algorithmic or hybrid belongs in provenance.

Thus an event can be both relational and derived without overloading `class`:

```json
{
  "class": "derived",
  "subject": "entity:A",
  "object": "entity:B",
  "feature": "org.example:proximity",
  "action": "org.example:established"
}
```

## Core vocabulary discipline

Core vocabulary is intentionally small. Mobility-specific `STAY` and `DWELL` semantics are **not** Core actions in Core 0.1; they are defined as:

```text
xq.mob:stay
xq.mob:dwell
```

New Core terms should normally demonstrate usefulness in at least two materially different modalities before promotion. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Conformance

Install the development validator dependency and run:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate.py --fixtures
```

The validator checks JSON Schema constraints plus semantic rules that JSON Schema alone cannot express, including:

- `end_time` not preceding `event_time`;
- explicit timezone offsets;
- registered composition polarity/state bindings;
- Mobility Profile eventizer provenance parameters;
- Network Profile entity-layer, viewpoint, first-observed, DNS, service and presence rules;
- `STAY` versus `DWELL` duration semantics;
- unique event IDs within the optional collection envelope.

## Licence

The specification, schemas, vocabularies, profiles, examples, conformance materials and reference tooling in this repository are licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE).

