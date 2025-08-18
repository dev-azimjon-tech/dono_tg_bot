import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "user.json"

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users,f, indent=2)

def is_auntecated(user_id):
    return str(user_id) in users


def main_menu(message):
    user_id = str(message.from_user.id)
    markup_main = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("List of Books")
    button2 = types.KeyboardButton("Borrowing Book")
    button3 = types.KeyboardButton("Returning Book")
    button4 = types.KeyboardButton("Advertisments")
    button5 = types.KeyboardButton("About Developer")
    log_out = types.KeyboardButton("Log Out")
    markup_main.add(button1, button2, button3, button4, button5, log_out)
    bot.send_message(message.chat.id, "Main Menu:", reply_markup=markup_main)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    if is_auntecated(user_id):
        main_menu(message)
    else:
        markup_start = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn_reg = types.KeyboardButton("Register")
        btn_log = types.KeyboardButton("Log In")
        markup_start.add(btn_reg, btn_log)
        bot.send_message(
            message.chat.id,
            "Hi! This bot lets you to borrow books and read it."
        )
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot", reply_markup=markup_start)

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "register")
def register(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        bot.send_message(message.chat.id, "You're already registered.")
        main_menu(message)
        return
    msg = bot.send_message(message.chat.id, "Enter your name:")
    bot.register_next_step_handler(msg, process_register_name)

def process_register_name(message):
    name = message.text.strip()
    user_id = str(message.from_user.id)
    users[user_id] = {"name": name}
    msg = bot.send_message(message.chat.id, "Now enter your phone number:")
    bot.register_next_step_handler(msg, process_register_phone)

def process_register_phone(message):
    phone = message.text.strip()
    user_id = str(message.from_user.id)
    if user_id in users:
        users[user_id]["phone"] = phone
        save_users()
        bot.send_message(message.chat.id, f"Registration complete!\nName: {users[user_id]['name']}\nPhone: {phone}")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please type 'register' again.")

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "log in")
def login(message):
    user_id = str(message.from_user.id)
    if is_auntecated(user_id):
        bot.send_message(message.chat.id, "You have already logged in!")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "You are not registered yet. Please register first!")

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "log out")
def logout(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        del users[user_id]
        save_users()
        print(f"{user_id} logged out.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Register", "Log In")
    bot.send_message(message.chat.id, "You've been logged out.", reply_markup=markup)



if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    print("Webhook removed!")
    bot.polling(none_stop=True)
