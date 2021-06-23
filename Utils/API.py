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


async def getChapterText(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://' + url) as gibText:
            text = await gibText.text()
        soup = BeautifulSoup(text, features="lxml")
        await session.close()
        array_text = soup.findAll('div', class_="ui text container")[1].findAll('p')
        return dict(name=soup.find('h1', class_="ui header").getText(),
                    text="\n".join(str(x) for x in array_text))


async def getLast():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ranobehub.org/api/search') as get:
            answer = await get.json()
            return answer["resource"]


loop = asyncio.get_event_loop()


async def main():
    data = await getChapterText('ranobehub.org/ranobe/34/1/1199')
    print(data["text"])


if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass
