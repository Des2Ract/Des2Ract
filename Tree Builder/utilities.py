import json
from classes import Node

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
    def filter_leaf_elements(page_data: dict):
        leaf_nodes = []
        queue : Queue = Queue()
        queue.put(page_data["document"])
        
        while not queue.empty():
            top : dict = queue.get()
            if "children" in top.keys():
                for child in top["children"]:
                    queue.put(child)
            else:
                leaf_nodes.append(top)
        
        return leaf_nodes

    @staticmethod
    def parse_figma_node(figma_node: dict):
        node = Node()
        node.name = figma_node["name"]
        node.figma_type = figma_node["type"]

        if node.figma_type != "TEXT":
            for element in ["r", "g", "b", "a"]:
                node.bg_color[element] = float(figma_node["fills"][0]["color"][element])

            if len(figma_node["strokes"]) > 0:
                for element in ["r", "g", "b", "a"]:
                    node.border.color[element] = float(figma_node["strokes"][0]["color"][element])
                node.border.style = figma_node["strokes"][0]["type"]
                node.border.weight = figma_node["strokeWeight"]
                node.border.radius = figma_node["cornerRadius"]
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