"""AWS Integration.

AWS services: SQS, SNS, Lambda.
"""

from .sqs import SQSClient
from .sns import SNSClient
from .lambda_client import LambdaClient

__all__ = [
    "SQSClient",
    "SNSClient",
    "LambdaClient",
]
