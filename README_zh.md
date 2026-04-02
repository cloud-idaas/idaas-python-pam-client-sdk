# cloud-idaas-pam-client

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-Beta-orange)](https://pypi.org/project/cloud-idaas-pam-client/)

简体中文 | [English](README.md)

IDaaS (Identity as a Service) PAM (Privileged Access Management) 客户端 Python SDK，提供安全的 API 密钥和凭证管理功能。

## 功能特性

- **凭证管理**：支持检索 API 密钥、OAuth 认证令牌、JWT 认证令牌等凭证
- **认证令牌生命周期管理**：支持生成、查询、吊销、恢复和验证认证令牌

## 环境要求

- Python >= 3.9
- 依赖项：
  - cloud-idaas-core >= 0.0.4b0
  - alibabacloud-eiam-developerapi20220225 >= 1.6.0

## 安装

```bash
pip install cloud-idaas-pam-client
```

[最新版本](https://pypi.org/project/cloud-idaas-pam-client/)

## 快速开始

> **重要**：在使用本 SDK 之前，您需要完成 cloud-idaas-core-sdk 的初始化配置。
> 详情请参考：https://github.com/cloud-idaas/idaas-python-core-sdk/blob/main/README.md

### 1. 配置文件

在 `~/.cloud_idaas/client_config.json` 创建配置文件：

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

### 2. 环境变量

设置环境变量：

```bash
export IDAAS_CLIENT_SECRET="your-client-secret"
```

### 3. 代码中使用

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 获取 API 密钥
api_key = pam_client.get_api_key("your-credential-identifier")
print(f"API Key: {api_key}")
```

## API 参考

### get_api_key

用途：获取有效的 API 密钥。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| credential_identifier | str | 是 | 凭证的业务标识符。<br>* 获取方式：在 EIAM 控制台，导航至 凭证 -> 凭证，创建凭证时填写。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| api_key | str | 是 | API 密钥的内容。<br>* 注意：包含敏感信息。 |

### fetch_oauth_authentication_token

用途：获取有效的 OAuth 认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| credential_provider_identifier | str | 是 | 凭证提供商的业务标识符。<br>* 获取方式：在 EIAM 控制台，导航至 凭证 -> 凭证提供商，创建凭证提供商时填写。 |
| scope | str | 否 | OAuth 协议中的 scope。<br>* 多个 scope 应该用空格分隔。<br>* 最大长度为 256 个字符。<br>* 如果未指定，将使用创建凭证提供商时配置的 Scope 进行 OAuth 请求。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| access_token_value | str | 是 | 对应 OAuth AccessToken 响应中的 access_token。<br>* 注意：包含敏感信息。 |

### generate_jwt_authentication_token

用途：获取有效的 JWT 认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| credential_provider_identifier | str | 是 | 凭证提供商的业务标识符。<br>* 获取方式：在 EIAM 控制台，导航至 凭证 -> 凭证提供商，创建凭证提供商时填写。 |
| issuer | str | 否 | 对应 JWT 中的 `iss` 字段。<br>* 如果调用者希望颁发的 JWT 具有自定义颁发者，可以使用此字段。<br>* 如果未提供，默认为对应 JWT 凭证提供商的颁发者（表示 JWT 由 IDaaS EIAM 颁发）。<br>* 注意：如果在凭证提供商上配置了**颁发者白名单**，在颁发 JWT 时会验证提供的颁发者值是否在白名单中；如果不在白名单中，颁发将失败。 |
| subject | str | 是 | 对应 JWT 中的 `sub` 字段。 |
| audiences | List[str] | 是 | 对应 JWT 中的 `aud` 字段。<br>* 可以提供多个受众。<br>* 重要：不得以 IDaaS 保留的受众前缀开头：`urn:cloud:idaas`。 |
| custom_claims | Dict[str, Any] | 否 | 自定义 Claims。<br>* 注意：这是一个字典结构，其中 key 必须是 String，value 可以是任意类型。 |
| expiration | int | 否 | JWT 的有效期，单位为秒。<br>* 注意：如果未提供，将使用对应 JWT 提供商上配置的有效期。 |
| include_derived_short_token | bool | 否 | 是否生成派生短令牌。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| JwtTokenResponse | object | 是 | JWT 认证令牌响应的内容。 |
| └ authentication_token_id | str | 是 | 认证令牌 ID。 |
| └ consumer_type | str | 是 | 认证令牌的消费者类型。<br>* 枚举值：`custom`（自定义类型）、`application`（应用） |
| └ consumer_id | str | 是 | 认证令牌的消费者 ID。 |
| └ jwt_content | object | 是 | JWT 认证令牌的内容。 |
| └└ jwt_value | str | 是 | JWT 内容。<br>* 注意：包含敏感信息。 |
| └└ derived_short_token | str | 否 | JWT 的派生短令牌。<br>* 注意：与 JWT 认证令牌本身具有相同效果，用于解决 JWT 令牌长度在某些平台上不兼容的问题。<br>* 此字段本身也是**敏感字段**。 |

### obtain_jwt_authentication_token

用途：通过消费者 ID 和认证令牌 ID 获取 JWT 认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| consumer_id | str | 是 | 认证令牌的消费者 ID。 |
| authentication_token_id | str | 是 | 认证令牌 ID。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| jwt_content | object | 是 | JWT 认证令牌的内容。 |
| └ jwt_value | str | 是 | JWT 内容。<br>* 注意：包含敏感信息。 |
| └ derived_short_token | str | 否 | JWT 的派生短令牌。<br>* 注意：与 JWT 认证令牌本身具有相同效果，用于解决 JWT 令牌长度在某些平台上不兼容的问题。<br>* 此字段本身也是**敏感字段**。 |

### obtain_jwt_authentication_token_by_derived_short_token

用途：使用派生短令牌获取 JWT 认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| derived_short_token | str | 是 | JWT 认证令牌的派生短令牌。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| jwt_content | object | 是 | JWT 认证令牌的内容。 |
| └ jwt_value | str | 是 | JWT 内容。<br>* 注意：包含敏感信息。 |
| └ derived_short_token | str | 否 | JWT 的派生短令牌。<br>* 注意：与 JWT 认证令牌本身具有相同效果，用于解决 JWT 令牌长度在某些平台上不兼容的问题。<br>* 此字段本身也是**敏感字段**。 |

### list_authentication_tokens

用途：列举认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| consumer_id | str | 是 | 认证令牌的消费者 ID。 |
| credential_provider_id | str | 是 | 凭证提供商标识符。 |
| next_token | str | 否 | 下一页起始位置索引的分页令牌。 |
| max_results | int | 否 | 本次查询返回的最大记录数。 |
| revoked | bool | 否 | 认证令牌是否已被吊销。 |
| expired | bool | 否 | 认证令牌是否已过期。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| next_token_pageable_response | NextTokenPageableResponse | 是 | 分页查询结果。 |
| └ entities | List | 是 | 认证令牌列表。 |
| └└ instance_id | str | 是 | IDaaS 实例 ID。 |
| └└ authentication_token_id | str | 是 | 认证令牌 ID。 |
| └└ credential_provider_id | str | 是 | 凭证提供商标识符。 |
| └└ create_time | int | 否 | 认证令牌的创建时间，Unix 时间戳。 |
| └└ update_time | int | 否 | 认证令牌的最后更新时间，Unix 时间戳。 |
| └└ authentication_token_type | str | 是 | 认证令牌的类型。<br>* 枚举值：`oauth_access_token`、`jwt`。 |
| └└ revoked | bool | 是 | 认证令牌是否已被吊销。 |
| └└ creator_type | str | 是 | 认证令牌的创建者类型。<br>* 枚举值：`application` |
| └└ creator_id | str | 是 | 认证令牌的创建者 ID。 |
| └└ consumer_type | str | 是 | 认证令牌的消费者类型。<br>* 枚举值：`custom`（自定义类型）、`application`（应用） |
| └└ consumer_id | str | 是 | 认证令牌的消费者 ID。 |
| └└ expiration_time | int | 是 | 认证令牌的过期时间，Unix 时间戳。 |
| └ total_count | int | 是 | 认证令牌记录的总数。 |
| └ next_token | str | 是 | 下一页起始位置索引的分页令牌。 |
| └ max_results | int | 是 | 本次查询返回的最大记录数。 |

### validate_authentication_token

用途：验证认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| token | str | 是 | 认证令牌的明文。<br>* 注意：敏感字段<br>* 此字段可以接受 `jwt_content.jwt_value` 或 `jwt_content.derived_short_token`。JWT 令牌本身及其对应的派生短令牌都可以用于验证。 |
| token_type_hint | str | 否 | 关于令牌类型的提示。<br>* 目前不需要。 |

响应：

| **参数** | **类型** | **始终返回** | **说明** |
| --- | --- | --- | --- |
| active | bool | 是 | 认证令牌是否仍然有效。 |

### revoke_authentication_token

用途：吊销认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| token | str | 是 | 认证令牌的明文。<br>* 注意：敏感字段<br>* 此字段可以接受 `jwt_content.jwt_value` 或 `jwt_content.derived_short_token`。JWT 令牌本身及其对应的派生短令牌都可以用于吊销。 |
| token_type_hint | str | 否 | 关于令牌类型的提示。<br>* 目前不需要。 |

响应：
无

### revoke_authentication_token_by_consumer

用途：按消费者 ID 吊销认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| consumer_id | str | 是 | 认证令牌的消费者 ID。 |
| credential_provider_id | str | 是 | 凭证提供商标识符。 |

响应：
无

### reinstate_authentication_token

用途：恢复已吊销的认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| token | str | 是 | 认证令牌的明文。 |
| token_type_hint | str | 否 | 关于令牌类型的提示。<br>* 目前不需要。 |

响应：
无

### reinstate_authentication_token_by_consumer

用途：按消费者 ID 恢复认证令牌。

请求参数：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| consumer_id | str | 是 | 认证令牌的消费者 ID。 |
| credential_provider_id | str | 是 | 凭证提供商标识符。 |

响应：
无

## 完整示例

完整示例请参见 `samples/` 目录：

### 获取 API 密钥

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 获取 API 密钥
api_key = pam_client.get_api_key("your-credential-identifier")

print(f"API Key: {api_key}")
```

### 获取 API 密钥（基于令牌交换）

IDaaS 支持令牌交换功能。您可以使用在用户访问配置文件中配置的 M2M 客户端应用的 Access Token 来交换凭证的 Access Token，然后获取带有用户身份的 API 密钥。

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.core.constants import OAuth2Constants
from cloud_idaas.core.credential import IDaaSCredential
from cloud_idaas.core.implementation import StaticIDaaSCredentialProvider
from cloud_idaas.core.provider import IDaaSCredentialProvider, IDaaSTokenExchangeCredentialProvider
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 待交换的主体令牌
subject_token = "your-subject-token"

# 创建令牌交换凭证提供商
token_exchange_provider: IDaaSTokenExchangeCredentialProvider = (
    IDaaSCredentialProviderFactory.get_idaas_token_exchange_credential_provider()
)

# 获取凭证
credential: IDaaSCredential = token_exchange_provider.get_credential(
    subject_token=subject_token,
    requested_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
    subject_token_type=OAuth2Constants.ACCESS_TOKEN_TYPE_VALUE,
)

# 创建静态凭证提供商
credential_provider: IDaaSCredentialProvider = (
    StaticIDaaSCredentialProvider.builder()
    .credential(credential)
    .build()
)

# 通过静态凭证提供商创建 PAM 客户端
pam_client: IDaaSPamClient = (
    IDaaSPamClient.builder()
    .credential_provider(credential_provider)
    .build()
)

# 获取 API 密钥
api_key: str = pam_client.get_api_key("your-credential-identifier")

print(f"API Key: {api_key}")
```

### 获取 OAuth 认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 获取 OAuth 认证令牌
# 不带可选参数
token = pam_client.fetch_oauth_authentication_token("your-credential-identifier")
# 带可选参数
# token = pam_client.fetch_oauth_authentication_token(
#     "your-credential-identifier",
#     scope="your-scope"
# )

print(f"OAuth Token: {token}")
```

### 生成 JWT 认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient, JwtContent, JwtTokenResponse

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

audiences = ["audience1", "audience2"]

# 生成 JWT 认证令牌
# 不带可选参数
jwt_token_response: JwtTokenResponse = pam_client.generate_jwt_authentication_token(
    "credential-provider-identifier",
    "subject",
    audiences
)
# 带可选参数
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

### 获取 JWT 认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 通过消费者 ID 和认证令牌 ID 获取 JWT 认证令牌
jwt_content = pam_client.obtain_jwt_authentication_token(
    "your-consumer-id",
    "your-authentication-token-id"
)

print(f"JWT: {jwt_content.jwt_value}")
print(f"Derived Short Token: {jwt_content.derived_short_token}")
```

### 通过派生短令牌获取 JWT 认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 通过派生短令牌获取 JWT 认证令牌
jwt_content = pam_client.obtain_jwt_authentication_token_by_derived_short_token(
    "your-derived-short-token"
)

print(f"JWT: {jwt_content.jwt_value}")
print(f"Derived Short Token: {jwt_content.derived_short_token}")
```

### 列举认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient, AuthenticationToken, NextTokenPageableResponse

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 查询认证令牌列表
# 不带可选参数
tokens: NextTokenPageableResponse[AuthenticationToken] = pam_client.list_authentication_tokens(
    "consumer-id",
    "credential-provider-id"
)
# 带可选参数
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

### 验证认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 验证认证令牌
# 不带可选参数
is_valid = pam_client.validate_authentication_token("your-token")
# 带可选参数
# is_valid = pam_client.validate_authentication_token(
#     "your-token",
#     token_type_hint="your-token-type-hint"
# )

print(f"Token is valid: {is_valid}")
```

### 吊销指定认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 吊销指定认证令牌
# 不带可选参数
pam_client.revoke_authentication_token("your-token")
# 带可选参数
# pam_client.revoke_authentication_token(
#     "your-token",
#     token_type_hint="your-token-type-hint"
# )
```

### 按消费者吊销认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 按消费者吊销认证令牌
pam_client.revoke_authentication_token_by_consumer(
    "consumer-id",
    "credential-provider-id"
)
```

### 恢复已吊销的认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 恢复已吊销的认证令牌
# 不带可选参数
pam_client.reinstate_authentication_token("your-token")
# 带可选参数
# pam_client.reinstate_authentication_token(
#     "your-token",
#     token_type_hint="your-token-type-hint"
# )
```

### 按消费者恢复认证令牌

```python
from cloud_idaas.core import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient

# 初始化（自动加载配置文件）
IDaaSCredentialProviderFactory.init()

# 创建 PAM 客户端
pam_client = IDaaSPamClient()

# 按消费者恢复认证令牌
pam_client.reinstate_authentication_token_by_consumer(
    "consumer-id",
    "credential-provider-id"
)
```

## 支持与反馈

- **邮箱**：cloudidaas@list.alibaba-inc.com
- **问题反馈**：如有问题或建议请提交 Issue

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。
