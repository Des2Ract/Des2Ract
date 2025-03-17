import requests
from urllib.parse import urlparse, parse_qs

FIGMA_API_KEY = "figd_o72r2VUukQuXx7Rm4DRHaBrhsyGTx6ZK1MHzFsUE"

def requestFigmaFileImage(figmaFileKey: str, nodeId: str | None, format: str = "jpg"):
    url = "https://api.figma.com/v1/images/:file_key?ids=:ids&format=:format".replace(":file_key", figmaFileKey).replace(":ids", nodeId.replace(":", "-")).replace(":format", format)

    headers = {
        "X-FIGMA-TOKEN": FIGMA_API_KEY
    }
    response = requests.get(url = url, headers=headers)
    data = response.json()

    imageUrl = data["images"][nodeId.replace("-", ":")]
    outputFile = f"debug/test.{format}"
    with open(outputFile, "wb") as f:
        f.write(requests.get(imageUrl).content)

    return data

def requestFigmaFileContentImages(figmaFileKey: str):
    url = "https://api.figma.com/v1/files/:file_key/images".replace(":file_key", figmaFileKey)

    headers = {
        "X-FIGMA-TOKEN": FIGMA_API_KEY
    }
    response = requests.get(url = url, headers=headers)
    data = response.json()["meta"]["images"]

    return data

def requestFigmaFile(figmaFileKey: str, nodeId: str | None):
    if nodeId is None:
        url = "https://api.figma.com/v1/files/:file_key".replace(":file_key", figmaFileKey)
    else:
        url = "https://api.figma.com/v1/files/:file_key/nodes?ids=:id".replace(":file_key", figmaFileKey).replace(":id", nodeId)
        requestFigmaFileImage(figmaFileKey, nodeId, format="jpg")

        # uncomment to download svg
        # requestFigmaFileImage(figmaFileKey, nodeId, format="svg")

    headers = {
        "X-FIGMA-TOKEN": FIGMA_API_KEY
    }
    response = requests.get(url = url, headers=headers)
    data = response.json()

    if nodeId is not None:
        nodeId = nodeId.replace("-", ":")
        data = data["nodes"][nodeId]


    return data


def getFigmaFileFromUrl(url: str):
    parsedUrl = urlparse(url)
    fileKey = parsedUrl.path.split("/")[2]
    query = parse_qs(parsedUrl.query)

    if "node-id" in query:
        rootId = query["node-id"][0]
    else:
        rootId = None

    return requestFigmaFile(fileKey, rootId), requestFigmaFileContentImages(fileKey)
