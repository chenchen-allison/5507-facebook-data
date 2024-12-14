import tkinter as tk
import pyautogui

# 创建主窗口 a simple tool to get the position of mouse, will be used in scraper
root = tk.Tk()
root.title("鼠标坐标显示器")
root.geometry("200x100")  # 设置窗口大小
root.resizable(False, False)  # 禁止窗口大小调整

# 创建标签来显示坐标
label = tk.Label(root, text="鼠标坐标：", font=("Arial", 14))
label.pack(pady=20)

# 更新坐标的函数
def update_coordinates():
    x, y = pyautogui.position()  # 获取鼠标当前坐标
    label.config(text=f"鼠标坐标：({x}, {y})")
    root.after(100, update_coordinates)  # 每100毫秒更新一次坐标

# 启动坐标更新
update_coordinates()

# 启动主循环
root.mainloop()