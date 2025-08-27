import unittest
from unittest.mock import MagicMock, patch
import main


class TestStart(unittest.TestCase):
    
    @patch("main.bot.send_message")
    def test_start_handler(self, mock_message):
        msg = MagicMock()
        msg.chat.id = 90
        msg.from_user.id = 90
        main.users = {}
        main.start(msg)
        self.assertEqual(mock_message.call_count, 2)
        welcome_text = mock_message.call_args_list[0][0][1]
        self.assertIn("Hi! This bot lets you borrow books and read them.", welcome_text)



class TestRegister(unittest.TestCase):

    @patch("main.bot.send_message")
    def test_register_feature(self,mock_message):
        message = MagicMock()
        message.chat.id = 809
        message.from_user.id = 809
        main.users = {}
        main.register(message)
        self.assertTrue(mock_message.called)
        args, _ = mock_message.call_args
        self.assertEqual(args[0], 809)
        self.assertIn("Enter your name:", args[1])

class TestBorrowHandler(unittest.TestCase):

    @patch("main.bot.send_message")
    def test_borrowing(self, mock_message):
        message = MagicMock()
        message.chat.id = 9090
        message.from_user.id = 9090
        main.users = {}
        main.books = []
        main.borrowing_book(message)
        self.assertTrue(mock_message.called)
        args, _ = mock_message.call_args
        self.assertEqual(args[0], 9090)
        self.assertIn("Enter the book ID or name to borrow: ", args[1])


class TestAdminPage(unittest.TestCase):

    @patch("main.bot.send_message")
    def test_admin(self, mock_message):
        message = MagicMock()
        message.chat.id = 12
        message.from_user.id = 12
        main.users = {}
        main.books = []
        main.admins = {}
        main.admin_panel_btns(message)
        self.assertTrue(mock_message.called)
        args, _ = mock_message.call_args
        self.assertEqual(args[0], 12)
        self.assertIn("Please Choose the Option:", args[1])




class TestReturnBook(unittest.TestCase):

    @patch("main.bot.send_message")
    def test_return(self, mock_message):
        message = MagicMock()
        message.chat.id = 2
        message.from_user.id = 2
        main.users = {}
        main.books = []
        main.return_book(message)
        self.assertTrue(mock_message.called)
        args, _ = mock_message.call_args
        self.assertEqual(args[0], 2)
        self.assertIn("Enter the Book ID or Title you want to return:", args[1])