from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict
from typing_extensions import override
from lib.course import Course
from lib.file_loader import FileLoader
from lib.lecture import Lecture
from lib.lecture_loader import LectureLoader
from lib.precompiled_files import AbstractPrecompiledFiles
from lib.precompilers.generic_precompiler import GenericPrecompiler
from lib.style import Style

class PrecompiledSummary(AbstractPrecompiledFiles):
    def __init__(self, course: Course, precompiled_latex: str, original_lecture: Lecture):
        #TODO: rename Lecture
        self.course = course
        self.precompiled_latex = precompiled_latex
        self.original_lecture = original_lecture
    
    @staticmethod
    def from_course(course: Course, tag: str|None) -> "PrecompiledSummary":
        loader = LectureLoader(course.root_path)
        lecture = loader.to_lecture()
        is_english = course.loader.config().english

        config = course.loader.config()
        latex = GenericPrecompiler.full_precompile(lecture.latex, is_english, None, lecture.latex_path)

        # Apply template
        template = FileLoader.summary_template()
        now = datetime.now()  #TODO: repeated code with precompiled_lecture_group.py
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        replacement: Dict[str, str] = {
            'precompilation_date': current_date,
            'precompilation_time': current_time,
            'title': config.title,
            'detailed summary': "Detailed summary" if config.english else "Résumé détaillé",
            'course by': "Course by" if config.english else "Cours par",
            'professor': config.professor,
            'potential comment': r"\\ " + config.comment if config.comment is not None else "",
            'date': course.date(is_english).short_name,
            'tag': f"--{tag}" if tag is not None else "",
            'content': latex,
        }
        latex = FileLoader.replace_in_template(template, replacement)

        return PrecompiledSummary(course, latex, lecture)
        
    @override
    def write(self, tag: str|None, root_path: Path):
        print("WARNING: tag is not used yet")

        style = Style.from_course(self.course)
        style.write(root_path)

        with open(root_path/"main.tex", "w+", encoding="utf-8") as file:
            file.write(self.precompiled_latex)
        for asset_path in self.original_lecture.assets_path:
            shutil.copy(asset_path, root_path/asset_path.name)
    