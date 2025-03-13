import cv2
from classes import Node as DesignNode
from queue import Queue

def debug_layout_division(imagePath: str, root: DesignNode):
    image = cv2.imread(imagePath)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    queue : Queue[tuple[DesignNode]] = Queue()
    queue.put(root)
    while not queue.empty():
        subroot = queue.get()
        isRow = subroot.name.startswith("ROW")
        isColumn = subroot.name.startswith("COLUMN")

        if isRow or isColumn:
            cv2.rectangle(image, (int(subroot.left()), int(subroot.top())), (int(subroot.right()), int(subroot.bottom())), colors[0] if isRow else colors[1], 2)

        for child in subroot.children:
            queue.put(child)
        
    resized_image = cv2.resize(image, (1280, 720), interpolation=cv2.INTER_AREA)
    cv2.imshow("Showing Layout ", resized_image)
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close the window

    # Show the image



def showLines(imgPath: str, lines: list[tuple[int, int, int, int]]):
    # Load an image
    image = cv2.imread(imgPath)

    # Define start and end points of the line
    thickness = 2

    # Draw the line on the image
    for x1, y1, x2, y2 in lines:
        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), thickness)

    resized_image = cv2.resize(image, (1280, 720), interpolation=cv2.INTER_AREA)
    # Show the image
    cv2.imshow("Showing Lines ", resized_image)
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close the window
