import json
from classes import UiNode

from os import system
from queue import Queue

from math import degrees, cos, sin
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel


def log_json(json_object):
    json_string = json.dumps(json_object, indent=4)

    console = Console()
    panel = Panel(json_string, title="", expand=True)
    console.print(Columns([panel]))


class Utils:
    def __init__(self):
        self.counter = 0
        self.leaf_nodes = []
        self.grouping_nodes = []
        pass

    @staticmethod
    def filter_leaf_elements(design_data: dict, target_page: int = 0):
        leaf_nodes = []
        stack = []
        
        page_data = design_data["document"]
        if page_data["type"] == "CANVAS":
            page_data = page_data["children"][0]

        stack.append((page_data, None, 0))
        x_offset = int(page_data["absoluteBoundingBox"]["x"])
        y_offset = int(page_data["absoluteBoundingBox"]["y"])

        #TODO: Here We Will Have Multiple Pages, So We Need To Find A Way to handle that later
        children_count = {}
        glob_count = 0
        while len(stack) > 0:
            top, parent, depth = stack[-1]
            stack.pop()

            if glob_count == 122:
                "hre"
            
            if parent not in children_count: children_count[parent] = 0
            is_leaf = "children" not in top.keys() or len(top["children"]) == 0

            if is_leaf:
                id = glob_count
                children_count[parent] += 1
            elif top["id"] not in children_count:
                stack.append((top, parent, depth))
                for child in top["children"]:
                    stack.append((child, top["id"], depth + 1))
                continue
            else:
                children_count[parent] += children_count[top["id"]] + 1
                id = glob_count + children_count[top["id"]]

            top["absoluteBoundingBox"]["x"] = int(top["absoluteBoundingBox"]["x"]) - x_offset
            top["absoluteBoundingBox"]["y"] = int(top["absoluteBoundingBox"]["y"]) - y_offset
            top["id"] = id
            leaf_nodes.append(top)
            glob_count += 1

        # leaf_nodes.sort(key=lambda node: int(node["id"].split(":")[1]))
        # for node in leaf_nodes:
        #     print(node["name"], " ", node["id"])
        # quit()
        return leaf_nodes

    @staticmethod
    def parse_figma_node(figma_node: dict):
        node = UiNode(figma_node["id"])
        node.name = figma_node["name"]
        node.figma_type = figma_node["type"]

        if node.figma_type == "LINE":
            node.rotation = figma_node["rotation"]

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