# twitch viewer bot

__disclaimer:__ this project is an experiment and does not work!

```bash
pip3 install -r requirements.txt
python3 bot.py --help
```

if you want to know how this works (or __not__ works), read the code. there are many comments.

### why is it not working?

the problem are the proxies. i have not figured out how to get alot of different stable low bandwidth proxies for small money.  
most of the time you have to pay per proxy and not per gigabyte used. proxies for this bot just need low bandwidth because the bot is only doing head requests.

the free proxies i am trying to scrape are all garbage. they are not even able to handle 1-3 consecutive head requests.  
i noticed this behaviour from __all__ free proxies sites out there. i really question their existence.  
if they are not able to handle head requests, what could they be used for?

the best option out there is probably [luminati.io](https://luminati.io/). they offer a pay-as-you-go plan with unlimited proxies and pay by bandwidth.  
their datacenter ips cost 0.6 euro per gigabyte and residential ips 25 euro per gigabyte which is kinda expensive.  
i tried using their datacenter ips but either they are blocked by twitch or luminati doesn't allow requests to twitch.  
they worked for maybe one hour before i experienced these blocks.

also when using residential ips you have to sign a letter that you are not using those for fraud or faking stuff and luminati will publish your information to help companies identify those actions.  
sadly a twitch viewer bot is a 'fake' action in my opinion so i won't risk it.

### conclusion

i put it some decent amount of hours to get this working cause i am a really curious person and love to reverse engineer stuff.  
i know that there are bots out there for twitch so i thought it has to be possible, but not for me.  
twitch is doing a great job in preventing commercial proxies on their site and free proxies are __garbage__ anyways.

feel free to play around with this code and if you manage to get something going, let me know or make a pull request!

---

_i love lowercase_
