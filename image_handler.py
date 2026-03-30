from PIL import Image, ImageTk


class ImageHandler:
    def __init__(self, root):
        self.root = root

    def display_original_image(self, image_path, canvas):
        """显示原图在上方区域"""
        try:
            canvas.delete("all")
            image = Image.open(image_path)
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
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
            
            canvas.create_image(x, y, anchor="nw", image=photo)
            canvas.image = photo  # 保持引用防止被垃圾回收
            
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(200, 150, text=f"图片加载失败: {str(e)}", fill="red", font=("SimSun", 13))

    def display_result_visualization(self, latex_formula, canvas):
        """在下方区域显示识别结果"""
        try:
            canvas.delete("all")
            canvas.create_text(200, 150, text=latex_formula, fill="black", font=("Consolas", 13), width=380)
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(200, 150, text=f"显示失败: {str(e)}", fill="red", font=("SimSun", 13))
