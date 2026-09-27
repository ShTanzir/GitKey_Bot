package com.modmase.dialog;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.widget.FrameLayout;

/**
 * Hook activity. The dialog UI lives entirely inside MIKASA.java.
 */
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Minimal host view. In your real APK, keep your existing layout here.
        FrameLayout host = new FrameLayout(this);
        host.setBackgroundColor(Color.rgb(169, 167, 165));
        setContentView(host);

        MIKASA.show(this);
    }
}
