from PIL import ImageGrab, Image
import numpy as np
import json
import collections
import os
import random

encoder = 1 << np.arange(8)
def encode(binary):
    return np.sum(encoder * binary[:, 0])

def grabCharacterData(filename):
    if filename == "accented.png":
        dy = 11
    else:
        dy = 8
    
    image = Image.open(filename)
    channel = image.getchannel('A')
    data = np.array(channel.getdata())

    data[data < 128] = 1
    data[data >= 128] = -1
    data = data.reshape(image.size)

    res = []
    for y in range(image.height // 8):
        row = []
        for x in range(image.width // 8):
            row.append(characterAt(data, y, x, dy))
        res.append(row[:])

    return res

def characterAt(data, y, x, dy = 8):
    x *= 8
    y *= dy
    c = data[y:y+dy, x:x+8]
    totals = np.sum(c, axis = 0)
    if np.all(totals == dy):
        end = 3
    else:
        end = np.max(np.where(totals != dy)) + 1
    return c[:, :end]

def grabJsonData(filename):
    res = dict()

    with open(filename, 'r') as f:
        data = json.load(f)
    
    for prov in data["providers"]:
        name = prov['file'].split('/')[1]
        res[name] = list(map(
            lambda s: s.replace('\x00', ' '),
            prov['chars']
        ))
    
    return res

def grabAll():
    folder = "C:/Users/brigh/AppData/Roaming/.minecraft/versions/1.20.1/1.20.1/assets/minecraft/textures/font/"
    json_data = grabJsonData("C:/Users/brigh/AppData/Roaming/.minecraft/versions/1.20.1/1.20.1/assets/minecraft/font/include/default.json")

    # encoder = 1 << np.arange(8)
    res = collections.defaultdict(lambda: list())

    for image_name in json_data:
        strings = json_data[image_name]
        binary = grabCharacterData(folder + image_name)
        for y, row in enumerate(strings):
            for x, c in enumerate(row):
                cbin = binary[y][x]
                if cbin.size == 0:
                    continue
                key = encode(cbin)
                res[key].append((c, cbin))
        # yield json_data[image_name], grabCharacterData(folder + image_name)
    return res

def chooseCharacter(char_data, img_data):
    highest = -1
    best = ""
    best_width = 0

    # for strings, binary in char_data:
    #     for y, all_chars in enumerate(strings):
    #         for x, c in enumerate(all_chars):
    #             cbin = characterAt(binary, y, x)
    #             h, w = cbin.shape
    #             if h == 0:
    #                 continue
    #             cropped = img_data[:h, :w]
    #             if cropped.size != cbin.size:
    #                 continue
    #             score = np.sum(cropped * cbin) / (w * h + 0.1)
    #             if score > highest:
    #                 highest = score
    #                 best = c
    #                 best_width = w

    key = encode(img_data)

    if key not in char_data:
        return "", 0

    for c, cbin in char_data[key]:
        h, w = cbin.shape
        cropped = img_data[:h, :w]

        if cropped.size != cbin.size:
            continue

        score = np.sum(cropped * cbin) / (w * h + 0.1)

        if score > highest:
            highest = score
            best = c
            best_width = w

    if highest < 0.95:
        return "", 0

    return best, best_width

def loadScreenshot():
    image = ImageGrab.grabclipboard()

    if image is None:
        return None

    # image = Image.open("helloworld.png")
    image = image.crop((770, 157, 1226, 661))
    image = image.reduce(4)
    image.save("preview.png")

    channel = image.getchannel(0)
    data = np.array(channel.getdata())

    data[data < 128] = -1
    data[data >= 128] = 1
    data = data.reshape((126, 114))
    return data

def readScreenshot(char_data, img_data):
    res = ""

    for i in range(14):
        y = i * 9
        x = 0
        text = ""
        nonempty = np.sum(img_data[y:y+8, x:], 0) != 8

        if not np.any(nonempty):
            res += "\n"
            continue

        end_x = np.max(np.where(np.sum(img_data[y:y+8, x:], 0) != 8))

        while x <= end_x:
            data = img_data[y:y+8, x:x+8]
            c, dx = chooseCharacter(char_data, data)
            x += dx + 1
            text += c

        res += text + "\n"
    
    return res[:-1]

def main():
    char_data = grabAll()

    current_book = []
    current_coords = ""
    current_author = ""
    current_title = ""

    while True:
        print()
        print("To edit the current book's title, type 'T',")
        print("Or to edit the current book's author, type 'A'.")
        start = input("Enter to continue, 'Q' to quit: ")
        if start.lower() == 'q':
            return

        if start.lower() == 'a':
            current_author = input("Author: ")
            if current_author == "":
                current_author = "Unknown"
            filename = f"library/{current_coords}.json"

            with open(filename, 'w', encoding = 'utf-8') as f:
                json.dump(
                    {
                        "title": current_title,
                        "author": current_author,
                        "pages": current_book
                    },
                    f,
                    indent = 4
                )
            print("** Saved! **")
            continue
    
        if start.lower() == 't':
            current_title = input("Title: ")
            filename = f"library/{current_coords}.json"

            with open(filename, 'w', encoding = 'utf-8') as f:
                json.dump(
                    {
                        "title": current_title,
                        "author": current_author,
                        "pages": current_book
                    },
                    f,
                    indent = 4
                )
            print("** Saved! **")
            continue
        
        img_data = loadScreenshot()
        if img_data is None:
            print("No screenshot found")
            continue
            
        text = readScreenshot(char_data, img_data)
        print()
        print(text)
        print()

        print("If this is a new book, enter your coords, formatted 'x_z'.")
        print("If you are continuing the previous book, press Enter.")
        opt = input("To cancel, type C: ")

        if opt.lower() == 'c':
            continue
        if opt != '':
            current_coords = opt
            filename = f"library/{current_coords}.json"

            if os.path.exists(filename):
                print("WARNING")
                print("-------")
                print("This file already exists!")
                password = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                if input(f"Type {password} to overwrite this file.").lower() != password.lower():
                    print("xx Failed to save xx")
                    continue
            
            current_author = input("Author: ")
            if current_author == "":
                current_author = "Unknown"
            current_book = []
            current_title = ""
        
        current_book.append(text)

        with open(filename, 'w', encoding = 'utf-8') as f:
            json.dump(
                {
                    "title": current_title,
                    "author": current_author,
                    "pages": current_book
                },
                f,
                indent = 4
            )
        print("** Saved! **")

if __name__ == "__main__":
    main()

