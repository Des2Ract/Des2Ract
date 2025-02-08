import os
from gateway import API
from utilities import Utils

class TreeBuilder:
    def __init__(self, figma_file_url: str):
        file_key = figma_file_url.replace(r"https://", "", 1).split("/")[int(os.getenv("FIGMA_FILE_KEY_INDEX"))]
        figma_json_file = API.get_figma_tree(file_key=file_key)
        leaf_nodes = Utils.filter_leaf_elements(figma_json_file)
        self.nodes = [ Utils.parse_figma_node(element) for element in leaf_nodes ]
        for node in self.nodes:
            node.log()
    

TreeBuilder(figma_file_url="https://www.figma.com/design/vWwqbxLzg15hcpOjoOhQ1M/qr-code-component?node-id=0-1468&p=f&t=MQzWnCigMSq2X0zb-0")