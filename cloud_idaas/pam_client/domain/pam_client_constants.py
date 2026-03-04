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
