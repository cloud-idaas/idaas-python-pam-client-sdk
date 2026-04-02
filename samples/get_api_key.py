import time

from cloud_idaas.core.factory import IDaaSCredentialProviderFactory
from cloud_idaas.pam_client import IDaaSPamClient


def loop_sample():
    """Continuously fetch and print API key in a loop."""
    while True:
        pam_client = IDaaSPamClient()
        api_key = pam_client.get_api_key("test_api_key")
        print(f"Api Key: {api_key}")
        time.sleep(10)


if __name__ == "__main__":
    IDaaSCredentialProviderFactory.init()
    loop_sample()
