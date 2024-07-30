from pathlib import Path
from lib.course import Course

# TODO: Would a main.py file be useful too
class Style:
    def __init__(self, latex: str):
        self.latex = latex
    
    @staticmethod
    def from_course(course: Course) -> "Style":
        result = course.loader.style()
        config = course.loader.config()
        if result.count(r"\usepackage[british]{babel}") == 0:
            raise Exception("The style file must contain the line \\usepackage[british]{babel}.")
        if not config.english:
            result = result.replace(r"\usepackage[british]{babel}", r"\usepackage[french]{babel}")
        return Style(result)
        
    def write(self, root_path: Path):
        with open(root_path/"style.sty", "w+", encoding="utf-8") as file:
            file.write(self.latex)
