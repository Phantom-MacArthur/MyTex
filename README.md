# 公式识别软件

## 文件结构说明

- `main.py` - 主程序入口和应用逻辑
- `ui.py` - 用户界面设置和布局管理  
- `api_client.py` - API调用和公式识别逻辑
- `image_handler.py` - 图片处理和显示功能
- `requirements.txt` - 依赖包列表

## 使用方法

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 运行程序：

   ```bash
   python main.py
   ```

3. 在程序界面中输入您的App ID和App Secret

## 功能特点

- **双区域显示**：上方显示原图，下方显示识别结果
- **多种输入方式**：选择图片、Ctrl+V粘贴、PrintScreen截图
- **自动识别**：选择或粘贴后自动开始识别
- **自动复制**：识别成功后自动复制LaTeX公式到剪贴板
- **API端口选择**：支持标准版（高精度）和轻量版（快速）
- **无弹窗干扰**：成功信息直接显示在文本区域