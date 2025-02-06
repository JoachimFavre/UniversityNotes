from enum import Enum

class Tags(Enum):
    NONE = (None, "outputs/NoTag")
    PRINTED = ("printed", "outputs/Printed")
    OFFICIAL = ("official", "outputs/Official")

    def __init__(self, tag: str|None, output_dir: str):
        self.tag = tag
        self.output_dir = output_dir
