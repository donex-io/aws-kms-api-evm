#  Copyright Donex UG or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import logging
import os
import json

from web3.auto import w3

from lambda_helper import (assemble_tx,
                           get_params,
                           get_tx_params,
                           calc_eth_address,
                           get_kms_public_key,
                           find_eth_signature)

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)


def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))

    try:
        params = get_params()
    except Exception as e:
        raise e

    _logger.debug(event)
    body = event['body']
    _logger.debug(body)
    body_dict = json.loads(body)
    _logger.debug(body_dict)
    operation = body_dict['operation']
    _logger.debug(operation)

    if not operation:
        raise ValueError('operation needs to be specified in request and needs to be eigher "status" or "send"')

    # {"operation": "status"}
    if operation == 'getaddress':
        key_id = os.getenv('KMS_KEY_ID')
        pub_key = get_kms_public_key(key_id)
        eth_checksum_address = calc_eth_address(pub_key)

        response_body = {'eth_checksum_address': eth_checksum_address}

        response_object = {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }

        return response_object

    
    elif operation == 'sign_message':
        key_id = os.getenv('KMS_KEY_ID')
        pub_key = get_kms_public_key(key_id)
        eth_checksum_address = calc_eth_address(pub_key)

        message = body_dict.get('message')
        _logger.debug(message)

        message_prefix = '\x19Ethereum Signed Message:\n' + str(len(bytes(message, 'utf-8')))
        _logger.debug(message_prefix)

        message_hash = w3.keccak(bytes(message_prefix + message, 'utf8'))
        _logger.debug(message_hash)

        sig = find_eth_signature(params, message_hash)
        _logger.debug(sig)

        response_body = {    
            'eth_checksum_address': eth_checksum_address,
            #'pub_key': pub_key,
            'message': message,
            'message_hash': message_hash.hex(),
            #'message_hash_bytes': message_hash,
            'r': hex(sig.get('r')),
            's': hex(sig.get('s'))
        }
        _logger.debug(response_body)

        response_object = {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }

        return response_object


    elif operation == 'sign':

        if not (body_dict.get('dst_address') and body_dict.get('amount', -1) >= 0 and body_dict.get('nonce', -1) >= 0):
            return {'operation': 'sign',
                    'error': 'missing parameter - sign requires amount, dst_address and nonce to be specified'}

        # get key_id from environment varaible
        key_id = os.getenv('KMS_KEY_ID')

        # get destination address from send request
        dst_address = body_dict.get('dst_address')

        # get amount from send request
        amount = body_dict.get('amount')

        nonce = body_dict.get('nonce')

        # optional params
        chainid = body_dict.get('chainid')
        type = body_dict.get('type')
        max_fee_per_gas = body_dict.get('max_fee_per_gas')
        max_priority_fee_per_gas = body_dict.get('max_priority_fee_per_gas')

        # download public key from KMS
        pub_key = get_kms_public_key(key_id)

        # calculate the Ethereum public address from public key
        eth_checksum_addr = calc_eth_address(pub_key)

        # collect rawd parameters for Ethereum transaction
        tx_params = get_tx_params(dst_address=dst_address,
                                  amount=amount,
                                  nonce=nonce,
                                  chainid=chainid,
                                  type=type,
                                  max_fee_per_gas=max_fee_per_gas,
                                  max_priority_fee_per_gas=max_priority_fee_per_gas)

        # assemble Ethereum transaction and sign it offline
        raw_tx_signed_hash, raw_tx_signed_payload = assemble_tx(tx_params=tx_params,
                                                                params=params,
                                                                eth_checksum_addr=eth_checksum_addr,
                                                                chainid=chainid)

        response_body = {"signed_tx_hash": raw_tx_signed_hash,
                        "signed_tx_payload": raw_tx_signed_payload}
        
        response_object = {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }

        return response_object