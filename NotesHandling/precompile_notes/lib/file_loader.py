import json
from pathlib import Path
from typing import Dict, List

from lib.loaded_files.course_config import CourseConfig
from lib.logger import Logger

CONFIG_PATH = Path("config.json")

TEMPLATES_PATH = Path("NotesHandling/precompile_notes/templates")
MAIN_TEMPLATE_PATH = TEMPLATES_PATH / "main_template.tex"
LECTURE_TEMPLATE_PATH = TEMPLATES_PATH / "lecture_template.tex"
SUMMARY_TEMPLATE_PATH = TEMPLATES_PATH / "summary_template.tex"
SUMMARY_BY_LECTURE_TEMPLATE_PATH = TEMPLATES_PATH / "summary_by_lecture_template.tex"
FOREWORD_EN_PATH = TEMPLATES_PATH / "foreword_en.tex"
FOREWORD_FR_PATH = TEMPLATES_PATH / "foreword_fr.tex"
HOMMAGE_EN_PATH = TEMPLATES_PATH / "hommage_en.tex"
HOMMAGE_FR_PATH = TEMPLATES_PATH / "hommage_fr.tex"


class FileLoader:
    def __init__(self, root_path: Path):
        self.root_path = root_path
    
    def lecture_paths(self) -> List[Path]:
        result: List[Path] = []
        for path in self.root_path.glob("*/"):
            if not path.is_dir():
                continue
            n_tex_files = len(list(path.glob("*.tex")))
            if n_tex_files == 0:
                Logger.warn(f"Path ignored because no tex file found.", path)
            elif n_tex_files > 1:
                raise Exception(f"Multiple tex files found in the same lecture, path {path}.")
            else:
                result.append(path)
        return result
    
    def config(self) -> CourseConfig:
        with open(self.root_path/CONFIG_PATH, "r", encoding="utf-8") as file:
            result = json.load(file)
        return CourseConfig(result)
    
    def style_path(self) -> Path:
        return self.root_path.parent / "style.sty"
    
    def style(self) -> str:
        # TODO: This is bad as well, since we always want to modify the style before using it
        return self._load_template(self.style_path())
    
    @staticmethod
    def _load_template(template_path: Path) -> str:
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
            
    @staticmethod
    def main_template() -> str:
        return FileLoader._load_template(MAIN_TEMPLATE_PATH)
    
    @staticmethod
    def lecture_template() -> str:
        return FileLoader._load_template(LECTURE_TEMPLATE_PATH)
    
    @staticmethod
    def summary_template() -> str:
        return FileLoader._load_template(SUMMARY_TEMPLATE_PATH)
    
    @staticmethod
    def summary_by_lecture_template() -> str:
        return FileLoader._load_template(SUMMARY_BY_LECTURE_TEMPLATE_PATH)
    
    @staticmethod
    def foreword(english: bool) -> str:
        path = FOREWORD_EN_PATH if english else FOREWORD_FR_PATH
        return FileLoader._load_template(path)
    
    @staticmethod
    def hommage(english: bool) -> str:
        path = HOMMAGE_EN_PATH if english else HOMMAGE_FR_PATH
        return FileLoader._load_template(path)


    # TODO: I don't think this really fits in here. Maybe a class "file_loader" is a bad idea
    @staticmethod
    def replace_in_template(template: str, replacements: Dict[str, str]) -> str:
        result = template
        for key, value in replacements.items():
            key = "{" + key + "}"
            if result.count(key) == 0:
                raise Exception(f"Key {key} not found in template.")
            result = result.replace(key, value)
        return result
