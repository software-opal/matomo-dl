import logging
import re

from matomo_dl.bundle.info import BuildInformation

logger = logging.getLogger(__name__)
AUTOLOAD_CLASSMAP_ENTRY_RE = re.compile(
    r'^.*? => \$(vendorDir|baseDir) \. ([\'"])(.*?)\2,$'
)
AUTOLOAD_STATIC_ENTRY_RE = re.compile(
    r'^.*? => __DIR__ \. ([\'"])/(.*?)\1 \. ([\'"])(.*?)\3,$'
)


def regenerate_autoload_classmap(build: BuildInformation) -> None:
    folder = build.folder
    bases = {"vendorDir": folder / "vendor", "baseDir": folder}
    autoload = folder / "vendor/composer/autoload_classmap.php"
    autoload_file = iter(autoload.read_text().splitlines(keepends=False))
    prefix = []
    content = []
    postfix = []
    for line in autoload_file:
        prefix.append(line)
        if "return array(" in line:
            break
    for line in autoload_file:
        match = AUTOLOAD_CLASSMAP_ENTRY_RE.fullmatch(line)
        if not match:
            postfix.append(line)
            break
        baseType, fname = match.group(1, 3)
        file = bases[baseType] / f".{fname}"
        if not file.exists() or not file.is_file():
            logger.debug(
                f"autoload_classmap.php Removing {baseType!r}, {fname!r} => ({file.exists()}, {file.is_file()}) {file!r} "
            )
            # Remove missing entries
            continue
        content.append(line)
    postfix.extend(autoload_file)
    autoload.write_text("\n".join(prefix + sorted(content) + postfix))


def regenerate_autoload_static(build: BuildInformation) -> None:
    folder = build.folder
    autoload = folder / "vendor/composer/autoload_static.php"
    base = autoload.parent
    autoload_file = iter(autoload.read_text().splitlines(keepends=False))
    prefix = []
    content = []
    postfix = []
    for line in autoload_file:
        prefix.append(line)
        if "public static $classMap = array (" in line:
            break
    for line in autoload_file:
        match = AUTOLOAD_STATIC_ENTRY_RE.fullmatch(line)
        if not match:
            postfix.append(line)
            break
        cdPart, filePart = match.group(2, 4)
        file = base / f"{cdPart}{filePart}"
        if not file.exists() or not file.is_file():
            logger.debug(
                f"autoload_static.php Removing {cdPart!r}{filePart!r} => ({file.exists()}, {file.is_file()}) {file!r} "
            )
            # Remove missing entries
            continue
        content.append(line)
    postfix.extend(autoload_file)
    autoload.write_text("\n".join(prefix + sorted(content) + postfix))
    pass
