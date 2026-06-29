prices = {}#这是创建了一个字典

prices["苹果"] = 5.5#这是给字典添加了一个键值对，键是苹果，值是5.5,这是字典的添加方式
prices["香蕉"] = 4.0#这是给字典添加了一个键值对，键是香蕉，值是4.0,这也是字典的添加方式

print(prices)#这是打印字典的内容，输出结果是{'苹果': 5.5, '香蕉': 4.0}
print(prices["苹果"])#这是打印字典中键为苹果的值，输出结果是5.5
print(prices.get("苹果"))#这是打印字典中键为苹果的值，输出结果是5.5,这是字典的获取方式
print(prices["香蕉"])#这是打印字典中键为香蕉的值，输出结果是4.0



books = {}#这是创建了一个书的字典
books["py入门"] = True  #这是给books的字典增加了一个键值对，其中py入门是键，True是值

print(books)
print(books["py入门"])#这是打印字典中键为py入门的值，输出结果是True
print(books.get("py入门"))#这是打印字典中键为py入门的值，输出结果是True,这是字典的获取方式
# 温和的方式

title = "py入门"

if title in books:
	print("这本书存在")
else:
	print("这本书不存在")

if books[title]:
	print("这本书可借")
else:
	print("这本书已经借出")
	