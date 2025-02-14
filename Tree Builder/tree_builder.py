import os
from urllib.parse import urlparse, parse_qs
from gateway import API
from utilities import Utils
from classes import GroupNode, Node
from queue import Queue
from anytree import Node, RenderTree


def debug_tree(root: GroupNode):
    queue : Queue[Node] = Queue()
    queue.put((root, Node(root, parent=None)))
    while not queue.empty():
        (top, prev_parent) = queue.get()
        for child in top.children:
            next_parent = Node(f"Child {child.name}", parent=prev_parent)
            queue.put((child, next_parent))
    
    # Render the tree
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name}")


class TreeBuilder:
    def __init__(self, figma_file_url: str):
        parsed_url = urlparse(figma_file_url)
        file_key = parsed_url.path.split("/")[int(os.getenv("FIGMA_FILE_KEY_INDEX"))]
        query = parse_qs(parsed_url.query)
        if "node-id" in query:
            root_id = query["node-id"][0]
        else:
            root_id = None
    
        figma_json_file = API.get_figma_tree(file_key=file_key, root_id=root_id)
        leaf_nodes = Utils.filter_leaf_elements(figma_json_file)
        self.nodes = [ Utils.parse_figma_node(element) for element in leaf_nodes ]
        self.nodes.sort(key=lambda node: node.area())

    def __make_distance_matrix(self, nodes: list[Node]):
        n = len(nodes)
        distance_matrix = [ [0 for _ in range(n)] for __ in range(n) ]

        for i, node in enumerate(nodes):
            for j, other_node in enumerate(nodes):
                distance_matrix[i][j] = node.distance(other_node)
        return distance_matrix
    
    def get_best_connection(self, nodes: list[Node]):
        if len(nodes) == 1:
            return None
        
        distance_matrix = self.__make_distance_matrix(nodes)
        best_id = (0, 1, distance_matrix[0][1])
        n = len(distance_matrix)
        for id_1 in range(n):
            for id_2 in range(n):
                if id_1 == id_2:
                    continue
                if distance_matrix[id_1][id_2] < distance_matrix[best_id[0]][best_id[1]]:
                    best_id = (id_1, id_2, distance_matrix[id_1][id_2])
        return best_id
    
    def get_contained_nodes(self, nodes: list[Node]):
        connection = None
        for id, node in enumerate(nodes):
            for other_id, other_node in enumerate(nodes):
                if id != other_id and node.is_inside(other_node):
                    connection = (id, other_id)
                    break
            if connection is not None:
                break
        return connection

    def cluster_sub_regions(self, nodes: list[Node]):
        best_connection = self.get_contained_nodes(nodes)
        while best_connection is not None:
            nodeA = nodes[best_connection[0]]
            nodeB = nodes[best_connection[1]]

            if nodeA.is_inside(nodeB):
                nodeB.children.append(nodeA)
                nodes.remove(nodeA)
            else:
                nodeA.children.append(nodeB)
                nodes.remove(nodeB)

            best_connection = self.get_contained_nodes(nodes)
        return nodes
    # def connect_nodes(self, distance_matrix: list[list], best_connection: tuple):

    def print_node_with_id(self, id: int):
        for node in self.nodes:
            if node.id == id:
                node.log()
                return

    def cluster(self):
        distance_matrix = self.__make_distance_matrix(self.nodes)

        nodes_copy = self.nodes.copy()
        id = len(nodes_copy)

        best_connection = self.get_best_connection(distance_matrix)
        while best_connection is not None:
            group = GroupNode(id)
            id += 1
            nodeA, nodeB = nodes_copy[best_connection[0]], nodes_copy[best_connection[1]]

            if id == 51:
                print("d")

            if best_connection[2] is False:
                nodeA.parent = group
                nodeB.parent = group
                group.append_child(nodeA).append_child(nodeB)
                
                nodes_copy.remove(nodeA)
                nodes_copy.remove(nodeB)
                nodes_copy.append(group)
            elif nodeA.is_inside(nodeB):
                nodeA.parent = nodeB
                nodeB.children.append(nodeA)
                nodes_copy.remove(nodeA)
            else:
                nodeB.parent = nodeA
                nodeA.children.append(nodeB)
                nodes_copy.remove(nodeB)
            
            nodes_copy.sort(key=lambda node: node.area())
            distance_matrix = self.__make_distance_matrix(nodes_copy)
            best_connection = self.get_best_connection(distance_matrix)
        self.debug_tree(nodes_copy[0])

    # second approch
    def cluster(self, nodes : list[Node]=None):
        if nodes is None: 
            nodes = self.nodes
            nodes.sort(key=lambda node: node.id, reverse=True)

        if len(nodes) == 0: return [] 

        clustered_nodes = self.cluster_sub_regions(nodes) 
        for node in clustered_nodes:
            clustered_children = self.cluster(node.children)
            node.children = clustered_children
        
        return nodes
        

# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/KJyVqweJFdfHOVzY3MPDRw/FIG-EXAMPLE-(Community)?node-id=16-172&t=ndbeAyT9TWX2Wojd-0")
# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/QpKlDdGRvg7DRe9NvXQRtZ/PUBLIC-SPACE-(Community)?node-id=0-1&p=f&t=25YO3NwZftMFXRBJ-0")
# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/7AdW2tcD7EAj92Ul9lCfUt/Desktop-sign-up-and-login-pages-by-EditorM-(Community)?node-id=0-1&p=f&t=tUKrWjhLVN2PDG5L-0")
tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/m0ORoL6sZmV3Mh8v40gy06/Furniture-Store-Figma-Template-(Community)?node-id=1-61&t=5qgfYlMcHKhQ6Roo-0")

# ok
# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/KJyVqweJFdfHOVzY3MPDRw/FIG-EXAMPLE-(Community)?node-id=16-172&t=hOTX01LOyxZrB3r2-0")


trees = tree_builder.cluster()

for root in trees:
    debug_tree(root)