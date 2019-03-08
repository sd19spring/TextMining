################################################################################

"""
This software will take a list of books (book_list) and automatically find,
download, and generate all associated files for the books.
"""

################################################################################

import requests
import os
from classes import Book
import pickle

################################################################################

book_list = [
('Frankenstein, by Mary Wollstonecraft (Godwin) Shelley'),
('A Tale of Two Cities, by Charles Dickens'),
('The Adventures of Sherlock Holmes, by Arthur Conan Doyle'),
('Adventures of Huckleberry Finn, by Mark Twain'),
('The Yellow Wallpaper, by Charlotte Perkins Gilman'),
('Metamorphosis, by Franz Kafka')
]


# book_list = [('The Adventures of Sherlock Holmes', 'Arthur Conan Doyle')]

def build_gutenberg_index():
    """
    Generates a python-readable index of project gutenberg's master index -
    GUTINDEX.txt - called gutenberg_index.txt. Returns a dictionary of the
    index. If gutenberg_index.txt exists, it is deleted and redownloaded.
    """
    if os.path.exists("gutenberg_index.txt"):
        print("Deleting old gutenberg_index.txt file.")
        os.system("rm -rf gutenberg_index.txt")

    gut_index_file = open("GUTINDEX.txt", 'r+')
    gut_index_text = gut_index_file.read()
    gut_index_file.close()

    skip_line_if = [" ", "~", "TITLE"]
    end_title_if = ["  ", " 1", " 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9"]
    gutenberg_index = {}
    gut_lines = gut_index_text.split("\n")

    print("Generating gutenberg_index dictionary and writing as \
gutenberg_index.txt")
    for line in gut_lines[260:]:
        if line == "<==End of GUTINDEX.ALL==>":
            break
        else:
            if len(line) != 0:
                if line[0] not in skip_line_if or line[0:5] not in skip_line_if:
                    for i in range(len(line)-1):
                        if line[i:i+2] in end_title_if:
                            book_name_author = line[0:i]
                            for j in range(0, len(line)):
                                if line[len(line)-j-1] == " ":
                                    book_number = line[len(line)-j:len(line)]
                                    break
                            gutenberg_index[book_name_author] = book_number
                            break
    gut_index_file = open("gutenberg_index.txt", 'wb')
    to_write = pickle.dumps(gutenberg_index)
    gut_index_file.write(to_write)
    gut_index_file.close()
    print("Index successfully generated and written to disk as \
gutenberg_index.txt")
    return gutenberg_index

def check_GUTINDEX():
    """
    Handles the GUTINDEX.txt file - either download it for the first time or
    redownloads the file.
    """
    if os.path.exists("GUTINDEX.txt"):
        yn = input("Redownload the index of project gutenberg - GUTINDEX.txt - \
file and delete the old one? New books may have been added. y/n --> ")
        while True:
            if yn == "y" or yn == "Y":
                print("Deleting old GUTINDEX.txt file")
                os.system("rm -rf GUTINDEX.txt")
                print("Downloading the GUTINDEX file...")
                try:
                    GUTINDEX = requests.get("https://www.gutenberg.org/dirs/GUTINDEX.ALL").text
                except requests.exceptions.MissingSchema:
                    print("Invalid url / could not download from this link")
                    break
                GUTINDEX_file = open("GUTINDEX.txt", "w")
                GUTINDEX_file.write(GUTINDEX)
                GUTINDEX_file.close()

                build_gutenberg_index()
                break
            elif yn == "n" or yn == "N":
                break
            else:
                print("Invalid input; try again")
    else:
        while True:
            try:
                print("Downloading the GUTINDEX file...")
                GUTINDEX = requests.get("https://www.gutenberg.org/dirs/GUTINDEX.ALL").text
            except requests.exceptions.MissingSchema:
                print("Invalid url / could not download from this link")
                break
            GUTINDEX_file = open("GUTINDEX.txt", "w")
            GUTINDEX_file.write(GUTINDEX)
            GUTINDEX_file.close()
            print("Download of the GUTINDEX file successful")

            build_gutenberg_index()
            break

def check_books_folder():
    """
    If existing books/ folder exists, the user is prompted to either delte it
    and make a new folder or keep it. If it doesn't exist, a books/ folder is
    made. The /books folder will store all of the books' files.
    """
    if os.path.exists("books/"):
        yn = input("Delete books/ folder? Problems may arise if there will be \
duplicate files. y/n --> ")
        # TODO: handle invalid characters
        if yn == "y" or yn == "Y":
            yn_2 = input("Are you sure you want to delete the folder /books? y/n --> ")
            if yn_2 == "y" or yn == "Y":
                os.system("rm -rf books")
                os.system("mkdir books")
            else:
                print("Okay, will not delete /books")
        else:
            print("Okay, will not delete /books")
    else:
        os.system("mkdir books")

if __name__=="__main__":
    check_GUTINDEX()
    check_books_folder()

    gutenberg_index_file = open("gutenberg_index.txt", "rb")
    gutenberg_index_text = gutenberg_index_file.read()
    gutenberg_index = pickle.loads(gutenberg_index_text)

    dict_books = {}
    yn = input("Download books from list? y/n --> ")
    if yn == "y" or yn == "Y":
        for book_name_author in book_list:
            print("Downloading: {}".format(book_name_author))
            dict_books[book_name_author] = Book(book_name_author)
            book = dict_books[book_name_author]
            book.make_book(gutenberg_index)
