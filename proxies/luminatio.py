from socket import gethostbyname
from random import randint

# proxy: https://luminati.io/


def get_luminati_session(username, password):
    """Returns a new sticky Luminati Proxy Session."""

    port = 22225
    ip = gethostbyname("zproxy.lum-superproxy.io")

    session_id = randint(1000, 9999)

    return (
        f"http://{username}-session-glob_{session_id}:{password}@{ip}:{port}",
        session_id,
    )
