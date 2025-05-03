import os
from joblib import Parallel, delayed
from tqdm import tqdm
from tqdm_joblib import tqdm_joblib
from tree_builder import *

files = [os.path.join("dataset", f) for f in os.listdir("dataset") if os.path.isfile(os.path.join("dataset", f))]

def process_file(file):
    file_name = os.path.basename(file)
    with open(file, 'r', encoding='utf-8') as f:
        figmaJsonFile = json.load(f)
    try:
        jsonNodes = parseTrainingJsonFile(figmaJsonFile)
        fileNodes: list[Node] = parseTrainingJsonNodes(jsonNodes)
    except:
        print("\nError in", file_name)
        return

    root = build_tree(fileNodes)
    root_dict = to_dict(root, dict())

    with open(f"output/{file_name}", "w") as json_file:
        json.dump(root_dict, json_file, indent=4)

with tqdm(total=len(files), desc="Processing files", unit="file") as pbar:
    with tqdm_joblib(pbar):
        Parallel(n_jobs=-1)(delayed(process_file)(file) for file in files)