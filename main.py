import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import threading
import time
from flask import request

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

USERS_FILE = "/tmp/user.json"
BOOKS_FILE = "books.json"
ADMINS_FILE = "/tmp/admins.json"

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

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f, indent=4)

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

def reminder_checker():
    while True:
        now = datetime.now().date()
        for user_id, user_data in users.items():
            borrowed = user_data.get("borrowed", [])
            for book in borrowed:
                try:
                    return_date = datetime.strptime(book["return_date"], "%Y-%m-%d").date()
                    if now >= return_date:
                        bot.send_message(
                            user_id,
                            f"⏰ Reminder: Please return '{book['title']}'!\nReturning date was: {book['return_date']}"
                        )
                except Exception:
                    continue
        time.sleep(60)

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

@bot.message_handler(func=lambda message: message.text.lower() == "users")
def see_users(message):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        if not users_data:
            bot.send_message(message.chat.id, "📭 No users found.")
            return
        response = "📚 *List of Registered Users:*\n\n"
        for user_id, user_info in users_data.items():
            name = user_info.get("name", "Unknown")
            phone = user_info.get("phone", "Not provided")
            borrowed_books = user_info.get("borrowed", [])
            if borrowed_books:
                borrowed_text = "\n".join(
                    [f"  - {book['title']} (Return: {book['return_date']})" for book in borrowed_books]
                )
            else:
                borrowed_text = "  - None"
            response += (
                f"👤 *Name:* {name}\n"
                f"📞 *Phone:* {phone}\n"
                f"📖 *Borrowed Books:*\n{borrowed_text}\n\n"
            )
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Users file not found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠ Error while loading users: {e}")

@bot.message_handler(func=lambda message: message.text.lower() == "returning date of books")
def ret_date_book(message):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        result = "📚 *Returning Dates of Borrowed Books:*\n\n"
        found_any = False
        for user_id, user_info in users_data.items():
            name = user_info.get("name", "Unknown")
            borrowed = user_info.get("borrowed", [])
            if borrowed:
                found_any = True
                result += f"👤 *{name}*:\n"
                for book in borrowed:
                    result += f"  - {book['title']} → Return by: *{book['return_date']}*\n"
                result += "\n"
        if not found_any:
            result = "✅ No books are currently borrowed."
        bot.send_message(message.chat.id, result, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠ Error loading borrowed books: {e}")

@bot.message_handler(func=lambda message: message.text.lower() == "add book")
def add_book(message):
    msg = bot.send_message(message.chat.id, "📖 Enter the *book title*:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_book_title)

def process_book_title(message):
    title = message.text.strip()
    msg = bot.send_message(message.chat.id, "✍️ Enter the *author name*:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_book_author, title)

def process_book_author(message, title):
    author = message.text.strip()
    msg = bot.send_message(message.chat.id, "🔢 Enter the *book ID* (unique number):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_book_id, title, author)

def process_book_id(message, title, author):
    book_id = message.text.strip()
    if any(str(b["id"]) == book_id for b in books):
        bot.send_message(message.chat.id, "❌ A book with this ID already exists.")
        return
    new_book = {"id": book_id, "title": title, "author": author, "available": True}
    books.append(new_book)
    save_books()
    bot.send_message(
        message.chat.id,
        f"✅ Book added successfully!\n\n📘 *Title:* {title}\n✍️ *Author:* {author}\n🆔 *ID:* {book_id}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text.lower() == "delete book")
def delete_book(message):
    msg = bot.send_message(message.chat.id, "🗑 Enter the *book ID or title* to delete:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_delete_book)

def process_delete_book(message):
    query = message.text.strip()
    global books
    book_to_delete = None
    for b in books:
        if str(b["id"]) == query or b["title"].lower() == query.lower():
            book_to_delete = b
            break
    if not book_to_delete:
        bot.send_message(message.chat.id, "❌ Book not found.")
        return
    books = [b for b in books if b != book_to_delete]
    save_books()
    bot.send_message(
        message.chat.id,
        f"✅ Book '{book_to_delete['title']}' was deleted successfully!",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text.lower() == "settings")
def admin_settings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Change Admin Username")
    btn2 = types.KeyboardButton("Change Admin Password")
    btn_back = types.KeyboardButton("Back")
    markup.add(btn1, btn2, btn_back)
    bot.send_message(message.chat.id, "⚙️ Admin Settings:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.lower() == "change admin username")
def change_admin_username(message):
    msg = bot.send_message(message.chat.id, "🆔 Enter the *new admin username*:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_change_username)

def process_change_username(message):
    new_username = message.text.strip()
    os.environ["ADMIN_USERNAME"] = new_username
    with open(".env", "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(".env", "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("ADMIN_USERNAME="):
                f.write(f"ADMIN_USERNAME={new_username}\n")
            else:
                f.write(line)
    global ADMIN_USERNAME
    ADMIN_USERNAME = new_username
    bot.send_message(message.chat.id, f"✅ Admin username successfully changed to: *{new_username}*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.lower() == "change admin password")
def change_admin_password(message):
    msg = bot.send_message(message.chat.id, "🔒 Enter the *new admin password*:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_change_password)

def process_change_password(message):
    new_password = message.text.strip()
    os.environ["ADMIN_PASSWORD"] = new_password
    with open(".env", "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(".env", "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("ADMIN_PASSWORD="):
                f.write(f"ADMIN_PASSWORD={new_password}\n")
            else:
                f.write(line)
    global ADMIN_PASSWORD
    ADMIN_PASSWORD = new_password
    bot.send_message(message.chat.id, "✅ Admin password successfully changed!", parse_mode="Markdown")

@bot.message_handler(func=lambda message:message.text.lower() == "back")
def sback(message):
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
        bot.send_message(message.chat.id, "Hi! This bot lets you borrow books and read them.")
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    phone_btn = types.KeyboardButton("📞 Send my phone number", request_contact=True)
    markup.add(phone_btn)
    bot.send_message(message.chat.id, "Now share your phone number:", reply_markup=markup)

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    user_id = str(message.from_user.id)
    if message.contact:
        phone = message.contact.phone_number
        if user_id in users:
            users[user_id]["phone"] = phone
            save_users()
            bot.send_message(
                message.chat.id,
                f"✅ Registration complete!\nName: {users[user_id]['name']}\nPhone: {phone}"
            )
            main_menu(message)
        else:
            bot.send_message(message.chat.id, "⚠ Something went wrong. Please register again.")

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
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            book_data = json.load(f)
        if not book_data:
            bot.send_message(message.chat.id, "📭 No books found in the library.")
            return
        response = "📚 *List of Books in the Library:*\n\n"
        for book in book_data:
            title = book.get("title", "Unknown Title")
            author = book.get("author", "Unknown Author")
            book_id = book.get("id", "N/A")
            available = book.get("available", True)
            tags = ", ".join(book.get("tags", []))
            description = book.get("description", "No description available.")
            status_emoji = "✅ Available" if available else "❌ Not Available"
            response += (
                f"📘 *Title:* {title}\n"
                f"✍️ *Author:* {author}\n"
                f"🆔 *ID:* {book_id}\n"
                f"🏷 *Tags:* {tags}\n"
                f"📝 *Description:* {description}\n"
                f"📦 *Status:* {status_emoji}\n\n"
            )
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Books file not found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠ Error while loading books: {e}")

threading.Thread(target=reminder_checker, daemon=True).start()



@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "borrowing book")
def borrowing_book(message):
    msg = bot.send_message(message.chat.id, "Enter the book ID or name to borrow: ")
    bot.register_next_step_handler(msg, process_borrow)

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
    if not book.get("available", True):
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
        "id": book["id"],
        "title": book["title"],
        "return_date": return_date
    })
    del users[user_id]["pending_borrow"]
    save_books()
    save_users()
    bot.send_message(
        message.chat.id,
        f"✅ You have successfully borrowed: {book['title']}\n📅 Returning date: {return_date}\nPlease remember to return it on time!"
    )

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() == "returning book")
def return_book(message):
    msg = bot.send_message(message.chat.id, "Enter the Book ID or Title you want to return:")
    bot.register_next_step_handler(msg, process_return)

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
        if str(b.get("id")) == str(borrowed_book["id"]) or b["title"].lower() == borrowed_book["title"].lower():
            b["available"] = True
            break
    borrowed_list.remove(borrowed_book)
    save_books()
    save_users()
    bot.send_message(message.chat.id, f"✅ Returned '{borrowed_book['title']}' successfully!")

@bot.message_handler(func=lambda message: message.text.lower() == "about developer")
def about_dev(message):
    markup_dev = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    back_menu = types.KeyboardButton("Back to Menu")
    markup_dev.add(back_menu)
    dev_info = (
        "👨‍💻 *About Developer*\n\n"
        "My name is *Azimjon Sobirov*, I am a young backend developer.\n"
        "I work with *Python, Flask, and Telegram Bots*.\n"
        "I constantly improve my skills in programming, testing with *pytest*, "
        "and building useful projects.\n\n"
        "🌟 My current focus:\n"
        "- Writing clean and tested code\n"
        "- Learning backend development deeply\n"
        "- Building creative web applications and bots\n\n"
        "💡 My goal is to grow as a professional programmer, "
        "create innovative projects, and help people with technology."
    )
    bot.send_message(message.chat.id, dev_info, reply_markup=markup_dev, parse_mode="Markdown")

@bot.message_handler(func=lambda message:message.text.lower() == "back to menu")
def back_menu_dev(message):
    main_menu(message)

@bot.message_handler(func=lambda message:message.text.lower() == "advertisments")
def ads(message):
    markup_ads = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    back_menu = types.KeyboardButton("Back to Menu")
    markup_ads.add(back_menu)
    bot.send_message(message.chat.id, "To buy advertisements write to admin: @lazy_proger")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://library-system-o2cp.onrender.com{WEBHOOK_PATH}"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running on Render 🚀", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    else:
        return "bad request", 403

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    print("Webhook removed!")
    reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
    reminder_thread.start()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
