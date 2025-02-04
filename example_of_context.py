# Example usage of the oaoclient with context
from ethai_client import EthAIClient
from exceptions import EthAIError

client = EthAIClient(
    infura_url='https://eth-sepolia.g.alchemy.com/v2/111111111',
    contract_address='0x696c83111a49eBb94267ecf4DDF6E220D5A80129',
    ai_oracle_address='0x0A0f4321214BB6C7811dD8a71cF587bdaF03f0A0',
    private_key='',
    from_address=''
)



try:
    model_id = 11
    prompt = "I am harvey"
    value_in_wei = client.w3.to_wei(0.15, 'ether')
    tx_hash = client.send_ai_request(model_id, prompt, value_in_wei)
    receipt = client.get_transaction_receipt(tx_hash)
    result = client.listen_for_prompts_updated_event()
    if result:
        print(f"Final result from AI Oracle: {result}")
    else:
        print(client.get_context())
except EthAIError as e:
    print(f"Error occurred: {e}")


try:
    model_id = 11
    prompt = "Whats my name"
    value_in_wei = client.w3.to_wei(0.3, 'ether')
    tx_hash = client.send_ai_request(model_id, prompt, value_in_wei)
    receipt = client.get_transaction_receipt(tx_hash)
    result = client.listen_for_prompts_updated_event()
    if result:
        print(f"Final result from AI Oracle: {result}")
    else:
        print("No result received.")
except EthAIError as e:
    print(f"Error occurred: {e}")
