class PamClientConstants:
    """PAM client constants definition class

    Contains constant configurations used by PAM (Privileged Access Management) client
    """

    # IDaaS PAM Service scope value.
    # The ".all" grants the machine-to-machine client full authorization
    # to access all PAM resource servers within the specified scope.
    SCOPE = "urn:cloud:idaas:pam|.all"

    # HTTP success response status code
    STATUS_CODE_200 = 200

    # OAuth authorization flow types (SDK-side parameter for client validation only;
    # NOT sent to the server, which determines the actual flow by CredentialProvider config).
    OAUTH_AUTHORIZATION_FLOW_M2M = "m2m"  # Machine-to-Machine (2LO / client_credentials)
    OAUTH_AUTHORIZATION_FLOW_USER_FEDERATION = "user_federation"  # User federation (3LO / authorization_code)

    # OAuth 3LO authorization session statuses.
    SESSION_STATUS_PENDING = "pending"  # Waiting for the user to complete authorization in the browser
    SESSION_STATUS_CALLBACK_RECEIVED = "callback_received"  # Server received the code, exchanging token (transient)
    SESSION_STATUS_COMPLETED = "completed"  # Authorization completed, token is ready
    SESSION_STATUS_FAILED = "failed"  # Authorization failed (user denied or token exchange failed)
    SESSION_STATUS_EXPIRED = "expired"  # Authorization session expired

    # OAuth 3LO end-to-end polling strategy.
    DEFAULT_POLLING_INTERVAL_SECONDS = 3  # Fixed interval between polls (not configurable)
    DEFAULT_MAX_POLLING_RETRIES = 60  # Default maximum number of polls (configurable)
    MAX_POLLING_DURATION_SECONDS = 180  # Internal hard timeout upper bound (seconds)
