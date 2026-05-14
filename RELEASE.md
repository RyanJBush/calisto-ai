# Release Instructions

1. Ensure main branch is green in CI.
2. Update `CHANGELOG.md` with release notes.
3. Create and push an annotated tag:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

4. Create a GitHub Release from tag `v1.0.0` and paste changelog highlights.
