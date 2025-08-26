import urllib.request
from pymongo import ReturnDocument

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, sudo_users, collection, db, CHARA_CHANNEL_ID, SUPPORT_CHAT

WRONG_FORMAT_TEXT = """Wrong ❌️ format...  
Example:  
`/upload Img_url muzan-kibutsuji Demon-slayer 3`

Format:  
`img_url character-name anime-name rarity-number`

Use rarity number according to rarity map:  
1 = ⚪ Common  
2 = 🟣 Rare  
3 = 🟡 Legendary  
4 = 🟢 Medium
"""

# Auto incrementing sequence for IDs
async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({"_id": sequence_name, "sequence_value": 0})
        return 0
    return sequence_document["sequence_value"]

# -------- UPLOAD -------- #
async def upload(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("Ask My Owner...")
        return

    args = context.args
    if len(args) != 4:
        await update.message.reply_text(WRONG_FORMAT_TEXT)
        return

    img_url = args[0]
    character_name = args[1].replace("-", " ").title()
    anime = args[2].replace("-", " ").title()

    # Validate image URL
    try:
        urllib.request.urlopen(img_url)
    except:
        await update.message.reply_text("Invalid URL.")
        return

    # Validate rarity
    rarity_map = {
        1: "⚪ Common",
        2: "🟣 Rare",
        3: "🟡 Legendary",
        4: "🟢 Medium"
    }
    try:
        rarity = rarity_map[int(args[3])]
    except Exception:
        await update.message.reply_text("Invalid rarity. Please use 1, 2, 3, or 4.")
        return

    # Generate ID
    id = str(await get_next_sequence_number("character_id")).zfill(2)

    character = {
        "img_url": img_url,
        "name": character_name,
        "anime": anime,
        "rarity": rarity,
        "id": id
    }

    try:
        message = await context.bot.send_photo(
            chat_id=CHARA_CHANNEL_ID,
            photo=img_url,
            caption=f"<b>Character Name:</b> {character_name}\n"
                    f"<b>Anime Name:</b> {anime}\n"
                    f"<b>Rarity:</b> {rarity}\n"
                    f"<b>ID:</b> {id}\n"
                    f"Added by <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
            parse_mode="HTML"
        )
        character["message_id"] = message.message_id
        await collection.insert_one(character)
        await update.message.reply_text("✅ CHARACTER ADDED....")
    except:
        await collection.insert_one(character)
        await update.message.reply_text(
            "Character added but no database channel found. Consider adding one."
        )

# -------- DELETE -------- #
async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("Ask my Owner to use this Command...")
        return

    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Incorrect format... Please use: /delete ID")
        return

    character = await collection.find_one_and_delete({"id": args[0]})

    if character:
        try:
            await context.bot.delete_message(
                chat_id=CHARA_CHANNEL_ID,
                message_id=character["message_id"]
            )
            await update.message.reply_text("✅ Deleted successfully")
        except:
            await update.message.reply_text(
                "Deleted from DB, but message not found in channel."
            )
    else:
        await update.message.reply_text("Character not found.")

# -------- UPDATE -------- #
async def update_character(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Incorrect format. Please use: /update id field new_value")
        return

    char_id, field, value = args[0], args[1], args[2]

    # Get character
    character = await collection.find_one({"id": char_id})
    if not character:
        await update.message.reply_text("Character not found.")
        return

    # Valid fields
    valid_fields = ["img_url", "name", "anime", "rarity"]
    if field not in valid_fields:
        await update.message.reply_text(
            f"Invalid field. Use one of: {', '.join(valid_fields)}"
        )
        return

    # Handle formatting
    if field in ["name", "anime"]:
        new_value = value.replace("-", " ").title()
    elif field == "rarity":
        rarity_map = {
            1: "⚪ Common",
            2: "🟣 Rare",
            3: "🟡 Legendary",
            4: "🟢 Medium"
        }
        try:
            new_value = rarity_map[int(value)]
        except Exception:
            await update.message.reply_text("Invalid rarity. Use 1, 2, 3, or 4.")
            return
    else:
        new_value = value

    # Update DB
    await collection.find_one_and_update({"id": char_id}, {"$set": {field: new_value}})

    try:
        if field == "img_url":
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character["message_id"])
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=new_value,
                caption=f"<b>Character Name:</b> {character['name']}\n"
                        f"<b>Anime Name:</b> {character['anime']}\n"
                        f"<b>Rarity:</b> {character['rarity']}\n"
                        f"<b>ID:</b> {character['id']}\n"
                        f"Updated by <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode="HTML"
            )
            await collection.find_one_and_update(
                {"id": char_id}, {"$set": {"message_id": message.message_id}}
            )
        else:
            await context.bot.edit_message_caption(
                chat_id=CHARA_CHANNEL_ID,
                message_id=character["message_id"],
                caption=f"<b>Character Name:</b> {character['name'] if field!='name' else new_value}\n"
                        f"<b>Anime Name:</b> {character['anime'] if field!='anime' else new_value}\n"
                        f"<b>Rarity:</b> {character['rarity'] if field!='rarity' else new_value}\n"
                        f"<b>ID:</b> {character['id']}\n"
                        f"Updated by <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode="HTML"
            )
        await update.message.reply_text("✅ Update successful. (Sometimes caption takes time to refresh)")
    except Exception as e:
        await update.message.reply_text(
            f"Update failed. Possible reasons: Bot not in channel, old message, or wrong ID.\nError: {e}"
        )

# -------- HANDLERS -------- #
UPLOAD_HANDLER = CommandHandler("upload", upload, block=False)
application.add_handler(UPLOAD_HANDLER)

DELETE_HANDLER = CommandHandler("delete", delete, block=False)
application.add_handler(DELETE_HANDLER)

UPDATE_HANDLER = CommandHandler("update", update_character, block=False)
application.add_handler(UPDATE_HANDLER)
