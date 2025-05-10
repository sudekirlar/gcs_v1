# core/interfaces/connector_interface.py

from abc import ABC, abstractmethod

class IConnector(ABC):
    """
    Bağlantı kurulumunu soyutlayan arayüz.
    Bu sınıf, Serial veya TCP gibi farklı bağlantı türlerini ortak bir sözleşmeyle tanımlar.
    """

    @abstractmethod
    def open(self):
        """
        Bağlantıyı başlatır.
        Blocking olabilir, bu yüzden genellikle ayrı bir iş parçacığında (thread) çalıştırılır.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Bağlantıyı kapatır. Kullanıcı arayüzü tarafından çağrılır.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Bağlantı durumu hakkında bilgi verir.
        Örn: Serial bağlandı mı, TCP soket aktif mi vs.
        """
        pass

    @abstractmethod
    def get_identifier(self) -> str:
        """
        Arayüzde görünmesi için bağlantının kısa tanımı (örneğin: 'COM7' veya '192.168.1.10:5760').
        """
        pass