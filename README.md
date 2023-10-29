# WeChat Tools
一个 PC 端微信的辅助工具。

## 免责声明

本工具仅供学习和技术研究使用，不得用于任何商业或非法行为，否则后果自负。

本工具的作者不对本工具的安全性、完整性、可靠性、有效性、正确性或适用性做任何明示或暗示的保证，也不对本工具的使用或滥用造成的任何直接或间接的损失、责任、索赔、要求或诉讼承担任何责任。

本工具的作者保留随时修改、更新、删除或终止本工具的权利，无需事先通知或承担任何义务。

本工具的使用者应遵守相关法律法规，尊重微信的版权和隐私，不得侵犯微信或其他第三方的合法权益，不得从事任何违法或不道德的行为。

本工具的使用者在下载、安装、运行或使用本工具时，即表示已阅读并同意本免责声明。如有异议，请立即停止使用本工具，并删除所有相关文件。

## 功能清单

- [x] 导出聊天记录
- [ ] 分析聊天记录

## 快速开始
在 Release 中下载可执行文件后，在命令行中，切换到可执行文件所在路径下，执行如下命令即可查看使用帮助。

**注意：** 运行时可能会被 Windows Defender 报毒，可以参考[将排除项添加到 Windows 安全中心](https://support.microsoft.com/zh-cn/windows/%E5%B0%86%E6%8E%92%E9%99%A4%E9%A1%B9%E6%B7%BB%E5%8A%A0%E5%88%B0-windows-%E5%AE%89%E5%85%A8%E4%B8%AD%E5%BF%83-811816c0-4dfd-af4a-47e4-c301afe13b26)进行设置。
```
wechat-tools.exe --help
```

## 快速开始（Python 环境）
开发环境为 `Python 3.11`，其他版本下未做测试。

### 配置环境
#### PDM
```
pdm install
python ./src/main.py --help
```

#### Pip
```
pdm install -r requirements.txt
python ./src/main.py --help
```

### 运行

#### 导出聊天记录
输入 `python ./src/main.py dump --help` 查看帮助信息：
```
Usage: main.py dump [OPTIONS] WXID

  导出与好友 FRIEND 的所有聊天记录

Arguments:
  WXID  你自己的 wxid  [required]

Options:
  --friend TEXT       好友的【微信名】或是【备注】  [required]
  --json / --no-json  以 json 格式导出  [required]
  --csv / --no-csv    以 csv 格式导出  [required]
  --output-dir TEXT   导出文件的存储文件夹路径，默认在程序同目录的 output 文件夹下  [default:
                      D:\Code\Python\wechat\output]
  --help              Show this message and exit.
```
```
python ./src/main.py dump wxid_xxxxxxxxxx --friend 文件专偷助手
```
上述命令会导出你与好友 `文件专偷助手` 的所有聊天记录，这里的 `wxid_xxxxxxxxxx` 是一个必填信息，该信息通常在路径下 `%USERPROFILE%\Documents\WeChat Files` 可以看到作为文件夹名称。

## References

1. [x1hy9/WeChatUserDB](https://github.com/x1hy9/WeChatUserDB)
2. [f13T2ach/WxMsgDump](https://github.com/f13T2ach/WxMsgDump)