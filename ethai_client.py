import json
import time
import logging
from time import sleep
from web3 import Web3
from exceptions import TransactionFailedError, InvalidResponseError, ContractInteractionError
from logging_config import setup_logging

CONTRACT_ABI = [
    {
      "inputs": [
        {
          "internalType": "contract IAIOracle",
          "name": "_aiOracle",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "contract IAIOracle",
          "name": "expected",
          "type": "address"
        },
        {
          "internalType": "contract IAIOracle",
          "name": "found",
          "type": "address"
        }
      ],
      "name": "UnauthorizedCallbackSource",
      "type": "error"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "requestId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "modelId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "prompt",
          "type": "string"
        }
      ],
      "name": "promptRequest",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "requestId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "output",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "bytes",
          "name": "callbackData",
          "type": "bytes"
        }
      ],
      "name": "promptsUpdated",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "aiOracle",
      "outputs": [
        {
          "internalType": "contract IAIOracle",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "requestId",
          "type": "uint256"
        },
        {
          "internalType": "bytes",
          "name": "output",
          "type": "bytes"
        },
        {
          "internalType": "bytes",
          "name": "callbackData",
          "type": "bytes"
        }
      ],
      "name": "aiOracleCallback",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "modelId",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "prompt",
          "type": "string"
        }
      ],
      "name": "calculateAIResult",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "callbackGasLimit",
      "outputs": [
        {
          "internalType": "uint64",
          "name": "",
          "type": "uint64"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "modelId",
          "type": "uint256"
        }
      ],
      "name": "estimateFee",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "requestId",
          "type": "uint256"
        }
      ],
      "name": "isFinalized",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "requests",
      "outputs": [
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "modelId",
          "type": "uint256"
        },
        {
          "internalType": "bytes",
          "name": "input",
          "type": "bytes"
        },
        {
          "internalType": "bytes",
          "name": "output",
          "type": "bytes"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "modelId",
          "type": "uint256"
        },
        {
          "internalType": "uint64",
          "name": "gasLimit",
          "type": "uint64"
        }
      ],
      "name": "setCallbackGasLimit",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
]

class EthAIClient:
    def __init__(self, infura_url, contract_address, ai_oracle_address, private_key, from_address, system_prompt="You are a assistant"):
        setup_logging()
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum network!")
        
        logging.info("Connected to Ethereum network successfully")

        self.contract_address = contract_address
        self.ai_oracle_address = ai_oracle_address
        self.private_key = private_key
        self.from_address = from_address
        self.contract_abi = CONTRACT_ABI
        self.contract = self.w3.eth.contract(address=contract_address, abi=self.contract_abi)
        self.context = []  # This will store the ongoing conversation context
        self.system_prompt = system_prompt

        logging.debug(f"Contract ABI loaded: {self.contract_abi}")

    def send_ai_request(self, model_id, prompt, value_in_wei):
        """
        This method sends a new AI request, appends the prompt to the context with role labeling,
        and includes the entire context when building the transaction.
        """
        if not self.context:
            self.context.append({'role': 'system', 'content': self.system_prompt})

        self.context.append({'role': 'user', 'content': prompt})
        context_for_prompt = "\n".join([f"{entry['role']}: {entry['content']}" for entry in self.context])

        try:
            logging.debug(f"Preparing transaction with model_id: {model_id}, prompt: {context_for_prompt}, value: {value_in_wei} Wei")
            gas_limit = 800000
            transaction = self.contract.functions.calculateAIResult(model_id, context_for_prompt).build_transaction({
                'chainId': 11155111,
                'gas': gas_limit,
                'gasPrice': self.w3.to_wei(100, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.from_address),
                'value': value_in_wei
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            logging.debug(f"Transaction signed: {signed_txn}")
            
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            logging.info(f"Transaction sent! TX hash: {self.w3.to_hex(tx_hash)}")
            return self.w3.to_hex(tx_hash)
        
        except Exception as e:
            logging.error(f"Error sending AI request: {e}")
            raise TransactionFailedError(f"Error sending AI request: {e}")


    def get_transaction_receipt(self, tx_hash):
        try:
            logging.debug(f"Fetching receipt for TX hash: {tx_hash}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logging.info(f"Transaction receipt received: {receipt}")
            
            if receipt['status'] == 1:
                logging.info("Transaction succeeded!")
                return receipt
            else:
                raise TransactionFailedError(f"Transaction failed! {tx_hash}")
        
        except Exception as e:
            logging.error(f"Error fetching transaction receipt: {e}")
            raise TransactionFailedError(f"Error fetching transaction receipt: {e}")

    def listen_for_prompts_updated_event(self, max_retries=200, timeout=120):
        retries = 0
        start_time = time.time()

        logging.info("Starting to listen for promptsUpdated event...")

        prompts_updated_filter = self.contract.events.promptsUpdated.create_filter(from_block='latest')

        while retries < max_retries:
            try:
                events = prompts_updated_filter.get_new_entries()
                if events:
                    logging.info(f"New events detected: {len(events)}")
                    for event in events:
                        request_id = event['args']['requestId']
                        output = event['args']['output']
                        callback_data = event['args']['callbackData']

                        logging.info(f"Prompt updated! Request ID: {request_id}")
                        logging.info(f"Output: {output}")
                        logging.info(f"Callback Data: {callback_data}")
                        decoded_output = self.decode_output(output)
                        
                        self.context.append({'role': 'assistant', 'content': decoded_output})

                        logging.info(f"Decoded Output: {decoded_output}")

                        return decoded_output

                else:
                    logging.info("No new events detected. Retrying...")
                    
                time.sleep(5)

                if time.time() - start_time > timeout:
                    logging.warning(f"Timeout exceeded ({timeout} seconds) without receiving a result.")
                    break

                retries += 1

            except Exception as e:
                logging.error(f"Error while listening for events: {e}")
                raise ContractInteractionError(f"Error while listening for events: {e}")

        logging.error(f"Failed to receive a result after {max_retries} retries and {timeout} seconds.")
        return None

    def decode_output(self, output):
        """Decode the output if necessary (e.g., hex to string)."""
        try:
            if output.startswith('0x'):
                decoded = bytes.fromhex(output[2:]).decode('utf-8')
            else:
                decoded = output

            return decoded
        except Exception as e:
            logging.error(f"Error decoding output: {e}")
            raise InvalidResponseError("Failed to decode AI response")

    def get_context(self):
        """Return the current context."""
        return self.context