from dotenv import load_dotenv
from os import getenv

load_dotenv()

class ModularBotConst:

    class Color:
        RANDOM: list[str] = ["ffe552", "ffc052",
                             "ff7d52", "ff5252", "ff5289", "ff5252"]
        SUCCESS: str = "198754"
        FAILED: str = "CA0B00"
        WARNING: str = "E49B0F"
        NEUTRAL: str = "0E86D4"

    class Image:
        RANDOM: list[str] = ["https://i.imgur.com/ImFzDtd.gif", "https://i.imgur.com/vSIWwxP.gif",
                             "https://i.imgur.com/tXnd4IZ.gif", "https://i.imgur.com/IverxEm.gif"]
        WELCOME_BANNER: str = "https://cdn.discordapp.com/attachments/709580371146047498/802553530460143636/Apq6gwr.png"
        LEAVE_BANNER: str = "https://cdn.discordapp.com/attachments/709580371146047498/802553806557544488/NlWRR4o.png"

    class LockDownTime:
        START: str = "Friday-09"
        END: str = "Friday-21"

    SERVER_NAME: str = "Kantin Yoyok"
    BOT_NAME: str = "Pak Yoyok"
    BOT_PREFIX: str = "!pkyyk"
    SERVER_ID: int = int(getenv('SERVER_ID'))
    TIMEZONE: str = "Asia/Jakarta"
    REQUEST_LIMIT: int = 2

    # Begin Environment Variable
    # TODO change it after debugging
    # TOKEN: str = getenv('TOKEN')
    TOKEN = open('TOKEN').readline()
    LAVALINK_SERVER: str = getenv('LAVALINK_SERVER')
    LAVALINK_PASSWORD: str = getenv('LAVALINK_PASSWORD')


class GuildChannel:
    BINCANG_HARAM_CHANNEL: int = int(getenv('BINCANG_HARAM_CHANNEL'))
    VERIFICATION_CHANNEL: int = int(getenv('VERIFICATION_CHANNEL'))
    INVITE_CHANNEL: int = int(getenv('INVITE_CHANNEL'))
    PRAYER_CHANNEL: int = int(getenv('PRAYER_CHANNEL'))
    WELCOME_CHANNEL: int = int(getenv('WELCOME_CHANNEL'))
    GOODBYE_CHANNEL: int = int(getenv('GOODBYE_CHANNEL'))

    MEMBER_ANALYTICS: int = int(getenv('MEMBER_ANALYTICS'))
    USER_ANALYTICS: int = int(getenv('USER_ANALYTICS'))
    BOT_ANALYTICS: int = int(getenv('BOT_ANALYTICS'))
    CHANNEL_ANALYTICS: int = int(getenv('CHANNEL_ANALYTICS'))
    ROLE_ANALYTICS: int = int(getenv('ROLE_ANALYTICS'))


class GuildRole:
    TETUA: int = int(getenv('TETUA'))
    THE_MUSKETEER: int = int(getenv('THE_MUSKETEER'))
    BOT: int = int(getenv('BOT'))
    MAGICIAN: int = int(getenv('MAGICIAN'))
    MUTE: int = int(getenv('MUTE'))


class GuildMessage:
    class Banner:
        WELCOME: str = f"Selamat Datang Di {ModularBotConst.SERVER_NAME}"
        LEAVE: str = "Al-Fatihah buat yang left"

    DM_MESSAGE: str = f"Selamat datang di **{ModularBotConst.SERVER_NAME}!**\n.\n.\n.\n.\n" \
        "**Kok cuma ada beberapa channel doang ?**\n" \
        f"kamu harus ***verifikasi dan baca rules*** di <#{GuildChannel.VERIFICATION_CHANNEL}>," \
        "kemudian **react rules dengan emot** :guard:\n" \
        f"degan begitu kamu setuju dengan rules kami, dan akan mendapat akses server **{ModularBotConst.SERVER_NAME}**\n\n" \
        "**Kalau mau invite temen pakai link mana ?**\n" \
        f"kalau mau ajak temen pakai link di <#{GuildChannel.INVITE_CHANNEL}>\n\n" \
        f"*Semoga betah ya di sini \ ya* :blush:\n\n\nSalam **{ModularBotConst.BOT_NAME}**"
    LOCKDOWN_FEATURE: str = "Hanya Mengingatkan..."


class Expression:
    BAD_WORDS_REGEX: str = getenv('BAD_WORDS_REGEX')
    STRESS_WORDS_REGEX: str = getenv('STRESS_WORDS_REGEX')
    HOLY_WORDS_REGEX: str = getenv('HOLY_WORDS_REGEX')
    RANDOM_EXPRESSION: list[str] = ["Gabut aja....", "Gua ngak tau", "Lah ngatur",
                                    "Gitu doang baper", "Suka-suka", "Gay", "Biadab", "Sok asik"]
