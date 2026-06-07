"""
yingqi.py — 应期（时间预判）计算模块
=========================================
根据体用关系、卦数、五行旺衰推算应期（事态应验的时间窗口）。

应期理论依据：
  - 体旺时：应期近，取生体之卦数或体卦本数为时间单位
  - 体衰时：应期远，取帮扶体卦的五行当令之时
  - 卦数对应：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8
"""

from datetime import datetime, timedelta

from .data_tables import (
    XIANTIAN_REVERSE,
    TRIGRAM_INFO,
    WUXING_SHENG, WUXING_SHENG_BY,
    SEASON_WUXING, LUNAR_MONTH_SEASON, EARTH_MONTHS,
    get_season_strength, get_wuxing_relation,
    DIZHI, DIZHI_WUXING,
)


def calculate_yingqi(hexagram_result: dict) -> dict:
    """
    根据完整的卦象结果计算应期。

    Args:
        hexagram_result: meihua_time_divination() 等函数的输出

    Returns:
        dict: {
            "summary": str,           # 一句话结论
            "ti_strength": str,        # 体卦旺衰状态
            "urgency": str,            # 紧迫程度 (urgent/moderate/relaxed)
            "number_hints": list,      # 卦数提示的时间数字
            "wuxing_timing": dict,     # 五行应期（等到某五行当令）
            "dizhi_days": list,        # 有利的地支日
            "practical_window": str,   # 实用时间窗口建议
            "reasoning": str,          # 推理过程说明
        }
    """
    ti = hexagram_result["体用"]["体卦"]
    yong = hexagram_result["体用"]["用卦"]
    ti_yong_rel = hexagram_result["体用"]["体用关系"]

    ti_name = ti["trigram"]
    ti_wx = ti["wuxing"]
    yong_name = yong["trigram"]
    yong_wx = yong["wuxing"]

    ti_num = XIANTIAN_REVERSE[ti_name]
    yong_num = XIANTIAN_REVERSE[yong_name]

    # 旺衰
    season_info = hexagram_result.get("旺衰")
    ti_strength = season_info["体卦旺衰"] if season_info else "未知"
    lunar_month = season_info["lunar_month"] if season_info else None

    # 变卦信息
    changed = hexagram_result["变卦"]
    changed_upper_wx = TRIGRAM_INFO[changed["upper"]["name"]]["wuxing"]
    changed_lower_wx = TRIGRAM_INFO[changed["lower"]["name"]]["wuxing"]

    reasoning_parts = []
    number_hints = []
    dizhi_days = []

    # ============================================================
    # 一、基于体卦旺衰判断应期远近
    # ============================================================

    if ti_strength in ("旺", "相"):
        urgency = "urgent"
        reasoning_parts.append(
            f"体卦{ti_name}（{ti_wx}）当前处于「{ti_strength}」态，气势充足，应期较近。"
        )

        # 体旺时：取生体之卦数
        sheng_ti_wx = WUXING_SHENG_BY.get(ti_wx)  # 什么五行生体
        if sheng_ti_wx:
            # 找到生体五行对应的卦
            for gua_name, info in TRIGRAM_INFO.items():
                if info["wuxing"] == sheng_ti_wx:
                    num = XIANTIAN_REVERSE[gua_name]
                    if num not in number_hints:
                        number_hints.append(num)

        # 也取体卦本数
        if ti_num not in number_hints:
            number_hints.append(ti_num)

        reasoning_parts.append(
            f"生体之五行为{sheng_ti_wx}，对应卦数"
            f"{number_hints}，体卦本数{ti_num}。"
            f"应期参考数字：{sorted(set(number_hints))}（可对应小时或天数）。"
        )

    elif ti_strength == "休":
        urgency = "moderate"
        reasoning_parts.append(
            f"体卦{ti_name}（{ti_wx}）当前处于「休」态，力量一般，应期适中。"
        )
        number_hints.append(ti_num)
        number_hints.append(yong_num)

    else:  # 囚 or 死
        urgency = "relaxed"
        reasoning_parts.append(
            f"体卦{ti_name}（{ti_wx}）当前处于「{ti_strength}」态，力量不足，"
            "应期可能较远，需等到有利时机或加大行动力度。"
        )
        number_hints.append(ti_num)

    # ============================================================
    # 二、五行应期（等到某五行当令）
    # ============================================================

    wuxing_timing = {}

    # 生体的五行当令之时
    sheng_ti = WUXING_SHENG_BY.get(ti_wx)
    if sheng_ti:
        wuxing_timing["生体当令"] = _find_wuxing_season(sheng_ti, lunar_month)

    # 同体的五行当令之时
    wuxing_timing["同体当令"] = _find_wuxing_season(ti_wx, lunar_month)

    # 体克用的五行当令
    if ti_yong_rel in ("被生", "比和", "克"):
        pass  # 已经有利
    else:
        # 体需要帮扶
        wuxing_timing["帮扶时机"] = _find_wuxing_season(
            sheng_ti if sheng_ti else ti_wx, lunar_month
        )

    reasoning_parts.append(
        f"五行应期：生体（{sheng_ti}）当令约在"
        f"{wuxing_timing.get('生体当令', {}).get('description', '未知')}；"
        f"同体（{ti_wx}）当令约在"
        f"{wuxing_timing.get('同体当令', {}).get('description', '未知')}。"
    )

    # ============================================================
    # 三、有利地支日
    # ============================================================

    # 生体或与体同五行的地支日
    for dz, wx in DIZHI_WUXING.items():
        rel = get_wuxing_relation(wx, ti_wx)
        if rel in ("生", "比和"):
            dizhi_days.append({"dizhi": dz, "wuxing": wx, "relation": rel})

    reasoning_parts.append(
        f"有利的地支日（生体或同体）："
        f"{'、'.join(d['dizhi'] + '日(' + d['wuxing'] + ')' for d in dizhi_days)}。"
    )

    # ============================================================
    # 四、变卦对应期的修正
    # ============================================================

    changed_rel_upper = get_wuxing_relation(changed_upper_wx, ti_wx)
    changed_rel_lower = get_wuxing_relation(changed_lower_wx, ti_wx)

    if changed_rel_upper in ("生", "比和") and changed_rel_lower in ("生", "比和"):
        reasoning_parts.append(
            "变卦上下皆与体卦比和或生体，事态向有利方向发展，应期可能提前。"
        )
        if urgency == "relaxed":
            urgency = "moderate"
    elif changed_rel_upper == "克" or changed_rel_lower == "克":
        reasoning_parts.append(
            "变卦中有克体之象，暗示越拖越不利，建议尽快行动。"
        )
        urgency = "urgent"

    # ============================================================
    # 五、综合实用建议
    # ============================================================

    if urgency == "urgent":
        practical_window = (
            f"参考时间窗口约{min(number_hints)}天，宜尽快把握时机。"
            "卦象显示窗口期较短，越早行动越好。"
        )
    elif urgency == "moderate":
        avg_num = sum(number_hints) // len(number_hints) if number_hints else 5
        practical_window = (
            f"参考时间窗口约{avg_num}天，宜在此期间推进。"
            "不算特别紧迫，但也不宜拖延过久。"
        )
    else:
        sheng_desc = wuxing_timing.get("生体当令", {}).get("description", "下一个有利时段")
        practical_window = (
            f"体卦力量不足，短期内推进效率可能不高。"
            f"一方面建议现在就着手行动（不要等），另一方面关注{sheng_desc}前后，"
            "可能是更有利的时间窗口。"
        )

    # 综合摘要
    if urgency == "urgent":
        summary = f"应期较近（体{ti_strength}），参考窗口约{min(number_hints)}天"
    elif urgency == "moderate":
        summary = f"应期适中（体{ti_strength}），宜近期内把握时机"
    else:
        summary = f"应期偏远（体{ti_strength}），但仍建议尽快行动，不宜等待"

    return {
        "summary": summary,
        "ti_strength": ti_strength,
        "urgency": urgency,
        "number_hints": sorted(set(number_hints)),
        "wuxing_timing": wuxing_timing,
        "dizhi_days": dizhi_days,
        "practical_window": practical_window,
        "reasoning": "\n".join(reasoning_parts),
    }


def _find_wuxing_season(wuxing: str, current_lunar_month: int = None) -> dict:
    """
    找到某五行当令（旺）的最近季节/月份。

    Returns:
        dict: {
            "season": str,
            "months": list[int],  # 农历月份
            "description": str,   # 中文描述
            "is_current": bool,   # 是否就是当前季节
        }
    """
    # 五行对应旺季
    wuxing_to_season = {
        "木": ("春", [1, 2, 3]),
        "火": ("夏", [4, 5, 6]),
        "金": ("秋", [7, 8, 9]),
        "水": ("冬", [10, 11, 12]),
        "土": ("四季末月", [3, 6, 9, 12]),
    }

    season_name, months = wuxing_to_season.get(wuxing, ("未知", []))

    month_names = {
        1: "正月", 2: "二月", 3: "三月", 4: "四月",
        5: "五月", 6: "六月", 7: "七月", 8: "八月",
        9: "九月", 10: "十月", 11: "冬月", 12: "腊月",
    }

    is_current = current_lunar_month in months if current_lunar_month else False

    if is_current:
        description = f"当前（{season_name}，{wuxing}旺）即是有利时段"
    elif current_lunar_month and months:
        # 找到下一个有利月份
        future_months = [m for m in months if m > current_lunar_month]
        if not future_months:
            # 跨年，取下一轮的第一个月
            next_month = months[0]
            description = f"明年{month_names.get(next_month, str(next_month))}（{season_name}，{wuxing}旺）"
        else:
            next_month = future_months[0]
            description = f"{month_names.get(next_month, str(next_month))}（{season_name}，{wuxing}旺）"
    else:
        description = f"{season_name}时节（{wuxing}旺）"

    return {
        "season": season_name,
        "months": months,
        "description": description,
        "is_current": is_current,
    }


def format_yingqi_text(yingqi: dict) -> str:
    """格式化应期分析为可读文本"""
    lines = []
    lines.append(f"## 应期分析")
    lines.append(f"")
    lines.append(f"**结论：** {yingqi['summary']}")
    lines.append(f"")
    lines.append(f"**实用建议：** {yingqi['practical_window']}")
    lines.append(f"")
    lines.append(f"**参考数字：** {yingqi['number_hints']}（可对应小时数或天数）")
    lines.append(f"")

    if yingqi["dizhi_days"]:
        days_str = "、".join(
            f"{d['dizhi']}日({d['wuxing']})"
            for d in yingqi["dizhi_days"]
        )
        lines.append(f"**有利地支日：** {days_str}")
        lines.append(f"")

    lines.append(f"### 推理过程")
    lines.append(f"")
    lines.append(yingqi["reasoning"])

    return "\n".join(lines)
