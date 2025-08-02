# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%
import os
import json
from tqdm.notebook import tqdm
from fbpyutils import file as fu

source_dir, source_mask, source_label = "H:/", "*", "SAMSUNG_M3_PORTABLE_BACKUP001"
source_dir, source_mask, source_label = "I:/", "*", "YGGDRASIL_DISK_IA"
source_dir, source_mask, source_label = "H:/Downloads", "*", "SAMSUNG_M3_PORTABLE_BACKUP001"

files_on_source = fu.find(source_dir, source_mask)

print(f"Found {len(files_on_source)} files on {source_label} ({source_dir})")

# %%
report = {
    "source_name": source_label,
    "source_dir": source_dir,
    "source_mask": source_mask,
    "files": [],
}

file_report = {
    "file_path": "",
    "status": "OK", 
    "status_message": None
}

for f in tqdm(files_on_source):
    file_report["file_path"] = f
    try:
        file_report["details"] = fu.describe_file(f)
        file_report["status"] = "OK"
        file_report["status_message"] = None
    except Exception as e:
        file_report["details"] = None
        file_report["status"] = "ERROR"
        file_report["status_message"] = str(e)
    report["files"].append(file_report.copy())

# %%
report['files'][0]
