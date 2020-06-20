import re
import requests
import time
from threading import Thread


def validate_ip(ip):
    # https://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
    return re.match(
        r"^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$",
        ip,
    )


def test_proxy(proxy, timeout=10):
    url = "https://api.ipify.org"

    opts = {
        "http": proxy,
        "https": proxy,
    }

    try:
        before = time.time()

        response = requests.get(url, proxies=opts, timeout=timeout)
        ip = response.text

        after = time.time()

        # TODO maybe filter proxies for speed
        proxy_speed = after - before

        # check if response contains proxy ip
        return ip in proxy
    except Exception as e:
        return False
