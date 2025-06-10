# -*- coding: utf-8 -*-
r"""
Notes compiler.

Takes a directory containing LaTeX notes split by lectures, and compiles them
to a single document.

Relations need to have their extension (such as \importslide{thing.pdf},
the .pdf is required.)

Do not name any file "[CourseName].pdf" or "[CourseName]_questions.txt" in the
result directory, or else it may get deleted or replaced.

Things to verify before printing a document:
    - Titles in headers must not overlap
    - Summaries are done using itemize with left=0pt
    - Verify lessons dates day
    - The Frontmatter was written

Created on Wed Jul 10 23:34:40 2024
@author: Joachim Favre
"""
import os
from pathlib import Path
import time
from typing import List

from lib.precompiled_files.precompiled_summary import PrecompiledSummary
from lib.tags import Tags
from lib.course import Course
from lib.course_list import CourseList
from lib.logger import Logger
from lib.precompiled_files import PrecompiledLectureGroup


courses: List[Course] = [
    # BA1
    #CourseList.ANALYSE_1,
    #CourseList.ALGEBRE_LINEAIRE,
    #CourseList.AICC_1,

    # BA2
    #CourseList.AICC_2,
    #CourseList.ANALYSE_2,
    #CourseList.ANALYSE_2_METHODES_DE_DEMONSTRATION,
    #CourseList.DIGITAL_SYSTEM_DESIGN,
    
    # BA3
    #CourseList.ALGORITHMS,
    #CourseList.ANALYSE_3,
    #CourseList.COMPUTER_NETWORKS,
    #CourseList.INTRO_TO_MACHINE_LEARNING_BA3,
    #CourseList.NUMERICAL_METHODS,
    
    # BA4
    #CourseList.ANALYSE_4,
    #CourseList.PROBABILITY_AND_STATISTICS,
    #CourseList.SIGNALS_AND_SYSTEMS,
    #CourseList.THEORY_OF_COMPUTATION,
    
    # BA5
    #CourseList.ALGEBRA,
    #CourseList.INTRO_TO_QUANTUM_INFORMATION_PROCESSING,
    
    # BA6
    #CourseList.INTRO_TO_QUANTUM_COMPUTATION,
    
    # MA1
    #CourseList.ALGORITHMS_2,
    #CourseList.COMPUTATIONAL_COMPLEXITY,
    #CourseList.QUANTUM_PHYSICS_2,
    
    # MA2
    #CourseList.SUBLINEAR_ALGORITHMS,
    CourseList.QUANTUM_INFORMATION_THEORY,
]

tag = Tags.NONE

# Set the correct active path
module_path = Path(__file__).resolve().parent
correct_active_path = module_path.parent.parent
os.chdir(correct_active_path)

# Compile each course
beginning_time = time.time()

for course in courses:
    Logger.info("#"*10 + f" Handling {course.name}... " + "#"*10)
    if course.is_summary:
        precompiled_files = PrecompiledSummary.from_course(course, tag.tag)
    else:
        precompiled_files = PrecompiledLectureGroup.from_course(course)
    precompiled_files.make_code_zip_and_compile(tag.tag, Path("NotesHandling/precompile_notes")/tag.output_dir)
    #precompiled_files.make_code_zip(tag.tag, Path("NotesHandling/precompile_notes")/tag.output_dir)

    Logger.newline()

Logger.info(f"Done in {int(time.time() - beginning_time)} seconds!\a")

