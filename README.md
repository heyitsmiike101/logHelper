# logHelper

## General
LogHelper takes a directory and unzips (zips and 7zips) and copies files into a new directory to quickly ingest into a log analyzer.  
* The original directory is not changed (original zips are left and all changes are made in the ZIP OUTPUT)
* LogHelper places all files in the destination directory without subdirectories.

## Features
* Unzip zip and 7zip files
* Move files in many subdirectories into a single directory for easy ingestion
* Recursively unzips zip files within zip files
* Specify a minimum file size to keep (in Bytes)
* Specify filetypes to keep
* Specify filenames to ignore

## Requirements
* Windows or Linux
* Python 3.7 +
* pip install py7zr

## Usage Guide
### Run
To run, open terminal/cmd in the directory and type:
* Windows: ```python LogHelper.py```
* Linux: ```python3 LogHelper.py ```

### Initial Run
The first run of the script will create a config file with the options set below. Edit the config or use the default values shown below. If using the default values, it is required to make a directory "logs" in the same folder as the script. This folder is where you place all files that you plan to unzip and analyze.

* INITIAL_LOG_DIRECTORY   = "logs"          # The initial folder for logs that are ingested. Place All logs/zips in this location.
* ZIP_OUTPUT              = "Unzip"         # The output where the unzipped files will go. This folder will auto-create if it does not exist.
* KEEP_FILETYPES          = ["evtx"]        # Filetypes that the script will keep. All other files will be deleted in ZIP_OUTPUT automatically.
* MINIMUM_FILE_SIZE_BYTES = 69640           # Minimum file size to keep a file. To keep all, set to zero. An example use case would be to skip empty evtx files.
* IGNORE_FILES            = ["FileXYZ.abc"] #Ignores any files in this list (case-insensitive).
### Config Examples
#### Default Config
The config below shows the layout of the config file with default values. One value to note is the list for KEEP_FILETYPES. While there is only one choice, it is still in a list and any filetype can be added. Files saved in "Logs" will be ingested and output into unzipped_logs. The INITIAL_LOG_DIRECTORY needs to be created by the user but the ZIP_OUTPUT will be automatically created.
```
{
  "INITIAL_LOG_DIRECTORY": "logs",
  "ZIP_OUTPUT": "unzipped_logs",
  "KEEP_FILETYPES": [
    "evtx"
  ],
  "MINIMUM_FILE_SIZE_BYTES": 69640,
  "IGNORE_FILES": [
    "FileXYZ.abc", 
    "FileABC.xyz"
  ]
}
```

#### Modified Config
The config below shows the layout of the config file with KEEP_FILETYPES set to preserve types("evtx","txt", "log", "log1", "log2", "xlsx", "xls", "csv", "dat") but remove any files named FileXYZ.abc and FileABC.xyz.
```
{
  "INITIAL_LOG_DIRECTORY": "logs",
  "ZIP_OUTPUT": "unzipped_logs",
  "KEEP_FILETYPES": [
    "evtx",
    "txt",
    "log",
    "log1",
    "log2",
    "xlsx",
    "xls",
    "csv",
    "dat"
  ],
  "MINIMUM_FILE_SIZE_BYTES": 69640,
  "IGNORE_FILES": [
    "FileXYZ.abc", 
    "FileABC.xyz"
  ]
}
```