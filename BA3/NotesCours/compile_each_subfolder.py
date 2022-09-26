# -*- coding: utf-8 -*-
"""
Compiles each subfolder separately.

Created on Sat Jan  8 00:11:06 2022
@author: Joachim Favre
"""
import time
import os
import subprocess

COURSES_NAME = ["AICC-2", "Analyse-2", "Analyse-2-MethodesDeDemonstration", "DigitalSystemDesign"]


def compile_tex(dir_path, file_path):
    # latexmk compiles multiple times and all, so that's great
    compile_cmd = ("latexmk \"" + file_path + "\" " +
                   "-output-directory=\"" + dir_path
                   + "\" -pdf -halt-on-error -shell-escape -lualatex")
    completed_process = subprocess.run(compile_cmd)
    return completed_process.returncode


def compile_each(course_name):
    dirs = [lecture for lecture in os.listdir(course_name)
            if os.path.isdir(course_name + "\\" + lecture)]

    for index, lecture in enumerate(dirs):
        message = ("[{}] Lecture " + "{}/{}: ".format(index+1, len(dirs))
                   + lecture)
        print(message.format("COMPILING"), end='')

        lecture_path = course_name + "\\" + lecture
        for file in os.listdir(lecture_path):
            file_path = lecture_path + "\\" + file
            if not os.path.isfile(file_path) or file.split(".")[-1] != "tex":
                continue
            succeeded = compile_tex(lecture_path, file_path)

        if succeeded == 0:
            print("\r" + message.format("SUCCEEDED") + " "*10)
        else:
            print("\r" + message.format("FAILED") + " "*10)


def compile_each_multiple_courses(courses):
    beginning_time = time.time()
    for course in courses:
        n = 10
        print("-"*n + " Compiling " + course + " " + "-"*n)
        compile_each(course)
        print()
    print("Took {} seconds!\a".format(int(time.time() - beginning_time)))


compile_each_multiple_courses(COURSES_NAME)
