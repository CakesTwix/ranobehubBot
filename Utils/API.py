import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def searchID(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ranobehub.org/api/ranobe/' + str(id)) as get:
            answer = await get.json()
            await session.close()
            return answer["data"]


async def getVolumes(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ranobehub.org/api/ranobe/' + str(id) + '/contents') as get:
            answer = await get.json()
            await session.close()
            return answer["volumes"]


async def getLastFreeChapter(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ranobehub.org/api/ranobe/' + str(id) + '/contents') as get:
            answer = await get.json()
            async with session.get(answer["volumes"][-1]["chapters"][-1]["url"]) as gibText:
                text = await gibText.text()
            soup = BeautifulSoup(text, features="lxml")
            await session.close()
            return dict(name=answer["volumes"][-1]["chapters"][-1]["name"],
                        text=' '.join(map(str, soup.find('div', class_="__ranobe_read_container").findAll('p'))))


async def getLast():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ranobehub.org/api/search') as get:
            answer = await get.json()
            return answer["resource"]


loop = asyncio.get_event_loop()


async def main():
    data = await searchID(153)
    print(data["names"]["rus"])


if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
