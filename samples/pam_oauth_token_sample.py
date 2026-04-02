"""
Example: Testing IDaaSPamClient New Interfaces

This example demonstrates the usage of the following APIs:
1. fetch_oauth_authentication_token - Fetch OAuth authentication token
2. generate_jwt_authentication_token - Generate JWT authentication token
3. obtain_jwt_authentication_token - Obtain JWT by consumer ID and authentication token ID
4. obtain_jwt_authentication_token_by_derived_short_token - Query JWT using derived short token
5. list_authentication_tokens - List authentication tokens
6. validate_authentication_token - Validate authentication token
7. revoke_authentication_token - Revoke authentication token
8. reinstate_authentication_token - Reinstate authentication token

Prerequisites:
1. Configure environment variables properly
2. Create corresponding credential providers in IDaaS console
"""

from cloud_idaas.core.factory import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient, JwtTokenResponse


def test_fetch_oauth_authentication_token(pam_client: IDaaSPamClient, credential_provider_identifier: str):
    """Test fetching OAuth authentication token"""
    print("\n=== 1. Fetch OAuth Authentication Token ===")
    access_token = pam_client.fetch_oauth_authentication_token(
        credential_provider_identifier=credential_provider_identifier,
        scope=None,  # Use default scope
    )
    if access_token:
        print(f"  access_token: {access_token[:50]}...")
    else:
        print("  No OAuth authentication token obtained")
    return access_token


def test_generate_jwt_authentication_token(
    pam_client: IDaaSPamClient, credential_provider_identifier: str, consumer_id: str
):
    """Test generating JWT authentication token

    Args:
        consumer_id: Used as the JWT subject (user identifier)
    """
    print("\n=== 2. Generate JWT Authentication Token ===")
    print(f"  Using consumer_id as subject: {consumer_id}")
    jwt_response: JwtTokenResponse = pam_client.generate_jwt_authentication_token(
        credential_provider_identifier=credential_provider_identifier,
        subject=consumer_id,  # Use consumer_id as subject
        audiences=["https://api.example.com"],
        issuer="https://idaas.example.com",
        custom_claims={"role": "admin", "department": "engineering"},
        expiration=3600,  # 1 hour validity
        include_derived_short_token=True,
    )
    if jwt_response:
        print(f"  authentication_token_id: {jwt_response.authentication_token_id}")
        print(f"  consumer_type: {jwt_response.consumer_type}")
        print(f"  consumer_id: {jwt_response.consumer_id}")
        print(f"  jwt_value: {jwt_response.jwt_content.jwt_value[:80]}...")
        print(f"  derived_short_token: {jwt_response.jwt_content.derived_short_token}")
    else:
        print("  Failed to generate JWT authentication token")
    return jwt_response


def test_obtain_jwt_authentication_token(pam_client: IDaaSPamClient, consumer_id: str, authentication_token_id: str):
    """Test obtaining JWT authentication token by consumer ID and authentication token ID"""
    print("\n=== 3. Obtain JWT by Consumer ID and Authentication Token ID ===")
    jwt_content = pam_client.obtain_jwt_authentication_token(
        consumer_id=consumer_id,
        authentication_token_id=authentication_token_id,
    )
    if jwt_content:
        print(f"  jwt_value: {jwt_content.jwt_value[:80]}...")
        print(f"  derived_short_token: {jwt_content.derived_short_token}")
    else:
        print("  No JWT found")
    return jwt_content


def test_obtain_jwt_by_derived_short_token(pam_client: IDaaSPamClient, derived_short_token: str):
    """Test querying JWT using derived short token"""
    print("\n=== 4. Query JWT Using Derived Short Token ===")
    jwt_content = pam_client.obtain_jwt_authentication_token_by_derived_short_token(
        derived_short_token=derived_short_token,
    )
    if jwt_content:
        print(f"  jwt_value: {jwt_content.jwt_value[:80]}...")
        print(f"  derived_short_token: {jwt_content.derived_short_token}")
    else:
        print("  No JWT found")
    return jwt_content


def test_list_authentication_tokens(pam_client: IDaaSPamClient, credential_provider_identifier: str, consumer_id: str):
    """Test listing authentication tokens with pagination

    Args:
        consumer_id: Consumer/user identifier for querying specific user's tokens
    """
    print("\n=== 5. List Authentication Tokens ===")
    print("  Query parameters:")
    print(f"    - credential_provider_identifier: {credential_provider_identifier}")
    print(f"    - consumer_id: {consumer_id} (consumer/user identifier)")

    # First page
    print("\n  Fetching first page...")
    result = pam_client.list_authentication_tokens(
        credential_provider_identifier=credential_provider_identifier,
        consumer_id=consumer_id,
        max_results=2,  # 2 items per page for pagination testing
        revoked=False,
        expired=False,
    )
    if not result:
        print("  No authentication token list found")
        return None

    print("  Results:")
    print(f"    - total_count: {result.total_count} (total tokens for this user)")
    print(f"    - max_results: {result.max_results}")
    print(f"    - entities count: {len(result.entities)} (items in this page)")
    print(f"    - next_token: {result.next_token}")

    for i, token in enumerate(result.entities):
        print(f"    [{i}] token_id: {token.authentication_token_id}")
        print(f"        consumer_id: {token.consumer_id} (owner)")
        print(f"        type: {token.authentication_token_type}")
        print(f"        revoked: {token.revoked}")

    # Test pagination if there is a next page
    if result.next_token:
        print("\n  Fetching second page (using next_token)...")
        result_page2 = pam_client.list_authentication_tokens(
            credential_provider_identifier=credential_provider_identifier,
            consumer_id=consumer_id,
            max_results=2,
            next_token=result.next_token,
            revoked=False,
            expired=False,
        )
        if result_page2:
            print(f"  entities count: {len(result_page2.entities)}")
            print(f"  next_token: {result_page2.next_token}")
            for i, token in enumerate(result_page2.entities):
                print(f"    [{i}] token_id: {token.authentication_token_id}")
                print(f"        consumer_id: {token.consumer_id}")
                print(f"        type: {token.authentication_token_type}")

    return result


def test_validate_authentication_token(pam_client: IDaaSPamClient, token: str):
    """Test validating authentication token"""
    print("\n=== 6. Validate Authentication Token ===")
    is_active = pam_client.validate_authentication_token(token=token)
    print(f"  active: {is_active}")
    return is_active


def test_revoke_authentication_token(pam_client: IDaaSPamClient, token: str):
    """Test revoking authentication token"""
    print("\n=== 7. Revoke Authentication Token ===")
    try:
        pam_client.revoke_authentication_token(token=token)
        print("  Revoke successful")
        return True
    except Exception as e:
        print(f"  Revoke failed: {e}")
        return False


def test_reinstate_authentication_token(pam_client: IDaaSPamClient, token: str):
    """Test reinstating authentication token"""
    print("\n=== 8. Reinstate Authentication Token ===")
    try:
        pam_client.reinstate_authentication_token(token=token)
        print("  Reinstate successful")
        return True
    except Exception as e:
        print(f"  Reinstate failed: {e}")
        return False


def run_jwt_flow_sample(pam_client: IDaaSPamClient, credential_provider_identifier: str, consumer_id: str):
    """
    Complete JWT flow example:
    Generate -> Obtain by ID -> Obtain by short token -> Validate -> List -> Revoke -> Validate -> Reinstate -> Validate

    Args:
        credential_provider_identifier: JWT credential provider identifier
        consumer_id: Consumer/user identifier (subject) for identifying token owner
    """
    print("\n" + "=" * 60)
    print("JWT Complete Flow Test")
    print("=" * 60)
    print("Test parameters:")
    print(f"  - credential_provider_identifier: {credential_provider_identifier}")
    print(f"  - consumer_id (user identifier): {consumer_id}")

    # 1. Generate JWT (using consumer_id as subject)
    jwt_response = test_generate_jwt_authentication_token(pam_client, credential_provider_identifier, consumer_id)
    if not jwt_response:
        print("JWT generation failed, terminating test")
        return

    jwt_token = jwt_response.jwt_content.jwt_value
    derived_short_token = jwt_response.jwt_content.derived_short_token
    authentication_token_id = jwt_response.authentication_token_id
    token_consumer_id = jwt_response.consumer_id

    # 2. Obtain JWT by consumer ID and authentication token ID
    if authentication_token_id and token_consumer_id:
        test_obtain_jwt_authentication_token(pam_client, token_consumer_id, authentication_token_id)

    # 3. Query JWT using derived short token
    if derived_short_token:
        test_obtain_jwt_by_derived_short_token(pam_client, derived_short_token)

    # 4. Validate token (should be True)
    test_validate_authentication_token(pam_client, jwt_token)

    # 5. List tokens
    test_list_authentication_tokens(pam_client, credential_provider_identifier, consumer_id)

    # 6. Revoke token
    test_revoke_authentication_token(pam_client, jwt_token)

    # 7. Validate again (should be False)
    test_validate_authentication_token(pam_client, jwt_token)

    # 8. Reinstate token
    test_reinstate_authentication_token(pam_client, jwt_token)

    # 9. Final validation (should be True)
    test_validate_authentication_token(pam_client, jwt_token)

    print("\n" + "=" * 60)
    print("JWT flow test completed")
    print("=" * 60)


def run_oauth_sample(pam_client: IDaaSPamClient, credential_provider_identifier: str):
    """OAuth related interfaces test"""
    print("\n" + "=" * 60)
    print("OAuth Interface Test")
    print("=" * 60)

    # Fetch OAuth authentication token
    test_fetch_oauth_authentication_token(pam_client, credential_provider_identifier)

    print("\n" + "=" * 60)
    print("OAuth interface test completed")
    print("=" * 60)


if __name__ == "__main__":
    # Initialize credential provider factory
    IDaaSCredentialProviderFactory.init()

    # Create PAM client
    pam_client = IDaaSPamClient()

    # =====================================================
    # Please modify the following configuration parameters according to actual situation
    # =====================================================

    # OAuth credential provider identifier (for OAuth Token related interfaces)
    OAUTH_CREDENTIAL_PROVIDER_IDENTIFIER = "your_oauth_credential_provider_identifier"

    # JWT credential provider identifier (for JWT Token related interfaces)
    JWT_CREDENTIAL_PROVIDER_IDENTIFIER = "your_jwt_credential_provider_identifier"

    # Consumer ID (for list_authentication_tokens)
    CONSUMER_ID = "your-consumer-id"

    # =====================================================
    # Run examples
    # =====================================================

    # Test OAuth related interfaces
    run_oauth_sample(pam_client, OAUTH_CREDENTIAL_PROVIDER_IDENTIFIER)

    # Test JWT complete flow
    run_jwt_flow_sample(pam_client, JWT_CREDENTIAL_PROVIDER_IDENTIFIER, CONSUMER_ID)
