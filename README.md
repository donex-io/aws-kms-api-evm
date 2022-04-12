# aws-kms-api-ethereum

***Disclaimer:** This project is work in progress and should not be used to manage keys that hold any real value!*

This project is an AWS API service that signs messages through an AWS Lambda function that creates and accesses an AWS KMS customer master key (CMK). It enables ECDSA signatures compatible with Ethereum or other EVM-based blockchains, i.e. it uses the EVM-specific pre-fixes and deals with the v parameter as well. 

In the subfolder `/tutorial/aws_kms_lambda_ethereum/` another project is placed that mimics the functionality of the [repository by David Dornseifer](https://github.com/aws-samples/aws-kms-ethereum-accounts) but is adapted to AWS CDK v2. This project signs complete Ethereum transactions (legacy or EIP1559). The main API project was based off of this tutorial.


## Setup

First make sure you have AWS CDK v2 up and running. These two tutorials can help: 

- https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
- https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-bootstrap

To deploy either one of the above introduced projects you first have to initialize your project like this:

```
mkdir project_name
cd project_name

cdk init app --language python

source .venv/bin/activate 
python -m pip install -r requirements.txt
```

Then insert / replace the files from this repo into the initialized project. After that you should be able to run: 

```
cdk synth
cdk init
```

It should print the url of your api on your console. 

## Tests

With the node script under `/tests/query_api.js` you can run a simple test of your deployed that returns your checksum address once directly from the key and once from the signature values `r`, `s` and `v`. The script has to be called like this:

```
node query_api.js 'test' 'url'
```

## Acknowledgements

This repository is based on the [blog post(s)](https://aws.amazon.com/de/blogs/database/part1-use-aws-kms-to-securely-manage-ethereum-accounts/) and the [repository](https://github.com/aws-samples/aws-kms-ethereum-accounts) by David Dornseifer.
