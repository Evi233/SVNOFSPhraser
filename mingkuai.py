from kuai import BaseBlock
#附属块，虽然只使用一次，就先放着
class NamedBlock(BaseBlock):
    def __init__(self, entry=None, block_content=None, block_name=None, original_name=None):
        super().__init__(entry, block_content)
        self.block_name = block_name if block_name else ""#bn？！
        self.original_name = original_name#on=传入的on
