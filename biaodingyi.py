#数据结构定义（似乎对standard无效？）
class EntryTypes:
    Block             = 0x0
    NamedBlock        = 0x1
    Frame             = 0x10
    FrameNodeTable    = 0x200
    MasterTableHeader = 0x1000
    MasterNodeTable   = 0x2000

class DataEntry:
    def __init__(self):
        self.identifier = 0
        self.position = -1
        self.data_length = 0
        self.entry_kind = 0