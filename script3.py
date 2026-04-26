import pytesseract
import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
from PIL import Image
import time
import win32gui
import win32con

custom_config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz: "

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def find_pest_cooldown_ready():
    tw = gw.getWindowsWithTitle("Minecraft")[0]
    hwnd = win32gui.FindWindow(None, tw.title)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    screenshot = pyautogui.screenshot(region=(tw.left, tw.top, tw.width, tw.height))
    screenshot.save("window_capture.png")
    img = Image.open("window_capture.png")
    text = pytesseract.image_to_string(img)
    print(text)


# while True:
#     find_pest_cooldown_ready()
#     time.sleep(1)

if __name__ == "__main__":
    find_pest_cooldown_ready()
