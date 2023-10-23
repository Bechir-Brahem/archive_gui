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

# email = "julian.heymes@psi.ch"
# username = "Julian Heymes"
# token = "KHA3HTHzEfATR0lUT2l38IJaEKZxsFqy56iV1AcPo4HkH6R1USqf1GaZV36Bekbd"
# token_prefix = "moench_Julian"
# generated_files_dir = "/home/l_msdetect/PSI_data_archive/"
# base_dir = "/sls_det_arxv/moench_data/Julian/moench04_Julian/"
# commands_file_name = "20230908_JH_ingestion_commands.sh"
# name_prefix = "moench_Julian"
# json_path = ""


email = "bb@psi.ch"
username = "Bechir"
token = "KHA3HTHzEfATR0lUT2l38IJaEKZxsFqy56iV1AcPo4HkH6R1USqf1GaZV36Bekbd"
token_prefix = "moench_Julian"
generated_files_dir = "/tmp/test_archive/01"
base_dir = "/tmp"
commands_file_name = "20230908_JH_ingestion_commands.sh"
name_prefix = "moench_Julian"
json_path = "/tmp/test_archive/01"

if 'nodes' not in st.session_state:
    st.session_state.nodes = []

if 'depth' not in st.session_state:
    st.session_state.depth = 2

if 'first_level_files' not in st.session_state:
    st.session_state.first_level_files = set()

if 'define_old' not in st.session_state:
    st.session_state.df_parent_old = pd.DataFrame()
    st.session_state.df_sublevel_old = pd.DataFrame()
    st.session_state.define_old = True


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
    root_path = Path(data_path)
    st.session_state.first_level_files = set(root_path.glob('*'))

    st.session_state.nodes = []
    st.session_state.nodes = _update_folders(root_path, st.session_state.depth)


c1, c2 = st.columns([3, 1])
with c1:
    data_path = st.text_input('Base Directory', key='data_path', value=base_dir)
with c2:
    depth = st.number_input('Enter depth', value=2, key='depth', on_change=update_folders, disabled=True)
# recursive function that goes through the folders and subfolders

json_path = st.text_input('Enter path to json file', value=json_path)

# job_description = st.text_input('Enter job description')

name_prefix = st.text_input('Enter name prefix', value=name_prefix)

command_file_name = st.text_input('Enter command file name', value=commands_file_name)

c1, c2 = st.columns(2)
with c1:
    username = st.text_input('Enter username', value=username)
with c2:
    email = st.text_input('Enter email', value=email)

token = st.text_input('Enter token', value=token)

update_folders()
return_select = tree_select(st.session_state.nodes)

df_sublevel = pd.DataFrame()
df_parent = pd.DataFrame()
if return_select['checked']:
    top_level = set()

    from pathlib import Path

    for file in return_select['checked']:
        path = Path(file)
        if path.parent in st.session_state.first_level_files:
            top_level.add(str(path.parent))
        elif path in st.session_state.first_level_files:
            top_level.add(str(path))

    df_parent = pd.DataFrame(
        {
            "name": list(top_level),
            "description": "" * len(top_level),
        }
    )

    # for index, row in st.session_state.df_parent_old.iterrows():
    #     if row['name'] in top_level:
    #         df_parent.loc[df_parent['name'] == row['name'], 'description'] = row['description']
    # st.session_state.df_parent_old = df_parent.copy()
    df_parent = st.data_editor(
        df_parent,
        column_config={
            "description": st.column_config.TextColumn()
        },
        disabled=["name"],
        hide_index=True,
    )

    sub_level = list(set(return_select['checked']) - top_level)

    if sub_level:
        df_sublevel = pd.DataFrame(
            {
                "name": sub_level,
                "selected": [False] * len(sub_level),
            }
        )
        # for index, row in st.session_state.df_sublevel_old.iterrows():
        #     if row['name'] in sub_level:
        #         df_sublevel.loc[df_sublevel['name'] == row['name'], 'selected'] = row['selected']
        #
        # st.session_state.df_sublevel_old = df_sublevel.copy()

        df_sublevel = st.data_editor(
            df_sublevel,
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
    for index, row in df_parent.iterrows():
        folders[row['name']] = {"description": row['description']}

    for index, row in df_sublevel.iterrows():
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


def setup():
    if validate_fields():
        archive.setup_config(email, username, token, name_prefix, json_path, data_path, command_file_name)
        archive.create_command_file()
        return generate_folders()
    return None


if dry:
    folders = setup()
    if folders:
        archive.generate_all(folders, action=archive.ArchiveAction.DRY)

if ingest:
    folders = setup()
    if folders:
        archive.generate_all(folders, action=archive.ArchiveAction.INGEST)

if archive_btn:
    folders = setup()
    if folders:
        archive.generate_all(folders, action=archive.ArchiveAction.ARCHIVE)

if Path(f"{generated_files_dir}/{commands_file_name}").exists():
    st.divider()
    st.text("commands file: ")
    st.code(Path(f"{generated_files_dir}/{commands_file_name}").read_text())

