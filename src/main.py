import csv
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Annotated

import typer

from config import EXPORT_FIELDS, OUTPUT_DIR_PATH, TEMP_DIR_PATH
from utils import logger
from wechat import Wechat

app = typer.Typer(help="Windows PC 端微信分析工具")


@app.command()
def dump(
    wxid: Annotated[
        str,
        typer.Argument(help="你自己的 wxid"),
    ],
    friend: Annotated[
        str,
        typer.Option(help="好友的【微信名】或是【备注】"),
    ],
    json: Annotated[bool, typer.Option(help="以 json 格式导出", prompt="需要以 json 格式导出吗？")],
    csv: Annotated[bool, typer.Option(help="以 csv 格式导出", prompt="需要以 csv 格式导出吗？")],
    output_dir: Annotated[
        str,
        typer.Option(help="导出文件的存储文件夹路径，默认在程序同目录的 output 文件夹下"),
    ] = OUTPUT_DIR_PATH,
):
    """
    导出与好友 FRIEND 的所有聊天记录
    """
    wechat = Wechat(wxid)

    if not wechat.message_db_path.exists():
        logger.info("没有发现任何聊天记录")
        return
    logger.info(f"所有聊天记录数据库文件已存储到: {wechat.message_db_path}")

    conn = sqlite3.connect(wechat.message_db_path)

    for f_wxid, user_id, alias, username in wechat.chat_list:
        if friend in [f_wxid, user_id, alias, username]:
            logger.info(f"匹配到聊天: {user_id}")
            logger.info(f"微信号: {f_wxid}")
            logger.info(f"微信名: {username}")
            logger.info(f"备注: {alias}")
            try:
                cursor = conn.execute(
                    "SELECT %s from MSG WHERE StrTalker = '%s' ORDER BY CreateTime ASC"
                    % (", ".join(EXPORT_FIELDS), f_wxid)
                )
            except sqlite3.OperationalError:
                logger.error("数据库出错，请重启微信并登录后重试")
                return
            rows = cursor.fetchall()
            break
    else:
        logger.warn(f"找不到与 {friend} 的聊天记录")

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    output_filename = output_dir / f"{alias}_{username}_{f_wxid}_messages"

    if json:
        save_json(output_filename, rows)
        logger.info(f"文件已保存至 {output_filename.with_suffix('.json')}")

    if csv:
        save_csv(output_filename, rows)
        logger.info(f"文件已保存至 {output_filename.with_suffix('.csv')}")

    conn.close()


@app.command()
def dump_all(
    wxid: Annotated[
        str,
        typer.Argument(help="你自己的 wxid"),
    ],
    json: Annotated[bool, typer.Option(help="以 json 格式导出")],
    csv: Annotated[bool, typer.Option(help="以 csv 格式导出")],
    output_dir: Annotated[
        str,
        typer.Option(help="导出文件的存储文件夹路径，默认在程序同目录的 output 文件夹下"),
    ] = OUTPUT_DIR_PATH,
):
    """导出所有的聊天记录"""
    wechat = Wechat(wxid)

    if not wechat.message_db_path.exists():
        logger.info("没有发现任何聊天记录")
        return
    logger.info(f"所有聊天记录数据库文件已存储到: {wechat.message_db_path}")

    conn = sqlite3.connect(wechat.message_db_path)
    try:
        cursor = conn.execute(
            "SELECT %s from MSG ORDER BY CreateTime ASC" % ", ".join(EXPORT_FIELDS)
        )
    except sqlite3.OperationalError:
        logger.error("数据库出错，请重启微信并登录后重试")
        return
    rows = cursor.fetchall()
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    output_filename = output_dir / f"messages"

    if json:
        save_json(output_filename, rows)
        logger.info(f"JSON 文件已保存至 {output_filename.with_suffix('.json')}")

    if csv:
        save_csv(output_filename, rows)
        logger.info(f"CSV 文件已保存至 {output_filename.with_suffix('.csv')}")

    conn.close()


@app.command()
def analyze():
    """对解密出的聊天记录进行数据分析"""
    logger.warn("功能正在开发中")


@app.command()
def clean():
    """清理程序运行时产生的临时文件"""
    try:
        shutil.rmtree(TEMP_DIR_PATH)
    except PermissionError as e:
        logger.error(f"{e}，请尝试手动删除")
    logger.info("临时文件夹已删除")


def save_csv(filename: Path, rows: list):
    with open(
        filename.with_suffix(".csv"), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(EXPORT_FIELDS)
        writer.writerows(rows)


def save_json(filename: Path, rows: list):
    json_data = []

    for row in rows:
        row_data = []
        for item in row:
            if isinstance(item, bytes):
                item = str(item)
            row_data.append(item)
        json_data.append(dict(zip(EXPORT_FIELDS, row_data)))

    with open(filename.with_suffix(".json"), "w", encoding="utf-8") as jsonfile:
        json.dump(json_data, jsonfile, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    app()
