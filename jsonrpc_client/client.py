import os
import ssl
import json
import logging
import urllib.request
from typing import Any


logger = logging.getLogger('jsonrpc_client.client')


class JSONRPCClientException(Exception):
    ...


class JSONRPCClient:
    DEFAULT_HEADERS = {'Content-Type': 'application/json'}
    DEFAULT_TEMPORARY_KEY_FILENAME = 'client_key.key'
    DEFAULT_TEMPORARY_CERTIFICATE_FILENAME = 'client_cert.crt'

    def __init__(self, url: str, key: str, certificate: str):
        self.url = url
        self.__CERTIFICATE = certificate
        self.__KEY = key
        self.__ssl_context = ...

    @staticmethod
    def _remove_temporary_file(filename: str):
        os.remove(filename)
        logger.debug(f'Removed temporary file: {filename}')

    @staticmethod
    def _create_temporary_file(filename: str, context: Any) -> str:
        with open(filename, 'w') as temporary_file:
            temporary_file.write(context)

        logger.debug(f'Created temporary file: {filename}')
        return filename

    def _create_ssl_context(self, certificate_filename: str, key_filename: str) -> None:
        try:
            self.__ssl_context = ssl.create_default_context()
            self.__ssl_context.load_cert_chain(certfile=certificate_filename, keyfile=key_filename)
            logger.debug('Successfully created ssl context.')
        except Exception as e:
            context = f'An error occurred while creating ssl context. Error: {e}'
            logger.error(context)
            raise JSONRPCClientException(context)

    def send(self, method: str, params: dict) -> dict:
        if not params:
            context = 'An error occurred while calling API with invalid parameters. Parameters cannot be empty.'
            logger.error(context)
            raise JSONRPCClientException(context)

        request_data = {
            'jsonrpc': '2.0',
            'method': method,
        }
        request_data.update(params)

        encoded_data = json.dumps(request_data).encode('utf-8')

        certificate_filename = self._create_temporary_file(self.DEFAULT_TEMPORARY_CERTIFICATE_FILENAME, self.__CERTIFICATE)
        key_filename = self._create_temporary_file(self.DEFAULT_TEMPORARY_KEY_FILENAME, self.__KEY)

        self._create_ssl_context(certificate_filename, key_filename)
        request = urllib.request.Request(self.url, data=encoded_data, headers=self.DEFAULT_HEADERS)

        try:
            with urllib.request.urlopen(request, context=self.__ssl_context) as response:
                logger.debug(f'Request successfully sent to url={self.url} with data={request_data}')
                response = response.read().decode('utf-8')
                serialized_response = json.loads(response)

            logger.debug(f'Response successfully got: {response}')

        except Exception as e:
            context = f'An error occurred while sending request to url={self.url} with data={request_data}. Error: {e}'
            logger.error(context)
            raise JSONRPCClientException(context)

        finally:
            self._remove_temporary_file(certificate_filename)
            self._remove_temporary_file(key_filename)

        return serialized_response
