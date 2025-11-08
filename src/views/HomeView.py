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
            ft.Image(
                src=f"https://sdmntprwestcentralus.oaiusercontent.com/files/00000000-8184-61fb-a617-4318a023d0cd/raw?se=2025-10-22T05%3A35%3A09Z&sp=r&sv=2024-08-04&sr=b&scid=6d7d842f-e541-43cb-9185-e94712fb30e0&skoid=1e4bb9ed-6bb5-424a-a3aa-79f21566e722&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-10-21T23%3A46%3A50Z&ske=2025-10-22T23%3A46%3A50Z&sks=b&skv=2024-08-04&sig=XMBfZ%2B9q/NPKHZkh7zCVt26TMUZwZiYmHGNYYcjaHnE%3D",
                width=1024 / 2,
                height=1536 / 2,
            ),
        ]

    def on_create_order_click(self, _):
        from ViewManager import ViewManager

        ViewManager.switch_view(DataContent())
