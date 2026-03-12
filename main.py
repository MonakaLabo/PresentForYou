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

        for line in lines[4:]:
            a, b = line.split("\t", 1)
            self.data.append((a, b))


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

    print("出題順")
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

        print("範囲外です")


def memorize(data, table, count):

    correct = 0
    total_time = 0
    last_time = 0

    data = data[:count]

    for i, q in enumerate(data):

        print("\n----------------")

        print(f"問題 {i+1}/{count}")
        print(f"前回 {last_time:.2f}s")
        print(f"累計 {total_time:.2f}s")
        if i:
            print(f"正答率 {(correct/i)*100:.1f}%")

        if table.numbering:
            print(f"単語番号 {table.start_number+i}")

        word = q[0]
        ans = q[1]

        choices = [ans]

        while len(choices) < 4:

            c = random.choice(data)[1]

            if c not in choices:
                choices.append(c)

        random.shuffle(choices)

        print(word)

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

        save_history({
            "time": datetime.now().isoformat(),
            "word": word,
            "correct": ok,
            "answer_time": elapsed
        })

    print("\n結果")

    print(correct, "/", count)


def weak_words():

    hist = load_history()

    stats = {}

    for h in hist:

        w = h["word"]

        if w not in stats:
            stats[w] = [0, 0]

        stats[w][1] += 1

        if h["correct"]:
            stats[w][0] += 1

    weak = []

    for w, (c, t) in stats.items():

        if c / t < 0.5:
            weak.append(w)

    print("苦手単語")

    for w in weak:
        print(w)


def history_menu():

    hist = load_history()

    print("履歴数:", len(hist))

    print("1:苦手単語")

    if input("> ") == "1":
        weak_words()


def memorize_menu():

    tables = load_tables()

    table = tables[0]

    data = table.data.copy()

    order = choose_order()

    data = reorder(data, order)

    count = choose_count(len(data))

    memorize(data, table, count)


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