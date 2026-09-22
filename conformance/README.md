# Conformance fixtures

`valid/` contains documents expected to pass structural and semantic validation.

`invalid/` contains documents deliberately constructed to fail at least one structural, Core-semantic, collection-semantic, Mobility Profile, Network Profile, or experimental Space draft rule.

`manifest.json` is the reference fixture list used by:

```bash
python tools/validate.py --fixtures
```

Fixtures are synthetic and licensed under Apache-2.0 with the rest of the repository.

Space draft fixtures exercise the bindings in
[`profiles/crosscue-space-0.1.md`](../profiles/crosscue-space-0.1.md).
Validator support does not officially allocate `xq.space:` or establish scientific
validity. The two worked Space examples are also included in the manifest so CI
checks them without a sibling checkout or live data.
