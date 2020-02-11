# pylint: skip-file
from urllib3 import HTTPResponse
from kubernetes.client import ApiClient

def create_response_data(testfile, response_type):
    data = read_file(testfile)

    client = ApiClient()
    response = HTTPResponse(body=data)
    return client.deserialize(response, response_type)

def read_file(testfile):
    with open(testfile, 'r') as file:
        return file.read().replace('\n','',-1)