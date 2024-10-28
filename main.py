import telebot
import sqlite3
from contextlib import closing
from datetime import datetime

TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"  # Token
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id,"hello")
# Helper function to connect to the database
def get_db_connection():
    return sqlite3.connect('library.db')

# Command to list available books
@bot.message_handler(commands=['bo'])
def list_books(message):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, title, author FROM books WHERE available = 1")
            books = cursor.fetchall()
            if books:
                response = "Available books:\n"
                for book in books:
                    response += f"{book[0]}. {book[1]} by {book[2]}\n"
            else:
                response = "No books are currently available."
        except Exception as e:
            response = "An error occurred while fetching books."
            print(e)

    bot.send_message(message.chat.id, response)



# Command to borrow a book
@bot.message_handler(commands=['bor'])
def borrow_book(message):
    try:
        book_id = int(message.text.split()[1])  # Extract the book ID from the message
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Please specify a valid book ID, e.g., /bor 1")
        return

    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()

        try:
            # Check if the book is available
            cursor.execute("SELECT title FROM books WHERE id = ? AND available = 1", (book_id,))
            book = cursor.fetchone()
            if not book:
                bot.send_message(message.chat.id, "This book is not available.")
                return

            # Mark the book as borrowed and add to borrowers list
            cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
            cursor.execute("INSERT INTO borrowers (user_id, username, book_id) VALUES (?, ?, ?)",
                           (message.from_user.id, message.from_user.username, book_id))
            conn.commit()
            bot.send_message(message.chat.id, f"You have successfully borrowed '{book[0]}'.")
        except Exception as e:
            bot.send_message(message.chat.id, "An error occurred while processing your request.")
            print(e)

# Command to return a book
@bot.message_handler(commands=['return'])
def return_book(message):
    try:
        book_id = int(message.text.split()[1])  # Extract the book ID from the message
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Please specify a valid book ID, e.g., /return 1")
        return

    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()

        try:
            # Check if the user has borrowed this book
            cursor.execute("SELECT title FROM books WHERE id = ? AND available = 0", (book_id,))
            book = cursor.fetchone()
            if not book:
                bot.send_message(message.chat.id, "This book is not borrowed by you or does not exist.")
                return

            # Mark the book as available and remove from borrowers list
            cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
            cursor.execute("DELETE FROM borrowers WHERE user_id = ? AND book_id = ?", (message.from_user.id, book_id))
            conn.commit()
            bot.send_message(message.chat.id, f"You have successfully returned '{book[0]}'.")
        except Exception as e:
            bot.send_message(message.chat.id, "An error occurred while processing your request.")
            print(e)

# Command to check borrowed books by user
@bot.message_handler(commands=['mybooks'])
def my_books(message):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()

        try:
            # Fetch all books borrowed by the user
            cursor.execute('''SELECT books.title FROM books
                              JOIN borrowers ON books.id = borrowers.book_id
                              WHERE borrowers.user_id = ?''', (message.from_user.id,))
            borrowed_books = cursor.fetchall()
            if borrowed_books:
                response = "Your borrowed books:\n"
                for book in borrowed_books:
                    response += f"- {book[0]}\n"
            else:
                response = "You haven't borrowed any books."
        except Exception as e:
            response = "An error occurred while fetching your borrowed books."
            print(e)

    bot.send_message(message.chat.id, response)

# Start the bot
bot.polling()
