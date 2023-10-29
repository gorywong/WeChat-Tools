import ctypes
import hmac
import sqlite3
import sys
from hashlib import pbkdf2_hmac
from pathlib import Path

import pymem
from Crypto.Cipher import AES
from pymem.exception import CouldNotOpenProcess, ProcessNotFound
from win32api import HIWORD, LOWORD, GetFileVersionInfo

from config import DECRYPTED_FILE_SUFFIX, TEMP_DIR_PATH
from utils import logger, merge_sqlite_db


class Wechat:
    def __init__(self, wxid: str):
        self.__wxid = wxid
        self.__chat_db_path = self.home_path / "Msg/MicroMsg.db"
        self.__message_db_path = TEMP_DIR_PATH / "messages.db"
        self.__decrypted_chat_db_path = (
            TEMP_DIR_PATH / self.__chat_db_path.with_suffix(DECRYPTED_FILE_SUFFIX).name
        )
        self.__message_db_path_list = [
            path
            for path in (self.home_path / "Msg/Multi").iterdir()
            if path.is_file() and path.suffix == ".db" and path.name.startswith("MSG")
        ]
        self.__decrypted_message_db_path_list = [
            TEMP_DIR_PATH / path.with_suffix(DECRYPTED_FILE_SUFFIX).name
            for path in self.__message_db_path_list
        ]

        self.crack_key()

    def crack_key(self):
        """获取 key 和 key_address"""
        key_bytes = b"-----BEGIN PUBLIC KEY-----\n..."
        public_key_list = pymem.pattern.pattern_scan_all(
            self.process.process_handle, key_bytes, return_multiple=True
        )
        if not public_key_list:
            logger.warn("无法找到公钥")
            return

        key_address_list = self.get_key_address_list(public_key_list)
        if not key_address_list:
            logger.warn("无法找到密钥的地址")
            return

        key_offset = 0x8C if self.architecture == 32 else 0xD0
        for key_address in key_address_list:
            key_length = self.process.read_uchar(key_address - key_offset)
            if self.architecture == 32:
                key = self.process.read_bytes(
                    self.process.read_int(key_address - 0x90), key_length
                )
            else:
                key = self.process.read_bytes(
                    self.process.read_longlong(key_address - 0xD8), key_length
                )
            if len(key) == 32:
                self._key_address = key_address
                self._key = key

    def memory_search(parent: bytes, child: bytes) -> list[int]:
        offset = []
        index = -1
        while True:
            index = parent.find(child, index + 1)
            if index == -1:
                break
            offset.append(index)
        return offset

    def get_key_address_list(self, public_key_list):
        """获取 key 的地址"""
        key_address = []
        buffer = self.process.read_bytes(self.dll_base_address, self.dll_size)
        byte_length = 4 if self.architecture == 32 else 8
        for public_key_address in public_key_list:
            key_bytes = public_key_address.to_bytes(
                byte_length, byteorder="little", signed=True
            )
            offset = self.memory_search(buffer, key_bytes)
            if not offset:
                continue
            offset[:] = [x + self.dll_base_address for x in offset]
            key_address += offset

        return key_address

    @property
    def process(self):
        if getattr(self, "_process", None) is None:
            try:
                self._process = pymem.Pymem("WeChat.exe")
            except ProcessNotFound:
                print("微信进程未启动")
                sys.exit(-1)
            except CouldNotOpenProcess:
                print("没有权限")
                sys.exit(-1)
        return self._process

    @property
    def dll(self):
        """WeChatWin.dll"""
        if getattr(self, "_dll", None) is None:
            self._dll = pymem.process.module_from_name(
                self.process.process_handle, "WeChatWin.dll"
            )
        return self._dll

    @property
    def dll_base_address(self):
        """WeChatWin.dll 在内存中的基址"""
        return self.dll.lpBaseOfDll

    @property
    def dll_size(self):
        """WeChatWin.dll 在内存中的空间长度"""
        return self.dll.SizeOfImage

    @property
    def architecture(self):
        if getattr(self, "_optinal_header_size", None) is None:
            address = (
                self.dll_base_address
                + self.process.read_int(self.dll_base_address + 60)
                + 4
                + 16
            )
            self._optinal_header_size = self.process.read_short(address)
        if self._optinal_header_size == 0xF0:
            return 64
        return 32

    @property
    def key(self):
        if getattr(self, "_key", None) is None:
            self.crack_key()
        return self._key

    @property
    def key_address(self):
        if getattr(self, "_key_address", None) is None:
            self.crack_key()
        return self._key_address

    @property
    def version(self):
        """当前运行的微信版本"""
        if getattr(self, "_version", None) is None:
            wechat_win_dll_path = next(
                (
                    m.filename
                    for m in self.process.list_modules()
                    if m.filename.endswith("WeChatWin.dll")
                ),
                None,
            )
            if not wechat_win_dll_path:
                raise RuntimeError("Cannot find WeChatWin.dll")

            version_info = GetFileVersionInfo(wechat_win_dll_path, "\\")
            msv = version_info["FileVersionMS"]
            lsv = version_info["FileVersionLS"]
            self._version = f"{HIWORD(msv)}.{LOWORD(msv)}.{HIWORD(lsv)}.{LOWORD(lsv)}"

        return self._version

    @property
    def wxid(self):
        """当前登陆账号的 wxid"""
        # length = self.process.read_int(self.key_address - 0x44)
        # address = self.process.read_int(self.key_address - 0x54)
        # wxid = self.process.read_bytes(address, length)
        # return wxid
        return self.__wxid

    @property
    def username(self):
        """当前登陆账号的 username"""
        # length = self.process.read_int(self.key_address - 0x5C)
        # address = self.process.read_int(self.key_address - 0x6C)
        # username = self.process.read_bytes(address, length)
        # return username.decode()
        return ""

    @property
    def home_path(self):
        """存储微信文件的文件夹路径"""
        if getattr(self, "_directory_path", None) is None:
            config = (
                Path.home()
                / "AppData/Roaming/Tencent/WeChat/All Users/config/3ebffe94.ini"
            ).read_text(encoding="utf-8")
            if config == "MyDocument:":
                self._directory_path = (
                    Path.home() / f"Documents/WeChat Files/{self.wxid}"
                )
            else:
                self._directory_path = (
                    Path(config) / f"Documents/WeChat Files/{self.wxid}"
                )
        return self._directory_path

    @property
    def chat_db_path(self):
        """存储联系人的数据库路径"""
        self.decrypt_db(self.__chat_db_path)
        return self.__decrypted_chat_db_path

    @property
    def message_db_path(self):
        """存储聊天记录的数据库路径"""
        for path in self.__message_db_path_list:
            self.decrypt_db(path)
        merge_sqlite_db(self.__message_db_path, self.__decrypted_message_db_path_list)
        return self.__message_db_path

    @property
    def chat_list(self):
        """格式 (wxid, user_id, alias, username)"""
        conn = sqlite3.connect(self.chat_db_path)
        cursor = conn.execute("SELECT UserName, Alias, Remark, NickName from Contact")
        output = cursor.fetchall()
        return output

    def decrypt_db(self, path: Path | str):
        KEY_SIZE = 32
        DEFAULT_ITER = 64000
        DEFAULT_PAGESIZE = 4096  # 4048 数据 + 16IV + 20 HMAC + 12
        SQLITE_FILE_HEADER = bytes("SQLite format 3", encoding="ASCII") + bytes(
            1
        )  # SQLite 文件头
        if isinstance(path, str):
            path = Path(path)

        blist = path.read_bytes()
        salt = blist[:16]  # 前 16 字节为 salt
        key = pbkdf2_hmac("sha1", self.key, salt, DEFAULT_ITER, KEY_SIZE)

        page1 = blist[16:DEFAULT_PAGESIZE]  # 丢掉 salt

        mac_salt = bytes([x ^ 0x3A for x in salt])
        mac_key = pbkdf2_hmac("sha1", key, mac_salt, 2, KEY_SIZE)

        hash_mac = hmac.new(mac_key, digestmod="sha1")
        hash_mac.update(page1[:-32])
        hash_mac.update(bytes(ctypes.c_int(1)))

        if hash_mac.digest() != page1[-32:-12]:
            raise RuntimeError("解密失败，密码错误")

        pages = [
            blist[i : i + DEFAULT_PAGESIZE]
            for i in range(DEFAULT_PAGESIZE, len(blist), DEFAULT_PAGESIZE)
        ]
        pages.insert(0, page1)  # 把第一页补上
        with open(
            TEMP_DIR_PATH / path.with_suffix(DECRYPTED_FILE_SUFFIX).name, "wb"
        ) as f:
            f.write(SQLITE_FILE_HEADER)  # 写入文件头
            for i in pages:
                t = AES.new(key, AES.MODE_CBC, i[-48:-32])
                f.write(t.decrypt(i[:-48]))
                f.write(i[-48:])


if __name__ == "__main__":
    wechat = Wechat()
    print(wechat.version)
    print(wechat.architecture)
    print(wechat.key_address)
    print(wechat.key)
    print(wechat.wxid)
    print(wechat.username)
