# application/services/master_provider.py

class MasterProvider:
    """
    pymavlink master nesnesini merkezi şekilde paylaşmak için kullanılır.
    Bu sayede bağlantı bir kez açılır ve tüm sistem modülleri bu bağlantıyı kullanabilir.
    """

    _master = None  # pymavlink master (mavutil.mavlink_connection sonucu)

    @classmethod
    def set(cls, master):
        """
        Master nesnesini tanımlar (bağlantı kurulduğunda çağrılır)
        """
        cls._master = master

    @classmethod
    def get(cls):
        """
        Master nesnesini döner. Tanımlanmamışsa hata fırlatır.
        """
        if cls._master is None:
            raise RuntimeError("[ERROR] Master bağlantısı henüz tanımlanmadı.")
        return cls._master

    @classmethod
    def clear(cls):
        """
        Bağlantı kapatıldığında master referansı temizlenir.
        """
        cls._master = None