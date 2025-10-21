import subprocess
import sys
import os
import time
import requests

from client import main_page
import flet as ft


def wait_for_server(url: str, timeout: int = 30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200 or r.status_code == 404:
                print("Сервер запущен")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    raise TimeoutError("Сервер не запустился за отведённое время")

if __name__ == "__main__":
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    server_process = subprocess.Popen([sys.executable, server_path])

    try:
        wait_for_server("http://127.0.0.1:8000/")
        ft.app(target=main_page, view=ft.AppView.WEB_BROWSER, port=8550)
    finally:
        server_process.terminate()
