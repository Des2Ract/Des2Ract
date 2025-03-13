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
        node = DesignNode(jsonNode["id"])
        node.name = jsonNode["name"]
        node.figma_type = jsonNode["type"]
        node.rotation = jsonNode["rotation"] if "rotation" in jsonNode.keys() else 0
        
        if node.figma_type == "TEXT":
            node.text = jsonNode["name"]

        if "fills" in jsonNode.keys() and len(jsonNode["fills"]) > 0:
            if "color" in jsonNode["fills"][0]:
                colorJson = jsonNode["fills"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(colorJson["a"])) 

                if node.figma_type == "TEXT":
                    node.textColor = color
                else:
                    node.bgColor = color
        
        if "strokes" in jsonNode.keys() and len(jsonNode["strokes"]) > 0:
            if "color" in jsonNode["strokes"][0]:
                colorJson = jsonNode["strokes"][0]["color"]
                color = (float(colorJson["r"]), float(colorJson["g"]), float(colorJson["b"]), float(colorJson["a"])) 
                node.borderColor = color
            
        if "cornerRadius" in jsonNode.keys():
            node.borderRadius = float(jsonNode["cornerRadius"])

        node.x = jsonNode["absoluteBoundingBox"]["x"]
        node.y = jsonNode["absoluteBoundingBox"]["y"]
        node.width = jsonNode["absoluteBoundingBox"]["width"]
        node.height = jsonNode["absoluteBoundingBox"]["height"]
        
        parsedNodes.append(node)
    return parsedNodes

def normalizeTexts(root: DesignNode):
    lettersRegex = r"\b[^a-zA-Z\s]*[a-zA-Z]+[^a-zA-Z\s]*\b"
    numbersRegex = r"[0-9]+"
    spacesRegex = r"[ \t]+"
    root.text = re.sub(lettersRegex, "/w", root.text)
    root.text = re.sub(numbersRegex, "/d", root.text)
    root.text = re.sub(spacesRegex,  "/s", root.text)

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