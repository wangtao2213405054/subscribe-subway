# Python应用程序打包为可执行文件

这是一个简单的打包指南，展示了如何使用 PyInstaller 将本项目打包为可执行文件。
PyInstaller是一个常用的工具，可以将Python代码和相关依赖项打包成单个可执行文件，使其在没有Python解释器的环境中独立运行。

## 步骤

以下是将Python应用程序打包为可执行文件的步骤：

1. 安装PyInstaller:

   ```bash
   pip install pyinstaller
   ```
2. 导航到项目目录:
    ```bash
   cd /xx/subscribe-subway
    ```
3. 执行打包命令:
   
   Mac OS 执行以下命令:
    ```bash
    pyinstaller -D -w --add-data "subway/conf:conf" --name SubwayTkinter --icon images/icon.png subway/app.py
    ```
   Windows 执行以下命令:
   
   您必须使用`--add-data` 选项手动包含 `customtkinter` `chinese_calendar` 目录。因为出于某种原因，pyinstaller 不会自动包含库中的 .json 等数据文件。您可以使用以下命令找到 `customtkinter` `chinese_calendar` 库的安装位置
   ```bash
   pip show customtkinter
   pip show chinese_calendar
   ```
   将显示一个位置，例如：`C:/Users/User/AppData/Local/Programs/Python/Python311-32/Lib/site-packages`
   
   然后添加库文件夹，如下所示：`--add-data "C:/Users/User/AppData/Local/Programs/Python/Python311-32/Lib/site-packages/customtkinter;customtkinter"`
   
   需要注意的是, 你需要将 `customtkinter` `chinese_calendar` 都添加上。以下是完整的命令:
   ```bash
   pyinstaller -D -w --add-data "subway/conf;conf" --add-data "C:/Users/User/AppData/Local/Programs/Python/Python311-32/Lib/site-packages/chinese_calendar;chinese_calendar" --add-data "C:/Users/User/AppData/Local/Programs/Python/Python311-32/Lib/site-packages/customtkinter;customtkinter" --name SubwayTkinter --icon images/icon.ico subway/app.py
   ```
   - `--add-data` 指定配置文件并在可执行文件中以 conf 命名
   - `subway/app.py` 要打包的Python脚本的文件名
   - `--name` 打包后生产的 app 名称
   - `--icon` 打包后应用的 icon
   - `-D` 生成目录模式
   - `-w` 生成窗口模式
5. 完成后，将在项目目录下生成一个dist目录，其中包含了打包好的可执行文件。

6. 测试可执行文件：
在打包过程中，PyInstaller将自动处理依赖项并将其打包到可执行文件中。
现在，您可以测试可执行文件，确保它在原始环境中正常运行，并且在打包后的可执行文件中也能正常工作。


## macOS 应用程序打包成可分发的 .dmg 文件

下面是一个简单的步骤指南:

1. 安装 `appdmg`:
   ```bash
   npm install -g appdmg
   ```
   如果尚未安装 Node.js 和 npm，请先安装它们。可以从 Node.js 官方网站（https://nodejs.cn/）下载并安装 Node.js。
2. 创建配置文件:
   ```json
   {
     "title": "SubwayTkinter",
     "icon": "images/icon.png",
     "background": "",
     "contents": [
       { "x": 192, "y": 120, "type": "file", "path": "dist/SubwayTkinter.app" },
       { "x": 448, "y": 120, "type": "link", "path": "/Applications" }
     ],
     "window": {
       "size": { "width": 660, "height": 300 }
     }
   }
   ```
3. 执行打包命令:
   打开终端，导航到包含 dmg.json 文件的目录，并执行以下命令来打包应用程序:
   ```bash
   appdmg mac-dmg.json dist/SubwayTkinterInstall.dmg
   ```
4. 完成打包:
打包完成后，您将在当前目录`/dist`下找到生成的 .dmg 文件，该文件可以在 macOS 上进行分发和安装应用程序。
请注意，`appdmg` 工具允许您进行更多高级的配置，例如自定义窗口样式、添加许可协议等。您可以在 dmg.json 文件中根据需要进行配置。

5. 有关更多详细信息和高级用法，请参阅 `appdmg` 的文档（https://github.com/LinusU/node-appdmg）。

## 注意事项

在使用PyInstaller进行打包时，请注意以下事项：

- 确保您的应用程序在原始环境中正常运行，没有任何运行时错误或依赖项问题。
- 在打包过程中，确保所有必要的文件和资源都被正确处理和包含。可以使用`--add-data`参数来指定额外的文件或目录。
- 如果有外部依赖项或扩展模块，确保它们也被正确处理和包含。您可以使用`--hidden-import`参数来显式指定缺失的模块。
- 请注意，打包过程可能需要一些时间，特别是在处理较大的项目或有许多依赖项的项目时。
- 在打包时，尽量保持Python环境的干净和精简，避免不必要的依赖项。
- 考虑不同操作系统的兼容性。在进行打包之前，最好在不同的操作系统上进行测试，以确保生成的可执行文件在目标操作系统上正常运行。
- 为了更好地调试和了解问题的原因，建议在打包过程中添加`--debug`参数，以便查看更详细的输出信息。
- 对于特殊的需求或更高级的配置，可以参考PyInstaller的官方文档和其他资源。

