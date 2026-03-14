import os

TABLE_DIR = "tables"


def load_table(path):

    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f]

    header = lines[:4]

    num = header[3].split(",")

    numbering = num[0] == "True"

    start = int(num[1]) if numbering else 0

    data = []

    for line in lines[4:]:

        if line.strip():

            a, b = line.split("\t", 1)

            data.append([a, b])

    return header, data, numbering, start


def save_table(path, header, data):

    with open(path, "w", encoding="utf-8") as f:

        for h in header:
            f.write(h + "\n")

        for a, b in data:
            f.write(f"{a}\t{b}\n")


def edit_loop(path, header, data, numbering, start):

    while True:

        i = len(data)

        if numbering:
            word_no = start + i
            print(f"\n[{i+1} | No.{word_no}]")
        else:
            print(f"\n[{i+1}]")

        word = input("単語 (/undo /exit): ")

        if word == "/undo":

            if data:
                data.pop()
                print("戻りました")

            continue

        if word == "/exit":

            print("\n確認")
            print("ファイル:", os.path.basename(path))
            print("問題数:", len(data))

            if len(data) <= 3:
                
                print("\n=====! 不正なtableファイル !=====")
                print("問題数が 4 未満のtableファイルは許可されていません。")
                print(f"現在の問題数は {len(data)} です。")
                print(f"少なくとも {4-len(data)} の問題を追加する必要があります。")
            
            else:

                if input("終了しますか y/n: ") == "y":

                    save_table(path, header, data)

                    return

            continue

        meaning = input("意味: ")

        if meaning == "":
            print("意味が空です")

            continue

        data.append([word, meaning])


def Noneinput(text):

    s = input(text)

    if s == "":
        
        s = "None"
    
    return s


def Falseinput(text):

    s = input(text)

    if s == "":

        s = "False"
    
    return s


def create_table():

    name = input("ファイル名: ")

    path = os.path.join(TABLE_DIR, name)

    tags = Noneinput("タグ: ")
    desc = Noneinput("説明: ")
    labels = Noneinput("ラベル: ")
    num = Falseinput("番号(True,1 or False): ")

    header = [tags, desc, labels, num]

    numbering = num.split(",")[0] == "True"

    start = int(num.split(",")[1]) if numbering else 0

    data = []

    edit_loop(path, header, data, numbering, start)


def edit_table():

    files = os.listdir(TABLE_DIR)

    for i, f in enumerate(files):
        print(i, f)

    idx = int(input("> "))

    path = os.path.join(TABLE_DIR, files[idx])

    header, data, numbering, start = load_table(path)

    edit_loop(path, header, data, numbering, start)


def main():

    print("1:新規")
    print("2:編集")

    s = input("> ")

    if s == "2":
        edit_table()
    else:
        create_table()


if __name__ == "__main__":
    main()