# Crosscue Event Model Mobility Profile 0.1

**Status:** Experimental profile  
**Profile identifier:** `xq.mob:profile-0.1`  
**Depends on:** Crosscue Event Model Core 0.1  
**Core modality:** `xq:mobility`  
**Profile namespace:** `xq.mob:`

## 1. Scope

The Mobility Profile maps normalized geospatial mobility observations and the current reference mobility eventizer into Core Events.

The reference eventizer produces:

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

This profile defines event semantics, not a required CSV schema or storage engine.

## 2. Profile claim

An event claiming Mobility Profile 0.1 conformance MUST contain:

```json
"profile": "xq.mob:profile-0.1"
```

and:

```json
"modality": "xq:mobility"
```

The reference eventizer mappings in this profile use:

```json
"class": "transition"
```

## 3. Subject

`subject` identifies the mobility entity being tracked. It is normally pseudonymous or source-scoped.

Examples:

```text
device:...
track:...
```

The profile does not define identity resolution.

## 4. Mapping

| Source event | Feature | Action | State | Polarity | Required primary magnitude | Catalogue ID |
|---|---|---|---|---:|---|---|
| START | `xq:track` | `xq:start` | `xq:active` | +1 | none | `xq:track.start` |
| STAY | `xq:presence` | `xq.mob:stay` | `xq:present` | 0 | duration, `s` | `xq.mob:presence.stay` |
| DWELL | `xq:presence` | `xq.mob:dwell` | `xq:present` | 0 | duration, `s` | `xq.mob:presence.dwell` |
| LEAVE | `xq:presence` | `xq:leave` | `xq:absent` | -1 | none | `xq:presence.leave` |
| ENTER | `xq:presence` | `xq:enter` | `xq:present` | +1 | none | `xq:presence.enter` |
| GAP | `xq:observation` | `xq:gap` | `xq:interrupted` | 0 | gap duration, `s` | `xq:observation.gap` |
| DISCONTINUITY | `xq:trajectory` | `xq:discontinuity` | `xq:discontinuous` | 0 | jump distance, `m` | `xq:trajectory.discontinuity` |
| END | `xq:track` | `xq:end` | `xq:inactive` | -1 | none | `xq:track.end` |

## 5. STAY versus DWELL

The distinction is profile-specific because it depends on the configured `dwell_threshold_s`.

### 5.1 STAY

A **STAY** is a closed stable-presence interval whose duration is **strictly less than** the effective dwell threshold.

It MUST use:

```text
feature   xq:presence
action   xq.mob:stay
state     xq:present
polarity  0
```

It MUST provide:

- `event_time` as interval start;
- `end_time` as interval end;
- `magnitude` equal to duration in seconds;
- `unit = "s"`.

### 5.2 DWELL

A **DWELL** is a closed stable-presence interval whose duration is **greater than or equal to** the effective dwell threshold.

It MUST use:

```text
feature   xq:presence
action   xq.mob:dwell
state     xq:present
polarity  0
```

It MUST provide the same interval/duration fields as STAY.

## 6. GAP

A GAP indicates an inter-observation interval exceeding the configured gap threshold.

It MUST use `magnitude` for the gap duration in seconds and `unit = "s"`.

The event location SHOULD be the first post-gap location. The pre-gap location SHOULD be retained in `context` when available.

## 7. DISCONTINUITY

A DISCONTINUITY declares that adjacent observations are not treated as one physically continuous trajectory under the effective eventizer rules.

It MUST use jump distance as `magnitude` with `unit = "m"`.

The event location SHOULD be the destination/post-break location. Origin and implied-speed evidence SHOULD be retained in `context` when available.

A discontinuity closes the current continuous-motion segment; the incoming observation begins the next segment.

## 8. ENTER and LEAVE

ENTER identifies a transition into stable presence and uses destination location.

LEAVE identifies a transition out of stable presence and uses origin location.

Distance, bearing, from/to cells and from/to coordinates are profile context rather than Core fields.

## 9. START and END

START marks the beginning of available track state for the subject.

END marks the end of available track state for the subject.

These are bookkeeping transitions; they do not imply physical appearance/disappearance outside the observed dataset.

## 10. Required eventizer provenance

Mobility event semantics depend materially on eventizer thresholds. Therefore every event claiming this profile's reference-eventizer mapping MUST provide:

```text
provenance.producer
provenance.producer_version
provenance.parameters
```

`parameters` MUST include the effective values of:

```text
geohash_precision
move_radius_m
dwell_threshold_s
gap_threshold_s
max_speed_mps
max_jump_m
confirm_moves
confirm_window_s
walk_max_speed_mps
walk_max_jump_m
```

Values need not equal reference defaults, but the effective values MUST be recorded.

This requirement is intentionally stricter than Core because the same input observations can produce different transition events under different thresholds.

## 11. Reference defaults

The current reference implementation uses:

```text
geohash precision       8
movement deadband       100 m
dwell threshold         900 s
gap threshold           7200 s
maximum speed           50 m/s
maximum jump            50000 m
move confirmation       true
confirmation window     900 s
walk max speed          6 m/s
walk max jump           8000 m
```

These are reference defaults, not universal constants.

## 12. Recommended context

The current reference producer may emit:

```text
source_event
segment_id
cell
from_cell
to_cell
from_location
to_location
travel_seconds
state_seconds
distance_m
bearing_deg
bearing_8
accuracy_m
observation_samples
observation_scatter_m
mode
implied_speed_mps
```

`context.source_event`, when supplied, MUST agree with the mapping in Section 4.

## 13. Analytical projections

A Mobility implementation MAY additionally materialize:

```text
observations
tracks
segments
presence_intervals
```

These are not Core Event objects.

### 13.1 Observations

Normalized/collapsed observations retain source evidence, time, coordinates, spatial indexing, accuracy and segment assignment.

### 13.2 Tracks

Track summaries may contain event counts, temporal coverage, movement statistics, spatial diversity, entropy, recurrence and analyzability metrics.

### 13.3 Segments

Segments represent continuous portions of a track separated by discontinuities.

### 13.4 Presence intervals

Presence intervals are interval-oriented projections of stable-presence semantics and supporting observations.

All projections SHOULD remain traceable to eventizer version and effective parameters.

## 14. Mobility-specific vocabulary

The normative profile vocabulary is `xq-mob-vocabulary.json`.

`xq.mob:stay` and `xq.mob:dwell` are profile terms in Core 0.1. They MUST NOT be presented as registered `xq:` Core terms.

## 15. Conformance

A Mobility Profile producer MUST pass applicable Core fixtures and Mobility semantic fixtures.

The packaged reference validator checks:

- mapping polarity/state;
- required eventizer provenance parameters;
- STAY/DWELL threshold classification;
- interval duration equality;
- GAP units;
- DISCONTINUITY units.
