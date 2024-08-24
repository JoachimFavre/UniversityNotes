from abc import ABC, abstractmethod
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from lib.course import Course
from lib.logger import Logger


class AbstractPrecompiledFiles(ABC):
    def __init__(self, course: Course):
        self.course = course

    @abstractmethod
    def write(self, tag: str|None, root_path: Path):
        pass
    
    def _zip(self, temp_path: Path, result_base_path: Path):
        shutil.make_archive(str(result_base_path/self.course.name), 'zip', temp_path)

    def _compile(self, temp_path: Path, result_base_path: Path) -> bool:
        beginning_dir = os.getcwd()
        os.chdir(temp_path)
        # latexmk compiles multiple times and all, so that's great
        # It requires perl and a latex distro to be installed.
        compile_cmd = ("latexmk main.tex -shell-escape -pdf -halt-on-error -lualatex")
        completed_process = subprocess.run(compile_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(beginning_dir)

        if completed_process.returncode == 0:
            shutil.copy(temp_path/"main.pdf", result_base_path/f"{self.course.name}.pdf")
            return True
        Logger.error("Compilation failed.", path=None)
        return False
    
    def _make_code_zip_and_compile(self, tag: str|None, base_path: Path, make_code_zip: bool, compile: bool):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self.write(tag, temp_path)
            Logger.info("Written precompiled files.")
            if make_code_zip:
                self._zip(temp_path, base_path)
                zip_path = base_path/f"{self.course.name}.zip"
                Logger.info(f"Code zip created at {zip_path}.")
            if compile:
                if self._compile(temp_path, base_path):
                    pdf_path = base_path/f"{self.course.name}.pdf"
                    Logger.info(f"Compilation successful, pdf at {pdf_path}.")
    
    def make_code_zip_and_compile(self, tag: str|None, result_base_path: Path):
        self._make_code_zip_and_compile(tag, result_base_path, make_code_zip=True, compile=True)

    def make_code_zip(self, tag: str|None, result_base_path: Path):
        self._make_code_zip_and_compile(tag, result_base_path, make_code_zip=True, compile=False)
    
    def compile(self, tag: str|None, result_base_path: Path):
        self._make_code_zip_and_compile(tag, result_base_path, make_code_zip=False, compile=True)
