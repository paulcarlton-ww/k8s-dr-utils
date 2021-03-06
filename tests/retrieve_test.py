# pylint: skip-file
import io
from botocore.response import StreamingBody

from utilslib.dr import Retrieve

def test_get_bucket_keys_exists(s3_stub):
    prefix = 'default/cluster2/'
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
    prefix = 'default/cluster2/'
    bucket_name = 'test-bucket'

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': prefix},
        service_response=STUB_NO_CONTENTS
    )
    s3_stub.activate()

    retrieve = Retrieve(client=s3_stub.client, bucket_name=bucket_name)
    result = retrieve.get_bucket_keys(prefix)

    assert len(result) == 0

def test_get_bucket_item(s3_stub):
    key = 'default/cluster2/bank-app2/Deployment/apps-v1/podinfo.yaml'
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

STUB_NO_CONTENTS = {
    "KeyCount": 0,
    "Contents": []
}

STUB_LIST_RESPONSE = {
    "KeyCount": 3,
    "Contents": [
        {
            "Key": "default/cluster2/namespace1/abc.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "2537abc",
            "Size": 1234,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "default/cluster2/namespace1/def.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "default/cluster2/namespace2/def.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        }
    ]
}
