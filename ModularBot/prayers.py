from random import choice
from discord import Embed
from aiohttp import ClientSession
from datetime import datetime
from typing import Union

from .util import ModularUtil
from const import ModularBotConst


class Prayers:
    __PRAYER_LOCATION = "Surabaya"

    __PRAYER_API = "https://muslim-pro-api-lleans.koyeb.app"
    __BUKA_IMAGE = ["https://i.imgur.com/1uVOu9s.gif", "https://i.imgur.com/lrrIzRY.gif",
                    "https://i.imgur.com/eWe8VvA.gif", "https://i.imgur.com/gFVKP74.gif",
                    "https://files.catbox.moe/un72tu.gif", "https://files.catbox.moe/v0uqbp.gif",
                    "https://files.catbox.moe/bbps8x.gif"]
    __SHALAT_IMAGE = ["https://i.imgur.com/I24KR5n.gif", "https://i.imgur.com/L2Yk6a2.gif",
                    "https://i.imgur.com/cRJQcfJ.gif", "https://i.imgur.com/IV5Nadb.gif",
                    "https://files.catbox.moe/d0a54j.gif", "https://files.catbox.moe/erh51k.gif",
                    "https://files.catbox.moe/tdml0y.gif"]

    __QUOTES = ["`Salah satu dosa terburuk adalah seseorang yang menganggap remeh dosanya. \n\n- Abu Bakar Asshidiq`",
                "`Tidak boleh seorang muslim menghina muslim yang lain. Yang kecil pada kaum muslimin, adalah besar pada sisi Allah. \n\n- Abu Bakar Asshidiq`",
                "`YBuatlah tujuan untuk hidup, kemudian gunakan segenap kekuatan untuk mencapainya, kamu pasti berhasil. \n\n- Ustman Bin Affan`",
                "`Jangan pernah membuat keputusan dalam kemarahan dan jangan pernah membuat janji dalam kebahagiaan. \n\n- Ali Bin Abi Thalib`",
                "`Memang sulit untuk bersabar, tapi menyia-nyiakan pahala dari sebuah kesabaran itu jauh lebih buruk. \n\n- Abu Bakar Ash-Shiddiq`",
                "`Terkadang, orang dengan masa lalu paling kelam akan menciptakan masa depan yang paling cerah. \n\n- Umar bin Khattab`",
                "`Jangan bersedih atas apa yang telah berlalu, kecuali kalau itu bisa membuatmu bekerja lebih keras untuk apa yang akan datang. \n\n- Umar bin Khattab`",
                "`Biasakan diri dengan hidup susah, karena kesenangan tidak akan kekal selamanya. \n\n- Umar bin Khattab`"]

    @classmethod
    async def get_prayertime(cls, session: ClientSession) -> Union[dict, None]:
        async with session.get(cls.__PRAYER_API+"/"+cls.__PRAYER_LOCATION) as resp:
            if resp.status == 200:
                resp: dict = await resp.json()
                time: datetime = ModularUtil.get_time()
                res: dict = {}
                res.update(resp['praytimes'][time.strftime('%a %d %b')])
                res.update({
                    'ramadhan': resp['ramadhan'][time.strftime('%Y')]
                })
                return res
            return 
            

    @classmethod
    def prayers_generator(cls, praytimes: dict, time: datetime) -> Union[Embed, None]:
        e: Embed = None
        for pray, prayt in praytimes.items():
            if prayt == time.strftime('%H:%M'):
                e = Embed(color=ModularUtil.convert_color(choice(ModularBotConst.COLOR['random_array'])))
                e.set_image(url=choice(cls.__SHALAT_IMAGE))
                if pray == "Maghrib":
                    e.title = f"Waktu Berbuka untuk area {ModularBotConst.__PRAYER_LOCATION} dan sekitarnya"
                    e.description = f"Selamat berbuka puasa, bersyukurlah kalian bisa berbuka dengan makanan enak diluar sana masih banyak yang belum bisa kayak kamu, " \
                        "jadi tetaplah bersyukur walaupun kamu buka dengan tahu tempe :).\nJangan lupa salat Maghrib habis buka.\n\n **Quote hari ini**\n" \
                        f"{choice(cls.__QUOTES)}\n\n**Jadwal shalat hari ini:**"
                    e.set_image(url=choice(cls.__BUKA_IMAGE))
                elif pray == "Isya" or pray == "Isha'a":
                    e.title = f"Waktu Terawih untuk area {ModularBotConst.__PRAYER_LOCATION} dan sekitarnya"
                    e.description = f"Waktunya terawih, bukanya terwaih malah buka nHen..., salat dulu ynag bener!!.\n\n " \
                        f"**Quote hari ini**\n{choice(cls.__QUOTES)}\n\n**Jadwal shalat hari ini:**"
                else:
                    e.title = f"Waktu {pray} untuk area {ModularBotConst.__PRAYER_LOCATION} dan sekitarnya"
                    e.description = f"Waktunya salat {pray}, salat yang khusyuk, biar bisa ketemu waifu di isekaid.\n\n " \
                        f"**Quote hari ini**\n{choice(cls.__QUOTES)}\n\n**Jadwal shalat hari ini:**"
        if e is not None:
            for key, value in praytimes.items():
                if value != "ramadhan":
                    e.add_field(name=f"{key}:", value=value)
            e.set_author(name="Muslim Pro",
                icon_url="https://i.imgur.com/T7Zqnzw.png")
        return e
