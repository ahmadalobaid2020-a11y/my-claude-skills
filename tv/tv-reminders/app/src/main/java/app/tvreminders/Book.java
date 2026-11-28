package app.tvreminders;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;
import java.util.UUID;

/** The list of reminders, kept as JSON wherever Disk puts it. All access is synchronized on the Book. */
public class Book {
    public interface Disk {
        String read();

        void write(String json);
    }

    public static final int MAX_TEXT = 200, MAX_ITEMS = 100;

    private final Disk disk;
    private final List<Rem> items = new ArrayList<>();

    public Book(Disk disk) {
        this.disk = disk;
        try {
            JSONArray a = new JSONArray(disk.read());
            for (int i = 0; i < a.length(); i++) items.add(fromJson(a.getJSONObject(i)));
        } catch (Exception ignored) {
            // nothing saved yet, or unreadable: start empty
        }
    }

    public synchronized List<Rem> all() {
        return new ArrayList<>(items);
    }

    /** Adds a reminder from the phone page's JSON. Returns null when it is not valid. */
    public synchronized Rem add(JSONObject in, long now, TimeZone tz) {
        if (items.size() >= MAX_ITEMS) return null;
        String text = in.optString("text", "").replaceAll("\\s+", " ").trim();
        String[] hm = in.optString("time", "").split(":");
        if (text.isEmpty() || hm.length != 2) return null;
        Rem r = new Rem();
        try {
            int h = Integer.parseInt(hm[0]), m = Integer.parseInt(hm[1]);
            if (h < 0 || h > 23 || m < 0 || m > 59) return null;
            r.minute = h * 60 + m;
        } catch (NumberFormatException e) {
            return null;
        }
        r.id = UUID.randomUUID().toString().substring(0, 8);
        r.text = text.length() > MAX_TEXT ? text.substring(0, MAX_TEXT) : text;
        r.mode = in.optInt("mode", Rem.ONCE);
        r.sound = in.optBoolean("sound", false);
        String clip = Sounds.clean(in.optString("clip", ""));
        r.clip = r.sound && clip != null ? clip : "";
        r.doneUntil = now; // a daily 08:00 reminder made at 10:00 starts tomorrow, not as "missed"
        if (r.mode == Rem.DAYS) {
            JSONArray d = in.optJSONArray("days");
            for (int i = 0; d != null && i < d.length(); i++) {
                int day = d.optInt(i);
                if (day >= 1 && day <= 7) r.days |= 1 << day;
            }
            if (r.days == 0) return null;
        } else if (r.mode == Rem.ONCE) {
            r.date = in.optString("date", "");
            if (!r.date.matches("\\d{4}-\\d{2}-\\d{2}")) {
                // No date given: today if that time is still ahead, otherwise tomorrow.
                Calendar c = Calendar.getInstance(tz);
                c.setTimeInMillis(now);
                if (c.get(Calendar.HOUR_OF_DAY) * 60 + c.get(Calendar.MINUTE) >= r.minute) c.add(Calendar.DAY_OF_YEAR, 1);
                r.date = String.format(Locale.US, "%04d-%02d-%02d", c.get(Calendar.YEAR), c.get(Calendar.MONTH) + 1, c.get(Calendar.DAY_OF_MONTH));
            }
            if (Schedule.next(r, now, tz) == -1) return null; // already in the past
        } else if (r.mode != Rem.DAILY) {
            return null;
        }
        items.add(r);
        save();
        return r;
    }

    public synchronized boolean remove(String id) {
        boolean gone = items.removeIf(r -> r.id.equals(id));
        if (gone) save();
        return gone;
    }

    /** Switches a reminder on or off. Switching on never brings back occurrences that have passed. */
    public synchronized boolean toggle(String id, long now) {
        for (Rem r : items) {
            if (!r.id.equals(id)) continue;
            r.enabled = !r.enabled;
            if (r.enabled) r.doneUntil = Math.max(r.doneUntil, now);
            save();
            return true;
        }
        return false;
    }

    /** Marks an occurrence as shown. A one-time reminder is switched off afterwards. */
    public synchronized void done(Rem r, long now) {
        r.doneUntil = now;
        if (r.mode == Rem.ONCE) r.enabled = false;
        save();
    }

    public synchronized JSONArray toJson(long now, TimeZone tz) {
        JSONArray a = new JSONArray();
        for (Rem r : items) {
            try {
                JSONObject o = json(r);
                o.put("next", Schedule.upcoming(r, now, tz));
                a.put(o);
            } catch (Exception ignored) {
            }
        }
        return a;
    }

    private void save() {
        JSONArray a = new JSONArray();
        for (Rem r : items) {
            try {
                a.put(json(r));
            } catch (Exception ignored) {
            }
        }
        disk.write(a.toString());
    }

    private static JSONObject json(Rem r) throws Exception {
        return new JSONObject().put("id", r.id).put("text", r.text).put("minute", r.minute).put("mode", r.mode)
                .put("days", r.days).put("date", r.date == null ? "" : r.date).put("sound", r.sound).put("clip", r.clip)
                .put("enabled", r.enabled).put("doneUntil", r.doneUntil);
    }

    private static Rem fromJson(JSONObject o) throws Exception {
        Rem r = new Rem();
        r.id = o.getString("id");
        r.text = o.getString("text");
        r.minute = o.getInt("minute");
        r.mode = o.getInt("mode");
        r.days = o.optInt("days");
        r.date = o.optString("date");
        r.sound = o.optBoolean("sound");
        r.clip = o.optString("clip", "");
        r.enabled = o.optBoolean("enabled", true);
        r.doneUntil = o.optLong("doneUntil");
        return r;
    }
}
