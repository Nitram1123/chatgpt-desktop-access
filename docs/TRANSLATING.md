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

## Add or update a language

`tools/translation_catalogs.py` keeps every catalog in step with the template:

```powershell
python .\tools\translation_catalogs.py export es ..\translations\es-strings.txt
python .\tools\translation_catalogs.py import es ..\translations\es-translated.txt
python .\tools\translation_catalogs.py check
```

1. `export` writes the strings a language still lacks, one per line, as
   `number<TAB>"JSON string"`. For a new language it also lists the
   `manifest:description` and `manifest:changelog` fields.
2. Translate the JSON strings and keep each line's number. Leave out lines
   that should stay in English; NVDA then shows the English text. The two
   support-report strings stay in English in every language so reports can be
   read when shared.
3. `import` checks every line before writing anything: placeholders such as
   `{message}` and `{duration}` must be unchanged, each `&` shortcut key must be
   kept, and line breaks and leading or trailing spaces must match the English.
   It then writes `locale/<language>/LC_MESSAGES/nvda.po`, compiles `nvda.mo`,
   and writes `locale/<language>/manifest.ini`.
4. `check` validates every catalog and confirms each compiled `nvda.mo`
   matches its `.po` file. `compile` rebuilds every `nvda.mo` after hand edits.
5. Run the complete build and test checklist before submitting the translation.

Machine-translated catalogs carry an `X-Translation-Note` header. Native
speakers are welcome to correct them, either by editing the `.po` file and
running `compile`, or with any standards-compliant gettext editor.

The package builder automatically includes compiled `nvda.mo` catalogs. Source
`.po` files and the `.pot` template remain in the repository for translators but
are not included in the installed add-on.

To translate the add-on's description and release summary shown by NVDA, add
`locale/<language>/manifest.ini` with the translated `description` and
`changelog` fields. The package builder includes localized manifests.
