package com.modmase.dialog;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.view.animation.DecelerateInterpolator;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.InputStream;

/**
 * Native Java recreation of the MODMASE / Mikasa HTML dialog.
 * No XML layout and no third-party dependencies are used.
 */
public class MIKASA extends Dialog {

    private static final int CREAM = Color.rgb(238, 231, 216);
    private static final int PAPER = Color.rgb(245, 240, 229);
    private static final int BLACK = Color.rgb(23, 21, 21);
    private static final int CHARCOAL = Color.rgb(40, 35, 35);
    private static final int RED = Color.rgb(168, 47, 67);
    private static final int RED_DARK = Color.rgb(129, 38, 56);
    private static final int MUTED = Color.rgb(117, 109, 101);
    private static final int FOOTER = Color.rgb(154, 145, 135);

    private final Activity activity;
    private LinearLayout card;
    private boolean closing;

    public MIKASA(Activity activity) {
        super(activity);
        this.activity = activity;
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setCanceledOnTouchOutside(true);
    }

    @Override
    protected void onCreate(android.os.Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildDialog();
    }

    private void buildDialog() {
        final Context context = activity;
        final int cardWidth = getCardWidth();
        final int imageHeight = Math.round(cardWidth * 675f / 1200f);

        FrameLayout outer = new FrameLayout(context);
        outer.setPadding(dp(18), 0, dp(18), 0);
        outer.setBackgroundColor(Color.TRANSPARENT);

        card = new LinearLayout(context);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setGravity(Gravity.CENTER_HORIZONTAL);
        card.setBackground(roundRect(PAPER, 25, Color.argb(89, 255, 255, 255), 1));
        card.setElevation(dp(10));

        if (Build.VERSION.SDK_INT >= 21) {
            card.setClipToOutline(true);
        }

        // IMAGE -------------------------------------------------------------
        FrameLayout imageBox = new FrameLayout(context);
        imageBox.setBackgroundColor(Color.rgb(36, 32, 30));

        ImageView image = new ImageView(context);
        image.setScaleType(ImageView.ScaleType.CENTER_CROP);
        Bitmap bitmap = loadAssetBitmap("mikasa.png");
        if (bitmap != null) {
            image.setImageBitmap(bitmap);
        }
        imageBox.addView(image, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        // Soft dark fade at the bottom of the image.
        View imageFade = new View(context);
        android.graphics.drawable.GradientDrawable fade = new android.graphics.drawable.GradientDrawable(
                android.graphics.drawable.GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{Color.argb(0, 0, 0, 0), Color.argb(82, 0, 0, 0)});
        imageFade.setBackground(fade);
        imageBox.addView(imageFade, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        // Crimson accent line.
        View accent = new View(context);
        GradientDrawable accentBg = roundRect(RED, 4, 0, 0);
        accent.setBackground(accentBg);
        FrameLayout.LayoutParams accentParams = new FrameLayout.LayoutParams(dp(65), dp(4));
        accentParams.gravity = Gravity.BOTTOM | Gravity.START;
        accentParams.leftMargin = dp(24);
        imageBox.addView(accent, accentParams);

        card.addView(imageBox, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, imageHeight));

        // CONTENT -----------------------------------------------------------
        LinearLayout content = new LinearLayout(context);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(25), dp(22), dp(25), dp(20));

        TextView eyebrow = textView("WELCOME", RED, 10, Typeface.BOLD);
        eyebrow.setGravity(Gravity.CENTER);
        eyebrow.setLetterSpacing(0.28f);
        content.addView(eyebrow, wrapParams());

        TextView title = textView("MODMASE", BLACK, 43, Typeface.BOLD);
        title.setGravity(Gravity.CENTER);
        title.setTypeface(Typeface.create("serif", Typeface.BOLD));
        title.setLetterSpacing(0.08f);
        content.addView(title, wrapParams());

        TextView description = textView(
                "Discover updates, resources and creative content from MODMASE. " +
                "Join our Telegram community and stay connected with the latest releases.",
                MUTED,
                13,
                Typeface.NORMAL);
        description.setGravity(Gravity.CENTER);
        description.setLineSpacing(0f, 1.55f);
        LinearLayout.LayoutParams descriptionParams = wrapParams();
        descriptionParams.topMargin = dp(12);
        descriptionParams.bottomMargin = dp(21);
        descriptionParams.width = dp(365);
        content.addView(description, descriptionParams);

        LinearLayout buttons = new LinearLayout(context);
        buttons.setOrientation(LinearLayout.HORIZONTAL);
        buttons.setGravity(Gravity.CENTER);

        Button exit = makeButton("EXIT", Color.TRANSPARENT, CHARCOAL, Color.argb(35, 23, 21, 21), false);
        Button telegram = makeButton("JOIN TELEGRAM", RED, Color.WHITE, RED, true);

        LinearLayout.LayoutParams exitParams = new LinearLayout.LayoutParams(0, dp(50), 0.8f);
        exitParams.rightMargin = dp(5);
        buttons.addView(exit, exitParams);

        LinearLayout.LayoutParams telegramParams = new LinearLayout.LayoutParams(0, dp(50), 1.2f);
        telegramParams.leftMargin = dp(5);
        buttons.addView(telegram, telegramParams);

        content.addView(buttons, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(50)));

        TextView footer = textView("MODMASE COMMUNITY", FOOTER, 9, Typeface.BOLD);
        footer.setGravity(Gravity.CENTER);
        footer.setLetterSpacing(0.18f);
        LinearLayout.LayoutParams footerParams = wrapParams();
        footerParams.topMargin = dp(17);
        content.addView(footer, footerParams);

        card.addView(content, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        outer.addView(card, new FrameLayout.LayoutParams(cardWidth, FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.CENTER));
        setContentView(outer);

        Window window = getWindow();
        if (window != null) {
            window.setBackgroundDrawableResource(android.R.color.transparent);
            WindowManager.LayoutParams lp = window.getAttributes();
            lp.width = WindowManager.LayoutParams.MATCH_PARENT;
            lp.height = WindowManager.LayoutParams.WRAP_CONTENT;
            lp.dimAmount = 0.58f;
            window.setAttributes(lp);
            window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        }

        // Soft opening animation, matching the HTML's staged motion.
        card.setAlpha(0f);
        card.setScaleX(0.94f);
        card.setScaleY(0.94f);
        card.setTranslationY(dp(30));

        image.setAlpha(0f);
        image.setScaleX(1.08f);
        image.setScaleY(1.08f);

        animateIn(card, 0, 650);
        animateImage(image, 80, 900);
        animateIn(eyebrow, 220, 450);
        animateIn(title, 280, 500);
        animateIn(description, 360, 450);
        animateIn(buttons, 430, 450);
        animateIn(footer, 520, 400);

        exit.setOnClickListener(v -> dismissWithAnimation());
        telegram.setOnClickListener(v -> openTelegram());

        setOnCancelListener(dialog -> {
            if (!closing) {
                dismissWithAnimation();
            }
        });
    }

    @Override
    public void show() {
        super.show();
        Window window = getWindow();
        if (window != null) {
            WindowManager.LayoutParams lp = window.getAttributes();
            lp.width = WindowManager.LayoutParams.MATCH_PARENT;
            lp.height = WindowManager.LayoutParams.WRAP_CONTENT;
            window.setAttributes(lp);
        }
    }

    private void openTelegram() {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://t.me/MODMASE"));
            activity.startActivity(intent);
        } catch (Exception ignored) {
            // No compatible handler installed.
        }
    }

    private void dismissWithAnimation() {
        if (closing || !isShowing()) {
            return;
        }
        closing = true;

        card.animate()
                .alpha(0f)
                .scaleX(0.97f)
                .scaleY(0.97f)
                .translationY(dp(15))
                .setDuration(250)
                .setInterpolator(new DecelerateInterpolator(1.4f))
                .withEndAction(this::dismiss)
                .start();
    }

    private void animateIn(View view, long delay, long duration) {
        view.setAlpha(0f);
        view.setTranslationY(dp(10));
        view.animate()
                .alpha(1f)
                .translationY(0f)
                .setStartDelay(delay)
                .setDuration(duration)
                .setInterpolator(new DecelerateInterpolator(1.6f))
                .start();
    }

    private void animateImage(View view, long delay, long duration) {
        view.animate()
                .alpha(1f)
                .scaleX(1.02f)
                .scaleY(1.02f)
                .setStartDelay(delay)
                .setDuration(duration)
                .setInterpolator(new DecelerateInterpolator(1.5f))
                .start();
    }

    private TextView textView(String text, int color, float size, int style) {
        TextView tv = new TextView(activity);
        tv.setText(text);
        tv.setTextColor(color);
        tv.setTextSize(size);
        tv.setTypeface(Typeface.create("sans-serif", style));
        return tv;
    }

    private Button makeButton(String text, int bgColor, int textColor, int strokeColor, boolean filled) {
        Button button = new Button(activity);
        button.setText(text);
        button.setTextColor(textColor);
        button.setTextSize(11);
        button.setTypeface(Typeface.create("sans-serif", Typeface.BOLD));
        button.setAllCaps(false);
        button.setGravity(Gravity.CENTER);
        button.setPadding(0, 0, 0, 0);
        button.setLetterSpacing(0.12f);

        GradientDrawable bg = roundRect(bgColor, 13, strokeColor, filled ? 0 : 1);
        if (!filled) {
            bg.setStroke(dp(1), strokeColor);
        }
        button.setBackground(bg);
        button.setStateListAnimator(null);

        // Small press animation; the HTML version uses scale(0.96).
        button.setOnTouchListener((v, event) -> {
            switch (event.getActionMasked()) {
                case android.view.MotionEvent.ACTION_DOWN:
                    v.animate().scaleX(0.96f).scaleY(0.96f).setDuration(90).start();
                    break;
                case android.view.MotionEvent.ACTION_UP:
                case android.view.MotionEvent.ACTION_CANCEL:
                    v.animate().scaleX(1f).scaleY(1f).setDuration(140).start();
                    break;
                default:
                    break;
            }
            return false;
        });

        return button;
    }

    private GradientDrawable roundRect(int fill, float radiusDp, int strokeColor, int strokeWidthDp) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(fill);
        drawable.setCornerRadius(dp(radiusDp));
        if (strokeWidthDp > 0) {
            drawable.setStroke(dp(strokeWidthDp), strokeColor);
        }
        return drawable;
    }

    private LinearLayout.LayoutParams wrapParams() {
        return new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    private Bitmap loadAssetBitmap(String name) {
        try (InputStream input = activity.getAssets().open(name)) {
            return BitmapFactory.decodeStream(input);
        } catch (Exception e) {
            return null;
        }
    }

    private int getCardWidth() {
        int screenWidth = activity.getResources().getDisplayMetrics().widthPixels;
        int maxWidth = dp(470);
        int safeWidth = screenWidth - dp(36);
        return Math.max(dp(280), Math.min(maxWidth, safeWidth));
    }

    private int dp(float value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
