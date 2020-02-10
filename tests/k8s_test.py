from utilslib.dr import K8s
from .testutils import create_response_data

def test_read_namespace(mocker, datadir):
    k8s = K8s(cluster_name='cluster2')

    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespace", autospec=True)
    patched.return_value = create_response_data(datadir.join('namespace.json').strpath, 'V1Namespace')

    result = k8s.read_namespace("namespace1")

    assert result.kind == "Namespace"
    assert result.metadata.name == "default"

def test_list_kind(mocker, datadir):
    k8s = K8s(cluster_name='cluster2')

    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.list_namespaced_config_map", autospec=True)
    patched.return_value = create_response_data(datadir.join('configmaplist.json').strpath, 'V1ConfigMapList')

    result = k8s.list_kind("kube-system","ConfigMap")

    assert len(result) == 3

def test_read_kind(mocker, datadir):
    k8s = K8s(cluster_name='cluster2')

    test = k8s.read_kind("kube-system","ConfigMap","coredns")

    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespaced_config_map", autospec=True)
    patched.return_value = create_response_data(datadir.join('configmap.json').strpath, 'V1ConfigMap')

    result = k8s.read_kind("kube-system","ConfigMap","coredns")

    assert result.kind == "ConfigMap"
    assert result.metadata.name == "coredns"
    assert result.metadata.namespace == "kube-system"