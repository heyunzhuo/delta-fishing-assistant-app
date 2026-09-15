# 单文件 exe 改造包

把源码项目改造为**双击即用**的 Windows 单文件 exe，不改动界面与功能。

## 为什么必须改源码

原版用 `config.py` 里的 `ROOT = Path(__file__).resolve().parents[1]` 定位配置与日志。
PyInstaller 单文件模式下，`__file__` 指向**进程退出即被删除的临时解包目录**，会导致：

| 症状 | 原因 |
|---|---|
| 每次重启参数全部回到默认 | `local_config.json` 写进了临时目录，退出即丢 |
| `logs\` 里什么都没有 | 日志写进临时目录，程序一关就没了 |

这是**确定性缺陷**：只要打包就必然发生，与机器和游戏无关。因此 `patches/` 里的 4 个文件做了路径改造：

- 新增 `BUNDLE_DIR`（打包后 = `sys._MEIPASS`，只读资源）与可写数据目录分离；
- 配置与日志改为落在 **exe 所在目录**；该目录只读时自动回退到 `%LOCALAPPDATA%\FishingAssistant\`，
  且配置与日志**整体一起回退**，不会出现一个在 exe 旁、一个在用户目录的分叉状态；
- `runtime.py` / `replay.py` 改用 `logs_dir()`；
- `vision.py` 改用 `ASSET_DIR`。**说明**：旧写法 `Path(__file__).parent / "assets" / "digits"`
  在标准 onefile 布局下其实也能工作（PyInstaller 会把包目录放进 `sys._MEIPASS`），
  这里改为显式依赖 `BUNDLE_DIR` 是为了不依赖打包器的模块落位细节，属加固而非修复；
  无论用哪种写法，**模板文件都必须由 `.spec` 的 `collect_data_files` 显式收集**，
  否则 `assets/*.png` 不会进包；
- 保留 `ROOT` / `CONFIG_PATH` 名称，`gui.py` 等既有导入无需改动。

`__main__.py` 无需修改：源码包入口在冻结后可直接作为启动入口。

## 已完成的验证

补丁已应用回真实源码并在本机验证（模拟 `sys.frozen` + `sys._MEIPASS`）：

| 验证项 | 结果 |
|---|---|
| 配置写入 exe 目录并跨次启动读回 | 通过 |
| 资源（`0~5.png` 模板）从 `sys._MEIPASS` 定位 | 通过 |
| 6 个模板全部被 `BaitReader` 载入 | 通过 |
| 旧别名 `ROOT` / `CONFIG_PATH` 兼容 | 通过 |
| exe 目录只读时回退 `%LOCALAPPDATA%\FishingAssistant\` | 通过 |
| 回退后配置与日志位于同一目录（不分叉） | 通过 |
| 原项目单元测试 | 13 通过 / 12 因非 Windows 跳过 / 1 需 cv2 未跑 |

未验证项（本机是 macOS，无法执行）：真实 PyInstaller 构建产物能否启动、exe 的 UAC 提权、
以及在 Windows 上对游戏窗口的实际鼠标控制。这三项必须在你或 CI 的 Windows 上实测。

## 文件清单

| 文件 | 放到仓库哪里 | 作用 |
|---|---|---|
| `patches/config.py` | `fishing_assistant/config.py` | 覆盖，路径改造核心 |
| `patches/runtime.py` | `fishing_assistant/runtime.py` | 覆盖，日志目录 |
| `patches/replay.py` | `fishing_assistant/replay.py` | 覆盖，回放输出目录 |
| `patches/vision.py` | `fishing_assistant/vision.py` | 覆盖，模板资源定位 |
| `钓鱼经验机.spec` | 仓库根目录 | PyInstaller 打包配置 |
| `app.manifest` | 仓库根目录 | 嵌入 UAC 管理员清单 + 高 DPI |
| `version_info.txt` | 仓库根目录 | exe 属性信息 |
| `build_exe.bat` | 仓库根目录 | 本地一键构建 |
| `build-exe.yml` | `.github/workflows/build-exe.yml` | 云端自动构建 |

## 两种构建方式

### 方式 A：GitHub Actions（不占用自己电脑，推荐）

1. Fork 或新建仓库，把改造后的项目推上去。
2. 仓库页面 → **Actions** 标签 → 左侧 **Build Windows EXE** → **Run workflow**。
3. 约 3~5 分钟后，在本次运行页面底部 **Artifacts** 下载 `fishing-assistant-windows-x64`。
4. 想发正式版：`git tag v0.1.3 && git push origin v0.1.3`，会自动创建 Release 并附上 exe。

### 方式 B：本地一键构建

在**装了 Python 3.11+ 的 Windows** 上，把仓库放好，双击 `build_exe.bat`。
脚本会自建 `.venv`、装依赖、装 PyInstaller、打包，并打印产物大小。产出在 `dist\钓鱼经验机.exe`。

## 打包后的关键行为（与源码版不同，务必知道）

1. **会给 exe 嵌入 `requireAdministrator` 清单**，双击直接弹 UAC 授权框，点"是"即可以管理员权限运行。
   这是必要的：游戏多为管理员进程，权限不对等时 Windows 会**静默丢弃**模拟点击，表现为"程序在跑但游戏没反应"。
2. **首次启动慢几秒**：单文件 exe 需自解压到临时目录，属正常现象。
3. 参数与日志落在 **exe 同目录**：`local_config.json` 与 `logs\`。
   **换电脑时把 `local_config.json` 一起带走，调好的参数就不会丢。**
4. exe 放在只读位置时自动回退到 `%LOCALAPPDATA%\FishingAssistant\`，不会启动即崩。

## 已知限制

- **不能在 macOS/Linux 上交叉打包**：PyInstaller 必须在本平台的 Python 环境构建，Windows exe 只能在 Windows 上产出（本地或 GitHub Actions 的 `windows-latest`）。
- 若游戏侧有反作弊/内存扫描类保护，**本项目的普通截图与输入模拟不在其白名单内也不做任何绕过**；是否可用取决于游戏规则，需自行判断。
- 未做代码签名，未签名 exe 可能触发 SmartScreen 提示（"更多信息" → "仍要运行"）；如需消除需购买代码签名证书。
- 产物约 30~60 MiB，主要是 OpenCV 与 Tk 运行时，属正常体积。
