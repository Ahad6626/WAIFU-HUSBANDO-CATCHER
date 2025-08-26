from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from itertools import groupby
from html import escape
import math

from shivu import collection, user_collection, application


async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id

    user = await user_collection.find_one({'id': user_id})
    if not user:
        if update.message:
            await update.message.reply_text('You Have Not Guessed any Characters Yet..')
        else:
            await update.callback_query.edit_message_text('You Have Not Guessed any Characters Yet..')
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}

    unique_characters = list({character['id']: character for character in characters}.values())

    total_pages = max(1, math.ceil(len(unique_characters) / 15))
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"<b>{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}</b>\n"

    current_characters = unique_characters[page*15:(page+1)*15]
    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, chars in current_grouped_characters.items():
        harem_message += f'\n<b>{anime} {len(chars)}/{await collection.count_documents({"anime": anime})}</b>\n'
        for character in chars:
            count = character_counts[character['id']]
            harem_message += f'{character["id"]} {character["name"]} ×{count}\n'

    total_count = len(user['characters'])
    keyboard = [[InlineKeyboardButton(f"See Collection ({total_count})", callback_data=f"collection.{user_id}")]]

    if update.message:
        await update.message.reply_text(harem_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(harem_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


async def collection_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = int(query.data.split(".")[1])

    if query.from_user.id != user_id:
        await query.answer("This is not your collection!", show_alert=True)
        return

    user = await user_collection.find_one({'id': user_id})
    if not user or not user.get("characters"):
        await query.answer("You don’t have any characters yet!", show_alert=True)
        return

    # Prepare popup details (limit to 10 so it fits Telegram alerts)
    details = []
    for char in user["characters"][:10]:
        details.append(f"{char['name']} ({char['anime']})")

    popup_text = "\n".join(details)
    if len(user["characters"]) > 10:
        popup_text += f"\n... and {len(user['characters']) - 10} more!"

    await query.answer(popup_text, show_alert=True)


# Register handlers
application.add_handler(CommandHandler("collection", harem))
application.add_handler(CallbackQueryHandler(collection_callback, pattern=r"^collection\.\d+$"))
