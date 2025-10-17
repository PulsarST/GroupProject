import flet as ft

from views.DataView import DataContent


class HomeContent(ft.Row):
    def __init__(self) -> None:
        super().__init__(
            spacing=200,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.controls = [
            ft.Column(
                controls=[
                    ft.Text(
                        value="Welcome !",
                        size=36,
                        style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                    ),
                    ft.TextButton(
                        text="Oder a spot",
                        icon=ft.Icons.CREATE,
                        on_click=self.on_create_order_click,
                    ),
                ]
            ),
            ft.Image(src=f"choose_us.png", width=1024 / 2, height=1536 / 2),
        ]

    def on_create_order_click(self, _):
        from ViewManager import ViewManager

        ViewManager.switch_view(DataContent())
