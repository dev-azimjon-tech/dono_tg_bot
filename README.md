# Dono Telegram Bot

A Telegram bot for the **Nasli Dono Library** (or any other online library).

---

## 📌 Features

- **User Registration**  
  Users can register by providing their phone number, name, and password.  
  (If possible, the bot automatically retrieves the profile information from Telegram.)

- **Borrowing Books**  
  The bot checks if a book is available. If available, the user sets a return date.

- **Returning Books**  
  Books can be marked as returned by either the user or the admin.

- **Reminders for Borrowed Books**  
  A background function runs every hour and checks if the return date has passed.  
  If overdue, the bot automatically sends a reminder message to the user.

- **Advertisements**  
  Users can send advertisement requests/messages directly to the admin.

---

## 🚀 Notes
- Designed with simplicity and flexibility to be adapted for different libraries.  
- JSON or database storage can be used for managing users and books.  
- Built with **PyTelegramBotAPI**.

