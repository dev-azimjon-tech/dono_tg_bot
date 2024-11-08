import telebot
from datetime import datetime, timedelta
from telebot import types

# Initialize the bot with your token
TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"
bot = telebot.TeleBot(TOKEN)

# Sample data structures to replace the database
books = [
    {"name": "Book 1", "status": "Available"},
    {"name": "Book 2", "status": "Available"},
    {"name": "Book 5", "status": "Available"},
    {"name": "Book 6", "status": "Available"}
]

borrowed_books = []
students = {}  # Dictionary to store student information

# Admin settings
ADMIN_PASSWORD = "12345"  # The password for admin login
logged_in_admins = {}  # Dictionary to track logged-in admin sessions by user ID

# Helper functions
def is_admin_logged_in(user_id):
    """Check if a user is logged in as an admin."""
    return logged_in_admins.get(user_id, False)

def find_book(name):
    """Find a book by name."""
    for book in books:
        if book["name"].lower() == name.lower():
            return book
    return None

def find_borrowed_book(book_name, student_name):
    """Find a borrowed book by name and student."""
    for record in borrowed_books:
        if record["book_name"].lower() == book_name.lower() and record["student_name"] == student_name:
            return record
    return None

# /start command handler to welcome and display main menu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    list_books_btn = types.KeyboardButton("📚 List Books")
    borrow_book_btn = types.KeyboardButton("📖 Borrow Book")
    return_book_btn = types.KeyboardButton("🔄 Return Book")
    login_admin_btn = types.KeyboardButton("🔑 Log in as Admin")
    about_btn = types.KeyboardButton("About Developer")
    markup.add(list_books_btn, borrow_book_btn, return_book_btn, login_admin_btn, about_btn)
    bot.send_message(message.chat.id, "Welcome to Nasli Dono bot! Choose an option:", reply_markup=markup)

# Handle main menu button clicks
@bot.message_handler(func=lambda message: message.text in ["📚 List Books", "📖 Borrow Book", "🔄 Return Book", "About Developer", "🔑 Log in as Admin", "👮 Admin View", "🚪 Log Out"])
def handle_menu_options(message):
    if message.text == "📚 List Books":
        list_books(message)
    elif message.text == "📖 Borrow Book":
        ask_student_name(message)
    elif message.text == "About Developer":
        about(message)
    elif message.text == "🔄 Return Book":
        bot.send_message(message.chat.id, "Enter the book name you want to return:")
        bot.register_next_step_handler(message, return_book)
    elif message.text == "🔑 Log in as Admin":
        ask_admin_password(message)
    elif message.text == "👮 Admin View":
        if is_admin_logged_in(message.from_user.id):
            view_borrowed_books(message)
        else:
            bot.send_message(message.chat.id, "You are not logged in as an admin. Please log in first.")
    elif message.text == "🚪 Log Out":
        log_out_admin(message)

# Command to list books with their status
def list_books(message):
    response = "Available books:\n\n"
    for book in books:
        status = book["status"]
        borrowed_info = next((borrowed for borrowed in borrowed_books if borrowed["book_name"] == book["name"]), None)
        if borrowed_info:
            response += f"📘 {book['name']} - Status: {status}, Borrowed by: {borrowed_info['student_name']}, Return date: {borrowed_info['return_date']}\n"
        else:
            response += f"📘 {book['name']} - Status: {status}, Not borrowed\n"
    bot.send_message(message.chat.id, response)

# Ask for student's name and surname before borrowing a book
def ask_student_name(message):
    bot.send_message(message.chat.id, "Please enter your full name (Name Surname):")
    bot.register_next_step_handler(message, borrow_book_step_2)

def borrow_book_step_2(message):
    # Store student name
    students[message.from_user.id] = message.text
    bot.send_message(message.chat.id, "Enter the book name you want to borrow:")
    bot.register_next_step_handler(message, borrow_book_step_3)

# Borrow book after student name is provided
def borrow_book_step_3(message):
    student_name = students.get(message.from_user.id, "Unknown")
    book_name = message.text
    book = find_book(book_name)

    if book and book["status"] == "Available":
        borrow_time = datetime.now()
        return_time = borrow_time + timedelta(weeks=1)
        return_time_str = return_time.strftime('%Y-%m-%d %H:%M:%S')

        book["status"] = "Borrowed"
        borrowed_books.append({
            "book_name": book["name"],
            "student_name": student_name,
            "return_date": return_time_str
        })
        bot.send_message(message.chat.id, f"You have borrowed '{book_name}'. Please return it by {return_time.strftime('%d.%m.%Y %H:%M:%S')}.")
    else:
        bot.send_message(message.chat.id, f"'{book_name}' is not available for borrowing.")

# Return book handler
def return_book(message):
    student_name = students.get(message.from_user.id, "Unknown")
    book_name = message.text
    record = find_borrowed_book(book_name, student_name)

    if record:
        current_time = datetime.now()
        return_time = datetime.strptime(record["return_date"], '%Y-%m-%d %H:%M:%S')

        book = find_book(book_name)
        if book:
            book["status"] = "Available"
            borrowed_books.remove(record)

            if current_time <= return_time:
                bot.send_message(message.chat.id, f"Thank you for returning '{book_name}' on time!")
            else:
                bot.send_message(message.chat.id, f"You are late in returning '{book_name}'. Please be mindful of the borrowing period in the future.")
        else:
            bot.send_message(message.chat.id, "An error occurred, please try again.")
    else:
        bot.send_message(message.chat.id, "It seems you have not borrowed this book or the name is incorrect.")

# Ask for admin password
def ask_admin_password(message):
    bot.send_message(message.chat.id, "Please enter the admin password:")
    bot.register_next_step_handler(message, verify_admin_password)

# Verify admin password
def verify_admin_password(message):
    if message.text == ADMIN_PASSWORD:
        logged_in_admins[message.from_user.id] = True
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        admin_view_btn = types.KeyboardButton("👮 Admin View")
        logout_btn = types.KeyboardButton("🚪 Log Out")
        markup.add(admin_view_btn, logout_btn)
        bot.send_message(message.chat.id, "Login successful! You now have admin access.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Incorrect password. Access denied.")

# Admin command to view all borrowed books
def view_borrowed_books(message):
    if borrowed_books:
        response = "Borrowed books:\n\n"
        for record in borrowed_books:
            response += f"📘 {record['book_name']} - Borrowed by: {record['student_name']}, Return date: {record['return_date']}\n"
    else:
        response = "No books are currently borrowed."
    bot.send_message(message.chat.id, response)

# Admin logout handler
def log_out_admin(message):
    if is_admin_logged_in(message.from_user.id):
        del logged_in_admins[message.from_user.id]
        bot.send_message(message.chat.id, "You have been logged out as admin.")
        send_welcome(message)  # Go back to the main menu
    else:
        bot.send_message(message.chat.id, "You are not currently logged in as an admin.")

# About developer section
def about(message):
    bot.reply_to(message, (
        "🤖 *Bot Developer:* Azimjon Sobirov\n"
        "📲 *Contact Information:*\n"
        " - *Telegram:* @lazy_proger\n"
        " - *Phone Number:* +992 918-15-47-46\n\n"
        "💼 *Background:*\n"
        " -  *Volunteer at American Space Khujand*\n"
        " - *NASA Space Apps 2024 Participant*\n"
        " - *Intern at ANUR.tech*\n"
        "🎓 *Future Goals:*\n"
        "Aspiring to bring technological innovations to education and make learning accessible for everyone.\n"
        "💼 *For Ads or Collaboration Opportunities,* reach out to @lazy_proger directly.\n\n"
        "Thank you for using Nasli Dono bot!"
    ), parse_mode='Markdown')

try:
    print("Bot is running...")
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error starting bot: {e}")