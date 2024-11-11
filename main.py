import telebot
from datetime import datetime, timedelta
from telebot import types

# Initialize the bot with your token
TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"
bot = telebot.TeleBot(TOKEN)

# Sample data structures to replace the database
books = [
    {"name": "Harry Potter 1", "author": "J.K Rowling", "status": "Available"},
    {"name": "Harry Potter 2", "author": "J.K Rowling", "status": "Available"},
    {"name": "Harry Potter 3", "author": "J.K Rowling", "status": "Available"},
    {"name": "The Hobbit", "author": "J.R.R. Tolkien", "status": "Available"},
    {"name": "1984", "author": "George Orwell", "status": "Available"},
    {"name": "The Catcher in the Rye", "author": "J.D. Salinger", "status": "Available"}
]

borrowed_books = []
students = {}  # Dictionary to store student information

# Admin settings
ADMIN_PASSWORD = "12345"  # The password for admin login
logged_in_admins = {}  # Dictionary to track logged-in admin sessions by user ID

# Helper functions
def is_admin_logged_in(user_id):
    return logged_in_admins.get(user_id, False)

def find_book(name):
    for book in books:
        if book["name"].lower() == name.lower():
            return book
    return None

def find_borrowed_book(book_name, student_name):
    for record in borrowed_books:
        if record["book_name"].lower() == book_name.lower() and record["student_name"] == student_name:
            return record
    return None

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📚 List Books", "📖 Borrow Book", "🔄 Return Book", "🔑 Log in as Admin", "About Developer")
    bot.send_message(message.chat.id, "Welcome to Nasli Dono bot! Choose an option:", reply_markup=markup)

# Handle main menu button clicks
@bot.message_handler(func=lambda message: message.text in ["📚 List Books", "📖 Borrow Book", "🔄 Return Book", "About Developer", "🔑 Log in as Admin", "👮 Admin View", "🚪 Log Out", "➕ Add Book", "🔍 Search Books"])
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
    elif message.text == "🔍 Search Books":
        bot.send_message(message.chat.id, "Enter the name or author of the book you want to search:")
        bot.register_next_step_handler(message, search_books_handler)
    elif message.text == "👮 Admin View":
        if is_admin_logged_in(message.from_user.id):
            show_admin_view(message)
        else:
            bot.send_message(message.chat.id, "You need to log in as an admin first.")
    elif message.text == "➕ Add Book":
        if is_admin_logged_in(message.from_user.id):
            ask_add_book(message)
        else:
            bot.send_message(message.chat.id, "You need to log in as an admin first.")

# Command to list books with pagination
def list_books(message, page=1):
    start_index = (page - 1) * 5
    end_index = start_index + 5
    page_books = books[start_index:end_index]
    
    response = "Available books:\n\n"
    for book in page_books:
        status = book["status"]
        response += f"📘 {book['name']} by {book['author']} - Status: {status}\n"
    
    if end_index < len(books):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("🔍 Search Books", "Next Page")
        bot.send_message(message.chat.id, response + "\nYou can search other books, press 'Search Books' button", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("🔍 Search Books")
        bot.send_message(message.chat.id, response + "\nEnd of list. You can search other books.", reply_markup=markup)

# Admin View
def show_admin_view(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ Add Book", "🔍 Search Books", "🚪 Log Out")
    bot.send_message(message.chat.id, "Admin View:\nSelect an action.", reply_markup=markup)

# Search books handler
def search_books_handler(message):
    query = message.text
    search_results = search_books(query)
    if search_results:
        response = "Search results:\n\n"
        for book in search_results:
            response += f"📘 {book['name']} by {book['author']} - Status: {book['status']}\n"
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("🔍 Search Books", "Back to Menu")
        bot.send_message(message.chat.id, response, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "No books found for that search.")

# Ask for student's name
def ask_student_name(message):
    bot.send_message(message.chat.id, "Please enter your full name (Name Surname):")
    bot.register_next_step_handler(message, borrow_book_step_3)

# Borrow book after student name is provided
def borrow_book_step_3(message):
    student_name = message.text
    students[message.from_user.id] = student_name
    bot.send_message(message.chat.id, "Enter the book name you want to borrow:")
    bot.register_next_step_handler(message, finalize_borrow_book)

def finalize_borrow_book(message):
    student_name = students.get(message.from_user.id, "Unknown")
    book_name = message.text
    book = find_book(book_name)
    if book and book["status"] == "Available":
        borrow_time = datetime.now()
        return_time = borrow_time + timedelta(weeks=1)
        book["status"] = "Borrowed"
        borrowed_books.append({
            "book_name": book["name"],
            "student_name": student_name,
            "return_date": return_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        bot.send_message(message.chat.id, f"You have borrowed '{book_name}'. Please return it by {return_time}.")
    else:
        bot.send_message(message.chat.id, f"'{book_name}' is not available for borrowing.")

# Return book handler
def return_book(message):
    student_name = students.get(message.from_user.id, "Unknown")
    book_name = message.text
    record = find_borrowed_book(book_name, student_name)
    if record:
        book = find_book(book_name)
        book["status"] = "Available"
        borrowed_books.remove(record)
        bot.send_message(message.chat.id, f"Thank you for returning '{book_name}'!")
    else:
        bot.send_message(message.chat.id, "It seems you have not borrowed this book or the name is incorrect.")

# Admin password functions
def ask_admin_password(message):
    bot.send_message(message.chat.id, "Please enter the admin password:")
    bot.register_next_step_handler(message, verify_admin_password)

def verify_admin_password(message):
    if message.text == ADMIN_PASSWORD:
        logged_in_admins[message.from_user.id] = True
        bot.send_message(message.chat.id, "Login successful! You now have admin access.")
        show_admin_view(message)
    else:
        bot.send_message(message.chat.id, "Incorrect password. Access denied.")

def about(message):
    bot.send_message(
        message.chat.id,
        "*Bot Developer:* Azimjon Sobirov\n"
        "*Telegram:* @lazy\\_proger",
        parse_mode='MarkdownV2'
    )
# Search books by name or author
def search_books(query):
    results = []
    for book in books:
        if query.lower() in book["name"].lower() or query.lower() in book["author"].lower():
            results.append(book)
    return results

# Admin functions for adding books (optional)
def ask_add_book(message):
    bot.send_message(message.chat.id, "Enter the name of the book you want to add:")
    bot.register_next_step_handler(message, add_book_step_2)

def add_book_step_2(message):
    book_name = message.text
    bot.send_message(message.chat.id, "Enter the author of the book:")
    bot.register_next_step_handler(message, add_book_step_3, book_name)

def add_book_step_3(message, book_name):
    author_name = message.text
    books.append({"name": book_name, "author": author_name, "status": "Available"})
    bot.send_message(message.chat.id, f"Book '{book_name}' by {author_name} added successfully!")

# Log out functionality
@bot.message_handler(func=lambda message: message.text == "🚪 Log Out")
def logout(message):
    if message.from_user.id in logged_in_admins:
        del logged_in_admins[message.from_user.id]
        bot.send_message(message.chat.id, "You have logged out successfully.")
    else:
        bot.send_message(message.chat.id, "You are not logged in.")

try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error starting bot: {e}")


# def about(message):
#     bot.send_message(
#         message.chat.id,
#         "*Bot Developer:* Azimjon Sobirov\n"
#         "*Telegram:* @lazy\\_proger",
#         parse_mode='MarkdownV2'
#     )