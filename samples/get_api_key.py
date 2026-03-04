import time

import dotenv
from cloud_idaas.core.factory import IDaaSCredentialProviderFactory

from cloud_idaas.pam_client import IDaaSPamClient


def loopSample():
    while True:
        pam_client = IDaaSPamClient()
        api_key = pam_client.get_api_key("dashscope_api_key")
        print(f"Api Key: {api_key}")
        time.sleep(10)

if __name__ == "__main__":
    dotenv.load_dotenv(dotenv_path="./Env/dot_envs/api_key.env")
    IDaaSCredentialProviderFactory.init()
    loopSample()
