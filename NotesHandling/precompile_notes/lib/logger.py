from pathlib import Path


class Logger:
    @staticmethod
    def info(message: str):
        print(message)
    
    @staticmethod
    def newline():
        print()

    @staticmethod
    def warn(message: str, path: Path|None):
        if path is not None:
            warning = f"WARNING ({path})"
        else:
            warning = "WARNING"

        print(f"\t{warning}: {message}")

    @staticmethod
    def error(message: str, path: Path|None):
        if path is not None:
            error = f"ERROR ({path})"
        else:
            error = "ERROR"

        print(f"\t\t{error}: {message}")
