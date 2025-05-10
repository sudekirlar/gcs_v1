import time
import unittest
from unittest.mock import patch, MagicMock
from infrastructure.connectors.tcp_connector import TcpConnector


class TestTcpConnectionTiming(unittest.TestCase):
    def test_connection_open_timing(self):
        ip = "127.0.0.1"
        port = 14550
        connector = TcpConnector(ip, port)

        with patch("infrastructure.connectors.tcp_connector.socket.socket") as mock_socket_class:
            mock_socket_instance = MagicMock()
            mock_socket_class.return_value = mock_socket_instance

            # Zaman ölçümü başlat
            start = time.perf_counter()

            # Open fonksiyonunu çalıştır
            connector.open()

            # ThreadPool'daki işlem tamamlanana kadar bekle (bu kritik!)
            connector.thread_pool.waitForDone()

            end = time.perf_counter()
            elapsed = end - start

            print(f"Bağlantı süresi: {elapsed:.4f} saniye")
            self.assertTrue(connector.is_connected())
