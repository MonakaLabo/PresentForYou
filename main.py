import os
import random
import time
import json
import re
from datetime import datetime

TABLE_DIR = "tables"
HISTORY_FILE = "history/history.json"
STATS_FILE = os.path.join("stats", "weakword.json")


class Table:

    def __init__(self, path):

        self.path = path
        self.name = os.path.basename(path)

        self.bookcode = ""
        self.tags = ""
        self.description = ""
        self.labels = []
        self.numbering = False
        self.start_number = 0
        self.data = []

        self.load()

    def load(self):

        with open(self.path, encoding="utf-8") as f:
            lines = [l.rstrip("\n") for l in f if l.strip()]

        self.tags = [s.strip() for s in lines[0].split(",")]

        if self.tags[0].startswith("BOOKCODE:"):
            self.bookcode = self.tags[0].split(":", 1)[1]
        else:
            raise ValueError(f"{self.path} の1行目(メタデータ：タグ)にBOOKCODEがありません。")
        
        self.tags = self.tags[1:]
        self.description = lines[1]
        self.labels = lines[2].split(",")

        num = lines[3].split(",")

        self.numbering = num[0] == "True"

        if self.numbering:
            self.start_number = int(num[1])

        for i, line in enumerate(lines[4:]):
            a, b = line.split("\t", 1)

            if self.numbering:
                wid = self.start_number + i
            else:
                wid = i + 1

            self.data.append({
                "id": wid,
                "q": a,
                "a": b
            })


def save_history(entry):

    os.makedirs("history", exist_ok=True)

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, encoding="utf-8") as f:
            hist = json.load(f)
    else:
        hist = []

    hist.append(entry)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)


def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_tables():

    # tablesファイルをリスト形式で取得
    files = os.listdir(TABLE_DIR)

    print("tables:")

    # iにindexを、fにファイル名を代入して繰り返す
    for i, f in enumerate(files):
        print(f"{i+1}: {f}")

    s = input("選択: ")

    # カンマ区切りで返された数値の列をリストに変換
    idx = [int(x)-1 for x in s.split(",")]

    tables = []
    bookcodes = set()

    for i in idx:

        table = Table(os.path.join(TABLE_DIR, files[i]))

        tables.append(table)

        bookcodes.add(table.bookcode)

    if len(bookcodes) == 1:
        bookcode = next(iter(bookcodes))
    else:
        bookcode = None

    return tables, bookcode


def choose_order():

    print("\n出題順")
    print("0:ランダム")
    print("1:正順")
    print("2:逆順")

    s = input("> ")

    if s == "1":
        return "forward"
    if s == "2":
        return "reverse"

    return "random"

def choose_reverse():
    
    print("\n方向")
    print("0:表向き")
    print("1:裏向き")

    s = input("> ")

    if s == "1":
        return "reverse"
    else:
        return "forward"


def choose_count(total):

    s = input(f"\n出題数 (max {total}): ")

    if s == "":
        return total

    n = int(s)

    return min(n, total)


def reorder(data, order):

    if order == "random":
        random.shuffle(data)

    elif order == "reverse":
        data.reverse()

    return data


def reverser(data, reverse):

    if reverse != "reverse":
        return data

    return [
        {"id":d["id"], "q":d["a"], "a":d["q"]}
        for d in data
    ]
        

def get_answer(n):

    while True:

        s = input("> ")

        if not s.isdigit():
            print("数字を入力してください")
            continue

        v = int(s)

        if 1 <= v <= n:
            return v

        print("選択肢の範囲外です")


def memorize(data, table, bookcode, count, mode):

    correct = 0
    total_time = 0
    last_time = 0

    correct_ids = []
    wrong_ids = []

    session_start = time.time()

    data = data[:count]

    for i, q in enumerate(data):

        print("\n----------------")

        print(f"問題 {i+1}/{count}")
        print(f"前回 {last_time:.2f}s")
        print(f"累計 {total_time:.2f}s")
        if i:
            print(f"正答率 {(correct/i)*100:.1f}%")

        if table.numbering:
            print(f"単語番号 {q['id']}")
        print("----------------")

        word = q["q"]
        ans = q["a"]

        choices = [ans]

        while len(choices) < 4:

            c = random.choice(data)["a"]

            if c not in choices:
                choices.append(c)

        random.shuffle(choices)

        print(f"\n{word}")

        for j, c in enumerate(choices):
            print(f"{j+1}: {c}")

        start = time.time()

        a = get_answer(4)

        elapsed = time.time() - start

        last_time = elapsed
        total_time += elapsed

        ok = choices[a-1] == ans

        print()

        if ok:
            print("OK")
            correct += 1
            correct_ids.append(q["id"])
        else:
            print("NG:", ans)
            wrong_ids.append(q["id"])

    duration = int(time.time() - session_start)

    history_entry = {
        "table": table.name,
        "start_time": datetime.now().isoformat(),
        "duration": duration,
        "mode": mode,
        "count": count,
        "correct": correct,
        "wrong_ids": wrong_ids
    }

    save_history(history_entry)

    print("\n---------------")
    print("結果\n")
    print(f"correct :{correct} / {count} ({(correct/count)*100:.1f} %)")
    print(f"Duration: {duration} s")
    print(f"Average : {duration/count:.1f} s")

    stats_update(bookcode, correct_ids, wrong_ids)


def stats_update(bookcode, correct, wrong):

    os.makedirs("stats", exist_ok=True)

    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    if bookcode not in data:
        data[bookcode] = {}

    words = data[bookcode]

    for wid in correct:

        wid = str(wid)

        if wid in words:
            words[wid][0] += 1
        else:
            words[wid] = [1, 0]
        
    for wid in wrong:

        wid = str(wid)

        if wid in words:
            words[wid][1] += 1
        else:
            words[wid] = [0, 1]
    
    data[bookcode] = dict(
        sorted(data[bookcode].items(), key=lambda x: int(x[0]))
    )

    data = dict(sorted(data.items()))

    text = json.dumps(data, ensure_ascii=False, indent=2)

    text = re.sub(r'\[\s*(\d+),\s*(\d+)\s*\]', r'[\1, \2]', text)

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        f.write(text)


def history_menu():

    hist = load_history()

    print("履歴数:", len(hist))

    for h in hist[-5:]:
        print(h["start_time"], h["table"], f'{h["correct"]}/{h["count"]}')


def memorize_menu():

    while True:
        tables, bookcode = load_tables()

        if bookcode is None:
            print("2種類以上の書籍が含まれています。")
            print("今回の結果は苦手単語として登録されません。")
            print("続行しますか？")
            if input("0:選択し直す\n1:続行する\n> ") == 1:
                break
        
        else:
            break

    data = []

    for t in tables:
        data.extend(t.data)

    order = choose_order()

    reverse = choose_reverse()

    data = reorder(data, order)

    data = reverser(data, reverse)

    count = choose_count(len(data))

    memorize(data, tables[0], bookcode, count, order)


def main():

    print("0:暗記")
    print("1:履歴")

    s = input("> ")

    if s == "1":
        history_menu()
    else:
        memorize_menu()


if __name__ == "__main__":
    main()
