import logging
import math
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ====== SOZLAMALAR ======
BOT_TOKEN = "7810689974:AAHzwtsWmWAKT7UfcNjAF884pb3rTT8gfag"
WEBAPP_URL = "https://kamron201111.github.io/web3-calc_bot/"

# Har bir user uchun kalkulyator ifodasi
USER_EXPR: dict[int, str] = {}

# ====== LOGGING ======
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ============= YORDAMCHI FUNKSIYALAR =============

def build_calc_keyboard() -> InlineKeyboardMarkup:
    """Kalkulyator uchun knopkalar."""
    rows = [
        [
            InlineKeyboardButton("7", callback_data="calc:7"),
            InlineKeyboardButton("8", callback_data="calc:8"),
            InlineKeyboardButton("9", callback_data="calc:9"),
            InlineKeyboardButton("⌫", callback_data="calc:bksp"),
        ],
        [
            InlineKeyboardButton("4", callback_data="calc:4"),
            InlineKeyboardButton("5", callback_data="calc:5"),
            InlineKeyboardButton("6", callback_data="calc:6"),
            InlineKeyboardButton("÷", callback_data="calc:/"),
        ],
        [
            InlineKeyboardButton("1", callback_data="calc:1"),
            InlineKeyboardButton("2", callback_data="calc:2"),
            InlineKeyboardButton("3", callback_data="calc:3"),
            InlineKeyboardButton("×", callback_data="calc:*"),
        ],
        [
            InlineKeyboardButton("0", callback_data="calc:0"),
            InlineKeyboardButton(".", callback_data="calc:."),
            InlineKeyboardButton("+", callback_data="calc:+"),
            InlineKeyboardButton("-", callback_data="calc:-"),
        ],
        [
            InlineKeyboardButton("🧹 Clear", callback_data="calc:clear"),
            InlineKeyboardButton("=", callback_data="calc:eq"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def calc_text(expr: str) -> str:
    """Kalkulyator ekrandagi matn."""
    if expr == "":
        expr_disp = "0"
    else:
        expr_disp = expr
    return (
        "🧮 *Kamron Calculator*\n\n"
        "Ifoda: `{}`\n"
        "👇 Tugmalardan foydalaning.".format(expr_disp)
    )


def is_safe_expr(expr: str) -> bool:
    """eval uchun ruxsat etilgan belgilarnigina qoldiramiz."""
    allowed = set("0123456789+-*/(). ")
    return set(expr).issubset(allowed)


# ============= HANDLERLAR =============

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚀 Web3 Super DApp", url=WEBAPP_URL)],
            [InlineKeyboardButton("🧮 Kalkulyator", callback_data="calc:open")],
        ]
    )

    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n"
        "Bu *Kamron Web3 Super DApp* bot.\n"
        "Pastdagi tugma orqali saytingga kira olasan,\n"
        "yoki knopkali kalkulyatorni ishlat.",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


# /calc komandasi – kalkulyatorni darhol ochish
async def cmd_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_EXPR[user_id] = ""
    await update.message.reply_text(
        calc_text(USER_EXPR[user_id]),
        reply_markup=build_calc_keyboard(),
        parse_mode="Markdown",
    )


# Kalkulyator knopkalari uchun callback
async def calc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data  # masalan: "calc:7", "calc:+", "calc:eq"
    _, action = data.split(":", 1)

    # Agar startdagi "Kalkulyator" tugmasi bosilsa
    if action == "open":
        USER_EXPR[user_id] = USER_EXPR.get(user_id, "")
        await query.edit_message_text(
            calc_text(USER_EXPR[user_id]),
            reply_markup=build_calc_keyboard(),
            parse_mode="Markdown",
        )
        return

    expr = USER_EXPR.get(user_id, "")

    if action == "clear":
        expr = ""
    elif action == "bksp":
        expr = expr[:-1]
    elif action == "eq":
        if not expr:
            await query.answer("Hech narsa kiritilmagan.")
        elif not is_safe_expr(expr):
            expr = ""
            await query.answer("Ruxsat etilmagan belgi!")
        else:
            try:
                # Matematik ifodani hisoblash
                result = eval(expr, {"__builtins__": None}, {})
                expr = str(result)
                await query.answer(f"Natija: {expr}")
            except Exception:
                expr = ""
                await query.answer("Xato ifoda!")
    else:
        # Raqam va operatorlar qo‘shish
        expr += action

    USER_EXPR[user_id] = expr

    try:
        await query.edit_message_text(
            calc_text(expr),
            reply_markup=build_calc_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning("edit_message_text xatosi: %s", e)


# Guruhga yangi odam kirsa – salomlashish
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    for user in message.new_chat_members:
        if user.username:
            name = f"@{user.username}"
        else:
            name = user.first_name
        await message.reply_text(f"Xush kelibsiz, {name}!")


# ============= MAIN =============

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Komandalar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", cmd_calc))

    # Callbacklar (kalkulyator)
    app.add_handler(CallbackQueryHandler(calc_callback, pattern=r"^calc:"))

    # Guruhga yangi kirganlarga salom
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
