import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import hashlib
import time
import random
import string
import json
from PIL import Image, ImageTk
import os


class FormulaRecognizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("公式识别软件")
        self.root.geometry("800x600")

        # API配置（用户需要替换为自己的）
        self.app_id = ""
        self.app_secret = ""

        self.setup_ui()

    def load_app_info(self):
        """加载同目录下的app info文件"""
        app_info_path = os.path.join(os.path.dirname(__file__), "app_info.txt")
        if os.path.exists(app_info_path):
            try:
                with open(app_info_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        app_id = lines[0].strip()
                        app_secret = lines[1].strip()
                        if app_id and app_secret:
                            self.app_id_entry.insert(0, app_id)
                            self.app_secret_entry.insert(0, app_secret)
            except Exception as e:
                print(f"加载app_info.txt失败: {e}")

    def setup_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：图片显示区域（分为上下两部分）
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 上部：原图显示
        original_frame = tk.LabelFrame(left_frame, text="输入图片", padx=5, pady=5)
        original_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.original_canvas = tk.Canvas(original_frame, bg="lightgray", height=250)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        self.original_canvas.create_text(200, 125, text="选择图片或按 Ctrl+V 粘贴", fill="gray", font=("Arial", 12))
        
        # 下部：识别结果可视化
        result_vis_frame = tk.LabelFrame(left_frame, text="识别结果", padx=5, pady=5)
        result_vis_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.result_vis_canvas = tk.Canvas(result_vis_frame, bg="white", height=250)
        self.result_vis_canvas.pack(fill=tk.BOTH, expand=True)
        self.result_vis_canvas.create_text(200, 125, text="识别结果将在此显示", fill="gray", font=("Arial", 12))
        
        # 右侧：配置和结果区域
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # API配置区域
        config_frame = tk.LabelFrame(right_frame, text="API配置", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(config_frame, text="App ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.app_id_entry = tk.Entry(config_frame, width=30)
        self.app_id_entry.grid(row=0, column=1, pady=2)
        
        tk.Label(config_frame, text="App Secret:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.app_secret_entry = tk.Entry(config_frame, width=30)
        self.app_secret_entry.grid(row=1, column=1, pady=2)
        
        # API端点选择
        tk.Label(config_frame, text="API端点:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.api_endpoint_var = tk.StringVar(value="standard")
        endpoint_frame = tk.Frame(config_frame)
        endpoint_frame.grid(row=2, column=1, sticky=tk.W, pady=2)
        tk.Radiobutton(endpoint_frame, text="标准版", variable=self.api_endpoint_var, value="standard").pack(side=tk.LEFT)
        tk.Radiobutton(endpoint_frame, text="轻量版", variable=self.api_endpoint_var, value="turbo").pack(side=tk.LEFT)
        
        # 按钮区域 - 简化截图按钮
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 选择图片按钮
        self.select_btn = tk.Button(button_frame, text="选择图片", command=self.select_image)
        self.select_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        # 截图按钮（简化版）
        self.screenshot_btn = tk.Button(button_frame, text="截图识别", command=self.take_screenshot)
        self.screenshot_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # 结果显示区域 - 只显示LaTeX格式
        result_frame = tk.LabelFrame(right_frame, text="LaTeX 公式", padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=20, font=("Consolas", 12))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        self.selected_image_path = None
        
        # 截图检查标志
        self.is_waiting_for_screenshot = False
        
        # 加载app info文件
        self.load_app_info()
        
        # 绑定Ctrl+V快捷键
        self.root.bind('<Control-v>', self.paste_image_from_clipboard)
    
    def take_screenshot(self):
        """截图功能 - 直接使用PrintScreen并监听剪贴板"""
        # 设置等待截图标志
        self.is_waiting_for_screenshot = True
        
        # 提示用户按PrintScreen键
        messagebox.showinfo("截图操作", "请按键盘上的 PrintScreen 键截取屏幕，然后点击确定。")
        
        # 等待用户按PrintScreen后，从剪贴板获取图片
        self.root.after(100, self.check_clipboard_for_screenshot)
    
    def check_clipboard_for_screenshot(self):
        """检查剪贴板是否有截图"""
        # 如果不再等待截图，停止检查
        if not self.is_waiting_for_screenshot:
            return
            
        try:
            from PIL import ImageGrab
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.display_original_image(temp_path)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "正在识别公式，请稍候...\n")
                self.root.update()
                self.auto_recognize_formula()
                # 重置标志
                self.is_waiting_for_screenshot = False
            else:
                # 如果没有图片，给用户更多时间
                self.root.after(500, self.check_clipboard_for_screenshot)
                
        except Exception as e:
            # 重置标志并显示错误
            self.is_waiting_for_screenshot = False
            messagebox.showerror("错误", f"获取截图失败: {str(e)}")
    
    def paste_image_from_clipboard(self, event=None):
        """从剪贴板粘贴图片"""
        # 重置截图等待标志
        self.is_waiting_for_screenshot = False
        
        try:
            from PIL import ImageGrab
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.display_original_image(temp_path)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "正在识别公式，请稍候...\n")
                self.root.update()
                self.auto_recognize_formula()
            else:
                messagebox.showwarning("警告", "剪贴板中没有图片！")
        except Exception as e:
            messagebox.showerror("错误", f"从剪贴板读取图片失败: {str(e)}")
    
    def display_original_image(self, image_path):
        """显示原图在上方区域"""
        try:
            self.original_canvas.delete("all")
            image = Image.open(image_path)
            canvas_width = self.original_canvas.winfo_width()
            canvas_height = self.original_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 250  # 上方区域高度
            
            ratio = min(canvas_width / image.width, canvas_height / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            new_width = max(new_width, 1)
            new_height = max(new_height, 1)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            self.original_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.original_canvas.image = photo
            
        except Exception as e:
            self.original_canvas.delete("all")
            self.original_canvas.create_text(200, 150, text=f"图片加载失败: {str(e)}", fill="red", font=("Arial", 12))
    
    def display_result_visualization(self, latex_formula):
        """在下方区域显示识别结果"""
        try:
            self.result_vis_canvas.delete("all")
            self.result_vis_canvas.create_text(200, 150, text=latex_formula, fill="black", font=("Consolas", 12), width=380)
        except Exception as e:
            self.result_vis_canvas.delete("all")
            self.result_vis_canvas.create_text(200, 150, text=f"显示失败: {str(e)}", fill="red", font=("Arial", 12))

    def generate_random_string(self, length=16):
        """生成16位随机字符串"""
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def generate_signature(self, data, app_secret):
        """生成签名"""
        # 将data中的key按字母顺序排序
        sorted_keys = sorted(data.keys())
        # 构建待签名字符串
        sign_string = "&".join([f"{key}={data[key]}" for key in sorted_keys])
        # 添加secret
        sign_string += f"&secret={app_secret}"
        # MD5签名
        md5_hash = hashlib.md5(sign_string.encode("utf-8")).hexdigest()

        # 调试信息
        print(f"待签名字符串: {sign_string}")
        print(f"生成的签名: {md5_hash}")

        return md5_hash

    def recognize_formula_api(self, image_path, app_id, app_secret):
        """调用公式识别API"""
        try:
            # 准备请求数据
            timestamp = str(int(time.time()))
            random_str = self.generate_random_string()

            # 表单数据（只包含业务参数）
            form_data = {"use_batch": "False"}

            # 用于签名的数据（包含所有参数：业务参数 + 鉴权参数）
            # 注意：这里必须包含所有要参与签名的参数
            sign_data = {
                "app-id": app_id,
                "random-str": random_str,
                "timestamp": timestamp,
                "use_batch": "False",
            }

            # 生成签名
            signature = self.generate_signature(sign_data, app_secret)

            # 准备headers
            headers = {
                "app-id": app_id,
                "random-str": random_str,
                "timestamp": timestamp,
                "sign": signature,
            }

            # 准备文件和表单数据
            with open(image_path, "rb") as f:
                files = {"file": f}
                # 根据选择的端点类型确定API URL
                endpoint_choice = self.api_endpoint_var.get()
                if endpoint_choice == "turbo":
                    url = "https://server.simpletex.cn/api/latex_ocr_turbo"
                else:
                    url = "https://server.simpletex.cn/api/latex_ocr"
                response = requests.post(
                    url, headers=headers, data=form_data, files=files, timeout=30
                )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API请求失败，状态码: {response.status_code}",
                    "details": response.text,
                }

        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}

    def display_image(self, image_path):
        """显示图片预览"""
        try:
            # 清除Canvas内容
            self.image_canvas.delete("all")

            # 打开并调整图片大小以适应显示区域
            image = Image.open(image_path)

            # 获取Canvas的实际尺寸
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()

            # 如果Canvas还没有实际尺寸，使用默认值
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 400

            # 计算缩放比例
            ratio = min(canvas_width / image.width, canvas_height / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)

            # 确保至少有最小尺寸
            new_width = max(new_width, 1)
            new_height = max(new_height, 1)

            # 缩放图片
            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            photo = ImageTk.PhotoImage(resized_image)

            # 在Canvas中心显示图片
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2

            self.image_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.image_canvas.image = photo  # 保持引用防止被垃圾回收

        except Exception as e:
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                200, 200, text=f"图片加载失败: {str(e)}", fill="red", font=("Arial", 12)
            )

    def select_image(self):
        """选择图片文件"""
        # 重置截图等待标志
        self.is_waiting_for_screenshot = False
        
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("所有文件", "*.*"),
            ],
        )

        if file_path:
            self.selected_image_path = file_path
            # 显示原图在上方区域
            self.display_original_image(file_path)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "正在识别公式，请稍候...\n")
            self.root.update()
            
            # 自动执行识别
            self.auto_recognize_formula()

    def recognize_formula(self):
        """执行公式识别"""
        if not self.selected_image_path:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return

        # 获取API配置
        app_id = self.app_id_entry.get().strip()
        app_secret = self.app_secret_entry.get().strip()

        if not app_id or not app_secret:
            messagebox.showwarning("警告", "请先填写App ID和App Secret！")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "正在识别公式，请稍候...\n")
        self.root.update()  # 刷新界面

        try:
            # 调用API
            result = self.recognize_formula_api(
                self.selected_image_path, app_id, app_secret
            )

            if "error" in result:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"识别失败:\n{result['error']}\n")
                if "details" in result:
                    self.result_text.insert(tk.END, f"详细信息:\n{result['details']}\n")
            else:
                # 成功识别，显示结果
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "✅ 识别成功！\n\n")

                # 提取LaTeX公式
                if "res" in result and "latex" in result["res"]:
                    latex_formula = result["res"]["latex"]
                    confidence = result["res"].get("conf", 0)

                    self.result_text.insert(tk.END, "📋 LaTeX 公式:\n")
                    self.result_text.insert(tk.END, f"{latex_formula}\n\n")
                    self.result_text.insert(tk.END, f"置信度: {confidence:.2%}")

                    # 添加使用说明
                    self.result_text.insert(tk.END, "\n\n💡 使用说明:\n")
                    self.result_text.insert(
                        tk.END, "- 在Markdown中使用: `$" + latex_formula + "$`\n"
                    )
                    self.result_text.insert(
                        tk.END, "- 在LaTeX文档中使用: `" + latex_formula + "`\n"
                    )
                    self.result_text.insert(
                        tk.END,
                        "- 在Jupyter Notebook中使用: `$" + latex_formula + "$`\n",
                    )

                else:
                    # 直接显示整个结果
                    formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
                    self.result_text.insert(tk.END, f"完整结果:\n{formatted_result}\n")
                
                # 更新可视化区域
                if "res" in result and "latex" in result["res"]:
                    self.display_result_visualization(result["res"]["latex"])

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"识别过程中发生错误:\n{str(e)}\n")
            self.display_result_visualization("")

    def auto_recognize_formula(self):
        """自动执行公式识别"""
        if not self.selected_image_path:
            return

        # 获取API配置
        app_id = self.app_id_entry.get().strip()
        app_secret = self.app_secret_entry.get().strip()

        if not app_id or not app_secret:
            messagebox.showwarning("警告", "请先填写App ID和App Secret！")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "请在右侧填写App ID和App Secret\n")
            return

        try:
            # 调用API
            result = self.recognize_formula_api(
                self.selected_image_path, app_id, app_secret
            )

            if "error" in result:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"识别失败:\n{result['error']}\n")
                if "details" in result:
                    self.result_text.insert(tk.END, f"详细信息:\n{result['details']}\n")
            else:
                # 成功识别，显示结果
                self.result_text.delete(1.0, tk.END)

                # 提取LaTeX公式
                if "res" in result and "latex" in result["res"]:
                    latex_formula = result["res"]["latex"]
                    confidence = result["res"].get("conf", 0)

                    # 只显示LaTeX公式和置信度
                    self.result_text.insert(tk.END, f"{latex_formula}\n\n")
                    self.result_text.insert(tk.END, f"置信度: {confidence:.2%}\n")
                    
                    # 显示成功信息（不弹窗）
                    self.result_text.insert(tk.END, "\n✅ 已成功识别并自动复制")

                    # 在下方区域显示识别结果
                    self.display_result_visualization(latex_formula)

                    # 自动复制到剪贴板
                    self.root.clipboard_clear()
                    self.root.clipboard_append(latex_formula)
                    self.root.update()
                    
                    # 移除弹窗提示
                    # messagebox.showinfo("成功", "LaTeX公式已自动复制到剪贴板！")
                else:
                    # 直接显示整个结果
                    formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
                    self.result_text.insert(tk.END, f"完整结果:\n{formatted_result}\n")

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"识别过程中发生错误:\n{str(e)}\n")
            self.display_result_visualization("")

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    print("公式识别软件启动中...")
    print("使用说明:")
    print("1. 前往 https://simpletex.cn/user/center 开通开放平台功能")
    print("2. 在应用列表中创建应用，获取App ID和App Secret")
    print("3. 在软件界面中填入App ID和App Secret")
    print("4. 选择包含公式的截图图片")
    print("5. 点击'识别公式'按钮获取LaTeX结果")
    print()

    try:
        app = FormulaRecognizer()
        app.run()
    except ImportError as e:
        print(f"缺少必要的依赖包: {e}")
        print("请安装以下依赖:")
        print("pip install requests pillow tkinter")
    except Exception as e:
        print(f"程序启动失败: {e}")


if __name__ == "__main__":
    main()
