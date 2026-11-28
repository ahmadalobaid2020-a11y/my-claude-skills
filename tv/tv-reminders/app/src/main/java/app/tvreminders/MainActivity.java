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
        String ip = address(this);
        text(box, "🔔 تذكيراتي", 40, 0xFFFACC15);
        text(box, "افتح هذا العنوان من متصفح جوالك (على نفس الواي فاي):", 24, Color.WHITE);
        text(box, ip == null ? "التلفزيون غير متصل بالشبكة" : "http://" + ip + ":" + Web.PORT, 44, 0xFFFACC15);
        text(box, "عدد التذكيرات: " + Svc.book(this).all().size()
                + (Svc.pageUp ? "   ·   صفحة الجوال شغّالة" : "   ·   ⚠️ صفحة الجوال ما اشتغلت، أعد فتح التطبيق"), 22, 0xFFBCCCDC);

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
            first = button(box, "جرّب تذكير الآن", () -> Banner.show(this, "هذا تذكير تجريبي", true, Svc.DEFAULT_CLIP));
        }
        boolean locked = !Svc.pin(this).isEmpty();
        text(box, locked ? "🔒  صفحة الجوال مقفلة برمز سري" : "🔓  صفحة الجوال بدون رمز: أي أحد على الواي فاي يقدر يفتحها", 20, 0xFFBCCCDC);
        button(box, locked ? "غيّر الرمز السري" : "حط رمز سري لصفحة الجوال", this::askPin);
        if (locked) button(box, "شيل الرمز السري", () -> {
            Svc.setPin(this, "");
            draw();
        });
        setContentView(box);
        first.requestFocus();
    }

    /** Asks for a new PIN with the TV keyboard: 4 to 8 digits. */
    private void askPin() {
        android.widget.EditText in = new android.widget.EditText(this);
        in.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        in.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(8)});
        in.setTextSize(28);
        in.setGravity(Gravity.CENTER);
        in.setHint("من 4 إلى 8 أرقام");
        new android.app.AlertDialog.Builder(this)
                .setTitle("الرمز السري لصفحة الجوال")
                .setView(in)
                .setPositiveButton("حفظ", (d, w) -> {
                    String pin = in.getText().toString().trim();
                    if (pin.matches("\\d{4,8}")) {
                        Svc.setPin(this, pin);
                    } else {
                        android.widget.Toast.makeText(this, "الرمز لازم يكون من 4 إلى 8 أرقام", android.widget.Toast.LENGTH_LONG).show();
                    }
                    draw();
                })
                .setNegativeButton("إلغاء", null)
                .show();
        in.requestFocus();
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

    /**
     * The TV's address on the home network, or null. Asks the system for the network in use first: a TV often has
     * a second, Wi-Fi Direct interface (for screen casting) whose address no phone can reach.
     */
    private static String address(android.content.Context c) {
        try {
            android.net.ConnectivityManager cm = c.getSystemService(android.net.ConnectivityManager.class);
            android.net.LinkProperties lp = cm.getLinkProperties(cm.getActiveNetwork());
            if (lp != null) {
                for (android.net.LinkAddress la : lp.getLinkAddresses()) {
                    if (la.getAddress() instanceof Inet4Address && !la.getAddress().isLoopbackAddress()) return la.getAddress().getHostAddress();
                }
            }
        } catch (Exception ignored) {
        }
        try {
            for (NetworkInterface ni : Collections.list(NetworkInterface.getNetworkInterfaces())) {
                if (!ni.isUp() || ni.isLoopback() || ni.getName().startsWith("p2p")) continue;
                for (InetAddress a : Collections.list(ni.getInetAddresses())) {
                    if (a instanceof Inet4Address && a.isSiteLocalAddress()) return a.getHostAddress();
                }
            }
        } catch (Exception ignored) {
        }
        return null;
    }
}
