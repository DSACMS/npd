# PuffinPyPipe
A Python Library that uses CSViper to import Public Use Files (PUFs) into PostGreSQL

* The subdirectories are for the various Public Use Files. They are self-contained scripts created by [CSViper](https://github.com/ftrotter/csviper).
* The .gitignore will assume that any ./?/?/data subdirectory is excluded, so that it is safe to have the data in the project tree. 
* We are also assuming that the database credentials will live in .env in the parent directory. 
