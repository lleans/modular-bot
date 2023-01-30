from os import getenv

from aiohttp import ClientSession


class PlayTogether():
    __APPS: dict = {
        'youtube': '880218394199220334',
        'poker': '755827207812677713',
        'betrayal': '773336526917861400',
        'fishing': '814288819477020702',
        'chess': '832012774040141894',
        # Credits to awesomehet2124
        'lettertile': '879863686565621790',
        'wordsnack': '879863976006127627',
        'doodlecrew': '878067389634314250',
        'spellcast': '852509694341283871'
    }

    @classmethod
    async def generate_invite(cls, session: ClientSession, channelId: int, option: str) -> str:
        if option is not None:
            data: dict = {
                'max_age': 86400,
                'max_uses': 5,
                'target_application_id': cls.__APPS[option.lower().replace(" ", "")],
                'target_type': 2,
                'temporary': False,
                'validate': None
            }
            headers: dict = {
                'Authorization': f'Bot {open("../TOKEN").readline() or getenv("TOKEN")}',
                'Content-Type': 'application/json'
            }
            async with session.post(f"https://discord.com/api/v8/channels/{channelId}/invites",
                                         data=data,
                                         headers=headers) as resp:
                if resp.status == 200:
                    result: dict = await resp.json()
                    return f"https://discord.gg/{result['code']}"
                else:
                    return 
