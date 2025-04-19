import os
from tree_builder import *



# input parsing


files = [os.path.join("dataset", f) for f in os.listdir("dataset") if os.path.isfile(os.path.join("dataset", f))]

for i, file in enumerate(files):

    file_name = os.path.basename(file)
    with open(file, 'r', encoding='utf-8') as f:
        figmaJsonFile = json.load(f)

    jsonNodes                   = parseTrainingJsonFile(figmaJsonFile)
    fileNodes : list[Node]      = parseTrainingJsonNodes(jsonNodes)

    print(len(fileNodes))

    root = build_tree(fileNodes)
    root_dict = to_dict(root, dict())

    with open(f"output/{file_name}", "w") as json_file:
        json.dump(root_dict, json_file, indent=4)

    print(f"{i+1}/{len(files)}")