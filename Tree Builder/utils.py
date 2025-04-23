import math
import json 
import re 

import numpy as np

from sklearn.cluster import DBSCAN
from queue import Queue

from anytree import Node, RenderTree

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel

from classes import Node as DesignNode

icons: dict[int, list[DesignNode]] = {}

staticIds = 5000
def generateId ():
    global staticIds
    staticIds += 1
    return staticIds

def log_json(json_object):
    json_string = json.dumps(json_object, indent=4)
    console = Console()
    panel = Panel(json_string, title="", expand=True)
    console.print(Columns([panel]))

def debug_tree(root: DesignNode):
    queue : Queue[DesignNode] = Queue()
    queue.put((root, Node(root, parent=None)))
    while not queue.empty():
        (top, prev_parent) = queue.get()
        for child in top.children:
            next_parent = Node(f"Child {child.name}", parent=prev_parent)
            queue.put((child, next_parent))
    
    # Render the tree
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name[:20]}")

def parseFigmaJsonFile(jsonFile: dict):
    extractedNodes = []
    
    page_data = jsonFile["document"]
    if page_data["type"] == "CANVAS": page_data = page_data["children"][0]
    x_offset = int(page_data["absoluteBoundingBox"]["x"])
    y_offset = int(page_data["absoluteBoundingBox"]["y"])

    stack = []
    stack.append((page_data, None, 0))

    nodeChildrenCount = {}
    globalCounter = 0
    while len(stack) > 0:
        top, parent, depth = stack[-1]
        stack.pop()
        
        if parent not in nodeChildrenCount: nodeChildrenCount[parent] = 0

        is_leaf = "children" not in top.keys() or len(top["children"]) == 0
        if is_leaf:
            id = globalCounter
            globalCounter += 1
            nodeChildrenCount[parent] += 1
        # if this parent was not traversed yet then explore its children 
        elif top["id"] not in nodeChildrenCount:
            stack.append((top, parent, depth))
            for child in top["children"]:
                stack.append((child, top["id"], depth + 1))
            continue
        # if its children was explored then place it behind them
        else:
            nodeChildrenCount[parent] += nodeChildrenCount[top["id"]] + 1
            id = globalCounter + nodeChildrenCount[top["id"]]
            globalCounter = id + 1 

        # shift coordinates to be relative to the page 
        top["absoluteBoundingBox"]["x"] = int(top["absoluteBoundingBox"]["x"]) - x_offset
        top["absoluteBoundingBox"]["y"] = int(top["absoluteBoundingBox"]["y"]) - y_offset
        top["id"] = id

        extractedNodes.append(top)

    return extractedNodes

def parseJsonNodes(jsonNodes: list[dict]):
    parsedNodes = []
    for jsonNode in jsonNodes:
        # if jsonNode["type"] in ["FRAME"]: continue
        node = DesignNode(jsonNode["id"])
        node.name = jsonNode["name"]
        node.figma_type = jsonNode["type"]
        node.rotation = jsonNode["rotation"] if "rotation" in jsonNode.keys() else 0
        
        if node.figma_type == "TEXT":
            node.text = jsonNode["characters"]

        if "fills" in jsonNode.keys() and len(jsonNode["fills"]) > 0:
            if "color" in jsonNode["fills"][0]:
                colorJson = jsonNode["fills"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(colorJson["a"])) 

                if node.figma_type == "TEXT":
                    node.textColor = color
                else:
                    node.bgColor = color
            if "imageRef" in jsonNode["fills"][0]:
                node.imageUrl = jsonNode["fills"][0]["imageRef"]
                node.imgScaleMode = jsonNode["fills"][0]["scaleMode"]
                node.name = "IMAGE " + str(node.id)

        if "backgrounds" in jsonNode.keys() and len(jsonNode["backgrounds"]) > 0:
            if "color" in jsonNode["backgrounds"][0]:
                colorJson = jsonNode["backgrounds"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(colorJson["a"])) 

                if node.figma_type == "TEXT":
                    node.textColor = color
                else:
                    node.bgColor = color
            if "imageRef" in jsonNode["backgrounds"][0]:
                node.imageUrl = jsonNode["backgrounds"][0]["imageRef"]
                node.imgScaleMode = jsonNode["backgrounds"][0]["scaleMode"]
                node.name = "IMAGE " + str(node.id)
        
        if "strokes" in jsonNode.keys() and len(jsonNode["strokes"]) > 0:
            if "color" in jsonNode["strokes"][0]:
                colorJson = jsonNode["strokes"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(colorJson["a"])) 
                node.borderColor = color
             
        if "cornerRadius" in jsonNode.keys():
            node.borderRadius = [float(jsonNode["cornerRadius"]) for _ in range(4)]

        node.x = jsonNode["absoluteBoundingBox"]["x"]
        node.y = jsonNode["absoluteBoundingBox"]["y"]
        node.width = jsonNode["absoluteBoundingBox"]["width"]
        node.height = jsonNode["absoluteBoundingBox"]["height"]
        
        parsedNodes.append(node)
    return parsedNodes


def parseTrainingJsonFile(jsonFile: dict):
    extractedNodes = []
    page_data = jsonFile
    stack = [page_data]
    
    ids = 0
    while len(stack) > 0:
        top = stack[-1]
        stack.pop()

        top["id"] = ids; ids += 1

        if "children" not in top.keys() or len(top["children"]) == 0:
            continue
        
        for child in top["children"]:
            stack.append(child)

        extractedNodes.append(top)

    return extractedNodes

def parseTrainingJsonNodes(jsonNodes: list[dict]):
    parsedNodes = []
    for jsonNode in jsonNodes:
        nodeDetails = jsonNode["node"]
        # if jsonNode["type"] in ["FRAME"]: continue
        node = DesignNode(jsonNode["id"])
        node.name = f"Node {jsonNode["id"]}"
        node.tag = jsonNode["tag"]
        node.figma_type = nodeDetails["type"]
        node.rotation = 0
        
        if node.figma_type == "TEXT":
            node.text = nodeDetails["characters"]

        if "fills" in nodeDetails.keys() and len(nodeDetails["fills"]) > 0:
            if "color" in nodeDetails["fills"][0]:
                colorJson = nodeDetails["fills"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(nodeDetails["fills"][0]["opacity"])) 

                if node.figma_type == "TEXT":
                    node.textColor = color
                else:
                    node.bgColor = color
            if "url" in nodeDetails["fills"][0]:
                node.imageUrl = nodeDetails["fills"][0]["url"]
                node.imgScaleMode = nodeDetails["fills"][0]["scaleMode"]
                node.name = "IMAGE " + str(node.id)

        if "backgrounds" in nodeDetails.keys() and len(nodeDetails["backgrounds"]) > 0:
            if "color" in nodeDetails["backgrounds"][0]:
                colorJson = nodeDetails["backgrounds"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(nodeDetails["backgrounds"][0]["opacity"])) 

                if node.figma_type == "TEXT":
                    node.textColor = color
                else:
                    node.bgColor = color
            if "url" in nodeDetails["backgrounds"][0]:
                node.imageUrl = nodeDetails["backgrounds"][0]["url"]
                node.imgScaleMode = nodeDetails["backgrounds"][0]["scaleMode"]
                node.name = "IMAGE " + str(node.id)
        
        if "strokes" in nodeDetails.keys() and len(nodeDetails["strokes"]) > 0:
            if "color" in nodeDetails["strokes"][0]:
                colorJson = nodeDetails["strokes"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(nodeDetails["strokes"][0]["opacity"])) 
                node.borderColor = color
             
        if "topLeftRadius" in nodeDetails.keys():
            node.borderRadius[0] = nodeDetails["topLeftRadius"]
        if "topRightRadius" in nodeDetails.keys():
            node.borderRadius[1] = nodeDetails["topRightRadius"]
        if "bottomRightRadius" in nodeDetails.keys(): 
            node.borderRadius[2] = nodeDetails["bottomRightRadius"]
        if "bottomLeftRadius" in nodeDetails.keys():
            node.borderRadius[3] = nodeDetails["bottomLeftRadius"]

        node.x = nodeDetails["x"]
        node.y = nodeDetails["y"]
        node.width = nodeDetails["width"]
        node.height = nodeDetails["height"]
        
        parsedNodes.append(node)
    return parsedNodes


def normalizeTexts(root: DesignNode):
    lettersRegex = r"\b[^a-zA-Z\s]*[a-zA-Z]+[^a-zA-Z\s]*\b"
    numbersRegex = r"[0-9]+"
    spacesRegex = r"[ \t]+"
    root.normalizedText = re.sub(lettersRegex, "W", root.text)
    root.normalizedText = re.sub(numbersRegex, "D", root.normalizedText)
    root.normalizedText = re.sub(spacesRegex,  "S", root.normalizedText)

def normalizeNodes(root: DesignNode):
    global icons
    if len(root.children) == 0:
        if root.isText():
            normalizeTexts(root)
            return False, True
        else:
            return root.isIconPart(), False
    
    allChildrenIconsPart = True
    textFound = False
    for child in root.children:
        isChildIcon, childHasText = normalizeNodes(child)
        allChildrenIconsPart &= isChildIcon
        textFound |= childHasText

    # if the current node contains only a set of vectors
    # or if it has no text children with pretty small area (TODO: we may add some exclusion for the checkboxes and change this 1000)
    if allChildrenIconsPart or ( not textFound and root.area() < 1000 ):
        vectorElements = root.children.copy()
        coordinates = np.array( [ vector.center() for vector in vectorElements ] )

        # cluster the whole children into clusters where each cluster will represent one icon
        clustering = DBSCAN(eps=25, min_samples=1, ).fit(coordinates)
        labels = clustering.labels_

        # extract these clusters
        clusters : dict[str, list] = {}
        for node, label in zip(vectorElements, labels):
            if label not in clusters: clusters[label] = []
            clusters[label].append(node)

        # store this icon components into some memory and erase it from the node children
        for _, cluster_vectors in clusters.items():
            iconId = len(icons.keys())
            icons[iconId] = cluster_vectors
            root.iconChildren.append(iconId) # a reference to this icon

        # set the type of this node to ICON and clear its children
        root.name = "ICON " + "-".join([ str(iconId) for iconId in root.iconChildren ])  
        root.children = []
    
    return allChildrenIconsPart, textFound

def getVerticalAlignmentLines(root: DesignNode):
    lines = set()
    for child in root.children:
        lines.add(child.left())
        lines.add(child.right())
    return lines

def getHorizontalAlignmentLines(root: DesignNode):
    lines = set()
    for child in root.children:
        lines.add(child.top())
        lines.add(child.bottom())
    return lines

def getNodesBetween(root: DesignNode, left: float, right: float, top: float, bottom: float):
    nodes = []
    for child in root.children:
        if child.left() >= left and child.right() <= right and child.top() >= top and child.bottom() <= bottom:
            nodes.append(child)
    return nodes

def getNodeDirection(root : Node):
    # this should make something that tells me that this node should be row based or column based
    rootWidth = max(root.calculatedWidth(), 1e-9)
    rootHeight = max(root.calculatedHeight(), 1e-9)
    for child in root.children:
        if child.calculatedWidth() / rootWidth > 0.9:
            return "rows"
        if child.calculatedHeight() / rootHeight > 0.9:
            return "columns"
        
    xPos = root.allXPos()
    yPos = root.allYPos()

    stdX : list[int] = np.std(xPos) if len(xPos) > 1 else 0 
    stdY : list[int] = np.std(yPos) if len(yPos) > 1 else 0
    
    normStdX = (stdX / rootWidth) if rootWidth > 0 else 0
    normStdY = (stdY / rootHeight) if rootHeight > 0 else 0

    if normStdX > normStdY:
        return "columns"
    else:
        return "rows"

def to_dict(node: DesignNode, images: dict[str, str]):
    return {
        "tag": node.tag,
        "name": node.name,
        "node" : {
            "type": node.figma_type,
            "x": node.left(),
            "y": node.top(),
            "width": node.calculatedWidth(),
            "height": node.calculatedHeight(),
            "fills": [
                {
                    "blendMode": "NORMAL",  
                    "type": "IMAGE" if node.name.startswith("IMAGE") else "SOLID",
                    "color": {
                        "r": node.bgColor[0] if not node.isText() else node.textColor[0],
                        "g": node.bgColor[1] if not node.isText() else node.textColor[1],
                        "b": node.bgColor[2] if not node.isText() else node.textColor[2],
                        "a": node.bgColor[3] if not node.isText() else node.textColor[3]
                    } if not node.name.startswith("IMAGE") else None,
                    "imageRef": images[node.imageUrl] if node.name.startswith("IMAGE") else None,
                }
            ],
            "strokes": [
                {
                    "blendMode": "NORMAL",
                    "type": "SOLID",
                    "color": {
                        "r": node.borderColor[0],
                        "g": node.borderColor[1],
                        "b": node.borderColor[2],
                        "a": node.borderColor[3]
                    },
                    "weight": node.borderWeight

                }
            ],#
            "topLeftRadius": node.borderRadius[0],
            "topRightRadius": node.borderRadius[1],
            "bottomLeftRadius": node.borderRadius[3],
            "bottomRightRadius": node.borderRadius[2],
            "StrokeWeight": node.borderWeight, 
            "flexDirection": "row" if getNodeDirection(node) == "columns" else "column",
            "characters": node.text if node.isText() else "",
            "fontSize": 15.0,
            "fontName": {
                "family": "Permanent Marker",
                "style": "Regular"
            },
        },
        "children": [to_dict(child, images) for child in node.children]
        # "children": ", ".join([child.id for child in self.children])
    }
