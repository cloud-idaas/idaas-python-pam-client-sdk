# cloud-idaas-pam-client

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-Beta-orange)](https://pypi.org/project/cloud-idaas-pam-client/)

[简体中文](README_zh.md)

Python SDK for IDaaS (Identity as a Service) PAM (Privileged Access Management) Client, providing secure API key and credential management capabilities.

## Features

- **Credential Management**: Support for retrieving API Keys, OAuth authentication tokens, JWT authentication tokens, and other credentials
- **OAuth 2LO / 3LO**: Support for both M2M (client credentials) and user federation (authorization code) flows, including an end-to-end 3LO authorization helper
- **Authentication Token Lifecycle Management**: Support for generating, querying, revoking, reinstating, and validating authentication tokens

## Requirements

- Python >= 3.9
- Dependencies:
  - cloud-idaas-core >= 0.0.4b0
  - alibabacloud-eiam-developerapi20220225 >= 1.8.0

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

> **Deprecated**: Use [fetch_oauth_authentication_token_v2](#fetch_oauth_authentication_token_v2) instead. This method only supports 2LO and returns just the access token string; its signature and return type are kept unchanged for backward compatibility.

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

### fetch_oauth_authentication_token_v2

Purpose: Retrieve a valid OAuth authentication token, covering both the 2LO (`m2m`) and 3LO (`user_federation`) flows, and returning a rich response object.
> **Note**: The 3LO scenario requires a user-auth Access Token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| credential_provider_identifier | str | Yes | The business identifier of the credential provider. |
| authorization_flow | str | Yes | The OAuth authorization flow type.<br>* Values: `PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M` (`m2m`, i.e. 2LO / client_credentials), `PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION` (`user_federation`, i.e. 3LO / authorization_code). |
| scope | str | No | The scope in OAuth protocol. Multiple scopes should be separated by spaces. |
| force_authentication | bool | No | Whether to force re-authorization, ignoring any existing valid token. Defaults to `false`. |
| custom_parameters | Dict[str, str] | No | Custom key-value pairs appended to the query parameters of the OAuth authorization URL.<br>* For example, Google's `access_type=offline` and `prompt=consent`. |

Response: `OAuthAuthenticationTokenResponse`

> `oauth_access_token_content` and `oauth_authorization_session` are **mutually exclusive** and never present at the same time. Use `has_oauth_access_token_content()` and `has_oauth_authorization_session()` to determine the current scenario.

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| instance_id | str | No | The IDaaS instance ID. |
| authentication_token_id | str | No | The authentication token ID. |
| credential_provider_id | str | No | The credential provider ID. |
| authentication_token_type | str | No | The authentication token type, with the value `oauth_access_token`. |
| revoked | bool | No | Whether the authentication token has been revoked. |
| creator_type / creator_id | str | No | The creator type / ID of the authentication token. |
| consumer_type / consumer_id | str | No | The consumer type / ID of the authentication token. |
| create_time / update_time / expiration_time | int | No | Creation / update / expiration time, as a Unix timestamp in milliseconds. |
| oauth_access_token_content | object | No | **Scenario 1: the token is already available**. |
| └ access_token_value | str | Yes | The access_token value.<br>* Note: Contains sensitive information. |
| └ token_type | str | No | The token_type, usually `Bearer`. |
| └ scope | str | No | The authorization scope. |
| oauth_authorization_session | object | No | **Scenario 2: user authorization is required** (3LO only). |
| └ session_id | str | Yes | The authorization session ID. |
| └ session_uri | str | Yes | The authorization session URI, used to query the session status later. |
| └ authorization_url | str | Yes | The URL that guides the user through authorization; pass it to the end user to open in a browser. |
| └ session_status | str | Yes | The authorization session status, which is `pending` at this point. |

### get_oauth_authorization_session

Purpose: Query the current status of an OAuth authorization session, used to orchestrate polling yourself in the 3LO atomic mode.

> **Note**: This API requires the Bearer Token to be a user-auth Access Token.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| session_uri | str | Yes | The authorization session URI, taken from `oauth_authorization_session.session_uri` returned by `fetch_oauth_authentication_token_v2`. |

Response: `OAuthAuthorizationSessionResponse`

| **Parameter** | **Type** | **Always Returned** | **Description** |
| --- | --- | --- | --- |
| instance_id | str | Yes | The IDaaS instance ID. |
| session_id | str | Yes | The authorization session ID. |
| session_uri | str | Yes | The authorization session URI. |
| session_status | str | Yes | The session status.<br>* Enum values: `pending` (waiting for user authorization), `callback_received` (authorization code received, exchanging the token), `completed` (authorization completed), `failed` (authorization failed), `expired` (session expired).<br>* Corresponding constants: `PamClientConstants.SESSION_STATUS_*`. |
| credential_provider_identifier | str | Yes | The business identifier of the credential provider. |
| consumer_type / consumer_id | str | Yes | The consumer type / ID. |
| creator_type / creator_id | str | Yes | The creator type / ID. |
| authorization_url | str | No | The authorization URL, returned when `session_status=pending`. |
| expiration_time | int | Yes | The session expiration time, as a Unix timestamp in milliseconds. |
| authentication_token_id | str | No | The associated authentication token ID, returned when `session_status=completed`. |
| error_code | str | No | The error code, returned when `session_status=failed`. |
| error_description | str | No | The error description, returned when `session_status=failed`. |

### poll_oauth_authentication_token

Purpose: The end-to-end 3LO method. It automatically performs the full flow internally: initiate authorization -> notify the authorization URL via callback -> poll and wait -> retrieve the token. Suitable for Agent / CLI scenarios without complex UI interaction.
> **Note**: This API requires the Bearer Token to be a user-auth Access Token.
>**Blocking behavior**: This is a synchronous, blocking method that blocks the calling thread while polling (up to 180 seconds). If you need non-blocking behavior, use the atomic methods to orchestrate the flow yourself, or call this method in a separate thread.

Request Parameters:

| **Parameter** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| credential_provider_identifier | str | Yes | The business identifier of the credential provider. |
| on_authorization_url | Callable[[str], None] | Yes | The authorization URL callback. When user authorization is required, the SDK invokes it once with the `authorization_url`.<br>* The caller decides how to deliver the URL to the end user (print to console, return to a frontend, open the system browser, etc.).<br>* Exceptions raised inside the callback are **propagated as-is** and are not wrapped by the SDK. |
| scope | str | No | The scope in OAuth protocol. Multiple scopes should be separated by spaces. |
| force_authentication | bool | No | Whether to force re-authorization, ignoring any existing valid token. Defaults to `false`. |
| custom_parameters | Dict[str, str] | No | Custom key-value pairs appended to the query parameters of the OAuth authorization URL. |
| max_polling_retries | int | No | The maximum number of polls, defaulting to 60.<br>* The polling interval is fixed at 3 seconds (not configurable).<br>* There is an internal hard timeout of 180 seconds: even if `polling interval x max retries` exceeds 180 seconds, polling stops after 180 seconds and a timeout exception is raised. |

Response: `OAuthAuthenticationTokenResponse` (same structure as `fetch_oauth_authentication_token_v2`)

> On success, the result **always contains** `oauth_access_token_content` and **never contains** `oauth_authorization_session` (the authorization logic has already been handled inside the method).

Exceptions:

| **Scenario** | **Exception** | **Error Code** |
| --- | --- | --- |
| Authorization session status is `failed` | `ClientException` | The server `error_code` is propagated (falls back to `authorization_failed` when empty) |
| Authorization session status is `expired` | `ClientException` | `authorization_session_expired` |
| Polling timed out / retries exhausted | `ClientException` | `polling_timeout` |
| Exception inside the callback | The original exception | Not wrapped, propagated as-is |

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

### Fetch OAuth Authentication Token (2LO, recommended)

Use `fetch_oauth_authentication_token_v2` and explicitly specify the `m2m` flow.

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient, PamClientConstants

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Create PAM Client
pam_client = IDaaSPamClient()

# Fetch OAuth authentication token (2LO / M2M)
response = pam_client.fetch_oauth_authentication_token_v2(
    credential_provider_identifier="your-credential-provider-identifier",
    authorization_flow=PamClientConstants.OAUTH_AUTHORIZATION_FLOW_M2M,
)

if response and response.has_oauth_access_token_content():
    print(f"Access Token: {response.oauth_access_token_content.access_token_value}")
    print(f"Token Type: {response.oauth_access_token_content.token_type}")
    print(f"Scope: {response.oauth_access_token_content.scope}")
```

### OAuth 3LO Authorization (end-to-end mode, recommended)

`poll_oauth_authentication_token` encapsulates the full 3LO flow: initiate authorization -> notify the authorization URL via callback -> poll and wait for the user to authorize -> retrieve the token. Suitable for Agent / CLI scenarios.

> The 3LO session APIs require a user-auth token, so the PAM client below is built via **token exchange**.

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.core.constants import OAuth2Constants
from cloud_idaas.core.credential import IDaaSCredential
from cloud_idaas.core.implementation import StaticIDaaSCredentialProvider
from cloud_idaas.core.provider import IDaaSCredentialProvider, IDaaSTokenExchangeCredentialProvider
from cloud_idaas.pam_client import IDaaSPamClient

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Obtain a user-auth credential via token exchange
token_exchange_provider: IDaaSTokenExchangeCredentialProvider = (
    IDaaSCredentialProviderFactory.get_idaas_token_exchange_credential_provider()
)
credential: IDaaSCredential = token_exchange_provider.get_credential(
    subject_token="your-subject-token",
    requested_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
    subject_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
)
credential_provider: IDaaSCredentialProvider = (
    StaticIDaaSCredentialProvider.builder().credential(credential).build()
)
pam_client: IDaaSPamClient = (
    IDaaSPamClient.builder().credential_provider(credential_provider).build()
)


# Authorization URL callback: the caller decides how to present it to the end user
def on_authorization_url(authorization_url: str):
    print(f"Please open the following URL in a browser to authorize:\n{authorization_url}")


# Retrieve the OAuth authentication token end-to-end (polling is handled internally)
response = pam_client.poll_oauth_authentication_token(
    credential_provider_identifier="your-oauth-3lo-credential-provider-identifier",
    on_authorization_url=on_authorization_url,
)
# With optional parameters
# response = pam_client.poll_oauth_authentication_token(
#     credential_provider_identifier="your-oauth-3lo-credential-provider-identifier",
#     on_authorization_url=on_authorization_url,
#     scope="your-scope",
#     force_authentication=True,
#     custom_parameters={"access_type": "offline"},
#     max_polling_retries=60,
# )

if response and response.has_oauth_access_token_content():
    print(f"Access Token: {response.oauth_access_token_content.access_token_value}")
```

### OAuth 3LO Authorization (atomic mode)

The caller orchestrates the polling logic, which suits scenarios that need custom UI interaction or a custom polling strategy.

```python
import time

from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.core.constants import OAuth2Constants
from cloud_idaas.core.credential import IDaaSCredential
from cloud_idaas.core.implementation import StaticIDaaSCredentialProvider
from cloud_idaas.core.provider import IDaaSCredentialProvider, IDaaSTokenExchangeCredentialProvider
from cloud_idaas.pam_client import IDaaSPamClient, PamClientConstants

# Initialize (automatically loads configuration file)
IDaaSCredentialProviderFactory.init()

# Obtain a user-auth credential via token exchange
token_exchange_provider: IDaaSTokenExchangeCredentialProvider = (
    IDaaSCredentialProviderFactory.get_idaas_token_exchange_credential_provider()
)
credential: IDaaSCredential = token_exchange_provider.get_credential(
    subject_token="your-subject-token",
    requested_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
    subject_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
)
credential_provider: IDaaSCredentialProvider = (
    StaticIDaaSCredentialProvider.builder().credential(credential).build()
)
pam_client: IDaaSPamClient = (
    IDaaSPamClient.builder().credential_provider(credential_provider).build()
)

credential_provider_identifier = "your-oauth-3lo-credential-provider-identifier"

# 1. Initiate authorization (user_federation flow)
response = pam_client.fetch_oauth_authentication_token_v2(
    credential_provider_identifier=credential_provider_identifier,
    authorization_flow=PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
)

if response.has_oauth_access_token_content():
    # 2. The token is already available, use it directly
    print(f"Access Token: {response.oauth_access_token_content.access_token_value}")
else:
    # 3. User authorization is required: show the URL and poll the session status
    session = response.oauth_authorization_session
    print(f"Please open the following URL in a browser to authorize:\n{session.authorization_url}")

    while True:
        session_response = pam_client.get_oauth_authorization_session(session.session_uri)
        status = session_response.session_status
        print(f"Authorization session status: {status}")
        if status == PamClientConstants.SESSION_STATUS_COMPLETED:
            break
        if status in (
            PamClientConstants.SESSION_STATUS_FAILED,
            PamClientConstants.SESSION_STATUS_EXPIRED,
        ):
            raise RuntimeError(f"Authorization not completed: {status}")
        time.sleep(PamClientConstants.DEFAULT_POLLING_INTERVAL_SECONDS)

    # 4. Authorization completed, fetch the token again
    final = pam_client.fetch_oauth_authentication_token_v2(
        credential_provider_identifier=credential_provider_identifier,
        authorization_flow=PamClientConstants.OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION,
    )
    print(f"Access Token: {final.oauth_access_token_content.access_token_value}")
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
