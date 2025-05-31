import asyncio
import itertools

from loguru import logger

from providers import http

_wordlist: list[str] | None = None


def wordlist() -> list[str]:
    global _wordlist
    if _wordlist:
        return _wordlist
    with open("assets/wordlist.txt", "r") as f:
        _wordlist = list(l.strip() for l in f)
    return _wordlist


async def dirsearch() -> None:
    wl = wordlist()
    res = await http.client.get("/")
    homepage_html = res.text

    max_depth = 1
    bases = [""]
    full_results = []
    while bases:
        base = bases.pop(0)
        depth = base.count("/")
        tasks = [http.client.get("/".join((base, word))) for word in wl]
        results = []
        for ts in itertools.batched(tasks, 100):
            responses = await asyncio.gather(*ts)
            for res in responses:
                if res.status_code == 200 and res.text != homepage_html:
                    results.append(res.url.path)
        logger.info(f"dirsearch found: {results}")
        full_results.extend(results)
        if depth < max_depth:
            bases.extend(results)
