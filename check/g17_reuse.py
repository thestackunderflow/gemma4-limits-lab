import json, os, sys, urllib.request
URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/chat"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "gemma4:e4b-it-q4_K_M"
TURNS = ["My plate is 60 x 40 x 5 mm.", "Make the holes 6 mm.", "What size is my plate?"]
msgs = []
for n, text in enumerate(TURNS, 1):
    msgs.append({"role": "user", "content": text})
    body = {"model": MODEL, "messages": msgs, "stream": False,
            "keep_alive": "5m", "options": {"num_ctx": 8192}}
    req = urllib.request.Request(URL, json.dumps(body).encode())
    r = json.load(urllib.request.urlopen(req))
    msgs.append(r["message"])
    sent, reused = r["prompt_eval_count"], r.get("prompt_eval_cached_count", 0)
    print(f"turn {n}: sent {sent}, reused {reused}")
print(msgs[-1]["content"][:200])
