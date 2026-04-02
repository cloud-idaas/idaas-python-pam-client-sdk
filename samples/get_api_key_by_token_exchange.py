"""Sample code for getting API key using token exchange.

This sample demonstrates how to:
1. Initialize the credential provider factory (auto-loads configuration)
2. Create a token exchange credential provider
3. Exchange a subject token for credentials
4. Create a static credential provider with the exchanged credential
5. Create a PAM client and retrieve an API key
"""

from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.core.constants import OAuth2Constants
from cloud_idaas.core.credential import IDaaSCredential
from cloud_idaas.core.implementation import StaticIDaaSCredentialProvider
from cloud_idaas.core.provider import IDaaSCredentialProvider, IDaaSTokenExchangeCredentialProvider
from cloud_idaas.pam_client import IDaaSPamClient


def get_api_key_by_token_exchange(subject_token: str):
    """Get API key using token exchange flow."""
    # Initialize (auto-load configuration file)
    IDaaSCredentialProviderFactory.init()

    # Create Token Exchange credential provider
    token_exchange_provider: IDaaSTokenExchangeCredentialProvider = (
        IDaaSCredentialProviderFactory.get_idaas_token_exchange_credential_provider()
    )

    # Get credential by exchanging the subject token
    credential: IDaaSCredential = token_exchange_provider.get_credential(
        subject_token=subject_token,
        requested_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
        subject_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
    )

    # Create static credential provider with the exchanged credential
    credential_provider: IDaaSCredentialProvider = (
        StaticIDaaSCredentialProvider.builder().credential(credential).build()
    )

    # Create PAM Client through static credential provider
    pam_client: IDaaSPamClient = IDaaSPamClient.builder().credential_provider(credential_provider).build()

    # Get API Key
    api_key: str = pam_client.get_api_key("test_api_key")
    print(f"API Key: {api_key}")

    return api_key


if __name__ == "__main__":
    # Subject token to be exchanged
    subject_token = "your_subject_token"
    get_api_key_by_token_exchange(subject_token)
