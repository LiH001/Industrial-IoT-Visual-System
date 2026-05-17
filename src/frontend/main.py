"""工业可视化监控平台 NiceGUI 前端入口。"""

import asyncio
import json
from datetime import datetime
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from nicegui import ui

PLATFORM_NAME = "工业可视化监控平台"
API_BASE_URL = "http://localhost:8000/api/v1/data"
LATEST_DATA_URL = f"{API_BASE_URL}/latest"
HISTORICAL_DATA_URL = f"{API_BASE_URL}/historical"
DEVICE_IDS = ["plc_01", "plc_02", "plc_03"]
MAX_HISTORY_POINTS = 20

PANEL_OVERVIEW = "panel_overview"
PANEL_REALTIME = "panel_realtime"
PANEL_ALARM = "panel_alarm"
PANEL_SETTINGS = "panel_settings"

STATUS_CLASSES = "bg-green-4 bg-grey-6 bg-red-5 fault-pulse"
STATUS_TEXT_CLASSES = (
    "text-green-4 text-grey-4 text-red-4 text-slate-700 dark:text-slate-200"
)
STATUS_CONFIG = {
    "running": {
        "text": "运行中",
        "dot_class": "bg-green-4",
        "text_class": "text-green-4",
    },
    "stopped": {
        "text": "已停止",
        "dot_class": "bg-grey-6",
        "text_class": "text-slate-700 dark:text-slate-200",
    },
    "fault": {
        "text": "故障",
        "dot_class": "bg-red-5 fault-pulse",
        "text_class": "text-red-4",
    },
}

# 强制开启暗黑模式，并保留控制器供系统设置面板双向绑定主题状态。
theme = ui.dark_mode(value=True)

# 注入全局中文字体，确保中文 UI 文本清晰显示。
ui.add_head_html(
    '<style>body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; }</style>'
)
ui.add_head_html("""
    <style>
        body {
            background: #f3f4f6;
        }

        body.body--dark {
            background: #05070a;
        }

        .admin-main {
            min-height: calc(100vh - 50px);
        }

        .hidden-tabs {
            display: none !important;
        }

        .trend-chart {
            height: 360px;
            border: 1px solid rgba(100, 181, 246, 0.16);
            border-radius: 10px;
            background:
                radial-gradient(circle at 18% 20%, rgba(0, 229, 255, 0.10), transparent 30%),
                linear-gradient(135deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.01));
        }

        .overview-table .q-table__top,
        .overview-table thead tr,
        .overview-table tbody td {
            background: #ffffff;
            color: #111827;
        }

        .overview-table thead th {
            background: #f3f4f6;
            color: #1d4ed8;
            font-weight: 700;
        }

        body.body--dark .overview-table .q-table__top,
        body.body--dark .overview-table thead tr,
        body.body--dark .overview-table tbody td {
            background: #111827;
            color: #e5e7eb;
        }

        body.body--dark .overview-table thead th {
            background: #0b1120;
            color: #93c5fd;
        }

        .tb-card {
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 9999px;
            box-shadow: 0 0 10px currentColor;
        }

        .fault-pulse {
            animation: fault-pulse 1s infinite;
        }

        @keyframes fault-pulse {
            0%, 100% {
                opacity: 1;
                box-shadow: 0 0 4px #ef4444, 0 0 14px #ef4444;
            }
            50% {
                opacity: 0.35;
                box-shadow: 0 0 2px #ef4444;
            }
        }

        .telemetry-value {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
                "Liberation Mono", "Courier New", monospace;
            letter-spacing: -0.04em;
            line-height: 1;
        }
    </style>
    """)

device_cards: dict[str, dict[str, Any]] = {}
# NiceGUI 的 ui.label/ui.table/ui.echart 是工厂函数，不适合作为类型注解；
# 这里统一使用 Any，避免 IDE/Pylance 把它们标记为类型错误。
last_update_label: Any
trend_chart: Any | None = None
main_panels: Any | None = None
history_table: Any | None = None
history_status_label: Any | None = None
data_timer: Any | None = None
time_labels: list[str] = []
temperature_history: list[float] = []


def fetch_latest_data() -> list[dict[str, Any]]:
    """从后端获取最新的 PLC 模拟遥测数据。"""
    with urlopen(LATEST_DATA_URL, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_historical_data(limit: int = 50) -> list[dict[str, Any]]:
    """从后端获取设备历史数据。"""
    query = urlencode({"limit": limit})
    with urlopen(f"{HISTORICAL_DATA_URL}?{query}", timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def build_temperature_chart_options() -> dict[str, Any]:
    """构建全中文的暗色科技感 ECharts 折线图配置。"""
    return {
        "backgroundColor": "transparent",
        "textStyle": {
            "color": "#cfd8dc",
            "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif",
        },
        "title": {
            "text": "全局温度实时趋势",
            "left": "center",
            "top": 8,
            "textStyle": {"color": "#ffffff", "fontSize": 18},
        },
        "tooltip": {
            "trigger": "axis",
            "formatter": "时间：{b}<br/>平均温度：{c} °C",
            "backgroundColor": "rgba(10, 18, 28, 0.92)",
            "borderColor": "#00e5ff",
            "borderWidth": 1,
            "textStyle": {"color": "#ffffff"},
            "axisPointer": {"type": "line", "lineStyle": {"color": "#00e5ff"}},
        },
        "legend": {
            "data": ["平均温度"],
            "top": 42,
            "textStyle": {"color": "#cfd8dc"},
        },
        "grid": {
            "left": "4%",
            "right": "4%",
            "top": 86,
            "bottom": 44,
            "containLabel": True,
        },
        "xAxis": {
            "type": "category",
            "name": "时间",
            "boundaryGap": False,
            "data": time_labels,
            "nameTextStyle": {"color": "#cfd8dc"},
            "axisLabel": {"color": "#b0bec5"},
            "axisLine": {"lineStyle": {"color": "#455a64"}},
            "splitLine": {"show": False},
        },
        "yAxis": {
            "type": "value",
            "name": "温度 (°C)",
            "min": 0,
            "max": 120,
            "nameTextStyle": {"color": "#cfd8dc"},
            "axisLabel": {"color": "#b0bec5"},
            "axisLine": {"lineStyle": {"color": "#455a64"}},
            "splitLine": {"lineStyle": {"color": "rgba(176, 190, 197, 0.14)"}},
        },
        "series": [
            {
                "name": "平均温度",
                "type": "line",
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 7,
                "showSymbol": True,
                "data": temperature_history,
                "lineStyle": {"width": 3, "color": "#00e5ff"},
                "itemStyle": {
                    "color": "#69f0ae",
                    "borderColor": "#ffffff",
                    "borderWidth": 1,
                },
                "areaStyle": {
                    "opacity": 0.42,
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(0, 229, 255, 0.50)"},
                            {"offset": 0.55, "color": "rgba(105, 240, 174, 0.18)"},
                            {"offset": 1, "color": "rgba(0, 229, 255, 0.02)"},
                        ],
                    },
                },
            }
        ],
    }


def build_header() -> None:
    """构建顶部标题栏。"""
    global last_update_label

    with ui.header().classes(
        "shadow-4 items-center text-slate-900 dark:text-slate-100"
    ):
        ui.icon("factory").classes("text-blue-4 text-h5 q-mr-sm")
        ui.label(PLATFORM_NAME).classes("text-xl text-weight-bold tracking-wide")
        ui.space()
        last_update_label = ui.label("等待遥测数据...").classes(
            "text-slate-700 dark:text-slate-200 text-caption"
        )


def switch_panel(panel_name: str) -> None:
    """通过侧边栏按钮切换 tab panel。"""
    if main_panels is not None:
        main_panels.set_value(panel_name)


def add_nav_button(text: str, icon: str, panel_name: str) -> None:
    """添加侧边栏导航按钮。"""
    ui.button(
        text,
        icon=icon,
        on_click=lambda _event, p=panel_name: switch_panel(p),
    ).props("flat align=left no-caps").classes(
        "w-full justify-start text-left text-slate-900 dark:text-slate-100 q-py-sm"
    )


def build_left_drawer() -> None:
    """构建左侧后台导航栏。"""
    with ui.left_drawer(value=True).classes("text-slate-900 dark:text-slate-100"):
        with ui.column().classes("w-full q-pa-md q-gutter-sm"):
            ui.label("功能菜单").classes(
                "text-slate-600 dark:text-slate-300 text-caption q-mb-sm"
            )
            add_nav_button("数据总览", "dashboard", PANEL_OVERVIEW)
            add_nav_button("实时监控", "memory", PANEL_REALTIME)
            add_nav_button("报警中心", "warning", PANEL_ALARM)
            add_nav_button("系统设置", "settings", PANEL_SETTINGS)


async def load_historical_table() -> None:
    """刷新数据总览表格。"""
    if history_table is None:
        return

    if history_status_label is not None:
        history_status_label.set_text("正在获取历史数据...")

    try:
        rows = await asyncio.to_thread(fetch_historical_data, 50)
    except (URLError, TimeoutError, OSError) as exc:
        if history_status_label is not None:
            history_status_label.set_text(f"历史数据获取失败：{exc}")
        return

    history_table.rows = rows
    history_table.update()

    if history_status_label is not None:
        history_status_label.set_text(f"历史数据已刷新：{datetime.now():%H:%M:%S}")


def build_overview_panel() -> None:
    """构建数据总览面板。"""
    global history_table, history_status_label

    columns = [
        {
            "name": "timestamp",
            "label": "时间 (Timestamp)",
            "field": "timestamp",
            "align": "left",
            "sortable": True,
        },
        {
            "name": "device_id",
            "label": "设备ID (Device ID)",
            "field": "device_id",
            "align": "left",
            "sortable": True,
        },
        {
            "name": "temperature",
            "label": "温度 (°C)",
            "field": "temperature",
            "align": "right",
            "sortable": True,
        },
        {
            "name": "pressure",
            "label": "压力 (MPa)",
            "field": "pressure",
            "align": "right",
            "sortable": True,
        },
    ]

    with ui.column().classes("w-full q-gutter-md"):
        with ui.card().classes(
            "w-full shadow-6 rounded-borders q-pa-md text-slate-900 dark:text-slate-100"
        ):
            with ui.row().classes("w-full items-center justify-between q-mb-md"):
                with ui.row().classes("items-center"):
                    ui.icon("dashboard").classes("text-blue-4 text-h5 q-mr-sm")
                    ui.label("设备历史数据查询").classes("text-h6 text-weight-bold")
                ui.button(
                    "刷新历史数据", icon="refresh", on_click=load_historical_table
                ).props("unelevated color=primary")

            history_status_label = ui.label("点击刷新按钮获取历史数据").classes(
                "text-slate-700 dark:text-slate-200 text-caption q-mb-sm"
            )
            history_table = ui.table(
                columns=columns, rows=[], row_key="timestamp", pagination=10
            ).classes("overview-table w-full ")


def build_chart_panel() -> None:
    """构建实时监控页上半部动态趋势图卡片。"""
    global trend_chart

    with ui.card().classes(
        "w-full shadow-6 rounded-borders q-pa-md text-slate-900 dark:text-slate-100"
    ):
        with ui.row().classes("w-full items-center justify-between q-mb-md"):
            with ui.row().classes("items-center"):
                ui.icon("show_chart").classes("text-blue-4 text-h5 q-mr-sm")
                ui.label("全局温度实时趋势").classes("text-subtitle1 text-weight-bold")
            ui.label("最近 20 个历史数据点").classes(
                "text-slate-600 dark:text-slate-300 text-caption"
            )

        trend_chart = ui.echart(build_temperature_chart_options()).classes(
            "trend-chart w-full"
        )


def show_plc_stats(device_id: str) -> None:
    """弹出指定 PLC 的统计分析窗口。"""
    stats = [
        {"label": "历史最高温度", "value": "98.6 °C", "icon": "device_thermostat"},
        {"label": "平均运行压力", "value": "3.24 MPa", "icon": "speed"},
        {"label": "今日故障次数", "value": "2 次", "icon": "warning"},
        {"label": "连续运行时间", "value": "128 小时", "icon": "schedule"},
    ]

    with ui.dialog() as dialog, ui.card().classes(
        "shadow-8 rounded-borders q-pa-md text-slate-900 dark:text-slate-100"
    ):
        with ui.row().classes("w-full items-center q-mb-md"):
            ui.icon("analytics").classes("text-blue-4 text-h5 q-mr-sm")
            ui.label(f"{device_id} 数据统计分析").classes("text-h6 text-weight-bold")

        ui.separator().classes("bg-gray-200 dark:bg-grey-8 q-mb-md")

        with ui.grid(columns=2).classes("w-full gap-4"):
            for item in stats:
                with ui.card().classes("q-pa-md text-slate-900 dark:text-slate-100"):
                    with ui.row().classes("items-center no-wrap"):
                        ui.icon(item["icon"]).classes("text-blue-4 text-h5 q-mr-sm")
                        with ui.column().classes("q-gutter-xs"):
                            ui.label(item["label"]).classes(
                                "text-slate-600 dark:text-slate-300 text-caption"
                            )
                            ui.label(item["value"]).classes(
                                "text-h5 text-weight-bold telemetry-value"
                            )

        with ui.row().classes("w-full justify-end q-mt-md"):
            ui.button("关闭", color="red", on_click=dialog.close).props("unelevated")

    dialog.open()


def create_device_card(device_id: str) -> None:
    """创建 ThingsBoard 风格的 PLC 监控卡片。"""
    with ui.card().classes(
        "shadow-8 rounded-borders q-pa-sm w-72 tb-card cursor-pointer text-slate-900 dark:text-slate-100"
    ).on("click", lambda _event, plc_id=device_id: show_plc_stats(plc_id)):
        with ui.row().classes("w-full items-center justify-between q-mb-sm"):
            with ui.row().classes("items-center no-wrap"):
                ui.icon("memory").classes("text-blue-4 text-h5 q-mr-sm")
                ui.label(device_id).classes("text-subtitle1 text-weight-bold")

            with ui.row().classes("items-center no-wrap"):
                status_label = ui.label("已停止").classes(
                    "text-slate-700 dark:text-slate-200 text-caption q-mr-xs"
                )
                status_dot = ui.element("div").classes("status-dot bg-grey-6")

        ui.separator().classes("bg-gray-200 dark:bg-grey-8 q-mb-sm")

        with ui.column().classes("w-full q-gutter-sm"):
            with ui.row().classes("w-full items-end justify-between"):
                ui.label("温度").classes(
                    "text-slate-600 dark:text-slate-300 text-caption"
                )
                with ui.row().classes("items-end no-wrap"):
                    temperature_value = ui.label("--.--").classes(
                        "text-h4 text-weight-bold telemetry-value"
                    )
                    ui.label("°C").classes(
                        "text-slate-600 dark:text-slate-300 text-caption q-ml-xs q-mb-xs"
                    )

            with ui.row().classes("w-full items-end justify-between"):
                ui.label("压力").classes(
                    "text-slate-600 dark:text-slate-300 text-caption"
                )
                with ui.row().classes("items-end no-wrap"):
                    pressure_value = ui.label("--.--").classes(
                        "text-h4 text-weight-bold telemetry-value"
                    )
                    ui.label("MPa").classes(
                        "text-slate-600 dark:text-slate-300 text-caption q-ml-xs q-mb-xs"
                    )

    device_cards[device_id] = {
        "status_label": status_label,
        "status_dot": status_dot,
        "temperature_value": temperature_value,
        "pressure_value": pressure_value,
    }


def build_device_monitor_grid() -> None:
    """构建三个 PLC 监控卡片网格。"""
    with ui.card().classes(
        "w-full shadow-4 rounded-borders q-pa-md text-slate-900 dark:text-slate-100"
    ):
        with ui.row().classes("w-full items-center q-mb-md"):
            ui.icon("memory").classes("text-blue-4 text-h5 q-mr-sm")
            ui.label("PLC 设备监控").classes("text-subtitle1 text-weight-bold")

        with ui.row().classes("w-full q-gutter-md items-start"):
            for device_id in DEVICE_IDS:
                create_device_card(device_id)


def build_realtime_panel() -> None:
    """构建实时监控面板。"""
    with ui.column().classes("w-full q-gutter-md"):
        build_chart_panel()
        build_device_monitor_grid()


def build_placeholder_panel(title: str, icon: str) -> None:
    """构建暂未开发的占位面板。"""
    with ui.card().classes(
        "w-full shadow-6 rounded-borders q-pa-xl text-slate-900 dark:text-slate-100"
    ):
        with ui.column().classes("items-center q-gutter-md"):
            ui.icon(icon).classes("text-blue-4 text-h3")
            ui.label(title).classes("text-h6 text-weight-bold")
            ui.label("功能模块待扩展").classes("text-slate-600 dark:text-slate-300")


def update_data_interval(interval: int | float) -> None:
    """动态调整图表和卡片数据刷新间隔。"""
    if data_timer is not None:
        data_timer.interval = float(interval)


def build_settings_panel() -> None:
    """构建系统设置面板。"""
    interval_options = {
        1: "1秒",
        2: "2秒",
        5: "5秒",
        10: "10秒",
    }

    with ui.column().classes("w-full q-gutter-md"):
        with ui.card().classes(
            "w-full shadow-6 rounded-borders q-pa-md text-slate-900 dark:text-slate-100"
        ):
            with ui.row().classes("w-full items-center q-mb-md"):
                ui.icon("settings").classes("text-blue-4 text-h5 q-mr-sm")
                ui.label("系统设置").classes("text-h6 text-weight-bold")

            ui.separator().classes("bg-gray-200 dark:bg-grey-8 q-mb-md")

            with ui.row().classes("w-full items-center justify-between q-py-sm"):
                with ui.column().classes("q-gutter-xs"):
                    ui.label("界面主题").classes("text-subtitle2 text-weight-bold")
                    ui.label("切换平台深浅色显示模式").classes(
                        "text-slate-600 dark:text-slate-300 text-caption"
                    )
                ui.switch(
                    "深色模式",
                    value=True,
                ).bind_value(
                    theme, "value"
                ).classes("text-slate-900 dark:text-slate-100")

            with ui.row().classes("w-full items-center justify-between q-py-sm"):
                with ui.column().classes("q-gutter-xs"):
                    ui.label("数据刷新频率").classes("text-subtitle2 text-weight-bold")
                    ui.label("控制实时图表和 PLC 卡片的数据请求时间间隔").classes(
                        "text-slate-600 dark:text-slate-300 text-caption"
                    )
                ui.select(
                    interval_options,
                    value=2,
                    label="数据请求时间间隔",
                    on_change=lambda event: update_data_interval(event.value),
                ).props("outlined dense").classes(
                    "w-48 text-slate-900 dark:text-slate-100"
                )


def build_main_content() -> None:
    """构建主内容区，使用 tabs/panels 管理页面切换。"""
    global main_panels

    with ui.column().classes(
        "admin-main w-full q-pa-md text-slate-900 dark:text-slate-100"
    ):
        with ui.tabs().classes("hidden-tabs") as tabs:
            ui.tab(PANEL_OVERVIEW, label="数据总览")
            ui.tab(PANEL_REALTIME, label="实时监控")
            ui.tab(PANEL_ALARM, label="报警中心")
            ui.tab(PANEL_SETTINGS, label="系统设置")

        with ui.tab_panels(tabs, value=PANEL_REALTIME).classes(
            "w-full bg-transparent"
        ) as panels:
            main_panels = panels
            with ui.tab_panel(PANEL_OVERVIEW).classes("q-pa-none"):
                build_overview_panel()
            with ui.tab_panel(PANEL_REALTIME).classes("q-pa-none"):
                build_realtime_panel()
            with ui.tab_panel(PANEL_ALARM).classes("q-pa-none"):
                build_placeholder_panel("报警中心", "warning")
            with ui.tab_panel(PANEL_SETTINGS).classes("q-pa-none"):
                build_settings_panel()


def build_page() -> None:
    """构建标准工业后台管理系统布局。"""
    build_header()
    build_left_drawer()
    build_main_content()


def update_device_card(device: dict[str, Any]) -> None:
    """更新单个 PLC 卡片的遥测数值和状态指示灯。"""
    device_id = str(device.get("device_id", ""))
    widgets = device_cards.get(device_id)
    if widgets is None:
        return

    status = str(device.get("status", "stopped")).lower()
    status_config = STATUS_CONFIG.get(status, STATUS_CONFIG["stopped"])

    widgets["status_label"].set_text(status_config["text"])
    widgets["status_label"].classes(
        remove=STATUS_TEXT_CLASSES, add=status_config["text_class"]
    )
    widgets["status_dot"].classes(remove=STATUS_CLASSES, add=status_config["dot_class"])
    widgets["temperature_value"].set_text(f"{float(device['temperature']):.2f}")
    widgets["pressure_value"].set_text(f"{float(device['pressure']):.2f}")


def update_temperature_chart(devices: list[dict[str, Any]]) -> None:
    """将最新平均温度写入趋势图，仅保留最近 20 个点。"""
    if trend_chart is None:
        return

    temperatures = [
        float(device["temperature"]) for device in devices if "temperature" in device
    ]
    if not temperatures:
        return

    time_labels.append(datetime.now().strftime("%H:%M:%S"))
    temperature_history.append(round(sum(temperatures) / len(temperatures), 2))

    if len(time_labels) > MAX_HISTORY_POINTS:
        time_labels.pop(0)
        temperature_history.pop(0)

    trend_chart.options["xAxis"]["data"] = time_labels
    trend_chart.options["series"][0]["data"] = temperature_history
    trend_chart.update()


async def refresh_dashboard() -> None:
    """定时获取 PLC 假数据，同时刷新趋势图和设备卡片。"""
    try:
        devices = await asyncio.to_thread(fetch_latest_data)
    except (URLError, TimeoutError, OSError) as exc:
        last_update_label.set_text(f"后端服务不可用：{exc}")
        return

    if not isinstance(devices, list) or not devices:
        last_update_label.set_text("未收到遥测数据")
        return

    plc_devices = devices[:3]
    update_temperature_chart(plc_devices)

    for device in plc_devices:
        update_device_card(device)

    last_update_label.set_text(f"遥测数据已更新：{datetime.now():%H:%M:%S}")


build_page()
data_timer = ui.timer(2.0, refresh_dashboard)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        show=False,
        title=PLATFORM_NAME,
        host="0.0.0.0",
        port=8080,
        favicon="🏭",
    )
