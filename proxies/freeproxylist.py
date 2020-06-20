import sys
import requests
from lxml.html import fromstring
from threading import Thread

if __name__ == "__main__":
    from utils import test_proxy, validate_ip
else:
    from .utils import test_proxy, validate_ip


# these sites got all the same structure
# proxy lists:
URLS = [
    "https://www.us-proxy.org/",
    "https://free-proxy-list.net/",
    "https://free-proxy-list.net/uk-proxy.html",
    "https://www.sslproxies.org/",
    "https://free-proxy-list.net/anonymous-proxy.html",
]


def start_freeproxylist_thread(callback):
    for url in URLS[:-1]:
        Thread(target=_start_proxy_thread, args=[callback, url]).start()

    # don't throw THIS thread away and start the last one
    _start_proxy_thread(callback, URLS[-1])


def _start_proxy_thread(callback, url):
    print(f"start getfreeproxylist: {url}")

    while True:
        try:
            proxies = _parse_proxies(url)
        except Exception as e:
            print("free proxy list errror", e)
            sys.exit(0)

        for proxy in proxies:
            if test_proxy(proxy):
                callback(proxy)


def _parse_proxies(url):
    response = requests.get(url)
    body = fromstring(response.text)

    proxy_list = set()

    for row in body.xpath("//tbody/tr"):
        ip = row.xpath(".//td[1]/text()")
        port = row.xpath(".//td[2]/text()")
        https = row.xpath(".//td[7]/text()")

        if len(ip) == 0 or len(port) == 0 or len(https) == 0:
            continue

        if not validate_ip(ip[0]):
            continue

        scheme = "http"
        if https[0] == "yes":
            scheme += "s"

        proxy = f"{scheme}://{ip[0]}:{port[0]}"
        proxy_list.add(proxy)

    return proxy_list


if __name__ == "__main__":
    # test proxy scraper here
    print(_parse_proxies(URLS[-1]))
