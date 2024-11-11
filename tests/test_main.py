from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
import telebot
from main import about, list_books, return_book, verify_admin_password, ask_student_name, borrow_book_step_3, finalize_borrow_book

class TestTelegramBot(unittest.TestCase):

    def setUp(self):
        self.bot = telebot.TeleBot("fake_token")
        self.bot.send_message = MagicMock()
        self.bot.reply_to = MagicMock()
        
        self.message = MagicMock()
        self.message.chat.id = 123456789
        self.message.from_user.id = 1234  # Mocking user ID for students dictionary

        # Mock for students dictionary to simulate storing student names
        self.students = {}

    @patch('main.bot', new_callable=lambda: MagicMock())
    def test_about_developer(self, mock_bot):
        about(self.message)
        mock_bot.reply_to.assert_called_once()

    @patch('main.bot', new_callable=lambda: MagicMock())
    def test_list_books(self, mock_bot):
        list_books(self.message)
        mock_bot.send_message.assert_called_once()

    @patch('main.bot', new_callable=lambda: MagicMock())
    def test_borrow_book(self, mock_bot):
        self.message.text = "Harry Potter 1"
        student_name = "Test Student"
        # Set up the mock for `ask_student_name` to register the student name.
        ask_student_name(self.message)
        
        # Mock the student name storage in self.students
        self.students[self.message.from_user.id] = student_name
        
        # Now finalize the borrow process with the book name
        finalize_borrow_book(self.message)
        
        # Assert that a message confirming the borrowing was sent
        mock_bot.send_message.assert_any_call(self.message.chat.id, f"You have borrowed '{self.message.text}'. Please return it by ")

    @patch('main.datetime', autospec=True)
    @patch('main.bot', new_callable=lambda: MagicMock())
    def test_return_book_on_time(self, mock_bot, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 11, 1, 12, 0, 0)
        return_book(self.message)
        mock_bot.send_message.assert_called_once()

    @patch('main.bot', new_callable=lambda: MagicMock())
    def test_verify_admin_password_success(self, mock_bot):
        self.message.text = "12345"
        verify_admin_password(self.message)
        mock_bot.send_message.assert_called_once()

    @patch('main.bot', new_callable=lambda: MagicMock())
    def test_verify_admin_password_failure(self, mock_bot):
        self.message.text = "wrong_password"
        verify_admin_password(self.message)
        mock_bot.send_message.assert_called_once()

if __name__ == '__main__':
    unittest.main()
