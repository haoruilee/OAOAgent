# OAOAgent - AI Oracle Client

OAOAgent is a Python client library for interacting with AI oracles deployed on the Ethereum blockchain based on [OAO SimplePrompt Contract](https://github.com/ora-io/OAO). It enables sending requests to AI models on-chain, fetching results, and storing conversation context, allowing developers to create intelligent agents with personalized behavior.


# Key Features:
- Context Management: Stores ongoing conversation context, ensuring continuity in the conversation with the AI oracle.
- System Prompts: Customize agent behavior using a system prompt that can be provided at initialization.
- Event Listening: Listens for events on the blockchain to fetch results from the AI oracle and handle responses.

# How to use

## Client Initialization
```python
class EthAIClient:
    def __init__(self, infura_url, contract_address, ai_oracle_address, private_key, from_address, system_prompt="You are an assistant"):
```
- infura_url: URL for the Ethereum node provider (e.g., Infura or Alchemy).
- contract_address: Ethereum smart contract address for interacting with the AI oracle.
- ai_oracle_address: Address of the AI oracle contract that handles the AI model.
- private_key: The private key for signing transactions.
- from_address: The Ethereum address used to send transactions.
- system_prompt: A customizable system prompt to guide the behavior of the agent. The default is "You are an assistant".

## Sending an AI Request
```python
def send_ai_request(self, model_id, prompt, value_in_wei):
```
- model_id: The ID of the AI model to be used.
- prompt: The user’s query or request.
- value_in_wei: The amount of Ether to be sent with the request, in Wei.

## Listening for Events

```python
def listen_for_prompts_updated_event(self, max_retries=200, timeout=120):
```

- max_retries: The maximum number of retries before stopping.
- timeout: Maximum time to wait for a response.

It fetches new events, decodes the AI’s response, and appends it to the context. It stops once the response is received or the retries/timeout conditions are met.

# Example Usage

Here’s how to use the EthAIClient to interact with the AI oracle:

## example_of_context

Example usage shows this client can successfully append context to the contract interaction.

Transaction history: https://sepolia.etherscan.io/tx/0x865f1f70fc9b5b423893cdd9d55cab0d087f74dc1ca1418cd76f0ed846d84c37

## example_of_systemprompt

This one is like https://www.freysa.ai/act-iii  

You can run a Love Challenge where you can try to make all agents say "I love you" to win. The agents are customizable with unique personalities defined by system prompts.

# On going

Current no LLMs with [toolChoice](https://cookbook.openai.com/examples/using_tool_required_for_customer_service) ability is deployed on OAO and the context length is limited, so we current cannot merge this client to other AI-Agent framework like swarm.