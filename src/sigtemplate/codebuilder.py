from typing import Any


class CodeBuilder():
    """Build source code."""
    # Standard defined by PEP8
    INDENT_STEP = 4

    def __init__(self, indent_level=0) -> None:
        """Initialize CodeBuilder class."""
        self.code: list[Any] = []
        self.indent_level: int = indent_level

    def add_line(self, line) -> None:
        """Add a new line to the source code.
        Indentation and newline will be added automatically.
        """
        self.code.extend([" " * self.indent_level, line, "\n"])

    def indent(self) -> None:
        """Increase the indent for the lines that will be added later."""
        self.indent_level += self.INDENT_STEP

    def dedent(self) -> None:
        """Decrease the indent for the lines that will be added later."""
        if self.indent_level - self.INDENT_STEP < 0:
            raise Exception("Indent level cannot go below 0")

        self.indent_level -= self.INDENT_STEP

    def add_section(self) -> CodeBuilder:
        """Adds a sub-CodeBuilder.
        This may be to add text later on in the build process.
        """
        section: CodeBuilder = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def get_globals(self) -> dict[str, Any]:
        """Executes the code and returns a dict of globals it defines."""
        assert self.indent_level == 0
        python_source: str = str(self)
        global_namespace: dict[str, Any] = dict()
        exec(python_source, global_namespace)
        return global_namespace

    def __str__(self) -> str:
        """Returns a string representation of all the lines of code."""
        return "".join(str(c) for c in self.code)
