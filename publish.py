import json
import os
import keyboard
import pyperclip

endNote = """The Great Library
does not expressly
endorse the opinions
presented in this
book, nor has the
provided information
been reviewed.

To present an issue
or remove your book
from the Library,
message Bright#0854.

Thank you!"""

class Book:
    PAGEWIDTH = 30
    TITLEWIDTH = 18

    def __init__(self, filename):
        self.filename = filename

        with open(filename, 'r', encoding = 'utf-8') as f:
            self.data = json.load(f)
        
        self.needsDewey = 'dewey' not in self.data
        
        pages = self.data['pages']
        pages = [page.split('\n') for page in pages[:6]]
        self.text = '\n'.join(map(Book.joinStories, list(zip(*pages))))

        if self.data['title'] == '':
            print("Title needed!")
            print(self.text)
            self.data['title'] = input("Title: ")
            print()
            self.saveData()

    def center(self, text):
        indent = ' ' * int((19 - len(text)) * 0.75)
        return indent + text
    
    def formattedTitle(self):
        lines = [""]
        words = self.data['title'].upper().split(' ')

        while words:
            nline = lines[-1] + ' ' + words[0]
            if len(nline) > Book.TITLEWIDTH:
                lines[-1] = self.center(lines[-1])
                lines.append(words[0])
            else:
                lines[-1] = nline
            del words[0]
        
        lines[-1] = self.center(lines[-1])

        lines = [''] * (5 - len(lines)) + lines

        return '\n'.join(lines)
    
    def coords(self):
        x = self.filename.split('\\')[-1].split('_')[0]
        z = self.filename.split('_')[-1].split('.')[0]
        return f"x: {x}, z: {z}"
    
    def titlePage(self):
        text = self.formattedTitle()

        if len(self.data['author']) < 19:
            text += "\n\n\n\n"
        else:
            text += "\n\n\n"
        
        text += self.center(self.data['author'])
        text += "\n\n"
        text += self.center(self.data['dewey'])
        text += "\n\n"
        text += self.center(self.coords())

        return text
    
    def sortKey(self):
        res = self.data['dewey'] + self.data['author']
        res += self.data['title']
        return res
    
    def saveData(self):
        with open(self.filename, 'w', encoding = 'utf-8') as f:
            json.dump(self.data, f, indent = 4)
    
    def setDewey(self, decimal):
        self.data['dewey'] = decimal
        self.saveData()
    
    def getPages(self):
        yield self.titlePage()
        for page in self.data['pages']:
            yield page
        yield endNote
        while True:
            yield ""

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
        res = []
        for dirpath, _, filenames in os.walk("library"):
            for filename in filenames:
                b = Book(os.path.join(dirpath, filename))
                if not b.needsDewey:
                    res.append(b)
        return sorted(res, key = lambda x: x.sortKey())

class BookCopier:

    def __init__(self):
        self.books = list(Book.loadAll())
        self.goto(0)
        self.pages = self.reset()
    
    def reset(self):
        self.pages = self.book.getPages()
    
    def getPage(self):
        pyperclip.copy(next(self.pages))
    
    def nextBook(self):
        self.i += 1
        self.book = self.books[self.i]
        self.reset()
    
    def prevBook(self):
        self.i -= 1
        self.book = self.books[self.i]
        self.reset()

    def goto(self, i):
        self.i = i
        self.book = self.books[self.i]
        self.reset()

def main():
    copier = BookCopier()
    
    keyboard.add_hotkey('ctrl+d', copier.getPage)

    while True:
        opt = input(str(copier.i) + '\t' + copier.book.data['title'] + ' ' + str(2 + len(copier.book.data['pages'])) + ' ')
        if opt == "":
            copier.nextBook()
        elif opt.lower() == "r":
            copier.reset()
        elif opt == "-":
            copier.prevBook()
        elif all(digit in "0123456789" for digit in opt):
            copier.goto(int(opt))
        elif opt.lower() == "q":
            break

if __name__ == "__main__":
    main()