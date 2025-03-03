import os
from jiexiqi import NofsParser

def kankan(nofs_path):
    if not os.path.isfile(nofs_path) or not os.access(nofs_path, os.R_OK):#在不？
        print(f"NOFS File Not Found: {nofs_path}")#打不开/找不到
        return

    nofs_file = NofsParser(nofs_path)#设置路径（有概率失败，不知道为啥）
    ###Todo：找到原因
    if not nofs_file.youxiao():
        print(f"Failed to Open NOFS File: {nofs_path}")#打不开（权限）
        return

    nofs_type = nofs_file.getmingzitext(".type")#ype
#type里面的东西
###Todo：错误处理
    print(f"名字:{nofs_file.getmingzitext('.name')}") # Name 缩写为 N
    print(f"公:{nofs_file.getmingzitext('.vendor')}") # Manufacturer 缩写为 M
    print(f"ver:{nofs_file.getmingzitext('.version')}") # Version 缩写为 V
    print(f"默认lang:{nofs_file.getmingzitext('.language')}") # Language 缩写为 L
    print(f"支语言:{nofs_file.getmingzitext('.multi')}")  # Supported Lang 缩写为 SL
    print(f"音素集:{nofs_file.getmingzitext('.phoneset')}") # Phoneme Set 缩写为 P
    print(f"类:{nofs_type}") # Type 缩写为 T
    print(f"AI吗:{'是' if nofs_type == 'mu' else '不'}") # AI 缩写为 A
