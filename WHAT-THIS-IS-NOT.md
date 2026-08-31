# What the Crosscue Event Model is not

The Crosscue Event Model is deliberately narrow.

It is **not**:

- a claim to be an industry standard;
- a replacement for source-native sensor or domain schemas;
- a universal intelligence ontology;
- a complete entity-resolution model;
- a security/classification/marking policy system;
- a storage engine, message bus or transport protocol;
- an event-sourcing architecture requirement;
- a requirement to discard raw evidence after projection;
- a guarantee that two producers will derive identical events without identical profile rules and parameters;
- a mechanism for establishing legal authority to collect, process, correlate or retain data;
- a guarantee that pseudonymous events are anonymous;
- a complete geometry, uncertainty, quality or confidence ontology.

Its intended role is smaller:

> provide a common semantic representation for temporally anchored events so heterogeneous producers and analytical processes can exchange and reason over a shared intermediate representation while preserving source-specific evidence and provenance.

Domain-specific detail belongs in profiles, qualified extension vocabularies and `context` rather than continual expansion of Core.
