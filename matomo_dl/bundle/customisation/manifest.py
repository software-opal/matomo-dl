import logging
import re
from hashlib import md5

from matomo_dl.bundle.info import BuildInformation

logger = logging.getLogger(__name__)
MANIFEST_ENTRY_RE = re.compile(r'^(\s+)"(.*?)" => .*,$')


def regenerate_manifest(build: BuildInformation) -> None:
    folder = build.folder
    manifest = folder / "config/manifest.inc.php"
    manifest_file = iter(manifest.read_text().splitlines(keepends=False))
    prefix = []
    content = []
    postfix = []
    for line in manifest_file:
        prefix.append(line)
        if "$files" in line:
            break
    for line in manifest_file:
        match = MANIFEST_ENTRY_RE.fullmatch(line)
        if not match:
            postfix.append(line)
            break
        indent, fname = match.groups()
        file = folder / fname
        if not file.exists() or not file.is_file():
            # Remove missing entries
            continue
        stat = file.stat()
        if build.clamp_mtime(stat.st_mtime) == stat.st_mtime:
            # File unchanged in build.
            content.append(line)
            continue
        file_size = stat.st_size
        file_hash = md5(file.read_bytes()).hexdigest()
        content.append(f'{indent}"{fname}" => array("{file_size}", "{file_hash}"),')
    postfix.extend(manifest_file)
    manifest.write_text("\n".join(prefix + sorted(content) + postfix))


def autoload():
    # vendor/composer/autoload_classmap.php
    # vendor/composer/autoload_static.php
    pass
