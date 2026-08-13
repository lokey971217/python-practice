"""Python review exercise: build a small product price manager.

Complete the TODO sections one at a time.
Run `python practice.py` to use the menu.
Run `python check_progress.py` to check your progress.
"""


def parse_price(text: str) -> float:
    try:
        price = float(text)
    except ValueError:
        raise ValueError("请输入数字")
    
    if price < 0:
        raise ValueError("价格不能小于 0")
    
    return price









    """Convert text to a non-negative price."""
    # TODO 1:
    # 1. Use float(text) to convert the text.
    # 2. If conversion fails, raise ValueError("请输入数字").
    # 3. If the price is negative, raise ValueError("价格不能小于 0").
    # 4. Return the price.
    raise NotImplementedError("请完成 TODO 1")


def add_product(prices: dict[str, float], name: str, price: float) -> bool:
    name = name.strip()

    if not name:
        return False
    
    if name in prices:
        return False
    
    prices[name] = price


    return True
                  



    books = {}





    """Add a new product; return False when its name already exists."""
    # TODO 2:
    # 1. Remove spaces around name with strip().
    # 2. Return False if name is empty or already in prices.
    # 3. Save the price with prices[name] = price.
    # 4. Return True.
    raise NotImplementedError("请完成 TODO 2")


def find_price(prices: dict[str, float], name: str) -> float | None:
    # if name in prices:
    #     return prices[name]
    # return None
    return prices.get(name)










    """Return a product's price, or None when it does not exist."""
    # TODO 3: Use prices.get(...) to return the result.
    raise NotImplementedError("请完成 TODO 3")


def update_price(prices: dict[str, float], name: str, new_price: float) -> bool:
    if name in prices:
        prices[name] = new_price
        return True
    return False
    
    
    
    
    
    
    
    """Update an existing product; return whether it was found."""
    # TODO 4:
    # 1. Return False if name is not in prices.
    # 2. Replace the old value with new_price.
    # 3. Return True.
    raise NotImplementedError("请完成 TODO 4")


def print_products(prices: dict[str, float]) -> None:
    for name,price in prices.items():
        print(f"{name}：{price:.2f} 元")

    return None


    for  name,price  in prices.items():
        print(f"name")


    """Print every product and price."""
    # TODO 5:
    # Use `for name, price in prices.items():` to print every item.
    # Suggested output: 苹果：5.50 元
    raise NotImplementedError("请完成 TODO 5")


def main() -> None:
    prices: dict[str, float] = {}

    while True:
        print("\n=== 商品价格管理器 ===")
        print("1. 添加商品")
        print("2. 查找价格")
        print("3. 修改价格")
        print("4. 显示全部")
        print("5. 退出")
        choice = input("请选择：").strip()

        try:
            if choice == "1":
                name = input("商品名称：")
                price = parse_price(input("商品价格："))
                added = add_product(prices, name, price)
                print("添加成功。" if added else "名称为空或商品已存在。")

            elif choice == "2":
                name = input("商品名称：").strip()
                price = find_price(prices, name)
                if price is None:
                    print("没有找到该商品。")
                else:
                    print(f"{name}：{price:.2f} 元")

            elif choice == "3":
                name = input("商品名称：").strip()
                new_price = parse_price(input("新价格："))
                updated = update_price(prices, name, new_price)
                print("修改成功。" if updated else "没有找到该商品。")

            elif choice == "4":
                print_products(prices)

            elif choice == "5":
                print("练习结束。")
                return

            else:
                print("请输入 1 到 5。")

        except (ValueError, NotImplementedError) as error:
            print(f"提示：{error}")


if __name__ == "__main__":
    main()






prices = {}#这是创建了一个字典

prices["苹果"] = 5.5#这是给字典添加了一个键值对，键是苹果，值是5.5,这是字典的添加方式
prices["香蕉"] = 4.0#这是给字典添加了一个键值对，键是香蕉，值是4.0,这也是字典的添加方式

print(prices)#这是打印字典的内容，输出结果是{'苹果': 5.5, '香蕉': 4.0}
print(prices["苹果"])#这是打印字典中键为苹果的值，输出结果是5.5
print(prices.get("苹果"))#这是打印字典中键为苹果的值，输出结果是5.5,这是字典的获取方式
print(prices["香蕉"])#这是打印字典中键为香蕉的值，输出结果是4.0