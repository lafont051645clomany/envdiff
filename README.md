# envdiff

Compare `.env` files across environments and flag missing or mismatched keys with optional secret masking.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git && cd envdiff && pip install .
```

---

## Usage

```bash
# Compare two .env files
envdiff .env.development .env.production

# Compare multiple environment files
envdiff .env.development .env.staging .env.production

# Mask secret values in output
envdiff .env.development .env.production --mask-secrets
```

**Example output:**

```
[MISSING]   STRIPE_SECRET_KEY     found in .env.development, missing in .env.production
[MISMATCH]  DATABASE_URL          values differ across environments
[OK]        APP_NAME              consistent across all files
```

### Options

| Flag              | Description                              |
|-------------------|------------------------------------------|
| `--mask-secrets`  | Redact values containing sensitive keys  |
| `--strict`        | Exit with non-zero code if diff found    |
| `--format json`   | Output results as JSON                   |

---

## Why envdiff?

Misconfigured environment variables are a common source of bugs and outages. `envdiff` makes it easy to audit `.env` files before deployments, catch missing keys early, and keep secrets out of your terminal logs.

---

## License

MIT © [yourname](https://github.com/yourname)