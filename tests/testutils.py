from urllib3 import HTTPResponse
from kubernetes.client import ApiClient

def create_response_data(testfile, response_type):
    with open(testfile, 'r') as file:
        data = file.read()

    client = ApiClient()
    response = HTTPResponse(body=data)
    return client.deserialize(response, response_type)