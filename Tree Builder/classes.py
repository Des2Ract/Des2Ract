from __future__ import annotations

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
    
    def __init__(self):
        self.x = 0
        self.y = 0

    def __setitem__(self, key, value):
        if key == "x":
            self.x = value
        else:
            self.y = value

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
    name: str 
    figma_type: str  
    position: Point 
    size: Rectangle  
    text_color: Color | None
    bg_color: Color | None
    border: Border | None
    parent: Node | None
    children: list[Node] 

    def __init__(self):
        self.name = ""
        self.figma_type = ""
        self.position = Point()
        self.size = Rectangle()
        self.text_color = Color()
        self.bg_color = Color()
        self.border = Border()
        self.parent = None
        self.children = []
    
    def log(self):
        json_object=  {
            "name": self.name,
            "figma_type": self.figma_type,
            "position": self.position.get_json_format(),
            "size": self.size.get_json_format(),
            "color": str(self.text_color) if self.text_color is not None else None,
            "backgroundColor": str(self.bg_color) if self.bg_color is not None else None,
            "border": str(self.border) if self.border is not None else None,
            "parent": self.parent,
            "children": self.children
        }

        log_json(json_object)


class GroupNode:
    children: Node
        