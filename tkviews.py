import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import sys
import requests
import re
import random
import string
import base64
import urllib.parse
import json
from requests_toolbelt import MultipartEncoder
from PIL import Image
import pytesseract
from requests.exceptions import RequestException

# Configuração do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

COOKIES, SUKSES, LOGOUT, GAGAL = {"Cookie": None}, [], [], []


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        # Schedule widget update in main thread
        self.widget.after(0, lambda: self.widget.insert(tk.END, s))
        self.widget.after(0, lambda: self.widget.see(tk.END))

    def flush(self):
        pass


class DIPERLUKAN:
    def __init__(self):
        pass

    def LOGIN(self):
        with requests.Session() as session:
            session.headers.update({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Host': 'zefoy.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document'
            })
            response = session.get('https://zefoy.com/').text
            if 'Sorry, you have been blocked' in response or 'Just a moment...' in response:
                print("Zefoy server is currently affected by cloudflare. Please check zefoy.com!")
                sys.exit()
            else:
                self.captcha_image = re.search(r'src="(.*?)" onerror="errimg\(\)"', response).group(1).replace('amp;', '')
                self.form = re.search(r'type="text" name="(.*?)"', response).group(1)
                session.headers.update({
                    'Cookie': "; ".join([f"{x}={y}" for x, y in session.cookies.get_dict().items()]),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
                })
                response2 = session.get('https://zefoy.com{}'.format(self.captcha_image))
                with open('Penyimpanan/Gambar.png', 'wb') as w:
                    w.write(response2.content)
                session.headers.update({
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Connection': 'keep-alive',
                    'Origin': 'null',
                    'Cache-Control': 'max-age=0',
                    'Cookie': "; ".join([f"{x}={y}" for x, y in session.cookies.get_dict().items()])
                })
                data = {self.form: self.BYPASS_CAPTCHA()}
                response3 = session.post('https://zefoy.com/', data=data).text
                if 'placeholder="Enter Video URL"' in response3:
                    COOKIES["Cookie"] = "; ".join([f"{x}={y}" for x, y in session.cookies.get_dict().items()])
                    print("LOGIN SUCCESSFUL!")
                    time.sleep(2.5)
                    return COOKIES["Cookie"]
                else:
                    print("LOGIN FAILED!")
                    time.sleep(2.5)
                    return False

    def BYPASS_CAPTCHA(self):
        self.file_gambar = 'Penyimpanan/Gambar.png'
        self.image = Image.open(self.file_gambar)
        self.image_string = pytesseract.image_to_string(self.image)
        return self.image_string.replace('\n', '')

    def MENDAPATKAN_FORMULIR(self, video_url):
        with requests.Session() as session:
            session.headers.update({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Host': 'zefoy.com',
                'Cookie': f'{COOKIES["Cookie"]}; window_size=1280x551; user_agent=Mozilla%2F5.0',
                'Sec-Fetch-Site': 'none',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
            })
            response = session.get('https://zefoy.com/').text
            if 'placeholder="Enter Video URL"' in response:
                self.video_form = re.search(r'name="(.*?)" placeholder="Enter Video URL"', response).group(1)
                self.post_action = re.findall(r'action="(.*?)">', response)[3]
                print("SUCCESSFULLY FOUND VIDEO FORM!")
                time.sleep(1.5)
                self.MENGIRIMKAN_TAMPILAN(self.video_form, self.post_action, video_url)
            else:
                print("VIDEO FORM NOT FOUND!")
                time.sleep(3.5)
                COOKIES["Cookie"] = None
                return False

    def MENGIRIMKAN_TAMPILAN(self, video_form, post_action, video_url):
        global SUKSES, GAGAL
        with requests.Session() as session:
            boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
                'Cookie': f'{COOKIES["Cookie"]};',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Connection': 'keep-alive',
                'Origin': 'https://zefoy.com',
                'Sec-Fetch-Dest': 'empty',
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Accept': '*/*'
            })
            data = MultipartEncoder({video_form: (None, video_url)}, boundary=boundary)
            response = session.post('https://zefoy.com/{}'.format(post_action), data=data).text
            self.base64_string = base64.b64decode(urllib.parse.unquote(response[::-1])).decode()
            if 'type="submit"' in self.base64_string:
                SUKSES.append(self.base64_string)
                print(f"SUCCESS: +1000 views sent for {video_url}")
                time.sleep(2.5)
                self.MENGIRIMKAN_TAMPILAN(video_form, post_action, video_url)
            elif 'Checking Timer...' in self.base64_string:
                print("WAIT FOR 4 MINUTES!")
                time.sleep(2.5)
                for _ in range(8):
                    self.DELAY(0, 30)
                    self.ANTI_LOGOUT()
                print("TRY SENDING VIEWS AGAIN!")
                time.sleep(2.5)
                self.MENGIRIMKAN_TAMPILAN(video_form, post_action, video_url)
            else:
                print("FAILED TO SEND VIEWS!")
                time.sleep(3.5)
                COOKIES["Cookie"] = None
                return False

    def ANTI_LOGOUT(self):
        with requests.Session() as session:
            session.headers.update({
                'Accept-Language': 'en-US,en;q=0.9',
                'Cookie': COOKIES["Cookie"],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Host': 'zefoy.com',
                'Sec-Fetch-Site': 'none',
                'User-Agent': 'Mozilla/5.0',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
            })
            session.get('https://zefoy.com/')
            return True

    def DELAY(self, menit, detik):
        total = menit * 60 + detik
        while total:
            m, s = divmod(total, 60)
            print(f"WAIT: {m:02d}:{s:02d} | SUKSES: {len(SUKSES)} | GAGAL: {len(GAGAL)}")
            time.sleep(1)
            total -= 1
        return "0_0"


class MAIN:
    def __init__(self):
        self.init_gui()

    def init_gui(self):
        self.root = tk.Tk()
        self.root.title("TikTok Views Automator by codywaroops")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        try:
            self.root.iconbitmap(r"C:\Users\bomba\Desktop\projeto\tkviews\app\tkviews.ico")
        except Exception as e:
            print(f"[ERROR] Failed to load icon: {e}")
        label = tk.Label(self.root, text="Enter TikTok Video URL:", font=("Arial", 12))
        label.pack(pady=10)
        self.entry = tk.Entry(self.root, width=50, font=("Arial", 10))
        self.entry.pack(pady=10)
        self.start_button = tk.Button(
            self.root, text="Start", command=self.start_process,
            font=("Arial", 12), bg="#4CAF50", fg="white", width=10
        )
        self.start_button.pack(pady=5)
        self.stop_button = tk.Button(
            self.root, text="Stop", command=self.stop_process,
            font=("Arial", 12), bg="red", fg="white", width=10
        )
        self.stop_button.pack(pady=5)
        log_label = tk.Label(self.root, text="Logs:", font=("Arial", 12))
        log_label.pack(pady=5)
        self.log_text = tk.scrolledtext.ScrolledText(self.root, width=70, height=10, font=("Arial", 10))
        self.log_text.pack(pady=10)
        # Redirect sys.stdout so that prints appear in the log widget.
        sys.stdout = TextRedirector(self.log_text)
        self.root.mainloop()

    def start_process(self):
        video_url = self.entry.get().strip()
        if not video_url:
            print("[ERROR] Please enter a valid TikTok video URL.")
            return
        print("[INFO] Starting the process...")
        self.start_button.config(state=tk.DISABLED)
        self.running = True

        def run_script():
            cycle = 0
            try:
                if ('tiktok.com' in video_url) or ('/video/' in video_url):
                    while self.running:
                        # Determine wait time based on cycle number:
                        # First cycle: 10 seconds, second: 120 seconds, then every subsequent: 240 seconds.
                        if cycle == 0:
                            wait_time = 10
                        elif cycle == 1:
                            wait_time = 120
                        else:
                            wait_time = 240

                        for remaining in range(wait_time, 0, -1):
                            if not self.running:
                                break
                            print(f"Waiting for next view: {remaining} seconds, Views sent: {len(SUKSES)}")
                            time.sleep(1)
                        if not self.running:
                            break

                        print("[INFO] Sending views...")
                        try:
                            if (COOKIES['Cookie'] is None) or (len(COOKIES['Cookie']) == 0):
                                DIPERLUKAN().LOGIN()
                            else:
                                DIPERLUKAN().MENDAPATKAN_FORMULIR(video_url)
                        except (AttributeError, IndexError):
                            print("[ERROR] Error in form parsing. Retrying...")
                            time.sleep(7.5)
                            continue
                        except RequestException:
                            print("[ERROR] Connection problem! Retrying...")
                            time.sleep(7.5)
                            continue
                        cycle += 1
                else:
                    print("[ERROR] Please enter a valid TikTok video URL.")
                    self.start_button.config(state=tk.NORMAL)
            except Exception as e:
                print(f"[ERROR] {str(e)}")
                self.start_button.config(state=tk.NORMAL)

        thread = threading.Thread(target=run_script)
        thread.start()

    def stop_process(self):
        self.running = False
        self.root.destroy()


if __name__ == '__main__':
    MAIN()
