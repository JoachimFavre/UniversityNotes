import re

from pathlib import Path
from typing import List

from lib.loaded_files.lecture_info import LectureInfo
from lib.logger import Logger
from lib.parser import Parser


class GenericPrecompiler:
    def __init__(self, latex: str):
        self.latex = latex
    
    @staticmethod
    def full_precompile(latex: str, is_english: bool, lecture_info: LectureInfo|None, latex_path: Path) -> str:
        return GenericPrecompiler(latex)\
            .remove_before_begin_document()\
            .remove_after_end_document()\
            .remove_make_title()\
            .correct_spaces(is_english)\
            .strip()\
            .make_warnings(lecture_info, latex_path)\
            .latex

    def remove_before_begin_document(self) -> "GenericPrecompiler":
        match = re.search(r"\\begin{document}", self.latex)
        if match is None:
            raise Exception(r"No \begin{document} found in the latex file.")
        return GenericPrecompiler(self.latex[match.end(0):])
    
    def remove_after_end_document(self) -> "GenericPrecompiler":
        match = re.search(r"\\end{document}", self.latex)
        if match is None:
            raise Exception(r"No \end{document} found in the latex file.")
        return GenericPrecompiler(self.latex[:match.start(0)])

    def remove_make_title(self) -> "GenericPrecompiler":
        return GenericPrecompiler(self.latex.replace(r"\maketitle", ""))

    def merge_consecutive_empty_slides(self) -> "GenericPrecompiler":
        if self.latex.count(r"\begin{slidecomment}") > 0:
            raise NotImplementedError("Merging consecutive empty slides is not implemented yet.")
        return self
    
    def correct_spaces(self, is_english: bool) -> "GenericPrecompiler":
        # We do not want to correct spaces in code environments.
        # We suppose that those \begin and \end are alone
        # on their line.
        result: List[str] = []
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
        return GenericPrecompiler('\n'.join(result))
    
    def strip(self) -> "GenericPrecompiler":
        return GenericPrecompiler(self.latex.strip())

    def make_warnings(self, lecture_info: LectureInfo|None, file_path: Path) -> "GenericPrecompiler":
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

        if latex.count("bmatrix") - latex.count("submatrix") > 0:
            Logger.warn("A bmatrix was left.", file_path)

        if latex.count("eq:label") > 0:
            Logger.warn("A default label eq:label was left.", file_path)
            
        if latex.count("Fourrier") > 0:
            Logger.warn("'Fourrier' instead of 'Fourier'.", file_path)

        if latex.count("Chernhoff") > 0:
            Logger.warn("'Chernhoff' instead of 'Chernoff'.", file_path)
            
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
