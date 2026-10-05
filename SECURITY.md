# Security policy

Report a vulnerability privately through [GitHub Security Advisories](https://github.com/gHashTag/ghashtag.github.io/security/advisories), not a public issue.

## Secrets never enter the repository

No password, API key, token or credentials file is committed, not even in docs or examples. Read secrets from the environment or from a gitignored file.

The gate has three layers, all driven by [`.gitleaks.toml`](.gitleaks.toml):

1. **pre-commit** (lefthook) scans staged changes with gitleaks.
2. **pre-push** (lefthook) scans every commit that is not yet on a remote.
3. **CI** ([`secret-scan`](.github/workflows/secret-scan.yml)) scans the PR range, so `--no-verify` does not get a secret past it.

Set up once per clone: `brew install gitleaks lefthook && lefthook install`.

A secret that was ever pushed is compromised. Removing it from the tree does not unpublish it, so rotate it at the provider.
