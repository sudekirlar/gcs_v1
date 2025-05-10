# utils/event_bus.py

from collections import defaultdict
from typing import Type, Callable, Dict, List

class EventBus:
    _subscribers: Dict[Type, List[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: Type, callback: Callable):
        """
        Belirli bir event türü için callback fonksiyonu ekler.
        """
        cls._subscribers[event_type].append(callback)

    @classmethod
    def unsubscribe(cls, event_type: Type, callback: Callable):
        """
        Belirli bir event türü için callback fonksiyonunu çıkarır.
        """
        if callback in cls._subscribers[event_type]:
            cls._subscribers[event_type].remove(callback)

    @classmethod
    def publish(cls, event):
        print(f"[EVENTBUS] Yayınlanıyor: {event.__class__.__name__}")
        for subscriber in cls._subscribers.get(type(event), []):
            subscriber(event)