import os, json, time
import shutil, hashlib
import zipfile, py7zr  # pip install py7zr
import re

shutil.register_unpack_format("7zip", [".7z"], py7zr.unpack_7zarchive)

LogCleanerVersion = "V2.0"
# Log unzipper.  Puts all zips into a single folder.  Once complete, there will be no zips or folders in the output folder.
USE_CONFIG_FILE = (
    True  # If false, the below variables are used. Otherwise a config file is used.
)
INITIAL_LOG_DIRECTORY = (
    "logs"  # A folder that the logs are stored in. These files will not be changed.
)
ZIP_OUTPUT = "unzipped_logs"  # The output where the unzipped files will go.
KEEP_FILETYPES = [
    "evtx"
]  # , "txt", "log", "log1", "log2", "xlsx", "xls", "csv", "dat"]
MINIMUM_FILE_SIZE_BYTES = (
    69640  # Minimum file size to keep a file. To keep all, set to zero.
)
IGNORE_FILES = ["FileXYZ.abc", "FileABC.xyz"]


def main():
    """Runs the Show"""
    print("Running Version", LogCleanerVersion)
    if USE_CONFIG_FILE:
        config = read_settings_JSON()
        global INITIAL_LOG_DIRECTORY, ZIP_OUTPUT, KEEP_FILETYPES, MINIMUM_FILE_SIZE_BYTES, IGNORE_FILES
        INITIAL_LOG_DIRECTORY = config["INITIAL_LOG_DIRECTORY"]
        ZIP_OUTPUT = config["ZIP_OUTPUT"]
        KEEP_FILETYPES = config["KEEP_FILETYPES"]
        MINIMUM_FILE_SIZE_BYTES = config["MINIMUM_FILE_SIZE_BYTES"]
        IGNORE_FILES = config["IGNORE_FILES"]

        IGNORE_FILES = [x.lower() for x in IGNORE_FILES]

        print_config_settings(config)
        print()
        # x = input("Press enter to GOoOo!!!")

    start_time = time.time()
    create_directories(ZIP_OUTPUT)
    modify_files(INITIAL_LOG_DIRECTORY, ZIP_OUTPUT, modify_files=False)
    remove_unwanted_filetypes(ZIP_OUTPUT, KEEP_FILETYPES)
    remove_unwanted_files(ZIP_OUTPUT, IGNORE_FILES)
    flatten_directory(ZIP_OUTPUT, ZIP_OUTPUT)
    delete_empty_directories(ZIP_OUTPUT)

    zipcount = count_zips(ZIP_OUTPUT)
    while zipcount > 0:
        modify_files(ZIP_OUTPUT, ZIP_OUTPUT, modify_files=True)
        remove_unwanted_filetypes(ZIP_OUTPUT, KEEP_FILETYPES)
        remove_unwanted_files(ZIP_OUTPUT, IGNORE_FILES)
        flatten_directory(ZIP_OUTPUT, ZIP_OUTPUT)
        zipcount = count_zips(ZIP_OUTPUT)
        delete_empty_directories(ZIP_OUTPUT)

    file_list = create_file_list(ZIP_OUTPUT)
    file_list = remove_small_files_by_bytes(file_list, MINIMUM_FILE_SIZE_BYTES)
    remove_duplicates(file_list)
    file_list = create_file_list(ZIP_OUTPUT)
    FileCount = len(file_list)

    end_time = time.time()
    print()
    min, sec = divmod(end_time - start_time, 60)
    print(
        "Time to run:", "{:.0f}".format(min), "minutes", "{:.0f}".format(sec), "seconds"
    )
    print("Total files after cleaning:", FileCount)
    x = input("\n\nPress enter to quit")


def remove_unwanted_files(dir: str, files: list):
    """Remove unawanted filetypes by specifying a list of file types to keep."""

    current_directory_list = os.listdir(dir)

    for result in current_directory_list:
        if os.path.isdir(os.path.join(dir, result)):
            remove_unwanted_files(os.path.join(dir, result), files)
        else:
            if result.lower() in files:
                print("DELETING:", result)
                os.remove(os.path.join(dir, result))


def flatten_directory(search_source: str, flat_destination_dir: str):
    """Recursively walk the directories and files. Calls itself when theres a new directory found. Moves all files from search_source to flat_destination_dir"""
    print("Flattening Directory")
    current_directory_list = os.listdir(search_source)
    zip_list = []

    for result in current_directory_list:
        print("Working Directory:", search_source)
        # if result is a directory, recursively call that directory.
        if os.path.isdir(os.path.join(search_source, result)):
            flatten_directory(os.path.join(search_source, result), flat_destination_dir)
        # Else, the results is a file. Move it to the flat_destination_dir
        else:
            save_filename = check_file_exists(
                os.path.join(flat_destination_dir, result)
            )
            print("Saving to:", save_filename)
            try:
                shutil.move(os.path.join(search_source, result), save_filename)
            except:
                pass


def print_config_settings(data: dict):
    print("************************************************************")
    print("Config File Settings")
    print("************************************************************")
    print("TOP_DIRECTORY          :", data["INITIAL_LOG_DIRECTORY"])
    print("ZIP_OUTPUT             :", data["ZIP_OUTPUT"])
    print("KEEP_FILETYPES         :", data["KEEP_FILETYPES"])
    print("MINIMUM_FILE_SIZE_BYTES:", data["MINIMUM_FILE_SIZE_BYTES"])
    print("IGNORE_FILES           :", data["IGNORE_FILES"])
    print()


def read_settings_JSON() -> dict:
    """Reads config.txt. if it does not exists, it creates it and closes the program."""
    filename = "config.json"

    data = {
        "INITIAL_LOG_DIRECTORY": "logs",
        "ZIP_OUTPUT": ZIP_OUTPUT,
        "KEEP_FILETYPES": KEEP_FILETYPES,
        "extra filetypes": [
            "evtx",
            "txt",
            "log",
            "log1",
            "log2",
            "xlsx",
            "xls",
            "csv",
            "dat",
        ],
        "MINIMUM_FILE_SIZE_BYTES": MINIMUM_FILE_SIZE_BYTES,
        "IGNORE_FILES": IGNORE_FILES,
    }

    # If the filename is found, overwrite the default data, otherwise use the file.
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
        json_file.close()

    except:
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=2)
        outfile.close()
        print_config_settings(data)
        x = input(
            "Created config.txt. Open the file to customize settings or run the application again to use default settings. (ENTER to quit)"
        )
        exit()

    return data


def remove_small_files_by_bytes(file_list: list, minimum_size_bytes: int) -> list:
    """Removes small files and returns a new file list without the small files"""
    new_file_list = []

    for i in file_list:
        if os.path.getsize(i) < minimum_size_bytes:
            os.remove(i)
            print("Removing File:", i)
        else:
            new_file_list.append(i)

    return new_file_list


def remove_duplicates(file_list: list):
    """Removes the duplicate files based on a list of files."""
    file_hash_list = []
    for i in file_list:
        hash = generate_hash(i)
        file_hash_list.append([i, hash])

    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):

            if file_hash_list[i][1] == file_hash_list[j][1]:
                print("Removing Duplicate file")
                try:
                    os.remove(file_hash_list[j][0])
                except:
                    print("File already removed")


def generate_hash(filename: str) -> bytes:
    """Generate a hash based on a filename and returns a string md5.digest"""
    print("Generating Hash\n", filename)
    block_size = 1024
    hash = hashlib.md5()
    with open(filename, "rb") as file:
        block = file.read(block_size)
        while len(block) > 0:
            hash.update(block)
            block = file.read(block_size)
    return hash.digest()


def create_file_list(dir: str) -> str:
    """Create a list of files"""
    file_list = []
    current_directory_list = os.listdir(dir)
    for result in current_directory_list:
        if os.path.isdir(os.path.join(dir, result)):
            file_list += create_file_list(os.path.join(dir, result))
        else:
            file_list.append(os.path.join(dir, result))
    return file_list


def remove_unwanted_filetypes(dir: str, keep_filetype_list: list):
    """Remove unawanted filetypes by specifying a list of file types to keep."""
    keep_filetype_list.append("zip")
    keep_filetype_list.append("7z")
    current_directory_list = os.listdir(dir)

    for result in current_directory_list:
        if os.path.isdir(os.path.join(dir, result)):
            remove_unwanted_filetypes(os.path.join(dir, result), keep_filetype_list)
        else:
            file_extension = ""
            if "." in result:
                file_extension = result.split(".")[-1]
            if file_extension in keep_filetype_list:
                continue
            else:
                os.remove(os.path.join(dir, result))


def count_zips(dir: str):
    """Takes in a directory to search for zips, then returns a count of zips."""
    zip_count = 0
    current_directory_list = os.listdir(dir)
    for result in current_directory_list:
        if os.path.isdir(os.path.join(dir, result)):
            zip_count += count_zips(os.path.join(dir, result))
        else:
            file_extension = result.split(".")[-1]
            if file_extension == "zip":
                zip_count += 1
            elif file_extension == "7z":
                zip_count += 1
    return zip_count


def modify_files(dir: str, destination: str, modify_files: bool = False):
    """Recursively walk the directories and files. Calls itself when theres a new directory found. If modify files is True, it will delete zips after unzipping and move regular files rather than copy."""
    current_directory_list = os.listdir(dir)
    zip_list = []

    for result in current_directory_list:
        print("Working Directory:", dir)
        # if result is a directory, recursively call that directory.
        if os.path.isdir(os.path.join(dir, result)):
            modify_files(os.path.join(dir, result), destination, modify_files)
        # Else, the results is a file, unzip it or un7ip it. If its any other file, copy/move it over.
        elif not result.lower() in IGNORE_FILES:
            # unzipping
            file_extension = result.split(".")[-1]
            if file_extension == "zip":
                unzip_file(dir, result, destination, modify_files)
            elif file_extension == "7z":
                un7zip_file(dir, result, destination, modify_files)
            elif file_extension in KEEP_FILETYPES:
                if modify_files:
                    move_file(dir, result, destination)
                else:
                    copy_file(dir, result, destination)


def delete_empty_directories(dir: str):
    """Delete Directories if they are empty"""
    current_directory_list = os.listdir(dir)

    for result in current_directory_list:
        result_dir = os.path.join(dir, result)
        if os.path.isdir(result_dir):
            delete_empty_directories(result_dir)
            try:
                print("Deleting directory:", result_dir)
                os.rmdir(result_dir)
            except:
                print(
                    "#########################################################################"
                )
                print("Error path not empty when deleting directory:", result_dir)
                print(
                    "#########################################################################"
                )


def create_directories(directories: str):
    """Builds out one or more directories deep if they don't exist."""
    directories = os.path.normpath(directories)
    directory_list = directories.split(os.sep)

    # Builds the directory one level at a time to prevent errors.
    dir_string = ""
    for i in directory_list:
        dir_string = os.path.join(dir_string, i)
        if not os.path.isdir(dir_string):
            os.mkdir(dir_string)


def unzip_file(
    dir: str, filename: str, zip_destination: str, delete_after_complete: bool = False
):
    """Unzips a file in the dir+filename then places it in the zip_destination"""
    print("Unzipping:", os.path.join(dir, filename))
    unzip_name = filename.replace(".zip", "")
    unzip_save = os.path.join(zip_destination, unzip_name)
    print("Saving to:", unzip_save)

    # checks if file exists in destination.  if so, it renames the filename.
    unzip_save = check_file_exists(unzip_save)

    with zipfile.ZipFile(os.path.join(dir, filename), "r") as zip_obj:
        list_of_filenames = zip_obj.namelist()

        for zipfile_filename in list_of_filenames:
            # unzipfile_filename = zipfile_filename.replace(".zip","")
            unzipfile_filename = os.path.join(unzip_save, zipfile_filename)
            file_errors = False
            file_extension = ""
            file_extension = unzipfile_filename.split(".")[-1]
            if file_extension in KEEP_FILETYPES or file_extension in ["zip", "7z"]:
                try:
                    zip_obj.extract(zipfile_filename, unzip_save)
                except:
                    file_errors = True
                    print(
                        "#########################################################################"
                    )
                    print("Error unzipping file:", os.path.join(dir, zipfile_filename))
                    print(
                        "Most Likely the file path is too long for python.\nPlace logs and program as close to root as possible."
                    )
                    print(
                        "#########################################################################"
                    )
        zip_obj.close()

        if delete_after_complete and not file_errors:
            try:
                os.remove(os.path.join(dir, filename))
            except:
                global IGNORE_FILES
                IGNORE_FILES.append(filename.lower())


def un7zip_file(
    dir: str, filename: str, zip_destination: str, delete_after_complete: bool = False
):
    """Un7zips a file in the dir+filename then places it in the zip_destination"""
    print("Un7zipping:", os.path.join(dir, filename))
    unzip_name = filename.replace(".7z", "")
    unzip_save = os.path.join(zip_destination, unzip_name)

    # checks if file exists in destination.  if so, it renames the filename.
    unzip_save = check_file_exists(unzip_save)
    print("Saving to:", unzip_save)

    try:
        shutil.unpack_archive(os.path.join(dir, filename), unzip_save)
    except:
        print(
            "#########################################################################"
        )
        error_directory = "ErrorFiles"
        print("Error un7zipping file:", os.path.join(dir, filename))
        print(
            "#########################################################################"
        )

    if delete_after_complete:
        try:
            os.remove(os.path.join(dir, filename))
        except:
            global IGNORE_FILES
            IGNORE_FILES.append(filename.lower())


def check_file_exists(path: str):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        filename = re.sub(r"(\([0-9]+\))$", "", filename)
        path = filename + "(" + str(counter) + ")" + extension
        if ")(" in path:
            x = print("HERE IT IS")

        counter += 1

    return path


def move_file(dir: str, filename: str, destination: str):
    print("Moving filename:", os.path.join(dir, filename))
    # checks if filename exists in destination.  if so, it renames the
    # filename.
    # if the file is already in the destination, skip it.
    if dir == destination:
        return
    save_filename = check_file_exists(os.path.join(destination, filename))
    print("Saving to:", save_filename)

    try:
        shutil.move(os.path.join(dir, filename), save_filename)
    except:
        print(
            "#########################################################################"
        )
        print("Error copying file:", os.path.join(dir, filename))
        print(
            "Most Likely the file path is too long for python.\nPlace logs and program as close to root as possible."
        )
        print(
            "#########################################################################"
        )


def copy_file(dir: str, filename: str, destination: str):
    """checks if filename exists in destination.  if so, it renames the filename"""
    print("Copying filename:", os.path.join(dir, filename))
    save_filename = check_file_exists(os.path.join(destination, filename))
    print("Saving to:", save_filename)

    try:
        shutil.copy2(os.path.join(dir, filename), save_filename)
    except:
        print(
            "#########################################################################"
        )
        print("Error copying file:", os.path.join(dir, filename))
        print(
            "Most Likely the file path is too long for python.\nPlace logs and program as close to root as possible."
        )
        print(
            "#########################################################################"
        )


if __name__ == "__main__":
    main()
