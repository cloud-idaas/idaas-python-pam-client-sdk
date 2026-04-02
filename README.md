# cloud-idaas-pam-client

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-Beta-orange)](https://pypi.org/project/cloud-idaas-pam-client/)

[简体中文](README_zh.md)

Python SDK for IDaaS (Identity as a Service) PAM (Privileged Access Management) Client, providing secure API key and credential management capabilities.

## Features

- **Credential Management**: Support for retrieving API Keys, OAuth authentication tokens, JWT authentication tokens, and other credentials
- **Authentication Token Lifecycle Management**: Support for generating, querying, revoking, reinstating, and validating authentication tokens

## Requirements

- Python >= 3.9
- Dependencies:
  - cloud-idaas-core >= 0.0.4b0
  - alibabacloud-eiam-developerapi20220225 >= 1.6.0

## Installation

```bash
pip install cloud-idaas-pam-client
```

[Latest Version](https://pypi.org/project/cloud-idaas-pam-client/)

## Quick Start

> **Important**: Before using this SDK, you need to complete the initialization configuration of cloud-idaas-core-sdk.
> For details, please refer to: https://github.com/cloud-idaas/idaas-python-core-sdk/blob/main/README.md

### 1. Configuration File

Create a configuration file at `~/.cloud_idaas/client_config.json`:

```json
{
    "idaasInstanceId": "your-idaas-instance-id",
    "clientId": "your-client-id",
    "issuer": "your-idaas-issuer-url",
    "tokenEndpoint": "your-idaas-token-endpoint",
    "scope": "your-requested-scope",
    "developerApiEndpoint": "your-developer-api-endpoint",
    "authnConfiguration": {
        "identityType": "CLIENT",
        "authnMethod": "CLIENT_SECRET_POST",
        "clientSecretEnvVarName": "IDAAS_CLIENT_SECRET"
    }
}
```

### 2. Environment Variables

Set the environment variable:

```bash
export IDAAS_CLIENT_SECRET="your-client-secret"
```

### 3. Usage in Code

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Get API Key
api_key = pam_client.get_api_key("your-credential-identifier")
print(f"API Key: {api_key}")
```

## API Reference

### get_api_key

Purpose: Retrieve a valid API Key.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| credential_identifier | str | Yes | The business identifier of the credential.<br>* How to obtain: In the EIAM Console, navigate to Credential -> Credential, and fill in when creating a credential. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| api_key | str | Yes | The content of the API Key.<br>* Note: Contains sensitive information. |

### fetch_oauth_authentication_token

Purpose: Retrieve a valid OAuth authentication token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| credential_provider_identifier | str | Yes | The business identifier of the credential provider.<br>* How to obtain: In the EIAM Console, navigate to Credential -> Credential Provider, and fill in when creating a credential provider. |
| scope | str | No | The scope in OAuth protocol.<br>* Multiple scopes should be separated by spaces. <br>* Maximum length is 256 characters. <br>* If not specified, the Scope configured when creating the credential provider will be used for the OAuth request. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| access_token_value | str | Yes | Corresponds to the access_token in the OAuth AccessToken response.<br>* Note: Contains sensitive information. |

### generate_jwt_authentication_token

Purpose: Retrieve a valid JWT authentication token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| credential_provider_identifier | str | Yes | The business identifier of the credential provider.<br>* How to obtain: In the EIAM Console, navigate to Credential -> Credential Provider, and fill in when creating a credential provider. |
| issuer | str | No | Corresponds to the `iss` field in JWT.<br>* If the caller wants the issued JWT to have a custom issuer, this field can be used.<br>* If not provided, defaults to the issuer of the corresponding JWT credential provider (indicating the JWT is issued by IDaaS EIAM).<br>* Note: If an **issuer whitelist** is configured on the credential provider, the provided issuer value will be validated against the whitelist during JWT issuance; if not in the whitelist, issuance will fail. |
| subject | str | Yes | Corresponds to the `sub` field in JWT. |
| audiences | List[str] | Yes | Corresponds to the `aud` field in JWT.<br>* Multiple audiences can be provided.<br>* Important: Must not start with IDaaS reserved audience prefix: `urn:cloud:idaas`. |
| custom_claims | Dict[str, Any] | No | Custom Claims.<br>* Note: This is a dict structure where the key must be a String, and the value can be any type. |
| expiration | int | No | The validity period of the JWT in seconds.<br>* Note: If not provided, the validity period configured on the corresponding JWT provider will be used. |
| include_derived_short_token | bool | No | Whether to generate a derived short token. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| JwtTokenResponse | object | Yes | The content of the JWT authentication token response. |
| └ authentication_token_id | str | Yes | The authentication token ID. |
| └ consumer_type | str | Yes | The consumer type of the authentication token.<br>* Enum values: `custom` (custom type), `application` (application) |
| └ consumer_id | str | Yes | The consumer ID of the authentication token. |
| └ jwt_content | object | Yes | The content of the JWT authentication token. |
| └└ jwt_value | str | Yes | The JWT content.<br>* Note: Contains sensitive information. |
| └└ derived_short_token | str | No | The derived short token of the JWT.<br>* Note: Has the same effect as the JWT authentication token itself, used to solve the problem of JWT token length incompatibility on certain platforms.<br>* This field itself is also a **sensitive field**. |

### obtain_jwt_authentication_token

Purpose: Retrieve a JWT authentication token by consumer ID and authentication token ID.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| consumer_id | str | Yes | The consumer ID of the authentication token. |
| authentication_token_id | str | Yes | The authentication token ID. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| jwt_content | object | Yes | The content of the JWT authentication token. |
| └ jwt_value | str | Yes | The JWT content.<br>* Note: Contains sensitive information. |
| └ derived_short_token | str | No | The derived short token of the JWT.<br>* Note: Has the same effect as the JWT authentication token itself, used to solve the problem of JWT token length incompatibility on certain platforms.<br>* This field itself is also a **sensitive field**. |

### obtain_jwt_authentication_token_by_derived_short_token

Purpose: Retrieve a JWT authentication token using a derived short token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| derived_short_token | str | Yes | The derived short token of the JWT authentication token. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| jwt_content | object | Yes | The content of the JWT authentication token. |
| └ jwt_value | str | Yes | The JWT content.<br>* Note: Contains sensitive information. |
| └ derived_short_token | str | No | The derived short token of the JWT.<br>* Note: Has the same effect as the JWT authentication token itself, used to solve the problem of JWT token length incompatibility on certain platforms.<br>* This field itself is also a **sensitive field**. |

### list_authentication_tokens

Purpose: List authentication tokens.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| consumer_id | str | Yes | The consumer ID of the authentication token. |
| credential_provider_id | str | Yes | The credential provider identifier. |
| next_token | str | No | Pagination token for the next page starting position index. |
| max_results | int | No | Maximum number of records to return in this query. |
| revoked | bool | No | Whether the authentication token has been revoked. |
| expired | bool | No | Whether the authentication token has expired. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| next_token_pageable_response | NextTokenPageableResponse | Yes | Paginated query results. |
| └ entities | List | Yes | List of authentication tokens. |
| └└ instance_id | str | Yes | The IDaaS instance ID. |
| └└ authentication_token_id | str | Yes | The authentication token ID. |
| └└ credential_provider_id | str | Yes | The credential provider identifier. |
| └└ create_time | int | No | The creation time of the authentication token, Unix timestamp. |
| └└ update_time | int | No | The last update time of the authentication token, Unix timestamp. |
| └└ authentication_token_type | str | Yes | The type of the authentication token.<br>* Enum values: `oauth_access_token`, `jwt`. |
| └└ revoked | bool | Yes | Whether the authentication token has been revoked. |
| └└ creator_type | str | Yes | The creator type of the authentication token.<br>* Enum value: `application` |
| └└ creator_id | str | Yes | The creator ID of the authentication token. |
| └└ consumer_type | str | Yes | The consumer type of the authentication token.<br>* Enum values: `custom` (custom type), `application` (application) |
| └└ consumer_id | str | Yes | The consumer ID of the authentication token. |
| └└ expiration_time | int | Yes | The expiration time of the authentication token, Unix timestamp. |
| └ total_count | int | Yes | The total number of authentication token records. |
| └ next_token | str | Yes | Pagination token for the next page starting position index. |
| └ max_results | int | Yes | Maximum number of records returned in this query. |

### validate_authentication_token

Purpose: Validate an authentication token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| token | str | Yes | The plaintext of the authentication token.<br>* Note: Sensitive field<br>* This field can accept either `jwt_content.jwt_value` or `jwt_content.derived_short_token`. Both the JWT token itself and its corresponding derived short token can be used for validation. |
| token_type_hint | str | No | A hint about the type of the token.<br>* Currently not required. |

Response:

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| active | bool | Yes | Whether the authentication token is still valid. |

### revoke_authentication_token

Purpose: Revoke an authentication token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| token | str | Yes | The plaintext of the authentication token.<br>* Note: Sensitive field<br>* This field can accept either `jwt_content.jwt_value` or `jwt_content.derived_short_token`. Both the JWT token itself and its corresponding derived short token can be used for revocation. |
| token_type_hint | str | No | A hint about the type of the token.<br>* Currently not required. |

Response:
None

### revoke_authentication_token_by_consumer

Purpose: Revoke authentication tokens by consumer ID.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| consumer_id | str | Yes | The consumer ID of the authentication token. |
| credential_provider_id | str | Yes | The credential provider identifier. |

Response:
None

### reinstate_authentication_token

Purpose: Reinstate a revoked authentication token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| token | str | Yes | The plaintext of the authentication token. |
| token_type_hint | str | No | A hint about the type of the token.<br>* Currently not required. |

Response:
None

### reinstate_authentication_token_by_consumer

Purpose: Reinstate authentication tokens by consumer ID.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| consumer_id | str | Yes | The consumer ID of the authentication token. |
| credential_provider_id | str | Yes | The credential provider identifier. |

Response:
None

## Complete Examples

For complete examples, see the `samples/` directory:

### Get API Key

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Get API Key
api_key = pam_client.get_api_key("your-credential-identifier")

print(f"API Key: {api_key}")
```

### Get API Key (Based on Token Exchange)

IDaaS supports token exchange capabilities. You can use the Access Token of the M2M client application configured in the user access profile to exchange for the Access Token of a credential, and then obtain the API Key with user identity.

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.core.constants import OAuth2Constants
from cloud_idaas.core.credential import IDaaSCredential
from cloud_idaas.core.implementation import StaticIDaaSCredentialProvider
from cloud_idaas.core.provider import IDaaSCredentialProvider, IDaaSTokenExchangeCredentialProvider
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (auto-load configuration file)
IDaaSCredentialProviderFactory.init()

# Subject token to be exchanged
subject_token = "your-subject-token"

# Create Token Exchange credential provider
token_exchange_provider: IDaaSTokenExchangeCredentialProvider = (
    IDaaSCredentialProviderFactory.get_idaas_token_exchange_credential_provider()
)

# Get credential
credential: IDaaSCredential = token_exchange_provider.get_credential(
    subject_token=subject_token,
    requested_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
    subject_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
)

# Create static credential provider
credential_provider: IDaaSCredentialProvider = (
    StaticIDaaSCredentialProvider.builder()
    .credential(credential)
    .build()
)

# Create PAM Client through static credential provider
pam_client: IDaaSPamClient = (
    IDaaSPamClient.builder()
    .credential_provider(credential_provider)
    .build()
)

# Get API Key
api_key: str = pam_client.get_api_key("your-credential-identifier")

print(f"API Key: {api_key}")
```

### Fetch OAuth Authentication Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Get OAuth authentication token
# Without optional parameters
token = pam_client.fetch_oauth_authentication_token("your-credential-identifier")
# With optional parameters
# token = pam_client.fetch_oauth_authentication_token(
#     "your-credential-identifier",
#     scope="your-scope"
# )

print(f"OAuth Token: {token}")
```

### Generate JWT Authentication Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient, JwtContent, JwtTokenResponse

# Initialize (automatically load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

audiences = ["audience1", "audience2"]

# Generate JWT authentication token
# Without optional parameters
jwt_token_response: JwtTokenResponse = pam_client.generate_jwt_authentication_token(
    "credential-provider-identifier",
    "subject",
    audiences
)
# With optional parameters
# custom_claims = {"key": "value"}
# jwt_token_response: JwtTokenResponse = pam_client.generate_jwt_authentication_token(
#     "credential-provider-identifier",
#     "subject",
#     audiences,
#     issuer="issuer",
#     custom_claims=custom_claims,
#     expiration=3600,
#     include_derived_short_token=True
# )

print(f"Authentication Token Id: {jwt_token_response.authentication_token_id}")
print(f"Consumer Type: {jwt_token_response.consumer_type}")
print(f"Consumer ID: {jwt_token_response.consumer_id}")
print(f"JWT Token: {jwt_token_response.jwt_content.jwt_value}")
print(f"Derived Short Token: {jwt_token_response.jwt_content.derived_short_token}")
```

### Obtain JWT Authentication Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (auto-load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Obtain JWT authentication token by consumer ID and authentication token ID
jwt_content = pam_client.obtain_jwt_authentication_token(
    "your-consumer-id",
    "your-authentication-token-id"
)

print(f"JWT: {jwt_content.jwt_value}")
print(f"Derived Short Token: {jwt_content.derived_short_token}")
```

### Obtain JWT Authentication Token by Derived Short Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Obtain JWT authentication token by derived short token
jwt_content = pam_client.obtain_jwt_authentication_token_by_derived_short_token(
    "your-derived-short-token"
)

print(f"JWT: {jwt_content.jwt_value}")
print(f"Derived Short Token: {jwt_content.derived_short_token}")
```

### List Authentication Tokens

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient, AuthenticationToken, NextTokenPageableResponse

# Initialize (auto-load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Query authentication token list
# Without optional parameters
tokens: NextTokenPageableResponse[AuthenticationToken] = pam_client.list_authentication_tokens(
    "consumer-id",
    "credential-provider-id"
)
# With optional parameters
# tokens: NextTokenPageableResponse[AuthenticationToken] = pam_client.list_authentication_tokens(
#     "consumer-id",
#     "credential-provider-id",
#     next_token=None,
#     max_results=10,
#     revoked=False,
#     expired=False
# )

print(f"Total Count: {tokens.total_count}")
print(f"Next Token: {tokens.next_token}")
print(f"Max Results: {tokens.max_results}")
authentication_tokens = tokens.entities
for authentication_token in authentication_tokens:
    print(authentication_token.authentication_token_id)
    print(authentication_token.authentication_token_type)
    print(authentication_token.consumer_id)
    print(authentication_token.consumer_type)
    print(authentication_token.creator_id)
    print(authentication_token.creator_type)
    print(authentication_token.credential_provider_id)
```

### Validate Authentication Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (auto-load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Validate authentication token
# Without optional parameters
is_valid = pam_client.validate_authentication_token("your-token")
# With optional parameters
# is_valid = pam_client.validate_authentication_token(
#     "your-token",
#     token_type_hint="your-token-type-hint"
# )

print(f"Token is valid: {is_valid}")
```

### Revoke Specified Authentication Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Revoke the specified authentication token
# Without optional parameters
pam_client.revoke_authentication_token("your-token")
# With optional parameters
# pam_client.revoke_authentication_token(
#     "your-token",
#     token_type_hint="your-token-type-hint"
# )
```

### Revoke Authentication Token by Consumer

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Revoke authentication token by consumer
pam_client.revoke_authentication_token_by_consumer(
    "consumer-id",
    "credential-provider-id"
)
```

### Reinstate Revoked Authentication Token

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically load configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Reinstate the revoked authentication token
# Without optional parameters
pam_client.reinstate_authentication_token("your-token")
# With optional parameters
# pam_client.reinstate_authentication_token(
#     "your-token",
#     token_type_hint="your-token-type-hint"
# )
```

### Reinstate Authentication Token by Consumer

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Reinstate authentication token by consumer
pam_client.reinstate_authentication_token_by_consumer(
    "consumer-id",
    "credential-provider-id"
)
```

## Support and Feedback

- **Email**: cloudidaas@list.alibaba-inc.com
- **Issue Feedback**: Please submit an Issue if you have any questions or suggestions

## License

This project is licensed under the [Apache License 2.0](LICENSE).
