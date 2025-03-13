from utils import *
from debug import *
from api import *
from classes import *

# ======================================================
# ================== ALGORITHM FUNCS ===================
# ======================================================
def handleContainedNodes(root: Node): 
    nodes = root.children.copy()
    nodes.sort(key=lambda n: (n.x, n.y, -n.area(), n.id))

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
    queue : Queue = Queue()
    queue.put((root, "columns"))

    while not queue.empty():
        subroot, dir = queue.get()

        for child in subroot.children:
            queue.put((child, "rows" if dir == "columns" else "columns"))

        occupied = findOccupiedYSpace(subroot) if dir == "rows" else findOccupiedXSpace(subroot)

        for section in occupied:
            top, bottom = section if dir == "rows" else (subroot.top(), subroot.bottom())
            left, right = section if dir == "columns" else (subroot.left(), subroot.right())

            nodes = getNodesBetween(subroot, top=top, bottom=bottom, left=left, right=right)

            if dir == "rows":
                nodes.sort(key=lambda n: (n.x, n.y, -n.area(), n.id))
            else:
                nodes.sort(key=lambda n: (n.y, n.x, -n.area(), n.id))

            if len(nodes) > 0:
                row = Node(generateId())
                row.name = ("Row " if dir == "rows" else "Column ") + str(row.id)
                row.appendChildren(nodes)
                for node in nodes:
                    subroot.children.remove(node)
                subroot.appendChildren([row])


# figmaFile = "https://www.figma.com/design/vWwqbxLzg15hcpOjoOhQ1M/qr-code-component?node-id=0-1469&t=TGy3WIKxJx9asl08-0"
figmaFile = "https://www.figma.com/design/QpKlDdGRvg7DRe9NvXQRtZ/PUBLIC-SPACE-(Community)?node-id=18-7&t=LsYsHDfY3ZS2xL9k-0"

# ======================================================
# ======================== MAIN ========================
# ======================================================

def build_tree(figmaUrl: str):
    # input parsing
    figmaJsonFile           = getFigmaFileFromUrl(figmaUrl)
    jsonNodes               = parseFigmaJsonFile(figmaJsonFile)
    fileNodes : list[Node]  = parseJsonNodes(jsonNodes)

    # building the tree
    root = Node(-1)
    root.appendChildren(fileNodes)
    handleContainedNodes(root)
    normalizeNodes(root)
    makeLayout(root)

    return root


root = build_tree(figmaFile)
debug_tree(root)
quit()
