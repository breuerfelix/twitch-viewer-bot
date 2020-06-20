from threading import Thread
from .getproxylist import start_getproxylist_thread
from .freeproxylist import start_freeproxylist_thread
from .luminatio import get_luminati_session
from .hideme import start_hideme_thread
from .premproxy import start_premproxy_thread
from .simple import start_simple_thread
from .utils import validate_ip, test_proxy


# TODO implemented these
# https://www.proxyrotator.com/free-proxy-list/
# netzwelt.de/proxy/index.html#proxy-server-einrichten


def start_proxy_threads(callback):
    proxies = [
        start_freeproxylist_thread,
        start_hideme_thread,
        start_premproxy_thread,
        start_simple_thread,
        start_getproxylist_thread,
    ]

    for func in proxies:
        Thread(target=func, args=[callback]).start()
