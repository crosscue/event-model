# Crosscue Event Model Network Profile 0.1

**Status:** Experimental published profile  
**Profile identifier:** `xq.net:profile-0.1`  
**Depends on:** Crosscue Event Model Core 0.1  
**Core modality:** `xq:network`  
**Profile namespace:** `xq.net:`  
**Reference implementation lineage:** Crosscue Zeek Eventizer `0.5.0-prototype`

`xq.net:` is allocated by Crosscue Event Model Core package 0.1.1 for this profile. Profile conformance is an explicit claim and requires the rules in this document; use of `xq:network` alone does not imply profile conformance.

## 1. Scope

The Network Profile defines semantic Core Event mappings for network observations and analytically derived network facts above source-native telemetry such as:

```text
packet capture / live interface / infrastructure telemetry
                     ↓
         Zeek / Suricata / IPFIX / adapters
                     ↓
          source-native structured evidence
                     ↓
             network eventization
                     ↓
        Crosscue Event Model Core Events
                     ↓
      analytical projections / correlation / fusion
```

The profile defines **network semantics**, not packet formats, IDS schemas, a storage engine, or a required upstream product.

A conforming implementation MUST preserve the distinction between source-native evidence and the semantic event layer. Packet captures, Zeek logs, Suricata EVE records, flow records and similar native evidence remain source records; profile events are semantic representations above them.

The profile is intentionally compatible with multiple upstream adapters. Zeek is the current reference implementation source, but Zeek field names and connection-state codes are not profile vocabulary.

## 2. Design principles

### 2.1 Entity layers are distinct

The following concepts MUST NOT be silently collapsed:

```text
device ≠ interface ≠ address ≠ endpoint ≠ service
```

In particular:

- observing an IP address does not prove a physical device identity;
- observing a MAC address identifies a link-layer/interface referent by default, not necessarily a whole physical device;
- traffic referencing an address/port does not prove an application service exists there;
- observing a service does not imply that the corresponding IP address or interface is itself a device identity.

### 2.2 Identity evidence remains explicit

Address, hostname, DNS, TLS and other associations are **bindings**, not automatic identity resolution.

A producer MUST NOT use evidence observed later in the dataset to retroactively rewrite earlier address-scoped events as device-scoped events.

### 2.3 First observed is not established

The first occurrence of evidence in available telemetry means **first observed within that telemetry**, not that the represented relationship, service, address binding or presence began at that instant in the external world.

### 2.4 Events are temporally pure

A point event MUST contain only assertions supportable from evidence available at or before `event_time` under the producer's declared processing model. An interval event MAY contain assertions supportable by evidence available at or before `end_time`.

A derived `first_observed` event MUST use only evidence represented by its immediate parent events or source records and MUST NOT contain values that depend on observations outside that evidence interval, such as eventual session count, eventual byte totals, final directionality or final `last_observed` time.

Whole-window facts belong in analytical projections.

### 2.5 Observation viewpoint matters

Network visibility is observer-dependent. Profile events MUST identify the observation point. Presence semantics require an explicitly declared network scope.

### 2.6 Repetition may be semantically compressed

Repeated source-native records supporting the same semantic assertion MAY be coalesced when the normalization rule is documented and provenance/evidence counts remain recoverable.

The reference implementation uses this rule for repetitive ARP evidence.

## 3. Profile claim

An event claiming Network Profile 0.1 conformance MUST contain:

```json
"profile": "xq.net:profile-0.1"
```

and:

```json
"modality": "xq:network"
```

The Core modality identifies the domain family. The `xq.net:` namespace carries profile-specific semantic terms. A consumer MUST NOT infer Network Profile conformance from `modality` alone.

## 4. Network entity model

The profile recognizes these semantic entity categories:

```text
device
interface
address
endpoint
service
domain
hostname
software
network
```

Core entity references remain strings. The profile recommends the following human-readable prefixes but does not require consumers to parse the remainder of an identifier unless an implementation explicitly claims the reference conventions in Section 4.1.

### 4.1 Recommended entity-reference conventions

```text
device:<deployment-controlled-device-id>
interface:mac:<mac-address>
address:ip:<ip-address>
endpoint:<implementation-defined transport/network locator>
service:net:<application>:<implementation-defined endpoint locator>
domain:<normalized-dns-name>
name:host:<normalized-hostname>
software:<normalized-software-name>
network:<deployment-scoped-network-id>
```

For example:

```text
device:inventory:laptop17
interface:mac:00:17:f2:e2:c0:ce
address:ip:192.168.15.4
endpoint:ip:203.0.113.8:443/tcp
service:net:tls:ip:203.0.113.8:443/tcp
domain:example.com
name:host:laptop17
network:lab-lan
```

Identifier strings identify referents; they do not by themselves assert `same-as` equivalence.

### 4.2 Device

A `device` represents a device-scoped referent supported by evidence stronger than an address or interface identifier alone, for example an authenticated device identifier, infrastructure inventory record, management-plane identifier, or documented correlation/fusion result.

A producer MUST NOT materialize a device solely because a MAC address or IP address was observed.

### 4.3 Interface

An `interface` represents a link-layer or network-interface referent. A MAC address SHOULD identify an interface-scoped referent by default. A producer MAY associate an interface with a device when stronger identity evidence supports that relationship, but the MAC address itself MUST NOT be treated as proof that interface and device are equivalent.

### 4.4 Address

An `address` represents a network-layer address observed in evidence. An IP address MUST NOT automatically be promoted to an interface or device.

### 4.5 Endpoint

An `endpoint` represents an address plus transport/network addressing context referenced by traffic.

An endpoint MAY exist even when:

- no response was observed;
- a TCP attempt failed;
- the traffic is multicast or broadcast;
- no application protocol was identified.

The existence of an endpoint MUST NOT by itself be interpreted as proof of a service.

### 4.6 Service

A `service` represents an application-level service supported by application-level evidence such as protocol identification, protocol parsing or an infrastructure source explicitly reporting a service.

A producer MUST NOT materialize a service solely because traffic targeted a port commonly associated with that service.

### 4.7 Domain and hostname

A `domain` represents a DNS name in DNS/TLS/application semantics. A `hostname` represents a host label reported or associated through evidence such as DHCP or inventory telemetry.

Domain and hostname bindings MUST remain distinguishable from identity equivalence.

### 4.8 Network

A `network` is an explicitly declared observation/presence scope. Network membership MUST NOT be inferred merely from RFC1918/private addressing, public/private classification, or occurrence in a capture.

## 5. Required observation context

Every `observation`, `normalized_observation`, or `transition` event claiming this profile MUST include:

```text
context.observation_point
```

`context.observation_point` identifies the sensor, tap, collector, logical monitor or other viewpoint from which the evidence is available.

A `derived`, `fusion`, or `assessment` event MUST include either `context.observation_point` or `context.observation_points`. `context.observation_points`, when used, MUST be a non-empty array of unique observation-point identifiers representing the contributing viewpoints.

Events MAY include:

```text
context.network_context
context.capture_id
```

When `context.network_context` is supplied it SHOULD identify a `network` entity represented in the deployment's entity/projection layer.

Presence events have stricter requirements in Section 13.

## 6. Vocabulary overview

The normative profile vocabulary is defined in `xq-net-vocabulary.json`.

The principal profile features are:

```text
xq.net:address_binding
xq.net:hostname_binding
xq.net:connection
xq.net:communication_relationship
xq.net:dns_query
xq.net:name_resolution
xq.net:name_alias
xq.net:tls_session
xq.net:service
xq.net:software
```

Network presence reuses the Core feature:

```text
xq:presence
```

Network Profile 0.1 reuses the Core neutral-observation action:

```text
xq:observed
```

The profile-specific actions are:

```text
xq.net:first_observed
xq.net:assigned
xq.net:reported
xq.net:queried
xq.net:resolved_to
xq.net:alias_of
```

## 7. Mapping summary

| Semantic event | Class | Feature | Action | State | Polarity |
|---|---|---|---|---|---:|
| connection observation | `normalized_observation` | `xq.net:connection` | `xq:observed` | — | 0 |
| communication relationship first observed | `derived` | `xq.net:communication_relationship` | `xq.net:first_observed` | — | +1 |
| ARP address binding first observed | `derived` | `xq.net:address_binding` | `xq.net:first_observed` | — | +1 |
| DHCP address assignment | `normalized_observation` | `xq.net:address_binding` | `xq.net:assigned` | — | +1 |
| DHCP hostname report | `normalized_observation` | `xq.net:hostname_binding` | `xq.net:reported` | — | 0 |
| DNS query | `normalized_observation` | `xq.net:dns_query` | `xq.net:queried` | — | 0 |
| DNS address answer | `normalized_observation` | `xq.net:name_resolution` | `xq.net:resolved_to` | — | 0 |
| DNS alias answer | `normalized_observation` | `xq.net:name_alias` | `xq.net:alias_of` | — | 0 |
| TLS session observation | `normalized_observation` | `xq.net:tls_session` | `xq:observed` | — | 0 |
| service observation | `normalized_observation` | `xq.net:service` | `xq:observed` | — | 0 |
| software observation | `normalized_observation` | `xq.net:software` | `xq:observed` | — | 0 |
| scoped network presence first observed | `derived` | `xq:presence` | `xq.net:first_observed` | `xq:present` | +1 |

## 8. Connection observation

A normalized connection/flow observation MUST use:

```text
class    normalized_observation
feature  xq.net:connection
action   xq:observed
polarity 0
```

The normal relational shape is:

```text
subject = originator address/interface/device referent supported at event time
object  = endpoint referenced by the traffic
```

The reference adapter keeps ordinary IP traffic address-scoped even when later ARP or DHCP evidence associates that address with an interface or stronger device-scoped referent.

A connection event SHOULD retain, where available:

```text
context.protocol
context.originator_port
context.responder_port
context.originator_packets
context.responder_packets
context.originator_bytes
context.responder_bytes
context.duration_s
context.connection_state
context.application_stack
```

Source-native state values MUST remain in `context` unless this profile explicitly defines a semantic mapping.

## 9. Communication relationship

A communication relationship is a higher-order fact derived from qualifying connection observations.

The first observation MUST use:

```text
class    derived
feature  xq.net:communication_relationship
action   xq.net:first_observed
polarity +1
```

The event MUST identify the same semantic endpoints as the qualifying parent connection unless the derivation explicitly performs and documents entity fusion.

### 9.1 Relationship qualification

A bare connection attempt MUST NOT automatically become a communication relationship.

For connection-oriented transports, the adapter MUST document what evidence qualifies as observed communication. The reference Zeek adapter excludes states representing unanswered/rejected attempts from relationship derivation.

For datagram, multicast, broadcast and similar traffic, one-way traffic MAY support a relationship, but its evidence directionality MUST remain explicit.

### 9.2 Evidence directionality

The first-observed relationship event MUST include:

```text
context.evidence_directionality
```

with one of:

```text
unidirectional_observed
bidirectional_observed
```

The value MUST describe only evidence available from the parent observation(s) supporting that event at its event time.

### 9.3 Temporal purity

A `communication_relationship / first_observed` event MUST NOT contain aggregate values derived from later sessions.

In particular, it MUST NOT carry eventual values such as:

```text
last_observed
connections_observed
total_connections
total_bytes
aggregate_directionality
```

unless those values are independently supportable at the event time.

Whole-window relationship summaries belong in the relationship projection defined in Section 19.5.

## 10. Address bindings

Address bindings represent evidence associating a network interface or stronger device-scoped referent with a network address.

### 10.1 ARP

ARP-derived first-observed binding evidence MUST use:

```text
class    derived
subject  interface
object   address
feature  xq.net:address_binding
action   xq.net:first_observed
polarity +1
```

The underlying ARP record is source-native evidence. `first_observed` is derived because it requires comparison with earlier evidence in the declared observation scope. A producer MAY materialize separate normalized ARP observations, but Network Profile 0.1 does not require one Core Event per ARP record.

`first_observed` means first observation of evidence supporting the binding within available telemetry. It MUST NOT be interpreted as authoritative assignment or proof that the binding began at that instant.

Repeated equivalent ARP source observations MAY be coalesced into one semantic first-observed Core Event. When coalescing is used, an analytical projection SHOULD retain raw evidence count plus first/last observation times.

### 10.2 DHCP

A DHCP assignment/acknowledgement mapped as an address assignment MUST use:

```text
class    normalized_observation
subject  interface or device
object   address
feature  xq.net:address_binding
action   xq.net:assigned
polarity +1
```

The source-native DHCP message sequence, lease duration and server information SHOULD remain in context/provenance when available.

An address assignment event MUST NOT retroactively rewrite earlier address-scoped events as device-scoped events.

## 11. Hostname binding

A source-reported hostname associated with a network interface or stronger device-scoped referent SHOULD be represented as:

```text
class    normalized_observation
subject  interface or device
object   hostname
feature  xq.net:hostname_binding
action   xq.net:reported
polarity 0
```

`reported` is deliberately weaker than `identified_as` or `same_as`.

## 12. DNS

### 12.1 Query

```text
class    normalized_observation
subject  querying address/interface/device
object   domain
feature  xq.net:dns_query
action   xq.net:queried
polarity 0
```

The query type and query-side server/transport metadata SHOULD remain in `context` when available. Response codes, answer counts, rejection/error results and other facts learned only from the response MUST NOT be placed on a point-in-time query event unless `event_time`/`end_time` explicitly covers the response evidence. They belong on response/transaction evidence or a later derived event.

### 12.2 Address resolution

A DNS answer associating a domain with an IP address MUST be distinguishable from a domain alias:

```text
subject  domain
object   address
feature  xq.net:name_resolution
action   xq.net:resolved_to
polarity 0
```

This is a DNS resolution observation, not a permanent identity assertion.

### 12.3 Alias

A domain-to-domain alias/CNAME-style observation uses:

```text
subject  domain
object   domain
feature  xq.net:name_alias
action   xq.net:alias_of
polarity 0
```

A producer MUST NOT collapse domain aliases and domain-to-address resolutions into one undifferentiated identity relationship.

## 13. Scoped network presence

Network presence is relational and viewpoint-dependent.

A first-observed scoped presence event MUST use:

```text
class    derived
subject  interface, device or address
object   network
feature  xq:presence
action   xq.net:first_observed
state    xq:present
polarity +1
```

It MUST include:

```text
context.observation_point
context.network_context
```

and `context.network_context` MUST identify the same network scope as `object`.

A producer MUST NOT infer network presence solely because an address appears anywhere in telemetry.

A producer MUST NOT map the beginning or end of a capture to `xq:enter` or `xq:leave` without independent evidence of those transitions.

Where a uniquely supported interface/device/address binding exists at the relevant time, a presence projection MAY prefer the strongest supported referent to avoid double-counting. If identity remains ambiguous, the producer SHOULD preserve the weaker interface- or address-scoped presence rather than selecting an arbitrary device.

## 14. Endpoint and service semantics

Connection observations target endpoints, not service entities.

A service MAY be materialized only when application-level evidence supports it.

A normalized service observation uses:

```text
class    normalized_observation
subject  endpoint
object   service
feature  xq.net:service
action   xq:observed
polarity 0
```

The feature name `service` deliberately makes only the claim that application-level evidence for the service was observed at the endpoint. It does not assert uninterrupted current availability, health, reachability, or persistence outside the evidence interval.

A producer MUST NOT create pseudo-services for ICMP targets, multicast destinations, failed TCP attempts or unidentified ports merely from the numeric port/protocol tuple.

## 15. TLS

A TLS observation MUST target the transport endpoint regardless of whether SNI is present:

```text
class    normalized_observation
subject  client address/interface/device
object   endpoint
feature  xq.net:tls_session
action   xq:observed
polarity 0
```

Where available, TLS version, cipher, resumption state, establishment state, certificate references and SNI SHOULD remain in `context` or dedicated projections.

SNI/domain association MUST NOT change the TLS event object from endpoint to domain.

An implementation MAY materialize an endpoint-to-domain `tls_server_name_binding` projection from the TLS observation.

## 16. Software

A software observation uses:

```text
class    normalized_observation
subject  address/interface/device/endpoint as supported by source evidence
object   software
feature  xq.net:software
action   xq:observed
polarity 0
```

Reported version fields and source-native software type SHOULD remain in context.

Software identification MUST NOT imply device identity beyond the subject evidence available at the event time.

## 17. Application stacks

Sources MAY identify layered application/security protocols for one endpoint, for example:

```text
xmpp + tls
```

The profile uses:

```text
context.application_stack
```

as an ordered array of normalized component names.

A producer MUST canonicalize stack order deterministically before aggregation.

The reference normalization:

1. lowercases tokens;
2. maps historical/source labels such as `ssl` to semantic `tls`;
3. removes duplicate components while preserving semantic order;
4. places `tls` after non-TLS application components when the source expresses an application-over-TLS stack.

Thus:

```text
xmpp,ssl → ["xmpp", "tls"]
```

A combined source string MUST NOT be treated as one synthetic service entity solely because it arrived as one source field.

## 18. Provenance and reproducibility

Every `normalized_observation` or `derived` event claiming this profile MUST provide:

```text
provenance.producer
provenance.producer_version
provenance.method
```

A normalized observation MUST additionally provide at least one relevant:

```text
provenance.source_records[]
```

A derived event MUST provide:

```text
provenance.parents[]
```

identifying its immediate contributing Core Events unless the derivation has no Core-event parent and source-native provenance is the only available evidence.

`provenance.parameters.mapping` SHOULD identify the semantic mapping/eventization rule used by the adapter.

Parameters that materially alter relationship qualification, deduplication/coalescing, network scope or identity resolution MUST be retained in provenance or dataset-level metadata sufficient for reproducibility.

## 19. Analytical projections

A Network Profile implementation MAY materialize the following companion projections:

```text
observations
entities
bindings
sessions
relationships
services
presence_intervals
networks
```

These are not Core Events.

### 19.1 Observations

An observation projection may provide a tabular view of normalized Core observations and selected context fields.

### 19.2 Entities

`entities` SHOULD contain typed referents discovered or materialized during eventization, including device, interface, address, endpoint, service, domain, hostname, software and network entities.

Entity first/last observation times are projection facts over the projection interval. They MUST NOT be interpreted as external-world creation/destruction times.

### 19.3 Bindings

Recommended binding kinds are:

```text
arp_address_binding
dhcp_address_binding
dhcp_hostname_binding
dns_address_binding
dns_alias
tls_server_name_binding
endpoint_service_binding
```

Bindings MUST retain their distinct epistemic meaning. They MUST NOT be presented as generic `same-as` identity equivalence.

A binding projection SHOULD contain:

```text
first_observed
last_observed
observations
parent_event_count
parent_events
parent_events_truncated
```

`observations` counts underlying evidence observations. `parent_event_count` counts supporting semantic Core Events. These values MAY differ after semantic coalescing.

If `parent_events` is capped, the cap MUST be explicit through `parent_event_count` and `parent_events_truncated` or an equivalently unambiguous mechanism.

### 19.4 Sessions

A session projection SHOULD represent individual normalized connection observations with selected transport/application context.

A session is not the same concept as a persistent communication relationship.

### 19.5 Relationships

A relationship projection MAY aggregate qualifying sessions over an explicit dataset or time window.

It MAY contain whole-window values such as:

```text
first_observed
last_observed
connections_observed
total_bytes
total_packets
aggregate_directionality
application_stack
```

The projection MUST make the aggregation interval/dataset externally knowable.

Whole-window projection facts MUST NOT be back-projected into a first-observed Core Event at the beginning of the relationship.

### 19.6 Services

A service projection SHOULD represent observed endpoint-to-service relationships and their supporting application evidence.

An endpoint without service evidence MUST remain valid and MUST NOT require a service row.

### 19.7 Presence intervals

Presence intervals represent first/last observed evidence within an explicitly configured network scope.

They MUST NOT be labeled as physical/network `enter`/`leave` intervals unless independent transition evidence supports those semantics.

### 19.8 Networks

A networks projection SHOULD record explicitly configured network scopes, CIDRs/segments where applicable, observation points and other deployment context used to derive scoped presence.

## 20. Source adapter guidance

This section is informative except where an adapter claims the named mapping.

### 20.1 Zeek reference mapping

The current reference eventizer consumes structured Zeek logs including:

```text
arp.log
conn.log
dns.log
dhcp.log
ssl.log
known_services.log
software.log
```

Representative mappings:

```text
conn.log            → connection observations / session projection
dns.log             → DNS queries, resolutions and aliases
dhcp.log            → address assignment and hostname binding
arp.log             → first-observed MAC↔IP binding evidence
ssl.log             → TLS observations and server-name bindings
known_services.log  → service observations
software.log        → software observations
```

Zeek-specific `conn_state` values remain source-native context. A Zeek adapter MAY use them in a documented relationship-qualification algorithm, but those codes are not Network Profile vocabulary.

### 20.2 Suricata mapping

A Suricata adapter may map EVE record families such as flow, DNS, TLS, HTTP, ARP and related protocol metadata into the same Network Profile semantics.

Suricata alert/detection events MUST remain detector observations unless a separate analytical process produces a derived/assessment event. An IDS alert MUST NOT automatically become a claim that a host is compromised.

### 20.3 Other adapters

IPFIX/NetFlow, switch/controller telemetry, wireless telemetry, cloud flow logs, firewall logs and infrastructure inventories MAY implement this profile when they can satisfy the semantic and provenance requirements.

## 21. Event ordering

Profile events SHOULD be serialized in ascending `event_time` when emitted as an ordered stream.

For equal event times, a producer SHOULD emit immediate parent Core Events before derived children where practical.

Producers SHOULD compare actual temporal values rather than variable-precision RFC3339 strings when sorting. Fixed fractional precision is RECOMMENDED for deterministic output.

Ordering does not replace provenance; consumers MUST use event semantics/provenance rather than assuming arrival order is causal order.

## 22. Conformance requirements

A Network Profile 0.1 producer MUST:

1. satisfy Crosscue Core 0.1 structural and semantic conformance;
2. use `profile = "xq.net:profile-0.1"` and `modality = "xq:network"`;
3. provide observation viewpoint context as required by Section 5;
4. preserve the device/interface/address/endpoint/service distinctions;
5. keep binding evidence explicit rather than silently resolving identity;
6. use endpoint objects for connection and TLS observations;
7. require application-level evidence before materializing service entities;
8. distinguish DNS address resolutions from DNS aliases;
9. use `first_observed`, not `established`, when only capture-scoped first evidence is known;
10. preserve temporal purity of first-observed derived events;
11. declare relationship evidence directionality;
12. derive network presence only under an explicit network scope;
13. retain immediate provenance to source records or parent Core Events as required in Section 18;
14. canonicalize application stacks deterministically when supplied;
15. ensure capped projection provenance is explicitly marked as incomplete.

## 23. Recommended conformance fixtures

Positive fixtures SHOULD include:

```text
connection_observed
tcp_relationship_first_observed
udp_unidirectional_relationship_first_observed
arp_address_binding_first_observed
dhcp_address_assigned
dhcp_hostname_reported
dns_query
dns_address_resolution
dns_alias
tls_session_endpoint_target
service_observed
software_observed
scoped_presence_first_observed
```

Negative fixtures SHOULD include at least:

```text
connection_targets_service_instead_of_endpoint
service_created_from_failed_port_attempt
presence_without_explicit_network_scope
presence_first_observed_labeled_enter
relationship_first_observed_labeled_established
relationship_event_contains_later_last_seen
relationship_event_contains_later_aggregate_count
dns_alias_collapsed_into_address_resolution
mac_or_ip_silently_promoted_to_device
application_stack_nondeterministic
projection_parent_list_truncated_without_marker
```

## 24. Privacy, security and dual use

Network telemetry can reveal device identity, service use, organisational structure, behaviour and relationships. Eventization can make correlation across datasets easier and can therefore increase sensitivity.

Implementers SHOULD apply appropriate legal authority, minimisation, access control, retention, audit, redaction and handling policies.

MAC addresses, IP addresses, hostnames, domain use and derived relationships can be identifying or sensitive. Pseudonymous entity references do not guarantee anonymity.

Public conformance fixtures SHOULD be synthetic.

## 25. Out of scope for Network Profile 0.1

The following are intentionally not standardized here:

- packet decoding or reassembly;
- IDS/IPS signature languages;
- threat taxonomy or compromise assessment;
- authoritative device identity resolution;
- NAT attribution;
- user/account identity;
- Wi-Fi-specific association semantics;
- routing/BGP topology semantics;
- network-path inference;
- certificate identity/trust assessment;
- flow-storage schema;
- graph query language;
- behavioural anomaly scoring;
- universal service taxonomy;
- authoritative enter/leave transitions inferred solely from capture boundaries.

These may be addressed by later profile revisions, specialized profiles, extensions or analytical layers.

## 26. Versioning

This published profile defines:

```text
xq.net:profile-0.1
```

and depends on:

```text
xq_version = "0.1"
```

The Network Profile version evolves independently of Core. Incompatible Network Profile semantics require a new profile version rather than silently changing the meaning of `profile-0.1` events.

## 27. Reference implementation findings

The profile design was stress-tested through the reference Zeek eventizer on a larger packet capture containing approximately 94k packets. The implementation work motivated the following distinctions now made normative or explicit in this profile:

```text
packet ≠ semantic event
MAC/interface evidence ≠ device
IP address ≠ device
interface ≠ address
address ≠ endpoint
endpoint ≠ service
connection attempt ≠ observed communication
session ≠ persistent relationship
first observation ≠ establishment
event-time knowledge ≠ whole-window projection knowledge
identity evidence ≠ resolved identity
```

High-frequency ARP evidence also demonstrated the value of semantic coalescing: thousands of packet-level address assertions can support a small number of first-observed binding events while retaining full evidence counts in projections.

These observations are implementation evidence for the profile; they do not make any particular sample dataset part of the normative specification.
