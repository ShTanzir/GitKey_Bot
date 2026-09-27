# MODMASE MIKASA Native Java Dialog

Native Android Java implementation of the MODMASE dialog.

## Main files

- `app/src/main/java/com/modmase/dialog/MainActivity.java` - hook only; starts `MIKASA`.
- `app/src/main/java/com/modmase/dialog/MIKASA.java` - complete dialog UI and animation; no XML layout.
- `app/src/main/assets/mikasa.png` - dialog image.
- `.github/workflows/build.yml` - GitHub Actions APK build workflow.

## Image

Replace `app/src/main/assets/mikasa.png` with your preferred 16:9 Mikasa image. The Java code reads the image directly from the `assets` folder.

## Build

Push the project to GitHub, then open **Actions -> Build MODMASE APK -> Run workflow**.

The workflow uploads `app-debug.apk` as the artifact `MODMASE-MIKASA-Debug-APK`.
