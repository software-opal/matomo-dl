from typing import IO, Callable, Generic, Iterable, Optional, TypeVar, overload

_T = TypeVar("_T")


class ProgressBar(object, Generic[_T]):
    short_limit: float = ...

    def update(self, n_steps: int) -> None:
        ...

    def finish(self) -> None:
        ...

    def __enter__(self) -> "ProgressBar[_T]":
        ...

    def __exit__(self, exc_type, exc_value, tb) -> None:
        ...

    def __iter__(self) -> "ProgressBar[_T]":
        ...

    def __next__(self) -> _T:
        ...


@overload
def progressbar(
    iterable: Iterable[_T],
    length: Optional[int] = ...,
    label: Optional[str] = ...,
    show_eta: bool = ...,
    show_percent: Optional[bool] = ...,
    show_pos: bool = ...,
    item_show_func: Optional[Callable[[_T], str]] = ...,
    fill_char: str = ...,
    empty_char: str = ...,
    bar_template: str = ...,
    info_sep: str = ...,
    width: int = ...,
    file: Optional[IO] = ...,
    color: Optional[bool] = ...,
) -> ProgressBar[_T]:
    ...


@overload  # noqa: F811
def progressbar(
    iterable: None = ...,
    length: Optional[int] = ...,
    label: Optional[str] = ...,
    show_eta: bool = ...,
    show_percent: Optional[bool] = ...,
    show_pos: bool = ...,
    item_show_func: Optional[Callable[[_T], str]] = ...,
    fill_char: str = ...,
    empty_char: str = ...,
    bar_template: str = ...,
    info_sep: str = ...,
    width: int = ...,
    file: Optional[IO] = ...,
    color: Optional[bool] = ...,
) -> ProgressBar[int]:
    ...
