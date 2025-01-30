from typing import Tuple

class Date:
    def __init__(self, english: bool, diploma: str, semester: int, season: str, year: int):
        self.diploma = diploma
        self.semester = semester
        self.season = season
        self.year = year

        self.semester_word = "Semester" if english else "Semestre"
    
    @property
    def full_name(self):
        # Ex: Computer science bachelor --- Semester 1 \\ Autumn 2021
        return fr"{self.diploma} --- {self.semester_word.capitalize()} {self.semester} \\ {self.season} {self.year}"

    @property
    def short_name(self):
        # Ex: Autumn semester 2021
        return f"{self.season} {self.semester_word.lower()} {self.year}"

class BilingualDate:
    def __init__(self, diploma: Tuple[str, str], semester: int, season: Tuple[str, str], year: int):
        self.diploma = diploma
        self.semester = semester
        self.season = season
        self.year = year

    def date(self, english: bool) -> Date:
        i = 0 if english else 1
        return Date(english, self.diploma[i], self.semester, self.season[i], self.year)
    