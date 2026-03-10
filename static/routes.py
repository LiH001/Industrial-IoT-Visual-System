routes = [
    {
        "component": "SubMenu",
        "props": {"key": "home", "title": "车间运行大屏"},
    },
    {
        "component": "SubMenu",
        "props": {"key": "actionAnalysis", "title": "设备实时监控"},
        "children": [
            {
                "component": "ItemGroup",
                "props": {"key": "userData", "title": "设备台账总览"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "tagAnalysis", "title": "设备状态标定"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "eventAnalysis", "title": "异常报警事件"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "funnelAnalysis", "title": "生产工序流转"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "retentionAnalysis", "title": "设备无故障率(留存)"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "distributionAnalysis", "title": "运行负荷分布"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "LTVAnalysis", "title": "设备综合效率(OEE)"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "sessionAnalysis", "title": "加工周期分析"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "userpathAnalysis", "title": "物料流转路径"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "customAnalysis", "title": "多维传感器查询"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "intervalAnalysis", "title": "维护间隔分析"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "attributionAnalysis", "title": "故障归因分析"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "heatAnalysis", "title": "车间温度热力图"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "clickAnalysis", "title": "操作指令记录"},
            }
        ],
    },
    {
        "component": "SubMenu",
        "props": {"key": "userAnalysis", "title": "预测性维护(AI)"},
        "children": [
            {
                "component": "ItemGroup",
                "props": {"key": "userPortraitAnalysis", "title": "设备健康画像"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "userPortraitReport", "title": "AI健康诊断报告"}, #
            },
            {
                "component": "ItemGroup",
                "props": {"key": "attributeAnalysis", "title": "振动/温度特征"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "userScan", "title": "单机深度细查"},
            },
        ],
    },
    {
        "component": "SubMenu",
        "props": {"key": "operationsAnalysis", "title": "生产调度与能耗"},
        "children": [
            {
                "component": "ItemGroup",
                "props": {"key": "dynamicsalesAnalysis", "title": "产能动态分析"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "searchAnalysis", "title": "历史工单检索"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "functionAnalysis", "title": "能耗趋势监测"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "vipAnalysis", "title": "核心重点设备"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "categoryAnalysis", "title": "备品备件库存"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "groupbuyAnalysis", "title": "班组效能对比"},
            },
        ],
    },
    {
        "component": "SubMenu",
        "props": {"key": "adsAnalysis", "title": "质量与合规管理"},
        "children": [
            {
                "component": "ItemGroup",
                "props": {"key": "adsOverview", "title": "良品率概览"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "launchAnalysis", "title": "原料批次分析"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "promotionAnalysis", "title": "工艺改进追踪"},
            }
        ],
    },
    {
        "component": "SubMenu",
        "props": {"key": "sysManage", "title": "系统配置与运维"},
        "children": [
            {
                "component": "ItemGroup",
                "props": {"key": "userManage", "title": "操作权限管理"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "tagManage", "title": "传感器节点管理"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "eventManage", "title": "报警规则阈值"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "cronManage", "title": "定时巡检任务"},
            },
            {
                "component": "ItemGroup",
                "props": {"key": "simulateAction", "title": "传感器数据模拟"},
            },
        ],
    },
]
