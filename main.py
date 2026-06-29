import os
import logging
from datetime import datetime
from typing import Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Try to import googletrans, fallback to simple translation if not available
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# ==================== CONFIGURATION ====================

# Get bot token from environment variable
TOKEN = os.environ.get("TOKEN") or os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ No TOKEN found! Please set TOKEN environment variable.")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==================== CONSTANTS ====================

# Supported languages
LANGUAGES = {
    "en": "🇬🇧 English",
    "es": "🇪🇸 Spanish",
    "fr": "🇫🇷 French",
    "de": "🇩🇪 German",
    "it": "🇮🇹 Italian",
    "pt": "🇵🇹 Portuguese",
    "ru": "🇷🇺 Russian",
    "zh-cn": "🇨🇳 Chinese (Simplified)",
    "zh-tw": "🇹🇼 Chinese (Traditional)",
    "ja": "🇯🇵 Japanese",
    "ko": "🇰🇷 Korean",
    "ar": "🇸🇦 Arabic",
    "hi": "🇮🇳 Hindi",
    "bn": "🇧🇩 Bengali",
    "ur": "🇵🇰 Urdu",
    "fa": "🇮🇷 Persian",
    "tr": "🇹🇷 Turkish",
    "nl": "🇳🇱 Dutch",
    "sv": "🇸🇪 Swedish",
    "pl": "🇵🇱 Polish",
    "uk": "🇺🇦 Ukrainian",
    "ro": "🇷🇴 Romanian",
    "el": "🇬🇷 Greek",
    "he": "🇮🇱 Hebrew",
    "th": "🇹🇭 Thai",
    "vi": "🇻🇳 Vietnamese",
    "id": "🇮🇩 Indonesian",
    "ms": "🇲🇾 Malay",
    "fil": "🇵🇭 Filipino",
    "sw": "🇰🇪 Swahili",
    "am": "🇪🇹 Amharic",
}

# Store user data
USER_DATA: Dict[int, Dict[str, Any]] = {}

# ==================== BOT COMMANDS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    welcome_text = f"""
👋 **Hello {user.first_name}!**

Welcome to **TranslateNowBot** - Your Instant Language Translator! 🌍

🔄 **How to use:**
1. Send me any text
2. Choose your target language
3. I'll translate it instantly!

📝 **Supported Languages:**
• 30+ languages available
• Auto-detects source language
• Fast and accurate translations

📝 **Commands:**
/start - Show this message
/help - Get detailed help
/languages - Show all supported languages
/about - About this bot
/cancel - Cancel current operation

Let's get started! Send me some text to translate. 🚀
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = """
📖 **Help Guide - TranslateNowBot**

🔹 **How it works:**
1. Send any text to the chat
2. Choose your target language from the buttons
3. Get your translation instantly!

🎯 **Features:**
• **Text Translation** - Translate any text
• **Auto-detect** - Automatically detects source language
• **30+ Languages** - Wide range of supported languages
• **Inline Buttons** - Easy language selection
• **Fast & Free** - Unlimited translations

⚡ **Tips:**
• Maximum text length: 4000 characters
• Supports emojis and special characters
• Preserves text formatting
• Works with any language combination

❓ **Need help?**
Just send text and follow the prompts!

🔗 **Commands:**
/start - Welcome message
/help - This help guide
/languages - Show all languages
/about - Bot information
/cancel - Cancel current operation
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /languages command."""
    lang_list = "🌍 **Supported Languages:**\n\n"
    
    # Split languages into two columns
    lang_items = list(LANGUAGES.items())
    half = len(lang_items) // 2
    
    for i in range(half):
        code1, name1 = lang_items[i]
        code2, name2 = lang_items[i + half] if i + half < len(lang_items) else (None, None)
        
        if code2:
            lang_list += f"• `{code1}` - {name1}  |  • `{code2}` - {name2}\n"
        else:
            lang_list += f"• `{code1}` - {name1}\n"
    
    lang_list += "\n📝 **How to use:**\n"
    lang_list += "1. Send text → 2. Choose language → 3. Get translation!"
    
    await update.message.reply_text(lang_list, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    about_text = """
🤖 **TranslateNowBot v1.0**

🌍 **Your Instant Language Translator**

✨ **Features:**
• Translate between 30+ languages
• Auto-detect source language
• User-friendly inline buttons
• Fast and accurate translations
• Free and unlimited use
• Open source

🛠️ **Built with:**
• Python 3.11+
• python-telegram-bot
• Google Translate API

🚀 **Hosted on:** Railway

📅 **Created:** 2024

👨‍💻 **Open Source**
Contributions welcome on GitHub!

📢 **Send /start to begin!**
"""
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command to clear user data."""
    user_id = update.effective_user.id
    if user_id in USER_DATA:
        del USER_DATA[user_id]
        await update.message.reply_text("✅ **Operation cancelled.**\n\nSend new text to start over.", parse_mode="Markdown")
    else:
        await update.message.reply_text("ℹ️ No active operation to cancel.", parse_mode="Markdown")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❌ Unknown command.\n\n"
        "Use /start, /help, /languages, /about, or /cancel.\n"
        "Or just send me text to translate!",
        parse_mode="Markdown"
    )

# ==================== TEXT HANDLER ====================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check text length
    if len(text) > 4000:
        await update.message.reply_text(
            "❌ **Text too long!**\n\n"
            f"Your text has {len(text)} characters.\n"
            "Maximum allowed: 4000 characters.\n\n"
            "Please send a shorter text.",
            parse_mode="Markdown"
        )
        return
    
    # Store text in user data
    USER_DATA[user_id] = {
        "text": text,
        "source": "auto"
    }
    
    # Create inline keyboard for language selection
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es")],
        [InlineKeyboardButton("🇫🇷 French", callback_data="lang_fr"),
         InlineKeyboardButton("🇩🇪 German", callback_data="lang_de")],
        [InlineKeyboardButton("🇮🇹 Italian", callback_data="lang_it"),
         InlineKeyboardButton("🇵🇹 Portuguese", callback_data="lang_pt")],
        [InlineKeyboardButton("🇷🇺 Russian", callback_data="lang_ru"),
         InlineKeyboardButton("🇨🇳 Chinese", callback_data="lang_zh-cn")],
        [InlineKeyboardButton("🇯🇵 Japanese", callback_data="lang_ja"),
         InlineKeyboardButton("🇰🇷 Korean", callback_data="lang_ko")],
        [InlineKeyboardButton("🇸🇦 Arabic", callback_data="lang_ar"),
         InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton("🌍 More Languages", callback_data="more_languages")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Show preview of text
    preview = text[:100] + "..." if len(text) > 100 else text
    
    await update.message.reply_text(
        f"📝 **Text received!**\n\n"
        f"`{preview}`\n\n"
        f"🌍 **Select target language:**\n"
        f"(Source language will be auto-detected)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ==================== CALLBACK HANDLER ====================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    # Handle cancel
    if data == "cancel":
        if user_id in USER_DATA:
            del USER_DATA[user_id]
        await query.edit_message_text(
            "❌ **Translation cancelled.**\n\nSend new text to start over.",
            parse_mode="Markdown"
        )
        return
    
    # Handle more languages
    if data == "more_languages":
        keyboard = [
            [InlineKeyboardButton("🇹🇷 Turkish", callback_data="lang_tr"),
             InlineKeyboardButton("🇳🇱 Dutch", callback_data="lang_nl")],
            [InlineKeyboardButton("🇸🇪 Swedish", callback_data="lang_sv"),
             InlineKeyboardButton("🇵🇱 Polish", callback_data="lang_pl")],
            [InlineKeyboardButton("🇺🇦 Ukrainian", callback_data="lang_uk"),
             InlineKeyboardButton("🇷🇴 Romanian", callback_data="lang_ro")],
            [InlineKeyboardButton("🇬🇷 Greek", callback_data="lang_el"),
             InlineKeyboardButton("🇮🇱 Hebrew", callback_data="lang_he")],
            [InlineKeyboardButton("🇹🇭 Thai", callback_data="lang_th"),
             InlineKeyboardButton("🇻🇳 Vietnamese", callback_data="lang_vi")],
            [InlineKeyboardButton("🇮🇩 Indonesian", callback_data="lang_id"),
             InlineKeyboardButton("🇲🇾 Malay", callback_data="lang_ms")],
            [InlineKeyboardButton("🇵🇭 Filipino", callback_data="lang_fil"),
             InlineKeyboardButton("🇰🇪 Swahili", callback_data="lang_sw")],
            [InlineKeyboardButton("🇪🇹 Amharic", callback_data="lang_am")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 **More Languages:**\n\nSelect a target language:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    
    # Handle back
    if data == "back":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
             InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es")],
            [InlineKeyboardButton("🇫🇷 French", callback_data="lang_fr"),
             InlineKeyboardButton("🇩🇪 German", callback_data="lang_de")],
            [InlineKeyboardButton("🇮🇹 Italian", callback_data="lang_it"),
             InlineKeyboardButton("🇵🇹 Portuguese", callback_data="lang_pt")],
            [InlineKeyboardButton("🇷🇺 Russian", callback_data="lang_ru"),
             InlineKeyboardButton("🇨🇳 Chinese", callback_data="lang_zh-cn")],
            [InlineKeyboardButton("🇯🇵 Japanese", callback_data="lang_ja"),
             InlineKeyboardButton("🇰🇷 Korean", callback_data="lang_ko")],
            [InlineKeyboardButton("🇸🇦 Arabic", callback_data="lang_ar"),
             InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
            [InlineKeyboardButton("🌍 More Languages", callback_data="more_languages")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 **Select target language:**\n\n(Source language will be auto-detected)",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    
    # Handle language selection
    if data.startswith("lang_"):
        target_lang = data.replace("lang_", "")
        user_id = update.effective_user.id
        
        # Check if user has text
        if user_id not in USER_DATA:
            await query.edit_message_text(
                "⚠️ **No text found!**\n\nPlease send text first.",
                parse_mode="Markdown"
            )
            return
        
        user_info = USER_DATA[user_id]
        text = user_info["text"]
        source = user_info.get("source", "auto")
        
        # Get language names
        target_name = LANGUAGES.get(target_lang, target_lang)
        source_name = "Auto-detected" if source == "auto" else LANGUAGES.get(source, source)
        
        # Update message to show processing
        await query.edit_message_text(
            f"🔄 **Translating...**\n\n"
            f"From: `{source_name}`\n"
            f"To: `{target_name}`\n\n"
            f"⏳ Please wait...",
            parse_mode="Markdown"
        )
        
        try:
            # Perform translation
            if TRANSLATOR_AVAILABLE:
                translator = Translator()
                
                # Perform translation
                if source == "auto":
                    translation = translator.translate(text, dest=target_lang)
                else:
                    translation = translator.translate(text, src=source, dest=target_lang)
                
                translated_text = translation.text
                detected_source = translation.src if source == "auto" else source
                
            else:
                # Fallback: Simple mock translation if googletrans not installed
                translated_text = f"[Translated to {target_name}] {text}"
                detected_source = "unknown"
                
                # Provide installation instructions
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="ℹ️ **Note:** For real translations, install googletrans:\n`pip install googletrans==4.0.0-rc1`",
                    parse_mode="Markdown"
                )
            
            # Send translation result
            result_text = (
                f"✅ **Translation Complete!**\n\n"
                f"📂 **Original:**\n`{text[:500]}{'...' if len(text) > 500 else ''}`\n\n"
                f"🌍 **Translated ({target_name}):**\n`{translated_text[:500]}{'...' if len(translated_text) > 500 else ''}`\n\n"
                f"📝 **From:** `{LANGUAGES.get(detected_source, detected_source).replace('🇨🇳 Chinese (Simplified)', 'Chinese') if detected_source != 'unknown' else 'Unknown'}`\n"
                f"📝 **To:** `{target_name}`"
            )
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                parse_mode="Markdown"
            )
            
            # Clean up user data
            if user_id in USER_DATA:
                del USER_DATA[user_id]
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"❌ **Translation Failed!**\n\n"
                    f"Error: `{str(e)}`\n\n"
                    f"Please try again with a different language or text.\n"
                    f"Tip: Make sure the text is not too long or empty."
                ),
                parse_mode="Markdown"
            )

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "❌ **An error occurred!**\n\n"
                "Please try again later.\n"
                "If the issue persists, send /cancel and try again."
            ),
            parse_mode="Markdown"
        )

# ==================== MAIN FUNCTION ====================

def main() -> None:
    """Start the bot."""
    logger.info("🚀 Starting TranslateNowBot...")
    
    if not TRANSLATOR_AVAILABLE:
        logger.warning("⚠️ googletrans not installed. Using fallback translation.")
    
    # Build application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Add message handler for text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot is running and listening for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
