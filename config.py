from os import getenv

class ModularBotConst:
    SERVER_NAME = "Kantin Yoyok"
    BOT_NAME = "Pak Yoyok"
    BOT_PREFIX = "!pkyyk"
    SERVER_ID = 623123009770749974
    TIMEZONE = "Asia/Jakarta"
    REQUEST_LIMIT = 2
    COLOR = {
        'random_array': ["ffe552", "ffc052", "ff7d52", "ff5252", "ff5289", "ff5252"],
        'success': '198754',
        'failed': 'CA0B00',
        'queue': '0E86D4',
        'play': 'E49B0F'
    }
    IMAGE = {
        'random_array': ["https://i.imgur.com/ImFzDtd.gif", "https://i.imgur.com/vSIWwxP.gif", "https://i.imgur.com/tXnd4IZ.gif", "https://i.imgur.com/IverxEm.gif"],
        'welcome_banner': "https://cdn.discordapp.com/attachments/709580371146047498/802553530460143636/Apq6gwr.png",
        'leave_banner': "https://cdn.discordapp.com/attachments/709580371146047498/802553806557544488/NlWRR4o.png"
    }

    #Begin Environment Variable
    #TODO change it after debugging
    TOKEN = getenv("TOKEN")
    # TOKEN = open("TOKEN").readline()
    SPOTIFY_CLIENT = getenv('SPOTIFY_CLIENT')
    SPOTIFY_SECRET = getenv('SPOTIFY_SECRET')
    LAVALINK_SERVER = getenv("LAVALINK_SERVER")
    LAVALINK_PASSWORD = getenv("LAVALINK_PASSWORD")



class GuildChannel:
    BINCANG_HARAM_CHANNEL = 783138508038471701
    VERIFICATION_CHANNEL = 811292476806660107
    INVITE_CHANNEL = 746678416434003998
    PRAYER_CHANNEL = 832276804189945857
    WELCOME_CHANNEL = 728584639475613736
    GOODBYE_CHANNEL = 768133346278244402

    MEMBER_ANALYTICS = 788003407834906664
    USER_ANALYTICS = 788003408006217749
    BOT_ANALYTICST = 788003408846127154
    CHANNEL_ANALYTICS = 788003409327685642
    ROLE_ANALYTICS = 788003409797840926


class GuildRole:
    TETUA = 758206420503494657
    THE_MUSKETEER = 684600810520182892
    BOT = 684600176303669260
    MAGICIAN = 728203532678725753
    MUTE = 1043875115932319865


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
    RANDOM_EXPRESSION = ["Gabut aja....", "Gua ngak tau", "Lah ngatur",
                         "Gitu doang baper", "Suka-suka", "Gay", "Biadab", "Sok asik"]
