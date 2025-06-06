# application/workers/command_runner_worker.py

from PyQt5.QtCore import QRunnable
from core.command.base_command import IRunnableCommand


class CommandRunnerWorker(QRunnable):
    """
    Komutları thread-safe biçimde çalıştıran worker sınıfı.
    Komutu GUI'den bağımsız şekilde arka planda yürütür.
    """

    def __init__(self, command: IRunnableCommand):
        """
        :param command: Çalıştırılacak IRunnableCommand örneği
        """
        super().__init__()
        self.command = command

    def run(self):
        """
        Qt thread havuzu tarafından çağrılır.
        Komutun run() metodunu çalıştırır.
        """
        try:
            self.command.run()
        except Exception as e:
            self.command.notify(f"[Hata] Komut çalıştırılırken hata oluştu: {e}")
