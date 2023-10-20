import os
from pathlib import Path

email = "julian.heymes@psi.ch"
name = "Julian Heymes"
token = "KHA3HTHzEfATR0lUT2l38IJaEKZxsFqy56iV1AcPo4HkH6R1USqf1GaZV36Bekbd"
token_prefix = "moench_Julian"
# generated_files_dir = "/afs/psi.ch/user/h/heymes_j/Desktop/tests_archiving/"
generated_files_dir = "/home/l_msdetect/PSI_data_archive/"
# base_dir = "/mnt/sls_det_storage/moench_data/Julian/moench04_Julian/"
base_dir = "/sls_det_arxv/moench_data/Julian/moench04_Julian/"
commands_file_name = "20230908_JH_ingestion_commands.sh"


def write_json_and_txt(json_loc,
                       base_directory,
                       folder_basename,
                       description_entry,
                       contents,
                       user_name,
                       user_email,
                       api_token,
                       dataset_name_folder_prefix):
    description_full = f"Description: {description_entry} ------ Folder contents: {' | '.join(contents)}"
    f = open(f"{json_loc}/metadata_{folder_basename}_a-35297.json", "w")
    f.write('{\n')
    f.write(f'    "datasetName": "{dataset_name_folder_prefix}/{folder_basename}",\n')
    f.write(f'    "owner": "{user_name}",\n')
    f.write(f'    "sourceFolder": "{base_directory}{folder_basename}",\n')
    f.write(f'    "type": "raw",\n')
    f.write(f'    "ownerEmail": "{user_email}",\n')
    f.write(f'    "contactEmail": "{user_email}",\n')
    f.write(f'    "principalInvestigator": "{user_email}",\n')
    f.write(f'    "creationLocation": "/PSI/SLS_DETECTOR",\n')
    f.write(f'    "description": "{description_full}",\n')
    f.write(f'    "ownerGroup": "a-35297"\n')
    f.write('}\n')
    f.close()

    f = open(f"{json_loc}/filelisting_{folder_basename}.txt", "w")
    for content in contents:
        f.write(f"{content}\n")
    f.close()

    # Dry run: /home/l_msdetect/PSI_data_archive/datasetIngestor -noninteractive -token {api_token}
    # Ingest only: /home/l_msdetect/PSI_data_archive/datasetIngestor -ingest -noninteractive -token {api_token}
    # Archive : /home/l_msdetect/PSI_data_archive/datasetIngestor -ingest -noninteractive -autoarchive-token {api_token}

    command_for_script = f"./datasetIngestor -ingest -noninteractive -autoarchive -token {api_token} " \
                         f"metadata_{folder_basename}_a-35297.json " \
                         f"filelisting_{folder_basename}.txt \n"
    return command_for_script


def generate_ingest_script(script_full_path, command):
    f = open(script_full_path, "a")
    f.write(command)
    f.close()


def generate_command_for_subfolder(
        folder_name,
        description,
        folder_contents,
):
    """
    Generate archiving files for a subfolder
    """
    print(email)
    cmd = write_json_and_txt(generated_files_dir, base_dir, folder_name, description,
                             folder_contents, name, email, token, name_prefix)
    generate_ingest_script(f"{generated_files_dir}/{commands_file_name}", cmd)


def create_command_file():
    """
    create an empty commands file
    """
    f = open(f"{generated_files_dir}/{commands_file_name}", "w")
    f.close()


def generate_all(folders):
    """
    Generate the commands for all the folders
    """
    for folder_path, folder_data in folders.items():
        folder_name = Path(folder_path).name
        folder_contents = [Path(file).name for file in folder_data["contents"]]
        description = folder_data["description"]
        generate_command_for_subfolder(folder_name, description, folder_contents)


def setup_config(
        tmp_email=email,
        tmp_name=name,
        tmp_token=token,
        tmp_name_prefix=name_prefix,
        tmp_generated_files_dir=generated_files_dir,
        tmp_base_dir=base_dir,
        tmp_commands_file_name=commands_file_name
):
    """
    Setup the global variables for the archive script
    """
    global email, name, token, name_prefix, generated_files_dir, base_dir, commands_file_name
    email = tmp_email
    name = tmp_name
    token = tmp_token
    name_prefix = tmp_name_prefix
    generated_files_dir = tmp_generated_files_dir
    base_dir = tmp_base_dir
    commands_file_name = tmp_commands_file_name


##
##
##
def generate_manually():
    sub_folders = [f.path for f in os.scandir(base_dir) if f.is_dir()]
    n_sub_folders = len(sub_folders)

    f = open(f"{generated_files_dir}/{commands_file_name}", "w")
    f.close()

    for i_sub_folder, sub_folder in enumerate(sub_folders):
        folder_name = os.path.basename(os.path.normpath(sub_folder))
        folder_contents = os.listdir(sub_folder)
        to_back_up = input(f"\n[{i_sub_folder + 1} / {n_sub_folders}] Backup {folder_name} ? (y/n)\n >>> ")
        # to_back_up = True
        if to_back_up in ["y", "Y", "yes", "Yes", "YES"]:
            description = input(
                f"[{i_sub_folder + 1}/{n_sub_folders}] Write description for folder: {folder_name}\n >>> ")
            cmd = write_json_and_txt(generated_files_dir, base_dir, folder_name, description,
                                     folder_contents, name, email, token, name_prefix)
            generate_ingest_script(f"{generated_files_dir}/{commands_file_name}", cmd)
        else:
            print(f"==== SKIPPING: {sub_folder} ====\n")


if __name__ == "__main__":
    generate_manually()
