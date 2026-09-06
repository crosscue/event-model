# Crosscue Event Model namespace rules

**Status:** Normative for Core 0.1

The human-facing specification name is **Crosscue Event Model**. Semantic identifiers use compact qualified namespaces so the wire representation is not coupled to future branding.

## 1. Qualified semantic identifier syntax

Core semantic fields use identifiers shaped as:

```text
<namespace>:<term>
```

The JSON Schema currently accepts lowercase ASCII identifiers matching:

```regex
^[a-z][a-z0-9.-]*:[a-z][a-z0-9._-]*$
```

Examples:

```text
xq:presence
xq:enter
xq.mob:dwell
org.example:signal
```

## 2. `xq:` Core namespace

`xq:` identifies terms registered by the Crosscue Event Model Core vocabulary.

An implementation claiming **Crosscue Core Vocabulary conformance**:

- MUST NOT assign a private or conflicting meaning to a registered `xq:` identifier;
- MUST obey semantic bindings associated with registered Core compositions;
- MUST NOT claim an unregistered `xq:` term is a Core term.

This specification does not claim ownership of the characters `xq` in every external context. The rule describes vocabulary conformance within the Crosscue Event Model ecosystem.

## 3. Official profile namespaces

A profile-specific namespace has the form:

```text
xq.<profile>:
```

A namespace is official only when it appears in `vocabulary/xq-namespaces.json` and a corresponding profile has been published.

Core package 0.1.1 allocates:

```text
xq.mob:
xq.net:
```

for Mobility Profile 0.1 and Network Profile 0.1 respectively.

Names such as `xq.rf:`, `xq.ais:` or `xq.adsb:` are **not allocated by Core 0.1.1**. They may be allocated later if/when those profiles are published.

This does not prevent Core from registering coarse modality values such as `xq:rf`, `xq:ais` or `xq:ads-b`. A Core modality identifier names a source/domain family; it does not allocate or imply a profile namespace.


## 3.1 Coarse modality registration

A published profile MAY be accompanied by an additive Core registration of a coarse modality identifier such as `xq:network`. Such a registration names a domain family; it does not move profile-specific features, actions, states or entity semantics into Core.

Within the 0.1.x line, adding a new coarse modality alongside a newly published profile is considered compatible provided that no existing Core term or composition changes meaning.

## 4. Third-party namespaces

Third parties SHOULD use a namespace they control or can reasonably keep collision-free.

Examples:

```text
org.example:signal
org.example:observed
uk.example.sensor:mode
```

A third-party term remains structurally valid even when a Core consumer does not understand it.

Third parties wishing to claim Core vocabulary conformance SHOULD NOT mint terms under `xq:` or allocated `xq.<profile>:` namespaces.

## 5. Promotion from profile to Core

A profile term may be proposed for promotion into `xq:` after it demonstrates genuinely cross-domain semantics.

A proposal SHOULD normally include examples and fixtures from at least two materially different modalities.

Promotion changes the identifier; implementations SHOULD NOT assume automatic equivalence between an older profile term and a later Core term unless the relevant specification explicitly maps them.

## 6. Field names are not namespaced

Core JSON field names remain ordinary names:

```text
feature
action
state
modality
```

Semantic values are qualified:

```json
{
  "feature": "xq:presence",
  "action": "xq:enter",
  "state": "xq:present"
}
```

This separation keeps the object readable while making semantic ownership explicit.
