# Contributing

The principal design goal is to keep Core small enough to remain genuinely cross-domain.

## Core vocabulary changes

A proposal for a new `xq:` Core term SHOULD include:

1. a precise definition;
2. at least two concrete examples;
3. at least two materially different modalities in which the same semantics apply;
4. expected polarity or allowed polarities where meaningful;
5. typical units where meaningful;
6. a "do not confuse with" note when adjacent terms exist;
7. at least one positive fixture;
8. a negative or boundary fixture when the semantics can be confused;
9. an explanation of why a profile-specific or third-party term is insufficient.

Core 0.1 terms remain experimental in maturity but are compatibility-frozen for the 0.1.x release line. Later profile work may motivate deprecation, replacement, or relocation in a future Core version, but existing 0.1 term meanings MUST NOT be silently changed within 0.1.x.

## Profile terms

Domain-specific terms belong in an allocated profile namespace such as `xq.mob:`. Profile terms may later be proposed for promotion to Core after cross-domain evidence exists.

## Core schema changes

Core schema changes MUST explain:

- compatibility impact;
- effect on existing fixtures;
- whether the wire-level `xq_version` changes;
- why the requirement cannot be handled by a profile, vocabulary binding, provenance or `context`.

## Sensitive data

Contributions MUST use synthetic or intentionally public examples. See `SECURITY.md`.

## Licence

Unless explicitly stated otherwise, contributions intentionally submitted for inclusion are licensed under the Apache License, Version 2.0, consistent with Section 5 of that licence.


## Profile-driven coarse modalities

A new official domain profile may propose an additive coarse Core modality (for example `xq:network`) in the same release that allocates its profile namespace. This exception does not waive the cross-domain evidence requirement for new Core features, actions or states.
