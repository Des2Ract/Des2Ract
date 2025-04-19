import json
from utils import *
from debug import *
from api import *
from classes import *
from sklearn.metrics import pairwise_distances
from matplotlib import pyplot as plt
# ======================================================
# ================== ALGORITHM FUNCS ===================
# ======================================================
def handleContainedNodes(root: Node): 
    nodes = root.children.copy()
    nodes.sort(key=lambda n: (n.x, n.y, 0 if n.isLeaf() else -1, -n.area(), -1 if n.isFigmaGroup() else 0, n.id))

    i = 0
    while i < len(nodes):
        node = nodes[i]
        for othernode in reversed(nodes[ : i]):
            if node.isInside(othernode):
                othernode.appendChildren([node])
                break
        i += 1
    
    root.children = []
    for node in nodes:
        if node.parent.id == root.id:
            root.appendChildren([node])

def findOccupiedXSpace(root: Node):
    occupied = [(0, 0)]
    for child in root.children:
        occupied.append(( child.left(), child.right() ))
    right = root.right()
    occupied.append([right, right])

    occupied.sort(key=lambda node: (node[0], node[1]))

    i = 0
    while i < len(occupied) - 1:
        l1, r1 = occupied[i]
        l2, r2 = occupied[i + 1]

        # whole section is inside
        if l2 >= r1:
            i += 1
        else:            
            occupied[i] = ( l1, max(r1, r2) )
            occupied.pop(i + 1)
    
    return occupied

def findOccupiedYSpace(root: Node):
    occupied = [(0, 0)]
    for child in root.children:
        occupied.append(( child.top(), child.bottom() ))
    bot = root.bottom()
    occupied.append([bot, bot])

    occupied.sort(key=lambda node: (node[0], node[1]))

    i = 0
    while i < len(occupied) - 1:
        t1, b1 = occupied[i]
        t2, b2 = occupied[i + 1]

        # whole section is inside
        if t2 >= b1:
            i += 1
        else:            
            occupied[i] = ( t1, max(b1, b2) )
            occupied.pop(i + 1)
    
    return occupied

def makeLayout(root: Node):
    queue : Queue[Node] = Queue()
    queue.put(root)


    while not queue.empty():
        subroot = queue.get()

        dir = getNodeDirection(subroot)

        if dir == "rows":
            subroot.children.sort(key=lambda n: (n.y, n.x, -n.area(), n.id))
        else:
            subroot.children.sort(key=lambda n: (n.x, n.y, -n.area(), n.id))
        
        subroot.layout = dir
        
        if len(subroot.children) == 0:
            continue

        occupied = findOccupiedYSpace(subroot) if dir == "rows" else findOccupiedXSpace(subroot)

        occupied = [ section for section in occupied if section[0] != section[1] ]  

        if len(occupied) == 1:
            for child in subroot.children:
                queue.put(child)
        else:
            for section in occupied:
                top, bottom = section if dir == "rows" else (subroot.top(), subroot.bottom())
                left, right = section if dir == "columns" else (subroot.left(), subroot.right())

                nodes = getNodesBetween(subroot, top=top, bottom=bottom, left=left, right=right)

                if dir == "rows":
                    nodes.sort(key=lambda n: (n.top(), n.left(), -n.area(), n.id))
                else:
                    nodes.sort(key=lambda n: (n.left(), n.top(), -n.area(), n.id))

                if len(nodes) > 0:
                    if len(nodes) > 1:
                        container = Node(generateId())
                        container.x = 10000
                        container.y = 10000
                        container.width = -10000
                        container.height = -10000
                        container.name = ("ROW " if dir == "rows" else "COLUMN ") + str(container.id)
                        container.appendChildren(nodes)
                        for node in nodes:
                            subroot.children.remove(node)
                        subroot.appendChildren([container])
                        queue.put(container)
                    else:
                        for child in nodes:
                            queue.put(child)

def checkNodesBetween(root: Node, left: int, right: int, length: int):
    for i in range(length):
        if right + i > len(root.children) or root.children[left + i].similarTo(root.children[right + i]) < 0.9:
            return False
    return True

def createContainer():
    container = Node(generateId())
    container.x = 10000
    container.y = 10000
    container.width = -10000
    container.height = -10000
    container.name = "GROUP " + str(container.id)

    return container

def custom_distance(node1: Node, node2: Node):
    if node1.id == node2.id:
        return 0
    return abs(node1.distance(node2))

def groupNearElements(root: Node):
    queue : Queue[Node] = Queue()
    queue.put(root)

    while not queue.empty():
        subroot = queue.get()
        for child in subroot.children: queue.put(child)

        if subroot.layout == "rows":
            subroot.children.sort(key=lambda n: (n.top(), n.left(), -n.area(), n.id))
        else:
            subroot.children.sort(key=lambda n: (n.left(), n.top(), -n.area(), n.id))

        if len(subroot.children) <= 1:
            continue

        distances = [ subroot.children[i].distance(subroot.children[i+1]) for i in range(len(subroot.children)-1) ]
        first_quartile = np.quantile(distances, 0.25) if len(distances) > 0 else 0

        restructured_children = [subroot.children[0]]

        for i in range(1, len(subroot.children)):
            child = subroot.children[i]
            if restructured_children[-1].distance(child) <= first_quartile:
                if restructured_children[-1].name.startswith("NEAR GROUP"):
                    restructured_children[-1].appendChildren([child])
                else:
                    groupNode = createContainer()
                    groupNode.name = "NEAR GROUP " + str(groupNode.id)
                    groupNode.appendChildren([restructured_children[-1], child])
                    restructured_children[-1] = groupNode
            else:
                restructured_children.append(child)

        if len(restructured_children) == 1:
            continue

        subroot.children = restructured_children

def substituteFigmaGroups(root: Node):
    children = root.children
    if root.isFigmaGroup() and len(children) == 1:
        return substituteFigmaGroups(children[0])
        
    new_children = []
    for child in children:
        new_children.append(substituteFigmaGroups(child))
    
    root.children = new_children
    return root

def getAbstractTree(root: Node):
    if len(root.children) == 0:
        return [root]
    
    abstractedChildren = []
    for child in root.children:
        abstractedChildren.extend(getAbstractTree(child))
    root.children = abstractedChildren
    
    if root.isGroupingNode():
        return abstractedChildren
    else:
        return [root]
        

# ======================================================
# ======================== MAIN ========================
# ======================================================

def build_tree(fileNodes: list[Node]):
    # building the tree
    
    
    global count
    root = Node(-1)
    root.appendChildren(fileNodes)
    handleContainedNodes(root)
    normalizeNodes(root)
    makeLayout(root)
    groupNearElements(root)
    substituteFigmaGroups(root)
    # getAbstractTree(root)
    return root

