# Manual NVDA integration test checklist

Complete this checklist with the packaged add-on before publishing a release.

## Recent-message review and conversation focus

- Open main and parallel conversations. Keep keyboard focus in one composer,
  navigate in the other with browse mode, and use Control+1 through Control+0.
  Check the selected conversation and message order without activating the
  latest-response heading. In focus mode, verify that its composer takes precedence.
- Scroll up in a long chat with an unsent draft. Review must load the end of that
  conversation without sending or changing the draft. Repeat shortcuts quickly,
  and change chats/panes/apps while content is loading to check cancellation.
- Leave the mascot visible. A background Electron surface must not replace
  NVDA's focus. Activate a real second window and open an owned approval or native
  file dialog to confirm that legitimate focus and speech remain accessible.
- Test project and Recents navigation in normal, full and Activity views, with
  the sidebar open/closed and sections expanded/collapsed, using French and English.

## Installation and startup

- Install the package and restart NVDA when prompted.
- Confirm the installed version and ensure the NVDA log has no add-on traceback.
- Confirm the one-time What's New document opens at the top and contains only
  the concise current-version summary. Confirm complete history remains available
  from the Settings panel.

## Settings organization

- Open ChatGPT Desktop Access Settings and confirm General, Speech and Braille,
  Sounds, Activity Output, Wording and Preview, Browser Access, Advanced, and
  Support are exposed as eight notebook pages.
- Use Control+Tab and Shift+Control+Tab to move through every page. Confirm Tab
  and Shift+Tab reach every control without leaving content clipped or hidden.
- Use the displayed Alt access keys on each page. Confirm each access key reaches a
  different control on that page and none activates a control from a hidden page.
- Confirm General contains the speech and Braille output switches, Speech and
  Braille contains active speech detail and both saved speech profiles, background
  timing is under Activity Output, technical compatibility controls are under
  Advanced, and account, documentation, report, import, and export actions are
  under Support.
- On Speech and Braille, switch Active speech detail between Minimal and Full.
  Confirm each choice names the profile it uses. Tab to Review selected profiles,
  confirm the button is reachable with speech and Braille, and press it to repeat
  the selected speech profile and independent Braille detail. Change Full,
  Minimal, and Braille choices separately and confirm the button follows the
  correct selection without changing the others.
- On Activity Output, change multiple categories, switch between them, Apply,
  reopen Settings, and confirm enabled state and routing remain independent. As
  each value changes, confirm the category selector immediately includes both its
  enabled state and route without requiring extra tabbing.
- Import a settings file while a non-first activity category is selected and
  confirm every page and the selected category refresh without stale values.
- Export settings and confirm the Save dialog suggests
  `chatgpt-desktop-access-settings.json` without forcing that name or location.

## Focus and browse modes

- Assign the Open searchable and arrow-navigable ChatGPT or Codex chat history
  action in Input Gestures. Invoke it from focus mode and browse mode, search by title,
  Tab from Recent chats to Archived chats, browse both lists with arrows, open
  with Enter, and verify Shift+F10 opens a native Windows context menu while the
  history dialog remains open. Confirm recent chats offer Pin or unpin chat and
  Archive chat, and archived chats offer only Open archived chat. Cancel with
  Escape and confirm no action runs.
- Restart NVDA while ChatGPT is already open, leave focus on a response link or
  sidebar chat without first visiting the prompt, and press NVDA+Alt+O exactly
  once. Confirm the correct ChatGPT or Codex History dialog opens automatically
  after the brief **Opening chat history** message. Confirm NVDA never reports
  that History is unavailable and never asks you to press the command again while
  it detects the mode or refreshes the cache.
- Populate Codex history, switch to ChatGPT mode, and open history again. Confirm
  the title and both lists identify ChatGPT and contain no Codex titles. Switch
  back to Codex and confirm its own cached lists return. Confirm a history dialog
  open during a mode change closes without performing its selected action.
- Confirm Codex archived titles load from the local session index without first
  visiting Settings. In ChatGPT mode, confirm archived titles remain separate
  and appear only after ChatGPT exposes its accessible Archived chats view.
- In ChatGPT focus and browse modes, confirm Control+1 reads the newest real
  conversation message and Control+2 through Control+0 read progressively older
  turns. Confirm timestamps, response controls, progress labels, hidden response
  copies, and the prompt are omitted. Confirm the keys pass through elsewhere.
- Repeat Control+1 through Control+0 in a conversation substantially longer than
  ten messages while focus is on the prompt, a response, and a link. Confirm all
  ten positions remain immediate, do not report an unavailable message, do not
  change focus, and do not stall NVDA while copying the full transcript.
- Fork a conversation or open a side conversation and exchange a new message.
  Confirm Control+1 and Control+2 read turns from the currently visible branch,
  not a hidden or inactive branch. Submit another prompt and press Control+1
  immediately; confirm the submitted text is already available. Check the NVDA
  log and confirm these shortcuts produce no watchdog freeze or recovery entry.
- In Input Gestures, confirm all ten message positions are separately named.
  Reassign one to Alt+1, remove a different default, restart NVDA, and confirm
  the custom assignments persist without changing the remaining positions.
- Reach Add files and more, the model control, and Change permissions using ordinary
  Tab or browse-mode navigation. Confirm each recognized control has a concise,
  useful description and retains its native name, role, collapsed or expanded state,
  and action. Open with Enter or Space, navigate with arrows, choose with Enter, and
  close with Escape. Confirm no actions for these controls appear in Input Gestures.
- While Add files and more is open, confirm every selected item is spoken once and
  appears in Braille. Close it with Escape and open the model or permissions menu;
  confirm no attachment item repeats in those menus.
- In both a ChatGPT chat and a Codex task, start in browse mode and activate Add
  files and more with keyboard Enter, Space, and Braille Enter. Confirm the **Add
  files and more** list opens with every section's options, title first. Choose
  **Files and folders** and confirm **Select files** opens. Repeat with a plugin
  and with Plan mode, use the filter box once, and confirm Escape closes both
  the list and ChatGPT's popup. Confirm no Working sound or submission starts.
- Repeat the Add files and more check in a new ChatGPT chat with **Chat**
  selected, where the message field is named **Ask ChatGPT**: choose Add photos &
  files, then Web search, and confirm the file picker opens and the Web search
  chip appears.
- On a new ChatGPT chat, press NVDA+Alt+W once and confirm the selected setting
  is spoken; press it twice quickly and confirm it switches between Chat and
  Work. Inside an existing conversation and in Codex, confirm it says the switch
  is not shown.
- In the message field in focus mode, type "/" and confirm the number of
  suggestions and the highlighted one are spoken; press Down Arrow and confirm
  each newly highlighted suggestion is spoken with its position; type letters and
  confirm the new first suggestion is spoken; press Escape. Repeat with "@".
  Turn off the General setting for suggestion menus and confirm nothing is
  added to NVDA's own speech. With the Slash Menus add-on installed, confirm
  only that add-on speaks.
- After a ChatGPT update, confirm the NVDA log has one "compatibility check for
  ChatGPT" line naming the new version, and that the support report's ChatGPT
  compatibility check line matches it.
- Attach a file and add Web search, press NVDA+Alt+A, and confirm both are
  named; remove them and confirm "Nothing is attached to the message". Repeat
  once with Work selected.
- With sanitized diagnostic logging on, open Add files and more, save a support
  report, and confirm its attachment capture lists menu controls but no chat text.
  Confirm the report's ChatGPT app line names the installed package version.
- Type a draft in the prompt and delete every character without pressing Enter.
  Wait longer than the Working-sound delay and confirm no Processing sound, working
  click, or still-running announcement begins. Repeat with Braille input, then submit
  real prompts with keyboard Enter and Braille Enter and confirm immediate feedback.
- Move focus into ChatGPT and confirm one active click; move to another app and
  confirm one inactive click. Moving inside ChatGPT must not repeat either cue.
- Focus a distinct control in another application, switch to ChatGPT, and close
  ChatGPT with Alt+F4. Confirm the inactive click plays once and NVDA speech and
  Braille immediately return to the previous control without another Alt+Tab.
  Repeat while ChatGPT is idle and while a task is active. Then use ordinary
  Alt+Tab and confirm it still plays one inactive cue without forcing focus.
  Finally, open ChatGPT and close it immediately before **Activity monitoring
  active** is announced; confirm the same recovery occurs.
- Close the application that was focused immediately before ChatGPT, then close
  ChatGPT with Alt+F4. Confirm another open application receives focus with
  working speech and Braille. Confirm the fallback never activates ChatGPT, the
  desktop, Task View, the taskbar, or a hidden utility window.
- Before closing ChatGPT, open History or a ChatGPT popup so delayed actions are
  pending. Close the app and leave focus in another program for at least ten
  seconds. Confirm ChatGPT does not receive focus or reopen, monitoring does not
  reactivate from a stale document event, and no new **Activity monitoring
  active** message is announced. Open ChatGPT yourself and confirm monitoring
  attaches normally.
- In focus mode at the Codex prompt, run a task containing commentary, a shell
  command, a file edit, and tests. Confirm each update is announced once.
- Switch to browse mode during a second task and confirm announcements continue.
- Switch repeatedly between modes and confirm monitoring does not detach.
- In a large conversation, read an older response in browse mode with Say All, arrow
  navigation, and Braille panning while a new response streams. With **Keep conversation
  reading stable** enabled, confirm streamed `Response:` updates do not interrupt speech,
  replace the Braille line, or relocate the browse cursor. Disable the option and confirm
  native live-region behavior returns. Focus the prompt in focus mode and confirm new
  response output still works normally.
- In that same large conversation, put the prompt in browse mode and begin with
  Up or Down Arrow while Chromium still reports focus on the editor. Continue
  with arrows, Page Up, Page Down, Home, and End. Confirm the first navigation
  key arms reading protection and background scans never return the browse
  cursor or Braille viewport to the prompt.
- During an active task, leave ChatGPT and return with Alt+Tab in browse mode.
  When Chromium restores focus to an older collapsed activity card, confirm the
  browse cursor, object navigator, and Braille begin at the newest **ChatGPT
  said** heading instead of several headings above it. Confirm no correction
  occurs after completion, in focus mode, or after pressing a navigation key.
- Repeat while a permission dialog opens. Confirm the dialog receives focus and its
  urgent speech and Braille output are never suppressed by reading protection.

## Embedded browser access

- Open ChatGPT's Browser submenu and arrow through Open Browser Tab, Focus Browser
  Address Bar, and Reload Browser Page. Confirm the menu keeps its native names,
  roles, states, focus, and keyboard behavior.
- Confirm NVDA's Input Gestures category contains no separate embedded-browser
  navigator, summary, snapshot, external-browser, return-to-prompt, or help
  commands.
- Open ChatGPT's embedded browser or web preview and confirm NVDA says **Loading
  page** followed by **Loading complete**. Test a fast page, a slow page, Back,
  Forward, Reload, and two pages with the same title. Confirm each navigation has
  only one start and one completion message.
- Disable **Announce when embedded browser pages start and finish loading** on
  the Browser Access settings page. Navigate again and confirm only the two add-on
  loading messages stop. Re-enable it for the remaining tests.
- Use the page in both focus mode and browse mode. Confirm Tab and Shift+Tab move
  among controls; Enter and Space activate the current native link or control
  exactly once; NVDA+Space switches modes; and H, K, F, D, T, Shift variants, and
  NVDA+F7 retain their normal browser behavior. Confirm no add-on description is
  appended to native controls.
- During a slow navigation, move around the page with speech and Braille. Confirm
  loading feedback never changes focus, mode, the review cursor, or the Braille
  reading position. Close the embedded browser before completion and confirm no
  delayed **Loading complete** message follows.
- Trigger an unrelated download or progress bar elsewhere in ChatGPT and confirm
  it is not called browser loading.
- Start a Codex task, move into the embedded browser while it runs, and confirm
  activity speech, sounds, and urgent Braille continue without a task reset. Then
  return to the conversation and confirm the original virtual buffer is still
  monitored.

## Output channels

- With an account at its usage limit, submit a prompt and confirm the limit
  pop-over produces one urgent speech announcement, one Braille flash, and the
  configured attention sound. Confirm it includes the exposed reset time, omits
  raw URLs, and stops every Working click and background pulse immediately.
- Keep the pop-over open for at least two polling cycles. Confirm stale activity
  beneath it cannot restart Working feedback. Submit another prompt and confirm a
  newly returned limit notice can be announced again.
- Test Essential, Balanced, and Informative Minimal speech. Then test Standard,
  Developer, and Raw Full speech. Confirm filtered speech does not disable
  independently configured braille or sounds.
- Turn NVDA speech mode off and confirm configured progress sounds still play.
- Re-enable speech and confirm speech and sounds follow their selected routes.
- With a braille display connected, confirm flash messages appear independently
  of speech and work in both focus and browse modes.

## Compatibility and support

- Run the assignable compatibility self-test and copy sanitized diagnostics.
- Save a sanitized support report from Support and through an
  assigned gesture. Confirm it includes add-on and NVDA versions, settings,
  monitoring state, and error status but excludes chat and command text.
- Test a built-in synthesizer and at least one third-party synthesizer.
- Test speech mode Off, a connected braille display, sleep mode, multiple Codex
  windows, and closing ChatGPT while monitoring is active.
- Export and import settings, then test speech-profile reset with Cancel and OK.
- Test command punctuation, truncation, and Copy latest full Codex progress.

## Sounds and custom announcements

- Preview each selected sound and speech action separately.
- Test Clicks and Tones plus Soft, Normal, and Loud click levels.
- Confirm the continuous Working sound repeats while busy, pauses around other
  action sounds, uses the selected click volume in Clicks mode, and uses the
  dedicated Working pattern in Tones mode.
- Type a prompt and press Enter, then repeat using the Send button. Confirm the
  Prompt submitted click starts immediately in both cases without a keyboard
  gesture, followed by Working clicks after the configured start delay.
- Repeat submission with the physical Enter key and a Braille display's standalone
  dot-8 Enter chord. Confirm each produces exactly one immediate submission click,
  Shift+Enter still inserts a new line, and no gesture is consumed or sent twice.
- Disable the distinct submission click and confirm an immediate Working click is
  used instead. Test minimum and maximum repeating-click start delays.
- Customize one announcement with `{message}`, save, and confirm live output.
- Restore the customized announcement and confirm built-in wording returns.

## Task state and attention

- Run a task longer than two background intervals and confirm progress pulses
  occur only while the task is active.
- Include a quiet processing interval longer than 30 seconds and confirm Working
  clicks continue until an explicit completion or cancellation signal.
- Complete and cancel tasks, confirming pulses stop promptly.
- Confirm the continuous Working sound also stops immediately when each task ends.
- Confirm a completed response stops Working clicks even when the NVDA log shows
  `Response complete` only as braille output and no live-region plug-in event.
- Confirm commentary followed by a delayed tool start (at least 11 seconds) does
  not stop Working clicks during the `Response complete` settling window.
- Trigger a permission or user-input request and confirm its urgent announcement.
- Confirm a final commentary update does not restart background pulses.
- Start work in two different Codex tasks, switch between them, and confirm no
  history, prompt state, or continuous-click state leaks between documents.
- Switch among idle tasks with different conversation lengths before typing and
  confirm no Prompt submitted or Working clicks play.
- Give a recent chat a title that starts like progress, such as "Using VoiceOver
  Rotor" or "Ran the numbers". Restart NVDA with ChatGPT open on a new chat,
  scroll the sidebar, and Alt+Tab back to that chat; confirm no Working sound or
  activity announcement begins.
- Confirm a tentative Response complete marker does not stop Working clicks if
  another command begins during the 30-second settling period.
- Generate repeated identical accessibility events and confirm each announcement
  is emitted once while later legitimate repeats remain available.

## Performance and shutdown

- Run a long task in a lengthy conversation and check that NVDA remains responsive.
- Type a multi-sentence prompt from a Braille display without pausing. Confirm character
  entry and Braille feedback remain responsive and no full-buffer diagnostic scan is
  logged until at least 1.25 seconds after typing stops.
- Repeat with contracted Braille and pause before pressing Space. Confirm no scan occurs
  while the display shows the uncommitted dot composition, even before Chromium emits a
  prompt text-change event. Confirm routing and scroll gestures still work normally.
- With contracted Braille enabled, repeatedly type `we need using Braille from the Sense`
  at normal speed without pausing between words. Confirm the first cell of the word after
  each Space is retained: `need` must not become `eed`, and `using` must not become `sing`.
  Open the add-on diagnostic report and confirm **Preserved Braille compositions**
  increases when ChatGPT delivers the delayed caret event. Repeat the phrase in Outlook
  and confirm the add-on does not change its Braille input or caret behavior there.
- Type `The developers need to see the error` at normal Braille Sense speed and confirm
  the result is exact. In an NVDA I/O log, compare each `Input: br(hims.BrailleSense)`
  timestamp with the following untranslated `Braille regions text` update. Confirm the
  enabled add-on no longer adds the repeated roughly 160–180 millisecond queue seen in
  the regression log and remains close to the disabled-add-on baseline.
- With ChatGPT idle, move to Outlook for at least one minute. Confirm no repeated
  ChatGPT URL-property lookups or full-buffer scans occur. Then run a task while focus
  remains in Outlook and confirm event-driven progress and completion still arrive.
- Repeat the idle test while the empty ChatGPT prompt remains focused. Confirm there is
  no periodic compatibility scan until a relevant accessibility event marks it dirty.
- Press Enter from a populated prompt and confirm the editor clears without an add-on
  traceback, Prompt submitted is detected, and continuous Working feedback begins.
- Review the NVDA log for repeated buffer-inspection errors or unexpected output.
- Restart NVDA while Codex is open and confirm the add-on attaches again cleanly.
