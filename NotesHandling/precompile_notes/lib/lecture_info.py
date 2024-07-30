import re

from lib.parser import Parser

class LectureInfo:
    def __init__(self, number: int, date: str, title: str, summary: str):
        self.number = number
        self.date = date
        self.title = title
        self.summary = summary
    
    @staticmethod
    def load_from_latex(latex: str) -> "LectureInfo|None":
        n_lecture_commands = latex.count("\\lecture")
        if n_lecture_commands == 0:
            return None
        elif n_lecture_commands > 1:
            raise Exception(f"Multiple lecture commands found in the same lecture.\nFile content:\n{latex}")
        
        match = Parser.find_lecture_command(latex)
        if match is None:
            raise Exception(f"Lecture command exists but is badly formatted in latex file.\nFile content:\n{latex}")
        
        number = int(match.group(1))
        date = match.group(2)
        title = match.group(3)

        final_bracket = match.end(0) - 1
        summary = Parser.block_content(latex, final_bracket).strip()
        return LectureInfo(number, date, title, summary)

    def __repr__(self) -> str:
        return f"LectureInfo({self.number}, {self.date}, {self.title})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LectureInfo)\
            and self.number == other.number\
            and self.date == other.date\
            and self.title == other.title\
            and self.summary == other.summary
