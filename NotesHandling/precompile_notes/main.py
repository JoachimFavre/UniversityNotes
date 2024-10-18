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
from pathlib import Path
import time
from typing import List

from lib.tags import Tags
from lib.course import Course
from lib.logger import Logger
from lib.precompiled_files import PrecompiledLectureGroup


courses: List[Course] = [
    # BA1
    #Course(is_bachelor=True, semester=1, name="Analyse-1"),
    #Course(is_bachelor=True, semester=1, name="AlgebreLinaire"),
    #Course(is_bachelor=True, semester=1, name="AICC-1"),

    # BA2
    #Course(is_bachelor=True, semester=2, name="AICC-2"),
    #Course(is_bachelor=True, semester=2, name="Analyse-2"),
    #Course(is_bachelor=True, semester=2, name="Analyse-2-MethodesDeDemonstration"),
    #Course(is_bachelor=True, semester=2, name="DigitalSystemDesign"),
    
    # BA3
    #Course(is_bachelor=True, semester=3, name="Algorithms"),
    #Course(is_bachelor=True, semester=3, name="Analyse-3"),
    #Course(is_bachelor=True, semester=3, name="ComputerNetworks"),
    #Course(is_bachelor=True, semester=3, name="IntroToMachineLearning-BA3-Summary", is_summary=True),
    #Course(is_bachelor=True, semester=3, name="NumericalMethods"),
    
    # BA4
    #Course(is_bachelor=True, semester=4, name="Analyse-4"),
    #Course(is_bachelor=True, semester=4, name="ProbabilityAndStatistics"),
    #Course(is_bachelor=True, semester=4, name="SignalsAndSystems"),
    #Course(is_bachelor=True, semester=4, name="TheoryOfComputation"),
    
    # BA5
    #Course(is_bachelor=True, semester=5, name="Algebra"),
    #Course(is_bachelor=True, semester=5, name="IntroToQuantumInformationProcessing-Summary", is_summary=True),
    
    # BA6
    #Course(is_bachelor=True, semester=6, name="IntroToQuantumComputation-Summary", is_summary=True),
    
    # MA1
    #Course(is_bachelor=False, semester=1, name="Algorithms-2"),
]

tag = Tags.NONE

beginning_time = time.time()

for course in courses:
    Logger.info("#"*10 + f" Handling {course.name}... " + "#"*10)
    lecture_group = PrecompiledLectureGroup.from_course(course)
    lecture_group.make_code_zip_and_compile(tag.tag, Path("NotesHandling/precompile_notes")/tag.output_dir)
    #lecture_group.make_code_zip(tag.tag, Path("NotesHandling/precompile_notes")/tag.output_dir)

    Logger.newline()

Logger.info(f"Done in {int(time.time() - beginning_time)} seconds!\a")
