# Security, privacy and sensitive-data reporting

The Crosscue Event Model can represent sensitive temporal, spatial, identity and sensor-derived information. Combining otherwise ordinary events can materially increase sensitivity through correlation.

## Public issue hygiene

Do not include the following in public issues, pull requests or fixtures:

- customer or partner data;
- live or historical operational intelligence;
- personal mobility traces;
- sensitive network telemetry such as internal IP/MAC mappings, hostnames, service inventories, packet/flow evidence or derived communication relationships;
- authentication material or secrets;
- protected source identifiers;
- sensitive collection parameters;
- data subject to contractual, statutory or classification controls.

Use synthetic or intentionally public data when reproducing specification issues.

## Reporting security issues

Use the repository host's private security-reporting mechanism when available. If that mechanism is unavailable, contact the repository owner through the private contact channel published with the canonical repository. Do not disclose exploitable security issues in a public issue before the maintainer has had an opportunity to assess them.

## Markings

The Core `markings` array merely transports opaque handling labels. Consumers MUST NOT assume it enforces access control. Deployments requiring mandatory controls must implement those controls outside the Crosscue Event Model.
