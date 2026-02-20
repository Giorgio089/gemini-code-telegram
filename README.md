# gemini-code-telegram
🤖 A powerful Telegram interface for Google Gemini to remotely manage, write, and deploy code directly from your chat. Features file system access, git integration, and real-time token tracking

Gemini Code Telegram Bot 🚀
A powerful Telegram bot that serves as a remote interface for Google Gemini, enabling you to analyze, write, and manage code directly in your local directory via chat.

Features
File System Access: Gemini can read your files and write changes (following your explicit confirmation).

Git Integration: Execute status, diff, and commit & push directly through the chat interface.

Model Selection: Switch between Gemini 2.0 Flash (speed) and Gemini 2.0 Pro (complex reasoning) via the /settings command.

Token Monitoring: Stay informed about your context usage with real-time token tracking for every response.

Security First: Strict whitelist protection ensures only authorized Telegram IDs can execute commands.

Audit Log: Comprehensive logging of all AI actions in gemini_bot.log for full transparency and debugging.

Installation
Clone the Repository:

Bash
git clone https://github.com/YOUR-USERNAME/gemini-code-bot.git
cd gemini-code-bot
Install Dependencies:

Bash
pip install -r requirements.txt
Configuration:
Create a .env file in the root directory:

Plaintext
TELEGRAM_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_google_ai_studio_key_here
AUTHORIZED_USER_ID=your_telegram_id_here
Run the Bot:

Bash
python bot.py
Usage
Chat Naturally: Simply message the bot: "Read main.py and optimize the database connection loop."

Interactive Coding: Review code suggestions sent by the bot and apply them instantly using the "Write" buttons.

Manage Deployment: Ask Gemini to summarize your changes and push them to your repository: "Check my diff and commit it with a professional message."

Requirements
Python 3.9+

A Google AI Studio API Key (Get it for free here)

A Telegram Bot Token (Created via @BotFather)

⚠️ Disclaimer & Safety
Use at your own risk: This tool grants an AI (Google Gemini) read/write access to your local file system and your Git environment.

Data Loss: AI models can "hallucinate" or misinterpret instructions. Always review code proposals before clicking the confirmation button.

Security: Never run this bot without the AUTHORIZED_USER_ID check. Without it, anyone who finds your bot on Telegram could execute commands on your machine.

Sensitive Data: Note that file contents are sent to the Google API. Avoid using this bot for projects containing highly sensitive or strictly confidential data.

No Substitute for Backups: This bot is not a backup solution. Ensure you have regular backups of your system and commit your changes frequently.

The author assumes no liability for any system damage, data loss, or unintended Git operations.
