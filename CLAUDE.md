# Keisetsu

A Tkinter flashcard app for studying Japanese (romaji → kana) and Chinese (numbered pinyin → tone marks) vocabulary from CSV decks.

## Layout

- `keisetsu.py` — the main app (single file). Run with `python3 keisetsu.py`. Requires `pandas` and `Pillow`.
- `vocab_manager.py` — the companion CSV deck editor, launched from the "CSV Manager" button.
- `vocab_lists/` — CSV decks that "Import CSV" reads from.
- `themes/` — one folder per custom theme (`bg_main.png`, `bg_sidebar.png`, `bg_topbar.png`, `btn_*.png`).
- `keisetsu_settings.json` — the user's saved settings.
- `logo.png` — shown in the About window. It's also the window icon if `icon.png` is missing.
- `icon.png` (optional) — the window and taskbar/panel icon.
- `install_launcher.sh` — installs `~/.local/share/applications/keisetsu.desktop` so Keisetsu shows up in the app menu and can be pinned to the panel. Rerun it after adding `icon.png` or moving the folder.
- `install_launcher_windows.py` — the Windows equivalent: run it with the Python that has pandas and Pillow, and it creates a `Keisetsu` desktop shortcut that starts `keisetsu.py` with `pythonw.exe` (no console window). It makes `keisetsu.ico` from `icon.png` (or `logo.png`). Rerun it after changing `icon.png`, moving the folder or reinstalling Python.
- `build_windows.py` — builds the standalone Windows version with PyInstaller (`pip install pyinstaller`, then `python build_windows.py`). It produces `dist/Keisetsu/` (`Keisetsu.exe`, `_internal/`, `icon.png`, `logo.png`, and only the sample deck `SAMPLE_DECKS` and the `.png` files of the sample theme `SAMPLE_THEMES`) and `dist/Keisetsu-Windows.zip`. `build/` and `dist/` are build output.
- `README.md`, `LICENSE` (MIT), `requirements.txt` — for the public GitHub repo.

## Git repo

The repo is public, so `.gitignore` keeps it to what the app needs. Of `vocab_lists/`, only the sample deck is tracked, and of `themes/`, only `mb/*.png`. Personal settings, `.psd`/`.zip` files, the old `keisetsuog.py`/`keisetsurev2.py`, and generated files (`keisetsu.ico`, `build/`, `dist/`) stay local. Keep this in step with `SAMPLE_DECKS`/`SAMPLE_THEMES` in `build_windows.py`. `.gitattributes` keeps `.sh` files on LF line endings.

## Windows .exe

- `APP_DIR` is Keisetsu's folder: the folder holding the .exe when frozen (`sys.frozen`), otherwise the folder holding `keisetsu.py`. Keisetsu `chdir`s there at startup, so relative paths (settings, `themes/`, `vocab_lists/`, `logo.png`) work however it's launched. Never locate files with `__file__` directly; it points into PyInstaller's unpack folder in the .exe. `vocab_manager.py`'s `BASE_DIR` follows the same rule.
- The .exe has the CSV Manager built in: `open_csv_manager` starts `Keisetsu.exe --csv-manager` (`CSV_MANAGER_ARG`), which runs `vocab_manager.main()` instead of Keisetsu.
- `EXCLUDED_MODULES` in `build_windows.py` leaves out optional pandas extras (pyarrow etc.), saving about 100 MB. If Keisetsu ever needs more than `pd.read_csv`/`concat`/`isna`/`notna`, check the build still works.

## Build number and date

These are set by `BUILD_VERSION` and `BUILD_DATE` near the top of `keisetsu.py`, and they appear in the About window.

**Every change to Keisetsu must:**
1. Bump `BUILD_VERSION`: minor (`1.4.0` → `1.5.0`) for features, patch (`1.4.0` → `1.4.1`) for fixes and small tweaks.
2. Set `BUILD_DATE` to the day of the change, written like `September 25, 2026`.
3. Add an entry at the top of the Build Log below, with the same build number and date and a short list of what changed.

## Conventions

- Mascot ASCII frames are 4 lines tall, and every line must be exactly 11 characters wide *and* use only glyphs that measure one cell in the mascot font (check with `tkinter.font.Font.measure`). The mascot is center-anchored, so frames with different widths make it jitter.
- Mascot states named in `ACTIVITY_STATES` (`idle`, `sleeping`, `startled`) are driven by user activity. States in `REACTION_STATES` (`embarrassed`, `angry`, `fuming`, `relieved`) are driven by answers. Any other state in an animal's `states` dict is its "fun" alternate state (`fun_states()`), used for correct answers and random idle flourishes. Every mascot must have all seven non-fun states, plus an `origin` ("Japanese" or "Chinese"), which picks its column in the chooser.
- States in `LOOPING_STATES` (`idle`, `sleeping`, `fuming`) loop. Every other state plays once and then returns to the resting state, which is `fuming` while `_grudge_cards` is non-empty and `idle` otherwise. `STATE_SPEED` slows a state's frame rate (`relieved` plays at half speed).
- Subwindows (`tk.Toplevel`) never get a fixed `geometry("WxH")`. Build the contents, then call `self.fit_window(top, design_w, design_h)` with the size at 100% zoom (0 = fit the contents). It scales by the real rendered font size (`self.px()`), never goes smaller than the contents, and centers over the main window. Scale fixed pixel sizes inside subwindows (thumbnails, canvases) with `self.px()` too.
- When you add a feature a user would notice, update the Help Guide text in `open_help_page`. The exception is surprises meant to be discovered, such as the Study Mascot's moods and the Perfect Run celebration: keep them out of the Help Guide.
- `vocab_manager.py` picks its palette at import time: `DARK_MODE` comes from `"theme"` in `keisetsu_settings.json`. Use the named color constants (`TEXT_FG`, `HINT_FG`, `FIELD_FG`...) rather than hex literals, so new widgets follow Dark mode.

## Build Log

### Build 1.11.1 — October 3, 2026
- The download now includes only the files Keisetsu needs, plus one sample deck ("Select this deck to test the program!", which walks new users through answering a card and points them to the CSV Manager) and one sample theme (`mb`, its `.png` files only, no `.psd`). The zip went from 68 MB to 46 MB. The public source code will follow the same rule.

### Build 1.11.0 — October 3, 2026
- Keisetsu can now be built as a standalone Windows app (`Keisetsu.exe`) that doesn't need Python installed. `build_windows.py` runs PyInstaller and assembles `dist/Keisetsu/` and `dist/Keisetsu-Windows.zip` (about 68 MB, including the bundled themes and decks). `keisetsu_settings.json` is left out, so downloads start with default settings.
- Keisetsu now finds its files from its own folder (`APP_DIR`) instead of the current working directory, so it also works when started from somewhere else. `vocab_manager.py` does the same.
- In the .exe, "CSV Manager" opens the built-in manager (`Keisetsu.exe --csv-manager`), since there's no separate Python to run `vocab_manager.py` with.

### Build 1.10.3 — September 27, 2026
- Added `install_launcher_windows.py`, which creates a Keisetsu shortcut on the Windows desktop (found through Windows, so a OneDrive-redirected desktop works). The shortcut runs `pythonw.exe keisetsu.py` from the app folder, so no terminal window opens, and uses a generated `keisetsu.ico` made from `icon.png`, or `logo.png` if there's no `icon.png`.

### Build 1.10.2 — September 27, 2026
- Fixed on Windows: "C-C-C-COMBO BREAKER!!!" left red slivers (the tips of its slanted letters) on screen until Keisetsu was closed. The combo text uses a synthesized bold italic whose glyphs stick out past the box Tk measures, and the canvas only repaints that box. Before each change, an invisible rectangle (`_combo_repaint_id`) is now stretched over the combo text plus a margin (`_repaint_combo_area`), so the whole area is repainted. This covers the combo counter, its glow and the "COMBO MODE!" splash too.
- Fixed on Windows: during the Perfect Run celebration with a custom theme, the dancing sidebar buttons smeared their edges across the themed background, like the Solitaire win screen. Windows didn't repaint the strips of the background label that the moving buttons uncovered. The sidebar and top bar background labels are now told to redraw (`<Expose>`) after each dance step, on Windows only.

### Build 1.10.1 — September 26, 2026
- Combo Mode is now temporary and never saved. It ends when you switch decks or restart Keisetsu. If it's switched on before any deck is loaded, it carries over to the first deck (`_combo_deck`). To turn it on again, repeat the 10 logo clicks.
- Removed the "🎮 Combo Mode: ON/OFF" sidebar button, the all-time best score (`combo_best`), and the `combo_unlocked`/`combo_mode`/`combo_best` settings. The end-of-deck results now show only that deck's MAX COMBO. The About unlock message now says "(Lasts until you switch decks or restart Keisetsu.)".

### Build 1.10.0 — September 26, 2026
- **Combo Mode**, a secret game mode. Keep it out of the Help Guide.
  - **Unlocking:** click the About window's logo `COMBO_UNLOCK_CLICKS` (10) times before closing it. If there's no `logo.png`, the title is the target. The disclaimer box then becomes a color-cycling "★ SECRET MODE UNLOCKED ★", and Combo Mode switches on. A "🎮 Combo Mode: ON/OFF" sidebar button (below Auto-Kana) appears from then on. `combo_unlocked`, `combo_mode` and `combo_best` are saved in `keisetsu_settings.json`.
  - **What changes:** the prompt, feedback, tip and "Cards remaining" text are hidden. Only the question, the entry row, the mascot and the progress bar stay. There's no delay between cards. Switching it on shows a "COMBO MODE!" splash.
  - **Correct answers:** the question explodes into its own characters in bright colors. From `COMBO_SHOW_AT` (3) in a row, an "N HIT COMBO" counter appears under the entry. It jumps on every hit and grows up to a cap. It fades from amber into a cycling rainbow from 25 to 50 hits. From 50 it has a pulsing white glow: 8 copies of the text around it, since Tk can't blur. From 75 it trembles, harder every 25 hits after that, up to a cap. Milestone callouts appear at 10 (NICE!), 25, 50, 75 and 100, then "GODLIKE!" every 50.
  - **Misses:** a visible counter explodes, and "C-C-C-COMBO BREAKER!!!" slams in red, shakes, and fades after 3 s. The correct answer floats up in red below it, because the usual feedback text is hidden.
  - **End of deck:** the results show MAX COMBO and either "★ NEW RECORD! ★" or your all-time BEST.
- Fixed: pressing Enter again during the 5 s result pause could grade the same card twice, or skip the next card entirely. Only one next-card timer can be pending now (`_schedule_next_card`), and answers are ignored while it is.
- Fixed: the mascot's "Ouch!"/"Phew~" words no longer start off-screen when the mascot is at the top of the window.
- Particles can have a font-size multiplier (`scale` on `AnimationEngine.emit`/`burst`).

### Build 1.9.1 — September 26, 2026
- Sidebar button labels are no longer cut off under desktop display scaling. The sidebar's width came only from the window size (170–300 px), but the text buttons use a fixed 11 pt font that renders far wider when scaled. The sidebar is now at least as wide as its widest text button needs (`_sidebar_text_width`), capped at 40% of the window. Themes whose buttons are all PNGs are unaffected.

### Build 1.9.0 — September 26, 2026
- Removed the "⚙️ 設定 (Settings)" header from the top of the sidebar. Import CSV is now the first item.
- The Auto-Kana / Auto-Pinyin button's text now follows Bright/Dark mode when no custom theme is applied. It sits inside its glow frame rather than directly in the sidebar, so `apply_theme`'s sidebar loop never reached it, and its text stayed black.
- CSV Manager (`vocab_manager.py`) now opens in Dark mode when Keisetsu is in Dark mode. It reads `"theme"` from `keisetsu_settings.json`, so this also works when the manager is run on its own. The dark palette matches Keisetsu's Dark theme. Hard-coded text colors became named constants (`TEXT_FG`, `HINT_FG`, `GROUP_FG`, `FIELD_FG`, `BANNER_SUB_FG`, `HEADER_ACTIVE`). In Dark mode, `apply_dark_defaults` also darkens plain tk widgets (`tk_setPalette` plus the option database), ttk widgets, and Tk's own message boxes and file picker, including the file list's hard-coded white canvas. Light mode looks exactly as before. The Help Guide's CSV Manager section mentions it.
- Removed the "Your Mascot's Moods" section from the Help Guide, so users discover the moods themselves.

### Build 1.8.0 — September 26, 2026
- Five new Study Mascots from Chinese mythology: **Sun Wukong** (golden circlet, `@` ears, staff; fun state `somersault` on his cloud), **Zhu Bajie** (pig snout, rake; `feasting`), **Jade Rabbit** (moon and pestle; `pounding` elixir), **Nezha** (hair buns, fire-tipped spear, wind-fire wheels; `wheels`) and **Chinese Dragon** (antler horns, whiskers, pearl; `pearl`). All are 4 lines and 11 cells wide like the others, so the frames didn't need a 5th line. Each animal now has an `origin`, and "Choose Study Mascot" lists them in Japanese and Chinese columns.
- Mascot moods, for all 10 mascots:
  - A wrong answer plays `embarrassed`: a wince and duck, a sweat drop and "Ouch!"/"Oof!"/"Yikes!". This replaces the old "no" shake.
  - Missing one card `ANGRY_STREAK` (3) times in a row plays `angry`: a stomp, a furious shake, red `╬` marks and "Grr!"/"Hmph!". The streak (`wrong_streak` in `card_stats`) resets when that card is answered right.
  - Missing one card `GRUDGE_MISSES` (5) or more times in total adds it to `_grudge_cards`. While any are left, the mascot rests in a looping `fuming` state (glaring with arms crossed, occasional steam and anger marks). It celebrates correct answers with a hop but doesn't smile, and it doesn't doze off. Loading a new deck clears the grudges.
  - Mastering the last grudge card plays `relieved`: a slow breath in, a sigh out with drifting puffs and "Phew~", then back to `idle`.
- One-shot mascot states now show their last frame for a full beat before returning to rest; before, the last frame flashed for one tick. The mascot can only fall asleep from `idle`, so dozing never cuts off a reaction.
- Particles can now have their own gravity, color and fixed size (`AnimationEngine.emit`), and `AnimationEngine.cancel` stops a running motion so a new one takes over cleanly.
- Help Guide lists the new mascots and has a new "Your Mascot's Moods" section.

### Build 1.7.1 — September 26, 2026
- Subwindows are no longer too small on scaled displays. They had fixed pixel sizes (Custom BG was 320×280), but Linux Mint at 125% renders fonts about 1.9× bigger than those sizes assumed, so buttons such as "Apply Opacity" were cut off. New `fit_window` sizes each window from its design size × the measured font scale (`compute_font_scale`, `px()`), never smaller than its contents, capped at 90% of the screen and centered over the main window. It applies to Themes, Help Guide, About, Custom BG Color, Change Study Mascot and Customize Font. Theme thumbnails and the About logo scale too.
- The "Import CSV" file picker (Tk's built-in dialog, whose file list is a fixed 400×120 px) opens at 720×480 × the font scale.

### Build 1.7.0 — September 25, 2026
- CSV Manager (`vocab_manager.py`) now adapts to display scaling. It measures the rendered UI font (`compute_ui_scale`, giving `UI_SCALE`) instead of trusting the reported DPI, and scales every pixel size through `px()`. Linux Mint at 125% renders fonts at 192 DPI while Tk reports 120, which made text about 3.4× larger than the fixed 26 px rows and caused them to overlap. Treeview row height now comes from the data font's real line height. Column widths, the `#` column (fits 4 digits), banner heights (fit the title/subtitle), button padding and scrollbar arrows scale too. The main window opens at its design size × `UI_SCALE`, capped at 90% of the screen and centered.
- The spreadsheet view's pinyin toggle and hint moved to their own row under the buttons, so they can't be pushed off-screen.
- New **Delete** button in the CSV Manager toolbar (also the Delete key and File → Delete Row…). It deletes the highlighted row after a confirmation that shows the row's number, question and answers (defaults to No), saves the file, and highlights the row that took its place. The table is now single-select. Help Guide's CSV Manager section mentions it.

### Build 1.6.3 — September 25, 2026
- Toggling Bright/Dark mode no longer makes the window bob. The top progress bar frame was created with `height=45`, but its contents need about 58 px. Tk re-applies a frame's configured height whenever the frame is reconfigured, such as setting its `bg` in `apply_theme`. So the bar snapped to 45 px and back, and the canvas re-laid out twice. The frame now has no fixed height, and its contents set it. This is the same underlying cause as the 1.6.2 mascot-switch bob.

### Build 1.6.2 — September 25, 2026
- Perfect Run: on the first celebration of a session, the "Incredible! You cleared the entire dataset…" tip no longer slides up underneath the "Answers:" text. The dance's rest positions were only recorded at the last layout pass, before the final feedback was shown. `start_perfect_run_celebration` now re-records them (`_snapshot_rest_coords`).
- Changing Study Mascot no longer makes the rest of the window bob. The mascot used a named `tkinter.font.Font`, and resizing a named font makes Tk re-lay out every widget. That briefly changed the top bar's height and re-ran the whole layout on each step of the switch animation. The mascot text now uses a plain font tuple (`BUDDY_FONT_FAMILY`), so resizing it only redraws the mascot.
- The mascot switch animation is faster: about 0.3 s (120 ms fade/shrink out, 180 ms fade/grow in) instead of about 0.7 s.

### Build 1.6.1 — September 25, 2026
- Missed cards are now put back at a random spot among the cards still to come (`requeue_card`), never as the very next card when others remain (`REQUEUE_MIN_GAP = 2`), instead of being added to the end of the deck. Cards that are answered correctly but not yet mastered are put back the same way. Added a "Missed Cards" section to the Help Guide.
- Study Mascot particles are a little bigger: 15 pt at full life instead of 12, scaled with the window, and never below 10 pt.
- Smoother Perfect Run celebration and particles. The animation loop runs at about 60 fps while anything is moving (20 fps when idle), and steps by the real time elapsed, so motion speed doesn't depend on frame rate. Stars, fireworks, embers, particles and the rainbow progress bar keep their canvas items and update them in place instead of deleting and recreating hundreds of items every frame. Sidebar widgets are only re-placed when their position changes. Star twinkle is now a smooth ~1 s pulse; before, it was fast enough to look like random flicker.
- The rainbow progress bar is a pre-rendered gradient image that slides each frame, instead of ~240 recolored rectangles.
- Themed sidebar/topbar backgrounds and button PNGs are flattened onto their widget's background color (`_opaque_photo`) before display. It looks identical, since Tk labels aren't see-through, but Tk on X11 blends partly transparent images pixel by pixel on every repaint. That was the main reason the sidebar dance was slow. With the y2k theme the celebration went from ~19 fps to ~58 fps.

### Build 1.6.0 — September 25, 2026
- Restyled the `sleeping` and `startled` frames of Shiba Inu, Maneki-Neko, Daruma Doll and Spirit Kitsune to match their 4-line designs (for example `(´ᴗωᴗ`)` asleep and `\( ◎ω◎ )/` startled).
- Study Mascot position: the mascot now defaults to the bottom-left corner of the window instead of sitting above the question. "Change Study Mascot" has a new "Mascot position" choice: Top Left, Top Center, Top Right, Bottom Left or Bottom Right. It's saved as `mascot_position` in `keisetsu_settings.json`. Corner mascots hug the window edge. When the panel is wide enough, the question and feedback wrap narrower to stay beside the mascot; otherwise the question moves below a top mascot, or the question and entry row move up above a bottom one. There's no Bottom Center, because the answer feedback fills that spot.
- The mascot's base font size went from 18 to 15, so the 4-line mascot takes about as much room as the old 3-line one.
- Particle bursts now start from the mascot's actual on-screen box, wherever it is placed.
- The "Choose Study Mascot" window now sizes itself to its contents instead of a fixed 320×300, so nothing is cut off with desktop display scaling.

### Build 1.5.0 — September 25, 2026
- Redesigned the default (`idle`) and fun-state frames of all four Study Mascots as 4-line, Shift-JIS-style text art using Unicode such as `∧___∧`, `ω`, `◉`, `╱╲`, `≋`. Shiba Inu has a curled `ɷ` tail. Maneki-Neko has a raised beckoning paw, a collar bell and a `[¥]` koban coin. Daruma Doll is rounded and has one eye painted in (`◉ ○`), and its wobble now tilts from its base. Spirit Kitsune has a fluffy `≋` tail and `∘°` foxfire.
- Added a fifth mascot, **Tanuki**, with a ☘ leaf on its head, `◐ ◑` eye mask and round belly. Its fun state is `drumming` (belly-drumming with ♪♫), and it has its own `sleeping` and `startled` frames.
- The existing `sleeping`/`startled` frames are unchanged apart from a blank 4th line, so every frame of a mascot has the same height.
- Mascot glyphs are limited to characters that render exactly one cell wide in the mascot font (DejaVu Sans Mono on Linux). Half-width and full-width kana such as `ﾟ`, `ﾉ` and `つ` are wider or narrower than one cell, so they would make the mascot jitter.

### Build 1.4.1 — September 25, 2026
- Added `install_launcher.sh`, which creates a `.desktop` menu launcher (with `StartupWMClass=Keisetsu`, so the running window groups with a pinned panel icon). It uses `icon.png` when present, otherwise `logo.png`.

### Build 1.4.0 — September 25, 2026
- Removed the "Perfect Run Easter Egg" section from the Help Guide. The celebration itself is unchanged.
- Study Mascot idle animation: after 30 seconds with no key press or click (`BUDDY_SLEEP_SECONDS`), the mascot falls asleep (closed eyes, drifting "zZ", slight sink). The next key press or click startles it awake with a jump and a burst of "!" particles. All four mascots have `sleeping` and `startled` frames.
- Window/taskbar icon: `icon.png` in the app folder is loaded automatically at several sizes (falling back to `logo.png`) and applied to all windows. The Tk root now uses `className="Keisetsu"` so Linux panels such as Linux Mint's Cinnamon group and label the window correctly.
- About window: "embi.neocities.org" is now a clickable link that opens https://embi.neocities.org/.
- Romaji → kana: added small kana with the x/l prefix (`xa`/`la` → ぁ, `xtsu`/`xtu`/`ltu` → っ, `xya` → ゃ, `xwa` → ゎ, etc.) and `vu` → ゔ, so "vuxo" → ゔぉ and "fuxa" → ふぁ.

### Build 1.3.0 — September 23, 2026
- Baseline build before this log was started.
