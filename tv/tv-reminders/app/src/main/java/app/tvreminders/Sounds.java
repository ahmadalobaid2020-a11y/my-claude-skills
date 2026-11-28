package app.tvreminders;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/** Sound files sent from the phone and kept on the TV, to play with a reminder. No Android types. */
public class Sounds {
    public static final int MAX_BYTES = 8 * 1024 * 1024, MAX_FILES = 20;
    private static final List<String> TYPES = Arrays.asList("mp3", "m4a", "aac", "wav", "ogg", "oga", "opus", "flac", "amr", "3gp");

    private final File dir;

    public Sounds(File dir) {
        this.dir = dir;
        dir.mkdirs();
    }

    /**
     * A safe file name made from what the phone sent: letters, digits, spaces, dash and underscore, plus a known
     * audio extension. Null when it is not an audio file name we accept. Nothing here can leave the folder.
     */
    public static String clean(String name) {
        if (name == null) return null;
        int dot = name.lastIndexOf('.');
        if (dot <= 0) return null;
        String ext = name.substring(dot + 1).toLowerCase(Locale.ROOT);
        if (!TYPES.contains(ext)) return null;
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < dot && b.length() < 40; ) {
            int cp = name.codePointAt(i);
            i += Character.charCount(cp);
            if (Character.isLetterOrDigit(cp) || cp == ' ' || cp == '-' || cp == '_') b.appendCodePoint(cp);
        }
        String base = b.toString().trim();
        return base.isEmpty() ? null : base + "." + ext;
    }

    /**
     * The name on disk: the clean name in URL-safe base64, plus its extension. Plain ASCII, so a stored sound
     * never depends on how the file system encodes Arabic names.
     */
    private static String disk(String clean) {
        String ext = clean.substring(clean.lastIndexOf('.'));
        return java.util.Base64.getUrlEncoder().withoutPadding().encodeToString(clean.getBytes(java.nio.charset.StandardCharsets.UTF_8)) + ext;
    }

    public synchronized List<String> list() {
        List<String> out = new ArrayList<>();
        String[] names = dir.list();
        if (names == null) return out;
        for (String n : names) {
            int dot = n.lastIndexOf('.');
            if (dot <= 0) continue;
            try {
                String name = new String(java.util.Base64.getUrlDecoder().decode(n.substring(0, dot)), java.nio.charset.StandardCharsets.UTF_8);
                if (name.equals(clean(name)) && disk(name).equals(n)) out.add(name);
            } catch (IllegalArgumentException ignored) {
                // not one of ours
            }
        }
        java.util.Collections.sort(out);
        return out;
    }

    /** The stored file for this name, or null if there is none. */
    public synchronized File file(String name) {
        String n = clean(name);
        if (n == null || !n.equals(name)) return null;
        File f = new File(dir, disk(n));
        return f.isFile() ? f : null;
    }

    /** Stores a sound. Returns the name it was stored under, or null when refused. */
    public synchronized String save(String name, byte[] data) {
        String n = clean(name);
        if (n == null || data.length == 0 || data.length > MAX_BYTES) return null;
        File f = new File(dir, disk(n));
        if (!f.exists() && list().size() >= MAX_FILES) return null;
        try (FileOutputStream out = new FileOutputStream(f)) {
            out.write(data);
        } catch (Exception e) {
            f.delete();
            return null;
        }
        return n;
    }

    public synchronized boolean delete(String name) {
        File f = file(name);
        return f != null && f.delete();
    }
}
