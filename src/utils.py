import logging
import sqlite3

logger = logging.getLogger("WeChat")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


def merge_sqlite_db(save_path, dbs):
    conn_new = sqlite3.connect(save_path)
    cursor_new = conn_new.cursor()

    # 创建一个新表用于保存合并后的数据
    cursor_new.execute(
        """CREATE TABLE IF NOT EXISTS MSG (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            TalkerId INT,
            MsgSvrID INT,
            Type INT,
            SubType INT,
            IsSender INT,
            CreateTime INT,
            Sequence INT,
            StatusEx INT,
            FlagEx INT,
            Status INT,
            MsgServerSeq INT,
            MsgSequence INT,
            StrTalker TEXT,
            StrContent TEXT,
            DisplayContent TEXT,
            Reserved0 INT,
            Reserved1 INT,
            Reserved2 INT,
            Reserved3 INT,
            Reserved4 INT,
            Reserved5 INT,
            Reserved6 INT,
            CompressContent BLOB,
            BytesExtra BLOB,
            BytesTrans BLOB
        )"""
    )

    for database_file in dbs:
        conn_temp = sqlite3.connect(database_file)
        cursor_temp = conn_temp.cursor()
        cursor_temp.execute(
            "SELECT TalkerId, MsgSvrID, Type, SubType, IsSender, CreateTime, Sequence, StatusEx, FlagEx, Status, MsgServerSeq, MsgSequence, StrTalker, StrContent, DisplayContent, Reserved0, Reserved1, Reserved2, Reserved3, Reserved4, Reserved5, Reserved6, CompressContent, BytesExtra, BytesTrans FROM MSG"
        )
        rows = cursor_temp.fetchall()
        cursor_new.executemany(
            "INSERT INTO MSG (TalkerId, MsgSvrID, Type, SubType, IsSender, CreateTime, Sequence, StatusEx, FlagEx, Status, MsgServerSeq, MsgSequence, StrTalker, StrContent, DisplayContent, Reserved0, Reserved1, Reserved2, Reserved3, Reserved4, Reserved5, Reserved6, CompressContent, BytesExtra, BytesTrans) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn_temp.close()

    conn_new.commit()
    conn_new.close()
