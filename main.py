import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

USERS_FILE = "user.json"
BOOKS_FILE = "books.json"
ADMINS_FILE = "admins.json"

if os.path.exists(BOOKS_FILE):
    with open(BOOKS_FILE, "r") as f:
        books = json.load(f)
else:
    books = []

if os.path.exists(ADMINS_FILE) and os.path.getsize(ADMINS_FILE) > 0:
    with open(ADMINS_FILE, "r") as f:
        admins = json.load(f)
else:
    admins = {}
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f, indent=4)

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f, indent=4)

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_books():
    with open(BOOKS_FILE, "w") as f:
        json.dump(books, f, indent=4)

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def is_authenticated(user_id):
    return str(user_id) in users

def load_books():
    with open(BOOKS_FILE, "r") as f:
        return json.load(f)

def admin_panel_btns(message):
    markup_admin = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_admin_panel = types.KeyboardButton("Admin Panel")
    btn_log_out = types.KeyboardButton("Log Out")
    markup_admin.add(btn_admin_panel, btn_log_out)
    bot.send_message(message.chat.id, "Please Choose the Option: ", reply_markup=markup_admin)

@bot.message_handler(func=lambda message: message.text.lower() == "admin panel")
def admin_panel_options(message):
    markup_admin_options = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    see_users_btn = types.KeyboardButton("Users")
    books_returning_btn = types.KeyboardButton("Returning Date of Books")
    book_add_btn = types.KeyboardButton("Add Book")
    delete_book_btn = types.KeyboardButton("Delete Book")
    settings_btn = types.KeyboardButton("Settings")
    back_main_btn = types.KeyboardButton("Back")
    markup_admin_options.add(
        see_users_btn, books_returning_btn, book_add_btn, delete_book_btn, settings_btn, back_main_btn
    )
    bot.send_message(message.chat.id, "Please Choose a Option: ", reply_markup=markup_admin_options)

@bot.message_handler(func=lambda message:message.text.lower() == "users")
def see_users(message):
    bot.send_message(message.chat.id, "See Users Handler in Progeress.......")

@bot.message_handler(func=lambda message:message.text.lower() == "returning date of books")
def returnig_date_books(message):
    bot.send_message(message.chat.id, "Returning Date of Books in Progeress.......")

@bot.message_handler(func=lambda message:message.text.lower() == "add book")
def add_book(message):
    bot.send_message(message.chat.id, "Adding Book in Progeress.......")

@bot.message_handler(func=lambda message:message.text.lower() == "delete book")
def delete_book(message):
    bot.send_message(message.chat.id, "Deleting Books in Progeress.......")

@bot.message_handler(func=lambda message:message.text.lower() == "settings")
def settings(message):
    bot.send_message(message.chat.id, "Settings in Progeress.......")

@bot.message_handler(func=lambda message:message.text.lower() == "back")
def back(message):
    admin_panel_btns(message)

def main_menu(message):
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
    if is_authenticated(user_id):
        main_menu(message)
    else:
        markup_start = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn_reg = types.KeyboardButton("Register")
        btn_log = types.KeyboardButton("Log In")
        btn_admin = types.KeyboardButton("Log In as Admin")
        markup_start.add(btn_reg, btn_log, btn_admin)
        bot.send_message(
            message.chat.id,
            "Hi! This bot lets you borrow books and read them."
        )
        bot.send_message(message.chat.id, "Please Register or Log In to use the bot", reply_markup=markup_start)

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "log in as admin")
def log_admin(message):
    user_id = str(message.from_user.id)
    if user_id in admins:
        bot.send_message(message.chat.id, "✅ You are already an Admin!")
        admin_panel_btns(message)
    else:
        msg = bot.send_message(message.chat.id, "Enter your Name:")
        bot.register_next_step_handler(msg, process_admin_name)

def process_admin_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    admins[user_id] = {"pending_name": name}
    save_admins()
    msg = bot.send_message(message.chat.id, "Now enter your Email:")
    bot.register_next_step_handler(msg, process_admin_email)

def process_admin_email(message):
    user_id = str(message.from_user.id)
    email = message.text.strip()
    if user_id not in admins or "pending_name" not in admins[user_id]:
        bot.send_message(message.chat.id, "⚠ Something went wrong. Please try logging in again.")
        return
    admins[user_id]["pending_email"] = email
    save_admins()
    msg = bot.send_message(message.chat.id, "Now enter the Admin Username:")
    bot.register_next_step_handler(msg, process_admin_username)

def process_admin_username(message):
    user_id = str(message.from_user.id)
    username = message.text.strip()
    if user_id not in admins or "pending_email" not in admins[user_id]:
        bot.send_message(message.chat.id, "⚠ Something went wrong. Please try logging in again.")
        return
    admins[user_id]["pending_username"] = username
    save_admins()
    msg = bot.send_message(message.chat.id, "Now enter the Admin Password:")
    bot.register_next_step_handler(msg, process_admin_password)

def process_admin_password(message):
    user_id = str(message.from_user.id)
    password = message.text.strip()
    if user_id not in admins or "pending_username" not in admins[user_id]:
        bot.send_message(message.chat.id, "⚠ Something went wrong. Please try logging in again.")
        return
    username = admins[user_id]["pending_username"]
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        name = admins[user_id]["pending_name"]
        email = admins[user_id]["pending_email"]
        admins[user_id] = {"name": name, "email": email}
        save_admins()
        bot.send_message(
            message.chat.id,
            f"✅ Admin login successful!\nWelcome, {name} ({email})"
        )
        admin_panel_btns(message)
    else:
        del admins[user_id]
        save_admins()
        bot.send_message(message.chat.id, "❌ Invalid username or password. Try again.")

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
    users[user_id] = {"name": name, "borrowed": []}
    msg = bot.send_message(message.chat.id, "Now enter your phone number:")
    bot.register_next_step_handler(msg, process_register_phone)

def process_register_phone(message):
    phone = message.text.strip()
    user_id = str(message.from_user.id)
    if user_id in users:
        users[user_id]["phone"] = phone
        save_users()
        bot.send_message(
            message.chat.id,
            f"Registration complete!\nName: {users[user_id]['name']}\nPhone: {phone}"
        )
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please type 'register' again.")

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "log in")
def login(message):
    user_id = str(message.from_user.id)
    if is_authenticated(user_id):
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
    markup.add("Register", "Log In", "Log In as Admin")
    bot.send_message(message.chat.id, "You've been logged out.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "list of books")
def list_books(message):
    try:
        with open(BOOKS_FILE, "rb") as f:
            bot.send_document(message.chat.id, f)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Books file not found.")

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "borrowing book")
def borrowing_book(message):
    bot.send_message(message.chat.id, "Enter the book ID or name to borrow: ")
    bot.register_next_step_handler(message, process_borrow)

def process_borrow(message):
    user_id = str(message.from_user.id)
    query = message.text.strip()
    book = None
    for b in books:
        if str(b["id"]) == query or b["title"].lower() == query.lower():
            book = b
            break
    if not book:
        bot.send_message(message.chat.id, "❌ Book not found. Try again.")
        return
    if book.get("available", True) is False:
        bot.send_message(message.chat.id, f"❌ '{book['title']}' is already borrowed.")
        return
    users[user_id]["pending_borrow"] = book["id"]
    save_users()
    msg = bot.send_message(message.chat.id, f"Enter returning date for '{book['title']}' (example: 2025-09-10):")
    bot.register_next_step_handler(msg, process_return_date)

def process_return_date(message):
    user_id = str(message.from_user.id)
    return_date = message.text.strip()
    if user_id not in users or "pending_borrow" not in users[user_id]:
        bot.send_message(message.chat.id, "⚠ Something went wrong. Please try borrowing again.")
        return
    book_id = users[user_id]["pending_borrow"]
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        bot.send_message(message.chat.id, "❌ Book not found. Please try again.")
        return
    book["available"] = False
    if "borrowed" not in users[user_id]:
        users[user_id]["borrowed"] = []
    users[user_id]["borrowed"].append({
        "title": book["title"],
        "return_date": return_date
    })
    del users[user_id]["pending_borrow"]
    save_books()
    save_users()
    bot.send_message(
        message.chat.id,
        f"✅ You have successfully borrowed: {book['title']}\n"
        f"📅 Returning date: {return_date}\n"
        f"Please remember to return it on time!"
    )


@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "returning book")
def return_book(message):
    bot.send_message(message.chat.id, "Enter the Book ID or Title you want to return:")
    bot.register_next_step_handler(message, process_return)


def process_return(message):
    user_id = str(message.from_user.id)
    query = message.text.strip()

    if user_id not in users or "borrowed" not in users[user_id]:
        bot.send_message(message.chat.id, "⚠ You have not borrowed any books.")
        return

    borrowed_list = users[user_id]["borrowed"]


    borrowed_book = next((b for b in borrowed_list if str(b.get("id")) == query), None)

    if not borrowed_book:
        borrowed_book = next((b for b in borrowed_list if b["title"].lower() == query.lower()), None)

    if not borrowed_book:
        bot.send_message(message.chat.id, "❌ You did not borrow this book or it does not exist.")
        return

    for b in books:
        if str(b.get("id")) == query or b["title"].lower() == query.lower():
            b["available"] = True
            break

    borrowed_list.remove(borrowed_book)

    save_books()
    save_users()

    bot.send_message(message.chat.id, f"✅ Returned '{borrowed_book['title']}' successfully!")


if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    print("Webhook removed!")
    bot.polling(none_stop=True)
