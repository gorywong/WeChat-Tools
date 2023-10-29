from pathlib import Path

OUTPUT_DIR_PATH = Path(__file__).parent.parent / "output"
TEMP_DIR_PATH = Path(__file__).parent.parent / "temp"
DECRYPTED_FILE_SUFFIX = ".db"

OUTPUT_DIR_PATH.mkdir(exist_ok=True)
TEMP_DIR_PATH.mkdir(exist_ok=True)
EXPORT_FIELDS = [
    # "Id",
    "TalkerId",
    "MsgSvrID",
    "Type",
    "SubType",
    "IsSender",
    "CreateTime",
    "Sequence",
    "StatusEx",
    "FlagEx",
    "Status",
    "MsgServerSeq",
    "MsgSequence",
    "StrTalker",
    "StrContent",
    "DisplayContent",
    # "Reserved0",
    # "Reserved1",
    # "Reserved2",
    # "Reserved3",
    # "Reserved4",
    # "Reserved5",
    # "Reserved6",
    "CompressContent",
    # "BytesExtra",
    # "BytesTrans",
]
