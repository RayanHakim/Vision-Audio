import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import time
import pytesseract
from collections import deque

# --- KONFIGURASI TESSERACT OCR ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VisionAudio:
    def __init__(self):
        # 1. Inisialisasi Suara 
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.last_spoken = ""
        
        # 2. Inisialisasi MediaPipe 
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2, 
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # 3. Variabel Canvas & Air Writing
        self.points = deque(maxlen=512)
        self.canvas = None
        self.prev_time = 0
        self.recognized_text = ""

    def speak(self, text):
        """Fungsi suara versi AWAL yang stabil untuk angka."""
        if self.last_spoken != text:
            def run_speech():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except: 
                    pass
            threading.Thread(target=run_speech, daemon=True).start()
            self.last_spoken = text

    def get_finger_count(self, multi_hand_landmarks, multi_handedness):
        total_fingers = 0
        for idx, hand_lms in enumerate(multi_hand_landmarks):
            hand_label = multi_handedness[idx].classification[0].label
            fingers = []
            
            # Logika Jempol
            if hand_label == "Right": 
                if hand_lms.landmark[4].x < hand_lms.landmark[5].x: fingers.append(1)
                else: fingers.append(0)
            else: 
                if hand_lms.landmark[4].x > hand_lms.landmark[5].x: fingers.append(1)
                else: fingers.append(0)
            
            # Logika 4 Jari lainnya
            tips = [8, 12, 16, 20]
            for tip in tips:
                if hand_lms.landmark[tip].y < hand_lms.landmark[tip - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)
                    
            total_fingers += fingers.count(1)
        return total_fingers

    def read_canvas_text(self):
        """Hanya memproses OCR ke layar, TANPA SUARA."""
        try:
            gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            
            text = pytesseract.image_to_string(thresh, config='--psm 10').strip()
            
            if text and text.isalnum(): 
                self.recognized_text = text.upper()
                print(f"🤖 OCR Berhasil: {self.recognized_text}")
            else:
                self.recognized_text = "?"
                print("🤖 OCR Gagal mendeteksi bentuk.")
        except Exception as e:
            print("Error OCR:", e)
            self.recognized_text = "ERROR"

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280) 
        cap.set(4, 720)
        
        window_name = "VisionAudio - Hand OCR"
        cv2.namedWindow(window_name)

        while cap.isOpened():
            success, frame = cap.read()
            if not success: break
            
            curr_time = time.time()
            fps = int(1 / (curr_time - self.prev_time)) if self.prev_time > 0 else 0
            self.prev_time = curr_time

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            if self.canvas is None: self.canvas = np.zeros_like(frame)

            rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_img)

            if results.multi_hand_landmarks:
                total = self.get_finger_count(results.multi_hand_landmarks, results.multi_handedness)
                
                cv2.putText(frame, f"Jari: {total}", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 200, 0), 2)
                
                # --- LOGIKA SUARA ANGKA  ---
                if total > 0:
                    self.speak(str(total))
                else:
                    self.last_spoken = "" # Reset jika tangan diturunkan

                for hand_lms in results.multi_hand_landmarks:
                    idx_tip = hand_lms.landmark[8]
                    cx, cy = int(idx_tip.x * w), int(idx_tip.y * h)
                    
                    index_up = hand_lms.landmark[8].y < hand_lms.landmark[6].y
                    middle_up = hand_lms.landmark[12].y < hand_lms.landmark[10].y
                    
                    # Mode Nulis (1 Jari) / Hover (2 Jari)
                    if index_up and not middle_up:
                        self.points.appendleft((cx, cy))
                        cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED) 
                    else:
                        self.points.appendleft(None)
                        cv2.circle(frame, (cx, cy), 15, (0, 0, 255), 2) 

                    self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
            else:
                # Reset suara jika tidak ada tangan di kamera
                self.last_spoken = ""

            # Gambar Coretan
            for i in range(1, len(self.points)):
                if self.points[i - 1] is None or self.points[i] is None: continue
                cv2.line(self.canvas, self.points[i - 1], self.points[i], (255, 255, 255), 18)

            combined = cv2.addWeighted(frame, 1, self.canvas, 0.8, 0)
            
            # UI
            cv2.putText(combined, f"FPS: {fps}", (w-150, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if self.recognized_text:
                cv2.putText(combined, f"HASIL BACA: {self.recognized_text}", (w//2 - 300, 100), 
                            cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 255, 255), 4)

            cv2.putText(combined, "[2 JARI: Pindah] | [1 JARI: Nulis]", (50, h-70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            cv2.putText(combined, "Q: Keluar | C: Hapus Layar | R: BACA TULISAN", (50, h-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            
            cv2.imshow(window_name, combined)

            # Kontrol Keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            if key == ord('c'): 
                self.points.clear() 
                self.canvas = np.zeros_like(frame)
                self.recognized_text = "" 
                
            if key == ord('r'):
                self.read_canvas_text()

            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = VisionAudio()
    app.run()