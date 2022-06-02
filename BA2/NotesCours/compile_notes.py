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

Created on Sun Sep 26 13:43:40 2021
@author: Joachim Favre
"""
import time
import os
import subprocess
import tempfile

import re
import json
import shutil
import datetime

DATE = {"french": r"Bachelor d'informatique --- Semestre 2 \\ Printemps 2022",
        "english": r"Computer science bachelor --- Semester 2 \\ Spring 2022"}

# uses the "temp" folder in this diriectory if true, else uses a temporary
# directory that gets destroyed after having finished
USE_TEMP_FOLDER = False
PRINTED_VERSION = False

CONFIG_NAME = "config.json"
STYLE_DIR = "style.sty"
RESULT_DIR = "_CompiledNotes"
COURSES_NAME = ["AICC-2", "Analyse-2", "Analyse-2-MethodesDeDemonstration", "DigitalSystemDesign"]
# COURSES_NAME = ["Analyse-2"]
# COURSES_NAME = ["Analyse-2-MethodesDeDemonstration"]
# COURSES_NAME = ["DigitalSystemDesign"]

COPY_EXTENSIONS = ["tex", "pdf", "png", "jpg", "jpeg", 'code', 'svg']
FOREWORD_NAME = {'fr': 'foreword_fr.txt', 'en': 'foreword_en.txt'}
FRONTMATTER_NAME = "frontmatter.tex"


def get_version():
    # double dash, for LaTeX
    today = datetime.datetime.now()
    result = today.strftime("%Y--%m--%d")
    if PRINTED_VERSION:
        result += "--printed"
    return result


def copy_lectures(tmp_dir, course_name):
    tex_files = []
    relations = []

    for dir_index, lecture in enumerate(os.listdir(course_name)):
        relations.append([])
        lecture_path = course_name + "/" + lecture
        if lecture == "config.json":
            with open(lecture_path, 'r', encoding='utf8') as file:
                config = json.load(file)
        if not os.path.isdir(lecture_path):
            continue
        for file in os.listdir(lecture_path):
            file_path = course_name + "/" + lecture + "/" + file
            if (not os.path.isfile(file_path)
                    or file.split(".")[-1] not in COPY_EXTENSIONS):
                continue

            if file.split(".")[-1] == "tex":
                tex_files.append([dir_index, file])
                shutil.copy(file_path, tmp_dir + "/" + file)
            else:
                relations[dir_index].append(file)
                shutil.copy(file_path, tmp_dir + "/" + str(dir_index) + file)
    return tex_files, relations, config


def extract_lecture_command(content):

    # We don't want a page break before \\lecture when it is followed
    # by a chapter
    result = ""
    lecture_command = False
    in_summary = False
    summary = ""
    title = ""
    lecture_no = 0
    date = "1970-01-01"
    temp = ""
    for line in content.split("\n"):
        if in_summary:
            if line.strip() == "}":
                in_summary = False
            else:
                summary += line + "\n"
            temp += line + "\n"

        elif not lecture_command:
            if line.strip()[:len("\\lecture")] == "\\lecture":
                lecture_command = True
                temp += line + "\n"
                params = re.search(r"\\lecture{([0-9]*)}{(.*)}{(.*)}{?}?",
                                   line.replace("\\", r"\\"))
                lecture_no = params.group(1)
                date = params.group(2)
                title = params.group(3).replace(r"\\", "\\")
                if line.strip()[-1] == "{":
                    in_summary = True
            else:
                result += line + "\n"

        else:
            if line.strip() == "":
                temp += "\n"
            elif (line.strip()[:len("\\chapter")] == "\\chapter"
                  or line.strip()[:len("\\part")] == "\\part"):
                result += ("\\cleardoublepage\n"
                           + temp
                           + "\n"
                           + "\\let\\defaultclearpage\\clearpage\n"
                           + "\\let\\clearpage\\relax\n"
                           + line + "\n"
                           + "\\let\\clearpage\\defaultclearpage")

                temp = ""
                lecture_command = False
            else:
                result += temp + line + "\n"
                temp = ""
                lecture_command = False

    if (summary.count(r"\begin{itemize}[left=0pt]")
            < summary.count(r"\begin{itemize}")):
        print("\tSummary has left indent in lecture " + lecture_no)

    if temp != "":  # should never happen
        result += temp

    return result, [int(lecture_no), summary, date, title]


def replace_empty_slides_in_a_row_by_double_slides(content):
    # If two slide comment environments are after each other, we want
    # to replace them by a \\doubleslide
    n_empty_comment_env = 0  # in a row
    in_empty_comment_env = False
    result = ""
    temp = ""
    for line in content.split("\n"):
        if not in_empty_comment_env:
            if (line.strip()[:len("\\begin{slidecomment}")]
                    == "\\begin{slidecomment}"):
                in_empty_comment_env = True
                temp += line + "\n"
            elif line.strip() == "":
                if temp == "":
                    result += "\n"
                else:
                    temp += "\n"
            else:
                n_empty_comment_env = 0
                result += temp + line + "\n"
                temp = ""
        else:
            if line.strip() == "":
                temp += "\n"
            elif (line.strip()[:len("\\end{slidecomment}")]
                  == "\\end{slidecomment}"):
                temp += line + "\n"
                n_empty_comment_env += 1
                in_empty_comment_env = False
            else:
                n_empty_comment_env = 0
                result += temp + line + "\n"
                temp = ""
                in_empty_comment_env = False

            if n_empty_comment_env == 2:
                result += "\\doubleslide\n"
                temp = ""
                n_empty_comment_env = 0

    if temp != "":  # may happen
        result += temp

    return result


def turn_subparag_to_paragsubparag(content):
    # Split subparag in parag into paragsubparag, for page breaking.
    in_parag = False
    in_sub_parag = False
    result = ""
    temp = ""
    # is "" unless we are considering the first line in the parag command
    title_parag = ""
    title_sub_parag = ""
    for line in content.split("\n"):
        if in_sub_parag:
            if line.strip() == "":
                temp += line + "\n"
            elif line.strip()[0] == "}":
                in_sub_parag = False
                result += ("\n\\paragsubparag{" + title_parag + "}{"
                           + title_sub_parag + "}{\n"
                           + temp + "}\n\n")
                temp = ""
                title_parag = ""
                title_sub_parag = ""
            else:
                temp += line + "\n"
        elif in_parag:
            if line.strip() == "":
                temp += line + "\n"
            elif line.strip()[:len("\\subparag{")] == "\\subparag{":
                in_sub_parag = True
                re_match = re.search(r"\\subparag{(.*)}{$",
                                     line.strip())
                title_sub_parag = re_match.group(1)
                if temp.strip() != "":
                    result += ("\\parag{" + title_parag + "}{\n"
                               + temp + "}\n")
                    temp = ""
                    title_parag = ""
            elif line.strip()[0] == "}":
                in_parag = False
                if temp.strip() != "":
                    result += ("\\parag{" + title_parag + "}{\n"
                               + temp + "}\n")
                    temp = ""
                    title_parag = ""
            else:
                temp += line + "\n"
        else:
            if line.strip() == "":
                result += line + "\n"
            elif line.strip()[:len("\\parag{")] == "\\parag{":
                re_match = re.search(r"\\parag{(.*)}{$",
                                     line.strip())
                title_parag = re_match.group(1)
                in_parag = True
            else:
                result += line + "\n"

    if temp != "":  # should never happen
        result += temp

    return result


def add_space_before_char(text, char):
    result = text.replace(" " + char, char)
    result = re.sub("(?<!\\\\)\\" + char, "~" + char, result)
    result = result.replace("http~:", "http:")
    result = result.replace("https~:", "https:")
    return result


def remove_space_before_char(text, char):
    return text.replace(" " + char, char).replace("~" + char, char)


def correct_spaces(content, is_english):
    result = ""
    in_no_touch_env = 0
    no_touch_env = ["lstlisting"]
    for line in content.split("\n"):
        begin = re.search(r"\\begin\{(.*)\}", line)
        end = re.search(r"\\end\{(.*)\}", line)
        if begin is not None and begin.group(1) in no_touch_env:
            in_no_touch_env += 1
        elif end is not None and end.group(1) in no_touch_env:
            in_no_touch_env -= 1
        elif in_no_touch_env == 0:
            for char in [";", ":", "!", "?"]:
                if is_english:
                    line = remove_space_before_char(line, char)
                else:
                    line = add_space_before_char(line, char)
        result += line + "\n"

    return result


def verify_content(content, file_name):
    n_opening_parenthesis = (content.count("(") - content.count("\\left(")
                             - content.count("\\right("))
    n_closing_parenthesis = (content.count(")") - content.count("\\left)")
                             - content.count("\\right)"))
    if n_opening_parenthesis != n_closing_parenthesis:
        print("\tThe number of opening parenthesis is not the same one "
              "as the number of closing parenthesis in {}.".format(file_name))

    if content.count("\\later") > 0:
        print("\tA note for later was left in {}.".format(file_name))

    if content.count("bmatrix") > 0:
        print("\tA bmatrix was left in {}.".format(file_name))


def modify_tex_documents(tmp_dir, tex_files, relations, is_english):
    frontmatter_summary = None
    frontmatter_tex_file = None

    informations = []
    for relation_index, tex_file in tex_files:
        file_path = tmp_dir + "/" + tex_file
        with open(file_path, 'r', encoding='utf8') as latex_document:
            content = latex_document.read()

        content = content[content.find("\\begin{document}"):]
        content = content[len("\\begin{document}"):]
        content = content[:content.rfind("\\end{document}")]
        if content.count("\\part") - content.count("\\partial") > 0:
            print("\tWARNING: There are parts used, see if they were "
                  "really intended.")
        # content = content.replace("\\part", "\\chapter")
        content = content.replace("\\section", "\\chapter")
        content = content.replace("\\subsection", "\\section")
        content = content.replace("\\subsubsection", "\\subsection")
        content = content.replace("\\maketitle", "")
        # content = content.replace("\\label{", "\\label{" + str(relation_index))
        content = content.replace("\\label{", "\\phantomsection\\label{")
        # content = content.replace("\\ref{", "\\ref{" + str(relation_index))
        # content = content.replace("\\pageref{",
        #                           "\\pageref{" + str(relation_index))

        for relation in relations[relation_index]:
            # If do the following, it will also replace the name in sections
            # or so
            # content = content.replace("{" + relation[:relation.rfind(".")]
            #                           + "}", "{" + str(relation_index)
            #                           + relation + "}")
            content = content.replace("{" + relation + "}",
                                      "{" + str(relation_index)
                                      + relation + "}")

        content, summary = extract_lecture_command(content)
        if tex_file == FRONTMATTER_NAME:
            frontmatter_summary = summary
            frontmatter_tex_file = [relation_index, tex_file]
        else:
            informations.append([summary, relation_index, tex_file])

            if summary[3] == "":
                print("\tNo summary defined in {}.".format(tex_file))

        content = replace_empty_slides_in_a_row_by_double_slides(content)

        # There are multiple problems in the style. Subparagraphs are not
        # breaking well, the line on their left is not very well used
        # and, as a general manner, it's nice to have the whole proof on one
        # page
        content = turn_subparag_to_paragsubparag(content)

        # content = correct_spaces(content, is_english)

        verify_content(content, tex_file)

        with open(file_path, 'w', encoding='utf8') as latex_document:
            latex_document.write(content)

    # sorted by first element of summary: lecture number
    informations = sorted(informations)
    sorted_tex_files = []
    sorted_summaries = []
    for summary, relation_index, tex_file in informations:
        sorted_tex_files.append([relation_index, tex_file])
        sorted_summaries.append(summary)

    if frontmatter_summary is not None:
        sorted_tex_files.insert(0, frontmatter_tex_file)
        sorted_summaries.insert(0, frontmatter_summary)

    return sorted_tex_files, sorted_summaries


def copy_style(tmp_dir, config):
    new_dir = tmp_dir + "/style.sty"
    shutil.copy(STYLE_DIR, new_dir)
    with open(new_dir, 'r', encoding='utf8') as file:
        content = file.read()

    if not config["english"]:
        content = content.replace("\\usepackage[british]{babel}",
                                  "\\usepackage[french]{babel}")

    with open(new_dir, 'w', encoding='utf8') as file:
        file.write(content)


def create_main_tex(tmp_dir, tex_files, config, summaries):
    by = "by" if config["english"] else "par"
    date = DATE["english"] if config["english"] else DATE["french"]
    summary_lectures = ("Summary by lecture" if config["english"]
                        else "Résumé par cours")

    page_style_no_title = ("\\fancyhf{}\n"
                           + "\\fancyfoot[LE,RO]{\\thepage}\n")

    if config["english"]:
        foreword_key = 'en'
    else:
        foreword_key = 'fr'

    with open(FOREWORD_NAME[foreword_key], encoding='utf8') as foreword_file:
        foreword = foreword_file.read()
    # foreword = ""

    main_tex_content = ("\\documentclass[a4paper]{book}\n"
                        + "\n"
                        + "\\usepackage{style}\n"
                        + "\n"
                        + "\\pagestyle{fancy}\n"
                        + page_style_no_title
                        # If modify left or right mark, must also modify them
                        # in style in \\listoflectures
                        + "\\fancyhead[RE]{\\textit{\\leftmark}}\n"
                        + "\\fancyhead[LO]{\\textit{\\rightmark}}\n"
                        + "\\fancyhead[LE]{" + config["title-alias"] + "}\n"
                        + ("\\fancyhead[RO]{" + "Notes " + by
                           + " Joachim Favre}\n")
                        + "\\fancypagestyle{plain}{\n"
                        + page_style_no_title
                        + "}\n"
                        + "\n"
                        + ("\\title{" + config["title"] + r"\\ Prof. "
                           + config["professor"] + " --- EPFL}\n")
                        + "\\author{Notes " + by + " Joachim Favre}\n"
                        + "\\date{" + date + "}\n"
                        + "\n"
                        + "\\begin{document}\n"
                        + "\\maketitle\n"
                        + "\n"
                        + "\\clearemptydoublepage\n"
                        + "\\thispagestyle{empty}\n"
                        + "\n"
                        + "\\invinsiblelistofquestions"
                        + "\n"
                        + "\\vspace*{\\fill}\n"
                        + foreword
                        + "\\vspace*{\\fill}\n"
                        + "\\vspace*{\\fill}\n"
                        + "\\begin{center}\n"
                        + "\\textit{Version " + get_version() + "}\n"
                        + "\\end{center}\n"
                        # + "\\vspace*{\\fill}\n"
                        + "\n"
                        + "\\clearemptydoublepage\n"
                        + "\\tableofcontents\n"
                        + "\\cleardoublepage\n"
                        + "\n"
                        + ("\\renewcommand{\\cftchapleader}"
                           "{\\cftdotfill{\\cftdotsep}}\n")
                        + "\\renewcommand*{\\cftchapfont}{}\n"
                        + "\n"
                        + "\\listoflectures\n"
                        + "\n"
                        + "\\chapter{" + summary_lectures + "}\n")

    for lecture_no, summary, date, title in summaries:
        if lecture_no != 0:
            main_tex_content += ("\\lecturetitlesummary{" + str(lecture_no)
                                 + "}{" + date + "}{" + title + "}\n")
            main_tex_content += "\\vspace{0.5em\n}"
            main_tex_content += summary + "\n"
            main_tex_content += "\\vspace{2em}\n"
            # main_tex_content += "\\parag{Lecture " + str(lecture_no) + "}{\n"
            # main_tex_content += summary + "}\n"

    main_tex_content += "\\cleardoublepage"

    for _, tex_file in tex_files:
        main_tex_content += "\\input{" + tex_file + "}\n"

    main_tex_content += "\\clearemptydoublepage\n"
    main_tex_content += "\n\\end{document}"

    with open(tmp_dir + "/main.tex", 'w+', encoding='utf8') as main_tex_file:
        main_tex_file.write(main_tex_content)


def compile_tex(tmp_dir):
    beginning_dir = os.getcwd()
    os.chdir(tmp_dir)
    # latexmk compiles multiple times and all, so that's great
    compile_cmd = ("latexmk main.tex -shell-escape -pdf -halt-on-error")
    completed_process = subprocess.run(compile_cmd, shell=True)
    os.chdir(beginning_dir)
    return completed_process.returncode


def move_result(tmp_dir, course_name):
    shutil.copy(tmp_dir + "/main.pdf", course_name + ".pdf")


def move_questions_if_any(tmp_dir, course_name):
    questions = []
    with open(tmp_dir + "/main.questions", encoding='utf8') as question_file:
        for line in question_file.read().split("\n"):
            pattern = r"\\contentsline(?: )?\{.*\}\{(.*)\}\{.*\}\{.*\}"
            quest = re.search(pattern, line)
            if quest is not None:
                questions.append(quest.group(1))
    result_file_name = course_name + "_questions.txt"
    if len(questions) > 0:
        with open(result_file_name, 'w+', encoding='utf8') as result_file:
            result_file.write("Questions\n" + "-"*len("Questions") + "\n")
            for question in questions:
                result_file.write("- " + question + "\n")
        return True
    elif os.path.exists(result_file_name):
        os.remove(result_file_name)
        print("\tDeleted " + result_file_name + " since there is no more "
              "question.")
    return False


def _compile_course(course_name, tmp_dir):
    print("Copying the source code and the documents to the temporary "
          "directory.")
    tex_files, relations, config = copy_lectures(tmp_dir, course_name)

    print("Modifying the latex documents.")
    tex_files, summaries = modify_tex_documents(tmp_dir, tex_files, relations,
                                                config["english"])

    print("Copying the style to the temporary directroy.")
    copy_style(tmp_dir, config)

    print("Creating the main latex file.")
    create_main_tex(tmp_dir, tex_files, config, summaries)

    print("Compiling.")
    if compile_tex(tmp_dir) != 0:
        print("\tThere was a problem during the compilation.")
    else:
        print("Moving the result.")

        result_path = RESULT_DIR + "\\" + course_name
        move_result(tmp_dir, result_path)

        if move_questions_if_any(tmp_dir, result_path):
            print("\tThere are hanging questions.")

        print("Done, the result is " + result_path + ".pdf.")


def compile_course(course_name, use_temp_folder):
    if use_temp_folder:
        tmp_dir = r"temp"
        _compile_course(course_name, tmp_dir)
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            _compile_course(course_name, tmp_dir)


def compile_multiple_courses(courses_name, use_temp_folder):
    beginning_time = time.time()
    for course_name in courses_name:
        print("#"*10 + " Compiling notes from " + course_name + " " + "#"*10)
        compile_course(course_name, use_temp_folder)
        print("\n")
    print("Done in {} seconds!\a".format(int(time.time() - beginning_time)))


compile_multiple_courses(COURSES_NAME, USE_TEMP_FOLDER)
