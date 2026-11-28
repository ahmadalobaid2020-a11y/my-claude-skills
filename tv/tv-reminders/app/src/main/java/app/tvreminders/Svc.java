package app.tvreminders;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.IBinder;
import android.os.PowerManager;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.Calendar;
import java.util.Locale;
import java.util.TimeZone;

/**
 * Keeps the phone page up and shows reminders when they are due. A reminder that comes due while the TV is in
 * standby waits, and shows when the screen comes back if that is within Schedule.LATE_OK.
 */
public class Svc extends Service implements Web.Host {
    static final String CHECK = "app.tvreminders.CHECK";

    private static Book book;
    /** Whether the phone page's server is listening, for the TV screen to say so. */
    static volatile boolean pageUp;
    private static Sounds sounds;
    private Web web;
    private BroadcastReceiver screenOn;

    static synchronized Book book(Context c) {
        if (book == null) {
            SharedPreferences p = c.getApplicationContext().getSharedPreferences("reminders", Context.MODE_PRIVATE);
            book = new Book(new Book.Disk() {
                @Override
                public String read() {
                    return p.getString("items", "[]");
                }

                @Override
                public void write(String json) {
                    p.edit().putString("items", json).apply();
                }
            });
        }
        return book;
    }

    static synchronized Sounds sounds(Context c) {
        if (sounds == null) {
            Context app = c.getApplicationContext();
            sounds = new Sounds(new java.io.File(app.getFilesDir(), "sounds"));
            seed(app, sounds);
        }
        return sounds;
    }

    /** The sounds that come with the app, by the name they get in the list. */
    private static final String[][] BUILT_IN = {{"doorbell.mp3", "جرس باب.mp3"}, {"phone.mp3", "تنبيه جوال.mp3"}};

    /** Copies the built-in sounds into the store once, so deleting one from the phone page stays deleted. */
    private static void seed(Context app, Sounds store) {
        SharedPreferences p = app.getSharedPreferences("settings", Context.MODE_PRIVATE);
        if (p.getBoolean("seeded1", false)) return;
        for (String[] s : BUILT_IN) {
            try (InputStream in = app.getAssets().open("sounds/" + s[0])) {
                ByteArrayOutputStream b = new ByteArrayOutputStream();
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) > 0) b.write(buf, 0, n);
                store.save(s[1], b.toByteArray());
            } catch (Exception ignored) {
                // a missing asset only means one sound fewer in the list
            }
        }
        p.edit().putBoolean("seeded1", true).apply();
    }

    static String pin(Context c) {
        return c.getApplicationContext().getSharedPreferences("settings", Context.MODE_PRIVATE).getString("pin", "");
    }

    static void setPin(Context c, String pin) {
        c.getApplicationContext().getSharedPreferences("settings", Context.MODE_PRIVATE).edit().putString("pin", pin).apply();
    }

    static void start(Context c) {
        try {
            c.startForegroundService(new Intent(c, Svc.class));
        } catch (Exception ignored) {
            // refused while in the background: the alarm still runs check() through Wake
        }
    }

    /** Shows what is due and sets the alarm for the next reminder. Safe to call from anywhere, any time. */
    static void check(Context context) {
        Context c = context.getApplicationContext();
        Book b = book(c);
        long now = System.currentTimeMillis();
        TimeZone tz = TimeZone.getDefault();
        boolean screen = c.getSystemService(PowerManager.class).isInteractive();
        long wake = -1;
        for (Rem r : b.all()) {
            long due = Schedule.due(r, now, tz);
            if (due != -1 && screen && Banner.allowed(c)) {
                Banner.show(c, now - due > 5 * 60_000 ? r.text + "  (كان " + clock(due, tz) + ")" : r.text, r.sound, r.clip);
                b.done(r, now);
            }
            long next = Schedule.upcoming(r, now, tz);
            if (next != -1 && (wake == -1 || next < wake)) wake = next;
        }
        AlarmManager am = c.getSystemService(AlarmManager.class);
        PendingIntent pi = PendingIntent.getBroadcast(c, 0, new Intent(c, Wake.class).setAction(CHECK),
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        if (wake == -1) {
            am.cancel(pi);
            return;
        }
        try {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, wake, pi);
        } catch (SecurityException e) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, wake, pi); // exact alarms refused: a little late beats never
        }
    }

    private static String clock(long t, TimeZone tz) {
        Calendar c = Calendar.getInstance(tz);
        c.setTimeInMillis(t);
        int h = c.get(Calendar.HOUR_OF_DAY);
        return String.format(Locale.US, "%d:%02d %s", h % 12 == 0 ? 12 : h % 12, c.get(Calendar.MINUTE), h < 12 ? "ص" : "م");
    }

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel("run", "تذكيراتي", NotificationManager.IMPORTANCE_MIN));
        Notification n = new Notification.Builder(this, "run")
                .setContentTitle("تذكيراتي")
                .setSmallIcon(android.R.drawable.ic_popup_reminder)
                .build();
        startForeground(1, n);

        try {
            web = new Web(book(this), sounds(this), this, asset("page.html"));
            web.start(Web.PORT);
            pageUp = true;
        } catch (Exception e) {
            web = null; // port taken or no network yet: reminders still fire, the phone page is just not up
        }
        screenOn = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent i) {
                check(c);
            }
        };
        registerReceiver(screenOn, new IntentFilter(Intent.ACTION_SCREEN_ON));
        check(this);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        if (web != null) web.stop();
        pageUp = false;
        if (screenOn != null) unregisterReceiver(screenOn);
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void changed() {
        check(this);
    }

    @Override
    public String pin() {
        return pin(this);
    }

    @Override
    public void show(String text, boolean sound, String clip) {
        Banner.show(this, text, sound, clip);
    }

    private byte[] asset(String name) throws Exception {
        try (InputStream in = getAssets().open(name)) {
            ByteArrayOutputStream b = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) b.write(buf, 0, n);
            return b.toByteArray();
        }
    }
}
