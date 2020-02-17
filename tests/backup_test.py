# pylint: skip-file
from utilslib.dr import Backup
from botocore.stub import ANY
from .testutils import create_response_data

def test_backup(s3_stub, mocker, datadir):
    bucket_name = 'test-bucket'
    namespace = 'kube-system'
    cluster_name = 'cluster1'
    cluster_set = 'default'
    prefix = 'default/cluster1/kube-system'

    patched_read_ns = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespace", autospec=True)
    patched_read_ns.return_value = create_response_data(datadir.join('namespace.json').strpath, 'V1Namespace')

    patched_list_kind_cm = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_config_map", autospec=True)
    patched_list_kind_cm.return_value = create_response_data(datadir.join('configmaplist_single.json').strpath, 'V1ConfigMapList')

    patched_list_kind_lm = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_limit_range", autospec=True)
    patched_list_kind_lm.return_value = create_response_data(datadir.join('limitrangelist_empty.json').strpath, 'V1LimitRangeList')

    patched_list_kind_rq = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_resource_quota", autospec=True)
    patched_list_kind_rq.return_value = create_response_data(datadir.join('resourcequotalist_empty.json').strpath, 'V1ResourceQuotaList')

    patched_list_kind_secret = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_secret", autospec=True)
    patched_list_kind_secret.return_value = create_response_data(datadir.join('secretlist_empty.json').strpath, 'V1SecretList')

    patched_list_kind_service = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_service", autospec=True)
    patched_list_kind_service.return_value = create_response_data(datadir.join('servicelist_empty.json').strpath, 'V1ServiceList')

    patched_list_kind_podtemp = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_pod_template", autospec=True)
    patched_list_kind_podtemp.return_value = create_response_data(datadir.join('podtemplatelist_empty.json').strpath, 'V1PodTemplateList')

    patched_list_kind_deployment = mocker.patch("kubernetes.client.apis.apps_v1_api.AppsV1Api.list_namespaced_deployment", autospec=True)
    patched_list_kind_deployment.return_value = create_response_data(datadir.join('deploymentlist.json').strpath, 'V1DeploymentList')

    patched_list_kind_custom = mocker.patch("kubernetes.client.apis.custom_objects_api.CustomObjectsApi.list_namespaced_custom_object", autospec=True)
    patched_list_kind_custom.return_value = create_response_data(datadir.join('customlist.json').strpath, 'object')
    
    patched_read_cm = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespaced_config_map", autospec=True)
    patched_read_cm.return_value = create_response_data(datadir.join('configmap.json').strpath, 'V1ConfigMap')

    patched_read_deployment = mocker.patch("kubernetes.client.apis.apps_v1_api.AppsV1Api.read_namespaced_deployment", autospec=True)
    patched_read_deployment.return_value = create_response_data(datadir.join('deployment.json').strpath, 'V1Deployment')
    
    patched_get_kind_deployment = mocker.patch("kubernetes.client.apis.custom_objects_api.CustomObjectsApi.get_namespaced_custom_object", autospec=True)
    patched_get_kind_deployment.return_value = create_response_data(datadir.join('custom.json').strpath, 'object')

    s3_stub.add_response(
        'put_object',
        expected_params={'Key': 'default/cluster1/kube-system/Namespace/v1/kube-system.yaml', 'Bucket': bucket_name, 'Body': ANY},
        service_response={'ETag': '1234abc', 'VersionId': '1234'},
    )
    s3_stub.add_response(
        'put_object',
        expected_params={'Key': 'default/cluster1/kube-system/ConfigMap/v1/coredns.yaml', 'Bucket': bucket_name, 'Body': ANY},
        service_response={'ETag': '1234abc', 'VersionId': '1234'},
    )
    s3_stub.add_response(
        'put_object',
        expected_params={'Key': 'default/cluster1/kube-system/Deployment/apps_v1/coredns.yaml', 'Bucket': bucket_name, 'Body': ANY},
        service_response={'ETag': '1234abc', 'VersionId': '1234'},
    )
    s3_stub.add_response(
        'put_object',
        expected_params={'Key': 'default/cluster1/bank-app2/VirtualService/networking.istio.io_v1alpha3/ingress-podinfo.yaml', 'Bucket': bucket_name, 'Body': ANY},
        service_response={'ETag': '1234abc', 'VersionId': '1234'},
    )
    s3_stub.add_response(
        'list_objects_v2',
        expected_params={'Bucket': bucket_name, 'Prefix': prefix},
        service_response=STUB_LIST_RESPONSE
    )
    s3_stub.add_response(
        'delete_object',
        expected_params={'Key': 'default/cluster1/kube-system/Deployment/apps_v1/appdeleted.yaml', 'Bucket': bucket_name},
        service_response={'DeleteMarker': False, 'VersionId': '1234'},
    )
    s3_stub.activate()

    backup = Backup(client=s3_stub.client, bucket_name=bucket_name, cluster_set=cluster_set, cluster_name=cluster_name, kube_config=datadir.join('kubeconfig').strpath)
    num_stored, num_deleted = backup.save_namespace(namespace)
    assert num_stored == 4
    assert num_deleted == 1


STUB_LIST_RESPONSE = {
    "Contents": [
        {
            "Key": "default/cluster1/kube-system/Namespace/v1/kube-system.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "2537abc",
            "Size": 1234,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "default/cluster1/kube-system/ConfigMap/v1/coredns.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "default/cluster1/kube-system/Deployment/apps_v1/coredns.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        },
        {
            "Key": "default/cluster1/kube-system/Deployment/apps_v1/appdeleted.yaml",
            "LastModified": "2020-02-06T11:48:37.000Z",
            "ETag": "126abc",
            "Size": 4321,
            "StorageClass": "STANDARD"
        }
    ]
}