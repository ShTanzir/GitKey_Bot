# MODMASE MIKASA Dialog v2

Pure-native Java Android dialog project.

## Behavior
- First launch: MIKASA dialog is shown.
- EXIT: closes the whole app. Reopening the app shows the dialog again.
- JOIN TELEGRAM: saves a persistent joined flag, opens the MODMASE Telegram channel in Telegram when available, otherwise opens the browser. Reopening the app will not show the dialog again.
- Back/outside touch cannot dismiss the dialog.

## Files
- `app/src/main/java/com/modmase/dialog/MainActivity.java` — hook only.
- `app/src/main/java/com/modmase/dialog/MIKASA.java` — all dialog UI, animation and logic.
- `app/src/main/assets/mikasa.png` — dialog image.
- `app/src/main/assets/fonts/` — bundled aesthetic fonts, so the APK does not depend on internet font loading.
- `app/src/main/res/drawable-nodpi/app_icon.png` — round launcher icon generated from the supplied `logo.jpg`.

## Build with GitHub Actions
Push to `main`, then open **Actions → Build MODMASE APK → Run workflow**.

The workflow intentionally uses no AndroidX/AppCompat/Material dependencies and checks that the built debug APK contains exactly one `classes.dex` file.
