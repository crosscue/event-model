# Cross-domain semantic examples

These examples demonstrate how several source domains use the same Crosscue Event Model fields. Mobility and Network have published profiles; AIS, ADS-B, RF and imagery remain non-normative Core-level examples and do not claim profile conformance.

The AIS, ADS-B, RF and imagery examples intentionally use only the Core semantic namespace (`xq:`) plus ordinary `context` keys. The Network example uses the published `xq.net:` namespace. No `xq.ais:`, `xq.adsb:`, `xq.rf:` or imagery profile namespace is allocated by these examples.

## Source-reported state is evidence, not semantic truth

A source may publish a status or state label. A producer MUST NOT automatically copy such a value into the Core `state` field unless the applicable profile explicitly defines that mapping or the state has been independently derived or validated.

Source-reported values SHOULD be retained in `context` when analytically useful.

AIS is a useful example. AIS Class A reports include a navigational-status field, but IMO guidance describes navigational status as information that has to be manually entered and changed by the officer of the watch. A semantic eventizer should therefore treat that value as reported evidence rather than unquestioned ground truth.

Reference:

- USCG NAVCEN, AIS Class A reports: https://www.navcen.uscg.gov/ais-class-a-reports
- IMO Revised Guidelines for the Onboard Operational Use of Shipborne AIS (A.1106(29)): https://www.navcen.uscg.gov/sites/default/files/pdf/ais/references/IMO_A1106_29_Revised_guidelines.pdf

The same principle applies generally to source-native status flags: preserve them, but do not silently elevate them into the semantic interpretation layer.

## Mobility / AdTech

File: `semantic-mobility.json`

A derived entry transition:

```text
modality  xq:mobility
class     transition
feature   xq:presence
action    xq:enter
state     xq:present
polarity  +1
```

The source family is retained only as context. A full Mobility Profile event may additionally claim `xq.mob:profile-0.1` and carry the required eventizer provenance.

## AIS

File: `semantic-ais.json`

An AIS position report is represented as an observation:

```text
modality  xq:ais
class     observation
feature   xq:position
action    xq:observed
polarity  0
```

The example deliberately omits Core `state`. The source-reported AIS navigational status is retained as:

```json
"context": {
  "reported_navigation_status": "at_anchor"
}
```

A later eventizer may derive movement, presence, port-entry, or other semantic state from the observation sequence without trusting this reported value as authoritative.

## ADS-B

File: `semantic-adsb.json`

ADS-B broadcasts position, altitude, ground speed and other aircraft data. The example represents a barometric-altitude observation:

```text
modality   xq:ads-b
class      observation
feature    xq:altitude
action     xq:observed
polarity   0
magnitude  28750
unit       ft
```

Reference:

- FAA ADS-B overview: https://www.faa.gov/about/office_org/headquarters_offices/avs/offices/afx/afs/afs400/afs410/ads-b
- FAA ADS-B FAQ: https://www.faa.gov/air_traffic/technology/equipadsb/resources/faq

A later eventizer could derive `climbing`, `descending`, take-off, landing, airspace-entry, or other transitions from sequences of observations. Those are not asserted by this raw observation example.

## RF

File: `semantic-rf.json`

The example is intentionally semantic rather than a replacement for a compact sensor-native RF event:

```text
modality   xq:rf
class      observation
feature    xq:signal
action     xq:observed
polarity   0
magnitude  -71.3
unit       dBm
```

RF-native fields such as sample index, stream ID, feature ID, detector element ID, flags, frequency or bandwidth can remain in native storage and/or `context`/provenance. A future RF Profile can define the registry mapping from compact native IDs into semantic terms.

The existing experimental RF event structure therefore remains a valid source representation rather than being replaced by the Core JSON object.


## Network — normalized connection observation

Network Profile 0.1 uses the Core modality `xq:network` and profile-specific `xq.net:` semantics. A connection is an observation of traffic to an endpoint, not proof that a persistent relationship or service exists.

```json
{
  "xq_version": "0.1",
  "id": "evt:semantic-network-001",
  "event_time": "2026-09-06T08:00:00Z",
  "source": "synthetic-network-sensor",
  "modality": "xq:network",
  "class": "normalized_observation",
  "profile": "xq.net:profile-0.1",
  "subject": "address:ip:192.0.2.10",
  "object": "endpoint:ip:198.51.100.8:443/tcp",
  "feature": "xq.net:connection",
  "action": "xq:observed",
  "polarity": 0,
  "provenance": {
    "producer": "synthetic-network-eventizer",
    "producer_version": "0.1.0",
    "method": "algorithmic",
    "source_records": [
      "synthetic:connection:1"
    ],
    "parameters": {
      "mapping": "connection-normalize"
    }
  },
  "context": {
    "observation_point": "sensor-demo",
    "protocol": "tcp",
    "originator_port": 52101,
    "responder_port": 443,
    "application_stack": [
      "tls"
    ]
  }
}
```

The Network Profile further distinguishes device, interface, address, endpoint and service referents. A MAC address is interface-scoped by default, and higher-order relationships such as `xq.net:first_observed` are derived rather than copied from a single source record.

## Imagery

File: `semantic-imagery.json`

Imagery is included as an exploratory example because it tests the distinction between event time and observed/analysis time:

```text
modality  xq:imagery
class     observation
feature   xq:presence
action    xq:observed
state     xq:present
polarity  0
```

`event_time` represents the imagery collection/event time, while `observed_time` can represent when an analyst or automated process made the observation available.

The example is intentionally modest: it asserts only that an object was observed as present. More complicated imagery semantics—footprints, uncertain geometries, object tracks, classification taxonomies and change detection—remain outside Core 0.1 and should be tested before an imagery profile is defined.

## Why these examples are in Core

The examples are intended to test whether the common semantic axes survive materially different source domains:

```text
source
modality
class
subject/object
feature
action
state
polarity
magnitude/unit
location
confidence
provenance/context
```

The Network example demonstrates the published Network Profile 0.1. The AIS, ADS-B, RF and imagery examples do not imply that those future profile semantics are complete or stable.
