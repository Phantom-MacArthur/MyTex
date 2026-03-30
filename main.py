import tkinter as tk
from ui import FormulaRecognizerUI
from api_client import FormulaAPIClient
from image_handler import ImageHandler
from config_loader import ConfigLoader


class FormulaRecognizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("公式识别软件")
        self.root.geometry("1000x700")
        
        # 初始化各个模块
        self.config_loader = ConfigLoader()
        self.api_client = FormulaAPIClient()
        self.image_handler = ImageHandler(self.root)
        self.ui = FormulaRecognizerUI(self.root, self)
        
        # 状态变量
        self.selected_image_path = None
        self.is_waiting_for_screenshot = False
        
        # 加载配置
        self.load_app_info()
        
        # 绑定快捷键
        self.root.bind('<Control-v>', self.paste_image_from_clipboard)

    def load_app_info(self):
        """加载同目录下的app info文件"""
        app_info = self.config_loader.load_app_info()
        if app_info:
            self.ui.set_app_config(app_info['app_id'], app_info['app_secret'])

    def select_image(self):
        """选择图片文件"""
        from tkinter import filedialog
        import os
        
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
            self.image_handler.display_original_image(file_path, self.ui.original_canvas)
            self.ui.clear_result_text()
            self.ui.show_processing_message()
            self.root.update()
            
            # 自动执行识别
            self.auto_recognize_formula()

    def paste_image_from_clipboard(self, event=None):
        """从剪贴板粘贴图片"""
        from PIL import ImageGrab
        import tempfile
        import os
        from tkinter import messagebox
        
        # 重置截图等待标志
        self.is_waiting_for_screenshot = False
        
        try:
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.image_handler.display_original_image(temp_path, self.ui.original_canvas)
                self.ui.clear_result_text()
                self.ui.show_processing_message()
                self.root.update()
                self.auto_recognize_formula()
            else:
                messagebox.showwarning("警告", "剪贴板中没有图片！")
        except Exception as e:
            messagebox.showerror("错误", f"从剪贴板读取图片失败: {str(e)}")

    def take_screenshot(self):
        """截图功能 - 直接使用PrintScreen并监听剪贴板"""
        from tkinter import messagebox
        
        # 设置等待截图标志
        self.is_waiting_for_screenshot = True
        
        # 提示用户按PrintScreen键
        messagebox.showinfo("截图操作", "请按键盘上的 PrintScreen 键截取屏幕，然后点击确定。")
        
        # 等待用户按PrintScreen后，从剪贴板获取图片
        self.root.after(100, self.check_clipboard_for_screenshot)

    def check_clipboard_for_screenshot(self):
        """检查剪贴板是否有截图"""
        from PIL import ImageGrab
        import tempfile
        from tkinter import messagebox
        
        # 如果不再等待截图，停止检查
        if not self.is_waiting_for_screenshot:
            return
            
        try:
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.image_handler.display_original_image(temp_path, self.ui.original_canvas)
                self.ui.clear_result_text()
                self.ui.show_processing_message()
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

    def auto_recognize_formula(self):
        """自动执行公式识别"""
        if not self.selected_image_path:
            return

        # 获取API配置
        app_id = self.ui.get_app_id()
        app_secret = self.ui.get_app_secret()

        if not app_id or not app_secret:
            from tkinter import messagebox
            messagebox.showwarning("警告", "请先填写App ID和App Secret！")
            self.ui.clear_result_text()
            self.ui.show_config_prompt()
            return

        try:
            # 调用API
            result = self.api_client.recognize_formula_api(
                self.selected_image_path, app_id, app_secret, self.ui.get_endpoint_choice()
            )

            if "error" in result:
                self.ui.clear_result_text()
                self.ui.show_error(result['error'], result.get('details', ''))
            else:
                # 成功识别，显示结果
                self.ui.clear_result_text()
                self.ui.show_success_result(result)
                
                # 在下方区域显示识别结果
                if "res" in result and "latex" in result["res"]:
                    latex_formula = result["res"]["latex"]
                    self.image_handler.display_result_visualization(latex_formula, self.ui.result_vis_canvas)
                    
                    # 自动复制到剪贴板
                    self.root.clipboard_clear()
                    self.root.clipboard_append(latex_formula)
                    self.root.update()

        except Exception as e:
            self.ui.clear_result_text()
            self.ui.show_error(f"识别过程中发生错误: {str(e)}", "")

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
    print("5. 软件会自动识别并复制LaTeX结果")
    print()
    # 强制刷新输出缓冲区
    import sys
    sys.stdout.flush()

    try:
        app = FormulaRecognizer()
        app.run()
    except ImportError as e:
        print(f"缺少必要的依赖包: {e}")
        print("请安装以下依赖:")
        print("pip install requests pillow tkinter")
        sys.stdout.flush()
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()