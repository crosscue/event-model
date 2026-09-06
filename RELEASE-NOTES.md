# Crosscue Event Model Core 0.1.1 — Release notes

**Release date:** 2026-09-06  
**Wire version:** `xq_version = "0.1"`  
**Status:** Experimental specification; compatible 0.1.x release

## Scope

This release keeps the frozen Core 0.1 wire model and publishes **Network Profile 0.1** alongside Mobility Profile 0.1. No Core field or existing registered Core term changes meaning.

The only additive Core vocabulary registration is the coarse modality `xq:network`. Network-specific features/actions remain in the newly allocated `xq.net:` profile namespace.

## Network Profile 0.1

The profile covers semantic events derived from network telemetry such as Zeek, Suricata, IPFIX/NetFlow, cloud flow logs and comparable structured sources. It deliberately keeps source-native records as evidence beneath the semantic event layer.

Key rules include:

- `device ≠ interface ≠ address ≠ endpoint ≠ service`;
- MAC addresses identify interface-scoped referents by default, not whole devices;
- connections target endpoints; services require application-level evidence;
- `xq:observed` is reused for neutral observations;
- `xq.net:first_observed` means first evidence in the declared observation scope, not external-world establishment;
- ARP first-observed bindings are `derived`;
- DNS aliases and address resolutions remain distinct;
- point events cannot contain response/future facts not yet supported at `event_time`;
- derived events may cite one or multiple observation points;
- network presence requires an explicit network scope.

## Compatibility

`xq_version` remains `0.1`. Existing Core fields, Core term meanings and Core composition bindings are unchanged.

Within 0.1.x, a patch release may register a new coarse modality when publishing an official profile for a previously unregistered domain, provided existing Core semantics remain unchanged. New Core features/actions/states still require the normal conservative promotion process and should target a future Core version where semantics are not already frozen.

## Included namespaces

```text
xq:       Core vocabulary
xq.mob:   Mobility Profile 0.1
xq.net:   Network Profile 0.1
```

## Reference validation

Run:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate.py --fixtures
```

The suite now covers Core, Mobility and Network profile semantics with positive and negative fixtures.

## Licence

All repository materials are licensed under the Apache License, Version 2.0. See `LICENSE`.
