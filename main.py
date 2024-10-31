import telebot
from datetime import datetime, timedelta

# Initialize the bot with your token
TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"
bot = telebot.TeleBot(TOKEN)

# Sample data structures to replace the database
books = [
    {"name": "Book 1", "status": "Available"},
    {"name": "Book 2", "status": "Available"},
    {"name": "Book 3", "status": "Available"}
]

borrowed_books = []

# Helper functions
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

# Command to list books with their status
@bot.message_handler(commands=['list_books'])
def list_books(message):
    response = "Available books:\n\n"
    for book in books:
        status = book["status"]
        borrowed_info = next((borrowed for borrowed in borrowed_books if borrowed["book_name"] == book["name"]), None)
        if borrowed_info:
            response += f"📘 {book['name']} - Status: {status}, Borrowed by: {borrowed_info['student_name']}, Return date: {borrowed_info['return_date']}\n"
        else:
            response += f"📘 {book['name']} - Status: {status}, Not borrowed\n"
    bot.reply_to(message, response)

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Nasli Dono bot! Use /borrow <book name> to borrow a book, or /return <book name> to return a book. Use /list_books to see available books.")

# /borrow command handler
@bot.message_handler(commands=['borrow'])
def borrow_book(message):
    user = message.from_user.username
    command, *book_name = message.text.split()
    book_name = " ".join(book_name)

    if not book_name:
        bot.reply_to(message, "Please specify the book name. Usage: /borrow <book name>")
        return

    book = find_book(book_name)

    if book and book["status"] == "Available":
        # Calculate return time (1 week from now)
        borrow_time = datetime.now()
        return_time = borrow_time + timedelta(weeks=1)
        return_time_str = return_time.strftime('%Y-%m-%d %H:%M:%S')

        # Update book status and record in borrowed_books
        book["status"] = "Borrowed"
        borrowed_books.append({
            "book_name": book["name"],
            "student_name": user,
            "return_date": return_time_str
        })
        bot.reply_to(message, f"You have borrowed '{book_name}'. Please return it by {return_time.strftime('%d.%m.%Y %H:%M:%S')}.")
    else:
        bot.reply_to(message, f"'{book_name}' is not available for borrowing.")

# /return command handler
@bot.message_handler(commands=['return'])
def return_book(message):
    user = message.from_user.username
    command, *book_name = message.text.split()
    book_name = " ".join(book_name)

    if not book_name:
        bot.reply_to(message, "Please specify the book name. Usage: /return <book name>")
        return

    record = find_borrowed_book(book_name, user)

    if record:
        # Check if the book is being returned within the allowed time
        current_time = datetime.now()
        return_time = datetime.strptime(record["return_date"], '%Y-%m-%d %H:%M:%S')

        book = find_book(book_name)
        if book:
            # Book returned on time
            book["status"] = "Available"
            borrowed_books.remove(record)  # Remove record from borrowed_books

            if current_time <= return_time:
                bot.reply_to(message, f"Thank you for returning '{book_name}' on time!")
            else:
                bot.reply_to(message, f"You are late in returning '{book_name}'. Please be mindful of the borrowing period in the future.")
        else:
            bot.reply_to(message, "An error occurred, please try again.")
    else:
        bot.reply_to(message, "It seems you have not borrowed this book or the name is incorrect.")

# Start polling
try:
    print("Bot is running...")
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error starting bot: {e}")
