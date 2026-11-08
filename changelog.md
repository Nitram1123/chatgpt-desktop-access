# Changelog

All notable changes to ChatGPT Desktop Access for NVDA, formerly Codex Access
Toolkit and Codex Status Announcer, are recorded here. The active release line
follows stable NVDA.

## Unreleased

- Added French translations for the add-on's settings, commands, and announcements.
  Regional French settings use the same translation.
- Added NVDA+Shift+C to read the current chat title. NVDA also announces the
  title when you switch to another chat.

### What to test

- With NVDA set to French, open the add-on settings and pause and resume
  announcements. Check that the settings and the two announcements are in French.
- Press NVDA+Shift+C inside a chat. Switch to another chat and check that NVDA
  announces its title once. Repeat from the chat history dialog.

## 2026.2.19

- Typing **/** or **@** in the message field announces ChatGPT's suggestion
  menu: how many suggestions there are and which is highlighted, then each one
  as you press Up or Down Arrow, with its position, such as "Goal, Set a goal to
  keep pursuing, 2 of 28". These menus keep focus in the message field and move
  an unannounced highlight, so NVDA said nothing about them; this is reported
  to OpenAI as openai/codex issues 32375 and 34339. The add-on reads them the
  same way as Add files and more, on UI Automation's thread. A General setting
  turns it off, and the add-on leaves these menus to the Slash Menus add-on
  when that is installed. Verified live on 24 October 2026 with ChatGPT
  26.1021.2667.0: "/" announced "Suggestions: 28. Feedback, Send feedback about
  this chat, 1 of 28" and Down Arrow announced the next suggestions; "@"
  worked the same way; the Add files and more list still opened.
- After each ChatGPT update, the add-on checks once that it can still find the
  message field, Add files and more, and the ChatGPT and Codex mode switch. It
  names anything new, such as an unfamiliar message field label, in the NVDA
  log and on the support report's ChatGPT compatibility check line, and says
  once that some features may not work if something is missing. Checked live
  with ChatGPT 26.1021.2667.0: "everything found".
- The Working sound no longer starts when ChatGPT is idle because a chat title
  in the "@" or Add files and more menu reads like Codex progress. These menus
  list recent conversations, such as "Using VoiceOver Rotor, ChatGPT
  conversation", and ChatGPT keeps their rows on the page after the menu
  closes. The add-on read that row as a tool starting. Rows of these menus are
  now never read as activity, in the conversation scan or in live events,
  alongside the sidebar chat titles below. Verified live on 24 October 2026
  with such a row on the page: the add-on stayed idle.
- Everything the add-on recognizes in ChatGPT by its wording or web class names
  is now listed in one place at the top of core.py, so a ChatGPT rename can be
  fixed in one line. A test keeps those names from spreading again.

- Naming a new project in Codex no longer pulls focus away from the **Project
  name** field (GitHub issue 4). Typing a name renames the dialog's **Change
  marker for** button, and each rename made the add-on think a new dialog had
  opened and move focus to that button, so in focus mode NVDA seemed stuck on
  it. The add-on compared NVDA objects by identity, but NVDA creates a new
  object for every lookup of the same control; it now compares the controls
  themselves. Verified live on 21 October 2026 with ChatGPT 26.1013.4894.0:
  "Demo" was typed in focus mode and focus stayed in Project name.
- The Working sound no longer starts when ChatGPT is idle because a chat in the
  sidebar has a title that reads like Codex progress. A recent chat named
  "Using VoiceOver Rotor" matched the "Using ..." tool pattern, so the add-on
  believed a tool was running and played the continuous Working sound. Recent
  and archived chat titles are no longer read as activity, whether found by the
  conversation scan or announced live as ChatGPT draws the sidebar, and a sidebar
  chat that has focus when you return to ChatGPT no longer moves the browse
  cursor. This mostly showed on a new chat, where the sidebar and the page are
  read together.
- **NVDA+Alt+W** reports whether ChatGPT's message field is set to **Chat** or
  **Work**, the switch above a new chat's message field. Press it twice quickly
  to switch. The two settings offer different tools and a different Add files
  and more menu; a tester's report showed the switch is easy to miss. The
  command works only while ChatGPT has focus, uses ChatGPT's own switch, and
  says so when the switch is not shown. Its UI Automation work runs off
  NVDA's main thread.
- **NVDA+Alt+A** says which files and tools are attached to the message you
  are writing, such as "Attached: report.pdf. Tools: Web search", or "Nothing
  is attached to the message". Tools such as Web search are chips inside the
  message field that NVDA reads only as an unlabeled object. The command only
  reports; files keep ChatGPT's own Remove buttons. Removing a tool chip was
  tried and left out: selecting the chip and pressing Delete also removed the
  typed text. Verified live on 21 October 2026 with ChatGPT 26.1013.4894.0:
  with Chat selected it reported a file and Web search together, and nothing
  after both were removed; with Work selected it reported the Documents plugin.
  Inside an existing conversation it says no message field with Add files and
  more is shown.
- NVDA+Alt+W verified live: one press said "Work selected. Press twice quickly
  to switch to Chat"; two presses switched to Chat; inside an existing
  conversation it said the switch is not shown.
- The support report and the NVDA log name the installed ChatGPT app version,
  such as "package 26.1013.3656.0". ChatGPT updates itself often, and the
  version is usually the first question when something changes.
- The readme describes both Add files and more menus, for Chat and for Work,
  instead of only the one that ends with "Type to search files".

## 2026.2.17

2026.2.15 and 2026.2.16 were test versions only; their changes are listed here
too.

- **Add files and more** works when ChatGPT's composer is set to **Chat**, as
  well as **Work**. ChatGPT's chat mode has a Chat and Work switch above the
  prompt. With Chat selected, the prompt is named **Ask ChatGPT** and the menu
  offers different options, such as Add photos & files, Add from library,
  Create image, Web search, and Deep research. That menu has no "Type to search
  files or chats" line, which is how the add-on found the menu, so it listed
  nothing. The add-on now also finds the menu by ChatGPT's row markers, in
  both NVDA document modes. A tester's NVDA log from 2026.2.16 showed exactly
  this: the button was recognized, then "found no Add files and more popup".
- **Ask ChatGPT** is recognized as the prompt.
- If the menu still cannot be found, the NVDA log now summarizes what follows
  the prompt: control types and ChatGPT's row and heading markers only, never
  names or text.
- Verified live on 17 October 2026 with ChatGPT 26.1013.3656.0: with Chat
  selected, all 13 options were chosen through the add-on, including Add
  photos & files (the file picker opened), Add from library, Create image and
  Web search (their chips appeared in the prompt), Deep research, Sketch, and
  the plugins. With Work selected, the menu now has 21 options and no section
  headings; it still opens, and options are chosen.

- A tester reported that **Add files and more** still did not open its list in
  ChatGPT chat mode, while Codex worked, with every NVDA UI Automation setting
  and in a fresh portable NVDA. Chat mode works on our test system, so the
  tester's ChatGPT shows something the add-on did not recognize. The add-on no
  longer depends on one wording:
  - The prompt is also recognized by its editor, a ProseMirror field, whatever
    its label says. The label was the cause of the 2026.2.14 chat-mode bug.
  - The button is also recognized as **Add photos and files**, **Attach files**,
    or **Upload files**, as well as **Add files and more**.
- When Enter or Space lands on an attachment-like button, the NVDA log now
  records the button's name and state, whether the add-on recognized it,
  whether it is attached to the conversation, and the mode. Every reason for
  not opening the list is also logged. These lines use NVDA's normal log
  level, so an ordinary NVDA log shows where it stopped, without changing any
  settings. Chat text and conversation titles are never logged.
- Verified live on 16 October 2026: the list still opens in chat (32 options)
  and Codex (31 options), and the new log line reports the press.

- **Add files and more** opens its list right away when NVDA reads ChatGPT
  through UI Automation instead of its usual Chromium document, in chat and in
  Codex. In that mode the add-on searched NVDA's whole copy of the page to find
  the popup, which took about six seconds; pressing another key in that time
  cancelled it, so the list seemed never to open. The popup, its options, and
  the Add files and more button are now found through UI Automation directly,
  which takes well under a second. Measured live: Enter to list in 1.3 seconds,
  down from 6.
- NVDA no longer freezes for seconds at a time in that mode. Each conversation
  scan there blocked NVDA for 2 to 3 seconds and ran as often as every 5
  seconds during a task. A slow scan is now followed by a pause of twenty times
  its length, up to a minute, and no scan runs while Add files and more is
  opening. Scans in NVDA's usual document are fast and are not delayed.
- Diagnostic logging no longer reads NVDA's UI Automation copy of the page when
  Add files and more opens, which blocked NVDA for about three seconds.
- Choosing an option, and Cancel, work in that mode too. They press **Add
  files and more** to reopen or close ChatGPT's popup, and NVDA cannot press
  that button in its UI Automation document because ChatGPT exposes it only as
  expandable. The add-on now expands or collapses it directly. Every other
  button the add-on presses, such as voice controls and chat-history actions,
  gets the same fallback.
- Named buttons, such as **Show more** in chat history, are found through UI
  Automation in that mode instead of by searching NVDA's copy of the page,
  which missed them.
- Verified live on 16 October 2026 in a ChatGPT chat with NVDA reading ChatGPT
  through UI Automation: all 32 options were chosen through the add-on, and
  each was announced, such as "Crossroads added". The usual document was
  checked again afterward.
- NVDA picks UI Automation for ChatGPT on its own on some systems, without any
  setting being changed. It is also used when **Use UI Automation to access
  Chromium-based browser controls** is set to Yes in NVDA's Advanced settings.
- What to test: press Enter on **Add files and more** in chat and in Codex, in
  browse and focus mode. If it still does not open, turn on diagnostic logging
  and send the support report.

## 2026.2.14

- **Add files and more** now works in ChatGPT chat mode as well as Codex. The
  chat-mode prompt is named **Work with ChatGPT**, which the add-on did not
  recognize, so after the popup opened it decided focus had moved elsewhere and
  left it alone. The add-on now recognizes that prompt everywhere it checks for
  one, including conversation detection and attachment diagnostics.
- Verified live on 14 October 2026 in a ChatGPT chat: all 32 options were chosen
  through the add-on. Chat mode adds **Work in a project**; Files and folders
  opened Select files, Goal and Plan mode opened their composers, Sketch opened
  the Sketch editor, and every plugin, app, site, and conversation added its tag.
- Option titles such as "Work in a projectStart a chat in a project" are now
  split into title and description in the list. Rows where ChatGPT puts a
  space between the two, such as "Code Review Review and manage GitHub pull
  requests", are now split as well: the list takes each row's exact title and
  description from UI Automation when it agrees with NVDA's document.
- Verified live on 14 October 2026 in a Codex task: all 31 options were chosen
  through the add-on again, and the rows that used to be joined were chosen
  by their new titles.
- **Add files and more** also works when NVDA reads ChatGPT through UI
  Automation instead of its usual Chromium document. That document mode does
  not carry ChatGPT's class names, so the add-on could not see which row was
  highlighted and had to count rows, which a non-selectable row could throw
  off. It now reads the rows, section names, and highlight directly from UI
  Automation in that case. Verified live by choosing every option through this
  reader.
- What to test: in a ChatGPT chat, press Enter on **Add files and more**,
  choose options from each section, and confirm each is chosen. Repeat in Codex.

## 2026.2.13

- Fixed plug-in installation progress. A `for _ in range(...)` loop replaced
  the translation function, so every announcement raised TypeError. The same
  defect stopped the unarchive fallback message after 25 focus attempts. A test
  now rejects any function that both assigns and calls `_`.
- The conversation message list now destroys itself when closed. Previously
  Close, Escape, and Cancel left the dialog open, and the next open created a
  second copy.
- The message list and its Refresh button now work in conversations longer than
  the bounded head-and-tail scan. When the list asks for turns, the next poll runs
  the same bounded scan used by Control+1 through Control+0. Otherwise new tail
  turns are merged with earlier cached turns. The possibly incomplete first tail
  turn is never kept on its own.
- Messages whose whole text matches interface wording, such as Stop, Retry,
  Copy, or a time, are kept as messages. Interface text after a message, or two
  interface labels in a row, still ends the turn.
- Usage-limit retry and reset times keep decimals and a.m. or p.m. suffixes, for
  example "try again in 2.5 hours" and "try again at 3:45 p.m.".
- Archived Codex task IDs from the local index are matched case-insensitively,
  so their titles are not replaced by "Archived task" placeholders.
- Permission dialogs focus Deny or Reject before Allow or Approve. The add-on
  still only moves focus and never activates a decision.
- The current activity summary and the verbosity toggle announcement are now
  translatable.
- Removed the embedded browser navigator, page summary, snapshot, and
  external-open code. No command could reach it, and it read a removed setting.
  Embedded browser loading announcements are unchanged.
- Completion counts of zero, such as "Tests passed: 0 errors", no longer play
  the failure sound or interrupt speech as urgent.
- Status words must match whole words. Labels such as "Random seed", "Ranked
  results", "Built-in tools", and "Ready" are no longer reported as finished
  commands, builds, or file reads.
- Elapsed times include hours and minutes. "Working for 1m 30s" is 90 seconds,
  which also corrects the Working announcement interval and Informative timing.
- Translation template fixes: 33 status phrases and the hour, minute, and second
  wording reached translation only through variables and were missing from the
  template. App-module command descriptions shown in Input Gestures were also
  missing because the extractor did not read `appModules`.
- An unexpected error in a ChatGPT command, such as Control+1 or the mode
  selector, is logged and reported instead of escaping as an NVDA script error.
- Saving settings with the message list disabled no longer tries to close a
  message list the user has already closed.
- The chat history Refresh button now asks for a fresh sidebar scan. Previously
  it only redisplayed the cached lists.
- Added **Add files and more** diagnostics. With sanitized diagnostic logging
  on, opening the popup records NVDA's focus and IA2 view of the button, UI
  Automation focus, menu-like UI Automation elements under ChatGPT's own windows
  (compared with a capture taken when the button was focused), and new ChatGPT
  top-level windows. Results go to the NVDA log and the end of the support
  report. UI Automation work runs on NVDA's UIA worker, is limited to ChatGPT's
  windows and 400 elements, and never searches the desktop.
- **Add files and more** now works from the keyboard in ChatGPT and Codex.
  After Enter, Space, or Braille Enter on the button, the add-on reads the
  popup and lists its options in a native **Add files and more** dialog, title
  first, with a filter box: Add (Files and folders, attach an app screenshot,
  Goal, Plan mode, Sketch), Plugins, Apps, Sites, and ChatGPT conversations.
  Enter chooses the option; Escape closes the dialog and ChatGPT's popup.
- How it works, from live NVDA logs: ChatGPT adds the popup at the end of the
  page, starting with **Type to search files or chats**, and returns keyboard
  focus to the prompt, where the arrows move a highlight that is never
  announced. UI Automation exposes no menu items or window. ChatGPT closes the
  popup when the dialog takes focus but keeps its rows on the page, hidden, and
  ignores clicks on them. The add-on therefore uses the popup's own keyboard
  handling: it waits until ChatGPT is in front with focus in the prompt, reopens
  the popup with the real **Add files and more** button, then presses Down
  Arrow one row at a time. ChatGPT marks the highlighted row with a class name,
  so after each key the add-on waits until NVDA's copy of the page shows the
  highlight has moved, and presses Tab only on the chosen row. Tab is used
  because Enter could send the prompt. Keys are never sent unless focus is in
  the prompt, and the user is told if the option could not be chosen.
- Rows are recognized by ChatGPT's row and section-heading class names, so a
  row that is not a button, such as "Attach appshot", is still counted. A row
  is found again by its text ignoring spacing, then by its position within its
  section, because the screenshot row renames itself with the last app used.
- After a choice that changes the prompt, the add-on announces the tag ChatGPT
  added, such as "Code Review added". When the choice opens a dialog, such as
  **Select files** or the **Sketch editor**, NVDA announces that instead.
- Option titles that ChatGPT runs into their descriptions, such as
  "GitHubTriage PRs" or "PDFRead, create", are split in the list. Conversation
  and site rows are split at their "ChatGPT conversation" and ".chatgpt.site"
  suffixes. Names such as GitHub, LinkedIn, AirPlay, and ChatGPT stay whole.
- Every option was verified live on 13 October 2026 with an in-NVDA test that
  chose each of the 31 options through the add-on: Files and folders opened
  Select files, Goal and Plan mode opened their composers, Sketch opened the
  Sketch editor, and every plugin, app, site, and conversation added its tag.
- If the options cannot be read, the add-on returns NVDA to browse mode on
  **Type to search files or chats**, the popup's last line, where Up Arrow reads
  the options. If the popup does not appear, it falls back to the Codex **Attach files or connect apps** control. When an option
  receives real focus, NVDA's own announcement is used instead of a second
  add-on announcement.
- Attachment diagnostics also list the controls and short labels after the
  prompt, where the popup appears. Recording starts at the prompt, so
  conversation text before it is never included.
- What to test: install a plug-in and listen for progress; open the message list
  in a long conversation, use Refresh, then close it with Escape and reopen it;
  send "Stop" as a prompt and review it with Control+2; trigger a permission
  dialog and confirm focus lands on Deny; run tests that report "0 errors" and
  confirm the normal completion sound; repeat the 2026.2.12 responsiveness
  checks.

## 2026.2.12

- Handles NVDA's RootProxyTextInfo wrapper when selecting the UIA bulk-range
  path. Only private copied ranges are changed; proxy ownership is preserved.
  Tests also cover wrapped UIA providers and cyclic proxy rejection.
- Restored bounded Chromium UIA scan ranges using NVDA's base UIATextInfo
  endpoint operation, bypassing the web override's character-by-character
  replaced-content walk. This applies to polling, recent-message recovery,
  conversation attachment, and replacement checks. Unknown providers still
  fail closed. Regression fixtures prohibit calls to the web move override
  and check both short and long UIA ranges and start-of-document clamping.
- What to test: open History in both modes, review Control+1 through Control+0
  in a large chat, start NVDA with ChatGPT closed and then open ChatGPT, and submit with keyboard and
  Braille Enter. Verify responsiveness and that Working clicks stop at completion.
- Delayed chat actions are bound to their initiating window, and hiding a
  pending dialog cancels its focus timer. Added regression coverage for input
  hooks, stale popup generations, defunct dialogs, foreground loss, and window
  replacement.
- Prompt gesture processing now runs on NVDA's main queue; the input hook
  retains only attachment activation timing and immutable identifiers.
- Delayed popup focus yields to intervening user input and skips unavailable,
  invisible, or defunct controls. Unsupported provider scans are disabled once
  per buffer rather than retried on every poll.
- Corrected incomplete recent-cache recovery without hiding short message lists.
- Safety audit: unknown text providers fail closed rather than using character
  walks for transcript scans. Recognized offset and UIA providers use bounded
  ranges; live events remain enabled.
- Incomplete split scans no longer overwrite the recent-message cache; explicit
  review retries incomplete caches. Delayed chat actions and unarchive focus
  stop when ChatGPT no longer owns the foreground. Removed a duplicate guard.
- What to test: startup with a UIA conversation, long responses and recent-message
  review, then Alt+Tab immediately after an archive or unarchive request.
- Working clicks now pause as soon as a response-completion marker is detected,
  rather than continuing while the stop control and completion state settle.
  New activity can resume ticks if completion was tentative. What to test:
  no Working ticks after the completion bell; a subsequent prompt ticks normally.
- Applied constant-time offset range extension to recent-message lookups,
  buffer replacement checks, and latest-response navigation as well as polling.
  Private scan ranges change without moving the user's caret or selection.
- Replaced character-by-character Chromium scan-range movement with direct
  offset ranges. Small buffers require no range movement. Failed range
  creation no longer falls back to scanning the entire conversation.
  What to test: stream a long response while typing with keyboard and Braille;
  verify activity feedback, recent messages, and responsiveness after restart.
- Recognized the current desktop prompt label **Work with Codex** for prompt
  tracking, conversation attachment, and the typing protections. Previously
  a task-titled document with this prompt could remain unattached, leaving
  activity sounds and submission feedback silent.
- Removed UIA description/help-text queries from embedded-browser focus
  classification. It uses container names and nested-document structure,
  avoiding the help-text call shown in a live watchdog recovery.
- Reused NVDA's resolved focus ancestors and the verified conversation buffer
  during navigation. Mode and embedded-browser classification now runs only
  when needed to attach or verify a buffer; candidates without a buffer are
  skipped before classification. This fixes repeated parent-chain queries
  observed in a watchdog recovery during a ChatGPT focus event.
- Background buffer discovery no longer borrows the foreground app's ancestor
  list. Parent discovery stops cleanly on a cycle or an unavailable provider.
- Discarded the previous prompt object when a chat or Chromium virtual buffer
  changes. Recent-message review can no longer anchor to a prompt from the
  prior conversation that Chromium has kept alive.
- Limited routine conversation scans to the sidebar and newest transcript
  ranges in large chats. This avoids traversing the entire Chromium virtual
  buffer on NVDA's main thread for every status check while retaining the
  sidebar history, current activity, and recent-message data. Smaller chats
  continue to use the original complete scan.
- The package audit now compares every archived file with the current source
  bytes, so an older package with the same version and archive layout cannot
  pass validation unnoticed.
- Scoped content-change handling to the ChatGPT app before reading accessibility
  names or states. An unrelated app's controls could previously trigger a slow
  display-text query and a cancelled add-on mode-switch event on NVDA's main
  thread. Focus and foreground tracking still observe app transitions.
- Fixed the ChatGPT-mode attachment handoff for hardware Enter and Space.
  Those keys arrive on NVDA's input-hook thread, while the earlier workaround
  checked for activation only on the main thread. The add-on now records a
  short-lived input candidate without reading Chromium accessibility objects
  on the input-hook thread, then verifies the exact **Add files and more**
  control on the main thread. The matching expanded-button event can confirm
  the activation even when it arrives before the queued verification.
- Kept the handoff conditional on the exact button, current ChatGPT window,
  and user navigation. Braille Enter continues through the existing path.
  This does not make an inaccessible original popup accessible and does not
  automatically choose an attachment.
- Prevented a delayed ChatGPT pop-up focus request from pulling focus back
  after switching to another app or another ChatGPT window. The request is
  cancelled on app deactivation and rechecks the live focus and window before
  moving focus.
- Attachment-item fallback announcements now respect the add-on's Speech and
  Braille master switches instead of forcing both channels on.

### What to test

- Restart with the **Work with Codex** prompt open. Confirm activity monitoring
  attaches, then type and correct a prompt using Braille and keyboard input.
  Submit it and confirm submission, Working, and completion cues. Open a
  download link or other control and check for browser-detection watchdog
  recoveries. Confirm native embedded-browser loading notices still work.
- Navigate a large chat with arrows, headings, and Braille controls, then
  Alt+Tab away and back. Confirm focus stays where expected and the log has
  no watchdog recovery involving `_rememberBuffer` or repeated mode ancestry
  queries. Switch modes and open History to confirm fresh mode detection.
- Open one chat, read a recent message with Control+1, then switch to another
  chat without restarting NVDA. Control+1 should read the new chat's latest
  available message, never the previous chat's message. Repeat after a mode
  switch and after Chromium refreshes the conversation view.
- Restart NVDA in a very large ChatGPT or Codex conversation, then review
  speech, Braille, and typing responsiveness. Check the Support timing report
  and log for slow conversation scans or watchdog recovery. Verify History,
  recent-message commands, and active/completed task cues still work.
- With this add-on enabled, navigate an unrelated app such as Access Chat and
  confirm its controls remain responsive. The NVDA log should not contain
  ChatGPT Desktop Access name-change handling errors for that app.
- In the Microsoft Store ChatGPT app, open ChatGPT mode. In focus mode and
  browse mode, activate **Add files and more** with hardware Enter, hardware
  Space, and Braille Enter. Where **Attach files or connect apps** is present,
  confirm focus lands on it. Activate that control with Enter, use Down Arrow
  to reach **Attach files or folders**, and press Enter. Confirm the Windows
  **Select files** dialog opens; an expanded button alone is not success.
- Repeat in Codex mode. Navigate away or close the popup immediately after
  opening it and confirm there is no delayed focus jump. Type spaces in the
  prompt with keyboard and Braille input and confirm typing stays responsive
  and does not move focus to the attachment menu.
- Check the NVDA log for exceptions or watchdog recoveries during these steps.
  This local test package is not automatically installed or published.
- Open a ChatGPT permission or other pop-up, then immediately Alt+Tab to a
  different app. Focus must stay in that app. Reopen the pop-up normally and
  confirm focus still enters its first useful control. Turn off add-on Speech
  or Braille separately and confirm attachment-item fallback announcements
  use only the enabled channel.

## 2026.2.11

- Added content-free timing measurements for whole-conversation scans and
  background mode probes. The Support diagnostics report last and maximum
  durations and slow-operation counts. Slow warnings are rate-limited in the
  NVDA log and never include chat text.
- Recognize alternative accessible mode-switch labels and descriptions while
  retaining the native selector. Only a button with explicit selector semantics
  can establish a mode; a similarly named sidebar chat is not enough. Added
  anonymized Chat, Work, and Codex accessibility fixtures.
- An unavailable optional Chromium help-text or state property no longer hides
  a valid mode-switch label. Failed background-probe scheduling also clears its
  timing state, and model controls are excluded from selector probing.
- Removed the **Add files and more** hint after live testing showed that the
  button can report expanded while ChatGPT exposes no attachment choices or
  file picker to NVDA. The hint incorrectly implied those choices were
  navigable. The add-on still announces attachment items if ChatGPT exposes
  them, and it still ignores late expanded events after the popup closes.
  A later log showed a separate native **Attach files or connect apps** menu
  after the User messages navigation. Its **Attach files or folders** item
  opened the Windows **Select files** dialog. In Codex views where that exact
  native menu is present, explicitly activating **Add files and more** now
  moves focus to the native attachment menu button. It never selects a file,
  and it leaves focus alone if that control is absent, the user navigates, or
  the ChatGPT window changes. This is a conditional workaround, not a claim that
  the original popup is accessible in every view.
- Fixed the first-open timing gap found in the live log: Braille Enter on **Add
  files and more** could expand the button before the add-on attached its
  conversation buffer, so no focus move was attempted. The explicit activation
  is now retained until that buffer becomes available, with the same
  exact-control, window, and user-navigation checks before moving focus.
- A second live log showed that Chromium did not deliver the expanded-state
  event needed by that handoff. The verified Enter or Space on the exact button
  now retains the target directly and completes the focus move after the
  conversation buffer attaches. Attachment UI inspection is confined to
  NVDA's main thread; the Braille input thread no longer touches Chromium's
  accessibility objects. The browse caret is also aligned with the native menu
  control when NVDA permits it, so Braille and arrow navigation start there.
- Skip conversation-buffer ancestry scans for native Windows dialogs owned by
  ChatGPT.exe. The live log showed a half-second NVDA watchdog recovery while
  the **Select files** dialog opened and the add-on followed the dialog's
  UIA/IA2 parent chain. The native chooser remains NVDA's to announce.
- Added a repeatable manual performance checklist for large conversations,
  Braille typing, mode changes, and NVDA restart.

### What to test

- Open a large conversation, type with both a keyboard and a Braille display,
  and confirm navigation and typing stay responsive. In Support diagnostics,
  check conversation-scan timing and slow counts before and after the run.
- Switch between Chat, Work, and Codex. Open History in each view; Chat and
  Work should use the ChatGPT history, and Codex its separate history. Check
  mode-probe timing and confirm similarly named sidebar chats do not switch
  modes.
- Restart NVDA and repeat the large-chat and mode-switch tests. Confirm
  monitoring reattaches without a main-thread stall.
- Open **Add files and more** in focus mode and browse mode. Confirm no
  misleading exploration hint plays. In a Codex task with **Attach files or
  connect apps** available below User messages, confirm focus moves to that
  menu button after Enter, Space, and Braille Enter on **Add files and more**.
  Open the native menu, choose **Attach files or folders**, and confirm the
  Windows **Select files** dialog opens. Repeat after changing tasks and with
  the native Sources control absent; focus must not jump elsewhere. Close the
  popup or navigate immediately after activation and confirm no delayed focus
  jump. Closing the menu must not announce a stale attachment item. When
  **Select files** opens, confirm NVDA reads the file-name field without a
  watchdog recovery in the log.

## 2026.2.10

- Updated model-control recognition for the desktop app's shorter labels,
  including examples such as **6 Sol Light**, **6.1 Sol Light**, and **Astra
  Light**, while retaining GPT-prefixed and older model names. A sentence
  mentioning a model is no longer mistaken for the model button.
- Updated the model control's NVDA help to refer to both model and reasoning
  choices. The add-on still uses ChatGPT's native picker and never selects a
  model or reasoning level for the user. Availability remains account-dependent.
- Restored serialized click and tone playback from the sound-capable 2026.2.9
  test package. Working ticks yield to meaningful cues; command and file cues
  no longer cut one another off. Pending operation sounds are discarded when
  the task ends, while the final completion cue is retained.
- Ignore stale operation-completion labels that appear after the whole task has
  already finished. This prevents a second completion click and announcement
  from following the task-finished cue; failures remain announceable. Sound
  starts and queued sounds are logged again for timing diagnostics.
- Updated **Open usage and credits** to ChatGPT's current Settings → Usage
  address. The previous Codex-specific address opened the main ChatGPT page
  instead of the usage dashboard.

### What to test

- In ChatGPT Work and Codex, move to the model and reasoning control under the
  composer. Confirm NVDA announces its native name and state and the updated
  help. Open it and verify the available model and reasoning choices remain
  navigable and selectable through the native interface.
- Repeat with a short model label (for example, **6 Sol Light**) and a
  GPT-prefixed label (for example, **GPT-6 Astra Light**) if both are available
  to the account. Confirm the add-on does not announce a model as selected
  until the app itself selects it.
- Switch among ChatGPT Chat, ChatGPT Work, and Codex using the app's controls.
  Confirm the add-on's mode, history, and prompt monitoring still attach to
  the intended conversation without moving focus.
- Submit a prompt that runs several commands or file edits. Confirm one
  submission cue, regular Working ticks, and distinct command/file cues that
  never interrupt one another. When the final answer arrives, confirm the
  Working ticks stop and no historical operation click plays afterward.
- Switch away from ChatGPT during a running task, then return. Confirm sounds
  report monitoring state without reviving a completed task. Check both click
  and musical-tone styles if available.
- On the Support settings page, activate **Open usage and credits**. Confirm the
  default browser opens ChatGPT Settings → Usage rather than the main chat page.

## 2026.2.9

- Rebuilt from the published 2026.2.8 source. The initial step restored
  the duplicate-title safety check in Chat History. When two visible Recent
  chats share a title, Open, Pin, and Archive explain the ambiguity and leave
  both chats unchanged. The user can choose the intended chat from the native
  Recents list. Unique titles keep their existing behavior.
- No queued-message, sound, focus, browser, or activity-heading experiments
  from the abandoned 2026.2.9 build are included yet.
- Added an app-scoped **Open the current conversation's messages in a native
  list** action with no default keyboard shortcut. NVDA+Alt+Shift+R conflicts
  with NVDA's add-on compatibility command, which prevented the list from
  opening in the live test. Users can assign their preferred key in NVDA
  Input Gestures. The list presents up to the
  latest 100 visible turns from the existing conversation scan. Arrow through
  the list, press Enter to
  read a selected message in the read-only text pane, or search and refresh.
  Older turns remain available in ChatGPT's native conversation view. This
  dialog never sends or edits a message.
- Added **Enable native conversation message list** on the General settings
  page. It is on by default. Turning it off prevents the assigned action from opening
  the list and closes the list if it is open; ChatGPT's native conversation
  view is unaffected.
- Fixed the list's Refresh button so it requests a new conversation scan
  instead of redisplaying the same cached messages. The scan runs after the
  button handler returns to keep NVDA responsive.
- Moved focus into the message list after its dialog is shown, so NVDA can
  announce the selected message when the list opens.
- Automatic response reading is deliberately reserved for the next separate
  increment so it can be tested independently of message-list navigation.

### What to test

- Find two Recent chats with the same title. Select that title in Chat History
  and try Enter, Pin, and Archive. Each action should explain the ambiguity;
  neither chat should change.
- Repeat with a unique title. Open, Pin, and Archive should still work normally.
  Switch between ChatGPT and Codex modes and confirm each history list remains
  separate. Check that ordinary response headings, typing, Braille reading,
  and Working sounds behave just as they did in 2026.2.8.
- Assign **Open the current conversation's messages in a native list** to an
  unused gesture in NVDA Input Gestures. Open a large conversation and press
  that gesture. Arrow through
  the message list, press Enter to read full text, search, refresh, and Escape
  back to the conversation. Confirm that prompt text, browse position, and
  Braille reading remain intact; Control+1 through Control+0 still read the
  newest ten messages.
- On the General settings page, turn **Enable native conversation message
  list** off. The assigned gesture should explain that the list is disabled.
  Turn it back on and confirm the list opens again. Confirm NVDA+Alt+Shift+R
  continues to run NVDA's own command rather than this add-on.

## 2026.2.8

- Fixed unsent draft deletion being mistaken for prompt submission. Clearing the
  prompt with Backspace, Delete, selection deletion, or Braille editing no longer
  starts Processing sounds, background clicks, or elapsed-time announcements.
  Real Enter and Braille Enter submissions remain immediate; mouse or touch
  submissions are confirmed from the posted message and active Stop control.
- Added speech and Braille feedback for the currently selected item in ChatGPT's
  **Add files and more** popup. Feedback is restricted to that popup, accepts
  menu-item, list-item, and button-style Chromium representations, suppresses
  duplicate events, and expires or clears when the popup closes.
- Fixed Chat History opening the Codex list after the user changed to ChatGPT
  with the native mode selector. The add-on now rechecks the authoritative mode
  control once the selector closes, refreshes the newly selected mode's cache,
  and keeps the UI Automation query off NVDA's main thread.
- Made NVDA+Alt+O a single-step Chat History command even when the current mode
  has not been detected yet. The add-on now opens History automatically as soon
  as the off-thread mode check and mode-specific cache are ready, uses the
  virtual buffer as an independent fallback, and reports a bounded failure
  instead of repeatedly asking the user to try the command again.
- Fixed History being reported unavailable when focus was already inside a
  ChatGPT response, link, or sidebar item but had not yet visited the prompt.
  An explicit History command can now attach the outer conversation from bounded
  prompt evidence while continuing to reject unrelated and embedded-browser
  documents.
- Fixed Control+1 through Control+0 failing or becoming unresponsive in very
  large conversations. Recent-message review now starts with a bounded 32 KiB
  conversation tail, expands only as needed to find ten complete turns, and
  never copies the full transcript.
- Fixed Control+1 through Control+0 reading convincing but incorrect messages
  from an inactive fork or side conversation. The add-on now keeps a ten-turn
  active-branch cache during its normal conversation scan, excludes hidden
  branches and content after the active prompt, and adds a submitted user turn
  immediately while Chromium refreshes. The review commands therefore avoid a
  second accessibility-tree walk on NVDA's main thread.
- Fixed the first Up or Down Arrow from the prompt in browse mode failing to arm
  reading protection. Arrow, Page Up, Page Down, Home, and End now defer
  background conversation scans even while Chromium still reports focus on the
  prompt, preserving the browse cursor and Braille reading position.
- Fixed returning to an active conversation in browse mode on an older collapsed
  activity card, several headings before the current response. When Chromium
  restores that stale activity focus and newer ChatGPT output follows it, the
  add-on now moves only NVDA's virtual caret and navigator to the newest response
  heading. The correction is limited to the first four seconds after re-entry,
  runs only while a task is active, and is cancelled by any user keystroke.
- Hardened ChatGPT window closure. As soon as the retained window disappears,
  the add-on cancels pending chat actions, History operations, popup focus,
  unarchive focus, voice confirmation, browser actions, and prompt inspection.
  After confirmed closure, delayed Chromium document events cannot silently
  recreate background monitoring; attachment resumes only when ChatGPT really
  has focus again.
- Fixed Alt+F4 closure producing no inactive sound and leaving NVDA speech and
  Braille attached to the defunct ChatGPT prompt. The add-on now remembers the
  last stable external application focus, excludes transient Windows Search,
  Start, Task View, and task-switcher objects, and uses NVDA's normal gain-focus
  event path only if Windows does not recover focus naturally. This produces one
  inactive cue and restores the previous application's focus without requiring
  an extra Alt+Tab. Window tracking now begins with ChatGPT's first foreground
  or focus event, so the same recovery works when the app is closed during
  startup before its Chromium conversation buffer finishes attaching. If the
  preceding application was also closed, the add-on activates the highest
  remaining usable application window instead of leaving NVDA attached to a
  defunct ChatGPT object.
- Replaced the redundant `appModules/codex.py` compatibility shim with NVDA's
  supported executable-alias API. `codex.exe` now loads the same application
  module as `chatgpt.exe`, and the alias is removed cleanly when the add-on
  unloads.
- Divided long README material in Input Gestures, Settings, Embedded browser
  access, Testing and building, and Braille timing into shorter sections and
  paragraphs for easier reading and translation.
- Removed NVDA+Alt+M as the default microphone-toggle gesture because it is
  NVDA's **Interact with math content** command. The microphone action remains
  available for user assignment under ChatGPT Desktop Access in Input Gestures.
- Updated the Chat History instructions to describe the Windows context menu
  introduced in 2026.2.7 instead of the older focus-transfer behavior.
- Combined **Check Codex usage statistics** and **Buy Codex usage credits** into
  one **Open usage and credits** control because both opened the same official
  account dashboard. Existing user gestures assigned to either old action keep
  working, while Input Gestures presents only the single current action.

### What to test

- Type text in the ChatGPT prompt, then remove all of it using Backspace, Delete,
  selected-text deletion, and a Braille display. Wait beyond the configured
  Working-sound delay and confirm no submission click, Processing sound,
  background click, or still-running message begins. Then submit a real prompt
  with keyboard Enter and Braille Enter and confirm feedback starts immediately.
- Open **Add files and more** with Enter and Space. Move through every item with
  Up and Down Arrow and confirm each selection is spoken once and shown in
  Braille. Close with Escape, move through another ChatGPT menu, and confirm the
  attachment labels do not repeat or leak into that menu.
- Start in Codex mode, press NVDA+grave accent, choose ChatGPT, wait for focus to
  return to the conversation, and press NVDA+Alt+O. Confirm the dialog is titled
  **ChatGPT chat history** and contains ChatGPT rather than Codex chats. Repeat
  in the opposite direction and confirm **Codex chat history** opens.
- Restart NVDA with ChatGPT already open, leave focus on a response link or
  sidebar chat without first visiting the prompt, then press NVDA+Alt+O exactly
  once. Confirm **Opening chat history** is
  followed automatically by the correct mode-specific dialog, with no
  unavailable-view or mode-detection message and no need to press the command
  again.
- In a conversation substantially longer than ten messages, use Control+1
  through Control+0 from the prompt, a response, and a link. Confirm all ten
  newest turns are read newest-first without a pause, error, focus change, or
  full-transcript traversal.
- Fork a conversation or open a side conversation, exchange at least one new
  message there, and press Control+1 and Control+2. Confirm they read the visible
  branch rather than messages retained from the other branch. Submit another
  prompt and press Control+1 immediately; confirm the newly submitted text is
  available without a pause or an NVDA watchdog/recovery entry in the log.
- Put the prompt in browse mode, then use Up Arrow, Down Arrow, Page Up, Page
  Down, Home, and End while the conversation updates. Confirm the first key and
  subsequent reading keep the browse cursor and Braille viewport in place.
- While a task is producing commentary or commands, Alt+Tab to another program
  and then return to ChatGPT in browse mode. If Chromium restores focus to an
  older collapsed activity card, confirm NVDA's browse position and Braille move
  to the newest **ChatGPT said** heading. Repeat after the task finishes and
  in focus mode; confirm the add-on does not force another move.
- Open History or a ChatGPT popup, close ChatGPT, and leave focus in another app
  for at least ten seconds. Confirm no delayed action focuses or reopens ChatGPT,
  no new **Activity monitoring active** message appears, and reopening ChatGPT
  yourself attaches monitoring normally.
- Focus a distinct control in another application, switch to ChatGPT, and close
  ChatGPT with Alt+F4. Confirm one inactive cue plays and speech and Braille
  immediately return to the previously focused control without another Alt+Tab.
  Repeat while ChatGPT is idle and while a task is active. Then use ordinary
  Alt+Tab and confirm it still produces one cue without forcing focus elsewhere.
  Finally, open ChatGPT and close it again immediately, before **Activity
  monitoring active** is announced, and confirm the same behavior.
- Close the application that was focused before ChatGPT, then close ChatGPT with
  Alt+F4. Confirm the add-on moves to another open application and restores
  speech and Braille instead of remaining silent. Confirm it does not activate
  ChatGPT, the desktop, Task View, the taskbar, or a hidden utility window.
- Start NVDA with ChatGPT open in ChatGPT mode and confirm Control+1 through
  Control+0, NVDA+Alt+V, and NVDA+grave accent work as before.
- Switch to Codex mode and repeat those commands. Confirm they appear under the
  same ChatGPT Desktop Access category and that the NVDA log contains no error
  loading the `codex` application module.
- Restart NVDA, disable and re-enable the add-on, and use **Reload plugins** from
  NVDA's Tools menu. Confirm Codex commands continue to work without duplicate
  gesture entries or app-module errors.
- In ChatGPT or Codex, confirm NVDA+Alt+M no longer toggles the microphone and
  remains available to NVDA's math-interaction command. Assign a user-chosen
  gesture to **Mute or unmute the ChatGPT microphone**, confirm it works, then
  remove the assignment and confirm it is no longer claimed.
- Open the add-on's Help document and review **Input gestures**. Confirm its
  shorter sections are easy to navigate by heading and accurately describe the
  available commands and Chat History context menu.
- Review **Settings**, **Embedded browser access**, **Testing and building**, and
  **Braille timing**. Confirm the shorter paragraphs remain clear, retain all
  prior information, and navigate naturally with NVDA's paragraph commands.
- On the Support settings page, confirm there is one **Open usage and credits**
  button and no separate Check usage or Buy credits buttons. Activate it and
  confirm the official usage dashboard opens. In Input Gestures, confirm only
  one current usage-and-credits action is listed.

## 2026.2.7

- Fixed recent-chat actions in the Chat History dialog. Shift+F10 now opens a
  genuine Windows context menu containing **Pin or unpin chat** and **Archive
  chat** instead of closing the dialog and attempting to transfer focus to a
  Chromium virtual-buffer object.
- The selected menu command now finds and invokes the matching native ChatGPT
  action directly. This prevents Enter or Space from opening the chat row when
  the user intended to archive it.
- Chat-history caches are invalidated after a native action is requested so the
  next history view can reflect the updated recent and archived lists.
- Success feedback says that the action was **requested**, rather than claiming
  the chat was already changed before ChatGPT finishes processing it.
- Reorganized the **Speech and Braille** settings page so **Active speech detail**
  appears directly beside the Full and Minimal profile choices. The choices now
  explicitly say which profile each detail level uses.
- Added a focusable **Review selected profiles** button showing the selected
  speech detail and profile together, followed by the independently selected
  Braille detail. Activating the button repeats that summary through NVDA.
- Relabeled command punctuation and maximum command length as Full-speech
  settings, and made Braille's independence from speech explicit. Existing saved
  settings and defaults are unchanged.
- A pending Pin, Unpin, or Archive retry is now tied to the conversation mode in
  which it started. It is cancelled before touching the old Chromium buffer if
  ChatGPT closes or the mode changes.

### What to test

- Open Chat History in both ChatGPT and Codex modes. In the Recent chats list,
  press Shift+F10 and confirm focus starts on **Pin or unpin chat**. Press Down
  Arrow to **Archive chat**, then Enter. Confirm the dialog closes, NVDA says
  **Archive chat requested**, and reopening history after a moment shows the
  updated lists.
- Repeat the archive test with Shift+F10 and Enter generated from a Braille
  display, including Space if the display uses it to activate menu items.
- Open the menu and press Escape. Confirm no action runs and focus returns to
  the selected item in Chat History.
- Test **Pin or unpin chat** and confirm it affects only the selected recent chat.
- Move to Archived chats, press Shift+F10, and confirm that menu contains only
  **Open archived chat**.
- Open Settings, move to **Speech and Braille**, and confirm **Active speech
  detail** is followed by the matching Full and Minimal profile choices. Switch
  between Minimal and Full and confirm the summary names the profile currently
  selected for that detail level.
- Change both speech profiles independently and confirm their selections remain
  separate. Tab to **Review selected profiles**, confirm it is reachable with
  speech and Braille, and press it to repeat the summary. Confirm the summary
  always identifies Braille detail as independent of speech, then test Apply,
  OK, Cancel, reset, export, and import.
- Start a recent-chat action and immediately close ChatGPT or change conversation
  modes. Confirm the action is cancelled instead of running against a stale chat.

## 2026.2.6

- Added the app-scoped **Open and focus the ChatGPT and Codex mode selector** action under
  NVDA's ChatGPT Desktop Access Input Gestures category. Its default shortcut is
  NVDA+grave accent, the key normally labeled backtick (`). It focuses and opens
  ChatGPT's native mode selector without requiring Control+Home and repeated Down
  Arrow presses. NVDA announces the current mode; the user chooses ChatGPT or
  Codex with Up or Down Arrow and Enter.
- Opening the selector runs through the existing off-main-thread UI Automation
  worker and works from both focus mode and browse mode. The add-on deliberately
  does not invoke a mode item automatically, avoiding unreliable Chromium menu
  activation and leaving the final choice under the user's control.
- Fixed the first test build's **not available in this view** result. ChatGPT's
  mode button exposes Expand/Collapse rather than Invoke, so the add-on now uses
  its native Expand/Collapse action and places keyboard focus in the selector.
- Repeated shortcut presses recognize an already-expanded native menu instead of
  calling Expand again and triggering a Chromium COM error.
- Fixed repeated **Activity monitoring active** announcements after ChatGPT was
  closed while its mode selector was open. Delayed Chromium popup events can no
  longer restore a detached conversation, and buffers are attached only when the
  conversation document belongs to a living, visible ChatGPT window.
- Fixed overlapping poll timers that could perform several full conversation scans
  less than 150 milliseconds apart. A poll that schedules an earlier follow-up now
  keeps that single timer instead of also creating an untracked periodic timer.
- Rate-limited repeated closed-window and unsettled-history diagnostics so debug or
  input/output logging cannot flood NVDA's main-thread log during Chromium event
  bursts. The first useful diagnostic remains available immediately.
- The shortcut can be changed or removed in Input Gestures, and the action remains
  available only while ChatGPT or Codex has focus.
- Release metadata tests now derive the add-on version from the manifest, which
  prevents a stale patch-number assertion from blocking a correctly bumped build.
- Release tags must point to a commit already present on `main`. The release guide
  now directs maintainers to let GitHub Actions create and verify the single
  correctly named package instead of uploading one manually.

### What to test

- Press NVDA+grave accent, the key normally labeled backtick (`), to run **Open
  and focus the ChatGPT and Codex mode selector**. Use it from both focus mode and
  browse mode, including while reading far down a long conversation. Confirm the
  native selector opens, NVDA announces the current mode, and Up or Down Arrow
  followed by Enter changes the mode manually.
- Change and remove the assignment in Input Gestures and confirm both customizations
  are honored.
- Open the selector while ChatGPT is slow to refresh. Confirm NVDA remains
  responsive and gives a clear failure message if the native control is unavailable.
- With focus in the prompt, open the selector and close ChatGPT with Alt+F4.
  Confirm monitoring detaches once, **Activity monitoring active** does not repeat,
  no Working feedback continues, and reopening ChatGPT attaches normally.
- While a response streams in a long conversation, confirm NVDA speech, Braille,
  and keyboard response remain smooth. In an input/output log, confirm repeated
  whole-buffer scans are never scheduled less than 150 milliseconds apart.

## 2026.2.5

### What to test

- Submit a prompt and let ChatGPT finish without exposing a Stop button or a
  status-button transition. Confirm **Prompt submitted** starts Working feedback,
  the plain **Response complete** accessibility marker ends it after the short
  settle period, and no clicks or background pulses continue after the answer.
  Repeat in both focus mode and browse mode, including a conversation containing
  several earlier completed responses.
- Start a task when the account has exhausted its allowance. Confirm the usage-limit
  pop-over stops the continuous Working sound immediately and announces **Usage
  limit reached** through speech and Braille. When exposed, confirm the message
  includes the reset time and the choices to upgrade or purchase more credits.
  Repeat with ChatGPT's percentage banner showing **0% usage remaining** and
  confirm it is detected even if Chromium does not announce the banner as an alert.
  Leave the pop-over open and confirm repeated accessibility events do not repeat
  the alert or restart Working feedback. Submit again and confirm a new rejection
  can be announced as a new event.
- Open a ChatGPT embedded-browser page and confirm NVDA says **Loading page** and
  **Loading complete** once for each navigation. Test a fast page, a slow page,
  Reload, Back, and Forward. Turn the Browser Access checkbox off and confirm
  those two add-on messages stop.
- In browse mode, use normal NVDA web commands for headings, links, form fields,
  landmarks, tables, and elements lists. Press Enter on a link and confirm its
  native action runs exactly once. In focus mode, confirm Tab, Shift+Tab, Enter,
  Space, arrow keys, and NVDA+Space behave exactly as they do in Microsoft Edge.
- Confirm the add-on adds no embedded-browser entries to NVDA's Input Gestures
  dialog and does not add descriptions to native page controls.
- Start a slow page load, move around its content with speech and Braille, and
  confirm loading feedback does not move focus, change browse/focus mode, scan the
  page, or relocate the Braille reading position. Close the browser during the
  load and confirm no delayed **Loading complete** message follows.
- Open chat history in Codex, note its Recent and Archived lists, switch to
  ChatGPT mode, and open history again. Confirm the dialog title says ChatGPT and
  no Codex title appears. Switch back and confirm the Codex list is restored.
- During that test, confirm the NVDA log records `conversation mode changed from
  chatgpt to codex` and then the reverse transition. Each subsequent history log
  entry must end with the same mode shown by ChatGPT's mode-switch control.
- After each switch, wait for the delayed history-classification and settled-cache
  log entries before opening history. ChatGPT's native Recents region deliberately
  combines ChatGPT chats and Codex tasks; confirm the add-on keeps only the correct
  type in each mode. The add-on must observe two matching post-switch snapshots.
  If history is opened too early, confirm NVDA says it is refreshing.
- Collapse Recents or leave older chats unloaded, then open add-on history. Confirm
  NVDA says it is loading recent chats, repeatedly uses only the native Recents
  **Show more** control, and opens the searchable dialog after the currently
  offered pages load. Alt+Tab away during loading and confirm expansion stops
  immediately.
- Load ChatGPT's accessible Archived chats view and confirm those titles appear
  only in ChatGPT history. Confirm Codex archived titles continue to come from
  the local Codex session index without first opening Settings.
- Let a long conversation expose its message controls below the recent-chat
  region, then open chat history. Confirm Share, Copy, Copy message, Read aloud,
  response-rating, regeneration, More actions, Sources, source results, and
  Outputs controls never appear as recent or archived chat titles in either
  ChatGPT or Codex mode.
- While a usage alert, account menu, or application-update notice is visible,
  open history and confirm Add credits, Upgrade, Update, reset details, plan
  controls, Settings, Help, and sign-out actions do not appear as chat titles.
- Start NVDA while Codex mode is already selected, then open chat history. Confirm
  the dialog is labeled Codex and contains Codex tasks rather than the much
  smaller ChatGPT list. Switch to ChatGPT without focusing the mode button (for
  example, activate it with a mouse or touch), open history again, and confirm the
  dialog follows the selector after one refresh without requiring an NVDA restart.

### Added

- Added terminal usage-limit detection for ChatGPT and Codex pop-overs. The alert
  reports an exposed reset time plus upgrade or credit options without speaking
  embedded URLs, and remains available in announcement history.
- Added automatic **Loading page** and **Loading complete** feedback for
  ChatGPT's embedded browser. Native document busy-state changes and exposed
  progress events are preferred; a bounded settle fallback handles pages that do
  not expose a final loading event.

### Changed

- Simplified Browser Access to native Chromium and NVDA behavior. Enter, Space,
  Tab, Shift+Tab, NVDA+Space, browse-mode quick navigation, and element lists are
  neither replaced nor simulated by the add-on.
- Reduced Browser Access settings to one loading-announcement checkbox. Removed
  the separate navigator, browser-help command, page actions, control-description
  overlay, and all browser-specific Input Gesture actions.
- Unchanged Codex session metadata is cached between history scans. The local
  session index is reread only after its source size or modification metadata
  changes, and unchanged classification summaries are no longer logged every
  polling interval.

### Fixed

- Continuous Working feedback now stops when Chromium exposes the plain
  **Response complete** text marker without a colon, even if it never exposed a
  Stop control or completion button event. The compatibility scan counts completed
  response markers, so markers belonging to earlier answers cannot end a newly
  submitted task.
- Exhausting the account allowance now clears pending completion and plug-in
  progress ownership, stops continuous Working clicks and background pulses, and
  prevents stale Thinking or Running labels beneath the pop-over from restarting
  them. Percentage banners showing zero remaining or 100 percent consumed are now
  terminal-limit evidence. A periodic virtual-buffer scan also detects the banner
  when Chromium omits its alert event. Repeated events from one visible notice are
  suppressed.
- Fixed a missing runtime dependency that could prevent percentage-based
  usage-limit banners from being recognized by the installed add-on.
- Corrected generated Add-on Store metadata so its changelog matches the
  packaged manifest exactly, as required by NV Access validation.
- Embedded-browser loading state now ends from a native busy-state change,
  100-percent progress, or a quiet settle timer and is canceled when focus leaves
  the browser or ChatGPT closes. Repeated events do not repeat the same start or
  completion message.
- ChatGPT and Codex chat history now use separate Recent and Archived caches.
  Changing modes closes an outdated history dialog and prevents delayed actions
  from opening a chat belonging to the previous mode.
- Active-mode detection now uses ChatGPT's exposed `Switch mode, current mode`
  control. The top-level document remains named ChatGPT while Codex is active;
  that host name can no longer overwrite the authoritative Codex mode during
  later focus events.
- ChatGPT's native Recents region is a unified list of ChatGPT chats and Codex
  tasks, regardless of which product mode is selected. The add-on now partitions
  that list with the active local Codex session index: ChatGPT history excludes
  active Codex task titles, and Codex history retains only those task titles.
- History mode verification now queries the live ChatGPT/Codex selector through
  Windows UI Automation when Chromium omits that control from NVDA's virtual
  buffer. The targeted query runs on NVDA's UI Automation worker instead of its
  main thread. Until verification completes, the add-on asks the user to retry
  history instead of opening a confidently wrong ChatGPT or Codex cache.
  Duplicate session-index records are resolved to their latest entry and archived
  task IDs are excluded. Logs report only aggregate kept and excluded counts.
- Opening add-on history now expands ChatGPT's native Recents list in ten-item
  pages before displaying the searchable dialog. It activates only the exact
  **Show more** button found inside the scanned Recents region, waits for the
  accessible item count to increase between actions, stops if ChatGPT loses focus,
  and caps one request at 20 pages to prevent an unbounded main-thread loop.
  **Show more**, **Show less**, and loading labels are excluded from chat titles.
- A newly selected mode's sidebar must now remain settled for 750 milliseconds
  and produce two matching snapshots at least 250 milliseconds apart before its
  titles can replace that mode's history cache. An early scan is discarded and
  automatically rescheduled. A candidate identical to the other mode's current
  cache is also rejected, and history refuses to open an unsettled cache.
  Privacy-safe log entries report classification, item, and overlap counts without
  recording any chat title.
- History dialog titles, empty-list notices, and errors now identify the active
  ChatGPT or Codex mode instead of always referring to Codex.
- Chat history now filters transcript and message-action controls even when
  Chromium does not expose a reliable boundary after the recent-chat region.
  The first conversation marker now ends history collection, the Recents region
  cannot restart inside message text, and alternate Main landmark metadata is
  recognized. Items such as Share, Copy, Read aloud, response ratings, Sources,
  source results, Outputs, and More actions can no longer become chat titles.
- Usage alerts and account or application controls interleaved with Chromium's
  Recents accessibility stream are no longer treated as chats. This includes
  Add credits, Upgrade, Update, reset information, plan controls, and account
  menu actions. A usage-alert marker also ends the active Recents region so later
  controls from the same pop-over cannot leak into history.

## 2026.2.4

### What to test

- Upgrade from 2026.2.3 and confirm existing settings and Input Gestures assignments
  remain unchanged.
- In Add-on Manager, open the add-on's Help document and confirm the README opens
  successfully at the top.
- Smoke-test speech, Braille, sounds, prompt submission, recent-message review,
  chat history, voice controls, and completion in both focus and browse modes;
  behavior should match 2026.2.3.
- Confirm the archive contains exactly 63 ordered entries and 51 tiered WAV files,
  including `readme.md`, `changelog.md`, and `LICENSE.txt`, with no root-level
  legacy sounds, translation template, cache files, or duplicate entries.
- Confirm GitHub publishes `chatGPTDesktopAccess-2026.2.4.nvda-addon` from the
  audited CI build and that the downloaded release asset has the same SHA-256
  checksum as the validated package.

### Fixed

- Corrected release packaging so the documentation, complete changelog, and GPL
  license are installed with the add-on.
- Excluded thirteen obsolete un-tiered sound files and the developer gettext
  template from release packages. Only the current Soft, Normal, and Loud sound
  sets are installed.
- Standardized the public release filename as
  `chatGPTDesktopAccess-2026.2.4.nvda-addon` while retaining the internal
  `codexStatusAnnouncer` identity for safe upgrades.
- Added a tag-triggered GitHub Actions release workflow that builds and audits
  the package, verifies reproducibility, publishes only that validated artifact,
  downloads it again, and confirms its checksum and archive layout.
- Kept source syntax audits scoped to project files so generated output folders
  and temporary validation dependencies cannot change release-audit results.

### Compatibility

- Runtime accessibility behavior is unchanged from 2026.2.3. This is a packaging
  and release-process correction only.

## 2026.2.3

### What to test

- Upgrade from 2026.2.2 and confirm NVDA Add-on Manager displays **ChatGPT
  Desktop Access for NVDA** while preserving all settings and Input Gestures
  assignments.
- Confirm NVDA Settings, Input Gestures, current release notes, diagnostics,
  settings import/export, and support-report dialogs use the new public name.
- Confirm documentation, package names, and release links point to the renamed
  `chatgpt-desktop-access` repository.
- In ChatGPT and Codex modes, smoke-test speech, Braille, sounds, prompt
  submission, recent-message review, chat history/actions, dialogs, voice
  controls, and completion in both focus and browse modes.
- Build the package twice and confirm identical SHA-256 checksums, a valid
  archive layout, current translations, and complete Add-on Store metadata.

### Changed

- Renamed the public product from **Codex Access Toolkit for NVDA** to
  **ChatGPT Desktop Access for NVDA** to reflect its support for both ChatGPT
  and Codex experiences.
- Moved public project and release links to the renamed
  `jcoffin1/chatgpt-desktop-access` GitHub repository.
- Renamed release packages, settings exports, support reports, CI artifacts,
  and the translation template to use the new product name.
- Added the required empty translations collection to generated NVDA Add-on
  Store metadata.
- Expanded the GitHub issue chooser with structured bug, feature,
  accessibility, compatibility, and documentation/support forms, plus direct
  links to security guidance, setup documentation, and published releases.

### Compatibility

- The internal add-on ID, Python module names, and configuration section remain
  `codexStatusAnnouncer`, so upgrades retain settings, gesture assignments, and
  compatibility with existing installations.
- This patch changes branding and release packaging only. Runtime accessibility
  behavior is unchanged from 2026.2.2.

## 2026.2.2

### What to test

- In Codex mode, submit a prompt and confirm prompt submission, Thinking, commentary,
  commands, file work, continuous Working feedback, completion, Braille, and sounds
  behave as configured in both NVDA focus mode and browse mode.
- Submit a non-empty prompt with physical Enter, numpad Enter, and Braille dot-8.
  Confirm each message is sent exactly once, the prompt clears, prompt-submission
  feedback starts, and NVDA does not play its log-error sound. Confirm Shift+Enter
  still inserts a new line without submitting.
- In both focus mode and browse mode, press NVDA+Alt+V with voice mode stopped and
  active. Confirm it starts and ends voice mode respectively. Press NVDA+Alt+M while
  voice mode is active and confirm it mutes and unmutes only the microphone, never
  the nearby speaker control. Confirm each action first reports the requested change
  and then reports success only after the native button state changes. Reassign or
  remove the actions in Input Gestures and confirm the custom assignments are honored.
- Reassign a recent-message or voice command to a gesture used by another NVDA add-on.
  Confirm it activates the Toolkit command in ChatGPT, then move outside ChatGPT and
  confirm the other add-on receives the same gesture without Toolkit interference.
- Upgrade over a build where a recent-message or voice command was customized or its
  default was removed. Confirm that assignment or removal is retained after restart.
- Switch to ChatGPT mode and repeat the same test. Confirm immediate activity events
  are announced without waiting for the fallback buffer poll.
- Open the usage page, allow usage to reset if applicable, and return to either mode.
  Confirm monitoring automatically reattaches without restarting NVDA.
- Open an embedded browser page from either mode. Confirm its page content is not
  misclassified as task commentary and the separate browser announcements still work.
- Open permission and other pop-up dialogs in both modes. Confirm focus enters each
  dialog and urgent information remains available in speech and Braille.
- Restart NVDA while ChatGPT is already open. Without first entering the prompt,
  invoke chat history from an older message, the top of the browse-mode document,
  and a sidebar chat. Confirm the Recent and Archived lists open each time.
- In a large active conversation, read several paragraphs with browse-mode keys and
  Braille scrolling commands while new response text arrives. Confirm the browse
  cursor and Braille viewport remain at the selected passage.
- Pause navigation and let the task finish. Confirm monitoring resumes, completion is
  spoken or sounded normally, and **Response complete** does not replace the Braille
  passage being read. Confirm permission dialogs still move focus and remain available.
- Let a task finish while ChatGPT is in the background. Confirm Working feedback stops
  within about five seconds after the final response. Then start another task, close the
  ChatGPT window, and confirm all retained activity stops without waiting for its helper
  processes to exit. Alt+Tab away without closing it and confirm monitoring continues.
- Install on stable NVDA 2026.2 and confirm the package is accepted as compatible.
- Run `build.ps1` and confirm all automated, translation, syntax, archive, sound,
  gesture, and reproducibility checks pass.

### Added

- Added configurable voice-mode controls with NVDA+Alt+V as the default for starting
  or ending voice mode and NVDA+Alt+M as the default for muting or unmuting the
  microphone. The actions locate and activate ChatGPT's exact native buttons in both
  focus and browse modes, report the requested transition in speech and Braille, and
  never match the separate speaker-mute control. Voice and recent-message commands
  now live on ChatGPT's application module, so default and reassigned bindings are
  claimed only in ChatGPT and cannot block another add-on elsewhere.

### Fixed

- Preserved existing Input Gestures customizations and default-command removals when
  migrating recent-message and voice commands from the global plug-in to ChatGPT's
  application module. Unrelated global mappings are never moved.
- Changed the packaged update channel from development to the stable default so the
  manifest agrees with the stable Add-on Store metadata and NVDA 2026.2 release target.
- Removed global key emulation from the twelve application-specific commands. NVDA's
  user gesture map can now scope customized bindings by the ChatGPT/Codex app-module
  class instead of bypassing a global plug-in focus check.
- Voice controls now announce an in-progress transition first and report success only
  after the corresponding native Start, Stop, Mute, or Unmute state is found. A failed
  or delayed interface action no longer produces a false success announcement.
- Added first-class support for both ChatGPT and Codex conversation document names.
  Immediate status and commentary events in ChatGPT mode no longer depend on slower
  whole-buffer polling.
- Mode changes now clear the previous task's busy state, preventing a continuous
  Working sound from carrying across a usage page or ChatGPT/Codex mode transition.
- Current-activity reports name ChatGPT while ChatGPT mode is active and retain Codex
  wording in Codex mode. Shared monitoring and new-chat messages are mode neutral.
- Required both `chatgpt` and `codex` NVDA app-module hosts in migrated, imported,
  and newly saved settings so a host-process change cannot silently disable support.
- Expanded conversation recognition to the **Message ChatGPT** and **Send a message**
  prompt variants used outside Codex mode.
- Kept nested embedded-browser documents excluded from conversation activity handling.
- Restored chat-history access when focus is on a top-level or browse-mode ChatGPT
  object. Buffer validation now happens while walking NVDA's focus ancestors instead
  of rejecting the request before the conversation document is reached.
- Embedded-browser recovery skips its nested web buffer and can retain or locate the
  outer ChatGPT/Codex conversation buffer safely.
- Preserved browse-mode reading when Chromium rebuilds the live region with a new
  tree-interceptor object. Reading protection now follows the retained conversation
  buffer instead of trusting a transient event object's identity.
- Suppressed the exact **Response complete** live-region variant, which previously
  bypassed the colon-based check and displaced the Braille line at task completion.
- Deferred whole-conversation status scans for three seconds after keyboard or Braille
  navigation. Direct activity and permission events continue immediately while large
  virtual-buffer reads wait until the user pauses.
- Replaced the full-transcript read performed during a Chromium buffer refresh with a
  bounded 8,192-character tail read, preventing large chats from blocking NVDA's main
  thread merely to determine whether a new blank chat opened.
- Suppressed non-urgent completion flash messages in Braille while browse-mode reading
  protection is active; speech and sounds continue, and urgent prompts are never hidden.
- Restored the minimum NVDA compatibility declaration to NVDA 2023.1 instead of
  incorrectly requiring a newer NVDA release, while keeping stable NVDA 2026.2 as
  the tested ceiling for this release line.
- Reduced the tentative final-response settling period from 30 seconds to five seconds.
  A missing Stop control and quiet activity scan are still required, and later work
  cancels the candidate. Working pulses and continuous sounds pause immediately during
  that confirmation, so completed tasks no longer produce false progress feedback.
- Tracked the outer ChatGPT window independently of its background helper processes.
  Closing or hiding that window for two seconds now discards its stale virtual buffer and
  clears speech, Braille, pulses, and continuous Working sounds; Alt+Tab does not.
- Preferred NVDA's current `braille.input` API and retained the legacy `brailleInput`
  import only as a fallback, removing the deprecation warning found in the NVDA log.
- Stopped NVDA's generic multiline-edit Enter handler from inspecting ChatGPT's
  already-replaced prompt object after submission. Physical Enter, numpad Enter, and
  Braille dot-8 now remain native while avoiding the misleading log-error sound and
  IA2 `COMError`; Shift+Enter continues to create a line break.

## 2026.2.1

### What to test

- In browse mode, place the browse cursor on ChatGPT's empty **Do anything** prompt
  and press Braille dot-8 once. Confirm NVDA enters focus mode without a Prompt
  submitted sound, Working sound, or elapsed-time announcement.
- With the empty prompt already in focus mode, press physical Enter or Braille dot-8.
  Confirm the Toolkit remains idle because no prompt was submitted.
- Type a prompt rapidly with the physical keyboard and submit it. Repeat with a
  Braille display, including contracted Braille. Confirm the Prompt submitted sound
  occurs immediately and the first elapsed announcement starts from the real submit.
- Submit a second prompt after the first task completes. Confirm task feedback starts
  once, elapsed time resets to zero, and no keystroke or Braille chord is consumed.
- Run `build.ps1` and confirm all automated, translation, syntax, archive, sound,
  gesture, and reproducibility checks pass.

### Fixed

- Added development-channel compatibility for NVDA alpha-57626,71bae80b
  (2026.3.0.57626) and later.
- Stopped Braille dot-8 from falsely starting task feedback when it is used only to
  activate ChatGPT's empty prompt from NVDA browse mode. Prompt-submission feedback
  now requires focus mode plus evidence of existing or just-entered prompt text.
- Stopped browse-mode Braille quick-navigation chords from being recorded as prompt
  typing. This prevents a later empty Enter from inheriting false typing evidence.
- Added regression coverage for browse-mode activation, empty focus-mode Enter, rapid
  Braille typing, and immediate real submission without claiming the user's gesture.

## 2026.2.0

### What to test

- Install the package manually and restart NVDA. Confirm Add-on Store manager,
  Settings, diagnostics, and release notes all report version 2026.2.0.
- Open **NVDA Settings > Codex Access Toolkit** and confirm the panel contains
  eight clearly named pages: General, Speech and Braille, Sounds, Activity
  Output, Wording and Preview, Browser Access, Advanced, and Support. Use
  Control+Tab and Shift+Control+Tab to move through every page.
- Test ChatGPT in both focus mode and browse mode. Confirm Thinking, commentary,
  commands, searches, file operations, builds, tools, permissions, and completion
  use the selected speech, Braille, and sound routes without duplicate output.
- Start a long task, leave ChatGPT, and return. Confirm background status remains
  available, the Working sound begins only after a prompt is submitted, continues
  only while the task is active, and stops promptly on completion or cancellation.
- Type long prompts with a physical keyboard and a Braille display. Confirm input
  is responsive, contracted Braille retains the first cell of each new word, Enter
  submits without leaving stale text, and Shift+Enter still inserts a new line.
- In a large streaming conversation, read an older response with speech or Braille.
  Confirm ordinary response updates do not displace the browse cursor, speech, or
  Braille line. Permission dialogs and urgent alerts must still interrupt normally.
- Press Control+1 through Control+0 in ChatGPT and confirm the ten most recent
  messages are read in order. Confirm these keys pass through outside ChatGPT and
  remain independently configurable in NVDA's Input Gestures dialog.
- Open searchable chat history. Confirm Recent and Archived chats are separate,
  chats open correctly, and Shift+F10 places focus on an available Pin, Archive,
  Unarchive, or Open action without freezing NVDA.
- Trigger permission, plug-in installation, and other ChatGPT pop-up dialogs.
  Confirm focus moves to each dialog, its essential text is announced, and exposed
  installation progress is reported without taking focus from an unrelated app.
- Open ChatGPT's embedded browser or web preview. Confirm entry, exit, useful page
  titles, and exposed ten-percent loading steps are announced once. Confirm native
  roles, states, actions, Tab behavior, NVDA+Space, and quick navigation remain intact.
- Export settings, preview each speech or sound action independently, edit custom
  announcement wording, and save a sanitized support report. Reopen Settings and
  confirm values persist without exposing chat text, commands, paths, or secrets.
- Run `build.ps1` and confirm unit tests, translation-template validation, Python
  syntax, archive layout, sound assets, gestures, and reproducible-build checks pass.

### Added

- Added structured Full and Minimal speech profiles. Full remains the default and
  can include exact commentary, commands, file changes, builds, and tool activity;
  Minimal gives concise but meaningful activity and completion summaries.
- Added independent speech, sound, Braille, and disabled output routing for every
  activity category, with editable announcement wording and individual previews.
- Added click earcons and musical tones for prompt submission, thinking, commands,
  searches, file work, builds, tools, permissions, completion, attachment, and
  working state, including Soft, Normal, and Loud click levels.
- Added a continuous, non-interfering Working sound that starts when a prompt is
  submitted, continues during active background work, and stops when work ends.
- Added active, inactive, and ChatGPT-closed feedback while preventing navigation
  and task switching from falsely starting the Working sound.
- Added searchable Recent and Archived chat lists with keyboard navigation, bounded
  loading, open and unarchive actions, and native chat actions through Shift+F10.
- Added ten independently configurable recent-message actions. Control+1 through
  Control+0 are the defaults and can be changed in NVDA's Input Gestures dialog.
- Added focused handling for permission requests, ChatGPT pop-ups, new chats, and
  plug-in installation progress.
- Added optional background commentary and autonomous-activity feedback plus an
  assignable action to hear the latest complete Codex progress without switching apps.
- Added accessible access to Add files and more, model selection, and permission
  controls while preserving their native behavior.
- Added eight keyboard-accessible Settings pages, per-page access keys, accessible
  help and release-note documents, settings import/export, and sanitized diagnostics.
- Added conservative embedded-browser descriptions, focus transitions, page-title
  announcements, loading progress, and a dedicated help document.
- Added deterministic translation-template generation, compiled-catalog packaging,
  automated accessibility fixtures, GitHub validation, issue forms, contribution
  guidance, security guidance, and Add-on Store metadata tooling.

### Changed

- Aligned the add-on version, package name, runtime constant, release notes, build
  tooling, tests, documentation, issue forms, translation metadata, and declared
  stable NVDA compatibility with NVDA 2026.2. Future add-on-only patches use
  2026.2.1, 2026.2.2, and so on until a newer stable NVDA release.
- Renamed the add-on to Codex Access Toolkit for NVDA to reflect its broader speech,
  Braille, sound, chat navigation, dialog, browser, and control-access features.
- Organized Settings into General, Speech and Braille, Sounds, Activity Output,
  Wording and Preview, Browser Access, Advanced, and Support pages.
- Replaced a single verbosity switch with configurable Full and Minimal profiles
  while retaining verbose developer-oriented output as the default.
- Replaced the combined preview with separate preview actions so speech and every
  sound can be evaluated independently.
- Moved all keyboard assignments into NVDA's Input Gestures dialog; no new fixed
  shortcuts are introduced when a configurable action is sufficient.
- Routed progress, duplicates, privacy redaction, speech, sounds, and Braille through
  shared category and priority rules for consistent foreground and background output.
- Preserved the Codex conversation virtual buffer while focus is inside a recognized
  embedded browser, allowing task monitoring to continue in focus and browse modes.
- Normalized packaged text line endings so identical source produces a reproducible
  add-on archive across LF and CRLF checkouts.

### Fixed

- Stabilized speech, Braille, and the browse cursor in large conversations. Ordinary
  streamed response updates no longer replace an older passage being read in browse
  mode when reading protection is enabled. Focus-mode output, permissions, dialogs,
  urgent alerts, and completion state continue normally.
- Replaced unconditional whole-document polling with event-marked inspections and a
  lightweight housekeeping timer. Idle ChatGPT monitoring is event-driven, and the
  compatibility fallback is bounded to protect NVDA's main thread.
- Suspended fallback scans and prompt-local text inspection during active typing so
  Braille input does not compete with Chromium virtual-buffer traversal.
- Protected contracted-Braille composition from Chromium's delayed caret event for
  the preceding word, preventing missing first cells and scrambled input without
  consuming or replacing NVDA's Braille gestures.
- Removed expensive browser-ancestry walks from ordinary prompt edits, toolbar
  controls, status buttons, and other objects that cannot be embedded-browser controls.
- Restored immediate Prompt submitted sounds for physical Enter and standalone
  Braille dot-8 Enter without claiming or replacing the input gesture.
- Corrected click-volume scaling so Soft, Normal, and Loud produce distinct levels,
  and made Working clicks slower, clearer, and non-overlapping with event earcons.
- Corrected musical-tone mode so active work has an audible continuing indicator.
- Stopped stale Working and file-operation states after completion, cancellation,
  navigation, a closed ChatGPT window, or a transient Chromium object replacement.
- Replaced vague elapsed output with category-aware durations such as file operations
  still running for one minute and twenty-five seconds.
- Fixed chat-history opening, archived-chat loading, unarchive focus, and Shift+F10
  chat actions while keeping retries bounded and off blocking NVDA paths.
- Prevented chat switches, empty conversations, browser pages, and unrelated busy
  controls from being mistaken for newly submitted tasks.
- Kept focus on permission dialogs and other ChatGPT pop-ups and placed focus on the
  appropriate action after unarchiving a chat.
- Prevented routine Toolkit Braille flash messages from taking the reading position;
  urgent messages remain available and respect NVDA's Braille message timeout.
- Isolated every NVDA event hook, speech call, Braille call, tone, click, dialog,
  history load, and completion classifier so one failure cannot break monitoring or
  stop the rest of NVDA's event chain.
- Restored the completion-sound classifier and failure-safe completion beep, preventing
  completion events from detaching monitoring or flooding the NVDA log.
- Prevented false embedded-browser entry from ChatGPT's native Browser menu and
  prevented unrelated downloads from being reported as browser loading progress.

### Earlier development history

Earlier development established focus- and browse-mode virtual-buffer discovery,
speech and Braille status output, configurable verbosity, activity sounds, editable
announcements, chat history and actions, recent-message reading, dialog focus,
background monitoring, privacy redaction, diagnostics, and extensive NVDA main-thread
and Braille-input safeguards. Exact legacy version labels remain available in Git
history; the active source and packaged documentation now use the current release line.
