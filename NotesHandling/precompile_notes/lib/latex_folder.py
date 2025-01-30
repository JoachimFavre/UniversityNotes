from pathlib import Path
from typing import List

FILE_EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "code", "svg"]

class LatexFolder:
    def __init__(self, path: Path, latex: str, latex_path: Path, assets_path: List[Path]):
        self.path = path
        self.latex = latex
        self.latex_path = latex_path
        self.assets_path = assets_path

    def __repr__(self) -> str:
        return f"Lecture({self.path})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LatexFolder)\
            and self.path == other.path\
            and self.latex == other.latex\
            and self.latex_path == other.latex_path\
            and self.assets_path == other.assets_path

    @staticmethod
    def from_path(path: Path):
        latex_files_paths = LatexFolder._latex_files_paths(path)
        if len(latex_files_paths) != 1:
            raise Exception(f"Multiple tex files found in the same lecture, path {path}: {latex_files_paths}")
        latex_path = latex_files_paths[0]
        
        with open(latex_path, 'r', encoding='utf-8') as file:
            latex = file.read()

        return LatexFolder(path, latex, latex_path, LatexFolder._asset_files_paths(path))

    @staticmethod
    def _latex_files_paths(path: Path) -> List[Path]:
        return list(path.glob("*.tex"))

    @staticmethod
    def _asset_files_paths(path: Path) -> List[Path]:
        result: List[Path] = []
        for ext in FILE_EXTENSIONS:
            result.extend(list(path.glob(f"*.{ext}")))

        pdfs_to_remove = [tex_file.with_suffix(".pdf") for tex_file in LatexFolder._latex_files_paths(path)]
        for elem in pdfs_to_remove:
            if elem in result:
                result.remove(elem)
        
        return result