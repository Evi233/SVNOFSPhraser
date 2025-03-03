from biaodingyi import DataEntry

'''
数据块
'''
class BaseBlock:
    def __init__(self, entry=None, block_content=None):
        self.entry = entry if entry else DataEntry() #如果提供了 entry就用，不然就新建（基础）
        self.block_content = block_content if block_content else bytearray()#放内容

    def zhuanhuanweitext(self):
        """
        注意编码！！！是utf8
        """
        return self.block_content.decode('utf-8', errors='ignore') 
