import collections
import re
import string
import typing as typ

SECTION_RE = re.compile(r"^\[(.*?)\](\s*;|$)")
ENTRY_RE = re.compile(r"^(.*?)\s*=\s*(.*?)(\s*;|$)")

ConfigValueScalars = typ.Union[None, int, float, str]
ConfigValues = typ.Union[ConfigValueScalars, typ.List[ConfigValueScalars]]


def read(file: typ.Iterable[str]) -> typ.Dict[str, typ.Dict[str, ConfigValues]]:
    current_section: typ.Dict[str, ConfigValues] = collections.OrderedDict()
    config: typ.Dict[str, typ.Dict[str, ConfigValues]] = collections.OrderedDict()
    for line in file:
        line = line.strip()
        if not line or line[0] == ";":
            continue
        section_match = SECTION_RE.match(line)
        entry_match = ENTRY_RE.match(line)
        if section_match:
            current_section = collections.OrderedDict()
            config[section_match.group(1)] = current_section
        elif entry_match:
            key, value = entry_match.group(1, 2)
            print(f"{key!r} = {value!r}")
            key, value = key.strip(), value.strip()
            if not value:
                real_value: ConfigValueScalars = None
            elif value[0] == value[-1] and value[0] in ['"', "'"]:
                real_value = value[1:-1]
            else:
                try:
                    real_value = int(value)
                except ValueError:
                    try:
                        real_value = float(value)
                    except ValueError:
                        real_value = value
            if key.endswith("[]"):
                val = current_section.setdefault(key[:-2], [])
                assert isinstance(val, list)
                val.append(real_value)
            else:
                current_section[key] = real_value
    return config


def write(
    config: typ.Dict[str, typ.Dict[str, ConfigValues]],
    file: typ.IO,
    *,
    include_php_exit=True,
):
    if include_php_exit:
        file.write("; <?php exit; ?> DO NOT REMOVE THIS LINE\n")
    for section, items in config.items():
        file.write(f"\n[{section}]\n")
        file.write("".join(_value_to_string(k, v) for k, v in items.items()))


def _value_to_string(key: str, value: ConfigValues) -> str:
    if value is None:
        return f"{key} =\n"
    elif isinstance(value, str):
        if not value:
            return f'{key} = ""\n'
        elif value[0] not in string.ascii_letters:
            return f'{key} = "{value}"\n'
        else:
            return f"{key} = {value}\n"
    elif isinstance(value, (int, float)):
        return f"{key} = {value}\n"
    else:
        return "".join(_value_to_string(f"{key}[]", val) for val in value)


if __name__ == "__main__":
    import sys

    write(read(open(sys.argv[1])), open(sys.argv[2], "w"))
