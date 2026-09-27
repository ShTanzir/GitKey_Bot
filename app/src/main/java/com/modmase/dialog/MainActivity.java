package com.modmase.dialog;

import android.app.Activity;
import android.os.Bundle;

public class MainActivity extends Activity {

    private MIKASA mikasa;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // MainActivity is only the hook. The entire dialog UI lives in MIKASA.java.
        mikasa = new MIKASA(this);
        mikasa.show();
    }
}
