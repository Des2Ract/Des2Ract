import os
import requests
from dotenv import load_dotenv
load_dotenv()

class API:
    @staticmethod
    def get_figma_tree(file_key: str):
        url = "https://api.figma.com/v1/files/:file_key".replace(":file_key", file_key)
        headers = {
            "X-FIGMA-TOKEN": os.getenv('FIGMA_TOKEN')
        }
        response = requests.get(url = url, headers=headers)
        data = response.json()
        return data
        

# API.get_figma_tree(file_key="vWwqbxLzg15hcpOjoOhQ1M")