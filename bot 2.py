import os
from anthropic import AsyncAnthropic
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          MessageHandler, filters, ContextTypes)

BOT_TOKEN = os.environ["BOT_TOKEN"]
MY_ID = int(os.environ.get("MY_TG_ID", "0"))
MODEL = os.getenv("MODEL", "claude-sonnet-5-5")

client = AsyncAnthropic()  # ANTHROPIC_API_KEY ni o'zi oladi
SYSTEM = (
    "Sen mening shaxsiy yordamchimsan. O'zbek tilida, qisqa va aniq javob ber. "
    "Matn, chat yoki xabarlarni tahlil qilib xulosa ber, kerak bo'lsa javob yozib ber."
)
history = []


async def my_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Hamma uchun ochiq: ID'ingizni bilish uchun
    await update.message.reply_text(f"Sizning ID: {update.effective_user.id}")


async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MY_ID:
        return
    history.clear()
    await update.message.reply_text("Suhbat tozalandi.")


async def reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MY_ID:
        return  # begonalarga javob bermaydi
    history.append({"role": "user", "content": update.message.text})
    # oxirgi 20 ta xabarni saqlaymiz, "user" bilan boshlanishi shart
    del history[:-20]
    while history and history[0]["role"] != "user":
        history.pop(0)
    try:
        msg = await client.messages.create(
            model=MODEL, max_tokens=1500, system=SYSTEM, messages=history
        )
        text = msg.content[0].text
    except Exception as e:
        history.pop()
        await update.message.reply_text(f"Xato: {type(e).__name__}")
        return
    history.append({"role": "assistant", "content": text})
    for i in range(0, len(text), 4000):
        await update.message.reply_text(text[i:i + 4000])


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("id", my_id))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app.run_polling()
