import pytest

from utilslib.dr import S3

def test_parse_key_correctly(s3_stub):
    key='cluster2/bank-app2/Deployment/apps-v1/podinfo.yaml'

    s3 = S3(client=s3_stub.client, bucket_name='my-bucket')

    cluster, app, kind, name = s3.parse_key(key)

    assert cluster == 'cluster2'
    assert app == 'bank-app2'
    assert kind == 'Deployment'
    assert name == 'podinfo.yaml'

def test_parse_key_incorrectley(s3_stub):
    key='this/is.wrong'

    s3 = S3(client=s3_stub.client, bucket_name='my-bucket')

    with pytest.raises(Exception):
        s3.parse_key(key)
