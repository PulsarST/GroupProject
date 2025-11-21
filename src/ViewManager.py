import flet as ft
from views import HomeContent, DataContent, AboutContent, SignInUpContent


class ViewManager:
    page: ft.Page | None = None
    content_container: ft.Container | None = None

    def __init__(self, page: ft.Page) -> None:
        ViewManager.page = page

        page.title = "Умная парковка"
        page.bgcolor = ft.Colors.WHITE
        page.scroll = ft.ScrollMode.AUTO
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed="blue")

        ViewManager.content_container = ft.Container(expand=True)
        page.add(ViewManager.content_container)

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
                    on_click=lambda _: ViewManager.switch_view(HomeContent()),
                ),
                ft.TextButton(
                    icon=ft.Icons.DATA_OBJECT,
                    text="Book a spot",
                    on_click=lambda _: ViewManager.switch_view(DataContent()),
                ),
                ft.TextButton(
                    icon=ft.Icons.GROUP,
                    text="About us !",
                    on_click=lambda _: ViewManager.switch_view(AboutContent()),
                ),
                ft.TextButton(
                    icon=ft.Icons.PERSON,
                    text="Sign in | Log in",
                    on_click=lambda _: ViewManager.switch_view(SignInUpContent()),
                ),
            ],
        )

        ViewManager.switch_view(HomeContent())

    @classmethod
    def switch_view(cls, content: ft.Row) -> None:
        """Switches only the content area to the given view."""
        if cls.content_container is not None and cls.page is not None:
            cls.content_container.content = content
            cls.page.update()
        else:
            raise RuntimeError("Content container not initialized in ViewManager")
