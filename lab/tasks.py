"""Task sets with answers computed by code (or written next to the question and unit-tested)."""
import datetime as dt
import random


# ---------- Part 14: can't ----------
def multiplications(seed=42, n=20):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        a, b = rng.randint(1000, 9999), rng.randint(1000, 9999)
        out.append({"id": f"mul{i:02d}", "a": a, "b": b, "answer": a * b,
                    "prompt": f"What is {a} × {b}? Answer with the number only."})
    return out


_WORDS = [("strawberry", "r"), ("banana", "a"), ("mississippi", "s"), ("committee", "t"), ("bookkeeper", "e"),
          ("occurrence", "c"), ("necessary", "s"), ("embarrassment", "s"), ("parallel", "l"), ("assessment", "s"),
          ("raspberry", "r"), ("possession", "s"), ("accommodation", "o"), ("tennessee", "e"), ("millennium", "l"),
          ("successful", "s"), ("referee", "e"), ("hippopotamus", "p"), ("abracadabra", "a"), ("peppermint", "p")]


def letter_counts():
    out = []
    for w, c in _WORDS:
        out.append({"id": f"let_{w}", "word": w, "letter": c, "answer": w.count(c),
                    "prompt": f'How many times does the letter "{c}" appear in the word "{w}"? '
                              f"Answer with the number only.",
                    "fix_prompt": f'Spell the word "{w}" one letter per line, numbering each line. Then count how '
                                  f'many of those letters are "{c}". End with the line: Answer: <number>'})
    return out


def date_questions(today="2026-11-10"):
    t = dt.date.fromisoformat(today)
    wd = lambda d: d.strftime("%A").lower()  # noqa: E731
    nf = t + dt.timedelta(days=(4 - t.weekday()) % 7 or 7)
    qs = [
        ("today_weekday", "What day of the week is it today? Answer with the weekday name only.", wd(t)),
        ("plus10_weekday", "What day of the week will it be 10 days from today? Answer with the weekday name only.",
         wd(t + dt.timedelta(days=10))),
        ("today_date", "What is today's date? Answer in the format YYYY-MM-DD only.", t.isoformat()),
        ("tomorrow_date", "What is tomorrow's date? Answer in the format YYYY-MM-DD only.",
         (t + dt.timedelta(days=1)).isoformat()),
        ("yesterday_weekday", "What day of the week was it yesterday? Answer with the weekday name only.",
         wd(t - dt.timedelta(days=1))),
        ("days_to_new_year", f"How many days are there from today until 1 January {t.year + 1}? Answer with the "
                             f"number only.", (dt.date(t.year + 1, 1, 1) - t).days),
        ("year", "What year is it now? Answer with the year only.", t.year),
        ("month", "What month is it now? Answer with the month name only.", t.strftime("%B").lower()),
        ("minus30_date", "What was the date 30 days ago? Answer in the format YYYY-MM-DD only.",
         (t - dt.timedelta(days=30)).isoformat()),
        ("next_friday", "What is the date of the next Friday after today? Answer in the format YYYY-MM-DD only.",
         nf.isoformat()),
    ]
    return [{"id": i, "prompt": p, "answer": a} for i, p, a in qs]


def date_system_prompt(today="2026-11-10"):
    t = dt.date.fromisoformat(today)
    return f"Today's date is {t.strftime('%A')}, {t.day} {t.strftime('%B')} {t.year} ({t.isoformat()})."


# ---------- Part 15: can ----------
_CODING = [
    ("is_palindrome", "is_palindrome(s) that returns True if the string s reads the same forwards and backwards, "
                      "ignoring case and any character that is not a letter or digit.",
     "def is_palindrome(s):\n    t = [c.lower() for c in s if c.isalnum()]\n    return t == t[::-1]\n",
     ["assert is_palindrome('A man, a plan, a canal: Panama')", "assert not is_palindrome('hello')",
      "assert is_palindrome('')", "assert is_palindrome('No 1on')"]),
    ("fizzbuzz", "fizzbuzz(n) that returns a list of strings for 1..n: 'Fizz' for multiples of 3, 'Buzz' for "
                 "multiples of 5, 'FizzBuzz' for multiples of both, otherwise the number as a string.",
     "def fizzbuzz(n):\n    return ['FizzBuzz' if i%15==0 else 'Fizz' if i%3==0 else 'Buzz' if i%5==0 else str(i) "
     "for i in range(1, n+1)]\n",
     ["assert fizzbuzz(5) == ['1','2','Fizz','4','Buzz']", "assert fizzbuzz(15)[-1] == 'FizzBuzz'",
      "assert fizzbuzz(0) == []"]),
    ("roman_to_int", "roman_to_int(s) that converts a Roman numeral string (I, V, X, L, C, D, M, with subtractive "
                     "forms like IV and CM) to an integer.",
     "def roman_to_int(s):\n    v = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n    t = 0\n"
     "    for i, c in enumerate(s):\n        if i+1 < len(s) and v[c] < v[s[i+1]]:\n            t -= v[c]\n"
     "        else:\n            t += v[c]\n    return t\n",
     ["assert roman_to_int('III') == 3", "assert roman_to_int('MCMXCIV') == 1994", "assert roman_to_int('XLII') == 42"]),
    ("flatten", "flatten(lst) that takes a list which may contain nested lists to any depth and returns a flat "
                "list of all non-list items in order.",
     "def flatten(lst):\n    out = []\n    for x in lst:\n        out.extend(flatten(x) if isinstance(x, list) "
     "else [x])\n    return out\n",
     ["assert flatten([1,[2,[3,[4]]],5]) == [1,2,3,4,5]", "assert flatten([]) == []",
      "assert flatten([[[]]]) == []", "assert flatten(['a',['b']]) == ['a','b']"]),
    ("word_freq", "word_freq(text) that returns a dict mapping each lowercase word to how many times it appears; "
                  "words are runs of letters a-z (case-insensitive), everything else separates words.",
     "import re\ndef word_freq(text):\n    d = {}\n    for w in re.findall(r'[a-z]+', text.lower()):\n"
     "        d[w] = d.get(w, 0) + 1\n    return d\n",
     ["assert word_freq('The cat, the HAT!') == {'the':2,'cat':1,'hat':1}", "assert word_freq('') == {}",
      "assert word_freq('a1b') == {'a':1,'b':1}"]),
    ("is_prime", "is_prime(n) that returns True if the integer n is a prime number, else False.",
     "def is_prime(n):\n    if n < 2:\n        return False\n    i = 2\n    while i*i <= n:\n"
     "        if n % i == 0:\n            return False\n        i += 1\n    return True\n",
     ["assert is_prime(2) and is_prime(97)", "assert not is_prime(1) and not is_prime(0) and not is_prime(-7)",
      "assert not is_prime(91)", "assert is_prime(7919)"]),
    ("merge_intervals", "merge_intervals(intervals) that takes a list of [start, end] pairs and returns the merged "
                        "list of overlapping intervals (touching intervals like [1,2],[2,3] merge), sorted by start.",
     "def merge_intervals(intervals):\n    out = []\n    for a, b in sorted(intervals):\n"
     "        if out and a <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], b)\n"
     "        else:\n            out.append([a, b])\n    return out\n",
     ["assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]",
      "assert merge_intervals([[1,2],[2,3]]) == [[1,3]]", "assert merge_intervals([]) == []",
      "assert merge_intervals([[5,6],[1,2]]) == [[1,2],[5,6]]"]),
    ("binary_search", "binary_search(arr, x) that returns the index of x in the sorted list arr, or -1 if x is "
                      "not present.",
     "def binary_search(arr, x):\n    lo, hi = 0, len(arr)-1\n    while lo <= hi:\n        m = (lo+hi)//2\n"
     "        if arr[m] == x:\n            return m\n        if arr[m] < x:\n            lo = m+1\n"
     "        else:\n            hi = m-1\n    return -1\n",
     ["assert binary_search([1,3,5,7,9], 7) == 3", "assert binary_search([1,3,5], 4) == -1",
      "assert binary_search([], 1) == -1", "assert binary_search([2], 2) == 0"]),
    ("rle_encode", "rle_encode(s) that run-length encodes a string as letter followed by count, e.g. 'aaabbc' -> "
                   "'a3b2c1'.",
     "def rle_encode(s):\n    out = []\n    i = 0\n    while i < len(s):\n        j = i\n"
     "        while j < len(s) and s[j] == s[i]:\n            j += 1\n        out.append(s[i] + str(j-i))\n"
     "        i = j\n    return ''.join(out)\n",
     ["assert rle_encode('aaabbc') == 'a3b2c1'", "assert rle_encode('') == ''", "assert rle_encode('abca') == "
      "'a1b1c1a1'"]),
    ("second_largest", "second_largest(nums) that returns the second largest DISTINCT value in the list nums, or "
                       "None if there is none.",
     "def second_largest(nums):\n    s = sorted(set(nums))\n    return s[-2] if len(s) > 1 else None\n",
     ["assert second_largest([3,1,4,4,5]) == 4", "assert second_largest([2,2]) is None",
      "assert second_largest([]) is None", "assert second_largest([-1,-5]) == -5"]),
]


def coding():
    return [{"id": f"code_{n}", "name": n, "reference": ref, "tests": tests,
             "prompt": f"Write a Python function {spec} Reply with only the code in one ```python block, no "
                       f"explanation, no example usage."}
            for n, spec, ref, tests in _CODING]


def multilingual():
    q = [
        ("es1", "es", "¿Cuánto es 17 más 25? Responde solo con el número.", 42),
        ("es2", "es", "Tengo 3 cajas con 12 manzanas cada una. ¿Cuántas manzanas tengo en total? Responde solo con "
                      "el número.", 36),
        ("es3", "es", "Un tren sale a las 14:00 y llega a las 17:30. ¿Cuántos minutos dura el viaje? Responde solo "
                      "con el número.", 210),
        ("es4", "es", "Si un libro cuesta 8 euros, ¿cuánto cuestan 7 libros? Responde solo con el número.", 56),
        ("hi1", "hi", "45 में से 18 घटाने पर कितना बचता है? केवल संख्या लिखें।", 27),
        ("hi2", "hi", "एक कक्षा में 6 पंक्तियाँ हैं और हर पंक्ति में 9 छात्र हैं। कुल कितने छात्र हैं? केवल संख्या लिखें।", 54),
        ("hi3", "hi", "राम के पास 120 रुपये हैं। वह 45 रुपये खर्च करता है। उसके पास कितने रुपये बचे? केवल संख्या लिखें।", 75),
        ("ja1", "ja", "23と18を足すといくつですか？数字だけで答えてください。", 41),
        ("ja2", "ja", "りんごが5個入った袋が8袋あります。りんごは全部で何個ですか？数字だけで答えてください。", 40),
        ("ja3", "ja", "100から37を引くといくつですか？数字だけで答えてください。", 63),
    ]
    return [{"id": i, "lang": l, "prompt": p, "answer": a} for i, l, p, a in q]


def puzzles():
    q = [
        ("bat_ball", "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How many cents "
                     "does the ball cost?", 5),
        ("widgets", "If 5 machines make 5 widgets in 5 minutes, how many minutes do 100 machines need to make 100 "
                    "widgets?", 5),
        ("lily", "A patch of lily pads doubles in size every day. It takes 48 days to cover the whole lake. On "
                 "which day was the lake half covered?", 47),
        ("sisters", "Sally has 3 brothers. Each of her brothers has 2 sisters. How many sisters does Sally have?", 1),
        ("sevens", "How many times does the digit 7 appear when you write all the whole numbers from 1 to 100?", 20),
        ("socks", "A drawer holds 6 socks: 2 red, 2 blue and 2 green. In the dark, how many socks must you take "
                  "out to be sure you have a matching pair?", 4),
        ("remainder", "What is the smallest positive integer that leaves a remainder of 1 when divided by 2, 3, 4, "
                      "5 and 6, and is divisible by 7?", 301),
        ("sheep", "A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?", 9),
        ("squares", "How many squares of any size are there on a standard 8 by 8 chessboard?", 204),
        ("weekday", "Today is Wednesday. Which day of the week is it 100 days from now? Answer with its number, "
                    "where Monday = 1 and Sunday = 7.", 5),
    ]
    return [{"id": i, "prompt": p + " End your reply with the line: Answer: <number>", "answer": a}
            for i, p, a in q]


def _schema(props):
    return {"type": "object", "properties": props, "required": list(props)}


S, I, N = {"type": "string"}, {"type": "integer"}, {"type": "number"}


def json_extractions():
    q = [
        ("order", "Order #4471: 3 units of USB-C cable at $7.50 each, shipped to Denver on 2026-03-14.",
         {"order_id": I, "quantity": I, "unit_price": N, "city": S, "date": S},
         {"order_id": 4471, "quantity": 3, "unit_price": 7.5, "city": "Denver", "date": "2026-03-14"}),
        ("person", "Dr. Amara Okafor, 41, joined the Lagos office as head of research in 2019.",
         {"name": S, "age": I, "city": S, "role": S, "year_joined": I},
         {"name": "Amara Okafor", "age": 41, "city": "Lagos", "role": "head of research", "year_joined": 2019}),
        ("flight", "Flight LH 431 leaves Frankfurt at 10:25 from gate B44 and lands in Chicago at 12:55.",
         {"flight": S, "from": S, "to": S, "departure": S, "gate": S},
         {"flight": "LH 431", "from": "Frankfurt", "to": "Chicago", "departure": "10:25", "gate": "B44"}),
        ("server", "The server web-07 had CPU at 93 percent, 61 percent memory used and 12 open alerts at 03:10.",
         {"host": S, "cpu_percent": I, "memory_percent": I, "alerts": I},
         {"host": "web-07", "cpu_percent": 93, "memory_percent": 61, "alerts": 12}),
        ("recipe", "Pancakes for 4 people need 250 g flour, 2 eggs and 500 ml milk, and take 20 minutes.",
         {"servings": I, "flour_g": I, "eggs": I, "milk_ml": I, "minutes": I},
         {"servings": 4, "flour_g": 250, "eggs": 2, "milk_ml": 500, "minutes": 20}),
        ("invoice", "Invoice INV-2209 from Northwind Ltd totals 1,284.60 EUR and is due on 30 November 2026.",
         {"invoice_id": S, "vendor": S, "total": N, "currency": S, "due_date_iso": S},
         {"invoice_id": "INV-2209", "vendor": "Northwind Ltd", "total": 1284.6, "currency": "EUR",
          "due_date_iso": "2026-11-30"}),
        ("weather", "Oslo tomorrow: high of 4 degrees, low of -3 degrees, 80 percent chance of snow.",
         {"city": S, "high_c": I, "low_c": I, "snow_chance_percent": I},
         {"city": "Oslo", "high_c": 4, "low_c": -3, "snow_chance_percent": 80}),
        ("book", "'The Time Machine' by H. G. Wells was first published in 1895 and has 12 chapters.",
         {"title": S, "author": S, "year": I, "chapters": I},
         {"title": "The Time Machine", "author": "H. G. Wells", "year": 1895, "chapters": 12}),
        ("ticket", "Bug JIRA-5521, priority P2, was opened by Chen Wei and assigned to Maria Lopez; 3 comments.",
         {"ticket": S, "priority": S, "reporter": S, "assignee": S, "comments": I},
         {"ticket": "JIRA-5521", "priority": "P2", "reporter": "Chen Wei", "assignee": "Maria Lopez",
          "comments": 3}),
        ("measure", "The bracket is 120 mm long, 35 mm wide, 8 mm thick and has 4 holes of 5.5 mm.",
         {"length_mm": I, "width_mm": I, "thickness_mm": I, "holes": I, "hole_diameter_mm": N},
         {"length_mm": 120, "width_mm": 35, "thickness_mm": 8, "holes": 4, "hole_diameter_mm": 5.5}),
    ]
    return [{"id": i, "text": t, "schema": _schema(p), "answer": a,
             "prompt": "Extract the fields from this text as JSON with the keys " + ", ".join(p) + ".\n\nText: " + t}
            for i, t, p, a in q]


# ---------- tools (function calling, Part 15; calculator fix, Part 14) ----------
def _fn(name, desc, props, required=None):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {
        "type": "object", "properties": props, "required": required or list(props)}}}


TOOLS = [
    _fn("get_weather", "Current weather for a city.",
        {"city": {"type": "string", "description": "City name"},
         "unit": {"type": "string", "enum": ["c", "f"], "description": "c = Celsius, f = Fahrenheit"}}),
    _fn("multiply", "Multiply two integers exactly.", {"a": {"type": "integer"}, "b": {"type": "integer"}}),
    _fn("convert_currency", "Convert an amount between currencies (ISO codes like USD, EUR, JPY).",
        {"amount": {"type": "number"}, "from_currency": {"type": "string"}, "to_currency": {"type": "string"}}),
    _fn("get_stock_price", "Latest price of a stock ticker symbol.", {"symbol": {"type": "string"}}),
    _fn("days_between", "Number of days between two ISO dates (YYYY-MM-DD).",
        {"start": {"type": "string"}, "end": {"type": "string"}}),
    _fn("lookup_capital", "Capital city of a country.", {"country": {"type": "string"}}),
]

_WEATHER = {"paris": 14, "tokyo": 16, "mumbai": 31}
_RATES = {("USD", "EUR"): 0.92, ("JPY", "USD"): 0.0067}


def run_tool(name, args):
    """Deterministic tool implementations (made-up weather/stock data: the score is about the call, not the data)."""
    if name == "get_weather":
        c = _WEATHER.get(str(args.get("city", "")).lower())
        if c is None:
            return {"error": "unknown city"}
        return {"temperature": c if args.get("unit") != "f" else round(c * 9 / 5 + 32), "unit": args.get("unit")}
    if name == "multiply":
        return {"result": int(args["a"]) * int(args["b"])}
    if name == "convert_currency":
        r = _RATES.get((str(args.get("from_currency", "")).upper(), str(args.get("to_currency", "")).upper()))
        return {"result": round(float(args["amount"]) * r, 2)} if r else {"error": "unknown pair"}
    if name == "get_stock_price":
        return {"symbol": args.get("symbol"), "price": 123.45}
    if name == "days_between":
        return {"days": (dt.date.fromisoformat(args["end"]) - dt.date.fromisoformat(args["start"])).days}
    if name == "lookup_capital":
        return {"capital": {"australia": "Canberra"}.get(str(args.get("country", "")).lower(), "unknown")}
    return {"error": "unknown tool"}


def tool_prompts():
    q = [
        ("weather_paris", "What's the weather in Paris right now, in Celsius?", "get_weather",
         {"city": "Paris", "unit": "c"}, "14"),
        ("mul1", "Multiply 4821 by 7293.", "multiply", {"a": 4821, "b": 7293}, "35159553"),
        ("usd_eur", "Convert 250 US dollars to euros.", "convert_currency",
         {"amount": 250, "from_currency": "USD", "to_currency": "EUR"}, "230"),
        ("weather_tokyo", "How warm is it in Tokyo right now in Fahrenheit?", "get_weather",
         {"city": "Tokyo", "unit": "f"}, "61"),
        ("days", "How many days are there between 2026-01-15 and 2026-03-01?", "days_between",
         {"start": "2026-01-15", "end": "2026-03-01"}, "45"),
        ("capital", "Use the lookup tool: what is the capital of Australia?", "lookup_capital",
         {"country": "Australia"}, "Canberra"),
        ("stock", "What is the latest price of the stock NVDA?", "get_stock_price", {"symbol": "NVDA"}, "123.45"),
        ("mul2", "What is 1234 times 5678?", "multiply", {"a": 1234, "b": 5678}, "7006652"),
        ("jpy_usd", "Convert 1000 Japanese yen to US dollars.", "convert_currency",
         {"amount": 1000, "from_currency": "JPY", "to_currency": "USD"}, "6.7"),
        ("weather_mumbai", "What's the weather like in Mumbai? Use Celsius.", "get_weather",
         {"city": "Mumbai", "unit": "c"}, "31"),
    ]
    return [{"id": i, "prompt": p, "tool": t, "args": a, "answer": ans} for i, p, t, a, ans in q]
