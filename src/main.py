from client import main_page
import flet as ft

if __name__ == "__main__":
    ft.app(target=main_page, view=ft.AppView.WEB_BROWSER, port=8550)
