import pyautogui
import time
import pyperclip
import tkinter as tk
from tkinter import messagebox

# 设置关键词列表和坐标位置
keywords = ["Scam", "Cheating", "Fraud", "欺騙", "行騙", "詐騙", "詐欺", "電騙", "騙", "騙徒", "電詐", "騙錢", "呃", "呃人", "呃錢", "電話騙案", "網上騙案", "網上呃錢", "網上詐騙", "騙徒手法層出不窮", "電郵騙案", "網上情緣騙案", "交友 app 騙案", "facebook 騙案"]  # 替换为实际关键词列表
search_box_position = (90, 180)  # 搜索框的固定坐标 search bos position
content_start_position = (500, 500)  # 拖动开始坐标 content start position
word_position = (1800, 1200)  # Word 文档的坐标 word position(paste here)
scroll_bar_position = (1360, 1350)  # 滚动条底端的检测点    the botton of the whole scroll bar →
tolerance = 10  # 颜色对比的宽容值

# 分段和滚动设置
segment_length = 800  # 每次复制的分段长度
scroll_length = 750   # 滚动长度略小于分段长度，避免内容缺漏

# 定义函数：拖动选择屏幕内容并复制
def drag_and_copy_segment():
    """从 content_start_position 拖动一定长度并复制到剪贴板"""
    pyautogui.moveTo(content_start_position)
    pyautogui.mouseDown()
    pyautogui.moveTo(content_start_position[0], content_start_position[1] + segment_length, duration=1)  # 拖动至分段长度
    pyautogui.mouseUp()

    # 复制内容
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)  # 等待复制完成
    return pyperclip.paste().strip()

# 定义函数：检测是否到底部
def has_reached_bottom(initial_color):
    """检测滚动条底端的颜色是否与初始颜色不同，且持续5秒"""
    different_color_time = 0

    while different_color_time < 5:
        # 获取滚动条底端颜色
        current_color = pyautogui.screenshot().getpixel(scroll_bar_position)
        
        # 判断颜色是否在宽容值范围内
        if all(abs(current_color[i] - initial_color[i]) <= tolerance for i in range(3)):
            different_color_time = 0  # 颜色相近，重置计时器
            return False  # 如果颜色接近，继续滚动
        else:
            different_color_time += 1
            time.sleep(1)

    return True  # 颜色在5秒内不同，说明到底了
    # the code get the initial color of the bottom of scroll, if the scroll bar hit the bottom and keep being there,
    # means no new contents will appear, means available content of this keyword has been fully scraped

# 主流程
def start_script():
    # 最小化 GUI 窗口
    root.iconify()
    time.sleep(5)  # 给用户留出足够的时间最小化 Python 窗口

    # 记录滚动条底端初始颜色（只记录一次）
    initial_color = pyautogui.screenshot().getpixel(scroll_bar_position)

    for keyword in keywords:
        # 将关键词复制到剪贴板
        pyperclip.copy(keyword)

        # 移动到搜索框并点击
        pyautogui.moveTo(search_box_position)
        pyautogui.click()
        time.sleep(5)  # 延长等待时间

        # 清空搜索框并粘贴关键词
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        pyautogui.hotkey("ctrl", "v")  # 从剪贴板粘贴关键词
        pyautogui.press("enter")
        time.sleep(5)  # 等待搜索结果加载

        # 循环滚动和复制页面内容
        page_number = 1
        print(f"处理关键词：{keyword}")

        while True:
            # 复制一个分段内容
            page_text = drag_and_copy_segment()

            # 移动到 Word 文档窗口并粘贴内容
            pyautogui.moveTo(word_position)
            pyautogui.click()
            pyautogui.hotkey("ctrl", "v")  # 使用简单的粘贴
            pyautogui.press("enter")  # 添加换行，方便下一次粘贴
            time.sleep(5)

            # 返回内容窗口并滚动一个分段长度
            pyautogui.moveTo(content_start_position)
            pyautogui.click()
            pyautogui.scroll(-scroll_length)  # 向下滚动页面，长度略小于分段长度
            time.sleep(5)  # 延长等待时间
            page_number += 1

            # 检查是否到底
            if has_reached_bottom(initial_color):
                print(f"关键词 {keyword} 的内容已全部复制")
                break

    messagebox.showinfo("完成", "所有关键词处理完成。")

# 创建 GUI 界面 this code need two fixed windows, the GUI can hide vscode window and give user time to adjust
root = tk.Tk()
root.title("自动化脚本启动器")
root.geometry("300x200")

# 创建启动按钮 
start_button = tk.Button(root, text="启动脚本", command=start_script, font=("Arial", 12))
start_button.pack(pady=50)

# 启动主循环
root.mainloop()
