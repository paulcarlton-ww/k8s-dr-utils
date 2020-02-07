import pytest
import boto3
from botocore.stub import Stubber


@pytest.fixture(autouse=True)
def s3_stub():
    stubbed_client = boto3.client('s3')

    with Stubber(stubbed_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()
