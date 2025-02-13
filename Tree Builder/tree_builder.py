import os
from gateway import API
from utilities import Utils
from classes import GroupNode, Node
from queue import Queue
from anytree import Node, RenderTree

class TreeBuilder:
    def __init__(self, figma_file_url: str):
        file_key = figma_file_url.replace(r"https://", "", 1).split("/")[int(os.getenv("FIGMA_FILE_KEY_INDEX"))]
        figma_json_file = API.get_figma_tree(file_key=file_key)
        leaf_nodes = Utils.filter_leaf_elements(figma_json_file)
        self.nodes = [ Utils.parse_figma_node(id, element) for id, element in enumerate(leaf_nodes) ]
        self.nodes.sort(key=lambda node: node.area())

    def __make_distance_matrix(self, nodes: list[Node]):
        n = len(nodes)
        distance_matrix = [ [0 for _ in range(n)] for __ in range(n) ]
        for i, node in enumerate(nodes):
            for j, other_node in enumerate(nodes):
                distance_matrix[i][j] = node.distance(other_node)
                if distance_matrix[i][j] > 20:
                    distance_matrix[i][j] = 10000000
        return distance_matrix
    
    def get_best_connection(self, distance_matrix):
        # this indicates that there is only one node in the tree which is the root
        if len(distance_matrix) == 1:
            return None

        best_id = (0, 1, distance_matrix[0][1] == -1)
        n = len(distance_matrix)
        for id_1 in range(n):
            for id_2 in range(n):
                if id_1 == id_2:
                    continue
                if distance_matrix[id_1][id_2] < distance_matrix[best_id[0]][best_id[1]]:
                    best_id = (id_1, id_2, distance_matrix[id_1][id_2] == -1)
    
        return best_id

    # def connect_nodes(self, distance_matrix: list[list], best_connection: tuple):

    def print_node_with_id(self, id: int):
        for node in self.nodes:
            if node.id == id:
                node.log()
                return

    def debug_tree(self, root: GroupNode):
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


# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/vWwqbxLzg15hcpOjoOhQ1M/qr-code-component?node-id=0-1468&p=f&t=MQzWnCigMSq2X0zb-0")
# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/KJyVqweJFdfHOVzY3MPDRw/FIG-EXAMPLE-(Community)?node-id=16-172&t=ndbeAyT9TWX2Wojd-0")
# tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/QpKlDdGRvg7DRe9NvXQRtZ/PUBLIC-SPACE-(Community)?node-id=0-1&p=f&t=25YO3NwZftMFXRBJ-0")
tree_builder = TreeBuilder(figma_file_url="https://www.figma.com/design/7AdW2tcD7EAj92Ul9lCfUt/Desktop-sign-up-and-login-pages-by-EditorM-(Community)?node-id=0-1&p=f&t=tUKrWjhLVN2PDG5L-0")
tree_builder.cluster()