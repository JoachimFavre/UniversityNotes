from enum import Enum

class Tags(Enum):
    NONE = (None, "temp-2")
    PRINTED = ("Printed", "printed")
    OFFICIAL = ("Official", "official")

    def __init__(self, tag: str|None, output_dir: str):
        self.tag = tag
        self.output_dir = output_dir
