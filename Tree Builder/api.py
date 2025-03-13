import requests
from urllib.parse import urlparse, parse_qs

FIGMA_API_KEY = "figd_o72r2VUukQuXx7Rm4DRHaBrhsyGTx6ZK1MHzFsUE"
def requestFigmaFile(figmaFileKey: str, nodeId: str | None):
    if nodeId is None:
        url = "https://api.figma.com/v1/files/:file_key".replace(":file_key", figmaFileKey)
    else:
        url = "https://api.figma.com/v1/files/:file_key/nodes?ids=:id".replace(":file_key", figmaFileKey).replace(":id", nodeId)

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

    return requestFigmaFile(fileKey, rootId)
