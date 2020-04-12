# Downloader
Downloads DOH Arca MODS XML. User chooses one DOH collection or all DOH collections to download, and collections are hard coded. Goals: infer collection structure; allow user to download XML for all DOH collections associated with a particular repository (e.g. all collections of Peachland Museum); use multithreading; add ability to download DC XML; make executable tool.

# Compile
In Command Prompt / Powershell (assuming a virtual environment was used, if not, change to path of pyinstaller.exe)  
`venv/Scripts/pyinstaller.exe --onefile Downloader.py -F -w`  
For other files, change Downloader.py to appropriate name.  
An easy way is to create a compile.bat file and just open it everytime you want to build the app. The compile.bat file will contain:  
`START venv/Scripts/pyinstaller.exe --onefile Downloader.py -F -w` 
