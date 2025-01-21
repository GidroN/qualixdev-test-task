from jsonrpc_client.client import JSONRPCClient


def process_rpc_request(
        url: str,
        key: str,
        certificate: str,
        method: str,
        params: dict) -> tuple[dict, str]:

    client = JSONRPCClient(url, key, certificate)
    try:
        response = client.send(method, params)
        return response, ''
    except Exception as e:
        error_message = f"Error while calling the API: {e}"
        return {}, error_message
