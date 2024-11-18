import telebot
from datetime import datetime, timedelta
from telebot import types

# Use your existing token
TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"  # Do not change
bot = telebot.TeleBot(TOKEN)

# Book data structure with IDs
books = [
    {"id": 1, "name": "A Big Ball of String", "author": "Marion Holland", "status": "Available"},
    {"id": 2, "name": "Charlotte's Web", "author": "E.B. White", "status": "Available"},
    {"id": 3, "name": "1984", "author": "George Orwell", "status": "Available"},
    {"id": 4, "name": "To Kill a Mockingbird", "author": "Harper Lee", "status": "Available"},
    {"id": 5, "name": "Moby-Dick", "author": "Herman Melville", "status": "Available"},
    {"id": 6, "name": "The Great Gatsby", "author": "F. Scott Fitzgerald", "status": "Available"},
    {"id": 7, "name": "War and Peace", "author": "Leo Tolstoy", "status": "Available"},
    {"id": 8, "name": "Crime and Punishment", "author": "Fyodor Dostoevsky", "status": "Available"},
    {"id": 9, "name": "Pride and Prejudice", "author": "Jane Austen", "status": "Available"},
    {"id": 10, "name": "The Hobbit", "author": "J.R.R. Tolkien", "status": "Available"},
]

borrowed_books = []  # List of borrowed books
ADMIN_PASSWORD = "12345"  # Admin password
logged_in_admins = {}  # Store admin login status

# Pagination settings
BOOKS_PER_PAGE = 5

# Helper functions
def is_admin_logged_in(user_id):
    return logged_in_admins.get(user_id, False)

def find_book_by_id(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def find_book_by_name(name):
    for book in books:
        if name.lower() in book["name"].lower():
            return book
    return None

# /start command handler
@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    list_books_btn = types.KeyboardButton("📚 List Books")
    search_books_btn = types.KeyboardButton("🔍 Search Books")
    borrow_book_btn = types.KeyboardButton("📖 Borrow Book")
    return_book_btn = types.KeyboardButton("🔄 Return Book")
    login_admin_btn = types.KeyboardButton("🔑 Log in as Admin")
    about_btn = types.KeyboardButton("ℹ️ About Developer")
    markup.add(list_books_btn, search_books_btn, borrow_book_btn, return_book_btn, login_admin_btn, about_btn)
    bot.send_message(message.chat.id, "Welcome to Nasli Dono bot! Choose an option:", reply_markup=markup)

# List books with pagination
@bot.message_handler(func=lambda message: message.text == "📚 List Books")
def list_books(message):
    send_books_page(message, 1)

def send_books_page(message, page):
    start = (page - 1) * BOOKS_PER_PAGE
    end = start + BOOKS_PER_PAGE
    books_page = books[start:end]
    total_pages = -(-len(books) // BOOKS_PER_PAGE)

    response = f"📚 Available books (Page {page}/{total_pages}):\n\n"
    for book in books_page:
        status = book["status"]
        response += f"📘 ID: {book['id']} | {book['name']} by {book['author']} - Status: {status}\n"

    markup = types.InlineKeyboardMarkup()
    if page > 1:
        markup.add(types.InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{page}"))
    if end < len(books):
        markup.add(types.InlineKeyboardButton("➡️ Next", callback_data=f"next_{page}"))
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("prev_") or call.data.startswith("next_"))
def paginate_books(call):
    current_page = int(call.data.split("_")[1])
    new_page = current_page - 1 if "prev" in call.data else current_page + 1
    send_books_page(call.message, new_page)

# Search books
@bot.message_handler(func=lambda message: message.text == "🔍 Search Books")
def search_books(message):
    bot.send_message(message.chat.id, "Enter the name or a keyword to search for books:")
    bot.register_next_step_handler(message, process_search)

def process_search(message):
    keyword = message.text.lower()
    results = [book for book in books if keyword in book["name"].lower()]
    if results:
        response = "🔍 Search results:\n\n"
        for book in results:
            status = book["status"]
            response += f"📘 ID: {book['id']} | {book['name']} by {book['author']} - Status: {status}\n"
    else:
        response = "❌ No books found matching your search. Try another keyword."
    bot.send_message(message.chat.id, response)

# Admin login
# Admin menu after login
@bot.message_handler(func=lambda message: message.text == "🔑 Log in as Admin")
def admin_login(message):
    bot.send_message(message.chat.id, "Enter the admin password:")
    bot.register_next_step_handler(message, process_admin_login)

def process_admin_login(message):
    if message.text == ADMIN_PASSWORD:
        logged_in_admins[message.from_user.id] = True
        bot.send_message(message.chat.id, "✅ You are now logged in as admin.")
        show_admin_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ Incorrect password. Try again.")

def show_admin_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    list_books_btn = types.KeyboardButton("📚 List Books")
    add_book_btn = types.KeyboardButton("➕ Add Book")
    edit_book_btn = types.KeyboardButton("✏️ Edit Book")
    delete_book_btn = types.KeyboardButton("❌ Delete Book")
    logout_btn = types.KeyboardButton("🚪 Logout")
    markup.add(list_books_btn, add_book_btn, edit_book_btn, delete_book_btn, logout_btn)
    bot.send_message(message.chat.id, "Welcome to the Admin Menu. Choose an option:", reply_markup=markup)

# Check if the user is an admin before allowing them to access the admin menu
@bot.message_handler(func=lambda message: message.text == "📚 List Books")
def list_books(message):
    if is_admin_logged_in(message.from_user.id):
        send_books_page(message, 1)
    else:
        bot.send_message(message.chat.id, "❌ You must be logged in as an admin to view this.")

@bot.message_handler(func=lambda message: message.text == "➕ Add Book")
def add_book(message):
    if is_admin_logged_in(message.from_user.id):
        bot.send_message(message.chat.id, "Enter the name of the new book:")
        bot.register_next_step_handler(message, process_add_book)
    else:
        bot.send_message(message.chat.id, "❌ You must be logged in as an admin to add books.")

def process_add_book(message):
    new_book_name = message.text
    bot.send_message(message.chat.id, "Enter the author's name:")
    bot.register_next_step_handler(message, lambda msg: process_add_author(msg, new_book_name))

def process_add_author(message, new_book_name):
    new_author_name = message.text
    new_book = {"id": len(books) + 1, "name": new_book_name, "author": new_author_name, "status": "Available"}
    books.append(new_book)
    bot.send_message(message.chat.id, f"✅ Book '{new_book_name}' by {new_author_name} has been added.")

@bot.message_handler(func=lambda message: message.text == "✏️ Edit Book")
def edit_book(message):
    if is_admin_logged_in(message.from_user.id):
        bot.send_message(message.chat.id, "Enter the ID of the book you want to edit:")
        bot.register_next_step_handler(message, process_edit_book)
    else:
        bot.send_message(message.chat.id, "❌ You must be logged in as an admin to edit books.")

def process_edit_book(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book:
            bot.send_message(message.chat.id, f"Editing book '{book['name']}' by {book['author']}.")
            bot.send_message(message.chat.id, "Enter the new name for the book:")
            bot.register_next_step_handler(message, lambda msg: process_edit_name(msg, book_id, book))
        else:
            bot.send_message(message.chat.id, "❌ Book not found.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid input. Please enter a numeric ID.")

def process_edit_name(message, book_id, book):
    new_name = message.text
    book["name"] = new_name
    bot.send_message(message.chat.id, "Enter the new author's name:")
    bot.register_next_step_handler(message, lambda msg: process_edit_author(msg, book_id, book))

def process_edit_author(message, book_id, book):
    new_author = message.text
    book["author"] = new_author
    bot.send_message(message.chat.id, f"✅ Book '{book['name']}' by {book['author']} has been updated.")

@bot.message_handler(func=lambda message: message.text == "❌ Delete Book")
def delete_book(message):
    if is_admin_logged_in(message.from_user.id):
        bot.send_message(message.chat.id, "Enter the ID of the book you want to delete:")
        bot.register_next_step_handler(message, process_delete_book)
    else:
        bot.send_message(message.chat.id, "❌ You must be logged in as an admin to delete books.")

def process_delete_book(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book:
            books.remove(book)
            bot.send_message(message.chat.id, f"✅ Book '{book['name']}' by {book['author']} has been deleted.")
        else:
            bot.send_message(message.chat.id, "❌ Book not found.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid input. Please enter a numeric ID.")

# Admin logout
@bot.message_handler(func=lambda message: message.text == "🚪 Logout")
def admin_logout(message):
    if is_admin_logged_in(message.from_user.id):
        del logged_in_admins[message.from_user.id]
        bot.send_message(message.chat.id, "✅ You have successfully logged out.")
        send_welcome(message)  # Send the welcome message back after logout
    else:
        bot.send_message(message.chat.id, "❌ You are not logged in.")


# Borrow book
@bot.message_handler(func=lambda message: message.text == "📖 Borrow Book")
def borrow_book(message):
    bot.send_message(message.chat.id, "Enter the ID of the book you want to borrow:")
    bot.register_next_step_handler(message, process_borrow)

def process_borrow(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book and book["status"] == "Available":
            book["status"] = "Borrowed"
            borrowed_books.append({"book_id": book_id, "student_id": message.from_user.id})
            bot.send_message(message.chat.id, f"✅ You have successfully borrowed '{book['name']}'.")
        else:
            bot.send_message(message.chat.id, "❌ Book not available or invalid ID.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid input. Please enter a numeric ID.")

# Return book
@bot.message_handler(func=lambda message: message.text == "🔄 Return Book")
def return_book(message):
    bot.send_message(message.chat.id, "Enter the ID of the book you want to return:")
    bot.register_next_step_handler(message, process_return)

def process_return(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book and book["status"] == "Borrowed":
            book["status"] = "Available"
            borrowed_books[:] = [b for b in borrowed_books if b["book_id"] != book_id]
            bot.send_message(message.chat.id, f"✅ You have successfully returned '{book['name']}'.")
        else:
            bot.send_message(message.chat.id, "❌ Book not found or already available.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid input. Please enter a numeric ID.")

# About Developer
@bot.message_handler(func=lambda message: message.text == "ℹ️ About Developer")
def about_developer(message):
    response = (
        "👨‍💻 *About the Developer:*\n\n"
        "📛 *Name:* Azimjon Sobirov\n"
        "🌍 *Location:* Khujand, Tajikistan\n"
        "🔧 *Expertise:* Backend Development, Flask, Python, Telegram Bots\n"
        "🎓 *Roles:* Intern at ANUR.tech, Volunteer at American Space Khujand\n"
        "🚀 *Achievements:* NASA Space Apps 2024 Participant\n"
        "📩 *Contact:* azimjonsobirov@example.com\n"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown")

# Run the bot
try:
    print("Bot is running...")
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error starting bot: {e}")
