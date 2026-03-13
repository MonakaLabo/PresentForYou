import os
import random
import time
import json
from datetime import datetime

TABLE_DIR = "tables"
HISTORY_FILE = "history/history.json"


class Table:

    def __init__(self, path):

        self.path = path
        self.name = os.path.basename(path)

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

        self.tags = lines[0]
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

    files = os.listdir(TABLE_DIR)

    print("tables:")

    for i, f in enumerate(files):
        print(f"{i}: {f}")

    s = input("選択: ")

    idx = [int(x) for x in s.split(",")]

    tables = []

    for i in idx:
        tables.append(Table(os.path.join(TABLE_DIR, files[i])))

    return tables


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


def choose_count(total):

    s = input(f"出題数 (max {total}): ")

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


def memorize(data, table, count, mode):

    correct = 0
    total_time = 0
    last_time = 0

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

        if ok:
            print("OK")
            correct += 1
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


def history_menu():

    hist = load_history()

    print("履歴数:", len(hist))

    for h in hist[-5:]:
        print(h["start_time"], h["table"], f'{h["correct"]}/{h["count"]}')


def memorize_menu():

    tables = load_tables()

    table = tables[0]

    data = table.data.copy()

    order = choose_order()

    data = reorder(data, order)

    count = choose_count(len(data))

    memorize(data, table, count, order)


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
