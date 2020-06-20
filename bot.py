import requests
import sys
import json
import math
import random
import uuid
import time
import click
import dateutil.parser
from datetime import datetime
from streamlink import Streamlink
from threading import Thread
from proxies import get_luminati_session, start_proxy_threads

TIMEOUT = 10


def init_session(proxy=None):
    """Creates a new requests session with sensible defaults."""

    session = requests.Session()
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"

    if proxy is not None:
        session.proxies = {
            "http": proxy,
            "https": proxy,
        }

    return session


def get_public_client_id(session, channel):
    """Scrapes the public Client ID that the Twitch Website is using."""

    res = session.get(f"https://twitch.tv/{channel}", allow_redirects=True)
    data = res.text
    # TODO refactor this and use a regex
    pos = data.find("Client-ID")
    start_pos = pos + 12
    end_pos = data.find('"', start_pos)
    return data[start_pos:end_pos]


def start_watching(channel, client_id, proxy=None, thread_id=None, on_exit=None):
    """Simulates watching the Stream."""

    if thread_id is None:
        thread_id = proxy or "local"

    session = init_session(proxy)

    run = False
    try:
        # set cookies for watching stream
        session.head(
            f"https://twitch.tv/{channel}", allow_redirects=True, timeout=TIMEOUT
        )
        token = get_token(session, channel, client_id)

        if "error" in token:
            print("error in token:", token["message"])
            # exit thread
            sys.exit(1)

        # got the stream url from twitch
        url = get_stream_url(session, channel, token)
        run = True
    except OSError as e:
        if "403 Forbidden" not in str(e):
            from traceback import print_exc

            # some generic error occured
            print_exc()
            sys.exit(1)

        # proxy is rejecting twitch requests
        # using streamlink library to obtain URL
        print(f"error getting stream url in thread {thread_id}. try streamlink")

        stream_session = Streamlink()
        custom_headers = {"Client-ID": client_id}
        stream_session.set_option("http-headers", custom_headers)
        streams = stream_session.streams(f"http://twitch.tv/{channel}")
        url = streams["worst"].url

        run = True

    all_batch_urls = dict()
    sorted_time = set()
    last_playlist = time.time() - 100
    last_segmet = None
    while run:
        try:
            # it should update the viewer count only by using prefetch urls
            # the browser is also only requesting these
            pref_url = request_prefetch_url(session, channel, url)
            if pref_url is None:
                raise Exception("could not get prefetch url")

            request_segment(session, channel, pref_url)

            # TODO reimplement this auto watcher once the bot is working

            # if (last_playlist < time.time() - 15):
            # # update batch urls
            # video_urls = request_playlist(session, channel, url)
            # all_batch_urls.update(video_urls)
            # sorted_time = sorted(set(all_batch_urls.keys()))

            # if last_segmet is not None:
            # # remove all batches already seen
            # items_to_remove = set()
            # for batch_time in sorted_time:
            # if batch_time > last_segmet:
            # continue

            # # mark item to remove
            # items_to_remove.add(batch_time)

            # # actually remove item
            # for item in items_to_remove:
            # sorted_time.remove(item)
            # del all_batch_urls[item]

            # last_playlist = time.time()

            # if len(sorted_time) > 0:
            # # remove the current batch from our lists
            # earliest_batch_time = sorted_time[0]
            # batch_url = all_batch_urls[earliest_batch_time]
            # sorted_time.remove(earliest_batch_time)
            # del all_batch_urls[earliest_batch_time]

            # # set last watch time
            # last_segmet = earliest_batch_time

            # # watch the batch
            # request_segment(session, channel, batch_url)

            time.sleep(2)
        except requests.exceptions.Timeout as e:
            print(f"timeout in thread: {thread_id}")
            break
        except Exception as e:
            print(f"error in thread: {thread_id}")
            from traceback import print_exc

            print_exc()
            break

    if on_exit is not None:
        on_exit(thread_id)

    sys.exit(0)


def request_segment(session, channel, url):
    """Sends a HEAD request which simulates watching the Stream."""

    headers = dict()
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"
    headers["Accept"] = "*/*"
    headers["Accept-Language"] = "en-US,en;q=0.5"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Origin"] = "https://www.twitch.tv"
    headers["Referer"] = f"https://www.twitch.tv/{channel}"
    headers["Connection"] = "keep-alive"
    headers["Pragma"] = "no-cache"
    headers["Cache-Control"] = "no-cache"

    session.head(url, headers=headers, timeout=TIMEOUT)


def request_prefetch_url(session, channel, url):
    """Request the Batch URLS for the current 12 seconds."""

    headers = dict()
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"
    headers[
        "Accept"
    ] = "application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain"
    headers["Accept-Language"] = "en-US,en;q=0.5"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Origin"] = "https://www.twitch.tv"
    headers["Referer"] = f"https://www.twitch.tv/{channel}"
    headers["Connection"] = "keep-alive"
    headers["Pragma"] = "no-cache"
    headers["Cache-Control"] = "no-cache"

    res = session.get(url, headers=headers, timeout=TIMEOUT)
    data = res.text.split("\n")

    reversed_row = reversed(data)

    for row in reversed_row:
        if "TWITCH-PREFETCH" in row:
            return row[row.find(":") + 1 :]

    # fallback when no prefetch url is present
    for row in reversed_row:
        if row.startswith("http"):
            return row

    return None


def request_playlist(session, channel, url):
    """Request the Batch URLS for the current 12 seconds."""

    headers = dict()
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"
    headers[
        "Accept"
    ] = "application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain"
    headers["Accept-Language"] = "en-US,en;q=0.5"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Origin"] = "https://www.twitch.tv"
    headers["Referer"] = f"https://www.twitch.tv/{channel}"
    headers["Connection"] = "keep-alive"
    headers["Pragma"] = "no-cache"
    headers["Cache-Control"] = "no-cache"

    res = session.get(url, headers=headers, timeout=TIMEOUT)
    data = res.text.split("\n")

    video_urls = dict()
    for index, line in enumerate(data):
        if "#EXT-X-PROGRAM-DATE-TIME" not in line:
            continue

        datestring = line[line.find(":") + 1 :]
        timestamp = dateutil.parser.parse(datestring)
        link = data[index + 2]
        video_urls[timestamp] = link

    return video_urls


def get_token(session, channel, client_id):
    """Request Twitch User Token to query Stream URL."""
    new_headers = session.headers.copy()
    new_headers["Accept"] = "application/vnd.twitchtv.v5+json; charset=UTF-8"
    new_headers["Content-Type"] = "application/json; charset=UTF-8"
    new_headers["Client-ID"] = client_id

    # also set the header permanent on session
    session.headers["Client-ID"] = client_id

    res = session.get(
        f"https://api.twitch.tv/api/channels/{channel}/access_token?oauth_token=&need_https=true&platform=web&player_type=site&player_backend=mediaplayer",
        headers=new_headers,
    )

    return json.loads(res.text)


def get_stream_url(session, channel, token):
    """Requests the Stream URL. Not needed when using Streamlink."""
    base_url = f"https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8?"

    # this is the original javascript code to generate this ID
    # p: Math.floor(9999999 * Math.random())
    p = math.floor(9999999 * random.uniform(0, 1))
    session_id = uuid.uuid4().hex

    params = {
        "allow_source": "true",
        "fast_bread": "true",
        "p": p,
        "play_session_id": session_id,
        "player_backend": "mediaplayer",
        "playlist_include_framerate": "true",
        "reassignments_supported": "true",
        "supported_codecs": "avc1",
        # sig from token request
        "sig": token["sig"],
        # token from request
        "token": token["token"],
        "cdm": "wv",
        "player_version": "0.9.5",
    }

    import urllib

    encoded = urllib.parse.urlencode(params)

    new_headers = session.headers.copy()
    new_headers[
        "Accept"
    ] = "application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain"

    res = session.get(base_url + encoded, timeout=TIMEOUT, headers=new_headers)

    # TODO use a random quality
    # return the last url which is worst quality
    last = res.text.split("\n")[-1]
    return last


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("channel", required=True, type=str)
@click.option(
    "--viewers",
    "-v",
    default=20,
    show_default=True,
    type=int,
    help="Amount of viewers the tool will add.",
)
@click.option(
    "--interval",
    "-i",
    default=10,
    show_default=True,
    type=int,
    help="Time in seconds to sleep between spawning viewers.",
)
@click.option("--luminati", "-n", is_flag=True, help="Enables Luminati Proxies.")
@click.option(
    "--luminati-username",
    "-u",
    default=None,
    type=str,
    envvar="LUMINATI_USERNAME",
    help="Luminati Proxy Username.",
)
@click.option(
    "--luminati-password",
    "-p",
    default=None,
    type=str,
    envvar="LUMINATI_PASSWORD",
    help="Luminati Proxy Password.",
)
@click.option(
    "--free-proxy", "-f", is_flag=True, help="Enables scraping for free proxies."
)
@click.option("--local", "-l", is_flag=True, help="Watch the Stream with Host Machine.")
def cli(
    channel,
    viewers,
    interval,
    luminati,
    luminati_username,
    luminati_password,
    free_proxy,
    local,
):
    """Starts the tool for given CHANNEL."""

    # pretty print channel on start
    from pyfiglet import Figlet

    print(Figlet().renderText(channel))

    # the api expects all lowercase
    channel = channel.lower()

    # latest public client id the twitch website is using
    client_id = get_public_client_id(init_session(), channel)

    threads = set()

    def on_exit(thread_id):
        threads.remove(thread_id)

    if local:
        threads.add("local")
        Thread(
            target=start_watching, args=[channel, client_id, None, "local", on_exit]
        ).start()

    if free_proxy:
        # callback when scraped a working proxy
        def cb(proxy):
            if proxy in threads:
                print(f"Proxy {proxy} already running.")
                return

            threads.add(proxy)
            Thread(
                target=start_watching, args=[channel, client_id, proxy, None, on_exit,],
            ).start()

        # scrapes multiple free proxy sites in threads
        start_proxy_threads(cb)

    if luminati and luminati_username is not None and luminati_password is not None:
        while True:
            if len(threads) < viewers:
                # add new viewer
                proxy, session_id = get_luminati_session(
                    luminati_username, luminati_password
                )
                if proxy not in threads:
                    threads.add(session_id)
                    Thread(
                        target=start_watching,
                        args=[channel, client_id, proxy, session_id, on_exit],
                    ).start()

            print(f"current viewer count: {len(threads)}")

            # 0.3 = 30%
            random_percentage = 0.3
            time.sleep(
                random.randint(
                    interval * (1 - random_percentage),
                    interval * (1 + random_percentage),
                )
            )

    # print out number of viewers if only using free proxy
    while True:
        print(f"current viewer count: {len(threads)}")
        time.sleep(10)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    cli()
