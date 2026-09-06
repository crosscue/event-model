# Changelog

## 0.1.1 — 2026-09-06

Compatible profile-enabling release. Wire version remains `xq_version = "0.1"`.

Changes:

- publishes Network Profile 0.1 and allocates `xq.net:`;
- registers the additive coarse Core modality `xq:network`;
- reuses Core `xq:observed` rather than minting a network-local equivalent;
- distinguishes `device`, `interface`, `address`, `endpoint`, and `service`; MAC identifiers are interface-scoped by default;
- makes ARP `first_observed` binding events derived facts rather than normalized observations;
- clarifies point/interval temporal-purity semantics and prevents DNS response facts from being placed on a point query event;
- renames the profile feature `xq.net:service_availability` to the weaker `xq.net:service`;
- permits derived/fusion network events to cite one or multiple observation points;
- adds Network Profile positive/negative conformance fixtures;
- refactors reference validation so profile vocabularies are loaded generically and profile-specific semantic validators are dispatched independently;
- restores all schemas, examples, fixtures, tooling and CI assets referenced by the release README into the packaged release tree.

## 0.1.0 — 2026-08-31

Initial public release, frozen from `0.1.0-draft.4`.

No wire-semantic changes were made between draft.4 and 0.1.0. The release:

- sets package/registry/conformance version to `0.1.0`;
- retains wire version `xq_version = "0.1"`;
- freezes Core schema, existing registered `xq:` term meanings, and Core composition bindings for the 0.1.x line;
- retains Apache License 2.0 across the repository;
- publishes Core, Mobility Profile 0.1, schemas, registries, synthetic examples, conformance fixtures and reference validation tooling.

## 0.1.0-draft.4

Cross-domain semantic-example and terminology revision.

Changes:

- renamed the Core semantic field `element` to `action`;
- renamed vocabulary term kind `element` to `action` and updated schemas, profiles, fixtures, examples and validator accordingly;
- registered coarse Core modality identifiers `xq:ais`, `xq:ads-b`, `xq:rf`, and `xq:imagery` without allocating corresponding profile namespaces;
- added cross-domain Core features `xq:position`, `xq:altitude`, and `xq:signal`;
- added Core action `xq:observed` and semantic bindings for observed position, altitude, signal and presence;
- added non-normative semantic examples for mobility/AdTech, AIS, ADS-B, RF and imagery;
- added a normative rule that source-reported status MUST NOT automatically become Core `state`;
- documented AIS reported navigational status as evidence that may remain in `context` while eventizer state is independently derived;
- added the five cross-domain semantic examples to the valid conformance suite;
- extended the reference validator to verify registered Crosscue term kinds for Core and Mobility identifiers.

Wire version remains `0.1` because this is still an experimental pre-release draft.

## 0.1.0-draft.3

Publication hardening after adversarial review.

Changes:

- changed public project name from **XQ Event Model (XQEM)** to **Crosscue Event Model**;
- retained `xq:` as the technical semantic namespace;
- renamed wire field `xqem_version` to `xq_version`;
- renamed schemas/examples/publication artifacts around Crosscue Event Model;
- applied Apache License 2.0 across specification, schemas, vocabularies, profiles, examples, conformance material and tooling;
- added `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `WHAT-THIS-IS-NOT.md`;
- strengthened privacy, dual-use and sensitive-data language in the README;
- reduced event `class` to the epistemic axis: observation, normalized_observation, transition, derived, fusion, assessment;
- removed `relational` class; `subject` + `object` now express relational structure orthogonally;
- removed `manual` class; production method now belongs in provenance;
- removed `xq:fusion` and `xq:assessment` modalities; added experimental `xq:multimodal`;
- reduced the Core vocabulary to terms exercised by the current Core/Mobility work plus the cross-domain multimodal modality;
- converted Core vocabulary from string lists to definition-bearing term records;
- added examples, allowed polarities, typical units and ambiguity guidance where applicable;
- moved STAY and DWELL from Core (`xq:stay`, `xq:dwell`) to Mobility (`xq.mob:stay`, `xq.mob:dwell`);
- formalized semantic composition bindings including required polarity/state;
- limited allocated namespaces to `xq:` and `xq.mob:`;
- softened namespace wording to vocabulary-conformance/allocation rules;
- made provenance extensible to unknown fields;
- made effective eventizer parameters mandatory for reference Mobility Profile conformance;
- added normative STAY/DWELL threshold semantics;
- added positive and negative conformance fixtures;
- added executable structural + semantic validator;
- added semantic checks for end-time ordering, profile bindings, non-finite numbers and collection ID uniqueness.

Wire version remains `0.1` because the project is still pre-release and draft.3 was the intended replacement for earlier draft wire experiments.

## 0.1.0-draft.2

Earlier public-draft candidate using the XQ Event Model (XQEM) public name and `xq:` namespace.

## 0.1.0-draft.1

Initial publication-oriented draft derived from the exploratory generic event work.
