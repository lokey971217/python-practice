"""Friendly progress checks for the product price manager exercise."""

from practice import (
    add_product,
    find_price,
    parse_price,
    update_price,
)


def run_check(number: int, title: str, check) -> bool:
    try:
        check()
    except (AssertionError, ValueError, NotImplementedError) as error:
        detail = str(error) or "结果与要求不一致"
        print(f"第 {number} 关：未完成 - {title}")
        print(f"  提示：{detail}")
        return False

    print(f"第 {number} 关：通过 - {title}")
    return True


def check_parse_price() -> None:
    assert parse_price("12.5") == 12.5
    try:
        parse_price("-1")
    except ValueError:
        return
    raise AssertionError("负数价格应该触发 ValueError")


def check_add_product() -> None:
    prices: dict[str, float] = {}
    assert add_product(prices, "苹果", 5.5) is True
    assert prices["苹果"] == 5.5
    assert add_product(prices, "苹果", 6.0) is False


def check_find_price() -> None:
    prices = {"苹果": 5.5}
    assert find_price(prices, "苹果") == 5.5
    assert find_price(prices, "香蕉") is None


def check_update_price() -> None:
    prices = {"苹果": 5.5}
    assert update_price(prices, "苹果", 6.0) is True
    assert prices["苹果"] == 6.0
    assert update_price(prices, "香蕉", 4.0) is False


def main() -> None:
    print("=== 练习进度检查 ===")
    results = [
        run_check(1, "转换并检查价格", check_parse_price),
        run_check(2, "添加商品", check_add_product),
        run_check(3, "查找价格", check_find_price),
        run_check(4, "修改价格", check_update_price),
    ]
    completed = sum(results)
    print(f"\n当前完成：{completed}/4")
    if completed == len(results):
        print("核心功能全部通过。最后手动练习 TODO 5 的商品输出。")


if __name__ == "__main__":
    main()
