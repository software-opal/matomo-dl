import logging
import typing as typ

import attr

logger = logging.getLogger(__name__)
T = typ.TypeVar("T")


def normalise_name(name: str, upper_names: typ.Collection[str]) -> str:
    if name in upper_names:
        return name
    else:
        if name != name.lower():
            logger.warning(f"The name {name} is not lower case")
        return name.lower()


def normalise_call_names(
    names: typ.Iterable[str], upper_names: typ.Collection[str]
) -> typ.FrozenSet[str]:
    out_names = set()
    for name in names:
        out_names.add(normalise_name(name, upper_names))
    return frozenset(out_names)


@attr.s(frozen=True)
class OrderedCall(typ.Generic[T]):

    name: str = attr.ib()
    call: T = attr.ib(cmp=False, default=lambda info: None)
    requires: typ.FrozenSet[str] = attr.ib(
        cmp=False, default=frozenset(), converter=frozenset
    )
    affects: typ.FrozenSet[str] = attr.ib(
        cmp=False, default=frozenset(), converter=frozenset
    )

    def normalise(self, upper_names: typ.Collection[str] = ()) -> "OrderedCall":
        upper_names = frozenset(upper_names)
        return attr.evolve(
            self,
            name=normalise_name(self.name, upper_names),
            requires=normalise_call_names(self.requires, upper_names),
            affects=normalise_call_names(self.affects, upper_names),
        )

    @classmethod
    def from_callable(cls, call, **k) -> "OrderedCall":
        return cls(name=call.__name__, call=call, **k)


def order_calls_by_dependencies(
    data: typ.Collection[OrderedCall]
) -> typ.Sequence[OrderedCall]:
    tree_inputs: typ.Dict[str, OrderedCall] = {}
    for call in data:
        if call.name in tree_inputs:
            raise ValueError("Cannot add calls with the same name twice")
        tree_inputs[call.name] = call

    requires_set: typ.Dict[str, typ.Set[str]] = {}
    for name, call in tree_inputs.items():
        assert call.requires.issubset(tree_inputs.keys())
        assert call.affects.issubset(tree_inputs.keys())
        requires_set.setdefault(name, set()).update(call.requires)
        for affects_name in call.affects:
            requires_set.setdefault(affects_name, set()).add(name)

    affects_single_set: typ.Dict[str, typ.Set[str]] = {
        name: set() for name in requires_set.keys()
    }
    for after, before_set in requires_set.items():
        for before in before_set:
            affects_single_set[before].add(after)
    affects_combined = {}
    for before, after_set in affects_single_set.items():
        affects_combined[before] = after_set
        affects_combined[before].update(
            *[affects_single_set[after] for after in after_set]
        )
        assert before not in affects_combined[before], f"Cycle detected{requires_set}"

    call_order = sorted(
        affects_single_set.items(),
        key=lambda name_val: (len(name_val[1]), sorted(name_val[1]), name_val[0]),
        reverse=True,
    )
    return tuple(tree_inputs[name] for name, _ in call_order)


if __name__ == "__main__":
    order_calls_by_dependencies(
        {
            OrderedCall("a", requires=["b", "c"]),
            OrderedCall("b", requires=["d", "c"]),
            OrderedCall("c", requires=[]),
            OrderedCall("d", requires=[]),
            OrderedCall("e", requires=[]),
        }
    )
