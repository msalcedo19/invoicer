from typing import Any, Callable, Coroutine, List, Type, Union, cast

from awebus import Bus

bus = Bus()


def _event_type(clazz: Type) -> str:
    return f"{clazz.__module__}.{clazz.__name__}"


class Event:
    """
    Base class for all events.
    """

    def event_type(self) -> str:
        return _event_type(self.__class__)


EventHandlerType = Callable[..., Coroutine[Any, Event, Any]]


def unregister(event_type: Type, async_event_handler: Callable[..., Coroutine[Any, Event, Any]]):
    """
    :event_type: the Class corresponding to the event type from which
        to unregister the given event handler (the class in question should
        inherit from this module's Event class).
    :async_event_handler: the async event handler function to unregister.
    """
    bus.off(_event_type(event_type), async_event_handler)


def register(
    event_type: Type, async_event_handler: Union[EventHandlerType, List[EventHandlerType]]
):
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
            bus.on(_event_type(event_type), h)
    else:
        bus.on(_event_type(event_type), async_event_handler)


async def publish(event: Event):
    """
    :event: publishes the given event (internally dispatched to the registered handlers).
    """
    await bus.emitAsync(event.event_type(), event)
