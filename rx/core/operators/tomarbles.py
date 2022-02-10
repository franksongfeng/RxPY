from typing import Any, List, Optional

from rx.core import Observable, abc
from rx.core.typing import RelativeTime
from rx.scheduler import NewThreadScheduler

new_thread_scheduler = NewThreadScheduler()


def to_marbles(
    scheduler: Optional[abc.SchedulerBase] = None, timespan: RelativeTime = 0.1
):
    def to_marbles(source: Observable[Any]) -> Observable[str]:
        """Convert an observable sequence into a marble diagram string.

        Args:
            timespan: [Optional] duration of each character in second.
                If not specified, defaults to 0.1s.
            scheduler: [Optional] The scheduler used to run the the input
                sequence on.

        Returns:
            Observable stream.
        """

        def subscribe(
            observer: abc.ObserverBase[str],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            scheduler = scheduler or new_thread_scheduler

            result: List[str] = []
            last = scheduler.now

            def add_timespan():
                nonlocal last

                now = scheduler.now
                diff = now - last
                last = now
                secs = scheduler.to_seconds(diff)
                dashes = "-" * int((secs + timespan / 2.0) * (1.0 / timespan))
                result.append(dashes)

            def on_next(value: Any) -> None:
                add_timespan()
                result.append(stringify(value))

            def on_error(exception: Exception) -> None:
                add_timespan()
                result.append(stringify(exception))
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            def on_completed():
                add_timespan()
                result.append("|")
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            return source.subscribe(on_next, on_error, on_completed)

        return Observable(subscribe)

    return to_marbles


def stringify(value: Any) -> str:
    """Utility for stringifying an event."""
    string = str(value)
    if len(string) > 1:
        string = "(%s)" % string

    return string


__all__ = ["stringify"]
