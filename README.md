# FocusFlow

A focus timer (counts down) and a time tracker (counts up) that share one task menu. A dashboard adds the two together.

**Live app:** https://ds-js1.github.io/focusflow/

Time entries are stored in the browser of the device you use. Nothing is sent to a server. Use Settings → Export CSV to back up your log or move it to another device.

## Files

- `focusflow.html`: the app source. Edit this file.
- `build.py`: wraps the source into `index.html` for GitHub Pages and bumps the offline cache version. Run `python build.py` after every edit.
- `index.html`: generated. Don't edit it by hand.
- `sw.js`, `manifest.webmanifest`, `icon*`: offline support and home-screen install.

## Test mode

Add `#test` to the URL and timer minutes run as seconds.
