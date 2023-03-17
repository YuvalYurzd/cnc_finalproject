from unittest.mock import patch
from client import *
import subprocess
import time
import socket
import unittest
import pyodbc
from sqlServer import count_workers, check_worker_exists


class TestDNSClient(unittest.TestCase):

    @patch('builtins.input', return_value='www.google.com')
    @patch('socket.socket')
    def test_dns_client(self, mock_socket, mock_input):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.recv.return_value = b'127.0.0.1'
        dns_client()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_socket_instance.sendto.assert_called_once_with(b'www.google.com', ('localhost', 53))
        mock_socket_instance.recv.assert_called_once_with(1024)


class TestDNSServer(unittest.TestCase):

    def setUp(self):
        self.dns_process = subprocess.Popen(['python', 'dnsServer.py'], stdout=subprocess.PIPE)
        time.sleep(1)

    def tearDown(self):
        self.dns_process.terminate()

    def test_resolve_google(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'www.google.com', ('localhost', 53))
        data, addr = sock.recvfrom(1024)
        self.assertEqual(data.decode('utf-8'), socket.gethostbyname('www.google.com'))
        sock.close()

    def test_resolve_cache(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'www.google.com', ('localhost', 53))
        data, addr = sock.recvfrom(1024)
        self.assertEqual(data.decode('utf-8'), socket.gethostbyname('www.google.com'))
        sock.close()


class TestSQLServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = pyodbc.connect(
            'Driver={SQL Server};' 'Server=localhost; ' 'Database=project;' 'Trusted_connection=yes;')

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_count_workers(self):
        expected_count = 11  # replace with the current number of workers in the table if you made changes
        actual_count = int(count_workers(self.connection).split()[3])
        self.assertEqual(actual_count, expected_count)

    def test_check_worker_exists(self):
        expected_output = "Here is a list of workers that their name is: Yuval:\n('Yuval', 'Yurzdichinsky', '111111111', '123', 2)"
        actual_output = check_worker_exists(self.connection)  # Enter Yuval here
        self.assertEqual(actual_output.strip(), expected_output.strip())


if __name__ == '__main__':
    unittest.main()
