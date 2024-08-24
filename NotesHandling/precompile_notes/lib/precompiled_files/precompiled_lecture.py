from functools import total_ordering
from pathlib import Path
import shutil

from lib.lecture import Lecture
from lib.lecture_info import LectureInfo
from lib.precompiler import Precompiler

@total_ordering
class PrecompiledLecture:
    def __init__(self, precompiled_latex: str, lecture_info: LectureInfo|None, original_lecture: Lecture):
        self.precompiled_latex = precompiled_latex
        self.lecture_info = lecture_info
        self.original_lecture = original_lecture
    
    @staticmethod
    def from_lecture(lecture: Lecture, is_english: bool) -> "PrecompiledLecture":
        lecture_info = LectureInfo.load_from_latex(lecture.latex)
        latex = Precompiler(lecture.latex).full_precompile(is_english, lecture_info, lecture.path, lecture.assets_path).latex
        return PrecompiledLecture(latex, lecture_info, lecture)
    
    def write(self, root_path: Path):
        lecture_dir = self.original_lecture.latex_path.parents[0].name  # a/b/c/d.txt becomes c
        lecture_path = root_path/lecture_dir
        lecture_path.mkdir(exist_ok=True)
        with open(lecture_path/self.original_lecture.latex_path.name, "w+", encoding="utf-8") as file:
            file.write(self.precompiled_latex)
        for asset_path in self.original_lecture.assets_path:
            shutil.copy(asset_path, lecture_path/asset_path.name)
    
    def __lt__(self, other: "PrecompiledLecture") -> bool:
        """
        Sorts the lectures by their number if they have a lecture info. Lectures that do not are always
        placed first of the list, and are sorted by their directory name. This is mainly for frontmatters.
        """
        if self.lecture_info is None and other.lecture_info is None:
            return self.original_lecture.path < other.original_lecture.path
        if self.lecture_info is None:
            return True
        if other.lecture_info is None:
            return False
        return self.lecture_info.number < other.lecture_info.number
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, PrecompiledLecture)\
            and self.original_lecture.path == other.original_lecture.path\
            and self.lecture_info == other.lecture_info\
            and self.original_lecture == other.original_lecture

    def __repr__(self) -> str:
        return f"PrecompiledLecture({self.lecture_info}, {self.original_lecture})"
