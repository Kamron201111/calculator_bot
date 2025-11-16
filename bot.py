import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import math

# ====== TOKEN ======
BOT_TOKEN = "7810689974:AAHzwtsWmWAKT7UfcNjAF884pb3rTT8gfag"

# ====== LOGGING ======
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Salom {update.effective_user.first_name}!\n"
        f"Men Kamron Super Kalkulyator botiman.\n"
        f"Hisoblash: /calc 2+2*3"
    )

# ====== CALCULATOR ======
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠ Misol kiriting!\nMasalan: /calc 2+2*3")
        return

    expr = " ".join(context.args)

    try:
        result = eval(expr, {
            "__builtins__": None,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
            "log": math.log,
            "log10": math.log10
        })

        await update.message.reply_text(f"📘 Natija:\n`{result}`", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: noto‘g‘ri formula!")

# ====== GROUP WELCOME ======
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        name = user.first_name
        await update.message.reply_text(f"🎉 Xush kelibsiz, *{name}*!", parse_mode="Markdown")

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc))

    # Guruhga yangi odam kirsa
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    app.run_polling()

if __name__ == "__main__":
    main()
