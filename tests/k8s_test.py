
from utilslib.dr import K8s

import logging

logger = logging.getLogger()

def test_create_kind(mocker):

    k8s = K8s(cluster_name='cluster2')

    patched = mocker.patch("kubernetes.client.apis.core_v1_api.CoreV1Api.read_namespace", new=mocked_readnamespace)


    result = k8s.read_namespace("namespace1")

    logger.info("result: {r}".format(r=result))

def mocked_readnamespace(self, name):
    return "Need to finish this"