# 🎙️ VisionAudio: Hand Tracking, Air Writing & OCR AI

VisionAudio adalah aplikasi interaktif berbasis **Computer Vision** yang memungkinkan pengguna untuk melakukan deteksi jari (*finger counting*), menulis di udara (*air writing*), dan membaca tulisan tangan tersebut menggunakan AI (**Tesseract OCR**), disertai dengan *Voice Feedback* (Text-to-Speech).

Aplikasi ini dirancang sebagai eksperimen *Human-Computer Interaction* (HCI) yang hanya membutuhkan webcam standar tanpa perangkat tambahan.

---

## ✨ Fitur Utama
* **Real-time Finger Counting:** Menghitung 1 hingga 10 jari dari kedua tangan dengan suara penyebutan angka otomatis.
* **Smart Air Writing:** * ✌️ **Mode Hover (Pindah):** Angkat jari telunjuk dan tengah (simbol Peace) untuk memindahkan kursor tanpa mencoret.
  * ☝️ **Mode Draw (Menulis):** Lipat jari tengah (sisakan telunjuk) untuk mulai menggoreskan tinta putih tebal di layar.
* **Air OCR (Optical Character Recognition):** Mampu mengenali huruf kapital yang ditulis di udara dan menampilkannya di UI.
* **Voice Feedback:** Sistem suara otomatis menggunakan `pyttsx3` yang berjalan di *background thread* (Anti-lag).

---

## 🛠️ Prasyarat Sistem (Wajib)

Sebelum menjalankan kode Python, Anda **HARUS** menginstal mesin Tesseract OCR di Windows Anda:

1. **Download Tesseract:** [UB-Mannheim Tesseract Repo](https://github.com/UB-Mannheim/tesseract/wiki).
2. **Instalasi:** Gunakan jalur *default* di `C:\Program Files\Tesseract-OCR`.
3. **Bahasa:** Pastikan mencentang opsi bahasa Inggris/Indonesia saat instalasi jika diperlukan.

---

## 🚀 Panduan Instalasi & Library

Sangat disarankan menggunakan **Virtual Environment (venv)** untuk menghindari konflik library.

### 1. Setup Environment
Buka terminal di folder project dan jalankan:
```bash
# Membuat venv
python -m venv venv

# Aktivasi venv (Windows)
.\venv\Scripts\activate

2. Instalasi Library yang Dibutuhkan
Anda bisa menginstal satu per satu dengan perintah berikut:

Bash
pip install numpy==1.26.4
pip install mediapipe==0.10.14
pip install opencv-python==4.10.0.84
pip install pyttsx3
pip install pytesseract
pip install pywin32

🎮 Cara Menjalankan
Setelah semua library terinstal dan venv aktif, jalankan perintah:

Bash
python vision_audio.py
