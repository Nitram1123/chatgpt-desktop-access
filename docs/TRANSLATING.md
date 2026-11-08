# Translating ChatGPT Desktop Access

The add-on uses NVDA's gettext translation mechanism for its interface and
announcements. The template is `locale/chatGPTDesktopAccess.pot`. ChatGPT's
native control names and status text are recognized separately from these
translations.

## Update the template

Run:

```powershell
python .\tools\extract_messages.py
```

The generated template is deterministic. CI runs the same script with
`--check` and fails when the committed template is stale.

## Add a language

1. Copy the template to
   `locale/<language>/LC_MESSAGES/nvda.po` and translate each `msgstr`.
2. Compile that file to
   `locale/<language>/LC_MESSAGES/nvda.mo` using GNU `msgfmt` or another
   standards-compliant gettext compiler.
3. Do not change placeholder names such as `{message}`, `{activity}`,
   `{seconds}`, or `{duration}`.
4. Run the complete build and test checklist before submitting the translation.

The package builder automatically includes compiled `nvda.mo` catalogs. Source
`.po` files and the `.pot` template remain in the repository for translators but
are not included in the installed add-on.

To translate the add-on's description and release summary shown by NVDA, add
`locale/<language>/manifest.ini` with the translated `description` and
`changelog` fields. The package builder includes localized manifests.
