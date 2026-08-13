# print("通讯录练习开始")

def add_contact(contacts:dict[str,dict[str,str]],name:str,phone:str,city:str) -> bool:
    name = name.strip()
    if not name:
        return False
    if name in contacts:
        return False
    else:
        contacts[name] = {"phone":phone,"city":city}
        return True
    

def find_contact(contacts:dict[str,dict[str,str]],name:str) ->dict[str,str] | None:
    name = name.strip()
    if not name:
        return None
    if name in contacts:
        return contacts[name]
    else:
        return None
    

def update_contact(contacts:dict[str,dict[str,str]],name:str,phone:str,city:str) -> bool:
    name = name.strip()
    if not name:
        return False
    if name not in contacts:
        return False
    contacts[name] = {"phone":phone,"city":city}
    return True


def remove_contact(contacts:dict[str,dict[str,str]],name:str) ->bool:
    name = name.strip()
    if not name:
        return False
    if name in contacts:
        del contacts[name]
        return True
    return False


def print_contacts(contacts:dict[str,dict[str,str]]) ->None:
    if not contacts:
        print(f"暂无联系人")
        return None
    for name in contacts:
        info = contacts[name]
        print(f"姓名：{name},电话号码：{info["phone"]},城市：{info["city"]}")
    

def main():
    contacts = {}
    print(add_contact(contacts,"小明","13511112222","北京"))
    print(contacts)
    print("查找小明:",find_contact(contacts,"小明"))
    print("查找小王:",find_contact(contacts,"小王"))
    print("修改小明",update_contact(contacts,"小明","200444","上海"))
    print("修改后的小明信息：",find_contact(contacts,"小明"))
    # print("删除小明信息：",remove_contact(contacts,"小明"))
    print("查找小明:",find_contact(contacts,"小明"))
    print("查找小王:",find_contact(contacts,"小王"))
    print_contacts(contacts)


if __name__ == "__main__":
    main()


