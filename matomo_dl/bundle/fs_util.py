import itertools
import logging
import pathlib
import re
import typing as typ

logger = logging.getLogger(__name__)


def iter_tree(folder: pathlib.Path) -> typ.Iterator[pathlib.Path]:
    for path in folder.iterdir():
        if path.is_file():
            yield path
        elif path.is_dir():
            yield path
            yield from iter_tree(path)


def get_path_regex(
    base_path,
    *,
    regexes: typ.Iterable[str] = (),
    folders: typ.Iterable[str] = (),
    paths: typ.Iterable[str] = (),
    names: typ.Iterable[str] = (),
    stems: typ.Iterable[str] = (),
    extensions: typ.Iterable[str] = (),
) -> typ.Pattern:
    names_re = or_regex(map(re.escape, names))
    stems_re = or_regex(map(re.escape, stems))
    extensions_re = or_regex(map(re.escape, extensions))
    folders_re = or_regex(map(re.escape, map(lambda s: s.rstrip("/"), folders)))
    resp = list(regexes)
    resp.extend(map(re.escape, paths))
    if names_re:
        resp.append(f".*/{names_re}")
    if extensions_re:
        resp.append(f".*{extensions_re}")
    if stems_re:
        resp.append(f".*/{stems_re}(?:.[^/.]+)?$")
    if folders_re:
        resp.append(f"{folders_re}/.*")
    resp_re = or_regex(resp)
    assert resp_re
    return re.compile("^" + re.escape(str(base_path)) + resp_re + "$", re.IGNORECASE)


def or_regex(res: typ.Iterable[str]) -> typ.Optional[str]:
    regs = set(res)
    if len(regs) == 0:
        return None
    elif len(regs) == 1:
        return regs.pop()
    else:
        return f"(?:{'|'.join(regs)})"


def iter_all_matching(
    path: pathlib.Path, pattern: typ.Pattern
) -> typ.Iterator[pathlib.Path]:
    return filter(lambda path: pattern.match(str(path)), iter_tree(path))


def delete_all_matching(
    path: pathlib.Path, *, folders=(), paths=(), **kwds
) -> typ.Iterator[pathlib.Path]:
    chainable = [
        delete_all_iter(path / file for file in set(paths)),
        delete_all_iter(path / folder for folder in set(folders)),
    ]
    if kwds:
        chainable.append(
            delete_all_iter(iter_all_matching(path, get_path_regex(path, **kwds)))
        )
    return itertools.chain.from_iterable(chainable)


def delete_all(*paths: pathlib.Path) -> typ.Collection[pathlib.Path]:
    return delete_all_iter(paths)


def delete_all_iter(paths: typ.Iterable[pathlib.Path]) -> typ.Collection[pathlib.Path]:
    to_delete = set()
    for item in paths:
        to_delete.add(item)
    deleted = set()
    while to_delete:
        item = to_delete.pop()
        if item.is_dir():
            folder_iter = iter(item.iterdir())
            first = next(folder_iter, None)
            if first is None:
                item.rmdir()
                deleted.add(item)
            else:
                to_delete.update(folder_iter)
                to_delete.add(item)
                to_delete.add(first)
        elif item.exists():
            item.unlink()
            deleted.add(item)
    return deleted
