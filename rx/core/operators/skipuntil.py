from asyncio import Future
from typing import Any, Callable, Optional, TypeVar, Union, cast

from rx import from_future
from rx.core import Observable, abc
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future

_T = TypeVar("_T")


def skip_until_(
    other: Union[Observable[_T], "Future[_T]"]
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the values from the source observable sequence only after
    the other observable sequence produces a value.

    Args:
        other: The observable sequence that triggers propagation of
            elements of the source sequence.

    Returns:
        An observable sequence containing the elements of the source
    sequence starting from the point the other sequence triggered
    propagation.
    """

    if is_future(other):
        obs: Observable[Any] = from_future(other)
    else:
        obs = cast(Observable[_T], other)

    def skip_until(source: Observable[_T]) -> Observable[_T]:
        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            is_open = [False]

            def on_next(left: _T) -> None:
                if is_open[0]:
                    observer.on_next(left)

            def on_completed() -> None:
                if is_open[0]:
                    observer.on_completed()

            subs = source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )
            subscriptions = CompositeDisposable(subs)

            right_subscription = SingleAssignmentDisposable()
            subscriptions.add(right_subscription)

            def on_next2(x: Any) -> None:
                is_open[0] = True
                right_subscription.dispose()

            def on_completed2():
                right_subscription.dispose()

            right_subscription.disposable = obs.subscribe(
                on_next2, observer.on_error, on_completed2, scheduler=scheduler
            )

            return subscriptions

        return Observable(subscribe)

    return skip_until


__all__ = ["skip_until_"]
