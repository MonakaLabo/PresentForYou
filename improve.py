import json
import os
import random


STATS_FILE = os.path.join("stats", "weakword.json")
BC2T_FILE = os.path.join("stats", "BC2T.join")


def load_json(path):

    if not os.path.exists(path):
        return {}
    
    with open(path, encoding="utf-8") as f:
        return json.load(f)
    

def intinput(text:str) -> int:
    

    while True:

        val = input(text)

        try:
            val = int(val)
        
        except:
            print("整数を入力してください。")

        else:
            return val

    

def get_bookcodes():

    data = load_json(STATS_FILE)

    return list(data.keys())


def load_booknames():

    return load_json(BC2T_FILE)


def select_book():

    bookcodes = get_bookcodes()
    names = load_booknames()

    for i, bc in enumerate(bookcodes, 1):
        title = names.get(bc, bc)
        print(f"{i}: {title}")

    idx = intinput("強化対象書籍を選択してください。\n> ")

    return bookcodes[idx-1]


def get_word_range(bookcode):

    data = load_json(STATS_FILE)

    words = data[bookcode]

    ids = [int(k) for k in words.keys()]

    return min(ids), max(ids)


def choose_range(min_id, max_id):

    print(f"\n単語範囲は {min_id} ～ {max_id} です。")

    start = intinput("開始番号: ")
    end = intinput("終了番号: ")

    start = max(start, min_id)
    end = min(end, max_id)

    return start, end


def sample_words(bookcode, start, end, n=20):
    
    data = load_json(STATS_FILE)

    words = data[bookcode]

    weak = []

    for wid, (c, w) in words.items():

        wid_i = int(wid)

        if start <= wid_i <= end:

            total = c + w
            rate = w / total if total else 0

            weak.append((wid_i, rate))

    weak.sort(key=lambda x: x[1], reverse=True)

    weak_ids = [wid for wid, _ in weak]

    weak_pick = weak_ids[: n//2]

    pool = [wid for wid in weak_ids if wid not in weak_pick]

    rand_pick = random.sample(pool, min(len(pool), n-len(weak_pick)))

    result = weak_pick + rand_pick

    random.shuffle(result)

    return result


def improve_menu():

    bookcode = select_book()

    min_id, max_id = get_word_range(bookcode)

    start, end = choose_range(min_id, max_id)

    words = sample_words(bookcode, start, end)

    print("\n出題単語ID:")
    print(words)

    return bookcode, words