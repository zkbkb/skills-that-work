"""
liuyao.py — 六爻纳甲排盘引擎
====================================
整合五大模块：
  A. 纳甲装卦（天干地支分配）
  B. 六亲推算
  C. 六神分配
  D. 月建日辰旺衰分析
  E. 世应关系

输出完整的六爻排盘数据，供解读使用。
"""

from .data_tables import (
    TRIGRAM_INFO, TRIGRAM_LINES, LINES_TO_TRIGRAM,
    HEXAGRAM_TABLE, DIZHI_WUXING,
    WUXING_SHENG, WUXING_KE, get_wuxing_relation,
)
from .liuyao_data import (
    NAJIA_RULES, BAGONG_TABLE, HEXAGRAM_GONG_INDEX, GONG_WUXING,
    SHIYAO_MAP, LIUQIN_RULES, LIUQIN_MEANING,
    LIUSHEN_BY_DAYGAN, LIUSHEN_MEANING,
    DIZHI_CHONG, DIZHI_HE,
    get_monthly_strength, check_yuepo, check_ri_chong, check_ri_he,
)
from .calendar_utils import get_liuyao_time_params, get_day_ganzhi, get_month_dizhi


# ============================================================
# 核心排盘函数
# ============================================================

def liuyao_paipan(
    hexagram_name: str,
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    moving_lines: list = None,
) -> dict:
    """
    六爻纳甲完整排盘。

    Args:
        hexagram_name: 卦名（如 "火地晋"）
        year, month, day, hour, minute: 起卦时间（公历）
        moving_lines: 动爻位列表（如 [6] 表示上爻动）

    Returns:
        dict: 完整排盘数据
    """
    if moving_lines is None:
        moving_lines = []

    # ---- 1. 查找宫位信息 ----
    gong_info = HEXAGRAM_GONG_INDEX.get(hexagram_name)
    if gong_info is None:
        raise ValueError(f"未找到卦名: {hexagram_name}")

    gong_name = gong_info["gong"]
    upper_name = gong_info["upper"]
    lower_name = gong_info["lower"]
    shi_num = gong_info["shi_num"]
    gong_type = gong_info["type"]
    gong_wx = GONG_WUXING[gong_name]

    # ---- 2. 纳甲装卦 ----
    inner_najia = NAJIA_RULES[lower_name]["inner"]  # [(天干,地支), ...]
    outer_najia = NAJIA_RULES[upper_name]["outer"]

    lines = []
    for i in range(6):
        pos = i + 1
        if i < 3:
            tg, dz = inner_najia[i]
        else:
            tg, dz = outer_najia[i - 3]

        yao_wx = DIZHI_WUXING[dz]
        yao_yinyang = "阳" if TRIGRAM_LINES[lower_name if i < 3 else upper_name][i % 3] == 1 else "阴"

        lines.append({
            "position": pos,
            "tiangan": tg,
            "dizhi": dz,
            "wuxing": yao_wx,
            "yinyang": yao_yinyang,
            "is_moving": pos in moving_lines,
        })

    # ---- 3. 六亲推算 ----
    for line in lines:
        line["liuqin"] = _calc_liuqin(gong_wx, line["wuxing"])

    # ---- 4. 世应爻位 ----
    shi_pos, ying_pos = SHIYAO_MAP[shi_num]
    for line in lines:
        line["is_shi"] = line["position"] == shi_pos
        line["is_ying"] = line["position"] == ying_pos

    # ---- 5. 时间参数和六神 ----
    time_params = get_liuyao_time_params(year, month, day, hour, minute)
    day_gz = time_params["day_ganzhi"]
    month_dz = time_params["month_dizhi"]
    day_gan = day_gz["tiangan"]
    day_zhi = day_gz["dizhi"]

    liushen_list = LIUSHEN_BY_DAYGAN.get(day_gan, ["?"] * 6)
    for i, line in enumerate(lines):
        line["liushen"] = liushen_list[i]

    # ---- 6. 月建日辰旺衰 ----
    for line in lines:
        line["month_strength"] = get_monthly_strength(line["wuxing"], month_dz)
        line["yuepo"] = check_yuepo(line["dizhi"], month_dz)
        line["ri_chong"] = check_ri_chong(line["dizhi"], day_zhi)
        ri_he, he_wx = check_ri_he(line["dizhi"], day_zhi)
        line["ri_he"] = ri_he
        line["ri_he_wuxing"] = he_wx

    # ---- 7. 变卦处理 ----
    changed_lines = None
    if moving_lines:
        lower_lines = TRIGRAM_LINES[lower_name][:]
        upper_lines = TRIGRAM_LINES[upper_name][:]
        all_lines = lower_lines + upper_lines

        for pos in moving_lines:
            idx = pos - 1
            all_lines[idx] = 1 - all_lines[idx]

        changed_lower_name = LINES_TO_TRIGRAM[tuple(all_lines[:3])]
        changed_upper_name = LINES_TO_TRIGRAM[tuple(all_lines[3:])]
        changed_hex_key = (changed_upper_name, changed_lower_name)
        changed_hex_info = HEXAGRAM_TABLE.get(changed_hex_key, {"name": "未知"})

        # 变卦纳甲
        changed_inner = NAJIA_RULES[changed_lower_name]["inner"]
        changed_outer = NAJIA_RULES[changed_upper_name]["outer"]

        changed_lines = []
        for i in range(6):
            pos = i + 1
            if pos not in moving_lines:
                changed_lines.append(None)  # 不动的爻无变
                continue
            if i < 3:
                tg, dz = changed_inner[i]
            else:
                tg, dz = changed_outer[i - 3]

            ch_wx = DIZHI_WUXING[dz]
            changed_lines.append({
                "position": pos,
                "tiangan": tg,
                "dizhi": dz,
                "wuxing": ch_wx,
                "liuqin": _calc_liuqin(gong_wx, ch_wx),
            })

    # ---- 8. 伏神处理 ----
    # 如果卦中缺少某个六亲（尤其是妻财），需要找伏神
    present_liuqin = set(l["liuqin"] for l in lines)
    fushen = {}
    if "妻财" not in present_liuqin:
        fushen["妻财"] = _find_fushen(gong_name, "妻财", lines)
    if "官鬼" not in present_liuqin:
        fushen["官鬼"] = _find_fushen(gong_name, "官鬼", lines)

    # ---- 9. 用神确定 ----
    yongshen = _find_yongshen(lines, fushen)

    # ---- 组装结果 ----
    return {
        "hexagram_name": hexagram_name,
        "gong": gong_name,
        "gong_wuxing": gong_wx,
        "gong_type": gong_type,
        "shi_yao": shi_pos,
        "ying_yao": ying_pos,

        "time_params": {
            "day_ganzhi": day_gz["ganzhi"],
            "day_gan": day_gan,
            "day_zhi": day_zhi,
            "month_dizhi": month_dz,
        },

        "lines": lines,
        "changed_lines": changed_lines,
        "fushen": fushen,
        "yongshen": yongshen,
    }


# ============================================================
# 辅助函数
# ============================================================

def _calc_liuqin(gong_wx: str, yao_wx: str) -> str:
    """根据宫五行和爻五行计算六亲"""
    if gong_wx == yao_wx:
        return "兄弟"
    # 生我者为父母
    if WUXING_SHENG.get(yao_wx) == gong_wx:
        return "父母"
    # 我生者为子孙
    if WUXING_SHENG.get(gong_wx) == yao_wx:
        return "子孙"
    # 克我者为官鬼
    if WUXING_KE.get(yao_wx) == gong_wx:
        return "官鬼"
    # 我克者为妻财
    if WUXING_KE.get(gong_wx) == yao_wx:
        return "妻财"
    return "未知"


def _find_fushen(gong_name: str, target_liuqin: str, current_lines: list) -> dict | None:
    """
    在本宫卦中寻找伏神。
    伏神是本宫纯卦中具有目标六亲的爻，藏在当前卦的对应爻位之下。
    """
    gong_wx = GONG_WUXING[gong_name]

    # 取本宫纯卦的纳甲
    pure_inner = NAJIA_RULES[gong_name]["inner"]
    pure_outer = NAJIA_RULES[gong_name]["outer"]

    for i in range(6):
        if i < 3:
            tg, dz = pure_inner[i]
        else:
            tg, dz = pure_outer[i - 3]

        wx = DIZHI_WUXING[dz]
        lq = _calc_liuqin(gong_wx, wx)

        if lq == target_liuqin:
            # 找到了伏神
            host_line = current_lines[i]  # 飞神（覆盖在上面的爻）
            return {
                "position": i + 1,
                "tiangan": tg,
                "dizhi": dz,
                "wuxing": wx,
                "liuqin": lq,
                "host_liuqin": host_line["liuqin"],
                "host_dizhi": host_line["dizhi"],
            }

    return None


def _find_yongshen(lines: list, fushen: dict) -> dict:
    """
    确定用神。默认取妻财爻（通用占问中可根据场景调整）。
    若卦中有妻财，取之；若无，取伏神中的妻财。
    """
    # 先在卦中找妻财
    caiyao_list = [l for l in lines if l["liuqin"] == "妻财"]

    if caiyao_list:
        # 取世爻最近的/动爻/旺相的妻财
        # 简化：取第一个妻财
        yongshen = caiyao_list[0]
        return {
            "type": "卦中",
            "position": yongshen["position"],
            "dizhi": yongshen["dizhi"],
            "wuxing": yongshen["wuxing"],
            "is_moving": yongshen["is_moving"],
            "month_strength": yongshen["month_strength"],
            "description": f"妻财{yongshen['tiangan']}{yongshen['dizhi']}{yongshen['wuxing']}在第{yongshen['position']}爻",
        }
    elif "妻财" in fushen and fushen["妻财"]:
        fs = fushen["妻财"]
        return {
            "type": "伏神",
            "position": fs["position"],
            "dizhi": fs["dizhi"],
            "wuxing": fs["wuxing"],
            "is_moving": False,
            "month_strength": None,
            "host_liuqin": fs["host_liuqin"],
            "description": f"妻财{fs['tiangan']}{fs['dizhi']}{fs['wuxing']}伏于第{fs['position']}爻{fs['host_liuqin']}之下",
        }
    else:
        return {
            "type": "缺失",
            "description": "卦中无妻财爻，伏神亦未找到——情况特殊，需综合分析",
        }


# ============================================================
# 格式化输出
# ============================================================

def format_liuyao_text(result: dict) -> str:
    """将六爻排盘结果格式化为可读的文本"""

    lines_data = result["lines"]
    tp = result["time_params"]

    out = []
    out.append(f"# 六爻排盘：{result['hexagram_name']}")
    out.append(f"")
    out.append(f"**{result['gong']}宫{result['gong_type']}卦** · 宫五行：{result['gong_wuxing']}")
    out.append(f"月建：{tp['month_dizhi']}　日辰：{tp['day_ganzhi']}（日干：{tp['day_gan']}）")
    out.append(f"世爻：第{result['shi_yao']}爻　应爻：第{result['ying_yao']}爻")
    out.append(f"")

    # 排盘表格
    out.append("```")
    out.append(f"六神  伏神      {'本卦':^16s}       变卦")
    out.append("─" * 56)

    for i in range(5, -1, -1):  # 从上爻到初爻
        line = lines_data[i]
        pos = line["position"]

        # 六神
        shen = line["liushen"][:2]

        # 伏神
        fu_str = "    "
        for fu_name, fu_info in result.get("fushen", {}).items():
            if fu_info and fu_info["position"] == pos:
                fu_str = f"{fu_info['liuqin'][:2]}{fu_info['tiangan']}{fu_info['dizhi']}"

        # 本卦爻
        yao_str = "————" if line["yinyang"] == "阳" else "—— ——"
        lq = line["liuqin"]
        tg_dz = f"{line['tiangan']}{line['dizhi']}"
        wx = line["wuxing"]

        # 标注
        marks = []
        if line["is_shi"]:
            marks.append("世")
        if line["is_ying"]:
            marks.append("应")
        if line["is_moving"]:
            marks.append("○")
        mark_str = " " + "".join(marks) if marks else ""

        # 变卦
        ch_str = ""
        if result.get("changed_lines") and result["changed_lines"][i]:
            ch = result["changed_lines"][i]
            ch_str = f" → {ch['liuqin'][:2]}{ch['tiangan']}{ch['dizhi']}"

        # 旺衰标注
        strength = line["month_strength"]
        strength_mark = ""
        if line["yuepo"]:
            strength_mark = "[破]"
        elif strength in ("旺", "相"):
            strength_mark = f"[{strength}]"
        elif strength in ("囚", "死"):
            strength_mark = f"[{strength}]"

        out.append(
            f"{shen:　<3s}{fu_str:　<5s}"
            f"{lq[:2]}{tg_dz}{wx} {yao_str}{mark_str}{ch_str} {strength_mark}"
        )

    out.append("─" * 56)
    out.append("```")
    out.append("")

    # 用神
    ys = result["yongshen"]
    out.append(f"**用神（妻财）：** {ys['description']}")
    if ys["type"] == "卦中":
        out.append(f"用神月建状态：{ys['month_strength']}")
        if ys["is_moving"]:
            out.append("用神发动——所问之事有变化趋势")
    elif ys["type"] == "伏神":
        out.append(f"用神伏藏——所求之事暂时不显现")
    out.append("")

    return "\n".join(out)


# ============================================================
# 与梅花易数结果联动
# ============================================================

def liuyao_from_meihua(meihua_result: dict, year: int, month: int, day: int,
                       hour: int = 12, minute: int = 0) -> dict:
    """
    基于梅花易数的结果自动进行六爻排盘。

    Args:
        meihua_result: meihua_time_divination() 的输出
        year, month, day, hour, minute: 起卦时间

    Returns:
        dict: 六爻排盘结果
    """
    hex_name = meihua_result["本卦"]["name"]
    moving = [meihua_result["动爻"]["position"]]

    return liuyao_paipan(
        hexagram_name=hex_name,
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        moving_lines=moving,
    )
