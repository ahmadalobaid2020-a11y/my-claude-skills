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

## Away from home

Off by default; switched on from the app's TV screen, which makes a random secret. The phone page (at home) then
shows a link, `docs/tv/remote.html#k=<secret>`, that works from any network: the same page, served over https,
talks to the TV through a public relay ([ntfy.sh](https://ntfy.sh)) instead of directly.

- The phone posts a command (add, delete, toggle, show now) to one topic; the TV listens there and posts its list
  to a second topic, which the page reads.
- Every message is AES-256-GCM under a key derived from the secret, and both topic names are derived from it too,
  so the relay sees neither the reminders nor a guessable name. A command not sealed with the key, one seen
  before, or one older than 13 hours is ignored.
- A command sent while the TV is off waits on the relay (about 12 hours) and is carried out when the TV is back;
  a "show now" older than five minutes is dropped.
- Making a new link on the TV cancels the old one. Anyone holding the link can send to the TV.
- Sounds are uploaded at home only. The relay limits message size, so the away page lists the newest reminders
  that fit in one message.
- `docs/tv/remote.html` is a copy of `app/src/main/assets/page.html`: copy it again after changing the page.
- The relay's free tier counts messages per sender address and per day. That is ample for one home, but a shared
  cloud address (such as the one this app was developed from) can find the quota already used up.

## Built-in sounds

Three sounds come with the app and appear in the list on first start (deleting one keeps it deleted).

- "صوت فهد": a voice saying «عندك تذكير», generated with ElevenLabs (voice "Fahad - Saudi, Warm & Confident",
  model eleven_v4). The phone page selects it by default.

The other two are CC0 1.0 recordings from Freesound, trimmed and normalised to -16 LUFS:

- "جرس باب": "Doorbell Notification" by TheBuilder15, <https://freesound.org/people/TheBuilder15/sounds/415763>
- "تنبيه جوال": "Phone Notification" by PearceWilsonKing, <https://freesound.org/people/PearceWilsonKing/sounds/413691>

## Layout

| File | What it holds |
| --- | --- |
| `Rem`, `Schedule`, `Book` | The reminder, when it is due, and the stored list. No Android types. |
| `Sounds` | The stored sound files. No Android types. |
| `Web` | The HTTP server behind the phone page. No Android types. |
| `Relay` | "Away from home": sealed commands and the TV's list through the public relay. No Android types. |
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
The relay path was tested end to end on a desktop JVM and a headless browser against a local stand-in for
ntfy.sh (publishing to the real service was refused from the development machine: daily quota of its shared
address), plus 16 checks of sealing and of refusing forged, replayed and stale commands.
It has not been run on a TV or an emulator.
