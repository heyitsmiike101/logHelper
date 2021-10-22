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
