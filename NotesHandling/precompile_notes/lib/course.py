from pathlib import Path
from typing import List

from lib.file_loader import FileLoader

# Those are hardcoded, for easier modularity
BACHELOR_SEMESTERS_EN = [
    r"Computer science bachelor --- Semester 1 \\ Autumn 2021",
    r"Computer science bachelor --- Semester 2 \\ Spring 2022",
    r"Computer science bachelor --- Semester 3 \\ Autumn 2022",
    r"Computer science bachelor --- Semester 4 \\ Spring 2023",
    r"Computer science bachelor --- Semester 5 \\ Autumn 2023",
    r"Computer science bachelor --- Semester 6 \\ Spring 2024",
]

BACHELOR_SEMESTERS_FR = [
    r"Bachelor d'informatique --- Semestre 1 \\ Automne 2021",
    r"Bachelor d'informatique --- Semestre 2 \\ Printemps 2022",
    r"Bachelor d'informatique --- Semestre 3 \\ Automne 2022",
    r"Bachelor d'informatique --- Semestre 4 \\ Printemps 2023",
    r"Bachelor d'informatique --- Semestre 5 \\ Automne 2023",
    r"Bachelor d'informatique --- Semestre 6 \\ Printemps 2024",
]

MASTER_SEMESTERS_EN: List[str] = []
MASTER_SEMESTERS_FR: List[str] = []


class Course:
    def __init__(self, *, is_bachelor: bool, semester: int, name: str, is_summary: bool = False):
        self.is_bachelor = is_bachelor
        self.semester = semester
        self.name = name
        self.is_summary = is_summary

    def __repr__(self) -> str:
        return f"Course({self.name}, {self.is_bachelor}, {self.semester}, {self.is_summary})"

    @property
    def root_path(self) -> Path:
        diploma = "BA" if self.is_bachelor else "MA"
        return Path(f"{diploma}{self.semester}/NotesCours/{self.name}") 
    
    @property
    def loader(self) -> FileLoader:
        return FileLoader(self.root_path)
    
    def date(self, english: bool) -> str:
        if self.is_bachelor:
            if english:
                names = BACHELOR_SEMESTERS_EN
            else:
                names = BACHELOR_SEMESTERS_FR
        else:
            if english:
                names = MASTER_SEMESTERS_EN
            else:
                names = MASTER_SEMESTERS_FR

        semester = self.semester - 1
        return names[semester]
