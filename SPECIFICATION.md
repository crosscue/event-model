# Crosscue Event Model
## Core Specification 0.1

**Status:** Experimental Specification  
**Package version:** `0.1.0`  
**Wire version:** `xq_version = "0.1"`  
**Specification identifier:** `crosscue-event-model-core-0.1`  
**Licence:** Apache License 2.0

---

## 1. Scope

This document defines the **Crosscue Event Model Core Event**, a small cross-domain representation for temporally anchored observations, state transitions, derived facts, fusion results and analytical assessments.

The Core Event is intended to act as a semantic intermediate representation between heterogeneous source-native data and downstream correlation or analytics.

```text
source-native data
       ↓
parse / normalize
       ↓
domain interpretation / eventization
       ↓
Crosscue Event Model Core Event
       ↓
correlation / fusion / derivation
       ↓
new Core Events
       ↓
materialized analytical projections
```

The Core does not attempt to replace source-native representations. Producers SHOULD retain sufficient provenance to locate or reconstruct source evidence where policy and architecture permit.

Core 0.1 is intentionally experimental in maturity, but version 0.1.0 freezes the Core schema and registered Core semantic bindings for the 0.1.x release line. Materially different domains SHOULD stress the abstraction through profiles and extensions. Any incompatible Core change discovered through that work belongs in a future Core version rather than silently changing 0.1 semantics.

---

## 2. Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in all capitals.

---

## 3. Design principles

### 3.1 Small Core

Core MUST NOT become a union of all fields required by all modalities. Domain-specific evidence belongs in profiles, qualified extension vocabularies, provenance and `context`.

### 3.2 Epistemic separation

An observation MUST remain distinguishable from a normalization, state transition, derived fact, fusion result or assessment.

### 3.3 Time is first-class

The time of the represented occurrence is distinct from the time it was observed, received, processed or assessed.

### 3.4 Provenance is first-class

Derived intelligence SHOULD be traceable to immediate parent events or source records. Producers SHOULD record the algorithm, version and parameters that materially affect derived semantics.

### 3.5 Domain richness is retained

Projection to Core MUST NOT imply that source-native evidence is expendable.

### 3.6 State and polarity are different axes

`state` carries semantic state. `polarity` carries a deliberately tiny directional axis. They MUST NOT be treated as synonyms.

### 3.7 One primary magnitude

`magnitude`, when present, denotes one primary scalar associated with the event. Secondary measurements belong in `context`.

### 3.8 Analytics may emit events

A consumer MAY also be a producer. Derived, fusion and assessment outputs can be represented as Core Events.

### 3.9 Corroboration is not duplication

Independent sources describing the same occurrence MUST NOT automatically be collapsed as duplicates.

### 3.10 Analytical tables are projections

Tracks, segments, intervals, summaries and similar structures SHOULD remain traceable to the observations/events from which they were derived.

---

## 4. Conceptual primitives

The wider model assumes three broad primitives:

```text
ENTITY
EVENT
RELATIONSHIP
```

An **entity** may persist through time: vessel, aircraft, device, vehicle, emitter, facility, person, organisation, anonymous track or other referent.

An **event** is a temporally anchored representation of an observation, occurrence, state transition, derived fact, fusion result or assessment.

An enduring **relationship** may be maintained outside the event stream. A relationship establishment, change or dissolution that is temporally meaningful can be represented as an event.

Relational structure is orthogonal to event class. A Core Event is relational when `object` is present; `subject` identifies the other endpoint.

---

## 5. Core Event model

The conceptual shape is:

```text
CoreEvent {
    xq_version
    id

    event_time
    end_time?
    observed_time?

    source
    modality
    class
    profile?

    subject?
    object?

    feature
    action
    state?
    polarity

    magnitude?
    unit?

    location?
    confidence?

    provenance?
    markings?
    context?
}
```

Fields marked `?` are optional unless a profile or another rule makes them required.

---

## 6. Required fields

Every Core Event MUST contain:

- `xq_version`
- `id`
- `event_time`
- `source`
- `modality`
- `class`
- `feature`
- `action`
- `polarity`

A producer SHOULD provide `subject` whenever the event concerns an identifiable, pseudonymous or source-scoped entity.

---

## 7. `xq_version`

For Core 0.1:

```json
"xq_version": "0.1"
```

A conforming Core 0.1 producer MUST emit exactly `"0.1"`.

The wire version deliberately uses the technical `xq` identity rather than the human-facing specification name. Editorial/package patch changes do not change `xq_version` unless Core wire semantics change.

---

## 8. Event identifier: `id`

`id` is the stable identifier for an event.

It MUST:

1. be a non-empty string;
2. uniquely identify the event within the producer's intended correlation domain.

It SHOULD:

- remain immutable once published;
- be globally unique where practical;
- be treated as opaque by consumers.

Examples:

```text
evt:01J6C8R7X2D7P4TV7F66PP9C86
urn:uuid:550e8400-e29b-41d4-a716-446655440000
provider-a:event:18374291
```

Consumers MUST NOT infer semantics from the identifier format unless a profile explicitly defines such semantics.

---

## 9. Time model

### 9.1 `event_time`

`event_time` is the time at which the represented occurrence began or occurred, to the best knowledge of the producer.

It MUST be an RFC 3339 date-time with an explicit timezone offset or `Z`.

```json
"event_time": "2026-08-30T11:08:22Z"
```

### 9.2 `end_time`

`end_time` MAY be supplied for an interval-like event.

If present:

- it MUST be an RFC 3339 date-time with explicit timezone information;
- it MUST NOT precede `event_time`.

The interval is interpreted as beginning at `event_time` and ending at `end_time`.

### 9.3 `observed_time`

`observed_time` is the time the event/evidence was observed, received, reported, processed or assessed.

It MAY differ from `event_time`.

Examples include delayed reporting, batch ingestion, retrospective imagery analysis and analytical derivation.

Producers SHOULD omit it rather than fabricate it when unknown.

### 9.4 Precision and uncertainty

Core 0.1 does not define a general temporal uncertainty model. Profiles MAY carry time uncertainty in `context` using appropriately documented fields.

---

## 10. `source`

`source` identifies the origin or producer-visible provenance of the information.

Examples:

```text
receiver-17
vendor-a
imagery-product-123
analytics:correlator-3
```

`source` MUST be non-empty.

It identifies origin, not event semantics. A producer MAY use `provenance` for richer source-record and processing-chain information.

---

## 11. `modality`

`modality` describes the collection/domain modality associated with the event. It MUST be a qualified semantic identifier.

Examples:

```text
xq:mobility
xq:multimodal
org.example:rf
org.example:access-control
```

`modality` MUST NOT be used to duplicate epistemic class. In particular, Core 0.1 does not define `xq:fusion` or `xq:assessment` modalities; those meanings belong in `class`.

A fusion or assessment spanning multiple modalities MAY use `xq:multimodal` or an appropriate qualified extension modality.

---

## 12. Event `class`

`class` records the epistemic/derivation class of the event.

Allowed Core 0.1 values are:

```text
observation
normalized_observation
transition
derived
fusion
assessment
```

### 12.1 `observation`

A direct representation of source-observed evidence with minimal interpretation.

### 12.2 `normalized_observation`

A normalized or canonicalized observation that remains evidentially equivalent to source evidence and does not assert a higher-order transition or behaviour.

Examples: field normalization, timestamp normalization, duplicate collapse where the normalization method is documented.

### 12.3 `transition`

A state change inferred or identified from one or more observations or source events.

Examples: enter, leave, track start/end, observation gap, trajectory discontinuity.

### 12.4 `derived`

A higher-order fact produced analytically from lower-level events or observations.

Examples: visit, recurring presence, proximity relationship, behavioural pattern.

### 12.5 `fusion`

A specialized derived event whose result materially combines evidence from multiple source records, events or modalities.

A `fusion` event SHOULD carry provenance sufficient to identify its immediate contributing evidence.

### 12.6 `assessment`

An analytical judgment, estimate or hypothesis. It may be produced manually, algorithmically or through a hybrid workflow.

Production method belongs in `provenance.method`, not in `class`.

### 12.7 Relational events are not a class

An event with `subject` and `object` may be an observation, transition, derived event, fusion result or assessment.

Example:

```json
{
  "class": "derived",
  "subject": "entity:A",
  "object": "entity:B",
  "feature": "org.example:proximity",
  "action": "org.example:established"
}
```

---

## 13. `profile`

`profile` identifies a published domain profile whose additional semantics the event claims to follow.

Core 0.1 does not require a profile.

The first allocated profile identifier is:

```text
xq.mob:profile-0.1
```

A consumer MUST NOT assume profile conformance merely because `modality` has a related value. Profile conformance is an explicit claim.

---

## 14. Entity references: `subject` and `object`

### 14.1 `subject`

`subject` identifies the principal entity or referent to which the event applies.

It is an opaque non-empty string.

Examples:

```text
device:abc
mmsi:235012345
icao24:406a3d
track:17
entity:123
```

Core 0.1 does not define identifier authority, identifier type or entity resolution.

### 14.2 `object`

`object` identifies the counterpart or target in a relational event.

If `object` is present, `subject` MUST also be present.

Examples:

```text
vehicle:A → facility:X
entity:A  → entity:B
track:A   → identity:Y
```

### 14.3 Entity resolution is outside Core

Identity confidence, identifier authority, same-as resolution and correlation graphs are intentionally outside Core 0.1. Profiles or future specifications may address them without changing the basic `subject`/`object` representation.

---

## 15. Semantic identifiers

`modality`, `feature`, `action`, and `state` (when supplied) use qualified semantic identifiers.

Examples:

```text
xq:presence
xq:enter
xq.mob:dwell
org.example:signal
```

The syntax is specified in `NAMESPACES.md`.

Registered `xq:` terms are defined in `vocabulary/xq-core-vocabulary.json`. A syntactically valid identifier is not automatically a registered Core term.

---

## 16. `feature`

`feature` identifies the concept, property or phenomenon being described.

Examples in the current Core registry include:

```text
xq:track
xq:presence
xq:observation
xq:trajectory
```

The Core vocabulary is intentionally small and experimental.

---

## 17. `action`

`action` identifies the occurrence, transition or semantic operation affecting the feature.

Examples:

```text
xq:start
xq:end
xq:enter
xq:leave
xq:gap
xq:discontinuity
```

Domain-specific actions SHOULD use a profile or third-party namespace rather than being prematurely promoted to Core.

For example, Mobility Profile 0.1 defines:

```text
xq.mob:stay
xq.mob:dwell
```

---

## 18. `state`

`state` is OPTIONAL and identifies a human/domain-readable semantic state resulting from or associated with the event.

Examples:

```text
xq:present
xq:absent
xq:active
xq:inactive
xq:interrupted
xq:discontinuous
```

When a registered semantic composition defines a required state, a vocabulary-conforming producer MUST use that state.

### 18.1 Source-reported status and semantic state

A source-native status, mode, classification or state label is evidence supplied by that source. It MUST NOT be copied into Core `state` merely because a similarly named Core state exists.

A producer MAY map a source-reported value into Core `state` only when at least one of the following applies:

1. the applicable published profile normatively defines that mapping;
2. the producer independently derives the state from observations under documented rules; or
3. the source-reported state has been explicitly validated under documented rules.

When a source-reported value is analytically useful but is not promoted into Core `state`, it SHOULD be retained in `context` using a descriptive key such as `reported_navigation_status`.

This rule exists to prevent the semantic layer from silently converting source assertions into trusted analytical state. AIS navigational status is a representative case: a vessel may transmit a published navigational-status value, while an eventizer may independently derive movement or presence semantics from observed position history.

---

## 19. `polarity`

`polarity` is REQUIRED and MUST be one of:

```text
-1
 0
+1
```

Core interpretation:

```text
-1  negative / departure / reduction / termination
 0  neutral / observation / persistence / non-directional state
+1  positive / arrival / increase / initiation
```

Polarity does not replace `action` or `state`.

Examples:

```text
presence / enter   → +1
presence / leave   → -1
track / start      → +1
track / end        → -1
observation / gap  →  0
```

JSON Schema can validate the numeric domain but cannot validate every semantic combination. Registered compositions therefore define semantic bindings such as required polarity.

An event may be structurally valid yet semantically invalid. For example:

```json
{
  "feature": "xq:presence",
  "action": "xq:enter",
  "polarity": -1
}
```

is rejected by Core semantic conformance because `xq:presence.enter` requires `+1`.

---

## 20. Registered compositions

A composition is a documented combination of `feature`, `action`, and optional `state` with semantic constraints.

Example registry entry:

```json
{
  "id": "xq:presence.enter",
  "feature": "xq:presence",
  "action": "xq:enter",
  "required_state": "xq:present",
  "required_polarity": 1
}
```

Composition IDs are catalogue/documentation identifiers. They do not replace the separate wire fields.

A Core Vocabulary producer claiming use of a registered composition MUST obey its required bindings.

---

## 21. `magnitude` and `unit`

`magnitude` is OPTIONAL and represents the primary scalar associated with the event.

If `magnitude` is present, `unit` MUST also be present.

Examples:

```text
presence dwell            duration / s
observation gap           duration / s
trajectory discontinuity  distance / m
third-party signal        power / dBm
```

JSON does not define `NaN`, positive infinity or negative infinity. Producers MUST NOT emit non-standard non-finite numeric tokens.

`unit` MAY be supplied without `magnitude` if a profile has a valid reason, although producers SHOULD normally omit unused fields.

Recommended unit strings are listed in the Core vocabulary registry. Core 0.1 does not define dimensional conversion rules.

---

## 22. `location`

Core 0.1 defines an optional point location:

```json
{
  "lat": 51.501,
  "lon": -0.142,
  "alt": 120,
  "alt_unit": "m",
  "accuracy_m": 23
}
```

Requirements:

- `lat` MUST be in `[-90, 90]`;
- `lon` MUST be in `[-180, 180]`;
- if `alt` is present, `alt_unit` MUST be present;
- `accuracy_m`, when present, MUST be non-negative.

Core 0.1 does not define lines, polygons, bearings, uncertainty ellipses or footprints. Profiles MAY carry those in `context` or qualified extensions.

---

## 23. `confidence`

`confidence` is OPTIONAL and, when used, MUST be a number in `[0,1]`.

It expresses producer confidence in the event assertion as a whole unless a profile explicitly defines a narrower meaning.

Producers MUST NOT use a single confidence scalar to silently conflate distinct concepts such as positional accuracy, source reliability, identity confidence and model probability.

Where multiple quality dimensions matter, profiles SHOULD define them explicitly in `context`.

---

## 24. `provenance`

`provenance` is OPTIONAL at Core structural level but is strongly RECOMMENDED for normalized observations, transitions, derived events, fusion results and assessments.

Defined Core provenance fields are:

```text
producer
producer_version
method
parents[]
source_records[]
parameters{}
```

### 24.1 `producer`

Identifies the software component, analytical process or workflow that produced the event.

### 24.2 `producer_version`

Identifies the producer implementation/version materially associated with event semantics.

### 24.3 `method`

Describes production method. Example values include:

```text
manual
algorithmic
hybrid
```

Core does not constrain these strings in 0.1.

### 24.4 `parents`

Immediate parent Core Event IDs from which the event was derived.

Producers SHOULD list immediate parents rather than every transitive ancestor.

### 24.5 `source_records`

Opaque identifiers or locators for source-native evidence.

### 24.6 `parameters`

Configuration values that materially affect derivation semantics.

Profiles MAY require specific parameters.

### 24.7 Provenance extensions

Unlike most of the Core Event object, the provenance object is intentionally extensible. Producers MAY add additional fields. Extension provenance fields SHOULD use qualified names when collision or semantic ownership matters.

Consumers performing a lossless transformation SHOULD preserve unknown provenance fields.

---

## 25. `markings`

`markings` is an OPTIONAL array of unique, opaque strings carrying deployment-specific handling labels.

Example:

```json
"markings": ["example:internal"]
```

Core assigns no access-control, classification, releasability or policy semantics to these values.

**The field is not a security model.**

---

## 26. `context`

`context` is an OPTIONAL object for source-, domain-, profile- or application-specific evidence that does not belong in Core.

Example:

```json
{
  "context": {
    "frequency_hz": 433920000,
    "bandwidth_hz": 25000,
    "bearing_deg": 137.2
  }
}
```

Rules:

1. `context` MUST NOT redefine Core field semantics.
2. Consumers claiming lossless transformation SHOULD preserve unknown context fields.
3. Profiles SHOULD document context fields they rely on for conformance.
4. Sensitive context SHOULD be protected according to deployment policy.

---

## 27. Relational structure

If `object` is present, the event is relational in structure and `subject` is REQUIRED.

Relational structure is independent of `class`.

Examples:

```text
class=observation   subject sensor:A  object emitter:B
class=derived       subject entity:A  object entity:B
class=assessment    subject track:A   object identity:Y
```

Core 0.1 supports a single subject/object pair. N-ary relation modeling is out of scope.

---

## 28. Observation versus interpretation

Producers MUST choose `class` according to the epistemic status of the event, not merely the source system.

Example progression:

```text
source position record
     ↓
normalized_observation
     ↓
transition: presence enter
     ↓
derived: visit
     ↓
fusion: cross-modal association
     ↓
assessment: probable identity
```

Each layer SHOULD preserve provenance to its immediate inputs.

---

## 29. Fusion

A `fusion` event is a specialized derived event that materially combines multiple evidence inputs.

A fusion producer SHOULD provide:

- `provenance.parents` and/or `source_records`;
- `producer` and `producer_version`;
- material parameters;
- confidence where meaningful.

The modality SHOULD describe the data domain, not duplicate fusion class. `xq:multimodal` is available when no single modality adequately characterizes the event.

---

## 30. Assessment

An `assessment` event represents a judgment, estimate or hypothesis rather than direct observation.

Assessment events SHOULD include provenance and MAY include `confidence`.

A manually produced assessment uses:

```text
class = assessment
provenance.method = manual
```

rather than a separate `manual` class.

---

## 31. Corrections and supersession

Core 0.1 does not define a normative correction, retraction or supersession mechanism.

Producers SHOULD prefer immutable event publication. Deployments that need correction semantics MAY define qualified extension events or provenance/context conventions, but those conventions are not Core-conformant semantics merely because they are structurally valid.

A future Core revision may standardize this area after real implementation experience.

---

## 32. Duplicate and corroborating events

A duplicate record and an independently corroborating event are different analytical concepts.

Producers MAY deduplicate repeated source records according to documented normalization rules. They MUST NOT collapse independent observations solely because time/location/semantics are similar.

---

## 33. Collection envelope

Core Events can be serialized individually or as a JSON array/JSONL stream without an envelope.

For small bundles, `schema/crosscue-event-collection.schema.json` defines an OPTIONAL envelope:

```json
{
  "xq_version": "0.1",
  "type": "event_collection",
  "generated_at": "2026-08-30T12:00:00Z",
  "producer": "example-exporter",
  "events": []
}
```

Within a collection envelope, event `id` values MUST be unique.

The collection envelope is not a transport protocol.

---

## 34. JSON serialization

JSON serialization MUST conform to `schema/crosscue-event.schema.json` plus the semantic requirements of this specification.

Objects are unordered. Consumers MUST NOT depend on JSON member order.

Numbers MUST be valid JSON numbers.

Character encoding SHOULD be UTF-8.

---

## 35. JSON Lines serialization

A JSONL representation MAY serialize exactly one Core Event per line.

Each line MUST independently contain a complete valid JSON object.

Blank lines SHOULD NOT be emitted.

JSONL ordering does not change event semantics.

---

## 36. Ordering

Event streams SHOULD normally be ordered by `event_time` when ordering is analytically relevant.

Producers requiring deterministic ordering for coincident events SHOULD document a secondary sort, for example:

```text
event_time
subject
source
feature
action
id
```

Arrival order MUST NOT be assumed to equal occurrence order.

---

## 37. Core vocabulary

The machine-readable Core vocabulary is `vocabulary/xq-core-vocabulary.json`.

Every term includes at least:

- identifier;
- kind;
- definition;
- status.

Where meaningful it also includes:

- examples;
- allowed polarities;
- typical units;
- "do not confuse with" guidance.

Core 0.1 terms are marked `experimental`.

A term's presence in a syntactically valid event does not make it a registered Core term. Registry membership determines registered Core vocabulary.

---

## 38. Core vocabulary promotion policy

New `xq:` Core terms SHOULD normally demonstrate consistent semantics in at least two materially different modalities and have fixtures before promotion.

Domain-specific terms SHOULD begin in a profile or third-party namespace.

This policy is intentionally conservative: a small Core that survives multiple domains is preferred to a large speculative ontology.

---

## 39. Namespace rules

The normative namespace rules are in `NAMESPACES.md`.

Core 0.1 allocates only:

```text
xq:
xq.mob:
```

Other apparent `xq.<profile>:` names are not official unless registered in `vocabulary/xq-namespaces.json`.

Third parties SHOULD use a qualified namespace they control.

---

## 40. Profiles

Profiles extend Core for a specific domain without redefining Core semantics.

A profile MAY:

- allocate profile-specific semantic terms;
- define required `context` fields;
- require provenance fields/parameters;
- define eventization algorithms or semantic thresholds;
- provide additional conformance fixtures;
- define analytical projections that are not Core Events.

A profile MUST NOT:

- redefine the meaning of a registered Core field;
- assign a conflicting meaning to a registered `xq:` term;
- make source-native schemas part of Core itself.

---

## 41. Mobility Profile 0.1

The first published profile is `profiles/crosscue-mobility-0.1.md` with wire identifier:

```text
xq.mob:profile-0.1
```

It maps the current reference mobility eventizer:

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

into Core semantics.

`STAY` and `DWELL` deliberately use the profile namespace because their distinction depends on configured mobility eventization thresholds.

---

## 42. Conformance layers

Conformance is layered:

```text
structural conformance
        ↓
Core semantic conformance
        ↓
Core vocabulary conformance (optional claim)
        ↓
profile conformance (optional claim)
```

### 42.1 Structural conformance

Validation against the JSON Schema.

### 42.2 Core semantic conformance

Compliance with semantic MUST/MUST NOT rules not fully expressible in JSON Schema, such as time ordering and composition bindings.

### 42.3 Core vocabulary conformance

Correct use of registered `xq:` terms and composition constraints.

### 42.4 Profile conformance

Compliance with all additional normative profile mappings and fixtures.

See `CONFORMANCE.md`.

---

## 43. Producer conformance

A Core 0.1 Producer MUST:

1. emit structurally valid Core Events;
2. obey Core semantic MUST/MUST NOT rules;
3. emit `xq_version = "0.1"`;
4. provide stable event IDs;
5. use explicit polarity in `{-1,0,1}`;
6. provide `unit` when `magnitude` is present;
7. use qualified identifiers for modality, feature, action and state;
8. provide `subject` whenever `object` is present;
9. not use `context` to redefine Core semantics.

A producer claiming Core Vocabulary conformance MUST additionally use registered `xq:` compositions according to their semantic bindings.

---

## 44. Consumer conformance

A Core 0.1 Consumer MUST:

1. parse Core-valid events;
2. preserve zero polarity as meaningful;
3. preserve the distinction between event classes;
4. tolerate unknown qualified semantic identifiers unless it explicitly claims a restricted-vocabulary mode;
5. tolerate unknown `context` and provenance extension fields;
6. preserve unknown extension fields when claiming a lossless transformation.

A consumer MUST NOT interpret an unknown qualified identifier as if it were a registered Core term.

---

## 45. Machine validation and fixtures

The repository provides:

```text
schema/
conformance/valid/
conformance/invalid/
tools/validate.py
```

The reference validator demonstrates the intended split between structural and semantic validation.

Conforming implementations are not required to use the reference validator or Python.

---

## 46. Privacy, security and dual use

The model can increase analytical power by making correlation easier. This can also increase the sensitivity of datasets and derived products.

Implementers SHOULD consider:

- legal authority and purpose limitation;
- data minimisation;
- re-identification risk;
- source protection;
- access control;
- auditability;
- retention;
- redaction;
- compartmentation;
- derived-data sensitivity.

Pseudonymous identifiers do not guarantee anonymity.

The `markings` field is not an enforcement mechanism.

Public conformance fixtures SHOULD be synthetic.

---

## 47. Out of scope for Core 0.1

The following are intentionally not standardized in Core 0.1:

- generalized entity resolution and identifier authorities;
- complex geometry and uncertainty ellipses;
- confidence decomposition and source-reliability scales;
- security/classification semantics;
- correction/retraction/supersession;
- n-ary relationships;
- graph query languages;
- storage engines;
- event buses/transport protocols;
- canonical unit conversion;
- domain-specific RF/AIS/ADS-B/imagery fields;
- tracks, segments and presence intervals as Core objects.

---

## 48. Analytical projections

Profiles and applications MAY materialize event-derived views such as:

```text
observations
tracks
segments
presence_intervals
encounters
associations
behaviour summaries
```

These views are not Core Events merely because they are derived from Core Events.

A projection SHOULD remain traceable to its evidence and eventization parameters.

---

## 49. Reproducibility

For deterministic eventizers, the desired property is:

```text
same normalized observations
+ same producer/version
+ same eventization parameters
= same semantic events
```

Profiles whose semantics depend on thresholds MUST specify how effective parameters are preserved.

---

## 50. Versioning

Package/documentation version:

```text
0.1.0
```

Wire version:

```text
xq_version = "0.1"
```

The 0.1.x line is compatibility-frozen at 0.1.0:

- existing Core field meanings MUST NOT be changed incompatibly within 0.1.x;
- existing registered `xq:` term meanings and Core composition bindings MUST NOT be changed incompatibly within 0.1.x;
- patch releases MAY correct editorial defects, validator defects, or add non-normative examples and tests that clarify existing semantics;
- new or incompatible Core semantics SHOULD target a later Core version, normally 0.2 or greater;
- a change that breaks Core wire semantics requires an explicit `xq_version` decision.

Profile versions evolve independently and MAY add domain-specific semantics without changing Core.

---

## 51. Licensing

This specification and repository materials are licensed under the Apache License, Version 2.0. See `LICENSE`.

The licence does not itself grant rights to third-party trademarks, source data, proprietary formats, or data-processing permissions.

---

## 52. Cross-domain semantic examples

The repository includes non-normative semantic examples for:

```text
mobility
AIS
ADS-B
RF
imagery
```

They are collected in [`examples/SEMANTIC-EXAMPLES.md`](examples/SEMANTIC-EXAMPLES.md).

The AIS, ADS-B, RF and imagery examples demonstrate Core semantics only. They do **not** allocate profile namespaces or claim profile conformance. Coarse Core modality identifiers such as `xq:ais` and `xq:rf` do not imply that `xq.ais:` or `xq.rf:` profile namespaces exist.

These examples are deliberately conservative: source-native status and measurements remain evidence, while derived semantic transitions require eventizer logic and provenance.

---

## Appendix A — Minimal valid event

```json
{
  "xq_version": "0.1",
  "id": "evt:1",
  "event_time": "2026-08-30T10:00:00Z",
  "source": "example",
  "modality": "org.example:test",
  "class": "observation",
  "feature": "org.example:feature",
  "action": "org.example:observed",
  "polarity": 0
}
```

## Appendix B — Core Mobility ENTER

```json
{
  "xq_version": "0.1",
  "id": "evt:mob-enter-001",
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

The profile requires additional provenance parameters; the abbreviated example above illustrates semantic fields only. See the profile and conformance fixture for the complete conforming event.

## Appendix C — Working definition

> A Crosscue Event Model Core Event is a temporally anchored representation of an observation, normalized observation, state transition, derived fact, fusion result or analytical assessment, expressed through a small semantic vocabulary and carrying sufficient identity, quantitative, spatial and provenance information for interoperable correlation and explanation.

