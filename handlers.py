import asyncio
import io
import os
from telegram import Update, InputFile
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

import config
import crypto_utils
from file_utils import TempFileManager, ApkInspector
from keyboards import (
    main_menu_keyboard, wizard_nav_keyboard, confirm_keystore_keyboard,
    result_keyboard, tools_menu_keyboard, settings_keyboard
)
from keystore import KeystoreConfig, KeystoreGenerator, KeystoreInspector
from security import rate_limiter, sanitize_filename, logger
from storage import session_manager


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command / main menu."""
    user = update.effective_user
    if not user:
        return

    if not rate_limiter.is_allowed(user.id):
        await update.message.reply_text("⚠️ Rate limit reached. Please wait a moment before trying again.")
        return

    session_manager.reset_session(user.id)

    welcome_text = (
        f"👋 Welcome <b>{user.first_name}</b> to <b>GitKey Bot</b>!\n\n"
        "<b>GitKey</b> is a lightweight developer utility for Android developers and modders. "
        "Create Android signing keystores and prepare <b>GitHub Actions Secrets</b> for automated APK/AAB builds.\n\n"
        "🔒 <b>Security First:</b>\n"
        "• All keystore files are generated locally in temporary memory.\n"
        "• Passwords and private keys are NEVER logged or stored on our servers.\n"
        "• Temporary files are automatically purged after download.\n\n"
        "Select an action below to get started:"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard()
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help & Security instructions."""
    help_text = (
        "<b>GitKey Bot Help & Safety Manual</b>\n"
        "------------------------------------\n\n"
        "🔑 <b>How to Create a Signing Key:</b>\n"
        "1. Tap <b>Create Keystore</b> from the main menu.\n"
        "2. Enter your Project Name (e.g. <code>MyApp</code>).\n"
        "3. Specify or auto-generate secure passwords.\n"
        "4. Tap <b>BUILD KEYSTORE</b>.\n"
        "5. Receive your <code>.jks</code> file and 4 GitHub Actions Secrets:\n"
        "   • <code>KEYSTORE_BASE64</code>\n"
        "   • <code>KEYSTORE_PASSWORD</code>\n"
        "   • <code>KEY_ALIAS</code>\n"
        "   • <code>KEY_PASSWORD</code>\n\n"
        "🐙 <b>GitHub Actions Integration:</b>\n"
        "In your GitHub repository go to: <b>Settings → Secrets and variables → Actions</b>, and add the four secret keys above.\n\n"
        "🛠️ <b>Available Commands:</b>\n"
        "• /start - Main Menu\n"
        "• /menu - Return to Main Menu\n"
        "• /tools - Developer Tools\n"
        "• /help - Help & Safety Manual\n"
        "• /cancel - Immediately cancel active workflow"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard()
        )


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global cancellation command."""
    user = update.effective_user
    if user:
        session_manager.reset_session(user.id)
    
    msg = "❌ Workflow cancelled. Returning to main menu."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg, reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(msg, reply_markup=main_menu_keyboard())


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query router."""
    query = update.callback_query
    if not query or not query.data:
        return

    user = update.effective_user
    if not user:
        return

    data = query.data
    await query.answer()

    session = session_manager.get_session(user.id)

    # Global Navigation Callbacks
    if data == "btn_main_menu" or data == "wiz_cancel":
        session_manager.reset_session(user.id)
        await cmd_start(update, context)
        return

    if data == "btn_help":
        await cmd_help(update, context)
        return

    if data == "btn_github_actions":
        await show_github_guide(update, context)
        return

    if data == "btn_settings":
        await show_settings(update, context)
        return

    if data == "btn_my_keys":
        await show_my_keys(update, context)
        return

    if data == "btn_tools":
        await show_tools_menu(update, context)
        return

    # Create Keystore Wizard Callbacks
    if data == "btn_create_keystore":
        session.current_state = "WIZARD"
        session.wizard_step = "PROJECT_NAME"
        session.draft_config = KeystoreConfig()
        # Default secure passwords
        auto_pass = crypto_utils.generate_secure_password(16)
        session.draft_config.store_password = auto_pass
        session.draft_config.key_password = auto_pass

        text = (
            "<b>Create Signing Key (Step 1 of 5)</b>\n"
            "------------------------------------\n\n"
            "Please type your <b>Project Name</b> (e.g. <code>MyApp</code> or <code>GameTitle</code>):\n"
            "<i>This will determine default filenames and aliases.</i>"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=wizard_nav_keyboard(is_first=True))
        return

    if data == "wiz_skip":
        await advance_wizard_step(update, context, skipped=True)
        return

    if data == "wiz_back":
        await regress_wizard_step(update, context)
        return

    if data == "wiz_build_now":
        await build_keystore_workflow(update, context)
        return

    # Result Actions
    if data == "res_copy_all":
        await send_copy_all_secrets(update, context)
        return

    if data == "res_toggle_hide":
        session.hide_secrets = not session.hide_secrets
        await show_result_screen(update, context)
        return

    if data == "res_download_jks":
        await download_jks_file(update, context)
        return

    if data == "res_download_env":
        await download_env_file(update, context)
        return

    # Settings Toggles
    if data == "sett_toggle_hide":
        session.hide_secrets = not session.hide_secrets
        await show_settings(update, context)
        return

    if data == "sett_toggle_confirm":
        session.confirm_before_export = not session.confirm_before_export
        await show_settings(update, context)
        return

    if data == "sett_clean_temp":
        TempFileManager.cleanup_expired_temp_files()
        await query.message.reply_text("🧹 Temporary files cleaned up!")
        await show_settings(update, context)
        return

    # Tool Callbacks
    if data.startswith("tool_"):
        await handle_tool_selection(update, context, data)
        return


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Router for user text inputs during wizards or tools."""
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    session = session_manager.get_session(user.id)

    if session.current_state == "WIZARD":
        await process_wizard_input(update, context, text)
        return

    if session.current_state == "TOOL_WAITING_INPUT":
        await process_tool_text_input(update, context, text)
        return


async def process_wizard_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Processes user input during the Create Keystore wizard."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    step = session.wizard_step

    if step == "PROJECT_NAME":
        session.draft_config.project_name = text
        session.draft_config.alias = sanitize_filename(text, "myapp")
        session.wizard_step = "ALIAS"

        msg = (
            f"<b>Create Signing Key (Step 2 of 5)</b>\n"
            f"Project Name: <code>{session.draft_config.project_name}</code>\n\n"
            f"Key Alias (Default: <code>{session.draft_config.alias}</code>):\n"
            f"<i>Type a custom alias or tap Skip to keep default.</i>"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=wizard_nav_keyboard(can_skip=True))

    elif step == "ALIAS":
        session.draft_config.alias = sanitize_filename(text, session.draft_config.alias)
        session.wizard_step = "STORE_PASS"

        msg = (
            f"<b>Create Signing Key (Step 3 of 5)</b>\n"
            f"Key Alias: <code>{session.draft_config.alias}</code>\n\n"
            f"Keystore Password (Default Generated: <code>{session.draft_config.store_password}</code>):\n"
            f"<i>Type your own custom password or tap Skip to keep the secure generated password.</i>"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=wizard_nav_keyboard(can_skip=True))

    elif step == "STORE_PASS":
        session.draft_config.store_password = text
        session.draft_config.key_password = text
        session.wizard_step = "CONFIRM"
        await show_wizard_confirmation(update, context)


async def advance_wizard_step(update: Update, context: ContextTypes.DEFAULT_TYPE, skipped: bool = False):
    """Advances wizard when user taps Skip."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    step = session.wizard_step

    if step == "ALIAS":
        session.wizard_step = "STORE_PASS"
        msg = (
            f"<b>Create Signing Key (Step 3 of 5)</b>\n"
            f"Key Alias: <code>{session.draft_config.alias}</code>\n\n"
            f"Keystore Password (Default Generated: <code>{session.draft_config.store_password}</code>):\n"
            f"<i>Type your custom password or tap Skip to keep the secure generated password.</i>"
        )
        await update.callback_query.edit_message_text(msg, parse_mode=ParseMode.HTML, reply_markup=wizard_nav_keyboard(can_skip=True))

    elif step == "STORE_PASS":
        session.wizard_step = "CONFIRM"
        await show_wizard_confirmation(update, context)


async def regress_wizard_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Goes back one step in the wizard."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    step = session.wizard_step

    if step == "ALIAS":
        session.wizard_step = "PROJECT_NAME"
        text = (
            "<b>Create Signing Key (Step 1 of 5)</b>\n"
            "------------------------------------\n\n"
            "Please type your <b>Project Name</b> (e.g. <code>MyApp</code>):"
        )
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=wizard_nav_keyboard(is_first=True))

    elif step == "STORE_PASS":
        session.wizard_step = "ALIAS"
        msg = (
            f"<b>Create Signing Key (Step 2 of 5)</b>\n"
            f"Project Name: <code>{session.draft_config.project_name}</code>\n\n"
            f"Key Alias (Default: <code>{session.draft_config.alias}</code>):"
        )
        await update.callback_query.edit_message_text(msg, parse_mode=ParseMode.HTML, reply_markup=wizard_nav_keyboard(can_skip=True))


async def show_wizard_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows final configuration confirmation summary (NO plain passwords shown)."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    cfg = session.draft_config

    summary = (
        "<b>Confirm Keystore Configuration</b>\n"
        "------------------------------------\n"
        f"<b>Project Name:</b> <code>{cfg.project_name}</code>\n"
        f"<b>Key Alias:</b> <code>{cfg.alias}</code>\n"
        f"<b>Algorithm:</b> <code>{cfg.algorithm} ({cfg.key_size} bits)</code>\n"
        f"<b>Validity:</b> <code>{cfg.validity_years} years</code>\n"
        f"<b>Filename:</b> <code>{sanitize_filename(cfg.project_name, 'upload_key')}-release.jks</code>\n"
        f"<b>Passwords:</b> <code>[Secure Password Set]</code>\n\n"
        "Ready to generate your Android signing keystore?"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(summary, parse_mode=ParseMode.HTML, reply_markup=confirm_keystore_keyboard())
    else:
        await update.message.reply_text(summary, parse_mode=ParseMode.HTML, reply_markup=confirm_keystore_keyboard())


async def build_keystore_workflow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes real keystore generation with progress updates."""
    query = update.callback_query
    user = update.effective_user
    session = session_manager.get_session(user.id)

    # Animated progress updates
    msg = await query.edit_message_text("⏳ <i>Generating signing key pair…</i>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    await msg.edit_text("⏳ <i>Creating self-signed X.509 certificate…</i>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    await msg.edit_text("⏳ <i>Encoding PKCS12 keystore to Base64…</i>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    await msg.edit_text("⏳ <i>Preparing GitHub Actions Secrets…</i>", parse_mode=ParseMode.HTML)

    try:
        result = KeystoreGenerator.generate(session.draft_config)
        session.last_result = result
        session_manager.add_history(user.id, result)
        await show_result_screen(update, context)
    except Exception as e:
        logger.error(f"Keystore Generation Failure: {e}")
        await msg.edit_text(f"❌ <b>Keystore Generation Failed:</b> {str(e)}", parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard())


async def show_result_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays generated GitHub Actions secrets."""
    query = update.callback_query
    user = update.effective_user
    session = session_manager.get_session(user.id)
    res = session.last_result

    if not res:
        return

    hide = session.hide_secrets

    b64_val = res.base64_secret if not hide else "••••••••••••••••••••••••••••••••••••••••"
    store_pass_val = res.store_password if not hide else "••••••••••••••••"
    key_pass_val = res.key_password if not hide else "••••••••••••••••"

    text = (
        "✅ <b>Keystore Ready!</b>\n"
        "Your GitHub Actions signing credentials have been generated.\n\n"
        f"<b>1. KEYSTORE_BASE64:</b>\n<code>{b64_val[:100]}...</code>\n\n"
        f"<b>2. KEYSTORE_PASSWORD:</b>\n<code>{store_pass_val}</code>\n\n"
        f"<b>3. KEY_ALIAS:</b>\n<code>{res.alias}</code>\n\n"
        f"<b>4. KEY_PASSWORD:</b>\n<code>{key_pass_val}</code>\n\n"
        f"<b>SHA-256 Fingerprint:</b>\n<code>{res.sha256_fingerprint}</code>"
    )

    if query:
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=result_keyboard(hide_secrets=hide))


async def send_copy_all_secrets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a copyable block with all 4 secrets."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    res = session.last_result

    if not res:
        return

    secrets_block = (
        f"KEYSTORE_BASE64={res.base64_secret}\n"
        f"KEYSTORE_PASSWORD={res.store_password}\n"
        f"KEY_ALIAS={res.alias}\n"
        f"KEY_PASSWORD={res.key_password}"
    )

    msg = (
        "📋 <b>GitHub Actions Secrets (Tap to copy full block):</b>\n\n"
        f"<code>{secrets_block}</code>\n\n"
        "⚠️ <i>Warning: Keep these credentials safe and never commit them publicly.</i>"
    )

    await update.callback_query.message.reply_text(msg, parse_mode=ParseMode.HTML)


async def download_jks_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the actual .jks binary file."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    res = session.last_result

    if not res:
        return

    bio = io.BytesIO(res.keystore_bytes)
    bio.name = res.filename

    warning_text = (
        "⚠️ <b>Sensitive Credentials Warning:</b>\n"
        "This <code>.jks</code> file contains your private signing key. "
        "Store it securely and do NOT upload it to public version control."
    )
    await update.callback_query.message.reply_text(warning_text, parse_mode=ParseMode.HTML)
    await update.callback_query.message.reply_document(document=InputFile(bio, filename=res.filename))


async def download_env_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the github_secrets.env text file."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    res = session.last_result

    if not res:
        return

    env_content = (
        f"# GitHub Actions Signing Secrets for {res.project_name}\n"
        f"KEYSTORE_BASE64={res.base64_secret}\n"
        f"KEYSTORE_PASSWORD={res.store_password}\n"
        f"KEY_ALIAS={res.alias}\n"
        f"KEY_PASSWORD={res.key_password}\n"
    )

    bio = io.BytesIO(env_content.encode('utf-8'))
    env_filename = f"{sanitize_filename(res.project_name, 'secrets')}-github.env"

    await update.callback_query.message.reply_document(document=InputFile(bio, filename=env_filename))


async def show_my_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays saved key metadata history."""
    user = update.effective_user
    history = session_manager.get_history(user.id)

    if not history:
        text = "<b>My Keys (History)</b>\n--------------------\nNo key metadata saved yet. Tap <b>Create Keystore</b> to generate one!"
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard())
        return

    lines = ["<b>Saved Key Metadata (Safe View)</b>", "------------------------------------"]
    for item in history:
        date_str = time.strftime('%Y-%m-%d %H:%M', time.gmtime(item.timestamp))
        lines.append(
            f"• <b>{item.project_name}</b> (Alias: <code>{item.alias}</code>)\n"
            f"  File: <code>{item.filename}</code> | Date: {date_str}\n"
            f"  SHA-256: <code>{item.sha256_fingerprint[:20]}...</code>"
        )

    lines.append("\n🔒 <i>Note: Plaintext passwords are never stored in history.</i>")
    await update.callback_query.edit_message_text("\n\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard())


async def show_tools_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays developer utilities menu."""
    text = (
        "<b>🛠️ Developer Utilities</b>\n"
        "--------------------------\n"
        "Select an offline developer utility from the options below:"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())


async def handle_tool_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, tool_id: str):
    """Handles selection of developer tools."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    session.active_tool = tool_id
    session.current_state = "TOOL_WAITING_INPUT"

    if tool_id == "tool_pwd_gen":
        pwd = crypto_utils.generate_secure_password(20)
        text = f"🎲 <b>Generated Secure Password:</b>\n<code>{pwd}</code>"
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())
        session.current_state = "MAIN_MENU"

    elif tool_id == "tool_uuid_gen":
        u = crypto_utils.generate_uuid_v4()
        text = f"🆔 <b>Generated Random UUID v4:</b>\n<code>{u}</code>"
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())
        session.current_state = "MAIN_MENU"

    elif tool_id in ("tool_b64_encode", "tool_b64_decode", "tool_sha256", "tool_sha1", "tool_md5", "tool_json_fmt", "tool_secrets_fmt"):
        prompts = {
            "tool_b64_encode": "🔤 Please paste the text or upload the file you wish to encode to Base64:",
            "tool_b64_decode": "🔓 Please paste the Base64 string you wish to decode:",
            "tool_sha256": "🛡️ Please paste text or upload a file to calculate SHA-256 hash:",
            "tool_sha1": "🔒 Please paste text or upload a file to calculate SHA-1 hash:",
            "tool_md5": "⚡ Please paste text or upload a file to calculate MD5 checksum:",
            "tool_json_fmt": "✨ Please paste the raw JSON text you wish to format:",
            "tool_secrets_fmt": "🐙 Please paste KEY=VALUE text to format for GitHub Actions:"
        }
        await update.callback_query.edit_message_text(prompts[tool_id], parse_mode=ParseMode.HTML)

    elif tool_id == "tool_keystore_inspect":
        await update.callback_query.edit_message_text("🔍 Please upload your <code>.jks</code> or <code>.p12</code> keystore file:", parse_mode=ParseMode.HTML)

    elif tool_id == "tool_apk_inspect":
        await update.callback_query.edit_message_text("📦 Please upload the <code>.apk</code> file you wish to inspect:", parse_mode=ParseMode.HTML)


async def process_tool_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Processes text input for active tool."""
    user = update.effective_user
    session = session_manager.get_session(user.id)
    tool = session.active_tool

    if tool == "tool_b64_encode":
        res = crypto_utils.encode_base64(text.encode('utf-8'))
        await update.message.reply_text(f"<b>Base64 Output:</b>\n<code>{res}</code>", parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    elif tool == "tool_b64_decode":
        ok, res, msg = crypto_utils.decode_base64(text)
        if ok:
            await update.message.reply_text(f"<b>Decoded Text:</b>\n<code>{res.decode('utf-8', errors='ignore')}</code>", parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())
        else:
            await update.message.reply_text(f"❌ {msg}", parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    elif tool in ("tool_sha256", "tool_sha1", "tool_md5"):
        alg = tool.replace("tool_", "").upper()
        h = crypto_utils.calculate_hash(text.encode('utf-8'), alg)
        await update.message.reply_text(f"<b>{alg} Hash:</b>\n<code>{h}</code>", parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    elif tool == "tool_json_fmt":
        ok, formatted = crypto_utils.format_json(text)
        await update.message.reply_text(f"<b>Formatted JSON:</b>\n<code>{formatted}</code>", parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    elif tool == "tool_secrets_fmt":
        lines = text.split("\n")
        out = ["# Formatted GitHub Actions Secrets:"]
        for line in lines:
            if "=" in line:
                k, v = line.split("=", 1)
                out.append(f"{k.strip().upper()}={v.strip()}")
        await update.message.reply_text("\n".join(out), parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    session.current_state = "MAIN_MENU"


async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes uploaded document files (keystores, APKs, files for hashes)."""
    user = update.effective_user
    doc = update.message.document
    if not user or not doc:
        return

    session = session_manager.get_session(user.id)
    tool = session.active_tool

    if doc.file_size > config.MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(f"❌ File exceeds maximum allowed size of {config.MAX_FILE_SIZE_MB}MB.")
        return

    file_obj = await doc.get_file()
    downloaded_bytes = await file_obj.download_as_bytearray()

    if tool == "tool_apk_inspect":
        ok, result = ApkInspector.inspect_apk(bytes(downloaded_bytes))
        await update.message.reply_text(result, parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    elif tool == "tool_keystore_inspect":
        # Prompt password
        session.temp_file_bytes = bytes(downloaded_bytes)
        session.current_state = "TOOL_WAITING_KEYSTORE_PASS"
        await update.message.reply_text("🔑 Keystore uploaded! Type the <b>Keystore Password</b> to inspect details:", parse_mode=ParseMode.HTML)
        return

    elif tool in ("tool_sha256", "tool_sha1", "tool_md5"):
        alg = tool.replace("tool_", "").upper()
        h = crypto_utils.calculate_hash(bytes(downloaded_bytes), alg)
        await update.message.reply_text(f"<b>File {alg} Hash:</b>\n<code>{h}</code>", parse_mode=ParseMode.HTML, reply_markup=tools_menu_keyboard())

    session.current_state = "MAIN_MENU"


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays settings panel."""
    user = update.effective_user
    session = session_manager.get_session(user.id)

    text = (
        "<b>⚙️ GitKey Bot Settings</b>\n"
        "--------------------------\n"
        f"• Hide Secrets by Default: <b>{'ON' if session.hide_secrets else 'OFF'}</b>\n"
        f"• Warning Dialog: <b>{'ON' if session.confirm_before_export else 'OFF'}</b>\n"
    )

    kb = settings_keyboard(session.hide_secrets, session.confirm_before_export)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


async def show_github_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays GitHub Actions setup guide."""
    guide = (
        "<b>🐙 GitHub Actions Integration Guide</b>\n"
        "-------------------------------------\n\n"
        "<b>1. Add Repository Secrets:</b>\n"
        "Go to your GitHub repo → <b>Settings → Secrets and variables → Actions</b>, and add:\n"
        "• <code>KEYSTORE_BASE64</code>\n"
        "• <code>KEYSTORE_PASSWORD</code>\n"
        "• <code>KEY_ALIAS</code>\n"
        "• <code>KEY_PASSWORD</code>\n\n"
        "<b>2. Sample Workflow (.github/workflows/build.yml):</b>\n\n"
        "<code>"
        "name: Android Build & Sign\n"
        "on:\n"
        "  push:\n"
        "    branches: [ main ]\n\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - name: Set up JDK 17\n"
        "        uses: actions/setup-java@v4\n"
        "        with:\n"
        "          distribution: 'zulu'\n"
        "          java-version: '17'\n\n"
        "      - name: Decode Keystore\n"
        "        run: |\n"
        "          echo \"${{ secrets.KEYSTORE_BASE64 }}\" | base64 -d > release-key.jks\n\n"
        "      - name: Build Signed APK\n"
        "        run: ./gradlew assembleRelease\n"
        "        env:\n"
        "          KEYSTORE_PATH: release-key.jks\n"
        "          STORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}\n"
        "          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}\n"
        "          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}\n"
        "</code>"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(guide, parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(guide, parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard())
