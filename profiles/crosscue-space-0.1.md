# Crosscue Event Model Space Profile 0.1 — draft

**Status:** Experimental draft for review  
**Profile identifier:** `xq.space:profile-0.1`  
**Depends on:** Crosscue Event Model Core 0.1  
**Profile modality:** `xq.space:orbital`  
**Proposed namespace:** `xq.space:` — not officially allocated

This draft has the experimental maturity posture of Core 0.1, but is not an
officially allocated profile. Inclusion in this repository or recognition by its
validator does not allocate the namespace. The namespace registry and Core
vocabulary are unchanged. Draft bindings may change before official publication;
implementers should identify the event-model commit used.

## 1. Scope and implementation evidence

This profile represents orbital consistency residuals and separates them from
identity and cause hypotheses. It defines exactly three domain event types.
They are encoded as `feature` values, not additions to Core's `class` enum.
There are no optical or event-based vision (EVS) event types in this draft.

The implemented reference is the `orbital-events` `sgp4_consistency` method,
version `0.2` (experimental). Its source-native results are mapped here; the
node does not currently emit this profile's Core JSON or its two hypothesis
types. The latter are provisional contracts for downstream assessment producers.
An identity hypothesis is not a prerequisite for a residual about a catalogue
object. A residual does not itself establish a cause hypothesis.

The mapping was reviewed against the `orbital-events/` subtree of the `barsoom`
checkout at commit `f9d1da31bec0bcb4144bacdcf89bda7530d38767`, in particular
`internal/processor/{event,residuals,scoring}.go`, `internal/public/model.go`,
`internal/identity/id.go`, and `docs/CALIBRATION.md`, and the database export
header `orbital_events_202609220946.csv` supplied for review. That live extract is
not distributed here. Section 5 reproduces its complete column mapping; the
examples and checks need neither that extract nor the producer repository.

This is a semantic interchange profile, not a required database schema or
transport. Other producers may implement the same meanings with different
source fields and documented analytical methods. The reference method's
thresholds are not universal orbital constants.

## 2. Common bindings

Events claiming this draft MUST contain `profile: xq.space:profile-0.1`,
`modality: xq.space:orbital`, a non-empty `subject`, and `polarity: 0`.
They MUST use one of these bindings:

| Feature / domain event type | Core class | Action | Primary magnitude | Maturity |
|---|---|---|---|---|
| `xq.space:consistency_residual` | `derived` | `xq:observed` | Position residual, `km` | Source-native result implemented |
| `xq.space:identity_hypothesis` | `assessment` | `xq.space:assessed` | Omitted | Provisional; not emitted by node |
| `xq.space:cause_hypothesis` | `assessment` | `xq.space:assessed` | Omitted | Provisional; not emitted by node |

`xq:observed` describes measurement of a computed discrepancy here; `derived`
preserves its analytical origin. No binding asserts a physical state transition.
`state` MUST be omitted. Signed components do not change event polarity.

Every event MUST provide non-empty `provenance.producer`, `producer_version`
and `method`, and evidence in `parents` and/or `source_records`. `parents`
contains Core Event IDs only; native input IDs belong in `source_records`.
Producer/version identifies the adapter or assessor, not the SGP4 method version.
`provenance.method` records production mode, such as `algorithmic` or `manual`.

The vocabulary stub is [xq-space-vocabulary.json](xq-space-vocabulary.json).
Its modality and action support the three types; they are not additional types.
No term is promoted to Core, including the modality.

## 3. Consistency residual

`subject` MUST be the catalogue-scoped referent `norad:<positive decimal ID>`
for the reference mapping, without leading zeros. It does not independently
verify the physical object's identity. Catalogue names are labels in context.
`object` MUST be omitted.

`magnitude` MUST be a finite, non-negative position residual norm with `unit: km`.
For `sgp4_consistency` 0.2 it is the norm of the later element-set position minus
the earlier element-set position propagated to the later epoch. Velocity
residual is a norm in km/s, not inferred manoeuvre delta-v. Signed components
are in the **later state's RTN frame**: radial along its position, cross-track
along its angular momentum, and in-track = cross-track cross radial. Components
are later minus earlier propagated state. These conventions MUST be retained.

`context.residuals` MAY contain `velocity_km_s`, `radial_km`, `in_track_km`,
and `cross_track_km`. Available values MUST be finite; velocity is non-negative.
When all three components are present, their norm MUST agree with `magnitude`
within a relative tolerance of `1e-6` or absolute tolerance of `1e-6 km`.
Unavailable optional measurements are omitted or null, never zero-filled.

`context.element_changes` contains later-minus-earlier published mean-element
differences with the units specified in Section 5. These are distinct from
propagated state residuals. This draft residual binding MUST omit Core's
geographic `location` field; the mapping does not derive a geographic location.
Orbital vectors or element changes are not geographic point coordinates.

### 3.1 Time

`event_time` MUST equal `context.reporting_epoch`, the later comparison epoch.
This anchors a derived comparison, not an inferred physical change at that time.
`context.observation_window` MUST contain `start`, `end`, and `duration_hours`:
start < end, end = reporting epoch, and duration > 0. `end_time` MUST be omitted:
the input evidence window is not an asserted duration of a physical event.

All event and profile timestamps MUST be RFC 3339 UTC (`Z`). For the reviewed
CSV's millisecond timestamp precision, duration agreement allows `0.002 s`
absolute difference. Retain supplied duration precision; do not recompute input
IDs from formatted timestamps. Exports with less precision need a separately
documented mapping rather than silently widening this tolerance.

`created_at` is database insertion time, not proof of acquisition, processing or
assessment time. Preserve it as source metadata. Omit `observed_time` unless its
meaning and origin are independently known.

### 3.2 Provenance and quality

Residuals MUST include `provenance["xq.space:method"]` with non-empty `name`,
`version`, and `maturity`. The reference values are `sgp4_consistency`, `0.2`,
and `experimental`; other versions must document their own meaning.

`provenance["xq.space:inputs"]` MUST contain `earlier` and `later` objects, each
with `id`, `source`, and `representation`. IDs MUST be distinct and listed in
`source_records`. Use literal `unknown` for unavailable source/representation,
not an inferred supplier. Optional `reconstructed` values are booleans or null.
This input metadata is preserved evidence, not a guarantee that a legacy ID was
derived from complete original input information.

`context.quality_flags` MUST be an object. Preserve flags such as
`legacy_identity`; an empty object means no flags supplied, not verified quality.
Optional processing metadata belongs in `provenance["xq.space:processing"]`.
A run ID alone is not an immutable snapshot or a claim of full reproducibility.

`context.heuristic`, when supplied, contains `score`, `severity`, and optionally
`detection_tier`, with `calibrated: false`. Available score is finite and
non-negative; available tiers are `low`, `medium`, or `high`. Preserve the stored
tier, including rounding boundary cases; do not infer it from share-card labels.
Core `confidence` MUST be omitted for residuals. Heuristic score, descriptive
history percentile, and robust deviation are not probabilities of identity,
physical cause, detection correctness, or operational risk.

`context.calibration` is optional/null descriptive history. Under
`object_position_v1`, baseline is in km, robust deviation is dimensionless,
percentile is 0–100, population is `self`, and the window is
`P28D;max_samples=256;reporting_epoch;exclude_current`. Preserve version, population,
window, and sample count with supplied statistics. This history includes valid
subthreshold pairs, so it cannot be reconstructed from emitted residual records
alone. Missing statistics stay unavailable; no fabricated default population.

## 4. Provisional hypotheses

Both hypothesis types MUST use `class: assessment`, `action: xq.space:assessed`,
and their own stable event ID. `event_time` is when the judgment was issued,
not a backdated physical-event time. `end_time`, `magnitude`, `unit`, and `state`
MUST be omitted. Evidence windows, if supplied, belong in context.

`context.assessment` MUST provide non-empty `statement`, `rationale`, and
`limitations`. The statement is a proposed interpretation; its text is not a
new registered vocabulary or a confirmed fact. Evidence MUST be linked through
provenance. Producers MUST retain contrary evidence and material alternatives
where available. Missing evidence cannot be supplied by copying a source label.

For `identity_hypothesis`, `subject` is the unresolved/source-scoped referent
(for example a track); `object` MUST identify the proposed candidate and MUST
differ from `subject`. One candidate is represented per event. An association
does not merge identifiers, assert equivalence, or rewrite preceding residuals.

For `cause_hypothesis`, `subject` identifies the referent whose evidence is being
explained. `object` MUST be omitted; the proposed explanation is the assessment
statement. `context.assessment.alternatives` MUST be a non-empty array of
non-empty strings identifying competing explanations. Evidence links MUST
identify what is being explained. A residual alone does not uniquely establish
manoeuvre, drag, input artefact, collision, or any other physical cause.

Core `confidence` MAY be supplied only with a non-empty
`context.assessment.confidence_basis` explaining what the number represents and
its derivation/limitations. It MUST NOT be obtained by rescaling the residual
score or percentile. Omission is the default; this draft defines no calibrated
hypothesis model or probability scale beyond Core's numeric range.

## 5. Reference CSV mapping

This table covers every column in the reviewed database export. Paths below are
output paths, not new Core fields. `P` abbreviates `provenance`, `C` abbreviates
`context`, `M` is `P["xq.space:method"]`, `I` is `P["xq.space:inputs"]`, and
`S` is `C.source_record`. Ordinary context keys and qualified provenance keys
are field names; they do not allocate additional semantic terms.

| CSV column(s) | Output / rule |
|---|---|
| `public_id` | `id = <source>:<public_id>`; retain original in `S.public_id`. `source` is a stable producer-instance identifier chosen by the adapter. Preserve native ID; do not rehash the rounded export. |
| `id` | `S.database_id` as a string; database-local only. Never the sole public event ID. |
| `norad_id` | `subject = norad:<decimal ID>` |
| `object_name` | `C.catalogue.name`; source-reported label, not resolved identity |
| `event_time` | Legacy alias of `reporting_epoch`; compare after normalization, retain in `S.event_time` if retaining aliases |
| `tle1_epoch`, `tle2_epoch` | Legacy aliases of observation-window start/end; not raw TLE content |
| `delta_t_hours` | Legacy alias of `window_duration_hours`, in hours |
| `residual_pos_km` | `magnitude`, `unit: km` |
| `residual_vel_km_s` | `C.residuals.velocity_km_s` |
| `residual_radial_km` | `C.residuals.radial_km` |
| `residual_intrack_km` | `C.residuals.in_track_km` |
| `residual_crosstrack_km` | `C.residuals.cross_track_km` |
| `delta_semi_major_km` | `C.element_changes.semi_major_axis_km` |
| `delta_inclination_deg` | `C.element_changes.inclination_deg` |
| `delta_eccentricity` | `C.element_changes.eccentricity` (dimensionless) |
| `delta_mean_motion` | `C.element_changes.mean_motion_rev_per_day` |
| `score` | `C.heuristic.score`; experimental method score, not magnitude or confidence |
| `significance` | Legacy alias of `severity`; retain as `S.significance` only if retaining aliases. Not statistical significance. |
| `assessment` | Parse JSON into `S.assessment` if retained. Residual metadata/duplicates, not `class: assessment` and not a cause hypothesis. |
| `method`, `method_version` | `M.name`, `M.version`; maturity is `experimental` for documented reference 0.2, not inferred for unknown methods |
| `source` | `S.source` (for example `processor`); not sufficient to identify the producer instance in Core `source` |
| `created_at` | `S.created_at`, normalized UTC; insertion timestamp |
| `earlier_input_id`, `later_input_id` | `I.earlier.id`, `I.later.id`, also in `P.source_records` |
| `earlier_source`, `later_source` | `I.earlier.source`, `I.later.source` |
| `earlier_representation`, `later_representation` | `I.earlier.representation`, `I.later.representation` |
| `earlier_reconstructed`, `later_reconstructed` | `I.earlier.reconstructed`, `I.later.reconstructed`; booleans or null |
| `processor_run_id` | `P["xq.space:processing"].run_id` |
| `observation_window_start`, `observation_window_end` | `C.observation_window.start`, `.end` |
| `reporting_epoch` | `event_time` and `C.reporting_epoch` |
| `window_duration_hours` | `C.observation_window.duration_hours` |
| `severity` | `C.heuristic.severity`; canonical stored tier |
| `quality_flags` | Parse JSON object into `C.quality_flags`, preserving unknown flags |
| `revision` | `S.revision`; source revision only, not a Core revision mechanism |
| `superseded_by`, `superseded_at` | `S.superseded_by`, `.superseded_at`; preserve native reference and UTC timestamp when available |
| `cal_rolling_baseline` | `C.calibration.rolling_baseline` (km) |
| `cal_robust_deviation` | `C.calibration.robust_deviation` (dimensionless, signed) |
| `cal_percentile` | `C.calibration.percentile` (0–100, not 0–1 confidence) |
| `cal_population`, `cal_window` | `C.calibration.population`, `.window` |
| `cal_sample_count`, `cal_version` | `C.calibration.sample_count`, `.version` |

The adapter supplies `xq_version`, `profile`, `modality`, `feature`, `class`,
`action`, `polarity`, `unit`, Core `source`, and its own provenance. The CSV has
no identity/cause hypothesis output to map. No top-level `assessment` field
exists in Core; profile assessment content uses Section 4.

### 5.1 Parsing, conflicts, and missing data

Use a CSV parser with quoted-field support, then parse embedded JSON objects.
Do not split rows on commas. Parse numbers as finite JSON numbers, booleans as
booleans, and dates with their explicit numeric offsets. For example,
`2026-01-02 13:00:00.000 +0100` becomes `2026-01-02T12:00:00Z`.

Blank cells in this export are treated as unavailable. The export does not
reliably distinguish SQL NULL from an empty string; do not claim a lossless
database round-trip. Omit or use null for unavailable optional context values;
never emit null in a Core field whose schema disallows it. Entirely blank
calibration columns produce null/omitted calibration, not a zero baseline.

Canonical columns take precedence over legacy aliases only when the aliases
are absent or agree (using the time/rounding tolerances above). If populated
aliases or duplicate assessment values contradict canonical values, the adapter
MUST reject/quarantine the row for review rather than silently choose a meaning.
Legacy aliases MAY fill missing canonical values when their documented meaning
agrees; record the fallback column names in `S.fallback_fields`.

Rows missing a public ID, subject, position residual, method name/version,
input IDs, or usable time window MUST NOT claim this draft's residual binding.
Missing optional provenance is not permission to fabricate it. Preserve unknown
quality flags. Extra source columns should be preserved in source context when
lossless transformation is claimed, subject to publication policy.

Supersession metadata is descriptive only. Consumers must not automatically
delete/retract other Core Events based on it. This draft does not establish a
revision protocol or solve conflicting source revisions sharing one public ID.

## 6. Worked examples

Both files below are wholly synthetic, including IDs, catalogue references and
judgments. They assert no facts about real catalogue objects. The simplified
native IDs are illustrative opaque strings, not valid `o1_`/`i1_` hash fixtures.

1. [Residual](../examples/space-consistency-residual.json): a six-hour pair with
   signed components `(-3, 4, 0) km` gives a `5 km` norm. The method 0.2 score
   is `5`: neither the in-track nor cross-track multiplier applies, and the
   tier is `low`. The earlier input is `2026-01-02T06:00:00Z`; the later input
   and reporting epoch are `12:00:00Z`. A hypothetical CSV row with those values
   maps to `class: derived`, `subject: norad:990001`, `magnitude: 5`, `unit: km`.
   `legacy_identity` and null calibration illustrate unavailable information.
2. [Assessment collection](../examples/space-hypotheses.json): includes that
   residual, a proposed association of a synthetic track with its catalogue
   referent, and a separate proposed explanation of the residual. Assessments
   link to the included event and explicitly described fictional source records.
   Their issue times are later than the cited evidence. Neither changes the
   original residual. No confidence is invented and neither hypothesis is
   presented as output of orbital-events.

The collection is an illustration of independent judgments, not a pipeline in
which a residual proves identity or identity proves cause. Supporting fictional
record summaries appear under `context.example_evidence` for readers; they are
not an additional event type or a required production evidence schema.

## 7. Draft validation and limitations

From a fresh event-model clone, install the existing development dependency:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate.py --fixtures
python tools/validate.py examples/space-consistency-residual.json examples/space-hypotheses.json
```

These commands require no sibling checkout, live data, credentials, or orbital
propagator. Tests are offline after dependency installation. Deterministic
positive and negative fixtures check the draft's bindings, residual units and
norm, time windows, method/input provenance, hypothesis evidence, and separation
of residuals from confidence and causal/identity assertions.

The validator checks the mapped JSON, not CSV ingestion. It cannot verify
propagation accuracy, authenticity of evidence, ID hash derivation, completeness
of an input history, truth of a hypothesis, or whether all source columns were
faithfully mapped. A pass establishes only the implemented structural and
semantic checks, not scientific validation or official profile allocation.

Residuals are research consistency observations, not confirmed manoeuvres,
conjunction/collision risk, exact physical event times, or operational
spaceflight-safety guidance. Source attribution and handling constraints remain
the producer's responsibility. This profile does not grant redistribution rights
to source data; public fixtures contain no raw TLE/OMM or live database records.
