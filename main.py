from datetime import datetime, timedelta
import telebot
from telebot import types

TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"
bot = telebot.TeleBot(TOKEN)

books = [
    {"id": 1, "name": "A Big Ball of String", "author": "Marion Holland", "status": "Available"},
    {"id": 2, "name": "A Child’s Garden of Versus (orange book)", "author": "Robert Louis Stevenson", "status": "Available"},
    {"id": 3, "name": "A Child’s Garden of Versus (grey book)", "author": "Robert Louis Stevenson", "status": "Available"},
    {"id": 4, "name": "A Fly Went By", "author": "Mike McClintock", "status": "Available"},
    {"id": 5, "name": "A Grain of Rice", "author": "Helena Clare Pittman", "status": "Available"},
    {"id": 6, "name": "A Grain of Rice", "author": "Helena Clare Pittman", "status": "Available"},
    {"id": 7, "name": "A Lion to Guard Us", "author": "Clyde Robert Bulla", "status": "Available"},
    {"id": 8, "name": "A Lion to Guard Us", "author": "Clyde Robert Bulla", "status": "Available"},
    {"id": 9, "name": "A POKE in the I", "author": "Paul B. Janeczko", "status": "Available"},
    {"id": 10, "name": "A Scandal in Bohemia", "author": "Arthur Conan Doyle", "status": "Available"},
    {"id": 11, "name": "A Simple Soul. Level 5", "author": "Gustave Flaubert", "status": "Available"},
    {"id": 12, "name": "An Anthology of Short Stories. Level 2", "author": "Henry Lawson", "status": "Available"},
    {"id": 13, "name": "Amelia Bedelia, level 2", "author": "Peggy Parish", "status": "Available"},
    {"id": 14, "name": "Amelia Bedelia, level 2", "author": "Peggy Parish", "status": "Available"},
    {"id": 15, "name": "American Adventures", "author": "Morrie Greenberg", "status": "Available"},
    {"id": 16, "name": "A Bear Called Paddington", "author": "Michael Bond", "status": "Available"},
    {"id": 17, "name": "And Then What Happened, PAUL REVERE?", "author": "Pictures By Margot Tomes", "status": "Available"},
    {"id": 18, "name": "Balto", "author": "Natalie Standiford", "status": "Available"},
    {"id": 19, "name": "Beat the Story-Drum Pum-Pum", "author": "Ashley Bryan", "status": "Available"},
    {"id": 20, "name": "Brown Bear, Brown Bear", "author": "Bill Martin Jr. & Eric Carle", "status": "Available"},
    {"id": 21, "name": "Caddie Woodlawn", "author": "Carol Ryrie Brink", "status": "Available"},
    {"id": 22, "name": "What's the Big Idea, Ben Franklin?", "author": "Margot Tomes", "status": "Available"},
    {"id": 23, "name": "Carry On, Mr. Bowditch", "author": "Jean Lee Latham", "status": "Available"},
    {"id": 24, "name": "Capyboppy", "author": "Bill Peet", "status": "Available"},
    {"id": 25, "name": "Can't You Make Them Behave, King George?", "author": "Jean Fritz", "status": "Available"},
    {"id": 26, "name": "Castle Diary", "author": "Richard Platt", "status": "Available"},
    {"id": 27, "name": "Christopher Columbus", "author": "Norman Green", "status": "Available"},
    {"id": 28, "name": "White Stallion of Lipizza", "author": "Marguerite Henry", "status": "Available"},
    {"id": 29, "name": "Chucaro, Wild Pony of the Pampa", "author": "Francis Kalnay", "status": "Available"},
    {"id": 30, "name": "Columbus in Japan?", "author": "Michael Johnstone", "status": "Available"},
    {"id": 31, "name": "Cornstalks: A Bushel of Poems", "author": "James Stevenson", "status": "Available"},
    {"id": 32, "name": "Daniel's Duck, Level 3", "author": "Clyde Robert Bulla", "status": "Available"},
    {"id": 33, "name": "Dear Mr. Henshaw", "author": "Beverly Cleary", "status": "Available"},
    {"id": 34, "name": "Detective in Togas", "author": "Henry Winterfeld", "status": "Available"},
    {"id": 35, "name": "The Story of Doctor Dolittle", "author": "Hugh Lofting", "status": "Available"},
    {"id": 36, "name": "English-Uzbek-Russian Picture Dictionary", "author": "Zamirjon Butaev", "status": "Available"},
    {"id": 37, "name": "Eric the Red and Leif the Lucky", "author": "Barbara Schiller", "status": "Available"},
    {"id": 38, "name": "Everyday Things", "author": "Eliot Humberstone", "status": "Available"},
    {"id": 39, "name": "Exploration of North America", "author": "Coloring Book", "status": "Available"},
    {"id": 40, "name": "Fables", "author": "Arnold Lobel", "status": "Available"},
    {"id": 41, "name": "Favorite poems of childhood", "author": "Philip Smith", "status": "Available"},
    {"id": 42, "name": "Finding the titanic", "author": "Robert D.Ballard", "status": "Available"},
    {"id": 43, "name": "", "author": "Arnold Lobel", "status": "Available"},
    {"id": 44, "name": "Fables", "author": "Arnold Lobel", "status": "Available"},
    {"id": 45, "name": "Fables", "author": "Arnold Lobel", "status": "Available"},
]

borrowed_books = []
ADMIN_PASSWORD = "12345"
logged_in_admins = {}
BOOKS_PER_PAGE = 5

def is_admin_logged_in(user_id):
    return logged_in_admins.get(user_id, False)

def find_book_by_id(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📚 List Books"),
        types.KeyboardButton("🔍 Search Books"),
        types.KeyboardButton("📖 Borrow Book"),
        types.KeyboardButton("🔄 Return Book"),
        types.KeyboardButton("🔑 Log in as Admin"),
        types.KeyboardButton("ℹ️ About Developer")
    )
    bot.send_message(message.chat.id, "Welcome to Nasli Dono bot! Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📚 List Books" and not is_admin_logged_in(m.from_user.id))
def list_books_user(message):
    send_books_page(message, 1)

@bot.message_handler(func=lambda m: m.text == "📚 List Books" and is_admin_logged_in(m.from_user.id))
def list_books_admin(message):
    send_books_page(message, 1)

def send_books_page(message, page):
    start = (page - 1) * BOOKS_PER_PAGE
    end = start + BOOKS_PER_PAGE
    books_page = books[start:end]
    total_pages = -(-len(books) // BOOKS_PER_PAGE)
    response = f"📚 Available books (Page {page}/{total_pages}):\n\n"
    for book in books_page:
        response += f"📘 ID: {book['id']} | {book['name']} by {book['author']} - Status: {book['status']}\n"
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
            response += f"📘 ID: {book['id']} | {book['name']} by {book['author']} - Status: {book['status']}\n"
    else:
        response = "❌ No books found."
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == "🔑 Log in as Admin")
def admin_login(message):
    bot.send_message(message.chat.id, "Enter the admin password:")
    bot.register_next_step_handler(message, process_admin_login)

def process_admin_login(message):
    if message.text == ADMIN_PASSWORD:
        logged_in_admins[message.from_user.id] = True
        bot.send_message(message.chat.id, "✅ Logged in as admin.")
        show_admin_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ Incorrect password.")

def show_admin_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📚 List Books"),
        types.KeyboardButton("➕ Add Book"),
        types.KeyboardButton("✏️ Edit Book"),
        types.KeyboardButton("❌ Delete Book"),
        types.KeyboardButton("🚪 Logout")
    )
    bot.send_message(message.chat.id, "Admin Menu:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "➕ Add Book")
def add_book(message):
    if is_admin_logged_in(message.from_user.id):
        bot.send_message(message.chat.id, "Enter book name:")
        bot.register_next_step_handler(message, process_add_book)
    else:
        bot.send_message(message.chat.id, "❌ Admin only.")

def process_add_book(message):
    new_book_name = message.text
    bot.send_message(message.chat.id, "Enter author name:")
    bot.register_next_step_handler(message, lambda msg: process_add_author(msg, new_book_name))

def process_add_author(message, new_book_name):
    new_author_name = message.text
    books.append({"id": len(books) + 1, "name": new_book_name, "author": new_author_name, "status": "Available"})
    bot.send_message(message.chat.id, f"✅ Book '{new_book_name}' added.")

@bot.message_handler(func=lambda message: message.text == "✏️ Edit Book")
def edit_book(message):
    if is_admin_logged_in(message.from_user.id):
        bot.send_message(message.chat.id, "Enter book ID to edit:")
        bot.register_next_step_handler(message, process_edit_book)
    else:
        bot.send_message(message.chat.id, "❌ Admin only.")

def process_edit_book(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book:
            bot.send_message(message.chat.id, f"Editing '{book['name']}' by {book['author']}. Enter new name:")
            bot.register_next_step_handler(message, lambda msg: process_edit_name(msg, book))
        else:
            bot.send_message(message.chat.id, "❌ Book not found.")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID.")

def process_edit_name(message, book):
    book["name"] = message.text
    bot.send_message(message.chat.id, "Enter new author name:")
    bot.register_next_step_handler(message, lambda msg: process_edit_author(msg, book))

def process_edit_author(message, book):
    book["author"] = message.text
    bot.send_message(message.chat.id, f"✅ Book updated to '{book['name']}' by {book['author']}.")

@bot.message_handler(func=lambda message: message.text == "❌ Delete Book")
def delete_book(message):
    if is_admin_logged_in(message.from_user.id):
        bot.send_message(message.chat.id, "Enter book ID to delete:")
        bot.register_next_step_handler(message, process_delete_book)
    else:
        bot.send_message(message.chat.id, "❌ Admin only.")

def process_delete_book(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book:
            books.remove(book)
            bot.send_message(message.chat.id, f"✅ Book '{book['name']}' deleted.")
        else:
            bot.send_message(message.chat.id, "❌ Book not found.")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID.")

@bot.message_handler(func=lambda message: message.text == "🚪 Logout")
def admin_logout(message):
    if is_admin_logged_in(message.from_user.id):
        del logged_in_admins[message.from_user.id]
        bot.send_message(message.chat.id, "✅ Logged out.")
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, "❌ Not logged in.")

@bot.message_handler(func=lambda message: message.text == "📖 Borrow Book")
def borrow_book(message):
    bot.send_message(message.chat.id, "Enter book ID to borrow:")
    bot.register_next_step_handler(message, process_borrow)

def process_borrow(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book and book["status"] == "Available":
            book["status"] = "Borrowed"
            borrowed_books.append({"book_id": book_id, "student_id": message.from_user.id})
            bot.send_message(message.chat.id, f"✅ Borrowed '{book['name']}'.")
        else:
            bot.send_message(message.chat.id, "❌ Not available.")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID.")

@bot.message_handler(func=lambda message: message.text == "🔄 Return Book")
def return_book(message):
    bot.send_message(message.chat.id, "Enter book ID to return:")
    bot.register_next_step_handler(message, process_return)

def process_return(message):
    try:
        book_id = int(message.text)
        book = find_book_by_id(book_id)
        if book and book["status"] == "Borrowed":
            book["status"] = "Available"
            borrowed_books[:] = [b for b in borrowed_books if b["book_id"] != book_id]
            bot.send_message(message.chat.id, f"✅ Returned '{book['name']}'.")
        else:
            bot.send_message(message.chat.id, "❌ Not borrowed.")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID.")

@bot.message_handler(func=lambda message: message.text == "ℹ️ About Developer")
def about_developer(message):
    response = (
        "👨‍💻 *About the Developer:*\n\n"
        "📛 *Name:* Azimjon Sobirov\n"
        "🌍 *Location:* Jabbor Rasulvov, Tajikistan\n"
        "🔧 *Expertise:* Backend Development, Flask, Python, Telegram Bots\n"
        "🎓 *Roles:* Intern at ANUR.tech, Volunteer at American Space Khujand\n"
        "🚀 *Achievements:* NASA Space Apps 2024 Participant\n"
        "📩 *Contact:* azimjon.sobirov.09@mail.ru\n"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
