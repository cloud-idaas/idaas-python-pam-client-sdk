"""
Example: IDaaSPamClient OAuth 3LO (Three-Legged OAuth) usage.

This example demonstrates the two usage modes introduced for OAuth 3LO:

1. Atomic mode: the caller orchestrates the flow by calling
   fetch_oauth_authentication_token_v2 and get_oauth_authorization_session,
   controlling the polling loop itself.
2. End-to-end mode: poll_oauth_authentication_token encapsulates the full flow
   (initiate authorization -> notify URL via callback -> poll -> fetch token).

Prerequisites:
1. Configure environment variables properly.
2. Create an OAuth (user_federation) credential provider in the IDaaS console.
3. In the 3LO scenario, the session APIs require a user-auth access token: the
   atomic sample below exchanges a subject token (token exchange) and builds
   the PAM client from the exchanged credential.
"""

import time

from cloud_idaas.core.constants import OAuth2Constants
from cloud_idaas.core.credential import IDaaSCredential
from cloud_idaas.core.factory import IDaaSCredentialProviderFactory
from cloud_idaas.core.implementation import StaticIDaaSCredentialProvider
from cloud_idaas.core.provider import IDaaSCredentialProvider, IDaaSTokenExchangeCredentialProvider
from cloud_idaas.pam_client import IDaaSPamClient, PamClientConstants


def run_atomic_3lo_sample(pam_client: IDaaSPamClient, credential_provider_identifier: str):
    """Atomic mode: caller orchestrates authorization and polling.

    The pam_client must carry a user-auth access token (e.g. built from a token
    exchange credential), as required by the 3LO session APIs.
    """
    print("\n" + "=" * 60)
    print("OAuth 3LO Atomic Mode")
    print("=" * 60)

    # 1. Initiate authorization (user_federation flow).
    response = pam_client.fetch_oauth_authentication_token_v2(
        credential_provider_identifier=credential_provider_identifier,
        authorization_flow=PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
    )
    if response is None:
        print("  No response returned")
        return

    # 2. Token already available -> use it directly.
    if response.has_oauth_access_token_content():
        print(f"  access_token: {response.oauth_access_token_content.access_token_value[:50]}...")
        return

    # 3. User authorization required -> show the URL and poll the session.
    session = response.oauth_authorization_session
    print(f"  Please open this URL in a browser to authorize:\n    {session.authorization_url}")

    while True:
        session_status = pam_client.get_oauth_authorization_session(session.session_uri)
        status = session_status.session_status if session_status else None
        print(f"  session status: {status}")
        if status == PamClientConstants.SESSION_STATUS_COMPLETED:
            break
        if status in (
            PamClientConstants.SESSION_STATUS_FAILED,
            PamClientConstants.SESSION_STATUS_EXPIRED,
        ):
            print(f"  authorization not completed: {status}")
            return
        time.sleep(PamClientConstants.DEFAULT_POLLING_INTERVAL_SECONDS)

    # 4. Authorization completed -> fetch the token.
    final = pam_client.fetch_oauth_authentication_token_v2(
        credential_provider_identifier=credential_provider_identifier,
        authorization_flow=PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
    )
    if final and final.has_oauth_access_token_content():
        print(f"  access_token: {final.oauth_access_token_content.access_token_value[:50]}...")


def run_end_to_end_3lo_sample(pam_client: IDaaSPamClient, credential_provider_identifier: str):
    """End-to-end mode: SDK handles the full flow; caller only shows the URL.

    The pam_client must carry a user-auth access token (e.g. built from a token
    exchange credential), as required by the 3LO session APIs.
    """
    print("\n" + "=" * 60)
    print("OAuth 3LO End-to-End Mode")
    print("=" * 60)

    def on_authorization_url(authorization_url: str):
        # Agent/CLI scenario: print the URL for the user to open in a browser.
        print(f"  Please open this URL in a browser to authorize:\n    {authorization_url}")

    response = pam_client.poll_oauth_authentication_token(
        credential_provider_identifier=credential_provider_identifier,
        on_authorization_url=on_authorization_url,
    )
    if response and response.has_oauth_access_token_content():
        print(f"  access_token: {response.oauth_access_token_content.access_token_value[:50]}...")
    else:
        print("  No OAuth authentication token obtained")


if __name__ == "__main__":
    # Initialize credential provider factory (required by the token exchange provider).
    IDaaSCredentialProviderFactory.init()

    # =====================================================
    # Please modify the following configuration parameters according to actual situation
    # =====================================================

    # OAuth (user_federation / 3LO) credential provider identifier.
    OAUTH_3LO_CREDENTIAL_PROVIDER_IDENTIFIER = "your_oauth_3lo_credential_provider_identifier"

    # Subject token to be exchanged for a user-auth access token.
    SUBJECT_TOKEN = "your_subject_token"

    # =====================================================
    # Build the PAM client from a user-auth credential (token exchange),
    # as required by the 3LO session APIs.
    # =====================================================

    token_exchange_provider: IDaaSTokenExchangeCredentialProvider = (
        IDaaSCredentialProviderFactory.get_idaas_token_exchange_credential_provider()
    )
    credential: IDaaSCredential = token_exchange_provider.get_credential(
        subject_token=SUBJECT_TOKEN,
        requested_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
        subject_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
    )
    credential_provider: IDaaSCredentialProvider = (
        StaticIDaaSCredentialProvider.builder().credential(credential).build()
    )
    pam_client: IDaaSPamClient = IDaaSPamClient.builder().credential_provider(credential_provider).build()

    # =====================================================
    # Run examples
    # =====================================================

    run_atomic_3lo_sample(pam_client, OAUTH_3LO_CREDENTIAL_PROVIDER_IDENTIFIER)
    run_end_to_end_3lo_sample(pam_client, OAUTH_3LO_CREDENTIAL_PROVIDER_IDENTIFIER)