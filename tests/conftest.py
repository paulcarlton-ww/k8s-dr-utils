import os
from distutils import dir_util
import pytest
import boto3
from botocore.stub import Stubber


@pytest.fixture(autouse=True)
def s3_stub():
    stubbed_client = boto3.client('s3')

    with Stubber(stubbed_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def datadir(tmpdir):
    filename = os.path.realpath(__file__)
    mod_dir = os.path.dirname(filename)
    test_dir = os.path.join(mod_dir, "data/")

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir
