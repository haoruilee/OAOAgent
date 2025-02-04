class EthAIError(Exception):
    """Base exception class for EthAI"""
    pass

class InvalidResponseError(EthAIError):
    """Exception raised when the response from the contract is invalid."""
    pass

class TransactionFailedError(EthAIError):
    """Exception raised when a transaction fails."""
    pass

class ContractInteractionError(EthAIError):
    """Exception raised for errors interacting with the smart contract."""
    pass
