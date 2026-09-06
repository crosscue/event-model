# Conformance fixtures

`valid/` contains documents expected to pass structural and semantic validation.

`invalid/` contains documents deliberately constructed to fail at least one structural, Core-semantic, collection-semantic, Mobility Profile rule, or Network Profile rule.

`manifest.json` is the reference fixture list used by:

```bash
python tools/validate.py --fixtures
```

Fixtures are synthetic and licensed under Apache-2.0 with the rest of the repository.
