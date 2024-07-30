from pathlib import Path
from typing import List

# TODO: Merge with lecture_loader
class Lecture:
    def __init__(self, path: Path, original_latex: str, latex_path: Path, assets_path: List[Path]):
        self.path = path
        self.latex = original_latex
        self.latex_path = latex_path
        self.assets_path = assets_path

    def __repr__(self) -> str:
        return f"Lecture({self.path})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Lecture)\
            and self.path == other.path\
            and self.latex == other.latex\
            and self.latex_path == other.latex_path\
            and self.assets_path == other.assets_path
