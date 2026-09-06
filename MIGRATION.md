# Migration to Crosscue Event Model Core 0.1

This document records the migration from the exploratory `csv2generic` object and the earlier draft naming.

## 1. Public naming

Earlier draft name:

```text
XQ Event Model (XQEM)
```

Current public name:

```text
Crosscue Event Model
```

The semantic namespace remains:

```text
xq:
```

The aim is to decouple the human-facing project name from the wire vocabulary.

## 2. Version field

Earlier draft:

```json
"xqem_version": "0.1"
```

Current draft:

```json
"xq_version": "0.1"
```

This is an intentional pre-release breaking change.

## 3. Exploratory CLI field migration

| Exploratory CLI | Core 0.1 | Reason |
|---|---|---|
| `timestamp` | `event_time` | occurrence time separated from observation/processing time |
| no event ID | `id` REQUIRED | correlation and provenance |
| no class | `class` REQUIRED | epistemic/derivation status |
| `entity_id` | `subject` | unary + relational consistency |
| `element` | `action` | clearer semantic verb/occurrence axis and avoids collision with domain-native element terminology |
| no counterpart | `object` optional | relational structure |
| no interval end | `end_time` optional | interval semantics |
| no confidence | `confidence` optional | event-level assertion confidence |
| provenance absent/in context | `provenance` | first-class reproducibility |
| no handling field | `markings` optional | opaque handling-label transport |

## 4. Semantic qualification

Exploratory values:

```json
{"modality":"mobility","feature":"presence","element":"enter","state":"present"}
```

Core 0.1:

```json
{"modality":"xq:mobility","feature":"xq:presence","action":"xq:enter","state":"xq:present"}
```

## 5. Core `element` to `action` rename in draft.4

Draft.3 used:

```json
{"feature":"xq:presence","element":"xq:enter"}
```

Draft.4 uses:

```json
{"feature":"xq:presence","action":"xq:enter"}
```

This is an intentional pre-release breaking change. `action` more clearly describes the semantic occurrence/transition axis and avoids collision with domain-native terms such as an RF detector `elementID`.

## 6. Class cleanup from draft.2

Draft.2 used one enum containing:

```text
observation
normalized_observation
transition
relational
derived
fusion
assessment
manual
```

Draft.3 removes `relational` and `manual` from `class` because they describe orthogonal concepts.

Relational structure is now represented by `subject` + `object`.

Production method is represented by `provenance.method`, for example:

```text
manual
algorithmic
hybrid
```

The class enum is now:

```text
observation
normalized_observation
transition
derived
fusion
assessment
```

## 7. Modality cleanup

Draft.2 registered `xq:fusion` and `xq:assessment` modalities. Draft.3 removes them because they duplicate event class.

Cross-modal fusion and assessment may use:

```text
modality = xq:multimodal
class = fusion | assessment
```

or another appropriate qualified modality.

## 8. Mobility STAY/DWELL migration

Draft.2 represented:

```text
xq:stay
xq:dwell
```

as Core actions.

Draft.3 moves them to the Mobility Profile:

```text
xq.mob:stay
xq.mob:dwell
```

because their distinction depends on a configured mobility dwell threshold and has not yet been demonstrated as a stable cross-domain Core concept.

Other Mobility mappings remain semantically equivalent.

## 9. Profile identifier

Draft.3 uses:

```text
xq.mob:profile-0.1
```

## 10. Provenance extension

Draft.2 closed the provenance object to unknown properties. Draft.3 allows provenance extensions so producer/model/audit metadata can evolve without forcing Core schema revisions.

Known Core provenance fields remain defined and SHOULD be used where applicable.
