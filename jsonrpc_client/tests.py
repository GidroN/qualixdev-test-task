from unittest.mock import patch, mock_open, Mock

from django.test import TestCase
from django.conf import settings

from jsonrpc_client.client import JSONRPCClient, JSONRPCClientException


class JSONRPCClientUnitTestCase(TestCase):
    def setUp(self):
        self.url = "https://example.com/api"
        self.key = "fake_key"
        self.certificate = "fake_certificate"
        self.client = JSONRPCClient(self.url, self.key, self.certificate)

    @patch('builtins.open', new_callable=mock_open)
    def test_create_temporary_file(self, mock_open_file):
        # Arrange
        filename = 'temp_file.tmp'
        context = 'some_context'

        # Act
        result = self.client._create_temporary_file(filename, context)

        # Assert
        mock_open_file.assert_called_once_with(filename, 'w')
        mock_open_file().write.assert_called_once_with(context)
        self.assertEqual(result, filename)

    @patch('os.remove')
    def test_remove_temporary_file(self, mock_remove):
        # Arrange
        filename = 'temp_file.temp'

        # Act
        self.client._remove_temporary_file(filename)

        # Asser
        mock_remove.assert_called_once_with(filename)

    @patch("ssl.create_default_context")
    def test_create_ssl_context(self, mock_ssl_context):
        # Arrange
        certificate_filename = 'temp_file.cert'
        key_filename = 'temp_file.key'
        mock_context = Mock()
        mock_ssl_context.return_value = mock_context

        #  Act
        self.client._create_ssl_context(certificate_filename, key_filename)

        # Assert
        mock_ssl_context.assert_called_once()
        mock_context.load_cert_chain.assert_called_once_with(certfile=certificate_filename, keyfile=key_filename)


class JSONRPCClientIntegrationTestCase(TestCase):
    def setUp(self):
        key = settings.CLIENT_KEY
        certificate = settings.CLIENT_CERTIFICATE
        self.url = settings.API_URL
        self.client = JSONRPCClient(self.url, key, certificate)

    def test_empty_params(self):
        # Arrange
        method = 'auth.check'
        params = {}

        # Act & Assert
        with self.assertRaises(JSONRPCClientException):
            self.client.send(method, params)

    def test_successful_auth_check(self):
        # Arrange
        method = 'auth.check'
        params = {'id': 1}

        # Act
        response = self.client.send(method, params)

        # Assert
        self.assertIn('result', response)
        self.assertNotIn('error', response)

    def test_invalid_ssl_context(self):
        # Arrange
        key = 'invalid_key'
        certificate = 'invalid_certificate'
        method = 'auth.check'
        params = {'id': 1}
        client = JSONRPCClient(self.url, key, certificate)

        # Act & Assert
        with self.assertRaises(JSONRPCClientException):
            client.send(method, params)

    def test_invalid_method(self):
        # Arrange
        method = 'invalid_method'
        params = {'id': 1}

        # Act
        response = self.client.send(method, params)

        # Assert
        self.assertIn('error', response)
