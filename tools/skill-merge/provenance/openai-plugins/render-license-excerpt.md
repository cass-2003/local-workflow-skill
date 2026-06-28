```bash
render login
```

3. Verify access:

```bash
render whoami -o json
```

If `render whoami -o json` fails, fix authentication before you rely on Render workflows in Codex.

## For maintainers

Run the sync script to refresh `skills/` from [render-oss/skills](https://github.com/render-oss/skills):

```bash
./scripts/sync-skills.sh
```

GitHub Actions also runs `.github/workflows/sync-skills.yml` each day and opens a pull request when upstream skills change.

## License

MIT. See [LICENSE](LICENSE).
