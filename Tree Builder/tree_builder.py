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
    nodes.sort(key=lambda n: (n.x, n.y, 0 if n.isLeaf() else -1, -n.area(), n.id))

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
        
        if len(subroot.children) == 0:
            continue

        occupied = findOccupiedYSpace(subroot) if dir == "rows" else findOccupiedXSpace(subroot)

        if len(occupied) == 3:
            for child in subroot.children:
                queue.put(child)
        else:
            for section in occupied:
                top, bottom = section if dir == "rows" else (subroot.top(), subroot.bottom())
                left, right = section if dir == "columns" else (subroot.left(), subroot.right())

                nodes = getNodesBetween(subroot, top=top, bottom=bottom, left=left, right=right)

                if dir == "rows":
                    nodes.sort(key=lambda n: (n.y, n.x, -n.area(), n.id))
                else:
                    nodes.sort(key=lambda n: (n.x, n.y, -n.area(), n.id))

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

def groupRepeatingPatterns(root: Node):
    if len(root.children) == 0:
        return
    
    for child in root.children:
        groupRepeatingPatterns(child)

    dir = getNodeDirection(root)

    vectorElements = root.children.copy()
    custom_dist_matrix = pairwise_distances(vectorElements, metric=custom_distance)
    
    # cluster the whole children into clusters where each cluster will represent one icon
    dbscan = DBSCAN(eps=5, min_samples=1, metric="precomputed")
    labels = dbscan.fit_predict(custom_dist_matrix)

    # extract these clusters
    clusters : dict[str, list] = {}
    for node, label in zip(vectorElements, labels):
        if label not in clusters: clusters[label] = []
        clusters[label].append(node)

    for label, nodes in clusters.items():
        if len(nodes) > 1:
            container = createContainer()
            for element in nodes:
                root.children.remove(element)
            container.appendChildren(nodes)
            root.appendChildren([container])
    
    if dir == "rows":
        root.children.sort(key=lambda n: (n.top(), n.left(), -n.area(), n.id))
    else:
        root.children.sort(key=lambda n: (n.left(), n.top(), -n.area(), n.id))
    
# figmaFile = "https://www.figma.com/design/vWwqbxLzg15hcpOjoOhQ1M/qr-code-component?node-id=0-1469&t=TGy3WIKxJx9asl08-0"
figmaFile = "https://www.figma.com/design/QpKlDdGRvg7DRe9NvXQRtZ/PUBLIC-SPACE-(Community)?node-id=18-7&t=LsYsHDfY3ZS2xL9k-0"
# figmaFile = "https://www.figma.com/design/7AdW2tcD7EAj92Ul9lCfUt/Desktop-sign-up-and-login-pages-by-EditorM-(Community)?node-id=1-83&t=jwueEHOV3AqdUCGf-0"

# ======================================================
# ======================== MAIN ========================
# ======================================================

def build_tree(figmaUrl: str):
    # input parsing
    figmaJsonFile, figmaImages  = getFigmaFileFromUrl(figmaUrl)
    jsonNodes                   = parseFigmaJsonFile(figmaJsonFile)
    fileNodes : list[Node]      = parseJsonNodes(jsonNodes)

    # building the tree
    root = Node(-1)
    root.appendChildren(fileNodes)
    handleContainedNodes(root)
    normalizeNodes(root)
    makeLayout(root)
    groupRepeatingPatterns(root)
    return root, figmaImages


root, figmaImages = build_tree(figmaFile)
root_dict = to_dict(root, figmaImages)
import json

with open("root.json", "w") as json_file:
    json.dump(root_dict, json_file, indent=4)

debug_layout_division("debug/test.jpg", root)
debug_tree(root)
quit()
