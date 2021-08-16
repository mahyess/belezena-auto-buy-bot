import requests as req
from bs4 import BeautifulSoup
import time
from random import randint


def random_user_agent():
    url = "http://www.useragentstring.com/pages/useragentstring.php?name=Chrome"
    r = req.get(url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
    else:
        soup = False

    if soup:
        div = soup.find("div", {"id": "liste"})
        lnk = div.findAll("a")
        return lnk[randint(0, len(lnk) - 1)].text

    else:
        print("No soup")
        raise SystemError("no user agent found.")
