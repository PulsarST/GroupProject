import datetime
import flet as ft
import flet_map as map


class DataContent(ft.Row):
    def __init__(self) -> None:
        super().__init__(
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        self.expand = True
        self.height = 900

        my_map = map.Map(
            expand=1,
            initial_center=map.MapLatitudeLongitude(43.236517, 76.930513),
            initial_zoom=19,
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda _: print("TileLayer error"),
                )
            ],
        )

        self.start_datetime: datetime.datetime | None = None
        self.end_time: datetime.datetime | None = None

        self.time_picker = ft.TimePicker(
            help_text="Choose time for parking", on_change=self.time_picker_on_change
        )

        self.end_time_picker = ft.TimePicker(
            help_text="Choose end time for parking",
            on_change=self.endtime_picker_on_change,
        )

        content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="Data content",
                        style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                    ),
                    ft.TextButton(
                        text="choose start time",
                        icon=ft.Icons.TIME_TO_LEAVE,
                        on_click=self.open_time_picker,
                    ),
                    ft.TextButton(
                        text="choose end time",
                        icon=ft.Icons.TIME_TO_LEAVE_SHARP,
                        on_click=self.open_endtime_picker,
                    ),
                    ft.TextButton(
                        text="Order",
                        icon=ft.Icons.CREATE,
                        on_click=self.on_confirm_session,
                    ),
                ],
            ),
            bgcolor=ft.Colors.GREY_200,
            padding=20,
        )

        self.controls.append(my_map)
        self.controls.append(content)

    def on_confirm_session(self, _):
        print(f"start time: {self.start_datetime}\nend time: {self.end_time}")

    def time_picker_on_change(self, _):
        selected_time = self.time_picker.value
        if selected_time:
            self.start_datetime = datetime.datetime.combine(
                datetime.date.today(), selected_time
            )

    def endtime_picker_on_change(self, _):
        selected_time = self.end_time_picker.value
        if selected_time:
            self.end_time = datetime.datetime.combine(
                datetime.date.today(), selected_time
            )

    def open_endtime_picker(self, _):
        if self.end_time_picker is not None and self.page is not None:
            self.page.open(self.end_time_picker)

    def open_time_picker(self, _):
        if self.time_picker is not None and self.page is not None:
            self.page.open(self.time_picker)
