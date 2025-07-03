import tkinter as tk
from PIL import Image, ImageTk

class ImageWindow(tk.Tk):
    def __init__(self, image_path):
        super().__init__()

        self.title("图片展示窗口")

        # 加载图片
        self.original_image = Image.open(image_path)
        self.photo_image = ImageTk.PhotoImage(self.original_image)

        # 创建标签用于显示图片
        self.image_label = tk.Label(self, image=self.photo_image)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 绑定窗口大小变化事件
        self.bind("<Configure>", self.resize_image)

    def resize_image(self, event):
        # 获取窗口的新宽度和高度
        window_width = event.width
        window_height = event.height

        # 调整图片大小
        resized_image = self.original_image.resize((window_width, window_height), Image.ANTIALIAS)
        self.photo_image = ImageTk.PhotoImage(resized_image)

        # 更新标签中的图片
        self.image_label.config(image=self.photo_image)

if __name__ == "__main__":
    # 创建并显示图片窗口
    window = ImageWindow("project_sets.png")
    window.mainloop()
