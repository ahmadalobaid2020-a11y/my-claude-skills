package app.tvreminders;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.util.Collections;

/** The TV screen of the app: the address to open on the phone, the one permission it needs, and a test button. */
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        Svc.start(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        draw();
    }

    private void draw() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setBackgroundColor(0xFF102A43);
        box.setPadding(120, 50, 120, 50);

        boolean overlay = Banner.allowed(this);
        String ip = address();
        text(box, "🔔 تذكيراتي", 40, 0xFFFACC15);
        text(box, "افتح هذا العنوان من متصفح جوالك (على نفس الواي فاي):", 24, Color.WHITE);
        text(box, ip == null ? "التلفزيون غير متصل بالشبكة" : "http://" + ip + ":" + Web.PORT, 44, 0xFFFACC15);
        text(box, "عدد التذكيرات: " + Svc.book(this).all().size(), 22, 0xFFBCCCDC);

        Button first;
        if (!overlay) {
            text(box, "⬜  لازم تسمح للتطبيق بـ«العرض فوق التطبيقات» عشان يطلع التذكير على الشاشة", 22, Color.WHITE);
            first = button(box, "افتح إعداد «العرض فوق التطبيقات»", () -> {
                try {
                    startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + getPackageName())));
                } catch (Exception e) {
                    try {
                        startActivity(new Intent(Settings.ACTION_SETTINGS));
                    } catch (Exception ignored) {
                    }
                }
            });
            text(box, "إذا ما انفتح الإعداد: الإعدادات ← التطبيقات ← أذونات خاصة للتطبيقات", 18, 0xFFBCCCDC);
        } else {
            text(box, "✅  التذكيرات جاهزة وتطلع فوق أي شي شغال", 22, Color.WHITE);
            first = button(box, "جرّب تذكير الآن", () -> Banner.show(this, "هذا تذكير تجريبي", true, ""));
        }
        setContentView(box);
        first.requestFocus();
    }

    private void text(LinearLayout box, String s, int size, int color) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(size);
        t.setTextColor(color);
        t.setGravity(Gravity.CENTER);
        t.setPadding(0, 14, 0, 14);
        box.addView(t);
    }

    private Button button(LinearLayout box, String label, Runnable action) {
        Button btn = new Button(this);
        btn.setText(label);
        btn.setTextSize(22);
        btn.setOnClickListener(v -> action.run());
        box.addView(btn);
        return btn;
    }

    /** The TV's address on the home network, or null. */
    private static String address() {
        try {
            for (NetworkInterface ni : Collections.list(NetworkInterface.getNetworkInterfaces())) {
                if (!ni.isUp() || ni.isLoopback()) continue;
                for (InetAddress a : Collections.list(ni.getInetAddresses())) {
                    if (a instanceof Inet4Address && a.isSiteLocalAddress()) return a.getHostAddress();
                }
            }
        } catch (Exception ignored) {
        }
        return null;
    }
}
