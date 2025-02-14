import os
import requests
from dotenv import load_dotenv
from utilities import log_json
load_dotenv()

class API:
    @staticmethod
    def get_figma_tree(file_key: str, root_id: str | None):
        if root_id is None:
            url = "https://api.figma.com/v1/files/:file_key".replace(":file_key", file_key)
        else:
            url = "https://api.figma.com/v1/files/:file_key/nodes?ids=:id".replace(":file_key", file_key).replace(":id", root_id)

        headers = {
            "X-FIGMA-TOKEN": os.getenv('FIGMA_TOKEN')
        }
        response = requests.get(url = url, headers=headers)
        data = response.json()

        if root_id is not None:
            root_id = root_id.replace("-", ":")
            data = data["nodes"][root_id]
        print(data["document"]["name"])

        return data
        

# API.get_figma_tree(file_key="vWwqbxLzg15hcpOjoOhQ1M")