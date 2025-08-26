class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "8195241636"
    sudo_users = "8195241636", "7694170809"
    GROUP_ID = -1002847095020
    TOKEN = "8267678007:AAE5G5WTjqaVnFWzd2u38Rdv2-PK8GrS9o4"
    mongo_url = "mongodb+srv://ahaan:ahaad@ahaan.hgkeruq.mongodb.net/?retryWrites=true&w=majority&appName=ahaan"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "IvanxNisha"
    UPDATE_CHAT = "BotsxUpdate"
    BOT_USERNAME = "PreetixMusic_bot"
    CHARA_CHANNEL_ID = "-1002946229785"
    api_id = 22657083
    api_hash = "d6186691704bd901bdab275ceaab88f3"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
