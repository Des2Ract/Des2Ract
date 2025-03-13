import cv2

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
