from typing import Any
from typing import Self

class CodeBuilder():
    """Build source code."""

    INDENT_STEP = 4

    def __init__(self, indent_level=0) -> None:
        """Initialize CodeBuilder.
        
        Args:
            indent_level: number of spaces to indent the newline with.
        """
        self.code: list[Any] = []
        self.indent_level: int = indent_level

    def add_line(self, line: Any) -> None:
        """Add a new line to the source code.

        Indentation and newline will be added automatically.

        Args:
            line: A line of source code to add.
                Can be of any type that has a `str` representation.
        """
        self.code.extend([" " * self.indent_level, line, "\n"])

    def indent(self) -> None:
        """Increase the indent for the lines that will be added later."""
        self.indent_level += self.INDENT_STEP

    def dedent(self) -> None:
        """Decrease the indent for the lines that will be added later.
        
        Raises:
            IndentationError: `indent_level` is subtracted to be less than 0.
        """
        if self.indent_level - self.INDENT_STEP < 0:
            raise IndentationError("Indent level cannot go below 0")

        self.indent_level -= self.INDENT_STEP

    def add_section(self) -> Self:
        """Adds a sub-CodeBuilder.

        This may be to add text later on in the build process.

        Returns:
            An instance of the `CodeBuilder` class.
        """
        section: CodeBuilder = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def get_globals(self) -> dict[str, Any]:
        """Executes the code and returns a dict of globals it defines.
        
        Returns:
            A dictionary of globals (where keys are of type `str` and 
            their values are of type `Any`) defined from the python source code 
            execution.
        """
        assert self.indent_level == 0
        python_source: str = str(self)
        global_namespace: dict[str, Any] = dict()
        exec(python_source, global_namespace)
        return global_namespace

    def __str__(self) -> str:
        """Returns a string representation of all the lines of code.
        
        Returns:
            Concatenated string of all source code lines in self.code.
        """
        return "".join(str(c) for c in self.code)
