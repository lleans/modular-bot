from dotenv import load_dotenv
from os import getenv

load_dotenv()

class ModularBotConst:
    SERVER_NAME = "Kantin Yoyok"
    BOT_NAME = "Pak Yoyok"
    BOT_PREFIX = "!pkyyk"
    SERVER_ID = int(getenv('SERVER_ID'))
    TIMEZONE = "Asia/Jakarta"
    LOCKDOWN_TIME = {
        'start': "Friday-09",
        'end': "Friday-21"
    }
    REQUEST_LIMIT = 2
    COLOR = {
        'random_array': ["ffe552", "ffc052", "ff7d52", "ff5252", "ff5289", "ff5252"],
        'success': "198754",
        'failed': "CA0B00",
        'queue': "0E86D4",
        'play': "E49B0F"
    }
    IMAGE = {
        'random_array': ["https://i.imgur.com/ImFzDtd.gif", "https://i.imgur.com/vSIWwxP.gif", "https://i.imgur.com/tXnd4IZ.gif", "https://i.imgur.com/IverxEm.gif"],
        'welcome_banner': "https://cdn.discordapp.com/attachments/709580371146047498/802553530460143636/Apq6gwr.png",
        'leave_banner': "https://cdn.discordapp.com/attachments/709580371146047498/802553806557544488/NlWRR4o.png"
    }

    # Begin Environment Variable
    # TODO change it after debugging
    TOKEN = getenv('TOKEN')
    # TOKEN = open('TOKEN').readline()
    SPOTIFY_CLIENT = getenv('SPOTIFY_CLIENT')
    SPOTIFY_SECRET = getenv('SPOTIFY_SECRET')
    MUSIXMATCH_KEY = getenv('MUSIXMATCH_KEY')
    LAVALINK_SERVER = getenv('LAVALINK_SERVER')
    LAVALINK_PASSWORD = getenv('LAVALINK_PASSWORD')


class GuildChannel:
    BINCANG_HARAM_CHANNEL = int(getenv('BINCANG_HARAM_CHANNEL'))
    VERIFICATION_CHANNEL = int(getenv('VERIFICATION_CHANNEL'))
    INVITE_CHANNEL = int(getenv('INVITE_CHANNEL'))
    PRAYER_CHANNEL = int(getenv('PRAYER_CHANNEL'))
    WELCOME_CHANNEL = int(getenv('WELCOME_CHANNEL'))
    GOODBYE_CHANNEL = int(getenv('GOODBYE_CHANNEL'))

    MEMBER_ANALYTICS = int(getenv('MEMBER_ANALYTICS'))
    USER_ANALYTICS = int(getenv('USER_ANALYTICS'))
    BOT_ANALYTICS = int(getenv('BOT_ANALYTICS'))
    CHANNEL_ANALYTICS = int(getenv('CHANNEL_ANALYTICS'))
    ROLE_ANALYTICS = int(getenv('ROLE_ANALYTICS'))


class GuildRole:
    TETUA = int(getenv('TETUA'))
    THE_MUSKETEER = int(getenv('THE_MUSKETEER'))
    BOT = int(getenv('BOT'))
    MAGICIAN = int(getenv('MAGICIAN'))
    MUTE = int(getenv('MUTE'))


class GuildMessage:
    DM_MESSAGE = f"Selamat datang di **{ModularBotConst.SERVER_NAME}!**\n.\n.\n.\n.\n" \
        "**Kok cuma ada beberapa channel doang ?**\n" \
        f"kamu harus ***verifikasi dan baca rules*** di <#{GuildChannel.VERIFICATION_CHANNEL}>," \
        "kemudian **react rules dengan emot** :guard:\n" \
        f"degan begitu kamu setuju dengan rules kami, dan akan mendapat akses server **{ModularBotConst.SERVER_NAME}**\n\n" \
        "**Kalau mau invite temen pakai link mana ?**\n" \
        f"kalau mau ajak temen pakai link di <#{GuildChannel.INVITE_CHANNEL}>\n\n" \
        f"*Semoga betah ya di sini \ ya* :blush:\n\n\nSalam **{ModularBotConst.BOT_NAME}**"
    LOCKDOWN_FEATURE = "Hanya Mengingatkan..."
    BANNER = {
        'welcome_banner': f"Selamat Datang Di {ModularBotConst.SERVER_NAME}",
        'leave_banner': "Al-Fatihah buat yang left"
    }


class Expression:
    BAD_WORDS_REGEX = getenv('BAD_WORDS_REGEX')
    STRESS_WORDS_REGEX = getenv('STRESS_WORDS_REGEX')
    HOLY_WORDS_REGEX = getenv('HOLY_WORDS_REGEX')
    RANDOM_EXPRESSION = ["Gabut aja....", "Gua ngak tau", "Lah ngatur",
                         "Gitu doang baper", "Suka-suka", "Gay", "Biadab", "Sok asik"]
