import collections
import re

SECTION_RE = re.compile(r"^\[(.*?)\](\s*;|$)")
ENTRY_RE = re.compile(r"^(.*?)\s*=\s*(.*?)(\s*;|$)")


def read(file):
    current_section = None
    config = collections.OrderedDict()
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
            key, value = key.strip(), value.strip()
            print(f"{key!r} {value!r}")
            if not value:
                value = None
            elif value[0] == value[-1] and value[0] in ['"', "'"]:
                value = value[1:-2]
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
            if key.endswith("[]"):
                current_section.setdefault(key[:-2], []).append(value)
            else:
                current_section[key] = value
    return config


def write(config, file):
    file.write("; <?php exit; ?> DO NOT REMOVE THIS LINE\n")
    for section, items in config.items():
        file.write(f"\n[{section}]\n")
        file.write("".join(_value_to_string(k, v) for k, v in items.items()))


def _value_to_string(key, value) -> str:
    if value is None:
        return f"{key} =\n"
    elif isinstance(value, str):
        if not value:
            return f"{key} =\n"
        elif value[0] in "0123456789":
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
