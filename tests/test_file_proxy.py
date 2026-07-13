import io
import sys

import pytest

from rich.console import Console
from rich.file_proxy import FileProxy


def test_empty_bytes():
    console = Console()
    file_proxy = FileProxy(console, sys.stdout)
    # File should raise TypeError when writing bytes
    with pytest.raises(TypeError):
        file_proxy.write(b"")  # type: ignore
    with pytest.raises(TypeError):
        file_proxy.write(b"foo")  # type: ignore


def test_flush():
    file = io.StringIO()
    console = Console(file=file)
    file_proxy = FileProxy(console, file)
    file_proxy.write("foo")
    assert file.getvalue() == ""
    file_proxy.flush()
    assert file.getvalue() == "foo\n"


def test_new_lines():
    file = io.StringIO()
    console = Console(file=file)
    file_proxy = FileProxy(console, file)
    file_proxy.write("-\n-")
    assert file.getvalue() == "-\n"
    file_proxy.flush()
    assert file.getvalue() == "-\n-\n"


def test_flush_decodes_pending_ansi():
    """flush() must run the pending buffer through the ANSI decoder so that
    partial escape sequences that never reached write()'s newline path are
    rendered to the console as real ANSI rather than left as raw text.

    Pre-fix the buffer was joined with '' and passed to console.print() as a
    string, which the decoder re-rendered and produced duplicated ESC bytes.
    """
    file = io.StringIO()
    console = Console(
        file=file, force_terminal=True, width=80, color_system="truecolor"
    )
    file_proxy = FileProxy(console, file)
    file_proxy.write("ABC\033[31mRED\033[0mEND")
    assert file.getvalue() == ""
    file_proxy.flush()
    # The escape sequences must round-trip through console.print as single
    # \x1b[...m sequences, not be mangled.
    assert file.getvalue() == "ABC\x1b[31mRED\x1b[0mEND\n"
    # An empty flush after the buffer is drained must not append anything.
    file_proxy.flush()
    assert file.getvalue() == "ABC\x1b[31mRED\x1b[0mEND\n"


def test_isatty():
    """Check isatty is proxied

    Regression test for https://github.com/Textualize/rich/issues/4041

    """

    class TTYFile:
        def isatty(self) -> bool:
            return True

    file = TTYFile()
    console = Console()
    file_proxy = FileProxy(console, file)
    assert file_proxy.isatty()
