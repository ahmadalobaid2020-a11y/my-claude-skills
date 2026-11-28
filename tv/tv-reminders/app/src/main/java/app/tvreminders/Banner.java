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

    static final long SHOWN = 60_000;
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    private static LinearLayout stack;

    static boolean allowed(Context c) {
        return Settings.canDrawOverlays(c);
    }

    static void show(Context context, String text, boolean sound) {
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
            if (sound) beep();
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
