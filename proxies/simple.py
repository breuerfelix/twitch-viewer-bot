import time
import sys
from .utils import test_proxy

FILENAME = "working.txt"


def start_simple_thread(callback):
    get_new = _init_proxies(FILENAME)
    while True:
        try:
            proxy = get_new()
            if proxy == None:
                raise "no proxy found"
        except Exception as e:
            print("simple proxy error", e)
            sys.exit(0)

        if test_proxy(proxy):
            callback(proxy)


def _init_proxies(filename):
    """Reads in proxies from a simple file."""

    proxies = []

    with open(filename, "r") as file:
        proxies = file.read().split("\n")

    print(f"loaded {len(proxies)} simple proxies")
    counter = 0

    def get_new():
        nonlocal counter

        if counter >= len(proxies):
            return None

        return proxies[counter]

    return get_new
