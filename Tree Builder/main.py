from tree_builder import *


# figmaUrl = "https://www.figma.com/design/vWwqbxLzg15hcpOjoOhQ1M/qr-code-component?node-id=0-1469&t=TGy3WIKxJx9asl08-0"
figmaUrl = "https://www.figma.com/design/QpKlDdGRvg7DRe9NvXQRtZ/PUBLIC-SPACE-(Community)?node-id=18-7&t=LsYsHDfY3ZS2xL9k-0"
# figmaUrl = "https://www.figma.com/design/7AdW2tcD7EAj92Ul9lCfUt/Desktop-sign-up-and-login-pages-by-EditorM-(Community)?node-id=1-83&t=jwueEHOV3AqdUCGf-0"
# figmaUrl = "https://www.figma.com/design/m0ORoL6sZmV3Mh8v40gy06/Furniture-Store-Figma-Template-(Community)?node-id=1-520&t=M2lMtSrDUQ0G6TP8-0"
# figmaUrl = "https://www.figma.com/design/qBxwgf5We3fLeX8qa39dxW/FIG-EXAMPLE-(Community)?node-id=3-4&t=M2lMtSrDUQ0G6TP8-0"
# figmaUrl = "https://www.figma.com/design/QMjnIjBFGqDkEMlcoBbHHk/Untitled-(Copy)?node-id=28-2&t=jDW7ez8C6BlMQTmJ-0"
# figmaUrl = "https://www.figma.com/design/cbPly3T9U1v4QcKVRlnrYp/AOZ-website?node-id=1-2&t=RUS4HJLboG4UjICH-0"

# figmaUrl = "https://www.figma.com/design/7AdW2tcD7EAj92Ul9lCfUt/Desktop-sign-up-and-login-pages-by-EditorM--Community-?node-id=1-83&t=22SPW53Rp8HGOBlM-0"

# input parsing
figmaJsonFile, figmaImages  = getFigmaFileFromUrl(figmaUrl)
jsonNodes                   = parseFigmaJsonFile(figmaJsonFile)
fileNodes : list[Node]      = parseJsonNodes(jsonNodes)


root = build_tree(fileNodes)
root_dict = to_dict(root, figmaImages)

with open("root.json", "w") as json_file:
    json.dump(root_dict, json_file, indent=4)

debug_layout_division("debug/test.jpg", root)
debug_tree(root)
quit()