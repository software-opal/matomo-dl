import difflib
import functools
import itertools

import attr
import click


class ColoredDiffer(difflib.Differ):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.line_diff_styles = {
            " ": functools.partial(click.style, dim=True),
            "-": functools.partial(click.style, fg="red"),
            "+": functools.partial(click.style, fg="green"),
        }
        self.char_diff_styles = {
            " ": functools.partial(click.style, dim=True),
            "-": functools.partial(click.style, bg="red"),
            "+": functools.partial(click.style, bg="green"),
            "^": functools.partial(click.style, bold=True),
        }

    def colorise(self, line):
        line = line.rstrip("\n")
        styling = self.line_diff_styles[line[0]]
        tag = styling(line[0], bold=True)
        return f"{tag}{styling(line[1:])}"

    def colorise_char_diff(self, line, diff):
        line = line.rstrip("\n")
        diff = diff.rstrip("\n")
        styling = self.line_diff_styles[line[0]]
        out = styling(line[0], bold=True) + " "
        if len(line) >= 3:
            last_char_tag = diff[2]
            run = line[2]
            for char, char_tag in itertools.zip_longest(
                line[3:], diff[3:], fillvalue=" "
            ):
                if last_char_tag != char_tag:
                    out += self.char_diff_styles[last_char_tag](run)
                    run = char
                    last_char_tag = char_tag
                else:
                    run += char
            out += self.char_diff_styles[last_char_tag](run)
        yield out
        # yield diff

    def compare(self, a, b):
        if isinstance(a, str):
            a = a.splitlines(keepends=True)
        if isinstance(b, str):
            b = b.splitlines(keepends=True)

        last = None
        cmpiter = super().compare(a, b)
        for line in cmpiter:
            tag = line[0]
            if tag != "?":
                if last is not None:
                    yield self.colorise(last)
                last = line
            else:
                a_line, a_diff = last, line
                yield from self.colorise_char_diff(a_line, a_diff)
                b_line, b_diff = next(cmpiter), next(cmpiter)
                yield from self.colorise_char_diff(b_line, b_diff)
                last = None
