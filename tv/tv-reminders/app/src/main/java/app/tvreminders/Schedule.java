package app.tvreminders;

import java.util.Calendar;
import java.util.TimeZone;

/** When a reminder is due. */
public final class Schedule {
    private Schedule() {
    }

    /** A reminder missed while the TV was off is still shown if the TV comes back within this long. */
    public static final long LATE_OK = 12 * 3600_000L;

    /** First occurrence at or after from, or -1 if there is none. */
    public static long next(Rem r, long from, TimeZone tz) {
        if (!r.enabled) return -1;
        Calendar c = Calendar.getInstance(tz);
        if (r.mode == Rem.ONCE) {
            String[] p = r.date == null ? new String[0] : r.date.split("-");
            if (p.length != 3) return -1;
            try {
                c.clear();
                c.set(Integer.parseInt(p[0]), Integer.parseInt(p[1]) - 1, Integer.parseInt(p[2]), r.minute / 60, r.minute % 60, 0);
            } catch (NumberFormatException e) {
                return -1;
            }
            return c.getTimeInMillis() >= from ? c.getTimeInMillis() : -1;
        }
        c.setTimeInMillis(from);
        c.set(Calendar.HOUR_OF_DAY, r.minute / 60);
        c.set(Calendar.MINUTE, r.minute % 60);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        for (int i = 0; i < 9; i++) {
            boolean dayOk = r.mode == Rem.DAILY || (r.days & (1 << c.get(Calendar.DAY_OF_WEEK))) != 0;
            if (dayOk && c.getTimeInMillis() >= from) return c.getTimeInMillis();
            c.add(Calendar.DAY_OF_YEAR, 1);
        }
        return -1;
    }

    /** The occurrence to show now, or -1: due, not shown yet and not older than LATE_OK. */
    public static long due(Rem r, long now, TimeZone tz) {
        long t = next(r, Math.max(r.doneUntil + 1, now - LATE_OK), tz);
        return t != -1 && t <= now ? t : -1;
    }

    /** The next moment to wake up for this reminder, or -1. */
    public static long upcoming(Rem r, long now, TimeZone tz) {
        return next(r, Math.max(r.doneUntil + 1, now + 1), tz);
    }
}
