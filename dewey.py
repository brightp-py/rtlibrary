import json
import os

class Dewey:

    def __init__(self):
        with open("dewey.json", 'r', encoding = 'utf-8') as f:
            self.dewey_data = json.load(f)
        
        self.atitle = ""
        self.btitle = ""
        self.ctitle = ""

        self.decimal = ""
    
    def menu(self):

        options = self.dewey_data
        
        if self.atitle != "":
            options = options[self.atitle]
        
        if self.btitle != "":
            options = options[self.btitle]

        options = list(options)
        
        print()
        for i, opt in enumerate(options):
            print(i, opt)
        
        res = "_"
        while res not in "0123456789xr":
            res = input("Select: ")

        if res == "x":
            self.reset()
            return

        if res == "r":
            with open("dewey.json", 'r', encoding = 'utf-8') as f:
                self.dewey_data = json.load(f)
            self.reset()
            return
        
        else:
            i = int(res)
            if self.atitle == "":
                self.atitle = options[i]
            elif self.btitle == "":
                self.btitle = options[i]
            elif self.ctitle == "":
                self.ctitle = options[i]
            self.decimal += res

    def reset(self):
        self.atitle = ""
        self.btitle = ""
        self.ctitle = ""
        self.decimal = ""

class Book:
    PAGEWIDTH = 30

    def __init__(self, filename):
        self.filename = filename

        with open(filename, 'r', encoding = 'utf-8') as f:
            self.data = json.load(f)
        
        self.needsDewey = 'dewey' not in self.data
        
        pages = self.data['pages']
        pages = [page.split('\n') for page in pages[:6]]
        self.text = '\n'.join(map(Book.joinStories, list(zip(*pages))))
    
    def setDewey(self, decimal):
        self.data['dewey'] = decimal

        with open(self.filename, 'w', encoding = 'utf-8') as f:
            json.dump(self.data, f, indent = 4)

    @staticmethod
    def joinStories(lines):
        res = ""
        width = 0

        for line in lines:
            res += line
            width += Book.PAGEWIDTH
            res += ' ' * (width - len(res))
        
        return res
    
    @staticmethod
    def loadAll():
        for dirpath, _, filenames in os.walk("library"):
            for filename in filenames:
                b = Book(os.path.join(dirpath, filename))
                if b.needsDewey:
                    yield b

def main():
    d = Dewey()
    books = Book.loadAll()

    for book in books:

        while True:
            print()
            print(book.text)
            d.menu()

            if len(d.decimal) == 3:
                book.setDewey(d.decimal)
                d.reset()
                break

if __name__ == "__main__":
    main()