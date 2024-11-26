import unittest
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

if __name__ == "__main__":
    unittest.main()
