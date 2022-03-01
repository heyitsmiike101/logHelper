import os, json, sys, time, re
import shutil, hashlib, threading
import zipfile, py7zr  # pip install py7zr

LogCleanerVersion = "V1.9"
# Log unzipper.  Puts all zips into a single folder.  Once complete, there will be no zips or folders in the output folder.
USE_CONFIG_FILE = (
    True  # If false, the below variables are used. Otherwise a config file is used.
)
TOP_DIRECTORY = (
    "logs"  # A folder that the logs are stored in. These files will not be changed.
)
ZIP_OUTPUT = "Unzip"  # The output where the unzipped files will go.
USE_THREADING = True  # Threading for unzipping files.
KEEP_FILETYPES = [
    "evtx"
]  # , "txt", "log", "log1", "log2", "xlsx", "xls", "csv", "dat"]
MINIMUM_FILE_SIZE_BYTES = (
    69640  # Minimum file size to keep a file. To keep all, set to zero.
)


def main():
    """Runs the Show"""
    print("Running Version", LogCleanerVersion)
    if USE_CONFIG_FILE:
        config = read_settings_JSON()
        global TOP_DIRECTORY, ZIP_OUTPUT, USE_THREADING, KEEP_FILETYPES, MINIMUM_FILE_SIZE_BYTES
        TOP_DIRECTORY = config["TOP_DIRECTORY"]
        ZIP_OUTPUT = config["ZIP_OUTPUT"]
        USE_THREADING = config["USE_THREADING"]
        KEEP_FILETYPES = config["KEEP_FILETYPES"]
        MINIMUM_FILE_SIZE_BYTES = config["MINIMUM_FILE_SIZE_BYTES"]
        print_config_settings(config)
        print()
        # x = input("Press enter to GOoOo!!!")

    start_time = time.time()
    create_directories(ZIP_OUTPUT)
    modify_files(
        TOP_DIRECTORY,
        ZIP_OUTPUT,
        move_files=False,
        delete_zips=False,
        threading_allowed=USE_THREADING,
    )
    zipcount = count_zips(ZIP_OUTPUT)
    while zipcount > 0:
        # Threading is not allowed this time because files could be overwritten when unzipping.
        modify_files(
            ZIP_OUTPUT,
            ZIP_OUTPUT,
            move_files=True,
            delete_zips=True,
            threading_allowed=False,
        )
        zipcount = count_zips(ZIP_OUTPUT)
    # Moves final files after all unzipping.  The folders can only be deleted if empty
    modify_files(
        ZIP_OUTPUT,
        ZIP_OUTPUT,
        move_files=True,
        delete_zips=True,
        threading_allowed=False,
    )
    initialFileCount = len(create_file_list(ZIP_OUTPUT))
    remove_unwanted_filetypes(ZIP_OUTPUT, KEEP_FILETYPES)
    delete_empty_directories(ZIP_OUTPUT)
    # Remove small and duplicate files.
    file_list = create_file_list(ZIP_OUTPUT)
    FileCount1 = len(file_list)
    file_list = remove_small_files_by_bytes(file_list, MINIMUM_FILE_SIZE_BYTES)
    FileCount2 = len(file_list)
    remove_duplicates(file_list)
    FileCount3 = len(create_file_list(ZIP_OUTPUT))

    end_time = time.time()
    print()
    min, sec = divmod(end_time - start_time, 60)
    print(
        "Time to run:", "{:.0f}".format(min), "minutes", "{:.0f}".format(sec), "seconds"
    )
    print("Count of total files            :", initialFileCount)
    filesRemoved1 = initialFileCount - FileCount1
    print("Total removed unwanted filetypes:", filesRemoved1)
    filesRemoved2 = FileCount1 - FileCount2
    print("Total removed small files       :", filesRemoved2)
    filesRemoved3 = FileCount2 - FileCount3
    print("Removed duplicates              :", filesRemoved3)
    print("Total files after cleaning      :", FileCount3)
    x = input("\n\nPress enter to quit")


def print_config_settings(data: dict):
    print("************************************************************")
    print("Config File Settings")
    print("************************************************************")
    print("TOP_DIRECTORY          :", data["TOP_DIRECTORY"])
    print("ZIP_OUTPUT             :", data["ZIP_OUTPUT"])
    print("USE_THREADING          :", data["USE_THREADING"])
    print("KEEP_FILETYPES         :", data["KEEP_FILETYPES"])
    print("MINIMUM_FILE_SIZE_BYTES:", data["MINIMUM_FILE_SIZE_BYTES"])
    print()


def read_settings_JSON() -> dict:
    """Reads config.txt. if it does not exists, it creates it and closes the program."""
    filename = "config.json"

    data = {
        "TOP_DIRECTORY": "logs",
        "ZIP_OUTPUT": "UnzippeTh",
        "USE_THREADING": True,
        "KEEP_FILETYPES": ["evtx"],
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
        "MINIMUM_FILE_SIZE_BYTES": 69640,
    }

    # If the filename is found, overwrite the default data, otherwise use the file.
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
        json_file.close()

    except:
        with open(filename, "w") as outfile:
            json.dump(data, outfile)
        outfile.close()
        print_config_settings(data)
        x = input(
            "Created config.txt. Open the file to customize settigns or run the application again to use default settings. (ENTER to quit)"
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


def remove_unwanted_filetypes(dir: str, keep_filetype_list: list[str]):
    """Remove unawanted filetypes by specifying a list of file types to keep."""
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


def modify_files(
    dir: str,
    destination: str,
    move_files: bool = False,
    delete_zips: bool = False,
    threading_allowed: bool = False,
):
    """Recursively walk the directories and files and calls itself when theres a new directory found. If move files is false, they will be copied instead of moved. If threading = True, the zips will be unzipped in parrallel"""
    current_directory_list = os.listdir(dir)
    thread_list = []
    zip_list = []

    for result in current_directory_list:
        # if result is a directory, recursively call that directory.
        if os.path.isdir(os.path.join(dir, result)):
            modify_files(
                os.path.join(dir, result),
                destination,
                move_files,
                delete_zips,
                threading_allowed,
            )
        # Else, the results is a file, unzip it or un7ip it. If its any other file, copy/move it over.
        else:
            # unzipping
            file_extension = result.split(".")[-1]
            if file_extension == "zip":
                if threading_allowed:
                    print("Creating Thread")
                    thread_list.append(
                        threading.Thread(
                            target=unzip_file,
                            args=(dir, result, destination, delete_zips),
                        )
                    )
                else:
                    unzip_file(dir, result, destination, delete_zips)
            elif file_extension == "7z":
                if threading_allowed:
                    print("Creating Thread")
                    thread_list.append(
                        threading.Thread(
                            target=un7zip_file,
                            args=(dir, result, destination, delete_zips),
                        )
                    )
                else:
                    un7zip_file(dir, result, destination, delete_zips)
            # Moving/Copying files.
            elif file_extension in KEEP_FILETYPES:
                if move_files:
                    move_file(dir, result, destination)
                else:
                    copy_file(dir, result, destination)

    # Unzipping files in seperate threads if specified.
    if threading_allowed:
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()


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
    """Builds out all the directories that don't exist."""
    directories = os.path.normpath(directories)
    directory_list = directories.split(os.sep)

    # Builds the directory one level at a time to prevent errors.
    dir_string = ""
    for i in directory_list:
        dir_string = os.path.join(dir_string, i)
        if not os.path.isdir(dir_string):
            os.mkdir(dir_string)


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
            os.remove(os.path.join(dir, filename))


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
    file_errors = False

    try:
        archive = py7zr.SevenZipFile(os.path.join(dir, filename), mode="r")
        archive.extractall(path=unzip_save)
        archive.close()
    except:
        file_errors = True
        print(
            "#########################################################################"
        )
        print("Error un7zipping file:", os.path.join(dir, filename))
        print(
            "Most Likely the file path is too long for python.\nPlace logs and program as close to root as possible."
        )
        print(
            "#########################################################################"
        )

    if delete_after_complete and not file_errors:
        os.remove(os.path.join(dir, filename))


def check_file_exists(filename: str):
    """Checks if file exists. If it does, this function will pass a new file name."""

    # if the file does not exist, send back the original file name.  No need to rename.
    if not os.path.exists(filename):
        if os.path.isdir(filename):
            create_directories(filename)
        return filename

    # otherwise rename.
    file_number = 1
    file_extension = ""
    # Some files do not
    if "." in filename:
        file_extension = filename.split(".")[-1]

    while True:
        print("Renaming", file_number, end="")
        # Checks if it's a directory that needs to be renamed.
        if os.path.isdir(filename):
            new_filename = filename + "(f" + str(file_number) + ")"
        else:
            # if it's not a folder, its a file.
            # File with an extension.
            if not file_extension == "":
                new_filename = filename.replace(
                    "." + file_extension,
                    "(f" + str(file_number) + ")" + "." + file_extension,
                )

            # File without extension.
            else:
                new_filename = filename + "(f" + str(file_number) + ")"

        if not os.path.exists(new_filename):
            print()
            return new_filename

        file_number += 1


if __name__ == "__main__":
    main()
