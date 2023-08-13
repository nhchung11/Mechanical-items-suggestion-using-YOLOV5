import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading
import time
import torch
import numpy as np 
from playsound import playsound 
import pandas as pd

# Load model
model = torch.hub.load('ultralytics/yolov5', 'custom' ,'yolov5/best.pt')
# model = YOLO('yolov5/best.pt')

screw_driver = threading.Event()
wrench = threading.Event()
screw_head = threading.Event()
bolt = threading.Event()

correct_sound = 'D:\code\Data\sound\correct-156911.mp3'
# incorrect_sound = 'D:\code\Data\sound\wrong-buzzer-6268.mp3'

found_bolt = 'D:\\code\\Data\\sound\\found a bolt.mp3'
found_screw_head = 'D:\\code\\Data\\sound\\found a screw head.mp3'

find_bolt_check = False
find_screw_head_check = False

overlay_image1 = cv2.imread('D:\code\image\cascsa-removebg-preview.png', cv2.IMREAD_UNCHANGED)
overlay_image1 = cv2.resize(overlay_image1, None, fx = 0.25, fy = 0.25)
overlay_image2 = cv2.imread('D:\code\image\wrench_img_trans-removebg-preview.png', cv2.IMREAD_UNCHANGED)
overlay_image2 = cv2.resize(overlay_image2, None, fx = 0.25, fy = 0.25)

def overlay_img(frame, overlay_image, x_pos, y_pos):
    overlay_height, overlay_width = overlay_image.shape[:2]
    overlay_alpha = overlay_image[:, :, 3] / 255.0
    background_alpha = 1.0 - overlay_alpha

    for c in range(0, 3):
        frame[y_pos:y_pos+overlay_height, x_pos:x_pos+overlay_width, c] = (
            overlay_alpha * overlay_image[:, :, c] +
            background_alpha * frame[y_pos:y_pos+overlay_height, x_pos:x_pos+overlay_width, c]
        )
    return frame

class WebcamApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Webcam App")
        
        self.status_label1 = tk.Label(window, text="Trạng thái 1: Khởi động", font=("Arial", 14))
        self.status_label1.pack(pady=10)
        
        self.status_label2 = tk.Label(window, text="Trạng thái 2: Khởi động", font=("Arial", 14))
        self.status_label2.pack(pady=10)
        
        self.video_label = tk.Label(window)
        self.video_label.pack()
    
        self.cap = cv2.VideoCapture(0)
        self.thread1 = threading.Thread(target=self.update)
        self.thread2 = threading.Thread(target=self.change_status1_continuously)
        self.thread1.daemon = True
        self.thread2.daemon = True
        self.thread1.start()
        self.thread2.start()

    def update(self):
        while True:
            ret, frame = self.cap.read()
            results = model(frame)  
            my_series = results.pandas().xyxy[0]["name"]
            wrench_check = my_series.isin(['wrench']).any()
            if wrench_check == True:
                wrench.set()
            else:
                wrench.clear()
                
            screw_driver_check = my_series.isin(['screw_driver']).any()
            if screw_driver_check == True:
                screw_driver.set()
            else:
                screw_driver.clear()
                
            bolt_check = my_series.isin(['bolt_a']).any() or my_series.isin(['bolt_b']).any() or my_series.isin(['bolt_c']).any()
            if bolt_check == True:
                bolt.set()
            # else:
            #     bolt.clear()    
            
            screw_head_check = my_series.isin(['screw_head']).any()
            if screw_head_check == True:
                screw_head.set()
            # else:
            #     screw_head.clear()
            if ret:
                frame = cv2.cvtColor(np.squeeze(results.render()), cv2.COLOR_BGR2RGB)
                frame = cv2.putText(frame, 'Tool require:', (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color=(0, 0, 255), thickness=2)
                if bolt.is_set():
                    x_pos, y_pos = 0, 200
                    frame = overlay_img(frame, overlay_image2, x_pos, y_pos)
                    if wrench.is_set():
                        frame = cv2.rectangle(frame, (0, 200), (76, 342), (0, 255, 0), 4)
                if screw_head.is_set():
                    x_pos, y_pos = 0, 50
                    frame = overlay_img(frame, overlay_image1, x_pos, y_pos)
                    if screw_driver.is_set():
                        frame = cv2.rectangle(frame, (0, 50), (46, 166), (0, 255, 0), 4)
                img = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = img
                self.video_label.config(image=img)
            else:
                self.status_label1.config(text="Trạng thái 1: Không thể kết nối tới webcam")
                self.status_label2.config(text="Trạng thái 2: Không thể kết nối tới webcam")
            self.window.update_idletasks()
           
    
    def change_status1_continuously(self):  
        while True:
            text = "Trạng thái 1: Kiểm tra"
            if screw_head.is_set():
                text = "Trạng thái 1: Tìm thấy ốc vít. Cần tìm tua vít"
                if screw_driver.is_set():
                    text = "Trạng thái 1: Dụng cụ phù hợp"
                    app.play_correct_sound()
                elif wrench.is_set():
                    text = "Trạng thái 1: Dụng cụ sai"
                    # app.play_incorrect_sound()
            time.sleep(0.3)
            self.status_label1.config(text = text)
    def change_status2_continuously(self):
        while True:
            text = "Trạng thái 2: Kiểm tra"
            if bolt.is_set():
                text = "Trạng thái 2: Tìm thấy bu lông. Cần tìm cờ lê"
                if wrench.is_set():
                    app.play_correct_sound()
                elif screw_driver.is_set():
                    text = "Trạng thái 2: Dụng cụ sai"
                    # app.play_incorrect_sound()
            time.sleep(0.3)
            self.status_label2.config(text = text)

    
    def play_correct_sound(self):
        playsound(correct_sound)
    
    # def play_incorrect_sound(self):
    #     playsound(incorrect_sound)

# Create the Tkinter window
window = tk.Tk()

# Create the WebcamApp instance
app = WebcamApp(window)

# Start the threads to change the status labels continuously
status_thread1 = threading.Thread(target=app.change_status1_continuously)
status_thread2 = threading.Thread(target=app.change_status2_continuously)
status_thread1.daemon = True
status_thread2.daemon = True
status_thread1.start()
status_thread2.start()

# Run the Tkinter event loop
window.mainloop()
