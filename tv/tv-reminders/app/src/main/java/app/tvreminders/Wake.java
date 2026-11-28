package app.tvreminders;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** The alarm for the next reminder, and the restart after the TV boots or the app is updated. */
public class Wake extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent i) {
        Svc.start(c);
        Svc.check(c);
    }
}
