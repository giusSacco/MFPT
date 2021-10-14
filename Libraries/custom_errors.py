from typing import NoReturn, Optional

class FileNotValidError(Exception):
    def __init__(self, filename : str, msg : Optional[str] = None) -> NoReturn:
        if msg is None:
            msg = f"Error: File '{filename}' does not match the required format"
        super().__init__(msg)

class NoTransitionFoundError(Exception):
    def __init__(self, filename : str, msg : Optional[str] = None) -> NoReturn:
        if msg is None:
            msg = f'No transition events have been found during the data analysis of {filename}'
        super().__init__(msg)

class OptionError(Exception):
    def __init__(self, parameter_name : str, msg : Optional[str] = None) -> NoReturn:
        if msg is None:
            msg = f'Error in option: given {parameter_name} is not valid'
        super().__init__(msg)

class SectionNotPresentError(Exception):
    def __init__(self, section_name : str, msg : Optional[str] = None) -> NoReturn:
        if msg is None:
            msg = f"Error: section '{section_name}' is missing in the input file"
        super().__init__(msg)

class ParameterNotPresentError(Exception):
    def __init__(self, section_name : str, parameter_name : str, msg : Optional[str] = None) -> NoReturn:
        if msg is None:
            msg = f"Error: {parameter_name} is missing in the section '{section_name}' of the input file"
        super().__init__(msg)