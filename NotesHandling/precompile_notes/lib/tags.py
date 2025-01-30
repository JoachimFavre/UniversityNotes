from enum import Enum

class Tags(Enum):
    NONE = (None, "temp-2")
    PRINTED = ("printed", "Printed")
    OFFICIAL = ("official", "Official")

    def __init__(self, tag: str|None, output_dir: str):
        self.tag = tag
        self.output_dir = output_dir
