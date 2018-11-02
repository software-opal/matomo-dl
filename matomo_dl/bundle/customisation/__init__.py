import logging
import typing as typ

from matomo_dl.bundle.info import BuildInformation
from matomo_dl.call_tree import OrderedCall, order_calls_by_dependencies
from matomo_dl.progress import progressbar

logger = logging.getLogger(__name__)


CustomisationCallable = typ.Callable[[BuildInformation], None]
CustomisationCollection = typ.Collection[OrderedCall]


BASE_CALLS: typ.FrozenSet[OrderedCall] = frozenset(
    {
        OrderedCall("ALL", requires=["CONFIG", "PLUGINS", "FILES"]),
        OrderedCall("CONFIG", requires=["PLUGINS"]),
        OrderedCall("PLUGINS", affects=["FILES"]),
        OrderedCall("FILES"),
    }
)

BASE_CALL_NAMES = frozenset(c.name for c in BASE_CALLS)


def apply_customisations(build: BuildInformation) -> None:
    tree_inputs = set(BASE_CALLS)
    for call in set(build.customisations.get_customisation_functions()):
        tree_inputs.add(call.normalise(BASE_CALL_NAMES))
    calls = order_calls_by_dependencies(tree_inputs)
    with progressbar(calls, label="Applying customisations") as bar:
        for call in bar:
            call.call(build)
