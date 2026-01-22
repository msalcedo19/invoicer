import asyncio
import inspect
import types
from typing import Any, Callable, Coroutine, List, Type, Union, cast

# Compatibility shim for Python 3.12+ where asyncio.coroutine was removed.
if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = types.coroutine  # type: ignore[attr-defined]

from awebus import Bus

# Avoid weakref handler collection when we wrap handlers at runtime.
bus = Bus(event_use_weakref=False)


def _event_type(clazz: Type) -> str:
    """Event type."""
    return f"{clazz.__module__}.{clazz.__name__}"


class Event:
    """
    Base class for all events.
    """

    def event_type(self) -> str:
        """Event type."""
        return _event_type(self.__class__)


EventHandlerType = Callable[..., Coroutine[Any, Event, Any]]


def _ensure_async(handler: Callable[..., Any]) -> EventHandlerType:
    """Ensure async."""
    if asyncio.iscoroutinefunction(handler):
        return cast(EventHandlerType, handler)

    async def _wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper."""
        result = handler(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    return cast(EventHandlerType, _wrapper)


def unregister(
    event_type: Type, async_event_handler: Callable[..., Coroutine[Any, Event, Any]]
) -> None:
    """
    :event_type: the Class corresponding to the event type from which
        to unregister the given event handler (the class in question should
        inherit from this module's Event class).
    :async_event_handler: the async event handler function to unregister.
    """
    bus.off(_event_type(event_type), async_event_handler)


def register(
    event_type: Type, async_event_handler: Union[EventHandlerType, List[EventHandlerType]]
) -> None:
    """
    :event_type: the class corresponding to the event type to register
        an event handler with (the class in question should
        inherit from this module's Event class).
    :async_event_handler: an async event handler function to call when events of
        of the passed in type are published
    """
    if type(async_event_handler) == list:
        handlers: List[EventHandlerType] = cast(List[EventHandlerType], async_event_handler)
        for h in handlers:
            bus.on(_event_type(event_type), _ensure_async(h))
    else:
        bus.on(_event_type(event_type), _ensure_async(async_event_handler))


async def publish(event: Event) -> None:
    """
    :event: publishes the given event (internally dispatched to the registered handlers).
    """
    await bus.emitAsync(event.event_type(), event)
