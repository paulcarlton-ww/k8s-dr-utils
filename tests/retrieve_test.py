# pylint: skip-file
import io
from botocore.response import StreamingBody

from utilslib.dr import Retrieve

def test_get_bucket_keys_exists(s3_stub):
    prefix = 'cluster2/'
    bucket_name = 'test-bucket'

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': prefix},
        service_response=STUB_LIST_RESPONSE
    )
    s3_stub.activate()

    retrieve = Retrieve(client=s3_stub.client, bucket_name=bucket_name)
    result = retrieve.get_bucket_keys(prefix)

    assert len(result) == 3

def test_get_bucket_keys_no_contents(s3_stub):
    prefix = 'cluster2/'
    bucket_name = 'test-bucket'

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': prefix},
        service_response={'Contents':[]}
    )
    s3_stub.activate()

    retrieve = Retrieve(client=s3_stub.client, bucket_name=bucket_name)
    result = retrieve.get_bucket_keys(prefix)

    assert len(result) == 0

def test_get_bucket_item(s3_stub):
    key = 'cluster2/bank-app2/Deployment/apps-v1/podinfo.yaml'
    bucket_name = 'test-bucket'
    body = 'hello world'.encode()

    response_stream = StreamingBody(
        io.BytesIO(body),
        len(body)
    )

    s3_stub.add_response(
        'get_object',
        expected_params={'Bucket': bucket_name, 'Key': key},
        service_response={'Body': response_stream}
    )
    s3_stub.activate()

    retrieve = Retrieve(client=s3_stub.client, bucket_name=bucket_name)
    result = retrieve.get_bucket_item(key)

    assert result == body

def test_get_s3_namespaces(s3_stub):
    clustername = 'cluster2'
    bucket_name = 'test-bucket'

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': clustername},
        service_response=STUB_LIST_RESPONSE
    )
    s3_stub.activate()

    retrieve = Retrieve(client=s3_stub.client, bucket_name=bucket_name)
    result = retrieve.get_s3_namespaces(clustername)

    assert len(result) == 2
    assert result[0] == "namespace1"
    assert result[1] == "namespace2"


STUB_LIST_RESPONSE = {
    "Contents": [
        {
            "Key": "cluster2/namespace1/abc.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "2537abc",
            "Size": 1234,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "cluster2/namespace1/def.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "cluster2/namespace2/def.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        }
    ]
}
