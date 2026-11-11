# ChatGPT Desktop Access for NVDA

ChatGPT Desktop Access supports both ChatGPT mode and Codex mode in the Windows app.
It automatically reattaches after switching modes or returning from the usage page;
no NVDA restart is required.

[![Validate NVDA add-on](https://github.com/jcoffin1/chatgpt-desktop-access/actions/workflows/ci.yml/badge.svg)](https://github.com/jcoffin1/chatgpt-desktop-access/actions/workflows/ci.yml)

ChatGPT Desktop Access for NVDA provides live activity announcements,
Braille, progress sounds, chat navigation and actions, and accessible dialog
focus in both browse mode and focus mode. It was formerly named Codex Access
Toolkit and Codex Status Announcer; the internal add-on identifier remains
unchanged so existing settings and Input Gestures assignments continue working.

## Download

Development-build compatibility note: Chromium UIA transcript scans now use
native bulk endpoint movement rather than web-navigation character walking.
History, recent-message review, and startup responsiveness still require live
verification with the updated app before this build is approved for release.

Download tested packages from the
[GitHub Releases page](https://github.com/jcoffin1/chatgpt-desktop-access/releases).
The project is being prepared for the official NVDA Add-on Store, but it is not
listed there yet.

## Settings

Open **NVDA Settings > ChatGPT Desktop Access**. The panel is divided into eight
keyboard-accessible pages: **General**, **Speech and Braille**, **Sounds**,
**Activity Output**, **Wording and Preview**, **Browser Access**, **Advanced**,
and **Support**.

Press Control+Tab or Shift+Control+Tab to move between pages. Every actionable
control has a distinct Alt access key within its page. General contains the main
output choices, and Activity Output contains background timing and category
routing.

Advanced contains technical compatibility controls. Support contains account,
documentation, troubleshooting, and settings-file actions.

Settings include:

- A General-page switch for the native conversation message list, on by default.
- Minimal or Full progress labels (Full is the default).
- Essential, Balanced, or Informative Minimal-speech profiles. Balanced is the
  default; Essential limits speech to critical states, while Informative adds
  safe filenames, counts, and useful timing without exposing full commands.
- Standard, Developer, or Raw Full-speech profiles. Standard announces an
  action with concise targets, counts, and useful timing; Developer preserves
  complete normalized commands and progress; Raw preserves the exact exposed
  wording. Full braille remains complete independently of the speech profile.
- Speech and braille independently.
- Concise, Informative, or Full Braille detail independently of speech verbosity.
- Optional conversation reading protection keeps routine add-on progress and ordinary
  streamed-response live updates from interrupting speech, replacing the current Braille
  line, or relocating browse-mode reading in ChatGPT. Focus-mode response output,
  important results, permission dialogs, and urgent alerts continue normally.
- When returning to a task that is still active, a stale Chromium activity-card
  focus is corrected to the newest response heading in browse mode if newer
  output follows it. This moves only NVDA's virtual reading position, never
  Windows keyboard focus, and any user keystroke cancels the correction.
- Optional interruption of current NVDA speech for urgent permissions and failures.
- Optional redaction of likely secrets and personal data.
- The interval for elapsed working-time updates.
- A recurring “Still working in background” pulse in Minimal and Full modes,
  with gentle alternating two-note earcons.
- Individual progress categories. Every category item states whether it is enabled
  and its current output route, such as “Commands: enabled; speech only.”
- Plain-language Codex commentary updates in both Minimal and Full modes.
- Completion sounds and sanitized diagnostic logging.
- Immediate, optional Prompt submitted sounds with a configurable delay before
  continuous Working sounds begin.
- Prompt submission detection for Enter and the Send button, prompt cancellation
  detection, duplicate-event suppression, and isolated state across Codex tasks.
- Immediate submission detection observes unmodified keyboard Enter and a Braille
  display's standalone dot-8 Enter before ChatGPT replaces its content-editable
  prompt. The observer never claims or re-sends the gesture; Shift+Enter and all
  other input retain their native behavior.
- Prompt-typing protection suspends full Chromium compatibility scans while text is
  being entered. Prompt-local state checks are debounced until typing pauses, leaving
  NVDA's main thread available for Braille translation, editor feedback, and ordinary
  key processing.
- A cancellable completion-settling window prevents commentary from being
  mistaken for the end of a task when delayed tool work follows.
- A choice of original soft click earcons or musical tones for every
  announcement, including while speech is enabled. Clicks are the default.
- Seventeen distinct percussive click signatures. Commands, code edits, searches,
  tests, tools, commentary, attention, completion, failure, submission, background
  work, and focus changes use different rhythms, pitch direction, and textures.
- Idle polling frequency.
- Soft, Normal, or Loud click levels, with an action selector and separate
  sound-only and speech-only preview buttons.
- Editable announcement wording for every action, with a restore button and
  `{message}`, `{activity}`, `{seconds}`, and `{duration}` placeholders for live details.
- Per-category routing to all enabled channels, speech, sound, braille, or off.
- Configuration repair, compatibility self-test, sanitized support diagnostics,
  a user-chosen-file sanitized support report, settings import/export, and focused
  speech-profile reset.
- The sanitized support report includes last and maximum conversation-scan and
  background mode-probe times, plus counts of slow operations. Slow timings are logged
  at most once per minute per operation; no message text is recorded in these
  measurements. Use the repeatable checklist in `tests/performance-scenarios.md`
  when checking large chats, Braille typing, mode changes, or NVDA restart.
- Command punctuation and maximum spoken-length controls. Long complete commands
  remain available to braille and an assignable clipboard action.
- Search result counts and refresh for the Recent and Archived task lists.
- A maximum background-activity timeout.
- High-priority permission and user-input alerts.
- High-priority usage-limit alerts that stop Working feedback, omit raw dashboard
  URLs, and report any exposed reset time, upgrade option, and credit-purchase option.
- Configurable application process names for future Codex hosts.
- An optional continuous Working sound while Codex is busy. Its interval is
  configurable, begins after a configurable start delay, and is postponed by
  other progress sounds to prevent overlap. It follows the selected Clicks or
  Musical tones style. A separate optional submission cue
  plays immediately when a populated prompt is submitted with Enter or Send.
- Optional rising and falling clicks when ChatGPT/Codex gains or loses focus.
  When Alt+F4 closes ChatGPT without a final Windows focus event, the inactive
  cue still plays and NVDA speech and Braille return to the previously focused
  application without requiring another Alt+Tab, including when ChatGPT closes
  during startup before conversation monitoring finishes attaching. If that
  application has also closed, the add-on moves to the highest remaining usable
  application window instead of leaving NVDA on a defunct ChatGPT object.
- Native embedded-browser access that leaves Chromium roles, states, actions,
  focus, Enter, Space, Tab, Shift+Tab, NVDA+Space, quick navigation, and element
  lists unchanged. There is no separate browser command layer to learn.
- Optional **Loading page** and **Loading complete** speech and Braille messages.
  Native document busy states and progress events are used when available, with a
  bounded fallback for pages that expose no final event. Feedback never scans the
  page or moves focus.
- One **Open usage and credits** button for the official ChatGPT account
  dashboard, where the user can review usage and available purchase options.
  The add-on never makes a purchase automatically.

The **Test current announcement outputs** button verifies the selected speech
and braille channels, including progress sounds.

The **Test command progress sound** button plays the selected command sound
directly, regardless of the current speech settings.

Choose an action under **Preview action**, then use **Preview selected sound**
or **Preview selected speech** to hear only that one output. Previews never run
the full sound collection automatically.

To customize an announcement, select its action, enter the desired wording in
**Announcement text**, and save Settings. Leave the field blank—or choose
**Restore built-in announcement**—to use the add-on's standard wording. For
example, `Still busy with {activity} after {duration}` retains live
background-progress details. Use `{message}` wherever the original Full-mode
command or progress text should appear in custom wording.

Settings export proposes `chatgpt-desktop-access-settings.json` as the filename;
the user can choose a different name or location. Support reports continue to use
a timestamped text filename. Neither file is created until the user approves its
Save dialog.

After each newly installed version starts for the first time, NVDA opens a
concise current-version summary and places focus at the top. **View current
release notes…** and **View complete release history…** are also available in
the add-on's Settings panel.

## Input gestures

All add-on actions appear under **NVDA > Preferences > Input Gestures > ChatGPT
Desktop Access**. A default gesture can be changed or removed there, and an
unassigned action can be given a gesture if wanted.

### Chat titles

NVDA+Shift+C reads the current chat title. When you switch chats, the add-on
interrupts the previous speech and announces only the new title. It reads the
outer document from NVDA's focus ancestry when available, and announces after
native focus handling completes. Native focus speech is briefly suppressed
throughout the transition so it does not cover the
title. Keyboard input ends that suppression, and speech in other apps is
unaffected. Announcement pause and output settings continue to apply.

### Recent-message review

Control+1 through Control+0 review the ten most recent user or ChatGPT messages:

- Control+1 reads the most recent message.
- Control+2 reads the second-most-recent message.
- The sequence continues through Control+0, which reads the tenth-most-recent
  message.

Review announces the author and message text directly, without a numbered prefix.

Each position is a separately named action. These shortcuts work in both focus
mode and browse mode. In forked and side conversations, review follows the
conversation containing the focused message field. Each request refreshes a
bounded range of that conversation, so new messages are available immediately
and adjacent conversation panes are kept separate.

For a native list instead of the conversation web view, assign **Open the
current conversation's messages in a native list** under NVDA Input Gestures,
then use that assignment while ChatGPT is focused. No key is assigned by
default; NVDA+Alt+Shift+R is already used by NVDA for add-on compatibility.

The General settings page can enable or disable the list; it is enabled by
default. The dialog shows up to the newest 100
visible turns, oldest to newest. Arrow
through the list; Enter moves to the selected message's read-only full text.
Search and Refresh are available; Refresh requests a new scan without blocking
the dialog. Escape closes the dialog. Older turns
remain in ChatGPT's conversation view. The list does not send, edit, or
activate messages.

### Voice mode

NVDA+Alt+V starts or ends ChatGPT voice mode. **Mute or unmute the ChatGPT
microphone** has no default gesture; assign one in Input Gestures if wanted.

Earlier versions assigned NVDA+Alt+M to the microphone action. That key is NVDA's
default **Interact with math content** command, so the add-on no longer claims it.
An existing user-created microphone assignment remains configurable in Input
Gestures.

### Chat and Work

Above a new chat's message field, ChatGPT has a **Chat** and **Work** switch. The
two settings offer different tools and a different **Add files and more** menu.
NVDA+Alt+W reports which one is selected, for example "Work selected. Press
twice quickly to switch to Chat". Press NVDA+Alt+W twice quickly to switch. The
action is named **Report whether ChatGPT's message field is set to Chat or
Work; press twice to switch**. If the switch is not shown, such as inside an
existing conversation or in Codex, NVDA says so.

### What is attached to the message

NVDA+Alt+A says which files and tools are attached to the message you are
writing, for example "Attached: report.pdf. Tools: Web search", or "Nothing is
attached to the message". Tools such as Web search, Create image, and Deep
research appear inside the message field, where NVDA otherwise reads them only
as an unlabeled object. The action is named **Report the files and tools
attached to the ChatGPT message**. To remove a file, Tab or move in browse mode
to its **Remove** button above the message field.

### ChatGPT and Codex mode selector

NVDA+grave accent—the key normally labeled backtick (`)—opens and focuses
ChatGPT's native mode selector. The action is named **Open and focus the ChatGPT
and Codex mode selector**.

The command works without navigating to the top of the page. NVDA announces the
current mode. Use Up or Down Arrow to choose ChatGPT or Codex, then press Enter.

### Gesture scope and additional actions

The ten message-review commands, voice-mode command, microphone action,
mode-selector command, Chat and Work command, and attachment report are
implemented by ChatGPT's application module. Default
and user-assigned gestures are claimed only while ChatGPT or Codex has focus.
Outside both, NVDA and other add-ons remain free to use the same keystrokes.

Additional unassigned actions include:

- Repeat the latest activity or move through announcement history.
- Show or clear announcement history.
- Pause or resume announcements.
- Toggle Minimal and Full output or privacy redaction.
- Show or copy diagnostics and save a sanitized support report. The report
  names the installed ChatGPT app version, which changes with each ChatGPT
  update.
- Open usage and credits in the official ChatGPT account dashboard.
- Open searchable ChatGPT or Codex chat history.

Assign only the additional commands you want. The embedded browser deliberately
adds no Input Gesture actions; use NVDA's normal web-navigation commands instead.

### Chat history

**Open searchable and arrow-navigable ChatGPT or Codex chat history** opens a
responsive, mode-specific dialog from focus or browse mode. Type to search, Tab
from Recent chats to Archived chats, use Up and Down Arrow to browse, and press
Enter to open the selected chat.

On a Recent chat, Shift+F10 opens a Windows context menu. Focus starts on **Pin
or unpin chat**; press Down Arrow for **Archive chat**, then press Enter to run
the selected native ChatGPT action. On an Archived chat, Shift+F10 offers **Open
archived chat**.

If two Recent chats have the same title, the add-on cannot safely identify one
from the title alone. Open, Pin, and Archive then ask you to choose the intended
chat from ChatGPT's native Recents list; neither chat is changed automatically.

ChatGPT's native Recents region combines ChatGPT chats and Codex tasks. The
add-on separates that region using the active local Codex session index, so
ChatGPT history excludes Codex task titles and Codex history retains only Codex
task titles.

The add-on reads ChatGPT's exposed current-mode control because the application
document itself remains named ChatGPT in both modes. After a mode change, it
waits for the unified sidebar to settle and confirms two matching snapshots
before separating the entries. If history is opened too early, NVDA reports that
the list is refreshing instead of showing an unclassified list.

Codex archived titles are read from local JSONL session metadata. ChatGPT archived
titles come only from ChatGPT's accessible Archived chats view. If that view has
not been exposed yet, the dialog explains how to load it.

Message controls and source panels—including Share, Copy, Read aloud, response
ratings, Sources, Outputs, and More actions—are excluded from both history lists.

When Recents offers **Show more**, opening history activates that native control
one page at a time and waits for the accessible item count to grow. Each request
is limited to 20 ten-item pages; reopen history to continue if more pages remain.

This expansion uses only ChatGPT's **Show more** control. It does not simulate
scrolling in an infinite-scroll layout, it stops if focus leaves ChatGPT, and it
never changes archive state merely by opening history.

### Prompt-toolbar controls

The add-on improves **Add files and more**, the **model** control, and **Change
permissions** without adding commands or gestures. Reach them with normal Tab or
browse-mode navigation.

The desktop app's product selector switches between ChatGPT and Codex. Within
ChatGPT, the separate Chat/Work switch appears above a new chat's composer.
In Work and Codex, the model and reasoning control appears beneath the
composer. The add-on recognizes both full GPT-prefixed model names and shorter
labels such as **6 Sol Light** without keeping a fixed model list. The account
and app determine which choices are available; the add-on does not choose a
model or reasoning level automatically.

NVDA gives each recognized control a concise description while preserving its
native name, state, and action. For the model and permissions menus, use Enter
or Space to open, arrow keys to navigate, Enter to choose, and Escape to close.

The **Add files and more** button opens a popup that ChatGPT adds at the end of
the page. ChatGPT then returns keyboard focus to the prompt, where the arrow keys
move a highlight that is never announced, and Tab or Enter chooses the
highlighted option without saying which one it was.

The popup's options depend on where you are. In Codex, and in ChatGPT with
**Work** selected, it lists items such as Files and folders, Goal, Plan mode,
Sketch, and plugins, and may end with **Type to search files or chats**. In
ChatGPT with **Chat** selected, where the message field is named **Ask
ChatGPT**, it lists items such as Add photos & files, Add from library, Create
image, Web search, Deep research, and Sketch. The add-on handles both.

When you activate **Add files and more** with keyboard Enter, Space, or Braille
Enter, the add-on reads the popup and opens an **Add files and more** list. Each
option is listed title first, then its description and, when ChatGPT groups the
options, its section, for example "GitHub — Triage PRs, issues, CI, and publish
flows (Plugins)".

Use the arrow keys or type a first letter, press Enter to choose, or Tab to
**Filter options** and type part of a name. Escape cancels and closes ChatGPT's
popup.

After you choose, the add-on returns to ChatGPT, reopens the popup, and moves
ChatGPT's own highlight to your option one row at a time, checking each step,
then selects it. Keep your hands off the keyboard for a moment while it does
this. You then hear what was added to the prompt, such as "GitHub added", or
NVDA reads the dialog the option opened, such as **Select files**.

If the options cannot be read but the popup ends with **Type to search files or
chats**, the add-on instead returns NVDA to browse mode on that line. Press Up
Arrow to read the options above it and Enter to choose one.

If the popup does not appear, the add-on falls back to the separate
**Attach files or connect apps** control that some Codex views show below the
**User messages** navigation. If neither is present, the window changes, or you
navigate away, the add-on leaves focus alone. It only ever chooses the option
you picked, and never chooses a file for you.

#### The "/" and "@" suggestion menus

Typing "/" or "@" in the message field opens a suggestion menu of commands, or
of files, tools, and chats. ChatGPT keeps focus in the message field and moves
an unannounced highlight with the arrow keys. The add-on says how many
suggestions there are and which is highlighted, for example "Suggestions: 28.
Feedback, Send feedback about this chat, 1 of 28", and announces each one as you
press Up or Down Arrow, such as "Goal, Set a goal to keep pursuing, 2 of 28".
Typing more filters the list; the add-on announces the new first suggestion when
the list changes. Press Tab or Enter to choose, or Escape to close.

Turn this off with **Announce the "/" and "@" suggestion menus in the message
field** on the General settings page. If the separate Slash Menus add-on is
installed, this add-on leaves these menus to it so the two never speak at once.

#### Attachment menu diagnostics

If the popup still does not work, turn on **Enable sanitized diagnostic
logging** on the Advanced settings page, then open **Add files and more**. The
add-on records where the popup appears: NVDA's focus, UI Automation menus and
menu items, and any new ChatGPT windows. Then save a support report from the
Support settings page;
the capture is at the end. **Capture diagnostics for the open Add files and
more menu**, an unassigned Input Gestures command, captures on demand while the
menu is open. Only menu-like control names are recorded, never chat text.

If the desktop app does not expose a working attachment control, open the
conversation in ChatGPT on the web in your browser and use its composer menu.

## Embedded browser access

When ChatGPT exposes a browser or web-preview container through Chromium
accessibility, the add-on recognizes objects beneath that explicitly named
container. It also recognizes a genuine web document nested inside ChatGPT's outer
document, which is how some browser tabs are exposed. The native Browser submenu
and its commands are deliberately excluded. The add-on does not click, submit,
move focus, replace native roles, add control descriptions, or read the page on
the user's behalf.

The result works like an ordinary Chromium page in NVDA. In focus mode, use Tab
and Shift+Tab to move between controls, Enter or Space to activate the current
native control, and arrow keys where the control supports them.

Press NVDA+Space to switch between focus and browse modes. In browse mode, use
normal NVDA web navigation, including H for headings, K for links, F for form
fields, D for landmarks, T for tables, and NVDA+F7 for the Elements List.

None of these keys are intercepted or simulated by the add-on.

The add-on keeps its original Codex conversation virtual buffer while focus is
inside the embedded page. This allows Codex activity monitoring to continue
without treating the page as a new task or detaching from the conversation.

The Browser Access settings page has one option, enabled by default, for automatic
**Loading page** and **Loading complete** messages.

The add-on observes native Chromium document creation, busy-state changes, and
exposed loading progress. A short settle timer completes fast pages that do not
expose a final event. A longer safety fallback applies while Chromium reports
the document as busy.

Repeated events do not repeat the same message. Closing or leaving the embedded
browser cancels pending loading state, so an old page cannot announce completion
later. These status messages do not change focus, browse mode, the review cursor,
or the Braille reading position.

Announcement history contains at most 20 entries, stays in memory, and is
cleared when the monitored Codex document changes or NVDA exits.

## Testing and building

Run `build.ps1` to execute the automated tests, validate the translation
template and Python syntax, audit version consistency, dependencies, gesture
policy, archive layout, CRCs, and sound inventory, and create a reproducible
package under `outputs`.

GitHub Actions runs the same release checks on pushes and pull requests. If
Python is not available as `python`, pass its executable with `-PythonPath`.
Identical source files produce an identical package checksum, including across
LF and CRLF Git checkouts.

See `docs/TESTING.md` for the manual NVDA checklist used before publishing a
release. Translation contributors should see `docs/TRANSLATING.md`. Add-on Store
maintainers should see `docs/ADDON_STORE.md`.

## Release versioning

Add-on versions follow the current stable NVDA release. With NVDA 2026.2 stable,
the base line is `2026.2.0` and add-on patches are `2026.2.1`, `2026.2.2`,
`2026.2.3`, `2026.2.4`, `2026.2.5`, `2026.2.6`, `2026.2.7`, `2026.2.8`, and so on. A newer stable NVDA release starts a new matching line. Preview NVDA releases
do not change the add-on version line. See `docs/VERSIONING.md` for full details.

## Privacy

Full mode may speak commands, commentary, paths, file names, URLs, and search terms. NVDA's
debug log records spoken output, regardless of the add-on's sanitized internal
logging. Enable redaction or Minimal mode before sharing an NVDA log, and review
logs for private data before sending them to anyone.

The privacy-redaction action can be assigned in Input Gestures for temporary
privacy changes. Redaction also applies to complete commentary retained for Braille,
history, and Copy latest full Codex progress. Sanitized diagnostics report configuration
and monitoring state without including command text.

## Braille timing

Progress uses NVDA's standard braille flash-message mechanism. Its duration is
controlled by NVDA's global braille message-timeout setting.

Routine add-on Braille messages are suppressed while focus is in ChatGPT when
**Keep conversation reading stable** is enabled. While the user reads in browse
mode, ordinary streamed `Response:`, `ChatGPT said:`, and `Response complete`
live-region updates are also withheld from NVDA's native output handler. This
prevents them from replacing speech, the browse cursor, or the Braille viewport.

Non-urgent add-on completion flashes are withheld from Braille at the same time,
while their selected speech and sound output continues. Focus-mode response
output, permission prompts, dialogs, and urgent alerts are never suppressed.

Full conversation-buffer inspection is paused while the prompt is being edited
and for three seconds after keyboard or Braille navigation in a conversation.
Direct status and permission events remain available without waiting for a scan.
When Chromium replaces its buffer, the add-on inspects only a bounded tail
instead of copying the full chat.

After a final response, Working pulses and continuous sounds pause while the
add-on waits five seconds for another operation and requires the Stop control to
be absent. It then confirms the task is idle.

Closing or hiding the ChatGPT window for two seconds clears retained activity
even if Electron helper processes remain. Simply moving to another application
keeps monitoring active.

While contracted Braille is entered in the focused ChatGPT prompt, the add-on also
protects an active new-word composition from the delayed caret event Chromium can emit
for the preceding word. This does not change translation tables, consume Braille
gestures, replace NVDA's input handler, or run outside the ChatGPT prompt.

## Installation and removal

Install the `.nvda-addon` package through NVDA's Add-on Store manager. Restart
NVDA when requested. Remove or disable it from the same manager. Upgrades retain
saved settings; new features use safe defaults.

## Support and compatibility

The add-on supports NVDA 2023.1 and later and has been tested with stable NVDA
2026.2.
If a Codex interface update stops announcements, enable sanitized diagnostics
and provide an NVDA log after removing remote keys and other personal data.

After each ChatGPT update, the add-on checks once that it can still find the
message field, **Add files and more**, and the ChatGPT and Codex mode switch.
The result is in the NVDA log and on the support report's **ChatGPT
compatibility check** line. If something is missing after an update, NVDA says
once that some add-on features may not work until the add-on is updated.

## License

ChatGPT Desktop Access is free software distributed under the GNU General
Public License, version 2 or, at your option, any later version. See
`LICENSE.txt` for the complete license terms.
