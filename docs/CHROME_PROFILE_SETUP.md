# Chrome profile setup (Alexandr Vinnitchii)

1. Open Chrome → `chrome://version`
2. Find **Profile path**, e.g. `...\User Data\Profile 2`
3. The folder name (`Profile 2`) is your `--profile-directory` value
4. Edit `config/apps.json`:

```json
"alexandr_vinnitchii": ["--profile-directory=Profile 2"]
```

Replace `Profile 2` with your actual profile folder name.

Profile voice aliases are in `profile_aliases` — add variants you say often.
