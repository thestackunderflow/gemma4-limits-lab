"""Filmed result lines for one g17 chat (sc5-l5 has no jq): python3 scripts/film17/show.py CHAT_ID"""
import json, sys
s = json.load(open("out/g17/chats/%s/summary.json" % sys.argv[1]))
c = s.get("checker") or {}
print("turn 1 gone at turn:", s["first_turn1_gone_turn"])
print("turn-20 facts recalled: %d of 8" % s["turn20_recall"]["score"])
print("plate.stl exported:", s["turn20_stl"])
print("checker size:", c.get("size"), " pass:", c.get("pass"))
