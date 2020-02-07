import pytest

from utilslib.dr import Store


def test_store_object(s3_stub):
    key = '/test/key/1234'
    bucket_name = 'test-bucket'
    data = 'hello world'
    
    s3_stub.add_response(
        'put_object',
        expected_params={'Key': key, 'Bucket': bucket_name, 'Body': b'hello world'},
        service_response={'ETag': '1234abc', 'VersionId': '1234'},
    )
    s3_stub.activate()

    store = Store(client=s3_stub.client, bucket_name=bucket_name)
    store.store_in_bucket(key, data)

def test_delete_object_from_versioned_bucket(s3_stub):
    key = '/test/key/1234'
    bucket_name = 'test-bucket'

    s3_stub.add_response(
        'delete_object',
        expected_params={'Key': key, 'Bucket': bucket_name},
        service_response={'DeleteMarker': True, 'VersionId': '1234'},
    )
    s3_stub.activate()

    store = Store(client=s3_stub.client, bucket_name=bucket_name)
    result = store.delete_from_bucket(key)

    assert result['DeleteMarker'] == True

def test_delete_object_from_unversioned_bucket(s3_stub):
    key = '/test/key/1234'
    bucket_name = 'test-bucket'

    s3_stub.add_response(
        'delete_object',
        expected_params={'Key': key, 'Bucket': bucket_name},
        service_response={'DeleteMarker': False, 'VersionId': '1234'},
    )
    s3_stub.activate()

    store = Store(client=s3_stub.client, bucket_name=bucket_name)
    result = store.delete_from_bucket(key)

    assert result['DeleteMarker'] == False

