import tkinter as tk
from tkinter import scrolledtext


class FormulaRecognizerUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧：图片显示区域（分为上下两部分）
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 上部：原图显示
        original_frame = tk.LabelFrame(
            left_frame, text="输入图片", padx=5, pady=5, font=("SimSun", 13)
        )
        original_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.original_canvas = tk.Canvas(original_frame, bg="white", height=250)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        self.original_canvas.create_text(
            200, 125, text="选择图片或按 Ctrl+V 粘贴", fill="gray", font=("SimSun", 13)
        )

        # 下部：识别结果可视化
        result_vis_frame = tk.LabelFrame(
            left_frame, text="识别结果", padx=5, pady=5, font=("SimSun", 13)
        )
        result_vis_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.result_vis_canvas = tk.Canvas(result_vis_frame, bg="white", height=250)
        self.result_vis_canvas.pack(fill=tk.BOTH, expand=True)
        self.result_vis_canvas.create_text(
            200, 125, text="识别结果将在此显示", fill="gray", font=("SimSun", 13)
        )

        # 右侧：配置和结果区域
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # API配置区域
        config_frame = tk.LabelFrame(
            right_frame, text="API配置", padx=10, pady=10, font=("SimSun", 13)
        )
        config_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(config_frame, text="App ID:", font=("SimSun", 13)).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.app_id_entry = tk.Entry(config_frame, font=("SimSun", 13))
        self.app_id_entry.grid(row=0, column=1, pady=2, sticky=tk.EW)

        tk.Label(config_frame, text="App Secret:", font=("SimSun", 13)).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.app_secret_entry = tk.Entry(config_frame, font=("SimSun", 13))
        self.app_secret_entry.grid(row=1, column=1, pady=2, sticky=tk.EW)

        # API端口选择
        tk.Label(config_frame, text="API端口:", font=("SimSun", 13)).grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.api_endpoint_var = tk.StringVar(value="standard")
        endpoint_frame = tk.Frame(config_frame)
        endpoint_frame.grid(row=2, column=1, sticky=tk.W, pady=2)
        tk.Radiobutton(
            endpoint_frame,
            text="标准版",
            variable=self.api_endpoint_var,
            value="standard",
            font=("SimSun", 13),
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            endpoint_frame,
            text="轻量版",
            variable=self.api_endpoint_var,
            value="turbo",
            font=("SimSun", 13),
        ).pack(side=tk.LEFT)

        # 让第二列可以扩展
        config_frame.columnconfigure(1, weight=1)

        # 按钮区域
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # 选择图片按钮
        self.select_btn = tk.Button(
            button_frame,
            text="选择图片",
            command=self.app.select_image,
            font=("SimSun", 13),
        )
        self.select_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        # 截图按钮
        self.screenshot_btn = tk.Button(
            button_frame,
            text="截图识别",
            command=self.app.take_screenshot,
            font=("SimSun", 13),
        )
        self.screenshot_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        # 结果显示区域 - 只显示LaTeX格式
        result_frame = tk.LabelFrame(
            right_frame, text="LaTeX 公式", padx=10, pady=10, font=("SimSun", 13)
        )
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, height=20, font=("SimSun", 13)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 启动时显示使用说明
        self.show_startup_instructions()

    def show_startup_instructions(self):
        """显示启动使用说明"""
        instructions = """💡 使用说明:
1. 前往 https://simpletex.cn/user/center 开通开放平台功能
2. 在应用列表中创建应用，获取App ID和App Secret  
3. 在软件界面中填入App ID和App Secret
4. 选择包含公式的截图图片
5. 软件会自动识别并复制LaTeX结果

📝 提示: 
- App Secret会以明文显示，方便核对
- 支持标准版(高精度)和轻量版(快速)API端口
- 识别成功后会自动复制，无需手动操作
"""
        self.result_text.insert(tk.END, instructions)

    def set_app_config(self, app_id, app_secret):
        """设置App配置"""
        self.app_id_entry.delete(0, tk.END)
        self.app_id_entry.insert(0, app_id)
        self.app_secret_entry.delete(0, tk.END)
        self.app_secret_entry.insert(0, app_secret)

    def get_app_id(self):
        """获取App ID"""
        return self.app_id_entry.get().strip()

    def get_app_secret(self):
        """获取App Secret"""
        return self.app_secret_entry.get().strip()

    def get_endpoint_choice(self):
        """获取API端口选择"""
        return self.api_endpoint_var.get()

    def clear_result_text(self):
        """清空结果文本"""
        self.result_text.delete(1.0, tk.END)

    def show_processing_message(self):
        """显示处理中消息"""
        self.result_text.insert(tk.END, "正在识别公式，请稍候...\n")

    def show_config_prompt(self):
        """显示配置提示"""
        self.result_text.insert(tk.END, "请在右侧填写App ID和App Secret\n")

    def show_error(self, error_msg, details=""):
        """显示错误信息"""
        self.result_text.insert(tk.END, f"识别失败:\n{error_msg}\n")
        if details:
            self.result_text.insert(tk.END, f"详细信息:\n{details}\n")

    def show_success_result(self, result):
        """显示成功结果"""
        if "res" in result and "latex" in result["res"]:
            latex_formula = result["res"]["latex"]
            confidence = result["res"].get("conf", 0)

            # 只显示LaTeX公式和置信度
            self.result_text.insert(tk.END, f"{latex_formula}\n\n")
            self.result_text.insert(tk.END, f"置信度: {confidence:.2%}\n")

            # 显示成功信息（不弹窗）
            self.result_text.insert(tk.END, "\n✅ 已成功识别并自动复制")
        else:
            # 直接显示整个结果
            import json

            formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
            self.result_text.insert(tk.END, f"完整结果:\n{formatted_result}\n")
