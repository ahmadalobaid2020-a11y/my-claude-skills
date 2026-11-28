package app.tvreminders;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.TimeZone;

/**
 * The phone page: a tiny web server on the home network. No password, so anyone on the same Wi-Fi can add or
 * remove reminders. Nothing here uses Android, so it also runs on a desktop JVM for testing.
 */
public class Web {
    public interface Host {
        /** The reminders changed: set the next alarm again. */
        void changed();

        /** Show this text on the TV right now, with the stored clip if one is named, else beeps if sound is set. */
        void show(String text, boolean sound, String clip);

        /** The PIN the phone page must send, or empty when the page is open to the whole home network. */
        String pin();

        /** The secret of the "away from home" link, or empty while that is switched off. */
        String remote();
    }

    public static final int PORT = 8090;
    private static final int MAX_BODY = 8192;
    /** After this many wrong PINs in a row, every request is refused for LOCK_MS. */
    static final int MAX_WRONG = 5;
    static final long LOCK_MS = 60_000;
    private int wrong;
    private long lockedUntil;

    private final Book book;
    private final Sounds sounds;
    private final Host host;
    private final byte[] page;
    private ServerSocket server;

    public Web(Book book, Sounds sounds, Host host, byte[] page) {
        this.book = book;
        this.sounds = sounds;
        this.host = host;
        this.page = page;
    }

    public void start(int port) throws Exception {
        server = new ServerSocket(port);
        Thread t = new Thread(() -> {
            while (!server.isClosed()) {
                try {
                    Socket s = server.accept();
                    new Thread(() -> serve(s), "web-client").start();
                } catch (Exception e) {
                    if (server.isClosed()) return;
                }
            }
        }, "web");
        t.setDaemon(true);
        t.start();
    }

    public void stop() {
        try {
            server.close();
        } catch (Exception ignored) {
        }
    }

    private void serve(Socket s) {
        try (Socket sock = s) {
            sock.setSoTimeout(8000);
            InputStream in = sock.getInputStream();
            String head = readHead(in);
            if (head == null) return;
            String[] lines = head.split("\r\n");
            String[] first = lines[0].split(" ");
            if (first.length < 2) return;
            int length = 0;
            for (String l : lines) {
                if (l.toLowerCase(java.util.Locale.ROOT).startsWith("content-length:")) length = Integer.parseInt(l.substring(15).trim());
            }
            String sent = "";
            for (String l : lines) {
                if (l.toLowerCase(java.util.Locale.ROOT).startsWith("x-pin:")) sent = l.substring(6).trim();
            }
            if (first[1].startsWith("/api/")) {
                int gate = gate(sent);
                if (gate != 200) {
                    // Answer before reading the body, so a locked-out client cannot make the TV buffer uploads.
                    json(sock, gate, new JSONObject().put("ok", false).put("pin", true));
                    return;
                }
            }
            boolean upload = first[0].equals("POST") && first[1].startsWith("/api/sound?");
            if (length < 0 || length > (upload ? Sounds.MAX_BYTES : MAX_BODY)) {
                reply(sock, 413, "text/plain", "too large".getBytes(StandardCharsets.UTF_8));
                return;
            }
            byte[] body = new byte[length];
            for (int got = 0; got < length; ) {
                int n = in.read(body, got, length - got);
                if (n < 0) return;
                got += n;
            }
            try {
                if (upload) {
                    String saved = sounds.save(param(first[1].substring(first[1].indexOf('?') + 1), "name"), body);
                    json(sock, saved != null ? 200 : 400, new JSONObject().put("ok", saved != null).put("name", saved == null ? "" : saved));
                    return;
                }
                route(sock, first[0], first[1], new String(body, StandardCharsets.UTF_8));
            } catch (org.json.JSONException e) {
                reply(sock, 400, "text/plain", "bad request".getBytes(StandardCharsets.UTF_8));
            }
        } catch (Exception ignored) {
            // a client that hangs up or sends rubbish is not worth more than this
        }
    }

    /** 200 when the request may go on, 401 for a missing or wrong PIN, 429 while locked out. */
    private synchronized int gate(String sent) {
        String pin = host.pin();
        if (pin == null || pin.isEmpty()) return 200;
        long now = System.currentTimeMillis();
        if (now < lockedUntil) return 429;
        if (java.security.MessageDigest.isEqual(pin.getBytes(StandardCharsets.UTF_8), sent.getBytes(StandardCharsets.UTF_8))) {
            wrong = 0;
            return 200;
        }
        if (!sent.isEmpty() && ++wrong >= MAX_WRONG) {
            wrong = 0;
            lockedUntil = now + LOCK_MS;
        }
        return 401;
    }

    private void route(Socket sock, String method, String target, String body) throws Exception {
        String path = target, query = "";
        int q = target.indexOf('?');
        if (q >= 0) {
            path = target.substring(0, q);
            query = target.substring(q + 1);
        }
        long now = System.currentTimeMillis();
        TimeZone tz = TimeZone.getDefault();
        boolean post = method.equals("POST");
        if (method.equals("GET") && path.equals("/")) {
            reply(sock, 200, "text/html; charset=utf-8", page);
        } else if (method.equals("GET") && path.equals("/api/list")) {
            json(sock, 200, new JSONObject().put("now", now).put("offset", tz.getOffset(now) / 60000).put("remote", host.remote()).put("items", book.toJson(now, tz))
                    .put("sounds", new org.json.JSONArray(sounds.list())));
        } else if (post && path.equals("/api/sound/delete")) {
            boolean ok = sounds.delete(param(query, "name"));
            json(sock, ok ? 200 : 404, new JSONObject().put("ok", ok));
        } else if (post && path.equals("/api/add")) {
            Rem r = book.add(new JSONObject(body), now, tz);
            if (r != null) host.changed();
            json(sock, r != null ? 200 : 400, new JSONObject().put("ok", r != null));
        } else if (post && path.equals("/api/delete")) {
            boolean ok = book.remove(param(query, "id"));
            if (ok) host.changed();
            json(sock, ok ? 200 : 404, new JSONObject().put("ok", ok));
        } else if (post && path.equals("/api/toggle")) {
            boolean ok = book.toggle(param(query, "id"), now);
            if (ok) host.changed();
            json(sock, ok ? 200 : 404, new JSONObject().put("ok", ok));
        } else if (post && path.equals("/api/now")) {
            JSONObject o = new JSONObject(body);
            String text = o.optString("text", "").replaceAll("\\s+", " ").trim();
            if (text.length() > Book.MAX_TEXT) text = text.substring(0, Book.MAX_TEXT);
            String clip = Sounds.clean(o.optString("clip", ""));
            if (!text.isEmpty()) host.show(text, o.optBoolean("sound", false), clip == null ? "" : clip);
            json(sock, text.isEmpty() ? 400 : 200, new JSONObject().put("ok", !text.isEmpty()));
        } else {
            reply(sock, 404, "text/plain", "not found".getBytes(StandardCharsets.UTF_8));
        }
    }

    private static String param(String query, String name) throws Exception {
        for (String kv : query.split("&")) {
            int eq = kv.indexOf('=');
            if (eq > 0 && kv.substring(0, eq).equals(name)) return URLDecoder.decode(kv.substring(eq + 1), "UTF-8");
        }
        return "";
    }

    private static String readHead(InputStream in) throws Exception {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        int state = 0, c;
        while (b.size() < 8192 && (c = in.read()) >= 0) {
            b.write(c);
            state = (c == '\r' && (state == 0 || state == 2)) || (c == '\n' && (state == 1 || state == 3)) ? state + 1 : (c == '\r' ? 1 : 0);
            if (state == 4) return b.toString("ISO-8859-1");
        }
        return null;
    }

    private static void json(Socket s, int code, JSONObject o) throws Exception {
        reply(s, code, "application/json; charset=utf-8", o.toString().getBytes(StandardCharsets.UTF_8));
    }

    private static void reply(Socket s, int code, String type, byte[] body) throws Exception {
        OutputStream out = s.getOutputStream();
        out.write(("HTTP/1.1 " + code + " X\r\nContent-Type: " + type + "\r\nContent-Length: " + body.length
                + "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n").getBytes(StandardCharsets.ISO_8859_1));
        out.write(body);
        out.flush();
    }
}
