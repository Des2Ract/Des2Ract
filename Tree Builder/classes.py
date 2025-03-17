from __future__ import annotations        
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from utils import *
import numpy as np
def calculate_angle(point_1: tuple[float, float], point_2: tuple[float, float]):
    angle = math.atan2(point_2[1] - point_1[1], point_2[0] - point_1[0])
    return math.degrees(angle)


def normalizeColor(color: tuple[int, int, int, int]):
    if color[0] > 1 and color[1] > 1 and color[2] > 1 and color[3] > 1:
        return [color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255]
    return [color[0], color[1], color[2], color[3]]

def textPatternToVec(text: str):
    vec = []
    sum = 0
    for char in text:
        if char == "W":
            vec.append(1)
        elif char == "D":
            vec.append(2)
        elif char == "S":
            vec.append(3)
        elif char == ".":
            vec.append(4)
        elif char == "_":
            vec.append(5)
        elif char == "#":
            vec.append(6)
        else:
            vec.append(0)
        sum += vec[-1]

    return np.array(vec) / sum

class Node:
    children: list[Node]
    parent: Node
    def __init__(self, id: int):
        self.id = id
        self.name = ""
        self.figma_type = "FRAME"

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.rotation = 0
        
        self.parent = None
        self.children = []
        self.iconChildren = []

        self.text = ""
        self.normalizedText = ""
        self.imageUrl = ""
        self.imgScaleMode = ""

        self.textColor = (0, 0, 0, 0)
        self.bgColor = (0, 0, 0, 0)
        self.borderColor = (0, 0, 0, 0)
        self.borderRadius = 0
        self.borderWeight = 0


        self.layout = None

    def left(self):     return min([self.x] + [child.left() for child in self.children])
    def right(self):    return max([self.x + self.width] + [child.right() for child in self.children])
    def top(self):      return min([self.y] + [child.top() for child in self.children])
    def bottom(self):   return max([self.y + self.height] + [child.bottom() for child in self.children])
    def calculatedWidth(self): return self.right() - self.left()
    def calculatedHeight(self): return self.bottom() - self.top()
    def area(self):     return (self.right() - self.left()) * (self.bottom() - self.top())
    def center(self):   return np.mean( [(self.x + self.width / 2, self.y + self.height / 2)] + [child.center() for child in self.children], axis=0)

    def isText(self):    return self.figma_type in ["TEXT"]
    def isLine(self):    return self.figma_type in ["LINE"]
    def isLeaf(self):    return self.figma_type in ["TEXT", "LINE", "VECTOR"]
    def isGroupingNode(self): return self.name.startswith("GROUP") or self.name.startswith("ROW") or self.name.startswith("COLUMN")
    def isIconPart(self):   return self.figma_type in ["VECTOR"]
    def isImage(self):  return False # modify this later

    def allXPos(self): return ([self.x] if self.x < 10000 else []) + [child.x for child in self.children]
    def allYPos(self): return ([self.y] if self.y < 10000 else []) + [child.y for child in self.children]

    def featureVector(self):
        features = []
        maxLength = 100

        if not self.isText():
            features.append(self.calculatedWidth())
            features.append(self.calculatedHeight())
            features.append(self.area())
            features.extend(normalizeColor(self.bgColor))
            features.extend(normalizeColor(self.textColor))
            features.extend(normalizeColor(self.borderColor))
            features.append(self.borderRadius)
            features.append(self.borderWeight)
            features.extend( [0 for _ in range(maxLength - len(features))] )
        else:
            features.extend( [0 for _ in range(17)] )
            features.extend(textPatternToVec(self.text))
            if len(self.text) < maxLength:
                features.extend( [0 for _ in range(maxLength - len(features))] )
        return features
    
    def similarTo(self, node: Node):
        if self.figma_type != node.figma_type: 
            return 0

        if self.isText() and node.isText():
            selfPattern = self.text
            nodePattern = node.text
            return SequenceMatcher(None, selfPattern, nodePattern).ratio()

        features = self.featureVector()
        nodeFeatures = node.featureVector()
        return abs(cosine_similarity([features], [nodeFeatures])[0][0])

    def line_border(self, line: Node, rectangle: Node):
        THRSH = 5
        if line.width >= rectangle.width:
            return abs(line.top() - rectangle.bottom()) < THRSH or abs(rectangle.top() - line.bottom()) < THRSH
        
        if line.height >= rectangle.height:
            return abs(line.left() - rectangle.right()) < THRSH or abs(rectangle.left() - line.right()) < THRSH

        return False

    def isInside(self, node: Node):
        NONE_INTERSECTING_ELEMENTS = [ "LINE", "TEXT", "VECTOR"]

        # if the current node is behind the other node (lower z index)
        if self.area() > node.area():
            return False
        
        # if the elements can't intersect
        if  self.figma_type in NONE_INTERSECTING_ELEMENTS and node.figma_type in NONE_INTERSECTING_ELEMENTS:
            return False

        THRSH = 3

        if self.left() < node.left() - THRSH \
        or self.right() > node.right() + THRSH\
        or self.top() < node.top() - THRSH \
        or self.bottom() > node.bottom() + THRSH:
            if self.figma_type == "LINE" and node.figma_type != "LINE":
                return self.line_border(self, node)
            return False
        return True
    
    def distance(self, node: Node):
        if self.isInside(node):
            return -1 * self.area()
        
        elif node.isInside(self):
            return -1 * node.area()
        
        distances = [
            abs(node.left() - self.right()), 
            abs(node.right() - self.left()),
            abs(node.top() - self.bottom()),
            abs(node.bottom() - self.top())
        ]

        return np.min(distances)

    def appendChildren(self, children: list[Node]):
        for child in children:
            found = False
            for currentChild in self.children:
                found |= currentChild.id == child.id

            if not found:
                self.children.append(child)
            else:
                print("sus")

            child.parent = self

    def maintainTreeConsistency(self):
        it = 0
        while it < len(self.children):
            child = self.children[it]
            if child.parent.id != self.id:
                self.children.remove(child)
            else:
                it += 1
        
        for child in self.children:
            child.maintainTreeConsistency()

    def log(self):
        log_json(self.to_dict())
