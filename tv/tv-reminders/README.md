# تذكيراتي (tv-reminders)

An Android TV / Google TV app that shows reminders over whatever is on screen. Reminders are added from a phone:
the TV serves a small page on the home network at `http://<tv-ip>:8090`.

- A reminder has a text, a time, and repeats once, every day, or on chosen weekdays.
- Its sound is silent, three beeps, or a sound file sent from the phone and kept on the TV (mp3, m4a, wav and similar, up to 8 MB, 20 files). The message leaves the screen after 6 seconds; a longer sound plays on to its end.
- "Show now" puts a line on the TV immediately.
- A reminder that comes due while the TV is in standby shows when the screen comes back, if that is within 12 hours.
- Reminders are stored on the TV. The service restarts after a reboot.

Ready-built APK: `docs/tv/reminders.apk`, on the install page <https://ahmadalobaid2020-a11y.github.io/my-claude-skills/tv/>
(short link <https://tinyurl.com/noor-tv-app>). Install it on the TV with the Downloader app, open it once and allow
"display over other apps". The app's screen shows the address to open on the phone.

The phone page is open to the home network unless a PIN (4 to 8 digits) is set from the app's TV screen. With a PIN, every request must carry it; five wrong PINs in a row lock the page for a minute. It is plain HTTP, so the PIN keeps out other people on the Wi-Fi, not someone capturing the network traffic.

## Built-in sounds

Two sounds come with the app and appear in the list on first start (deleting one keeps it deleted). Both are CC0 1.0
recordings from Freesound, trimmed and normalised to -16 LUFS:

- "جرس باب": "Doorbell Notification" by TheBuilder15, <https://freesound.org/people/TheBuilder15/sounds/415763>
- "تنبيه جوال": "Phone Notification" by PearceWilsonKing, <https://freesound.org/people/PearceWilsonKing/sounds/413691>

## Layout

| File | What it holds |
| --- | --- |
| `Rem`, `Schedule`, `Book` | The reminder, when it is due, and the stored list. No Android types. |
| `Sounds` | The stored sound files. No Android types. |
| `Web` | The HTTP server behind the phone page. No Android types. |
| `Svc`, `Wake` | Foreground service, alarms, boot restart. |
| `Banner` | The strip drawn over other apps. |
| `MainActivity` | The TV screen: phone address, permission button, test button. |
| `assets/page.html` | The phone page. |

## Build

Needs JDK 17+ and the Android SDK (`platforms;android-34`, `build-tools;34.0.0`); point `local.properties` at it.

```bash
./gradlew assembleRelease   # app/build/outputs/apk/release/app-release.apk
```

The APK in `docs/tv/` is signed with a throwaway debug key that was not kept, so a rebuilt APK will not install
over it: uninstall the app on the TV first (its reminders go with it).

## Tested

The schedule, the stored list and the sound store were tested on a desktop JVM, and the phone page was driven with a headless
browser against the same server code. The app builds and passes Android lint without errors.
It has not been run on a TV or an emulator.
