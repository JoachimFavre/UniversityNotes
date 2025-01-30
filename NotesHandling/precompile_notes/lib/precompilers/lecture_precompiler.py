import re

from typing import List
from pathlib import Path

from lib.file_loader import FileLoader
from lib.loaded_files.lecture_info import LectureInfo
from lib.logger import Logger
from lib.parser import Parser
from lib.precompilers.generic_precompiler import GenericPrecompiler


class LecturePrecompiler:
    def __init__(self, latex: str):
        self.latex = latex
    
    @staticmethod
    def full_precompile(latex: str, is_english: bool, lecture_info: LectureInfo|None, latex_path: Path, asset_paths: List[Path]) -> "str":
        latex = GenericPrecompiler.full_precompile(latex, is_english, lecture_info, latex_path)
        return LecturePrecompiler(latex)\
            .increase_section_level()\
            .increase_asset_name_level(asset_paths)\
            .replace_chapter_after_lecture_command()\
            .remove_summary_in_lecture_command()\
            .latex

    def increase_section_level(self) -> "LecturePrecompiler":
        latex = self.latex
        latex = latex.replace("\\section", "\\chapter")
        latex = latex.replace("\\subsection", "\\section")
        latex = latex.replace("\\subsubsection", "\\subsection")
        return LecturePrecompiler(latex)
    
    def increase_asset_name_level(self, asset_paths: List[Path]) -> "LecturePrecompiler":
        # Turn picture.png into Lecture05/picture.png in LaTeX
        latex = self.latex
        for asset_path in asset_paths:
            asset_name = asset_path.name  # a/b/c/d.png becomes d.png
            new_asset_name = str(asset_path.relative_to(asset_path.parent.parent))  # a/b/c/d.png becomes c/d.png
            new_asset_name = new_asset_name.replace("\\", "/")
            if latex.count(f"{{{asset_name}}}") == 0:
                Logger.warn(f"Asset in folder but not found in latex file.", asset_path)
            latex = latex.replace(f"{{{asset_name}}}", f"{{{new_asset_name}}}")

        return LecturePrecompiler(latex)
    
    def replace_chapter_after_lecture_command(self) -> "LecturePrecompiler":
        lecture_command = Parser.find_lecture_command(self.latex)
        if lecture_command is None:
            return self
        summary_open_bracket = lecture_command.end(0) - 1
        summary_close_bracket = Parser.matching_parenthesis(self.latex, summary_open_bracket)

        chapter_pattern = r"\\chapter"
        first_chapter = re.search(chapter_pattern, self.latex)
        if first_chapter is None:
            return self

        if Parser.something_between(self.latex, start=summary_close_bracket+1, end=first_chapter.start(0)):
            return self
        
        latex = self.latex
        latex = latex[:lecture_command.start(0)] + r"\cleardoublepage" + "\n" + latex[lecture_command.start(0):]
        latex = re.sub(chapter_pattern, r"\\chapterafterlecture", latex, count=1)
        return LecturePrecompiler(latex)
    
    def remove_summary_in_lecture_command(self) -> "LecturePrecompiler":
        lecture_command = Parser.find_lecture_command(self.latex)
        if lecture_command is None:
            return self
        summary_open_bracket = lecture_command.end(0) - 1
        summary_close_bracket = Parser.matching_parenthesis(self.latex, summary_open_bracket)
        latex = self.latex
        latex = latex[:summary_open_bracket + 1] + latex[summary_close_bracket:]
        return LecturePrecompiler(latex)

    def apply_template(self) -> "GenericPrecompiler":
        # Stip latex before applying the template
        latex = self.latex.strip()

        template = FileLoader.lecture_template()
        replacement = {
            'content': latex,
        }
        latex = FileLoader.replace_in_template(template, replacement)
        return GenericPrecompiler(latex)