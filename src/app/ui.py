import flet as ft
from flet import Colors
import requests

API_BASE = "http://localhost:8000"

def main(page: ft.Page):
    page.title = "Attendance Dashboard"
    page.vertical_alignment = ft.MainAxisAlignment.START

    today_text = ft.Text(value="Fetching today's count...", size=20, weight="bold")

    chart = ft.BarChart(
        border=ft.border.all(1, Colors.GREY_400),
        left_axis=ft.ChartAxis(
            labels_size=20,
            title=ft.Text("Count"),
            title_size=20,
        ),
        bottom_axis=ft.ChartAxis(
            labels_size=20,
            labels=[],
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=Colors.GREY_300,
            width=1,
            dash_pattern=[3, 3],
        ),
        tooltip_bgcolor=Colors.with_opacity(0.5, Colors.GREY_300),
        max_y=0,  
        interactive=True,
        expand=True,
    )

    def load_data():
        try:
            today_res = requests.get(f"{API_BASE}/attendance/today").json()
            today_text.value = f"Today's Attendance: {today_res['count']}"

            weekly_res = requests.get(f"{API_BASE}/attendance/week").json()
            labels = weekly_res["labels"]
            counts = weekly_res["counts"]

            bar_groups = []
            max_count = max(counts) if counts else 0
            colors = [
                Colors.GREEN,
                Colors.BLUE,
                Colors.RED,
                Colors.ORANGE,
                Colors.PURPLE,
                Colors.CYAN,
                Colors.YELLOW,
            ]

            for i, count in enumerate(counts):
                bar_groups.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=count,
                                width=40,
                                color=colors[i % len(colors)],
                                border_radius=0,
                            ),
                        ],
                    )
                )

            chart.bar_groups = bar_groups
            chart.bottom_axis.labels = [
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Container(ft.Text(label), padding=10)
                ) for i, label in enumerate(labels)
            ]
            chart.max_y = max_count + max_count * 0.1
            page.update()

        except Exception as e:
            today_text.value = f"Error loading data: {e}"
            page.update()

    def shutdown_server(e):
        try:
            res = requests.post(f"{API_BASE}/shutdown")
            if res.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Server shutdown triggered!"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Failed to shutdown server: {res.text}"))
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
        page.snack_bar.open = True
        page.update()

    shutdown_button = ft.ElevatedButton("Shutdown Server", on_click=shutdown_server)

    load_data()

    page.add(
        ft.Column(
            [
                today_text,
                chart,
                shutdown_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
