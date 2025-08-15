import telebot
from telebot import types

TOKEN = "8013244955:AAFDQjLpxvoUrXBdFqmRuKx4FMxJjc_W7Tw"
bot = telebot.TeleBot(TOKEN)

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
