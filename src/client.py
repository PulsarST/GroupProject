import logging
import flet as ft

BACKEND_URL = "http://127.0.0.1:8000"
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s][%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("smart_parking")

class HomeContent(ft.Column):
    def __init__(self) -> None:
        super().__init__()
        self.controls = [
            ft.Text("HOME !")
        ]

class DataContent(ft.Column):
    def __init__(self) -> None:
        super().__init__()
        self.controls = []

class AboutContent(ft.Column):
    def __init__(self) -> None:
        super().__init__()
        self.controls = []

class SignInUpContent(ft.Column):
    def __init__(self) -> None:
        super().__init__()
        self.controls = []

def main_page(page: ft.Page):
    page.title = "Умная парковка"
    page.bgcolor = ft.Colors.WHITE
    page.scroll = ft.ScrollMode.AUTO
    content_area = ft.Container(expand=True)
    page.add(content_area)
    
    def switch_view(col: ft.Column):
        content_area.content = col
        page.update()

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.APPS),
        leading_width=40,
        title=ft.Text("Smart parking"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[
            ft.TextButton(icon=ft.Icons.HOME, text="Home", on_click=lambda _: switch_view(HomeContent())),
            ft.TextButton(icon=ft.Icons.DATA_OBJECT, text="Book an spot", on_click=lambda _: switch_view(DataContent())),
            ft.TextButton(icon=ft.Icons.GROUP, text="About us !", on_click=lambda _: switch_view(AboutContent())),
            ft.TextButton(icon=ft.Icons.PERSON, text="Sign in | Log in", on_click=lambda _: switch_view(SignInUpContent()))
        ]
    )

    switch_view(HomeContent())


if __name__ == "__main__":
    ft.app(target=main_page, view=ft.AppView.WEB_BROWSER)
