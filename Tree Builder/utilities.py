import json
from classes import UiNode

from os import system
from queue import Queue

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel


def log_json(json_object):
    json_string = json.dumps(json_object, indent=4)

    console = Console()
    panel = Panel(json_string, title="", expand=True)
    console.print(Columns([panel]))


class Utils:
    def __init__():
        pass

    @staticmethod
    def filter_leaf_elements(design_data: dict, target_page: int = 0):
        leaf_nodes = []
        queue : Queue = Queue()
        
        page_data = design_data["document"]["children"][target_page]
        if page_data["type"] == "CANVAS":
            page_data = page_data["children"][0]

        queue.put(page_data)
        x_offset = int(page_data["absoluteBoundingBox"]["x"])
        y_offset = int(page_data["absoluteBoundingBox"]["y"])

        #TODO: Here We Will Have Multiple Pages, So We Need To Find A Way to handle that later
        while not queue.empty():
            top : dict = queue.get()
            if "children" in top.keys():
                for child in top["children"]:
                    queue.put(child)
            elif top["type"] != "LINE":
                top["absoluteBoundingBox"]["x"] = int(top["absoluteBoundingBox"]["x"]) - x_offset
                top["absoluteBoundingBox"]["y"] = int(top["absoluteBoundingBox"]["y"]) - y_offset
                leaf_nodes.append(top)
        
        return leaf_nodes

    @staticmethod
    def parse_figma_node(id: int, figma_node: dict):
        node = UiNode(id)
        node.name = figma_node["name"]
        node.figma_type = figma_node["type"]

        if node.figma_type != "TEXT":
            if len(figma_node["fills"]) > 0 and "color" in figma_node["fills"][0]:
                for element in ["r", "g", "b", "a"]:
                    node.bg_color[element] = float(figma_node["fills"][0]["color"][element])
            else:
                node.bg_color.a = 0

            if len(figma_node["strokes"]) > 0:
                for element in ["r", "g", "b", "a"]:
                    node.border.color[element] = float(figma_node["strokes"][0]["color"][element])
                node.border.style = figma_node["strokes"][0]["type"]
                node.border.weight = figma_node["strokeWeight"]  

                if "cornerRadius" in figma_node.keys():
                    node.border.radius = figma_node["cornerRadius"]
                else:
                    node.border.radius = 0
            else:
                node.border = None

        else:
            for element in ["r", "g", "b", "a"]:
                node.text_color[element] = float(figma_node["fills"][0]["color"][element])

        for element in ["x", "y"]:
            node.position[element] = figma_node["absoluteBoundingBox"][element]
        
        for element in ["width", "height"]:
            node.size[element] = figma_node["absoluteBoundingBox"][element]

        return node