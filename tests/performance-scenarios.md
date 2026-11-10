# 2026.3.0 responsiveness check

Run with NVDA 2026.2 and the test package installed only after choosing to
install it. Use the same large conversation for before/after comparisons. In
NVDA Settings > ChatGPT Desktop Access > Support, copy the sanitized diagnostics
before and after each scenario. Record the last/max durations and slow counts
for **conversation scan** and **background mode probe**; do not include chat content.

| Scenario | Steps | Expected result |
| --- | --- | --- |
| Large conversation | Open a conversation with many turns; use headings, arrows, Control+1, and Control+0. | Speech, Braille, and navigation remain responsive; scans are not repeated on every arrow key. |
| UI Automation document | In NVDA Advanced settings, set UI Automation for Chromium to Yes, restart ChatGPT, run a Codex task, then press Enter on Add files and more. | The Add files and more list opens within about a second; speech keeps up during the task; conversation scans run at most about once a minute. |
| Braille typing | Enter and correct a multi-sentence prompt using a Braille display. Repeat with the keyboard. | Characters remain in order; scans are deferred while typing; no main-thread stall. |
| Mode changes | Switch Chat to Work to Codex and back, opening History in each view. | Chat/Work use ChatGPT history, Codex uses Codex history; a sidebar title does not change mode. |
| NVDA restart | Restart NVDA with ChatGPT open, then repeat the three scenarios. | Monitoring reattaches and the first scan/mode probe completes without a watchdog recovery. |
| Attachment popup | In ChatGPT and Codex, open Add files and more in focus and browse modes with hardware Enter, hardware Space, and Braille Enter; then navigate or close it immediately on a repeat. | Focus moves only to the exact native Attach files or connect apps control when present after an explicit activation. A second Enter, Down Arrow, Enter opens Select files. No delayed jump after navigation or closure. An expanded button alone is not a successful file-selection test. |
| ChatGPT pop-up focus | Open a permission or other ChatGPT pop-up, then immediately Alt+Tab away; repeat while staying in ChatGPT. | The delayed focus request never pulls focus back from another app. When staying in ChatGPT, focus enters the pop-up normally. |

For reproducible comparisons, record the NVDA version, ChatGPT desktop version,
add-on version, conversation size (rough number of turns), speech mode, Braille
display model, and the timing counts. A `conversation scan` warning starts at
100 ms; a `mode detection` warning starts at 500 ms. These are diagnostic
thresholds, not pass/fail limits. Check the NVDA log for `slow conversation scan`
or `slow mode detection` entries and any watchdog recovery. Never share raw
private conversation text in a report.
