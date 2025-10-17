import flet as ft

class HomeContent(ft.Row):
    def __init__(self) -> None:
        super().__init__(spacing=100)
        self.controls = [
            ft.Text(value="Welcome !", size=36, style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
            ft.Image(
                src=f"choose_us.png",
                width=1024 / 2,
                height=1536 / 2
            )
        ]


