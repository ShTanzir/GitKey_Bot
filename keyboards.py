from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔑 Create Keystore", callback_data="btn_create_keystore"),
            InlineKeyboardButton("📂 My Keys", callback_data="btn_my_keys")
        ],
        [
            InlineKeyboardButton("🛠️ Developer Tools", callback_data="btn_tools"),
            InlineKeyboardButton("🐙 GitHub Actions", callback_data="btn_github_actions")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="btn_settings"),
            InlineKeyboardButton("❓ Help & Safety", callback_data="btn_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def wizard_nav_keyboard(can_skip: bool = False, is_first: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    if not is_first:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data="wiz_back"))
    if can_skip:
        buttons.append(InlineKeyboardButton("⏭️ Skip", callback_data="wiz_skip"))
    
    buttons.append(InlineKeyboardButton("❌ Cancel", callback_data="wiz_cancel"))
    return InlineKeyboardMarkup([buttons, [InlineKeyboardButton("🏠 Main Menu", callback_data="btn_main_menu")]])


def confirm_keystore_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🚀 BUILD KEYSTORE", callback_data="wiz_build_now")],
        [
            InlineKeyboardButton("✏️ Edit Project Name", callback_data="wiz_edit_project"),
            InlineKeyboardButton("⚙️ Edit Advanced", callback_data="wiz_edit_advanced")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="wiz_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def result_keyboard(hide_secrets: bool = True) -> InlineKeyboardMarkup:
    toggle_label = "👁️ Show Secrets" if hide_secrets else "🙈 Hide Secrets"
    keyboard = [
        [
            InlineKeyboardButton("📋 Copy All Secrets", callback_data="res_copy_all"),
            InlineKeyboardButton(toggle_label, callback_data="res_toggle_hide")
        ],
        [
            InlineKeyboardButton("📥 Download .jks File", callback_data="res_download_jks"),
            InlineKeyboardButton("📄 Download Secrets .env", callback_data="res_download_env")
        ],
        [
            InlineKeyboardButton("🐙 GitHub Actions Guide", callback_data="btn_github_actions"),
            InlineKeyboardButton("🔄 Regenerate", callback_data="btn_create_keystore")
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="btn_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def tools_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔑 Keystore Generator", callback_data="tool_keystore_gen"),
            InlineKeyboardButton("🔍 Keystore Inspector", callback_data="tool_keystore_inspect")
        ],
        [
            InlineKeyboardButton("🔤 Base64 Encoder", callback_data="tool_b64_encode"),
            InlineKeyboardButton("🔓 Base64 Decoder", callback_data="tool_b64_decode")
        ],
        [
            InlineKeyboardButton("🛡️ SHA-256 Generator", callback_data="tool_sha256"),
            InlineKeyboardButton("🔒 SHA-1 Generator", callback_data="tool_sha1")
        ],
        [
            InlineKeyboardButton("⚡ MD5 Generator", callback_data="tool_md5"),
            InlineKeyboardButton("📄 File Checksum Utility", callback_data="tool_checksum")
        ],
        [
            InlineKeyboardButton("📦 APK Cert Inspector", callback_data="tool_apk_inspect"),
            InlineKeyboardButton("🐙 Secrets Formatter", callback_data="tool_secrets_fmt")
        ],
        [
            InlineKeyboardButton("✨ JSON Formatter", callback_data="tool_json_fmt"),
            InlineKeyboardButton("🎲 Password Generator", callback_data="tool_pwd_gen")
        ],
        [
            InlineKeyboardButton("🆔 UUID Generator", callback_data="tool_uuid_gen"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="btn_main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_keyboard(hide_secrets: bool, confirm_export: bool) -> InlineKeyboardMarkup:
    hide_label = "👁️ Hide Secrets: ON" if hide_secrets else "👁️ Hide Secrets: OFF"
    confirm_label = "🛡️ Warning Dialog: ON" if confirm_export else "🛡️ Warning Dialog: OFF"

    keyboard = [
        [InlineKeyboardButton(hide_label, callback_data="sett_toggle_hide")],
        [InlineKeyboardButton(confirm_label, callback_data="sett_toggle_confirm")],
        [InlineKeyboardButton("🧹 Clean Temporary Files", callback_data="sett_clean_temp")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="btn_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
