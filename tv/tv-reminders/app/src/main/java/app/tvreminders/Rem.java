package app.tvreminders;

/** One reminder. Plain fields, no Android types, so the schedule can be tested on a desktop JVM. */
public class Rem {
    public static final int ONCE = 0, DAILY = 1, DAYS = 2;

    public String id;
    public String text;
    /** Minutes after midnight, TV local time. */
    public int minute;
    public int mode;
    /** For DAYS: bit n set means java.util.Calendar day n (1 = Sunday ... 7 = Saturday). */
    public int days;
    /** For ONCE: yyyy-MM-dd. */
    public String date;
    public boolean sound;
    public boolean enabled = true;
    /** Occurrences at or before this moment are done with (shown, or older than the reminder itself). */
    public long doneUntil;
}
