from random import choice
from discord import Embed
from aiohttp import ClientSession
from datetime import datetime
from typing import Union

from .util import ModularUtil
from const import ModularBotConst


class Prayers:
    __PRAYER_LOCATION = "DKI Jakarta"

    __PRAYER_API = "https://muslim-pro-api-lleans.koyeb.app"
    __BUKA_IMAGE = ["https://i.imgur.com/1uVOu9s.gif", "https://i.imgur.com/lrrIzRY.gif",
                    "https://i.imgur.com/eWe8VvA.gif", "https://i.imgur.com/gFVKP74.gif",
                    "https://i.imgur.com/tW3Hjcb.gif", "https://i.imgur.com/ey1KKAd.gif",
                    "https://i.imgur.com/Tgx5w3E.gif"]
    __SHALAT_IMAGE = ["https://i.imgur.com/I24KR5n.gif", "https://i.imgur.com/L2Yk6a2.gif",
                    "https://i.imgur.com/cRJQcfJ.gif", "https://i.imgur.com/IV5Nadb.gif",
                    "https://i.imgur.com/zCSohsn.gif", "https://i.imgur.com/OGesUM4.gif",
                    "https://i.imgur.com/VTPufTo.gif"]

    __QUOTES = ["`Salah satu dosa terburuk adalah seseorang yang menganggap remeh dosanya. \n\n- Abu Bakar Asshidiq`",
                "`Tidak boleh seorang muslim menghina muslim yang lain. Yang kecil pada kaum muslimin, adalah besar pada sisi Allah. \n\n- Abu Bakar Asshidiq`",
                "`Buatlah tujuan untuk hidup, kemudian gunakan segenap kekuatan untuk mencapainya, kamu pasti berhasil. \n\n- Ustman Bin Affan`",
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
                res.update(resp['praytimes'][f"{time.strftime('%a')} {time.strftime('%d').replace('0', '') if time.strftime('%d').startswith('0') else time.strftime('%d')} {time.strftime('%b')}"])
                res.update({
                    'Maghrib': res.pop('Maghrib'),
                    'Subuh': res.pop('Fajr'),
                    'Dhuha': res.pop('Sunrise'),
                    'Dzuhur': res.pop('Dhuhr'),
                    'Ashar': res.pop('Asr'),
                    'Isya': res.pop("Isha'a"),
                    'ramadhan': resp['ramadhan'][time.strftime('%Y')],
                })

                return res
            return 
            

    @classmethod
    def prayers_generator(cls, praytimes: dict, time: datetime) -> Union[Embed, None]:
        e: Embed = Embed(color=ModularUtil.convert_color(choice(ModularBotConst.COLOR['random_array'])), title=None)
        e.set_author(name="Muslim Pro", icon_url="https://i.imgur.com/T7Zqnzw.png")
        e.description = f"**Quote hari ini**\n{choice(cls.__QUOTES)}\n\n**Jadwal salat hari ini:**"
        
        for pray, prayt in praytimes.items():

            if time.strftime('%A') == "Friday" and pray == "Dzuhur":
                pray = "Jumatan"

            if prayt == time.strftime('%H:%M'):
                e.set_image(url=choice(cls.__SHALAT_IMAGE))
                
                if pray == "Maghrib":
                    e.title = f"Waktu Berbuka untuk area {cls.__PRAYER_LOCATION} dan sekitarnya."
                    e.description = "Selamat Berbuka Puasa. Bersyukurlah kalian bisa berbuka dengan makanan enak, diluar sana masih banyak yang belum bisa kayak kamu. " \
                        "Jadi, tetaplah bersyukur walaupun kamu buka dengan tahu tempe :).\nJangan lupa Salat Maghrib habis buka.\n\n" + e.description
                    e.set_image(url=choice(cls.__BUKA_IMAGE))
                elif pray == "Isya":
                    e.title = f"Waktu Salat Tarawih untuk area {cls.__PRAYER_LOCATION} dan sekitarnya."
                    e.description = f"Waktunya Tarawih. Bukanya Tarawih, malah buka nHen..., salat dulu yang bener!!.\n\n" + e.description
                else:
                    e.title = f"Waktu Salat {pray} untuk area {cls.__PRAYER_LOCATION} dan sekitarnya."
                    e.description = f"Waktunya Salat {pray}. Salat yang khusyuk, biar bisa ketemu waifu di isekaid.\n\n" + e.description
            if pray != "ramadhan":
                    e.add_field(name=f"{pray+' (Buka)' if pray == 'Maghrib' else pray}:", value=prayt)

        if e.title == None:
            e = None    
        
        return e
