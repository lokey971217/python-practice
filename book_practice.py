


def add_book(books:dict[str,bool],title:str)-> bool:
    title = title.strip()

    if not title:
        return False
    
    if title not in books:
        books[title] = True
        return True
    return False


def find_book(books:dict[str,bool],title:str)-> bool| None:
    title = title.strip()

    if not title:
        return None
    
    if title in books: 
        return books[title]
    return None


def borrow_book(books:dict[str,bool],title:str)-> bool:
    title = title.strip()

    if not title:
        return False
    if title in books:
        if books[title]:
            books[title] = False
            return True
        else:
            return False
    return False


def return_book(books:dict[str,bool],title:str)-> bool:
    title = title.strip()
    if not title:
        return False
    if title not in books:
        return False
    if books[title]:
        return False
    else:
        books[title] = True
        return True


def remove_book(books:dict[str,bool],title:str)->bool:
    title = title.strip()
    if not title:
        return False
    if title in books:
        del books[title]
        return True
    else:
        return False


def print_books(books:dict[str,bool])-> None:
    if not books:
        print(f"暂无图书")
        return None
    for title in books:
        if books[title]:
            print(f"{title}是可以借阅的")
        else:
            print(f"{title}已借出")
    
    #另一种方法是print(f"{books.items()}")吗


def main():
    
    books = {}

    add_book(books,"py入门")
    add_book(books,"数学")

    print("查找数学:",find_book(books,"数学"))
    print("查找py入门:",find_book(books,"py入门"))

    print("借py入门:",borrow_book(books,"py入门"))
    print("查找py入门:",find_book(books,"py入门"))
    print("借py入门:",borrow_book(books,"py入门"))
    print("还py入门",return_book(books,"py入门"))
    print("查找py入门:",find_book(books,"py入门"))


    print("删除数学:", remove_book(books, "数学"))
    #print("删除py",remove_book(books,"py入门"))
    print("查找数学:", find_book(books, "数学"))
    print("查找py:", find_book(books, "py入门"))




    print_books(books)


if __name__ == "__main__":
    main()