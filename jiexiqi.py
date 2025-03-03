#zhubiao：主表
#jiugeshi：旧格式
#jiazaimeta：加载元数据
#offsetmingzi：偏移量读名字
#dustringyoulong:读字符串有前缀长度
#wenjianwei：设置文件位（因为用的是流读取字节）
#daowenjianwei：到文件尾了吗？
#getmingzitext：获取名字（给其他文件用）
#chazhaomingziblock：查找名字块
import struct
import os
from biaodingyi import EntryTypes, DataEntry
from mingkuai import NamedBlock

class NofsParser:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file#文件路径
        self.main_entry_list = []#
        self.name_index_map = {}
        self.is_valid = False#（验证？）
        self.version_number = 0#版本
        self.file_total_size = 0#文件大小
        self.is_old_format = False#旧格式（stand）


        with open(self.path_to_file, 'rb') as input_stream:
            if struct.unpack('<i', input_stream.read(4))[0] != 0xF580:#开头到4字节，魔数
                print("Invalid File Magic Number")#不是nofs
                return
            if struct.unpack('<i', input_stream.read(4))[0] > 13:#4-8字节
                print("Unsupported File Format Version")#版本没有（新的？可能SV2）
                #开源注：目前无论如何声库最高就13
                return
            if struct.unpack('<q', input_stream.read(8))[0] != os.path.getsize(self.path_to_file):#8-16，文件大小
                print("File Incomplete")#不完整
                return

            if not self.zhubiao(input_stream):
                print("Failed to Load Main Entry Table")#主表坏了
                return
            if not self.jiazaimeta(input_stream):
                print("Failed to Load Entry Metadata")#元信息坏
                return
            if not self.jiugeshi(input_stream):
                print("Failed to Create Legacy Table")#旧版本声库创建不了
                return

            self.is_valid = True#检查完毕



    def zhubiao(self, input_stream):#加载主表
        try:
            struct.unpack('<i', input_stream.read(4))[0]
            if struct.unpack('<h', input_stream.read(2))[0] != EntryTypes.MasterTableHeader:
                return False

            while True:
                current_entry = DataEntry()
                current_entry.identifier = struct.unpack('<i', input_stream.read(4))[0]
                current_entry.position = struct.unpack('<q', input_stream.read(8))[0]
                if current_entry.identifier == 0:
                    break
                self.main_entry_list.append(current_entry)
            return True
        except:
            return False

    def jiugeshi(self, input_stream):#旧格式
        if self.getmingzitext(".type") != "mu":#声库类型不是mu
                                                #开源注：mu是AI声库
            self.is_old_format = True#就是旧版
            self.main_entry_list = []

            current_offset = 0x10#偏移量
            while not self.daowenjianwei(input_stream, current_offset) and current_offset <= (self.file_total_size - 0x6):
                if not self.wenjianwei(input_stream, current_offset):
                    return current_offset < (self.file_total_size - 0x1000)

                current_entry = DataEntry()
                current_entry.identifier = current_offset
                current_entry.position = current_offset

                current_entry.data_length = struct.unpack('<i', input_stream.read(4))[0]
                current_entry.entry_kind = struct.unpack('<h', input_stream.read(2))[0]

                if current_entry.entry_kind not in [EntryTypes.NamedBlock, EntryTypes.Frame, EntryTypes.FrameNodeTable, EntryTypes.MasterTableHeader, EntryTypes.MasterNodeTable, EntryTypes.MasterNodeTable]:
                    return False
                if current_entry.data_length == 0:
                    return current_offset < (self.file_total_size - 0x1000)

                entry_index = len(self.main_entry_list)
                self.main_entry_list.append(current_entry)

                if current_entry.entry_kind == EntryTypes.NamedBlock:
                    name_size = struct.unpack('<h', input_stream.read(2))[0]
                    if name_size == 0:
                        goto_next = True
                    else:
                        name_bytes = input_stream.read(name_size)
                        if len(name_bytes) != name_size:#长度
                            goto_next = True
                        else:
                            name = name_bytes.decode('utf-8', errors='ignore')#未知原因，效率低下
                            self.name_index_map[name] = entry_index
                            goto_next = False

                    if goto_next:
                        pass
                current_offset += current_entry.data_length
            return True
        return True

    def jiazaimeta(self, input_stream):
        for i in range(len(self.main_entry_list)):
            current_entry = self.main_entry_list[i]
            if not self.wenjianwei(input_stream, current_entry.position):
                return False
            current_entry.data_length = struct.unpack('<i', input_stream.read(4))[0]
            current_entry.entry_kind = struct.unpack('<h', input_stream.read(2))[0]

            if current_entry.entry_kind == EntryTypes.NamedBlock:
                name_size = struct.unpack('<h', input_stream.read(2))[0]
                if name_size == 0:
                    return False
                name_bytes = input_stream.read(name_size)
                if len(name_bytes) != name_size:
                    return False
                name = name_bytes.decode('utf-8', errors='ignore')
                self.name_index_map[name] = i
        return True

    def offsetmingzi(self, input_stream, offset):
        if not self.wenjianwei(input_stream, offset):
            return None

        struct.unpack('<i', input_stream.read(4))[0]
        struct.unpack('<h', input_stream.read(2))[0]

        name = self.dustringyoulong(input_stream)
        if not name:
            return None

        data_size = struct.unpack('<i', input_stream.read(4))[0]
        if data_size == 0:
            return None

        data = input_stream.read(data_size)
        if len(data) != data_size:
            return None

        return NamedBlock(block_name=name.decode('utf-8', errors='ignore'), block_content=bytearray(data))

    def dustringyoulong(self, input_stream):
        string_size = struct.unpack('<h', input_stream.read(2))[0]
        if string_size == 0:
            return b""
        string_bytes = input_stream.read(string_size)
        if len(string_bytes) != string_size:
            return None
        return string_bytes

    def wenjianwei(self, input_stream, position):
        try:
            input_stream.seek(position)
            return True
        except:
            return False

    def daowenjianwei(self, input_stream, current_pos):
        return current_pos >= self.file_total_size

    def getmingzitext(self, name):
        named_block = self.chazhaomingziblock(name)
        if named_block:
            return named_block.zhuanhuanweitext()
        return ""

    def chazhaomingziblock(self, name):
        index = self.name_index_map.get(name)
        if index is None:
            return None

        entry = self.main_entry_list[index]
        try:
            with open(self.path_to_file, 'rb') as input_stream:
                block = self.offsetmingzi(input_stream, entry.position)
                if block:
                    block.entry = entry
                return block
        except:
            return None

    def youxiao(self):
        #有效检查
        return self.is_valid

    def geshiwenben(self):
        #格式文本
        return self.version_number

    def wenjiandaxiao(self):
        #文件大小
        return self.file_total_size

    def suoyourukou(self):
        #算了我自己也忘了
        #索引入口？
        return self.main_entry_list

    def mingzisuoyin(self):
        #名字索引
        return self.name_index_map
