import json, sys, urllib.request
topic, title, msg = sys.argv[1], sys.argv[2], sys.argv[3]
body = json.dumps({"topic": topic, "title": title, "message": msg, "priority": 4,
    "click": "https://parkminhyeokjw.github.io/morning-news/"}).encode("utf-8")
req = urllib.request.Request("https://ntfy.sh/", data=body, headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(req, timeout=20).status)
