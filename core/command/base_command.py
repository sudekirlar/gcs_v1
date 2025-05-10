# core/command/base_command.py

from abc import ABC, abstractmethod
from typing import Callable


class IRunnableCommand(ABC):
    """
    Her drone komutunun temel soyut arayüzü.
    Arayüzden bağımsız şekilde çalıştırılabilir.
    """

    def __init__(self, notify_user: Callable[[str], None]):
        """
        :param notify_user: Kullanıcıya bilgi vermek için UI tarafından sağlanan callback fonksiyonu.
        """
        self.notify_user = notify_user

    @abstractmethod
    def run(self):
        """
        Komutun çalıştırıldığı ana fonksiyon.
        Tüm iş mantığı burada yer alır.
        """
        pass

    def notify(self, message: str):
        """
        UI’ye bilgi mesajı gönderir. Gelişmiş sistemde loglama veya event yayınlama ile entegre edilebilir.
        """
        if callable(self.notify_user):
            self.notify_user(message)
        else:
            print(f"[Notify] {message}")
