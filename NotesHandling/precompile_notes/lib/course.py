from pathlib import Path

from lib.date import BilingualDate, Date
from lib.file_loader import FileLoader

# Those are hardcoded, for easier modularity
BACHELOR = ("Computer science bachelor", "Bachelor d'informatique")
MASTER = ("Quantum science and engineering master", "Master de science et ingénierie quantiques")
AUTUMN = ("Autumn", "Automne")
SPRING = ("Spring", "Printemps")

BACHELOR_SEMESTERS = [
    BilingualDate(BACHELOR, 1, AUTUMN, 2021),
    BilingualDate(BACHELOR, 2, SPRING, 2022),
    BilingualDate(BACHELOR, 3, AUTUMN, 2022),
    BilingualDate(BACHELOR, 4, SPRING, 2023),
    BilingualDate(BACHELOR, 5, AUTUMN, 2023),
    BilingualDate(BACHELOR, 6, SPRING, 2024),
]

MASTER_SEMESTERS = [
    BilingualDate(MASTER, 1, AUTUMN, 2024),
    BilingualDate(MASTER, 2, SPRING, 2025),
    BilingualDate(MASTER, 3, AUTUMN, 2025),
]

class Course:
    def __init__(self, *, is_bachelor: bool, semester: int, name: str, is_summary: bool = False):
        self.is_bachelor = is_bachelor
        self.semester = semester
        self.name = name
        self.is_summary = is_summary

    @property
    def semester_name(self) -> str:
        diploma = "BA" if self.is_bachelor else "MA"
        return f"{diploma}{self.semester}"

    def __repr__(self) -> str:
        return f"Course({self.name}, {self.semester_name}, is_summary={self.is_summary})"

    @property
    def root_path(self) -> Path:
        return Path(f"{self.semester_name}/NotesCours/{self.name}") 
    
    @property
    def loader(self) -> FileLoader:
        return FileLoader(self.root_path)
    
    def date(self, english: bool) -> Date:
        if self.is_bachelor:
            dates = BACHELOR_SEMESTERS
        else:
            dates = MASTER_SEMESTERS

        semester = self.semester - 1
        if semester >= len(dates):
            raise Exception(f"Semester date is not defined for {self}.")
        return dates[semester].date(english)
