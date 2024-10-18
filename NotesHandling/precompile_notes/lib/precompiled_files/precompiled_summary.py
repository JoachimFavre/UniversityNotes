from lib.course import Course
from lib.lecture import Lecture
from lib.lecture_loader import LectureLoader
from lib.precompiled_files import AbstractPrecompiledFiles

class PrecompiledSummary(AbstractPrecompiledFiles):
    def __init__(self, precompiled_latex: str, original_lecture: Lecture):
        #TODO: rename Lecture
        self.precompiled_latex = precompiled_latex
        self.original_lecture = original_lecture
    
    @staticmethod
    def from_course(course: Course) -> "PrecompiledSummary":
        result = []
        is_english = course.loader.config().english
        loader = LectureLoader(course.root_path)
        tex_paths = loader.latex_files_paths()
        if len(tex_paths) == 0:
            raise Exception("No latex file found.")
        elif len(tex_paths) > 1:
            raise Exception("Multiple latex files found.")
        tex_path = tex_paths[0]

        # TODO: I think I need to refactor what a Lecture is
        with open(tex_path, 'r', encoding='utf-8') as file:
            # TODO: Didn't I have a method to do so?
            latex = file.read()
        lecture = Lecture(course.root_path, latex, tex_path, loader.asset_files_paths())
        
        
    