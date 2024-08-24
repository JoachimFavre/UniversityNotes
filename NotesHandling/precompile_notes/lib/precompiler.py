import re

from typing import List
from pathlib import Path

from lib.course_config import CourseConfig
from lib.file_loader import FileLoader
from lib.lecture_info import LectureInfo
from lib.logger import Logger
from lib.parser import Parser


class Precompiler:
    def __init__(self, latex: str):
        self.latex = latex
    
    def full_precompile(self, is_english: bool, lecture_info: LectureInfo|None, latex_path: Path, asset_paths: List[Path]) -> "Precompiler":
        return Precompiler(self.latex)\
            .remove_before_begin_document()\
            .remove_after_end_document()\
            .remove_make_title()\
            .increase_section_level()\
            .increase_asset_name_level(asset_paths)\
            .replace_chapter_after_lecture_command()\
            .remove_summary_in_lecture_command()\
            .merge_consecutive_empty_slides()\
            .correct_spaces(is_english)\
            .strip()\
            .apply_template()\
            .make_warnings(lecture_info, latex_path)

    def remove_before_begin_document(self) -> "Precompiler":
        match = re.search(r"\\begin{document}", self.latex)
        if match is None:
            raise Exception(r"No \begin{document} found in the latex file.")
        return Precompiler(self.latex[match.end(0):])
    
    def remove_after_end_document(self) -> "Precompiler":
        match = re.search(r"\\end{document}", self.latex)
        if match is None:
            raise Exception(r"No \end{document} found in the latex file.")
        return Precompiler(self.latex[:match.start(0)])

    def remove_make_title(self) -> "Precompiler":
        return Precompiler(self.latex.replace(r"\maketitle", ""))
    
    def increase_section_level(self) -> "Precompiler":
        latex = self.latex
        latex = latex.replace("\\section", "\\chapter")
        latex = latex.replace("\\subsection", "\\section")
        latex = latex.replace("\\subsubsection", "\\subsection")
        return Precompiler(latex)
    
    def increase_asset_name_level(self, asset_paths: List[Path]) -> "Precompiler":
        # Turn picture.png into Lecture05/picture.png in LaTeX
        latex = self.latex
        for asset_path in asset_paths:
            asset_name = asset_path.name  # a/b/c/d.png becomes d.png
            new_asset_name = str(asset_path.relative_to(asset_path.parent.parent))  # a/b/c/d.png becomes c/d.png
            new_asset_name = new_asset_name.replace("\\", "/")
            if latex.count(f"{{{asset_name}}}") == 0:
                Logger.warn(f"Asset in folder but not found in latex file.", asset_path)
            latex = latex.replace(f"{{{asset_name}}}", f"{{{new_asset_name}}}")

        return Precompiler(latex)
    
    def replace_chapter_after_lecture_command(self) -> "Precompiler":
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
        return Precompiler(latex)
    
    def remove_summary_in_lecture_command(self) -> "Precompiler":
        lecture_command = Parser.find_lecture_command(self.latex)
        if lecture_command is None:
            return self
        summary_open_bracket = lecture_command.end(0) - 1
        summary_close_bracket = Parser.matching_parenthesis(self.latex, summary_open_bracket)
        latex = self.latex
        latex = latex[:summary_open_bracket + 1] + latex[summary_close_bracket:]
        return Precompiler(latex)
    
    def merge_consecutive_empty_slides(self) -> "Precompiler":
        if self.latex.count(r"\begin{slidecomment}") > 0:
            raise NotImplementedError("Merging consecutive empty slides is not implemented yet.")
        return self
    
    def correct_spaces(self, is_english: bool) -> "Precompiler":
        # We do not want to correct spaces in code environments.
        # We suppose that those \begin and \end are alone
        # on their line.
        result = []
        in_no_touch_env = 0
        no_touch_envs = ["lstlisting", "filecontents*"]
        for line in self.latex.split("\n"):
            begin = re.search(r"\\begin\{(.*)\}", line)
            end = re.search(r"\\end\{(.*)\}", line)
            if begin is not None and begin.group(1) in no_touch_envs:
                in_no_touch_env += 1
            elif end is not None and end.group(1) in no_touch_envs:
                in_no_touch_env -= 1
            elif in_no_touch_env == 0:
                for char in [";", ":", "!", "?"]:
                    if is_english:
                        # Remove spaces
                        line = line.replace(f" {char}", char)
                        line = line.replace(f"~{char}", char)
                    else:
                        pass
                        ## Add spaces
                        #line = line.replace(f" {char}", char)
                        ## Except for \;, \! https: and http: and watch?v= of youtube
                        #line = re.sub("(?<!\\\\)\\" + char, "~" + char, line)
                        #line = line.replace("http~:", "http:")
                        #line = line.replace("https~:", "https:")
                        #line = line.replace("watch~?v=", "watch?v=")
            result.append(line)
        return Precompiler('\n'.join(result))
    
    def strip(self) -> "Precompiler":
        return Precompiler(self.latex.strip())
    
    def apply_template(self) -> "Precompiler":
        template = FileLoader.latex_template()
        replacement = {
            'content': self.latex,
        }
        latex = FileLoader.replace_in_template(template, replacement)
        return Precompiler(latex)

    def make_warnings(self, lecture_info: LectureInfo|None, file_path: Path) -> "Precompiler":
        latex = self.latex

        if latex.count(r"\part") - latex.count(r"\partial"):
            Logger.warn(r"\part is used.", file_path)

        # We only count parenthesis in text, because we may have \left(1, 3\right] in maths.
        n_opening_parenthesis = latex.count("(") - latex.count("\\left(") - latex.count("\\right(")
        n_closing_parenthesis = latex.count(")") - latex.count("\\left)") - latex.count("\\right)")
        if n_opening_parenthesis != n_closing_parenthesis:
            Logger.warn(f"{n_opening_parenthesis} opening parenthesis and {n_closing_parenthesis} closing parenthesis.", file_path)
        
        if latex.count(r"\later") > 0:
            Logger.warn("A note for later was left.", file_path)
        
        if latex.count(r"\unexpanded") > 0:
            Logger.warn("An unexpanded was kept.", file_path)

        if latex.count("bmatrix") > 0:
            Logger.warn("A bmatrix was left.", file_path)

        if latex.count("eq:label") > 0:
            Logger.warn("A default label eq:label was left.", file_path)
            
        if latex.count("Fourrier") > 0:
            Logger.warn("'Fourrier' instead of 'Fourier'.", file_path)
            
        if latex.lower().count("rotationel") > 0:
            Logger.warn("'rotationel' instead of 'rotationnel'.", file_path)

        for command in ["hat", "bvec", "bhat", "widetilde"]:
            if Parser.any_cmd_content_contains(latex, command, "_"):
                Logger.warn(f"{command.capitalize()} containing underscore.", file_path)
        
        if lecture_info is not None:
            if lecture_info.title.strip() == "":
                Logger.warn("Empty title in lecture command.", file_path)
            
            if lecture_info.summary.strip() == "":
                Logger.warn("Empty summary in lecture command.", file_path)
            
            if lecture_info.summary.count(r"\begin{enumerate}") > 0:
                Logger.warn("Enumerate in summary, should use itemize.", file_path)
            
            if lecture_info.summary.count(r"\begin{itemize}[left=0pt]") == 0:
                Logger.warn("Should use itemize with left=0pt.", file_path)

        return self
