import logging
import flet as ft

from src.views import (
    HomeContent,
    DataContent,
    AboutContent,
    SignInUpContent
)


BACKEND_URL = "http://127.0.0.1:8000"
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)s][%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("smart_parking")


def main_page(page: ft.Page):
    page.title = "Умная парковка"
    page.bgcolor = ft.Colors.WHITE
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed="blue")
    content_area = ft.Container(expand=True)
    page.add(content_area)

    def switch_view(col: ft.Row):
        content_area.content = col
        page.update()

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.APPS),
        leading_width=40,
        title=ft.Text("Smart parking"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[
            ft.TextButton(
                icon=ft.Icons.HOME,
                text="Home",
                on_click=lambda _: switch_view(HomeContent()),
            ),
            ft.TextButton(
                icon=ft.Icons.DATA_OBJECT,
                text="Book an spot",
                on_click=lambda _: switch_view(DataContent()),
            ),
            ft.TextButton(
                icon=ft.Icons.GROUP,
                text="About us !",
                on_click=lambda _: switch_view(AboutContent()),
            ),
            ft.TextButton(
                icon=ft.Icons.PERSON,
                text="Sign in | Log in",
                on_click=lambda _: switch_view(SignInUpContent()),
            ),
        ],
    )

    switch_view(HomeContent())


if __name__ == "__main__":
    ft.app(
        target=main_page,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="../assets",
        port=8080
    )
