from utils import *
from debug import *
from api import *
from classes import *

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

def getNodeDirection(root : Node):
    # this should make something that tells me that this node should be row based or column based
    rootWidth = root.calculatedWidth()
    rootHeight = root.calculatedHeight()
    for child in root.children:
        if child.calculatedWidth() / rootWidth > 0.9:
            return "rows"
        if child.calculatedHeight() / rootHeight > 0.9:
            return "columns"
        
    xPos = root.allXPos()
    yPos = root.allYPos()

    stdX : list[int] = np.std(xPos) if len(xPos) > 1 else 0 
    stdY : list[int] = np.std(yPos) if len(yPos) > 1 else 0
    
    normStdX = (stdX / np.mean(xPos)) if len(xPos) > 1 else 0
    normStdY = (stdY / np.mean(yPos)) if len(yPos) > 1 else 0


    if normStdX > normStdY:
        return "columns"
    else:
        return "rows"

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

                    if len(container.children) > 1:
                        queue.put(container)
                    else:
                        for child in container.children:
                            queue.put(child)

# figmaFile = "https://www.figma.com/design/vWwqbxLzg15hcpOjoOhQ1M/qr-code-component?node-id=0-1469&t=TGy3WIKxJx9asl08-0"
# figmaFile = "https://www.figma.com/design/QpKlDdGRvg7DRe9NvXQRtZ/PUBLIC-SPACE-(Community)?node-id=18-7&t=LsYsHDfY3ZS2xL9k-0"
# figmaFile = "https://www.figma.com/design/7AdW2tcD7EAj92Ul9lCfUt/Desktop-sign-up-and-login-pages-by-EditorM-(Community)?node-id=1-83&t=jwueEHOV3AqdUCGf-0"

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
debug_layout_division("debug/test.jpg", root)
debug_tree(root)
quit()
