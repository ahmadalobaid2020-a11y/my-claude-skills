package app.tvreminders;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.TimeZone;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * Reminders from outside the home network. The TV cannot be reached from the internet, so both sides meet at a
 * public relay (ntfy.sh): the phone posts a command to one topic, the TV listens there and posts its list to a
 * second topic for the phone to read.
 *
 * Everything on the relay is AES-256-GCM under a key that only the TV and the phone's link hold. The topic names
 * are derived from the same secret, so the relay sees neither the reminders nor a name anyone could guess, and a
 * command that was not sealed with the key is dropped. No Android types: this also runs on a desktop JVM.
 */
public class Relay {
    /** Where the last handled message and the recent command ids are kept across restarts. */
    public interface Memory {
        String get(String key);

        void put(String key, String value);
    }

    public static final String BASE = "https://ntfy.sh/";
    /** The relay refuses longer messages. */
    static final int MAX_MESSAGE = 3900;
    /** A command older than this is ignored: the relay keeps messages for about twelve hours. */
    static final long MAX_AGE = 13 * 3600_000L;
    /** The list is posted again this often, so the relay always has a recent copy for the phone. */
    static final long STATE_EVERY = 6 * 3600_000L;

    private final byte[] key;
    private final String commands, state;
    private final Book book;
    private final Sounds sounds;
    private final Web.Host host;
    private final Memory memory;
    private final String base;
    private volatile boolean stopped;
    private volatile HttpURLConnection open;
    private long statePosted, stateTried;

    public Relay(String secret, Book book, Sounds sounds, Web.Host host, Memory memory) {
        this(secret, book, sounds, host, memory, BASE);
    }

    /** base: the relay's address, for a test double. */
    public Relay(String secret, Book book, Sounds sounds, Web.Host host, Memory memory, String base) {
        this.key = sha256("key:" + secret);
        this.commands = topic("topic:", secret);
        this.state = topic("state:", secret);
        this.book = book;
        this.sounds = sounds;
        this.host = host;
        this.memory = memory;
        this.base = base;
    }

    /** A new secret for the phone's link: 24 random bytes, URL-safe. */
    public static String newSecret() {
        byte[] b = new byte[24];
        new SecureRandom().nextBytes(b);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(b);
    }

    static String topic(String label, String secret) {
        StringBuilder hex = new StringBuilder("tvr");
        for (byte b : sha256(label + secret)) hex.append(String.format("%02x", b));
        return hex.substring(0, 43);
    }

    static byte[] sha256(String s) {
        try {
            return MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    /** base64url(iv || ciphertext || tag). */
    String seal(String plain) throws Exception {
        byte[] iv = new byte[12];
        new SecureRandom().nextBytes(iv);
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, iv));
        byte[] ct = c.doFinal(plain.getBytes(StandardCharsets.UTF_8));
        byte[] out = new byte[iv.length + ct.length];
        System.arraycopy(iv, 0, out, 0, iv.length);
        System.arraycopy(ct, 0, out, iv.length, ct.length);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(out);
    }

    /** The plain text, or null when the message was not sealed with our key. */
    String unseal(String sealed) {
        try {
            byte[] in = Base64.getUrlDecoder().decode(sealed.trim());
            if (in.length < 12 + 16) return null;
            Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
            c.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, in, 0, 12));
            return new String(c.doFinal(in, 12, in.length - 12), StandardCharsets.UTF_8);
        } catch (Exception e) {
            return null;
        }
    }

    public void start() {
        Thread t = new Thread(this::listen, "relay");
        t.setDaemon(true);
        t.start();
    }

    public void stop() {
        stopped = true;
        HttpURLConnection c = open;
        if (c != null) c.disconnect();
    }

    /** Listens for commands until stopped, reconnecting whenever the stream ends. */
    private void listen() {
        long wait = 5_000;
        while (!stopped) {
            try {
                stateIfDue();
                String since = memory.get("since");
                // First time: only what arrives from now on. After that: everything since the last one handled.
                URL url = new URL(base + commands + "/json" + (since == null || since.isEmpty() ? "" : "?since=" + since));
                HttpURLConnection c = (HttpURLConnection) url.openConnection();
                open = c;
                c.setConnectTimeout(15_000);
                c.setReadTimeout(120_000); // the relay sends a keep-alive line well within this
                try (BufferedReader in = new BufferedReader(new InputStreamReader(c.getInputStream(), StandardCharsets.UTF_8))) {
                    wait = 5_000;
                    String line;
                    while (!stopped && (line = in.readLine()) != null) {
                        if (!line.isEmpty()) event(new JSONObject(line));
                        stateIfDue();
                    }
                } finally {
                    c.disconnect();
                    open = null;
                }
            } catch (Exception e) {
                // no network, the TV waking up, the relay restarting: try again, backing off to a minute
            }
            if (stopped) return;
            try {
                Thread.sleep(wait);
            } catch (InterruptedException e) {
                return;
            }
            wait = Math.min(wait * 2, 60_000);
        }
    }

    private void event(JSONObject e) {
        if (!"message".equals(e.optString("event"))) return;
        String id = e.optString("id");
        try {
            String plain = unseal(e.optString("message"));
            if (plain != null && handle(new JSONObject(plain), System.currentTimeMillis())) publishState();
        } catch (Exception ignored) {
            // not ours, or malformed: drop it
        }
        if (!id.isEmpty()) memory.put("since", id);
    }

    /** Carries out one command. Returns whether the TV's list should be posted again. */
    boolean handle(JSONObject cmd, long now) throws Exception {
        String nonce = cmd.optString("id");
        long ts = cmd.optLong("ts");
        if (nonce.isEmpty() || Math.abs(now - ts) > MAX_AGE || seen(nonce)) return false;
        String op = cmd.optString("op");
        JSONObject data = cmd.optJSONObject("data");
        if (data == null) data = new JSONObject();
        TimeZone tz = TimeZone.getDefault();
        switch (op) {
            case "add":
                if (book.add(data, now, tz) != null) host.changed();
                return true;
            case "delete":
                if (book.remove(data.optString("rid"))) host.changed();
                return true;
            case "toggle":
                if (book.toggle(data.optString("rid"), now)) host.changed();
                return true;
            case "now":
                String text = data.optString("text", "").replaceAll("\\s+", " ").trim();
                if (text.length() > Book.MAX_TEXT) text = text.substring(0, Book.MAX_TEXT);
                String clip = Sounds.clean(data.optString("clip", ""));
                // A "show now" that sat on the relay while the TV was off is stale: only show a fresh one.
                if (!text.isEmpty() && Math.abs(now - ts) < 5 * 60_000) host.show(text, data.optBoolean("sound", false), clip == null ? "" : clip);
                return true;
            case "list":
                return true;
            default:
                return false;
        }
    }

    /** Whether this command id was handled before; remembers it if not. Keeps the last hundred. */
    private synchronized boolean seen(String nonce) throws Exception {
        String saved = memory.get("seen");
        JSONArray a = saved == null || saved.isEmpty() ? new JSONArray() : new JSONArray(saved);
        List<String> ids = new ArrayList<>();
        for (int i = 0; i < a.length(); i++) ids.add(a.getString(i));
        if (ids.contains(nonce)) return true;
        ids.add(nonce);
        while (ids.size() > 100) ids.remove(0);
        memory.put("seen", new JSONArray(ids).toString());
        return false;
    }

    /**
     * Posts the list when the relay has no recent copy. The relay allows a limited number of messages a day, so a
     * connection that keeps dropping must not post on every reconnect: a failed post is retried after ten minutes.
     */
    private void stateIfDue() {
        long now = System.currentTimeMillis();
        if (now - statePosted > STATE_EVERY && now - stateTried > 10 * 60_000) publishState();
    }

    /** Posts the TV's list for the phone. Runs on the caller's thread: never call it from the main thread. */
    public synchronized void publishState() {
        try {
            long now = System.currentTimeMillis();
            stateTried = now;
            TimeZone tz = TimeZone.getDefault();
            JSONArray all = book.toJson(now, tz);
            // Short keys and as many reminders as fit in one relay message, newest last.
            String sealed = null;
            for (int keep = all.length(); keep >= 0; keep--) {
                JSONArray items = new JSONArray();
                for (int i = all.length() - keep; i < all.length(); i++) {
                    JSONObject r = all.getJSONObject(i);
                    items.put(new JSONObject().put("i", r.getString("id")).put("t", r.getString("text")).put("m", r.getInt("minute"))
                            .put("o", r.getInt("mode")).put("d", r.getInt("days")).put("a", r.getString("date"))
                            .put("s", r.getBoolean("sound") ? 1 : 0).put("c", r.getString("clip")).put("e", r.getBoolean("enabled") ? 1 : 0));
                }
                String plain = new JSONObject().put("v", 1).put("ts", now).put("offset", tz.getOffset(now) / 60000)
                        .put("items", items).put("more", all.length() - keep).put("sounds", new JSONArray(sounds.list())).toString();
                sealed = seal(plain);
                if (sealed.length() <= MAX_MESSAGE) break;
                sealed = null;
            }
            if (sealed == null) return;
            HttpURLConnection c = (HttpURLConnection) new URL(base + state).openConnection();
            c.setConnectTimeout(15_000);
            c.setReadTimeout(15_000);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            try (OutputStream out = c.getOutputStream()) {
                out.write(sealed.getBytes(StandardCharsets.UTF_8));
            }
            if (c.getResponseCode() == 200) statePosted = now;
            c.disconnect();
        } catch (Exception ignored) {
            // posted again on the next change or reconnect
        }
    }
}
