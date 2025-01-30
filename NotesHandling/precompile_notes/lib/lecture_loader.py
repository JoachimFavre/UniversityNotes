from pathlib import Path
from typing import List

from lib.lecture import Lecture

FILE_EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "code", "svg"]

class LectureLoader:
    def __init__(self, path: Path):
        self.path = path

    def latex_files_paths(self) -> List[Path]:
        return list(self.path.glob("*.tex"))

    def asset_files_paths(self) -> List[Path]:
        result = []
        for ext in FILE_EXTENSIONS:
            result.extend(list(self.path.glob(f"*.{ext}")))

        pdfs_to_remove = [tex_file.with_suffix(".pdf") for tex_file in self.latex_files_paths()]
        for elem in pdfs_to_remove:
            if elem in result:
                result.remove(elem)
        
        return result

    def to_lecture(self) -> Lecture:
        latex_files_paths = self.latex_files_paths()
        if len(latex_files_paths) != 1:
            raise Exception(f"Multiple tex files found in the same lecture, path {self.path}: {latex_files_paths}")
        
        with open(latex_files_paths[0], 'r', encoding='utf-8') as file:
            latex = file.read()

        return Lecture(self.path, latex, latex_files_paths[0], self.asset_files_paths())
