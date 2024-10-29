import telebot
from datetime import datetime, timedelta
import sqlite3

# Initialize the bot with your token
TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"
bot = telebot.TeleBot(TOKEN)

# Connect to the database
def get_db_connection():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Nasli Dono bot! Use /borrow <book name> to borrow a book, or /return <book name> to return a book. Use /list to see available books.")

# /list command handler to list available books with borrowed information
@bot.message_handler(commands=['list'])
def list_books(message):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT b.name, b.status, bb.student_name, bb.return_date FROM books b LEFT JOIN borrowed_books bb ON b.id = bb.book_id")
    books = cursor.fetchall()
    
    available_books = []
    for book in books:
        if book["status"] == "Available":
            available_books.append(f"{book['name']}: {book['status']}")
        else:
            # Show borrowed info with return date in day.month.year format
            return_date_str = datetime.strptime(book["return_date"], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
            available_books.append(f"{book['name']}: Borrowed by {book['student_name']} (time returning: {return_date_str})")

    bot.reply_to(message, "Books available:\n" + "\n".join(available_books))
    conn.close()

# /borrow command handler
@bot.message_handler(commands=['borrow'])
def borrow_book(message):
    user = message.from_user.username
    command, *book_name = message.text.split()
    book_name = " ".join(book_name)
    
    if not book_name:
        bot.reply_to(message, "Please specify the book name. Usage: /borrow <book name>")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the book is available
    cursor.execute("SELECT id, status FROM books WHERE name = ?", (book_name,))
    book = cursor.fetchone()

    if book and book["status"] == "Available":
        # Calculate return time (1 week from now)
        borrow_time = datetime.now()
        return_time = borrow_time + timedelta(weeks=1)
        return_time_str = return_time.strftime('%Y-%m-%d %H:%M:%S')

        # Update book status and insert into borrowed_books
        cursor.execute("UPDATE books SET status = 'Borrowed' WHERE id = ?", (book["id"],))
        cursor.execute("INSERT INTO borrowed_books (book_id, student_name, return_date) VALUES (?, ?, ?)", (book["id"], user, return_time_str))

        conn.commit()
        bot.reply_to(message, f"You have borrowed '{book_name}'. Please return it by {return_time.strftime('%d.%m.%Y %H:%M:%S')}.")
    else:
        bot.reply_to(message, f"'{book_name}' is not available for borrowing.")
    conn.close()

# /return command handler
@bot.message_handler(commands=['return'])
def return_book(message):
    user = message.from_user.username
    command, *book_name = message.text.split()
    book_name = " ".join(book_name)

    if not book_name:
        bot.reply_to(message, "Please specify the book name. Usage: /return <book name>")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Find the borrowed book by user and name
    cursor.execute("""
    SELECT b.id, bb.return_date
    FROM books b
    JOIN borrowed_books bb ON b.id = bb.book_id
    WHERE b.name = ? AND bb.student_name = ?
    """, (book_name, user))
    record = cursor.fetchone()

    if record:
        # Check if the book is being returned within the allowed time
        current_time = datetime.now()
        return_time = datetime.strptime(record["return_date"], '%Y-%m-%d %H:%M:%S')

        if current_time <= return_time:
            # Book returned on time
            cursor.execute("UPDATE books SET status = 'Available' WHERE id = ?", (record["id"],))
            cursor.execute("DELETE FROM borrowed_books WHERE book_id = ?", (record["id"],))
            bot.reply_to(message, f"Thank you for returning '{book_name}' on time!")
        else:
            # Book returned late
            bot.reply_to(message, f"You are late in returning '{book_name}'. Please be mindful of the borrowing period in the future.")
            cursor.execute("UPDATE books SET status = 'Available' WHERE id = ?", (record["id"],))
            cursor.execute("DELETE FROM borrowed_books WHERE book_id = ?", (record["id"],))

        conn.commit()
    else:
        bot.reply_to(message, "It seems you have not borrowed this book or the name is incorrect.")
    conn.close()

# Start polling
bot.polling()
