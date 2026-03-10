import dash
from dash import html, dcc, Input, Output, callback
import feffery_antd_components as fac
from static.routes import routes

layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        # 左侧菜单栏
        html.Div(
            [
                fac.AntdCenter(
                    [
                        fac.AntdSpace(
                            [
                                fac.AntdImage(
                                    src="../assets/images/logo.png",
                                    style={
                                        "width": 35,
                                        "borderRadius": 8,
                                    },
                                    preview=False,
                                ),
                                html.Span(
                                    "工业监控中枢",
                                    style={
                                        "color": "#ffffff",
                                        "fontSize": "18px",
                                        "fontWeight": "bold",
                                        "letterSpacing": "2px"
                                    }
                                )
                            ],
                            align="center",
                            size="middle"
                        )
                    ],
                    style={"height": "60px", "marginTop": "10px", "marginBottom": "10px"},
                ),
                fac.AntdMenu(
                    id="layout-menu",
                    menuItems=routes,
                    mode="inline",
                    theme="dark",
                    style={"width": 240},
                ),
            ],
            style={
                "backgroundColor": "#011528",
                "height": "100vh",
                "width": "240px",
                "overflowY": "auto",
                "overflowX": "hidden",
                # 隐藏滚动条
                "scrollbarWidth": "none",
            },
        ),
        # 右侧内容
        html.Div(
            [
                # nav
                html.Div(
                    [
                        html.Span(
                            [],
                            id="layout-rightContent-nav-path",
                            style={
                                "marginLeft": 20,
                                "fontSize": 14,
                                "color": "#6c6c6c",
                            },
                        ),
                        html.Div(
                            [
                                # 1. 工业系统运行状态标签
                                fac.AntdTag(
                                    content="系统状态: 正常运行",
                                    color="success",
                                    style={"fontSize": "14px", "padding": "4px 8px"}
                                ),

                                # 2. 设备报警铃铛（带小红点）
                                fac.AntdBadge(
                                    fac.AntdButton(
                                        icon=fac.AntdIcon(icon='antd-bell', style={"fontSize": "20px"}),
                                        type='text',
                                    ),
                                    count=3,
                                ),

                                # 3. 保留原有的下载和全屏按钮
                                fac.AntdButton(
                                    icon=fac.AntdIcon(icon='antd-download', style={"fontSize": "20px"}),
                                    type='text',
                                    id="layout-rightContent-nav-download",
                                ),
                                fac.AntdButton(
                                    icon=fac.AntdIcon(icon='antd-full-screen', style={"fontSize": "20px"}),
                                    type='text',
                                    id="layout-rightContent-nav-fullScreen",
                                ),

                                # 4. 保留原有的头像下拉菜单
                                fac.AntdDropdown(
                                    fac.AntdAvatar(
                                        icon="antd-user",
                                        size="large",
                                        style={
                                            "marginRight": 50,
                                            "width": 32,
                                            "height": 32,
                                            "background": "#1f63fb",
                                            "cursor": "pointer"
                                        },
                                    ),
                                    menuItems=[
                                        {
                                            "title": fac.AntdSpace(
                                                [
                                                    fac.AntdAvatar(
                                                        icon="antd-user",
                                                        style={
                                                            "background": "#f7f8f9",
                                                            "color": "#9ea5b5",
                                                            "width": 20,
                                                            "height": 20,
                                                        },
                                                    ),
                                                    fac.AntdText(
                                                        [],
                                                        id="layout-rightContent-nav-dropdown-accountrole"
                                                    ),
                                                ]
                                            ),
                                            "key": "user"
                                        },
                                        {
                                            "title": fac.AntdSpace(
                                                [
                                                    fac.AntdAvatar(
                                                        icon="antd-power-off",
                                                        style={
                                                            "background": "#f7f8f9",
                                                            "color": "#9ea5b5",
                                                            "width": 24,
                                                            "height": 24,
                                                        },
                                                    ),
                                                    "logout",
                                                ]
                                            ),
                                            "key": "logout"
                                        }
                                    ],
                                    trigger="hover",
                                    placement="bottomRight",
                                    id='layout-rightContent-nav-dropdown',
                                ),
                            ],
                            id="layout-rightContent-nav-div",
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "gap": 15,
                            }
                        ),
                    ],
                    # 这里是刚才被不小心删掉的 nav 外层容器的收尾配置
                    id="layout-rightContent-nav",
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "width": "100%",
                        "height": "50px",
                        "backgroundColor": "#ffffff",
                        "lineHeight": "50px",
                    },
                ),

                # 下面是正常的数据看板内容区域
                html.Div(
                    [],
                    id="layout-rightContent-content",
                    style={
                        "margin": "10px 10px",
                        "height": "calc(100% - 70px)",
                        "overflowY": "auto",
                        "overflowX": "hidden",
                        "backgroundColor": "#f7f9fa",
                    },
                ),
            ],
            id="layout-rightContent",
            style={
                "width": "calc(100vw - 240px)",
                "height": "100%",
            },
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        "flexWrap": "nowrap",
        "width": "100vw",
        "height": "100vh",
        "backgroundColor": "#f7f9fa",
        "overflowY": "hidden",
        "margin": 0,
        "padding": 0,
    },
)
