import os
import logging
import subprocess
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters

# 1. Konfiguration & Logging
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("gemini_bot.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def log_action(action_type, details):
    logger.info(f"[{action_type.upper()}] {details}")

# 2. Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
AVAILABLE_MODELS = {
    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 2.0 Pro (Exp)": "gemini-2.0-pro-exp-02-05"
}
current_model_code = "gemini-2.0-flash"
pending_changes = {}

# 3. Tools für Gemini
def list_files(directory="."):
    """Listet Dateien im Projekt auf."""
    log_action("FILE_LIST", f"Scanning directory: {directory}")
    try:
        return "\n".join([f for f in os.listdir(directory) if not f.startswith('.')])
    except Exception as e: return str(e)

def read_file(filepath):
    """Liest Dateiinhalte."""
    log_action("FILE_READ", f"Reading: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: return str(e)

def write_file_request(filepath, content):
    """Bereitet Datei-Schreiben vor."""
    log_action("WRITE_REQUEST", f"Request for: {filepath}")
    pending_changes[filepath] = content
    return f"REQUEST_CONFIRMATION:{filepath}"

def run_git(command_type, message=None):
    """Führt Git-Befehle aus."""
    log_action("GIT", f"Command: {command_type}")
    try:
        if command_type == 'status': return subprocess.check_output(['git', 'status']).decode()
        if command_type == 'diff': return subprocess.check_output(['git', 'diff']).decode()
        if command_type == 'commit_push' and message:
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', message], check=True)
            subprocess.run(['git', 'push'], check=True)
            return "✅ Successfully committed and pushed!"
    except Exception as e: return f"Git Error: {str(e)}"

tools_list = [list_files, read_file, write_file_request, run_git]
model = genai.GenerativeModel(model_name=current_model_code, tools=tools_list)
chat_session = model.start_chat(enable_automatic_function_calling=True)

# 4. Telegram Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID: return
    await update.message.reply_text("🚀 Gemini Code Bot online. Sende mir eine Nachricht oder nutze /settings.")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"set_model|{code}")] for name, code in AVAILABLE_MODELS.items()]
    await update.message.reply_text(f"Aktuelles Modell: `{current_model_code}`\nWähle ein Modell:", 
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID: return
    log_action("USER_MSG", f"Received message of length {len(update.message.text)}")
    
    try:
        response = await chat_session.send_message_async(update.message.text)
        usage = response.usage_metadata
        stats = f"\n\n📊 `In: {usage.prompt_token_count} | Out: {usage.candidates_token_count} | Total: {usage.total_token_count}`"

        if "REQUEST_CONFIRMATION:" in response.text:
            filepath = response.text.split("REQUEST_CONFIRMATION:")[1].strip()
            content = pending_changes.get(filepath)
            keyboard = [[InlineKeyboardButton("✅ Schreiben", callback_data=f"write_yes|{filepath}"),
                         InlineKeyboardButton("❌ Abbrechen", callback_data="write_no")]]
            await update.message.reply_text(f"Gemini möchte `{filepath}` ändern:\n```python\n{content}\n```", 
                                          reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            await update.message.reply_text(response.text + stats, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Fehler: {str(e)}")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_session, current_model_code
    query = update.callback_query
    await query.answer()

    if query.data.startswith("set_model|"):
        current_model_code = query.data.split("|")[1]
        new_model = genai.GenerativeModel(model_name=current_model_code, tools=tools_list)
        chat_session = new_model.start_chat(enable_automatic_function_calling=True)
        await query.edit_message_text(f"✅ Modell gewechselt auf `{current_model_code}`")

    elif query.data.startswith("write_yes"):
        filepath = query.data.split("|")[1]
        content = pending_changes.pop(filepath, None)
        if content:
            with open(filepath, "w", encoding="utf-8") as f: f.write(content)
            log_action("FILE_WRITE", f"Success: {filepath}")
            await query.edit_message_text(f"✅ Datei `{filepath}` wurde aktualisiert.")

    elif query.data == "write_no":
        pending_changes.clear()
        await query.edit_message_text("🚫 Änderung abgelehnt.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    log_action("SYSTEM", "Bot started and polling...")
    app.run_polling()
