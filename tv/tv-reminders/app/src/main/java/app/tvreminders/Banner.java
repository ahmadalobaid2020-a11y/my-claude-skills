package app.tvreminders;

import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.TextView;

/** The reminder strip drawn over whatever the TV is showing. Several reminders stack under each other. */
final class Banner {
    private Banner() {
    }

    /** How long a message stays on screen. Its sound, if longer, plays on to the end. */
    static final long SHOWN = 6_000;
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    private static LinearLayout stack;

    static boolean allowed(Context c) {
        return Settings.canDrawOverlays(c);
    }

    private static android.media.MediaPlayer player;

    /** clip: a stored sound's name to play with the strip; without one, sound means three beeps. */
    static void show(Context context, String text, boolean sound, String clip) {
        Context c = context.getApplicationContext();
        if (!allowed(c)) return;
        MAIN.post(() -> {
            WindowManager wm = c.getSystemService(WindowManager.class);
            if (stack == null) {
                LinearLayout box = new LinearLayout(c);
                box.setOrientation(LinearLayout.VERTICAL);
                box.setGravity(Gravity.CENTER_HORIZONTAL);
                WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                        WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
                        WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
                        PixelFormat.TRANSLUCENT);
                lp.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
                lp.y = 60;
                try {
                    wm.addView(box, lp);
                } catch (Exception e) {
                    return;
                }
                stack = box;
            }
            View line = line(c, text);
            stack.addView(line);
            if (sound && play(c, clip) == 0) beep();
            MAIN.postDelayed(() -> {
                if (stack == null) return;
                stack.removeView(line);
                if (stack.getChildCount() == 0) {
                    try {
                        wm.removeView(stack);
                    } catch (Exception ignored) {
                    }
                    stack = null;
                }
            }, SHOWN);
        });
    }

    /** Plays a stored clip on the media stream. Returns its length in ms, or 0 when there is nothing to play. */
    private static int play(Context c, String clip) {
        java.io.File f = clip == null || clip.isEmpty() ? null : Svc.sounds(c).file(clip);
        if (f == null) return 0;
        try {
            if (player != null) player.release();
            android.media.MediaPlayer p = new android.media.MediaPlayer();
            p.setAudioAttributes(new android.media.AudioAttributes.Builder()
                    .setUsage(android.media.AudioAttributes.USAGE_MEDIA)
                    .setContentType(android.media.AudioAttributes.CONTENT_TYPE_MUSIC).build());
            p.setDataSource(f.getAbsolutePath());
            p.prepare();
            p.setOnCompletionListener(mp -> {
                mp.release();
                if (player == mp) player = null;
            });
            p.start();
            player = p;
            return Math.min(Math.max(p.getDuration(), 1), 10 * 60_000);
        } catch (Exception e) {
            player = null;
            return 0; // unreadable file: fall back to beeps
        }
    }

    private static View line(Context c, String text) {
        TextView v = new TextView(c);
        v.setText("🔔  " + text);
        v.setTextColor(Color.WHITE);
        v.setTextSize(30);
        v.setTypeface(Typeface.DEFAULT_BOLD);
        v.setGravity(Gravity.CENTER);
        v.setMaxWidth(c.getResources().getDisplayMetrics().widthPixels * 8 / 10);
        v.setPadding(56, 24, 56, 24);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(0xF0102A43);
        bg.setCornerRadius(44);
        bg.setStroke(3, 0xFFFACC15);
        v.setBackground(bg);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = 14;
        v.setLayoutParams(lp);
        return v;
    }

    /** Three short tones on the media stream, the one a TV always plays. */
    private static void beep() {
        try {
            ToneGenerator tone = new ToneGenerator(AudioManager.STREAM_MUSIC, 90);
            for (int i = 0; i < 3; i++) MAIN.postDelayed(() -> tone.startTone(ToneGenerator.TONE_PROP_BEEP, 250), i * 450L);
            MAIN.postDelayed(tone::release, 2000);
        } catch (Exception ignored) {
            // no tone generator on this TV: the strip still shows
        }
    }
}
