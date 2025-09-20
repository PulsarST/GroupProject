import flet as ft
import httpx

BACKEND_URL = "http://127.0.0.1:8000"

MENU = [
    "Overview",
    "Data",
    "Functional Core",
    "Pipelines",
    "Async/FRP",
    "Reports",
    "Tests",
    "About",
]

MENU_ICONS = [
    ft.Icons.DASHBOARD,
    ft.Icons.STORAGE,
    ft.Icons.SETTINGS,
    ft.Icons.TRENDING_UP,
    ft.Icons.TIMELINE,
    ft.Icons.INSIGHTS,
    ft.Icons.BUG_REPORT,
    ft.Icons.INFO,
]

state = {}


def main_page(page: ft.Page):
    page.title = "Умная парковка"
    page.bgcolor = ft.Colors.WHITE
    page.scroll = ft.ScrollMode.AUTO

    section_name = ft.Text(
        "Overview", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87
    )
    section_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    sidebar_open = True

    # ---------------- Sidebar Toggle ---------------- #
    def toggle_sidebar():
        nonlocal sidebar_open
        sidebar_open = not sidebar_open
        sidebar_container.width = 200 if sidebar_open else 50

        # Update all buttons content
        for btn, label, icon in zip(sidebar_buttons, MENU, MENU_ICONS):
            btn.content = ft.Row(
                [
                    ft.Icon(icon, size=24),
                    ft.Text(label, size=14) if sidebar_open else ft.Container(width=0),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            )
        page.update()

    toggle_btn = ft.IconButton(
        icon=ft.Icons.MENU,
        icon_color=ft.Colors.BLACK87,
        on_click=lambda e: toggle_sidebar(),
    )

    # ---------------- Sidebar Buttons ---------------- #
    sidebar_buttons = []
    for label, icon in zip(MENU, MENU_ICONS):
        btn = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(icon, size=24), ft.Text(label, size=14)],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            bgcolor=ft.Colors.GREY_200,
            color=ft.Colors.BLACK87,
            width=180,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            on_click=lambda e, name=label: switch_section(name),
        )
        sidebar_buttons.append(btn)

    sidebar_column = ft.Column(
        [toggle_btn, *sidebar_buttons],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    # ---------------- Animated Sidebar ---------------- #
    sidebar_container = ft.Container(
        content=sidebar_column,
        width=200,
        bgcolor=ft.Colors.GREY_200,
        padding=10,
        animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    # ---------------- Main Content ---------------- #
    main_content_container = ft.Container(
        content=ft.Column(
            [section_name, section_content],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True,  # fills vertical space
        ),
        expand=True,
        padding=20,
        animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    # ---------------- Layout ---------------- #
    page.add(
        ft.Row(
            [sidebar_container, main_content_container],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,  # <-- aligns content to top
        )
    )

    # ---------------- Section Handling ---------------- #
    def switch_section(name: str):
        section_name.value = name
        update_section()

    def update_section():
        section_content.controls.clear()
        if section_name.value == "Overview":
            show_overview()
        elif section_name.value == "Data":
            show_data_section()
        else:
            section_content.controls.append(
                ft.Text(
                    f"This is {section_name.value} section", color=ft.Colors.BLACK87
                )
            )
        page.update()

    # ---------------- Overview Section ---------------- #

    # ---------------- Overview Section ---------------- #
    def show_overview():
        section_content.controls.clear()
        if not state.get("zones"):
            section_content.controls.append(
                ft.Text(
                    "No data loaded. Go to Data section to load seed.",
                    color=ft.Colors.BLACK87,
                )
            )
            page.update()
            return

        table_rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(z["id"], color=ft.Colors.BLACK87)),
                    ft.DataCell(ft.Text(z["name"], color=ft.Colors.BLACK87)),
                ]
            )
            for z in state["zones"]
        ]
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Name"))],
            rows=table_rows,
            border=ft.border.all(1, ft.Colors.BLACK12),
            heading_row_color=ft.Colors.GREY_400,  # <-- darker header
            heading_text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
            ),
        )
        section_content.controls.append(table)
        page.update()

    # ---------------- Data Section ---------------- #
    def show_data_section():
        async def load_data(e):
            section_content.controls.clear()
            section_content.controls.append(
                ft.Text("Loading...", color=ft.Colors.BLACK87)
            )
            page.update()

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{BACKEND_URL}/load_seed")
                    result = response.json()
                    r = await client.get(f"{BACKEND_URL}/data")
                    data = r.json()
                    state.update(data)

                section_content.controls.clear()
                section_content.controls.append(
                    ft.Text(
                        f"Loaded {result['zones']} zones, {result['spots']} spots",
                        color=ft.Colors.BLACK87,
                    )
                )
            except Exception as e:
                section_content.controls.clear()
                section_content.controls.append(
                    ft.Text(f"Error: {e}", color=ft.Colors.RED)
                )
            page.update()

        section_content.controls.clear()
        section_content.controls.append(
            ft.ElevatedButton(
                "Load Data",
                bgcolor=ft.Colors.GREY_200,
                color=ft.Colors.BLACK87,
                width=180,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
                on_click=load_data,
            )
        )
