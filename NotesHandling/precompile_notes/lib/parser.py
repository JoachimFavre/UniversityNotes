import re
from typing import List

CLOSING_FOR = {
    "(": ")",
    "{": "}",
    "[": "]"
}

class Parser:
    @staticmethod
    def find_lecture_command(latex: str) -> re.Match[str]|None:
        return re.search(r"\\lecture{(\d+)}{([^\}]+)}{([^\n]+)}{", latex)

    @staticmethod
    def matching_parenthesis(string: str, pos: int) -> int:
        if string[pos] not in CLOSING_FOR:
            raise Exception(f"Character at position {pos} is not an opening parenthesis.")
        
        stack = [string[pos]]
        while len(stack) > 0 and pos < len(string) - 1:
            pos += 1
            if string[pos] in CLOSING_FOR:
                stack.append(string[pos])
            elif string[pos] == CLOSING_FOR[stack[-1]]:
                stack.pop()
            elif string[pos] in CLOSING_FOR.values():
                raise Exception(f"Unexpected closing parenthesis {string[pos]} at position {pos}.")
        
        if len(stack) > 0:
            raise Exception(f"Missing closing parenthesis for {stack[-1]}.")

        return pos
    
    @staticmethod
    def block_content(string: str, pos: int) -> str:
        if string[pos] != "{":
            raise Exception(f"Character at position {pos} is not an opening bracket.")
        
        closing_pos = Parser.matching_parenthesis(string, pos)
        return string[pos+1:closing_pos]
    
    @staticmethod
    def extract_all_cmd_content(string: str, cmd: str) -> List[str]:
        matches = re.finditer(rf"\\{cmd}{{", string)
        result = []
        for match in matches:
            result.append(Parser.block_content(string, match.end(0) - 1))
        return result
    
    @staticmethod
    def any_cmd_content_contains(string: str, cmd: str, content: str) -> bool:
        for current_content in Parser.extract_all_cmd_content(string, cmd):
            if current_content.count(content) > 0:
                return True
        return False
    
    @staticmethod
    def matching_end_env(string: str, pos: int) -> int:
        match = re.match(r"^\begin{([^\}]+)}", string[pos:])
        if match is None or match.start(0) != 0:
            raise Exception(f"Position {pos} does not show the start of an environment.")
        env = match.group(1)

        count = 1
        while count > 0 and pos < len(string) - 1:
            pos += 1
            if string[pos:].startswith(f"\\begin{{{env}}}"):
                count += 1
            elif string[pos:].startswith(f"\\end{{{env}}}"):
                count -= 1

        if count > 0:
            raise Exception(f"Missing closing \\end{{{env}}}.")
        
        return pos
    
    @staticmethod
    def something_between(string: str, *, start: int, end: int) -> bool:
        return string[start:end].strip() != ""
