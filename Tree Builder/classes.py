from __future__ import annotations
import math


import json
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
def log_json(json_object):
    json_string = json.dumps(json_object, indent=4)

    console = Console()
    panel = Panel(json_string, title="", expand=True)
    console.print(Columns([panel]))


class Point:
    x: float
    y: float
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __setitem__(self, key, value):
        if key == "x":
            self.x = value
        else:
            self.y = value

    def __add__(self, point: Point):
        return Point(self.x + point.x, self.y + point.y)
    
    def __truediv__(self, scalar: float):
        if scalar == 0:
            raise ZeroDivisionError()
        return Point(self.x / scalar, self.y / scalar)
    
    def angle(self, point: Point):
        angle = math.atan2(point.y - self.y, point.x - self.x)
        return math.degrees(angle)

    def euclidean_distance(self, point: Point):
        return math.sqrt( (self.x - point.x) ** 2 + (self.y - point.y) ** 2)
    
    def manhatten_distance(self, point: Point):
        return (self.x - point.x) + (self.y + point.y)

    def get_json_format(self):
        return {"x": self.x, "y": self.y}

    def log(self):
        log_json(self.get_json_format())   

class Rectangle:
    width: float
    height: float
    
    def __init__(self):
        self.width = 0
        self.height = 0

    def __setitem__(self, key, value):
        if key == "width":
            self.width = value
        else:
            self.height = value
    
    def get_json_format(self):
        return {"width": self.width, "height": self.height}

    def log(self):
        log_json(self.get_json_format())
    
class Color:
    r: float
    g: float
    b: float
    a: float
    
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        self.a = 0

    def __setitem__(self, key, value):
        if key == "r":
            self.r = value
        elif key == "g":
            self.g = value
        elif key == "b":
            self.b = value
        else:
            self.a = value
    
    def __str__(self):
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"

    def get_json_format(self):
        return {"color": f"rgba({self.r}, {self.g}, {self.b}, {self.a})"}

    def log(self):
        log_json(self.get_json_format())

class Border:
    weight: float
    color: Color
    radius: float
    style: str

    def __init__(self):
        self.weight = 0
        self.color = Color()
        self.radius = 0
        self.style = ""

    def __setitem__(self, key, value):
        if key == "weight":
            self.weight = value
        elif key == "radius":
            self.radius = value
        elif key == "style":
            self.style = value
        else:
            pass

    def __str__(self):
        return f"{self.weight}px {self.style} {str(self.color)}"
    
    def get_json_format(self):
        return {"border": f"{self.weight}px {self.style} {str(self.color)}"}

    def log(self):
        log_json(self.get_json_format())

class Node:
    id: int
    name: str
    depth: int
    figma_type: str
    position: Point
    size: Rectangle
    rotation: float
    parent: Node | None
    children: list[Node]

    def __init__(self, id: int):
        self.id = id
        self.name = ""
        self.figma_type = "FRAME"
        self.position = Point(0, 0)
        self.size = Rectangle()
        self.rotation = 0
        self.parent = None
        self.children = []

    def left(self): return self.position.x
    def right(self): return self.position.x + self.size.width
    def top(self): return self.position.y
    def bottom(self): return self.position.y + self.size.height
    
    def center(self):
        return Point(x=self.position.x + (self.size.width / 2), y=self.position.y + (self.size.height / 2))

    def area(self):
        return self.size.width * self.size.height

    def line_border(self, line: Node, rectangle: Node):
        THRSH = 5
        if line.size.width >= rectangle.size.width:
            return abs(line.top() - rectangle.bottom()) < THRSH or abs(rectangle.top() - line.bottom()) < THRSH
        
        if line.size.height >= rectangle.size.height:
            return abs(line.left() - rectangle.right()) < THRSH or abs(rectangle.left() - line.right()) < THRSH

        return False
    


    def is_inside(self, node: Node):
        if self.name == "Profile":
            "here"

        NONE_INTERSECTING_ELEMENTS = [
            "LINE",
            "TEXT", 
            "VECTOR"
        ]

        if self.id > node.id:
            return False
        
        if self.area() > node.area():
            return False
        
        if  self.figma_type in NONE_INTERSECTING_ELEMENTS and \
            node.figma_type in NONE_INTERSECTING_ELEMENTS:
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
        if self.is_inside(node):
            return -1 * self.area()
        elif node.is_inside(self):
            return -1 * node.area()
        
        angle = center_1.angle(center_2)

        if angle > -45 and angle < 45:
            return abs(node.position.x - (self.position.x + self.size.width))
        elif angle >= 45 and angle < 135:
            return abs(self.position.y - (node.position.y + node.size.height))
        elif (angle >= 135 and angle <= 180) or (angle >= -180 and angle < -135):
            return abs(self.position.x - (node.position.x + node.size.width))
        else:
            return abs(node.position.y - (self.position.y + self.size.height))


    def to_dict(self):
        return {
            "id": self.id,
            "figma_type": self.figma_type,
            "position": self.position.get_json_format(),
            "size": self.size.get_json_format(),
            "parent": self.parent.id if self.parent is not None else None,
            # "children": ", ".join([child.id for child in self.children])
        }
               
    def log(self):
        log_json(self.to_dict())

class UiNode(Node):
    text_color: Color | None
    bg_color: Color | None
    border: Border | None

    def __init__(self, id: int):
        super().__init__(id)
        self.text_color = Color()
        self.bg_color = Color()
        self.border = Border()

    def to_dict(self):
        tempelate = super().to_dict()
        tempelate.update({
            "name": self.name,
            "color": str(self.text_color) if self.text_color is not None else None,
            "backgroundColor": str(self.bg_color) if self.bg_color is not None else None,
            "border": str(self.border) if self.border is not None else None,
        }) 
        return tempelate

    
        
# for now it is just something to make it readable -- may add some attributes later
class GroupNode(Node):
    def __init__(self, id):
        super().__init__(id)
        self.initialized = False
        self.name = f"Grouping {id}"

    def append_child(self, child: Node):
        if not self.initialized:
            self.position.x = child.position.x
            self.position.y = child.position.y
            self.size.width = child.size.width
            self.size.height = child.size.height
            self.initialized = True
        else:
            x_right = max(self.position.x + self.size.width, child.position.x + child.size.width)
            y_height = max(self.position.y + self.size.height, child.position.y + child.size.height)

            self.position.x = min(self.position.x, child.position.x)
            self.position.y = min(self.position.y, child.position.y)

            self.size.width = x_right - self.position.x
            self.size.height = y_height - self.position.y

        self.children.append(child)
        return self
        