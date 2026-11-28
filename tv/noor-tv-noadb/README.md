# noor-tv without a computer

A build of the five shortcut apps from [majedphotos/noor-tv](https://github.com/majedphotos/noor-tv) (MIT, commit `c0ae5b7`)
for a TV that is set up without `adb`: the APKs are installed on the TV itself (for example with the Downloader app)
from `docs/tv/`, published at `https://ahmadalobaid2020-a11y.github.io/my-claude-skills/tv/`.

What this gives: the adhan banner and sound, the 45-minute reminder line, the phone page on port 8080 and the five
video shortcuts. What it does not give: disabling the maker's ad apps and the new home screen, which need `adb`.

## Changes to the upstream app (`no-adb.patch`)

- The Kahf app opens a set-up screen with buttons to the two TV settings pages (display over other apps, usage access)
  until both are granted. Upstream grants them with `adb shell appops`.
- "Home screen" means any installed launcher, not only the CleanYourTV one, so the adhan sound plays on the stock home screen.
- Without usage access the adhan is banner only.
- Exact-alarm permissions are declared, with a fallback to an inexact alarm.
- City: Dammam (26.4207, 50.0888), Aladhan method 4 (Umm al-Qura).

## Adhan recording

"Beautiful adhan" by Adam-synagda, CC0 1.0, from Wikimedia Commons
(<https://commons.wikimedia.org/w/index.php?curid=117597882>), trimmed and normalised to -18 LUFS.

## Rebuild

Needs JDK 17+, the Android SDK (`platforms;android-34`, `build-tools;34.0.0`) and ffmpeg.

```bash
git clone https://github.com/majedphotos/noor-tv && cd noor-tv/noor-app
git checkout c0ae5b7 && patch -p1 < /path/to/no-adb.patch
# put the adhan at app/src/kahf/res/raw/adhan.mp3, then:
./gradlew assembleRelease
```

The APKs are signed with a throwaway debug key that was not kept. A rebuilt APK will not install over these ones:
uninstall the old app on the TV first.

Not tested on a real TV: the APKs build and their manifest was checked, nothing more.
