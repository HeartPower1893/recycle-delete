# recycle-delete

把文件或目录移进回收站的小工具（Windows 专用），用于替代 `del` 这类**不可还原**的删除。

## 为什么写它

命令行里删东西是永久的，手一抖就没了。而有些操作（清理缓存、清掉旧项目目录）我希望删完还能反悔，所以直接调 Windows 的 `SHFileOperationW`，带上 `FOF_ALLOWUNDO` 标志，效果等同于在资源管理器里按 Delete。

## 用法

需要 Python 3.8+，只用标准库，不用装任何依赖。

```bash
python recycle_delete.py "C:\some\path\to\remove"
python recycle_delete.py "C:\path\a" "C:\path\b"
```

必须至少传一个路径。不带参数时会打印用法，并以退出码 `1` 结束——不会有任何默认路径被删。

输出格式：

```
OK      7162 MB  code=0  C:\Users\...\Cities_Skylines
MISSING 0 MB     code=0  C:\not\exist
ERROR   0 MB     code=5  C:\locked\x        权限不足或文件正被占用，先关掉相关程序再试
```

状态含义：`OK` 已进回收站 / `MISSING` 路径不存在 / `STILL_EXISTS` 文件仍存在（可能被占用）/ `ABORTED` 用户取消 / `ERROR` 系统返回错误码，并在行尾附一句中文说明（字典里没有的码会提示把数字反馈）。

## 已知不足

这是第一版，明确记录待改进的地方：

- [ ] 没有 `--dry-run`，不能先看要删什么再决定
- [ ] 不支持通配符和批量清单文件
- [x] 出错时只有数字错误码，没有可读的说明
- [ ] 只支持 Windows
- [ ] 没有单元测试

## 实现要点

- `SHFileOperationW` 要求路径以双 `\0` 结尾，所以用 `create_unicode_buffer(path + "\0", len(path) + 2)` 构造缓冲区，而不是直接传字符串。这一步写错会出现各种诡异行为。
- `dir_size` 用 `os.walk` 而非 `os.path.getsize`，因为目录本身不占空间，要累加内部文件。
- `SHFileOperationW` 的返回值不可全信：删真实目录时可能返回 `2`（ERROR_FILE_NOT_FOUND），但文件其实已经进了回收站。所以 `res != 0` 时要再看一眼 `os.path.exists(path)`，路径没了就判成功。

## 许可

MIT
