import json
import requests
import sys

if __name__ == "__main__":
    from utils import test_proxy, validate_ip
else:
    from .utils import test_proxy, validate_ip

# proxy list: https://api.getproxylist.com/proxy


def start_getproxylist_thread(callback):
    while True:
        try:
            proxy = _get_fresh_proxy()
            if proxy == None:
                raise "no proxy found"
        except:
            print("get proxy list error")
            sys.exit(0)

        if test_proxy(proxy):
            callback(proxy)


def _get_fresh_proxy():
    url = "https://api.getproxylist.com/proxy"
    response = requests.get(url)
    body = json.loads(response.text)

    if "error" in body:
        print(f"get proxy list error: {body['error']}")
        return None

    return f"{body['protocol']}://{body['ip']}:{body['port']}"
