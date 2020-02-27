# pylint: skip-file
from utilslib.dr import DRBase
from .testutils import create_response_data

def test_create_s3_namespace(mocker, datadir):
    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespaced_config_map", autospec=True)
    patched.return_value = create_response_data(datadir.join('clusterdata.json').strpath, 'V1ConfigMap')

    drbase = DRBase(kube_config=datadir.join('kubeconfig').strpath)


    key = drbase.create_s3_key("bank-app1", "Deployment", "v1/apps", "test-app")

    assert key == "default/cluster2/bank-app1/Deployment/v1_apps/test-app.yaml"

def test_create_s3_namespace_prefix_notemplate(mocker, datadir):
    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespaced_config_map", autospec=True)
    patched.return_value = create_response_data(datadir.join('clusterdata.json').strpath, 'V1ConfigMap')

    drbase = DRBase(kube_config=datadir.join('kubeconfig').strpath, prefix='application-backups')


    key = drbase.create_s3_key("bank-app1", "Deployment", "v1/apps", "test-app")

    assert key == "application-backups/default/cluster2/bank-app1/Deployment/v1_apps/test-app.yaml"

def test_create_s3_namespace_prefix_template(mocker, datadir):
    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespaced_config_map", autospec=True)
    patched.return_value = create_response_data(datadir.join('clusterdata.json').strpath, 'V1ConfigMap')

    drbase = DRBase(kube_config=datadir.join('kubeconfig').strpath, prefix='$cluster_name/application-backups')


    key = drbase.create_s3_key("bank-app1", "Deployment", "v1/apps", "test-app")

    assert key == "cluster2/application-backups/default/cluster2/bank-app1/Deployment/v1_apps/test-app.yaml"
