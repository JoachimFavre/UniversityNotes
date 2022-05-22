# -*- coding: utf-8 -*-
"""
Opens the notes corresponding to the given page.

Created on Mon Jan  3 17:36:31 2022
@author: Joachim Favre
"""
import os
import re
import fitz  # pip install PyMuPDF

COMPILED_DIR = "_CompiledNotes"
# COURSE = "Analyse-2"
COURSE = "AICC-2"
PDF = ".pdf"

LECTURE_PATH = r"{}\Lecture{:02d}\lecture{}.tex"
LECTURE_TOC_REGEX = r"(?:Lecture|Cours) (\d+) .* \d{4}\D*(\d+)\n"

BEGIN_EXTRACTION = ["Liste des cours", "List of lectures"]
END_EXTRACTION = ["Chapitre 1\nRésumé par cours",
                  "Chapter 1\nSummary by lecture"]

PROMPT = "\n> "


def uin(text):
    return input(text + PROMPT)


def extract_lectures_begin_page(course):
    began_extraction = False
    result = []
    with fitz.open(COMPILED_DIR + "/" + course + PDF) as pdf_file:
        for page in pdf_file:
            content = page.get_text()

            # Verify extraction status
            for title in BEGIN_EXTRACTION:
                if content.find(title) != -1:
                    began_extraction = True
                    last_lecture = 0
            for title in END_EXTRACTION:
                if content.find(title) != -1:
                    return result

            # Extract if must
            if began_extraction:
                lectures = re.findall(LECTURE_TOC_REGEX, content)

                for lecture in lectures:
                    lecture_number = int(lecture[0])
                    lecture_page = int(lecture[1])
                    if lecture_number != last_lecture + 1:
                        print("Missing lecture " + str(last_lecture + 1))
                        return None
                    last_lecture = lecture_number
                    result.append(lecture_page)


def get_lecture_path(course, lecture):
    return LECTURE_PATH.format(course, lecture, lecture)


def get_page_content(course, page):
    with fitz.open(course + PDF) as pdf_file:
        page_content = pdf_file.get_page_text(page-1)
    return page_content


def locate_lecture(page, lectures_begin_page):
    if page < lectures_begin_page[0]:
        return [0]
    if page > lectures_begin_page[-1]:
        return [len(lectures_begin_page)]
    if page in lectures_begin_page:
        hesitation = lectures_begin_page.index(page) + 1
        return [hesitation-1, hesitation]

    for lecture_index in range(len(lectures_begin_page) - 1):
        if (lectures_begin_page[lecture_index] <= page
                <= lectures_begin_page[lecture_index + 1]):
            return [lecture_index + 1]
    return [-1]


def extract_lines(text, to_find):
    result = []
    for line in text.split("\n"):
        if line.count(to_find) > 0:
            result.append(line)
    return result


def modify_lecture(course, lecture, to_replace, to_replace_with):
    path = get_lecture_path(course, lecture)

    with open(path, 'r', encoding='utf8') as file:
        file_content = file.read()

    if file_content.count(to_replace) == 0:
        print("No occurence in file.")
        return False

    must_break = False
    lines = extract_lines(file_content, to_replace)
    for line_to_replace in lines:
        splitted_line_to_replace = line_to_replace.split(to_replace)
        chunks = [splitted_line_to_replace[i] + to_replace
                  + splitted_line_to_replace[i+1]
                  for i in range(len(splitted_line_to_replace) - 1)]
        for chunk_to_replace in chunks:
            assert chunk_to_replace.count(to_replace) == 1
            assert file_content.count(chunk_to_replace) == 1
            chunk_to_replace_with = chunk_to_replace.replace(to_replace,
                                                             to_replace_with)
            text = "\nReplacing:\n->{}\n->{}"
            print(text.format(chunk_to_replace, chunk_to_replace_with), end='')
            answer = uin('y/n')
            if answer == 'y':
                file_content = file_content.replace(chunk_to_replace,
                                                    chunk_to_replace_with)
                must_break = True
                break
        if must_break:
            break

    try:
        with open(path, 'w', encoding='utf8') as file:
            file.write(file_content)
    except Exception:
        # This should not happen, but we don't want to end up with
        # an empty file
        print(file_content)


def modify_lectures(course, lectures, to_replace, to_replace_with):
    for lecture in lectures:
        if modify_lecture(course, lecture, to_replace, to_replace_with):
            return


def open_lecture(course, lecture):
    print("Opening lecture " + str(lecture) + "...")
    path = get_lecture_path(course, lecture)
    os.startfile(path)


print("Extracting lecture pages from table of contents...")
lectures_begin_page = extract_lectures_begin_page(COURSE)

if lectures_begin_page is not None:
    while True:
        page = int(uin("Give a page to open."))
        lecture_number = locate_lecture(page, lectures_begin_page)

        if (len(lecture_number) == 0
                or (len(lecture_number) == 1 and lecture_number[0] <= 0)):
            print("This page could not be found in the courses.")
        else:
            if len(lecture_number) != 1:
                hesitation = ", ".join([str(i) for i in lecture_number])
                print("Hesitating between: " + hesitation)
                text = "to choose which lecture to open."
            else:
                print("Located at lecture " + str(lecture_number[0]))
                text = "to open this lecture."

            text_to_find = uin("Give the text that you want to modify, "
                               "or write OPEN " + text)
            if text_to_find == "OPEN":
                if len(lecture_number) == 1:
                    open_lecture(COURSE, lecture_number[0])
                else:
                    lecture_to_open = uin("Give the lecture you want to open.")
                    open_lecture(COURSE, int(lecture_to_open))
            else:
                to_replace_with = uin("Give the text you want to use for "
                                      "the replacemment.")
                modify_lectures(COURSE, lecture_number, text_to_find,
                                to_replace_with)
