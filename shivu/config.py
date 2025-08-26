class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "8195241636"
    sudo_users = "8195241636", "8195241636"
    GROUP_ID = -1002847095020
    TOKEN = "8319779558:AAEgds2ieL21JU-4J0nZhOJAz2_RfLi65nY"
    mongo_url = "mongodb+srv://ahaan:ahaad@ahaan.hgkeruq.mongodb.net/?retryWrites=true&w=majority&appName=ahaan"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "Collect_em_support"
    UPDATE_CHAT = "Collect_em_support"
    BOT_USERNAME = "Collect_Em_AllBot"
    CHARA_CHANNEL_ID = "-1002133191051"
    api_id = 22657083
    api_hash = "d6186691704bd901bdab275ceaab88f3"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
