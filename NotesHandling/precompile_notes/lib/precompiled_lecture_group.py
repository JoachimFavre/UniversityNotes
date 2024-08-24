from datetime import datetime
from pathlib import Path
from typing import Dict, List
from typing_extensions import override

from lib.abstract_precompiled_files import AbstractPrecompiledFiles
from lib.course import Course
from lib.lecture_loader import LectureLoader
from lib.precompiled_lecture import PrecompiledLecture
from lib.style import Style

class PrecompiledLectureGroup(AbstractPrecompiledFiles):
    def __init__(self, course: Course, lectures: List[PrecompiledLecture]):
        super().__init__(course)
        self.lectures = sorted(lectures)

        n_lectures_without_info = len([lecture for lecture in self.lectures if lecture.lecture_info is None])
        for reordering in course.loader.config().reorderings:
            a, b = reordering
            # Lecture i is at index i-1 of the part of the list that contain information.
            a = a - 1 + n_lectures_without_info
            b = b - 1 + n_lectures_without_info
            self.lectures[a], self.lectures[b] = self.lectures[b], self.lectures[a]
    
    @staticmethod
    def from_course(course: Course) -> "PrecompiledLectureGroup":
        result: List[PrecompiledLecture] = []
        is_english = course.loader.config().english
        for path in course.loader.lecture_paths():
            loader = LectureLoader(path)
            lecture = loader.to_lecture()
            precompiled = PrecompiledLecture.from_lecture(lecture, is_english)
            result.append(precompiled)
        return PrecompiledLectureGroup(course, result)

    def _summary_by_lecture_content(self) -> str:
        loader = self.course.loader
        template = loader.summary_by_lecture_template()
        result = []
        for lecture in self.lectures:
            if lecture.lecture_info is None:
                continue
            current = loader.replace_in_template(template, {
                'number': str(lecture.lecture_info.number),
                'date': lecture.lecture_info.date,
                'title': lecture.lecture_info.title,
                'summary': lecture.lecture_info.summary,
            })
            result.append(current)
        return '\n\n'.join(result)
    
    def _content(self) -> str:
        result = []
        for lecture in self.lectures:
            # TODO: Extract this and the other occurence to a function
            full_path = lecture.original_lecture.latex_path
            relative_path = full_path.relative_to(full_path.parent.parent)
            name = str(relative_path).replace("\\", "/")
            result.append(f"\\input{{{name}}}")
        return '\n'.join(result)

    def _make_main_tex(self, tag: str|None) -> str:
        loader = self.course.loader
        config = loader.config()
        english = config.english

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        replacements: Dict[str, str] = {
            'precompilation_date': current_date,
            'precompilation_time': current_time,
            'page_style_no_title': r"\fancyhf{}\fancyfoot[LE,RO]{\thepage}",
            'title_alias': config.title_alias,
            'by': 'by' if english else 'par',
            'title': config.title,
            'professor': config.professor,
            'date': self.course.date(english),
            'foreword': loader.foreword(english),
            'tag': f"--{tag}" if tag is not None else "",
            'hommage': loader.hommage(english),
            'summary_by_lecture_title': 'Summary by lecture' if english else 'Résumé par cours',
            'summary_by_lecture_content': self._summary_by_lecture_content(),
            'content': self._content(),
        }
        return loader.replace_in_template(self.course.loader.main_template(), replacements)
    
    @override
    def write(self, tag: str|None, root_path: Path):
        with open(root_path/"main.tex", "w+", encoding="utf-8") as file:
            file.write(self._make_main_tex(tag))
        
        style = Style.from_course(self.course)
        style.write(root_path)

        for lecture in self.lectures:
            lecture.write(root_path)
