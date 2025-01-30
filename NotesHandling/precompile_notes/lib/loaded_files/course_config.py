from typing import Dict, List

class CourseConfig:
    def __init__(self, json: Dict[str, str|bool|List[List[int]]]):
        self.title = str(json["title"])
        self.title_alias = str(json["title-alias"])
        self.professor = str(json["professor"])
        self.english = bool(json["english"])

        self.reorderings: List[List[int]] = []
        if "reorderings" in json:
            reorderings = json["reorderings"]
            if not isinstance(reorderings, List):
                raise Exception("Reorderings must be a list.")
            self.reorderings = reorderings

            for reordering in self.reorderings:
                if len(reordering) != 2:
                    raise Exception("Reorderings must have exactly 2 elements: they switch pairs of consecutive elements.")
        
        self.comment: str|None = None
        if "comment" in json:
            self.comment = str(json["comment"])
