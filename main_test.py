import unittest
from unittest.mock import MagicMock
from main import * 

#Unit test
books = [
    {"id": 1, "name": "A Big Ball of String", "author": "Marion Holland", "status": "Available"},
    {"id": 2, "name": "A Child’s Garden of Versus (orange book)", "author": "Robert Louis Stevenson", "status": "Available"},
    {"id": 45, "name": "Fables", "author": "Arnold Lobel", "status": "Available"},
]

class TestBooks(unittest.TestCase):
    def test_book_structure(self):
        for book in books:
            self.assertIn("id", book)
            self.assertIn("name", book)
            self.assertIn("author", book)
            self.assertIn("status", book)

    def test_book_data(self):
        # Find the book with id 1
        book = next((b for b in books if b["id"] == 1), None)
        self.assertIsNotNone(book, "Book with id 1 not found")
        self.assertEqual(book["name"], "A Big Ball of String")
        self.assertEqual(book["author"], "Marion Holland")
        self.assertEqual(book["status"], "Available")

    def test_unique_ids(self):
        
        ids = [book["id"] for book in books]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate book IDs found")


class TestSearchBooks(unittest.TestCase):
    def setUp(self):
        # Mock the bot to avoid actual Telegram API calls
        self.mock_bot = MagicMock()
        self.mock_message = MagicMock()
        self.mock_message.chat.id = 123456  # Simulating a chat ID

        # Sample books data
        self.books = [
            {"id": 1, "name": "The Great Gatsby", "author": "F. Scott Fitzgerald", "status": "Available"},
            {"id": 2, "name": "To Kill a Mockingbird", "author": "Harper Lee", "status": "Checked Out"},
            {"id": 3, "name": "1984", "author": "George Orwell", "status": "Available"}
        ]

    def test_search_books_found(self):
        # Simulate a search for books containing the word 'great'
        keyword = 'great'
        expected_response = "🔍 Search results:\n\n📘 ID: 1 | The Great Gatsby by F. Scott Fitzgerald - Status: Available\n"
        
        # Set up the function to process the search
        bot.register_next_step_handler(self.mock_message, lambda message: process_search(message))
        self.mock_message.text = keyword
        process_search(self.mock_message)
        
        # Assert that bot sends the correct response
        self.mock_bot.send_message.assert_called_with(self.mock_message.chat.id, expected_response)

    def test_search_books_not_found(self):
        # Simulate a search with no matching books
        keyword = 'nonexistent'
        expected_response = "❌ No books found matching your search. Try another keyword."
        
        # Set up the function to process the search
        bot.register_next_step_handler(self.mock_message, lambda message: process_search(message))
        self.mock_message.text = keyword
        process_search(self.mock_message)
        
        # Assert that bot sends the "no results" response
        self.mock_bot.send_message.assert_called_with(self.mock_message.chat.id, expected_response)

    def test_search_books_empty_keyword(self):
        # Simulate a search with an empty keyword
        keyword = ''
        expected_response = "❌ No books found matching your search. Try another keyword."
        
        # Set up the function to process the search
        bot.register_next_step_handler(self.mock_message, lambda message: process_search(message))
        self.mock_message.text = keyword
        process_search(self.mock_message)
        
        # Assert that bot sends the "no results" response
        self.mock_bot.send_message.assert_called_with(self.mock_message.chat.id, expected_response)


if __name__ == "__main__":
    unittest.main()
