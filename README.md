# logHelper

LogHelper takes a directory and unzips and copies files into a new directory to easily ingest into a log analyzer.  
* The orginal directory is not changed
* Nothing in the unzipped destionation directory will be in subdirectories.

Features
* Unzip zip and 7zip files
* Multithreading for the inital unzipping
* Recursively unzips zip files within zip files
* Specify a minimum file size to keep (in Bytes)
* Specify filetypes to keep

Requirements
* pip install py7zr


To Run
<br />
Run without a config file.

* USE_CONFIG_FILE         = True        # If false, the below variables are used. Otherwise a config file is used.
* TOP_DIRECTORY           = "logs"      # A folder that the logs are stored in. These files will not be changed.
* ZIP_OUTPUT              = "Unzip"     # The output where the unzipped files will go.
* USE_THREADING           = True        # Threading for unzipping files.
* KEEP_FILETYPES          = ["evtx"]    #, "txt", "log", "log1", "log2", "xlsx", "xls", "csv", "dat"]
* MINIMUM_FILE_SIZE_BYTES = 69640       # Minimum file size to keep a file. To keep all, set to zero.
<br />
Run with a config file. Set USE_CONFIG_FILE to True. Once the program runs, if the file does not exist it will create config.json. The below config is the default settings.

<br />'TOP_DIRECTORY': "logs",
<br />'ZIP_OUTPUT': 'UnzippeTh',
<br />'USE_THREADING': True,
'KEEP_FILETYPES': ["evtx"],
<br />'MINIMUM_FILE_SIZE_BYTES': 69640
