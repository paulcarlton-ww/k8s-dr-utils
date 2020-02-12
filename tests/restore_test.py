# pylint: skip-file
import io
from utilslib.dr import Restore
from utilslib.restore.strategy import NullStrategy
from botocore.stub import ANY
from botocore.response import StreamingBody
from .testutils import create_response_data, read_file

def test_restore_all_namespaces(s3_stub, mocker, datadir):
    bucket_name = 'test-bucket'
    cluster_name = 'cluster1'

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': cluster_name},
        service_response=STUB_LIST_RESPONSE_MULTINS
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Namespace'},
        service_response=STUB_LIST_RESPONSE_KS_NS
    )

    body = read_file(datadir.join('namespace.json').strpath)
    response_stream = StreamingBody(
        io.BytesIO(body.encode()),
        len(body)
    )
    s3_stub.add_response(
        'get_object',
        expected_params={'Bucket': bucket_name, 'Key': 'cluster1/kube-system/Namespace/v1/kube-system.yaml'},
        service_response={'Body': response_stream}
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/LimitRange'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/ResourceQuota'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/ConfigMap'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Secret'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Service'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Deployment'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/Namespace'},
        service_response=STUB_LIST_RESPONSE_APP_NS
    )

    body = read_file(datadir.join('namespace_app1.json').strpath)
    response_stream = StreamingBody(
        io.BytesIO(body.encode()),
        len(body)
    )
    s3_stub.add_response(
        'get_object',
        expected_params={'Bucket': bucket_name, 'Key': 'cluster1/app1/Namespace/v1/app1.yaml'},
        service_response={'Body': response_stream}
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/LimitRange'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/ResourceQuota'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/ConfigMap'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/Secret'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/Service'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/app1/Deployment'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )

    s3_stub.activate()

    strategy = NullStrategy(cluster_name)

    restore = Restore(bucket_name,strategy,client=s3_stub.client,cluster_name=cluster_name, kube_config=datadir.join('kubeconfig').strpath)
    num_processed = restore.restore_namespaces(cluster_name)

    assert num_processed == 2

def test_restore_single_namespaces(s3_stub, mocker, datadir):
    bucket_name = 'test-bucket'
    namespace = 'kube-system'
    cluster_name = 'cluster1'

    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': cluster_name},
        service_response=STUB_LIST_RESPONSE_MULTINS
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Namespace'},
        service_response=STUB_LIST_RESPONSE_KS_NS
    )

    body = read_file(datadir.join('namespace.json').strpath)
    response_stream = StreamingBody(
        io.BytesIO(body.encode()),
        len(body)
    )
    s3_stub.add_response(
        'get_object',
        expected_params={'Bucket': bucket_name, 'Key': 'cluster1/kube-system/Namespace/v1/kube-system.yaml'},
        service_response={'Body': response_stream}
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/LimitRange'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/ResourceQuota'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/ConfigMap'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Secret'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Service'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': 'cluster1/kube-system/Deployment'},
        service_response=STUB_LIST_RESPONSE_EMPTY
    )

    s3_stub.activate()

    strategy = NullStrategy(cluster_name)

    restore = Restore(bucket_name,strategy, client=s3_stub.client, cluster_name=cluster_name, kube_config=datadir.join('kubeconfig').strpath)
    num_processed = restore.restore_namespaces(cluster_name,namespace)

    assert num_processed == 1


STUB_LIST_RESPONSE_MULTINS = {
    "Contents": [
        {
            "Key": "cluster1/kube-system/Namespace/v1/kube-system.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "2537abc",
            "Size": 1234,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "cluster1/app1/Namespace/v1/app1.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        }
    ]
}

STUB_LIST_RESPONSE_KS_NS = {
    "Contents": [
        {
            "Key": "cluster1/kube-system/Namespace/v1/kube-system.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "2537abc",
            "Size": 1234,
            "StorageClass": "STANDARD"
        }
    ]
}

STUB_LIST_RESPONSE_APP_NS = {
    "Contents": [
        {
            "Key": "cluster1/app1/Namespace/v1/app1.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        }
    ]
}

STUB_LIST_RESPONSE_EMPTY = {
    "Contents": []
}