package com.modmase.dialog;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
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
 * Pure-native Java MODMASE / MIKASA dialog.
 * No XML layouts and no external Android libraries.
 */
public final class MIKASA {

    private static final String PREFS = "modmase_dialog";
    private static final String JOINED_KEY = "telegram_joined";
    private static final String TELEGRAM_HANDLE = "MODMASE";
    private static final String TELEGRAM_URL = "https://t.me/MODMASE";

    private static final int CREAM = Color.rgb(245, 240, 229);
    private static final int BLACK = Color.rgb(23, 21, 21);
    private static final int CHARCOAL = Color.rgb(47, 42, 40);
    private static final int RED = Color.rgb(173, 46, 68);
    private static final int RED_DARK = Color.rgb(139, 33, 52);
    private static final int MUTED = Color.rgb(117, 109, 101);
    private static final int FOOTER = Color.rgb(151, 143, 134);
    private static final int BORDER = Color.argb(42, 23, 21, 21);

    private static final int IMAGE_WIDTH = 1200;
    private static final int IMAGE_HEIGHT = 675;

    private MIKASA() {
        // Utility class.
    }

    /** Show the dialog unless the user has already joined Telegram. */
    public static void show(final Activity activity) {
        if (activity == null || activity.isFinishing()) {
            return;
        }

        SharedPreferences prefs = activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        if (prefs.getBoolean(JOINED_KEY, false)) {
            return;
        }

        final Dialog dialog = new Dialog(activity);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(false);
        dialog.setCanceledOnTouchOutside(false);

        // ----- Root container -----
        FrameLayout root = new FrameLayout(activity);
        root.setPadding(dp(activity, 12), 0, dp(activity, 12), 0);
        root.setBackgroundColor(Color.TRANSPARENT);

        // ----- Card -----
        final LinearLayout card = new LinearLayout(activity);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setGravity(Gravity.CENTER_HORIZONTAL);
        card.setClipToOutline(true);
        card.setElevation(dp(activity, 10));
        card.setBackground(rounded(activity, CREAM, 25, 1, Color.argb(55, 255, 255, 255)));

        FrameLayout.LayoutParams cardParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        cardParams.gravity = Gravity.CENTER;
        root.addView(card, cardParams);

        // ----- Image + accent line -----
        FrameLayout imageFrame = new FrameLayout(activity);
        imageFrame.setBackgroundColor(Color.rgb(37, 33, 31));

        final AspectImageView imageView = new AspectImageView(activity);
        imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
        imageView.setImageResource(android.R.color.transparent);

        try (InputStream input = activity.getAssets().open("mikasa.png")) {
            android.graphics.Bitmap bitmap = android.graphics.BitmapFactory.decodeStream(input);
            imageView.setImageBitmap(bitmap);
        } catch (Exception ignored) {
            // Keep the image area instead of crashing the app.
        }

        FrameLayout.LayoutParams imageParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        imageFrame.addView(imageView, imageParams);

        View accent = new View(activity);
        accent.setBackground(rounded(activity, RED, 4, 0, Color.TRANSPARENT));
        FrameLayout.LayoutParams accentParams = new FrameLayout.LayoutParams(
                dp(activity, 65),
                dp(activity, 4)
        );
        accentParams.gravity = Gravity.BOTTOM | Gravity.START;
        accentParams.leftMargin = dp(activity, 42);
        imageFrame.addView(accent, accentParams);

        LinearLayout.LayoutParams imageFrameParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(activity, 220)
        );
        card.addView(imageFrame, imageFrameParams);

        // ----- Content -----
        LinearLayout content = new LinearLayout(activity);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(activity, 24), dp(activity, 22), dp(activity, 24), dp(activity, 20));
        card.addView(content, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        Typeface titleFont = loadFont(activity, "fonts/MikasaTitle.otf", Typeface.SERIF);
        Typeface bodyFont = loadFont(activity, "fonts/MikasaBody.ttf", Typeface.DEFAULT);
        Typeface bodyBoldFont = loadFont(activity, "fonts/MikasaBodyBold.ttf", Typeface.DEFAULT_BOLD);

        // ----- Eyebrow -----
        TextView welcome = text(activity, "WELCOME", RED, 10, bodyBoldFont);
        welcome.setGravity(Gravity.CENTER);
        welcome.setLetterSpacing(0.26f);
        content.addView(welcome);

        // ----- Title -----
        TextView title = text(activity, "MODMASE", BLACK, 42, titleFont);
        title.setGravity(Gravity.CENTER);
        title.setLetterSpacing(0.07f);
        title.setIncludeFontPadding(true);

        LinearLayout.LayoutParams titleParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        titleParams.topMargin = dp(activity, 2);
        content.addView(title, titleParams);

        // ----- Description -----
        TextView description = text(
                activity,
                "Discover updates, resources and creative content from MODMASE. "
                        + "Join our Telegram community and stay connected with the latest releases.",
                MUTED,
                13.5f,
                bodyFont
        );
        description.setGravity(Gravity.CENTER);
        description.setLineSpacing(0, 1.38f);
        description.setPadding(dp(activity, 2), 0, dp(activity, 2), 0);
        description.setMaxLines(4);

        LinearLayout.LayoutParams descriptionParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        descriptionParams.topMargin = dp(activity, 10);
        descriptionParams.bottomMargin = dp(activity, 20);
        content.addView(description, descriptionParams);

        // ----- Buttons -----
        LinearLayout buttons = new LinearLayout(activity);
        buttons.setOrientation(LinearLayout.HORIZONTAL);
        buttons.setGravity(Gravity.CENTER);
        buttons.setWeightSum(2f);
        content.addView(buttons, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(activity, 50)
        ));

        Button exitButton = button(activity, "EXIT", CHARCOAL, bodyBoldFont);
        exitButton.setBackground(rounded(activity, Color.TRANSPARENT, 13, 1, BORDER));
        exitButton.setStateListAnimator(null);
        exitButton.setAllCaps(false);

        LinearLayout.LayoutParams exitParams = new LinearLayout.LayoutParams(0, dp(activity, 50), 0.8f);
        exitParams.rightMargin = dp(activity, 5);
        buttons.addView(exitButton, exitParams);

        Button telegramButton = button(activity, "JOIN TELEGRAM", Color.WHITE, bodyBoldFont);
        telegramButton.setBackground(rounded(activity, RED, 13, 0, Color.TRANSPARENT));
        telegramButton.setStateListAnimator(null);
        telegramButton.setAllCaps(false);
        telegramButton.setElevation(dp(activity, 3));

        LinearLayout.LayoutParams telegramParams = new LinearLayout.LayoutParams(0, dp(activity, 50), 1.2f);
        telegramParams.leftMargin = dp(activity, 5);
        buttons.addView(telegramButton, telegramParams);

        // ----- Footer -----
        TextView footer = text(activity, "MODMASE COMMUNITY", FOOTER, 8.5f, bodyBoldFont);
        footer.setGravity(Gravity.CENTER);
        footer.setLetterSpacing(0.20f);
        LinearLayout.LayoutParams footerParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        footerParams.topMargin = dp(activity, 17);
        content.addView(footer, footerParams);

        // ----- Button actions -----
        exitButton.setOnClickListener(v -> {
            press(v);
            v.postDelayed(() -> {
                if (!activity.isFinishing()) {
                    activity.finishAffinity();
                    if (Build.VERSION.SDK_INT >= 21) {
                        activity.finishAndRemoveTask();
                    }
                }
            }, 110);
        });

        telegramButton.setOnClickListener(v -> {
            press(v);

            // Save BEFORE launching Telegram/browser so the dialog stays hidden next time.
            prefs.edit().putBoolean(JOINED_KEY, true).apply();

            v.postDelayed(() -> {
                openTelegram(activity);
                dialog.dismiss();
            }, 110);
        });

        // ----- Dialog window -----
        dialog.setContentView(root);
        dialog.setOnShowListener(d -> {
            Window window = dialog.getWindow();
            if (window == null) {
                return;
            }

            window.setBackgroundDrawableResource(android.R.color.transparent);
            window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);

            WindowManager.LayoutParams lp = window.getAttributes();
            lp.dimAmount = 0.56f;
            window.setAttributes(lp);

            int screenWidth = activity.getResources().getDisplayMetrics().widthPixels;
            int maxWidth = dp(activity, 470);
            int width = Math.min(maxWidth, (int) (screenWidth * 0.88f));
            window.setLayout(width, WindowManager.LayoutParams.WRAP_CONTENT);

            // Exact 1200:675 image ratio.
            imageView.post(() -> {
                int w = imageFrame.getWidth();
                if (w > 0) {
                    int h = Math.round(w * ((float) IMAGE_HEIGHT / IMAGE_WIDTH));
                    ViewGroup.LayoutParams lp2 = imageView.getLayoutParams();
                    lp2.height = h;
                    imageView.setLayoutParams(lp2);
                    ViewGroup.LayoutParams fp = imageFrame.getLayoutParams();
                    fp.height = h;
                    imageFrame.setLayoutParams(fp);
                }
            });

            // Soft entrance animation.
            card.setAlpha(0f);
            card.setScaleX(0.94f);
            card.setScaleY(0.94f);
            card.setTranslationY(dp(activity, 30));
            card.animate()
                    .alpha(1f)
                    .scaleX(1f)
                    .scaleY(1f)
                    .translationY(0f)
                    .setDuration(620)
                    .setInterpolator(new DecelerateInterpolator(1.8f))
                    .start();

            imageView.setAlpha(0f);
            imageView.setScaleX(1.07f);
            imageView.setScaleY(1.07f);
            imageView.animate()
                    .alpha(1f)
                    .scaleX(1.02f)
                    .scaleY(1.02f)
                    .setDuration(900)
                    .setInterpolator(new DecelerateInterpolator(1.5f))
                    .start();

            animateIn(welcome, 180, 8);
            animateIn(title, 240, 12);
            animateIn(description, 320, 10);
            animateIn(buttons, 390, 10);
            animateIn(footer, 480, 8);
        });

        dialog.show();
    }

    private static void openTelegram(Activity activity) {
        try {
            Intent tg = new Intent(Intent.ACTION_VIEW, Uri.parse("tg://resolve?domain=" + TELEGRAM_HANDLE));
            activity.startActivity(tg);
            return;
        } catch (Exception ignored) {
            // Telegram app not installed or tg:// unsupported. Fallback to browser.
        }

        try {
            Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse(TELEGRAM_URL));
            activity.startActivity(web);
        } catch (Exception ignored) {
            // No browser available.
        }
    }

    private static void press(View view) {
        view.animate()
                .scaleX(0.96f)
                .scaleY(0.96f)
                .setDuration(70)
                .withEndAction(() -> view.animate()
                        .scaleX(1f)
                        .scaleY(1f)
                        .setDuration(90)
                        .start())
                .start();
    }

    private static void animateIn(View view, long delay, float translationDp) {
        view.setAlpha(0f);
        view.setTranslationY(view.getResources().getDisplayMetrics().density * translationDp);
        view.animate()
                .alpha(1f)
                .translationY(0f)
                .setStartDelay(delay)
                .setDuration(450)
                .setInterpolator(new DecelerateInterpolator(1.4f))
                .start();
    }

    private static TextView text(Context context, String value, int color, float size, Typeface typeface) {
        TextView t = new TextView(context);
        t.setText(value);
        t.setTextColor(color);
        t.setTextSize(size);
        t.setTypeface(typeface);
        return t;
    }

    private static Button button(Context context, String value, int color, Typeface typeface) {
        Button b = new Button(context);
        b.setText(value);
        b.setTextColor(color);
        b.setTextSize(11);
        b.setTypeface(typeface);
        b.setGravity(Gravity.CENTER);
        b.setPadding(0, 0, 0, 0);
        b.setMinHeight(0);
        b.setMinWidth(0);
        return b;
    }

    private static Typeface loadFont(Context context, String path, Typeface fallback) {
        try {
            return Typeface.createFromAsset(context.getAssets(), path);
        } catch (Exception e) {
            return fallback;
        }
    }

    private static GradientDrawable rounded(Context context, int color, float radiusDp, int strokeWidth, int strokeColor) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(dp(context, radiusDp));
        if (strokeWidth > 0) {
            drawable.setStroke(dp(context, strokeWidth), strokeColor);
        }
        return drawable;
    }

    private static int dp(Context context, float value) {
        return (int) (value * context.getResources().getDisplayMetrics().density + 0.5f);
    }

    /** Simple 16:9 ImageView helper with no XML. */
    private static final class AspectImageView extends ImageView {
        AspectImageView(Context context) {
            super(context);
        }
    }
}
