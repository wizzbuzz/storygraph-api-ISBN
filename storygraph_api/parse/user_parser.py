from storygraph_api.request.user_request import UserScraper
from storygraph_api.exception_handler import parsing_exception
from bs4 import BeautifulSoup
import re
from datetime import datetime

class UserParser:
    @staticmethod
    @parsing_exception 
    def parse_html(html,get_id, get_isbn, get_format, get_language, get_pub_date, get_author):
        soup = BeautifulSoup(html, 'html.parser')
        books_list = []
        books = list({element.parent for element in soup.find_all(class_="book-title-author-and-series") if element.parent})
        for book in books:
            book_details = {}
            title = book.find('a').text
            book_details["title"] = title
            if(get_author):
                try:
                    book_author = book.select_one('a[href*="author"]').text
                    book_details["book_author"] = book_author
                except:
                    book_details["book_author"] = None

            if(get_id):
                try:
                    book_id = book.find('div', class_='edition-info').get('data-book-id')
                    book_details["book_id"] = book_id
                except:
                    book_details["book_id"] = None

            if(get_pub_date):
                try:
                    book_pub_date = UserParser.get_detail(book, "edition pub date")
                    book_details["book_pub_date"] = datetime.strptime(book_pub_date, "%d %b %Y").isoformat().split("T")[0]
                except:
                    book_details["book_pub_date"] = None

            UserParser.add_detail_to_list(get_isbn, book, book_details, "book_isbn", "isbn")
            UserParser.add_detail_to_list(get_format, book, book_details, "book_format", "format")
            UserParser.add_detail_to_list(get_format, book, book_details, "book_language", "language")

            books_list.append(book_details)
        data = list({
            (book.get('title'), book.get('book_id'), book.get('book_isbn')): book 
            for book in books_list
            }.values())
        return data

    @staticmethod
    def add_detail_to_list(detail_boolean, book, book_details, book_detail_name, query):
        if(detail_boolean):
            try:
                book_isbn = UserParser.get_detail(book, query)
                book_details[book_detail_name] = book_isbn
            except:
                book_details[book_detail_name] = None

    @staticmethod
    def get_detail(book, name):
        return book.find('span', string=re.compile(rf'{name}', re.IGNORECASE)).parent.text.split(":")[1][1::]

    @staticmethod
    def currently_reading(uname, cookie,get_id, get_isbn, get_format, get_language, get_pub_date, get_author):
        content = UserScraper.currently_reading(uname,cookie)
        return UserParser.parse_html(content,get_id, get_isbn, get_format, get_language, get_pub_date, get_author)

    @staticmethod
    def to_read(uname, cookie,get_id, get_isbn, get_format, get_language, get_pub_date, get_author):
        content = UserScraper.to_read(uname,cookie)
        return UserParser.parse_html(content,get_id, get_isbn, get_format, get_language, get_pub_date, get_author)

    @staticmethod
    def books_read(uname, cookie,get_id, get_isbn, get_format, get_language, get_pub_date, get_author):
        content = UserScraper.books_read(uname,cookie)
        return UserParser.parse_html(content,get_id, get_isbn, get_format, get_language, get_pub_date, get_author)
