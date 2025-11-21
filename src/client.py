import logging
import flet as ft

from ViewManager import ViewManager

BACKEND_URL = "http://127.0.0.1:8000"
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s][%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("smart_parking")


def main_page(page: ft.Page):
    ViewManager(page)


if __name__ == "__main__":
    ft.app(
        target=main_page, view=ft.AppView.WEB_BROWSER, assets_dir="../assets", port=8080
    )
