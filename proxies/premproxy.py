import csv
import time
import sys

if __name__ == "__main__":
    from utils import test_proxy, validate_ip
else:
    from .utils import test_proxy, validate_ip

FILENAME = "prem_proxy.csv"


def start_premproxy_thread(callback):
    get_new = _init_proxies(FILENAME)
    while True:
        try:
            proxy = get_new()
            if proxy == None:
                raise "no proxy found"
        except Exception as e:
            print("premproxy error", e)
            sys.exit(0)

        if test_proxy(proxy):
            callback(proxy)


def _init_proxies(filename):
    proxies = []

    with open(filename, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")

        for line, row in enumerate(csv_reader):
            if line == 0:
                continue

            if row["Host"] == "":
                continue

            proxies.append(row)

    print(f"loaded {len(proxies)} proxme proxies")
    counter = 0

    def get_new():
        nonlocal counter

        if counter >= len(proxies):
            return None

        row = proxies[counter]

        auth = "" if row["Username"] == "" else f"{row['Username']}:{row['Password']}@"

        proxy = f"http://{auth}{row['Host']}:{row['Port']}"
        counter += 1
        return proxy

    return get_new


if __name__ == "__main__":
    # extract working proxies for test here
    get_new = _init_proxies(FILENAME)
    while True:
        try:
            proxy = get_new()
            if proxy == None:
                print("no more new proxies")
                break
        except Exception as e:
            print("premproxy error", e)
            sys.exit(0)

        if test_proxy(proxy, 3):
            with open("working.txt", "a") as file:
                file.write(proxy + "\n")
