#  Copyright Donex UG or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import aws_cdk as cdk

from aws_cdk import (Stack,
                     aws_apigateway as apigateway,
                     aws_s3 as s3,
                     aws_kms as kms,
                     aws_lambda as lambda_)

from constructs import Construct

class EthLambda(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 dir: str,
                 env: dict
                 ):
        super().__init__(scope, id)

        bundling_docker_image = cdk.DockerImage.from_registry(
            "lambci/lambda:build-python3.8"
        )

        commands = [
            "if [[ -f requirements.txt ]]; then pip install --target /asset-output -r requirements.txt; fi",
            "cp --parents $(find . -name '*.py') /asset-output"
        ]

        bundling_config = cdk.BundlingOptions(
            image=bundling_docker_image, command=["bash", "-xe", "-c", " && ".join(commands)]
        )

        code = lambda_.Code.from_asset(
            path=dir, bundling=bundling_config
        )

        lf = lambda_.Function(
            self,
            "Function",
            handler="lambda_function.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            environment=env,
            timeout=cdk.Duration.minutes(2),
            code=code,
            memory_size=256
        )

        self.lf = lf


class AwsKmsLambdaEthereumStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, eth_network: str = 'rinkeby', **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cmk = kms.Key(self, "eth-cmk-identity",
                          removal_policy=cdk.RemovalPolicy.DESTROY)
        cfn_cmk = cmk.node.default_child
        cfn_cmk.key_spec = 'ECC_SECG_P256K1'
        cfn_cmk.key_usage = 'SIGN_VERIFY'

        eth_client = EthLambda(self, "eth-kms-client",
                               dir="aws_kms_lambda_ethereum/_lambda/functions/eth_client",
                               env={"LOG_LEVEL": "DEBUG",
                                    "KMS_KEY_ID": cmk.key_id,
                                    "ETH_NETWORK": eth_network
                                    }
                               )

        cmk.grant(eth_client.lf, 'kms:GetPublicKey')
        cmk.grant(eth_client.lf, 'kms:Sign')

        eth_client_eip1559 = EthLambda(self, "KmsClientEIP1559",
                                       dir="aws_kms_lambda_ethereum/_lambda/functions/eth_client_eip1559",
                                       env={"LOG_LEVEL": "DEBUG",
                                            "KMS_KEY_ID": cmk.key_id,
                                            "ETH_NETWORK": eth_network
                                            }
                                       )

        cmk.grant(eth_client_eip1559.lf, 'kms:GetPublicKey')
        cmk.grant(eth_client_eip1559.lf, 'kms:Sign')

        cdk.CfnOutput(self, 'KeyID', value=cmk.key_id,
                       description="KeyID of the KMS-CMK instance used as the Ethereum identity instance")
