from __future__ import annotations
from utils import *
import numpy as np
def calculate_angle(point_1: tuple[float, float], point_2: tuple[float, float]):
    angle = math.atan2(point_2[1] - point_1[1], point_2[0] - point_1[0])
    return math.degrees(angle)

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
    def area(self):     return (self.right() - self.left()) * (self.bottom() - self.top())
    def center(self):   return np.mean( [(self.x + self.width / 2, self.y + self.height / 2)] + [child.center() for child in self.children], axis=0)

    def isText(self):    return self.figma_type in ["TEXT"]
    def isLine(self):    return self.figma_type in ["LINE"]
    def isIconPart(self):   return self.figma_type in ["VECTOR"]
    def isImage(self):  return False # modify this later

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
        center_1 = self.center()
        center_2 = node.center()
        if self.isInside(node):
            return -1 * self.area()
        
        elif node.isInside(self):
            return -1 * node.area()
        
        angle = calculate_angle((center_1[0], center_1[1]), (center_2[0], center_2[1]))

        if angle > -45 and angle < 45:
            return abs(node.left() - node.right())
        elif angle >= 45 and angle < 135:
            return abs(self.top() - node.bottom())
        elif (angle >= 135 and angle <= 180) or (angle >= -180 and angle < -135):
            return abs(self.left() - node.right())
        else:
            return abs(node.top() - self.bottom())

    def to_dict(self):
        return {
            "id": self.id,
            "figma_type": self.figma_type,
            "position": self.position.get_json_format(),
            "size": self.size.get_json_format(),
            "parent": self.parent.id if self.parent is not None else None,
            # "children": ", ".join([child.id for child in self.children])
        }
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
