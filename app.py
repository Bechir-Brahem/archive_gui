# three streamlit input fields
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
from pathlib import Path
import random
import pandas as pd
import streamlit as st
from streamlit_tree_select import tree_select
import archive

if 'nodes' not in st.session_state:
    st.session_state.nodes = []

if 'depth' not in st.session_state:
    st.session_state.depth = 2

if 'first_level_files' not in st.session_state:
    st.session_state.first_level_files = set()


# recursive function that goes through the folders and subfolders
def _update_folders(path, depth):
    if depth <= 0:
        return
    ret = []

    for file in path.glob('*'):
        if file.is_file() or file.is_symlink():
            ret.append({
                "label": file.name,
                "value": str(file.absolute())
            })
        elif file.is_dir():
            ret.append({
                "label": file.name,
                "value": str(file.absolute()),
                "children": _update_folders(file, depth - 1),
            })
    return ret


def update_folders():
    root_path = Path(st.session_state.data_path)
    st.session_state.first_level_files = set(root_path.glob('*'))

    st.session_state.nodes = []
    st.session_state.nodes = _update_folders(root_path, st.session_state.depth)


c1, c2 = st.columns([3, 1])
with c1:
    data_path = st.text_input('Base Directory', on_change=update_folders, key='data_path', value='/sls_det_arxv/')
with c2:
    depth = st.number_input('Enter depth', value=2, key='depth', on_change=update_folders, disabled=True)

json_path = st.text_input('Enter path to json file', )

# job_description = st.text_input('Enter job description')

name_prefix = st.text_input('Enter name prefix')

command_file_name = st.text_input('Enter command file name')

c1, c2 = st.columns(2)
with c1:
    username = st.text_input('Enter username')
with c2:
    email = st.text_input('Enter email')

token = st.text_input('Enter token')

return_select = tree_select(st.session_state.nodes)
df = pd.DataFrame()

if return_select['checked']:
    top_level = set()

    from pathlib import Path

    for file in return_select['checked']:
        path = Path(file)
        if path.parent in st.session_state.first_level_files:
            top_level.add(str(path.parent))
        elif path in st.session_state.first_level_files:
            top_level.add(str(path))
    df1 = pd.DataFrame(
        {
            "name": list(top_level),
            "description": "" * len(top_level),
        }
    )
    df1 = st.data_editor(
        df1,
        column_config={
            "description": st.column_config.TextColumn()
        },
        disabled=["name"],
        hide_index=True,
    )

    sub_level = list(set(return_select['checked']) - top_level)

    if sub_level:
        df = pd.DataFrame(
            {
                "name": sub_level,
                "selected": [False] * len(sub_level),
            }
        )

        df = st.data_editor(
            df,
            column_config={
                "selected": st.column_config.CheckboxColumn()
            },
            disabled=["name"],
            hide_index=True,
        )

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    dry = st.button("Dry Run")
with c2:
    ingest = st.button("Ingest")
with c3:
    archive_btn = st.button("Archive")


def generate_folders():
    folders = {}
    for index, row in df1.iterrows():
        folders[row['name']] = {"description": row['description']}

    for index, row in df.iterrows():
        if row['selected']:
            parent = str(Path(row['name']).parent)
            if 'contents' not in folders[parent]:
                folders[parent]['contents'] = []
            folders[parent]['contents'].append(row['name'])
    return folders

def validate_fields():
    if not username:
        st.error("Username cannot be empty")
        return False
    if not email:
        st.error("Email cannot be empty")
        return False
    if not token:
        st.error("Token cannot be empty")
        return False
    if not name_prefix:
        st.error("Name prefix cannot be empty")
        return False
    if not command_file_name:
        st.error("Command file name cannot be empty")
        return False
    if not json_path:
        st.error("Json path cannot be empty")
        return False
    if not data_path:
        st.error("Data path cannot be empty")
        return False
    # if not job_description:
    #     st.error("Job description cannot be empty")
    #     return False
    return True

if dry:
    print("Dry Run")
    print(data_path)
    if validate_fields():
        print('json_path',json_path)
        archive.setup_config(email, username, token, name_prefix, json_path, data_path,command_file_name)
        archive.create_command_file()
        folders = generate_folders()
        print(folders)
        archive.generate_all(folders)


