# SCRATCH-TOOLS
most of these only work on MacOS


------------------------------------
EXR Compression Updater v3.\
Injects compression type metadata to exr files in Assimilate Scratch.

Add as Application type Custom command and make sure "Require Shot Selection" is ON , select one or more shots in a construct and use the custom command in the tools menu.\
The compression type of the EXRs are now added to the metadata stack.


Make sure you update the script paths before using.\
External file paths.\
LOG_FILE = Path.home() / "your-path-here/updater_log.txt"\
DEFAULT_OUTPUT_FILE = Path.home() / "your-path-here/updated_metadata.xml"\
SCRATCH_CMD_LOG = Path.home() / "your-path-here/scratch_cmd_log.txt"


------------------------------------

Assimilator Debug Launcher.\
Launches Assimilator/Scratch with the debug flag.\
Opens terminal that tails the current log.\
MacOS only.



------------------------------------

OmniScope Scratch Scripts.\
These two scripts open and close omniscope along with scratch.\
Add as System Event type Custom Commands.\
ScopeOpen.py as Application Start\
ScopeClose.py as Application Close

------------------------------------

backup assimilator.\
Copies your Project, Settings and Users directories.\
Make sure to edit the filepaths.

SOURCE_FOLDERS = [
    "/Library/Application Support/Assimilator/Project",\
    "/Library/Application Support/Assimilator/Settings",\
    "/Library/Application Support/Assimilator/Users",\
]

DESTINATION = Path("/your/path/here/ScratchBackups")


------------------------------------
