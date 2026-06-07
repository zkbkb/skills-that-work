"""
meihua.py — 梅花易数起卦计算引擎
=======================================
支持三种起卦方式：
  1. 时间起卦（默认）
  2. 报数起卦（可选，用户主动要求时使用）
  3. 汉字起卦（可选，用户主动要求时使用）

输出完整的卦象信息，包括本卦、变卦、互卦、体用关系、五行生克。
"""

import json
from datetime import datetime

from .data_tables import (
    XIANTIAN_NUMBER, XIANTIAN_REVERSE,
    TRIGRAM_INFO, TRIGRAM_LINES, LINES_TO_TRIGRAM,
    HEXAGRAM_TABLE,
    WUXING_SHENG, WUXING_KE, get_wuxing_relation,
    get_season_strength,
)
from .calendar_utils import get_divination_time_params


# ============================================================
# 核心起卦函数
# ============================================================

def meihua_time_divination(
    year: int, month: int, day: int,
    hour: int, minute: int = 0
) -> dict:
    """
    梅花易数 · 时间起卦法

    算法：
      上卦 = (年支数 + 农历月 + 农历日) mod 8，余数为0则作8
      下卦 = (年支数 + 农历月 + 农历日 + 时辰数) mod 8
      动爻 = (年支数 + 农历月 + 农历日 + 时辰数) mod 6，余数为0则作6

    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 24小时制小时
        minute: 分钟

    Returns:
        dict: 完整卦象信息
    """
    # 获取时间参数
    time_params = get_divination_time_params(year, month, day, hour, minute)

    yb = time_params["year_branch_number"]    # 年支数
    lm = time_params["lunar_month"]           # 农历月
    ld = time_params["lunar_day"]             # 农历日
    sc = time_params["shichen_number"]        # 时辰数

    # 计算上卦、下卦、动爻
    upper_sum = yb + lm + ld
    total_sum = yb + lm + ld + sc

    upper_num = upper_sum % 8 or 8
    lower_num = total_sum % 8 or 8
    moving_line = total_sum % 6 or 6

    # 组装卦象
    result = _build_hexagram_result(
        upper_num=upper_num,
        lower_num=lower_num,
        moving_line=moving_line,
        method="时间起卦",
        params={
            "time_params": time_params,
            "calculation": {
                "year_branch": yb,
                "lunar_month": lm,
                "lunar_day": ld,
                "shichen": sc,
                "upper_sum": upper_sum,
                "total_sum": total_sum,
                "upper_mod": f"{upper_sum} mod 8 = {upper_num}",
                "lower_mod": f"{total_sum} mod 8 = {lower_num}",
                "moving_mod": f"{total_sum} mod 6 = {moving_line}",
            }
        },
        lunar_month=lm,
    )

    return result


def meihua_number_divination(num1: int, num2: int = None) -> dict:
    """
    梅花易数 · 报数起卦法

    算法：
      - 报一个数：上卦 = 数 mod 8，下卦 = 时辰数，动爻 = 数 mod 6
      - 报两个数：上卦 = num1 mod 8，下卦 = num2 mod 8，
                  动爻 = (num1 + num2) mod 6

    注意：此方法仅在用户主动要求时使用。

    Args:
        num1: 第一个数
        num2: 第二个数（可选）

    Returns:
        dict: 完整卦象信息
    """
    if num2 is None:
        # 单数起卦
        now = datetime.now()
        time_params = get_divination_time_params(
            now.year, now.month, now.day, now.hour, now.minute
        )
        sc = time_params["shichen_number"]

        upper_num = num1 % 8 or 8
        lower_num = sc % 8 or 8
        moving_line = num1 % 6 or 6
        lunar_month = time_params["lunar_month"]

        params = {
            "number": num1,
            "shichen": sc,
            "calculation": {
                "upper_mod": f"{num1} mod 8 = {upper_num}",
                "lower_mod": f"{sc} (时辰) mod 8 = {lower_num}",
                "moving_mod": f"{num1} mod 6 = {moving_line}",
            }
        }
    else:
        # 双数起卦
        upper_num = num1 % 8 or 8
        lower_num = num2 % 8 or 8
        moving_line = (num1 + num2) % 6 or 6

        now = datetime.now()
        time_params = get_divination_time_params(
            now.year, now.month, now.day, now.hour, now.minute
        )
        lunar_month = time_params["lunar_month"]

        params = {
            "numbers": [num1, num2],
            "calculation": {
                "upper_mod": f"{num1} mod 8 = {upper_num}",
                "lower_mod": f"{num2} mod 8 = {lower_num}",
                "moving_mod": f"({num1}+{num2}) mod 6 = {moving_line}",
            }
        }

    return _build_hexagram_result(
        upper_num=upper_num,
        lower_num=lower_num,
        moving_line=moving_line,
        method="报数起卦",
        params=params,
        lunar_month=lunar_month,
    )


def meihua_character_divination(text: str) -> dict:
    """
    梅花易数 · 汉字起卦法

    算法：
      - 单字：总笔画数同时取上下卦，再加时辰取动爻
      - 两字：第一字笔画取上卦，第二字笔画取下卦，
              总笔画加时辰取动爻
      - 多字：前半笔画总和取上卦，后半笔画总和取下卦，
              全部笔画总和加时辰取动爻

    注意：此方法仅在用户主动要求时使用。
    自动查询 Unicode Unihan 笔画数据，覆盖 CJK 基本区 20992 个汉字。

    Args:
        text: 汉字字符串

    Returns:
        dict: 完整卦象信息，或 need_stroke_count 状态（若有字未收录）
    """
    from .stroke_count import get_total_strokes

    stroke_info = get_total_strokes(text)

    if not stroke_info["all_found"]:
        missing = "、".join(stroke_info["missing"])
        return {
            "method": "汉字起卦",
            "text": text,
            "status": "need_stroke_count",
            "stroke_info": stroke_info,
            "message": (
                f"以下汉字未收录笔画数据：{missing}。"
                "请用户提供这些字的笔画数，或由 Claude 根据知识判断后确认。"
            ),
        }

    strokes = [c["strokes"] for c in stroke_info["characters"]]

    now = datetime.now()
    time_params = get_divination_time_params(
        now.year, now.month, now.day, now.hour, now.minute
    )
    shichen_number = time_params["shichen_number"]
    lunar_month = time_params["lunar_month"]

    return meihua_character_divination_with_strokes(
        strokes=strokes,
        shichen_number=shichen_number,
        lunar_month=lunar_month,
        _text=text,
        _stroke_info=stroke_info,
    )


def meihua_character_divination_with_strokes(
    strokes: list,
    shichen_number: int = None,
    lunar_month: int = None,
    _text: str = None,
    _stroke_info: dict = None,
) -> dict:
    """
    汉字起卦的实际计算（笔画数已确认后调用）

    Args:
        strokes: 每个字的笔画数列表，如 [8, 12]
        shichen_number: 时辰数（若不提供则自动获取当前时辰）
        lunar_month: 农历月（若不提供则自动获取）
        _text: 原始文本（由 meihua_character_divination 自动传入）
        _stroke_info: 笔画查询详情（由 meihua_character_divination 自动传入）
    """
    if shichen_number is None or lunar_month is None:
        now = datetime.now()
        time_params = get_divination_time_params(
            now.year, now.month, now.day, now.hour, now.minute
        )
        if shichen_number is None:
            shichen_number = time_params["shichen_number"]
        if lunar_month is None:
            lunar_month = time_params["lunar_month"]

    total = sum(strokes)
    n = len(strokes)

    if n == 1:
        upper_num = strokes[0] % 8 or 8
        lower_num = strokes[0] % 8 or 8
        moving_line = (strokes[0] + shichen_number) % 6 or 6
    elif n == 2:
        upper_num = strokes[0] % 8 or 8
        lower_num = strokes[1] % 8 or 8
        moving_line = (total + shichen_number) % 6 or 6
    else:
        mid = n // 2
        upper_sum = sum(strokes[:mid])
        lower_sum = sum(strokes[mid:])
        upper_num = upper_sum % 8 or 8
        lower_num = lower_sum % 8 or 8
        moving_line = (total + shichen_number) % 6 or 6

    return _build_hexagram_result(
        upper_num=upper_num,
        lower_num=lower_num,
        moving_line=moving_line,
        method="汉字起卦",
        params={"strokes": strokes, "total": total, "shichen": shichen_number},
        lunar_month=lunar_month,
    )


# ============================================================
# 卦象构建核心函数
# ============================================================

def _build_hexagram_result(
    upper_num: int,
    lower_num: int,
    moving_line: int,
    method: str,
    params: dict,
    lunar_month: int = None,
) -> dict:
    """
    根据上卦数、下卦数、动爻位，构建完整的卦象分析结果。

    Args:
        upper_num: 上卦先天数 (1-8)
        lower_num: 下卦先天数 (1-8)
        moving_line: 动爻位 (1-6)
        method: 起卦方式名称
        params: 起卦参数详情
        lunar_month: 农历月（用于判断旺衰）

    Returns:
        dict: 完整卦象结构
    """

    upper_name = XIANTIAN_NUMBER[upper_num]
    lower_name = XIANTIAN_NUMBER[lower_num]

    # --- 本卦 ---
    hex_key = (upper_name, lower_name)
    hex_info = HEXAGRAM_TABLE.get(hex_key, {
        "name": f"{upper_name}上{lower_name}下",
        "seq": 0,
        "gong": "未知",
        "summary": "",
    })

    # --- 本卦六爻 (从下到上: 1-6) ---
    lower_lines = TRIGRAM_LINES[lower_name]  # 爻1,2,3
    upper_lines = TRIGRAM_LINES[upper_name]  # 爻4,5,6
    all_lines = lower_lines + upper_lines     # [爻1, 爻2, ..., 爻6]

    # --- 动爻变化 -> 变卦 ---
    changed_lines = list(all_lines)
    moving_idx = moving_line - 1  # 转为0-indexed
    changed_lines[moving_idx] = 1 - changed_lines[moving_idx]  # 阳变阴，阴变阳

    changed_lower = LINES_TO_TRIGRAM[tuple(changed_lines[:3])]
    changed_upper = LINES_TO_TRIGRAM[tuple(changed_lines[3:])]

    changed_hex_key = (changed_upper, changed_lower)
    changed_hex_info = HEXAGRAM_TABLE.get(changed_hex_key, {
        "name": f"{changed_upper}上{changed_lower}下",
        "seq": 0,
        "gong": "未知",
        "summary": "",
    })

    # --- 互卦 (取2,3,4爻为下卦；3,4,5爻为上卦) ---
    mutual_lower = LINES_TO_TRIGRAM[tuple(all_lines[1:4])]  # 爻2,3,4
    mutual_upper = LINES_TO_TRIGRAM[tuple(all_lines[2:5])]  # 爻3,4,5

    mutual_hex_key = (mutual_upper, mutual_lower)
    mutual_hex_info = HEXAGRAM_TABLE.get(mutual_hex_key, {
        "name": f"{mutual_upper}上{mutual_lower}下",
        "seq": 0,
        "gong": "未知",
        "summary": "",
    })

    # --- 体用关系 ---
    # 动爻在哪个经卦中，该经卦为「用」，另一个为「体」
    if moving_line <= 3:
        # 动爻在下卦 -> 下卦为用，上卦为体
        ti_trigram = upper_name
        yong_trigram = lower_name
        ti_position = "上卦"
        yong_position = "下卦"
    else:
        # 动爻在上卦 -> 上卦为用，下卦为体
        ti_trigram = lower_name
        yong_trigram = upper_name
        ti_position = "下卦"
        yong_position = "上卦"

    ti_wuxing = TRIGRAM_INFO[ti_trigram]["wuxing"]
    yong_wuxing = TRIGRAM_INFO[yong_trigram]["wuxing"]
    ti_yong_relation = get_wuxing_relation(ti_wuxing, yong_wuxing)

    # --- 五行生克分析 ---
    mutual_upper_wx = TRIGRAM_INFO[mutual_upper]["wuxing"]
    mutual_lower_wx = TRIGRAM_INFO[mutual_lower]["wuxing"]
    changed_lower_wx = TRIGRAM_INFO[changed_lower]["wuxing"]
    changed_upper_wx = TRIGRAM_INFO[changed_upper]["wuxing"]

    wuxing_analysis = {
        "体卦": {
            "trigram": ti_trigram,
            "wuxing": ti_wuxing,
            "position": ti_position,
        },
        "用卦": {
            "trigram": yong_trigram,
            "wuxing": yong_wuxing,
            "position": yong_position,
        },
        "体用关系": ti_yong_relation,
        "互卦上对体": get_wuxing_relation(
            TRIGRAM_INFO[mutual_upper]["wuxing"], ti_wuxing
        ),
        "互卦下对体": get_wuxing_relation(
            TRIGRAM_INFO[mutual_lower]["wuxing"], ti_wuxing
        ),
        "变卦下对体": get_wuxing_relation(
            changed_lower_wx, ti_wuxing
        ),
        "变卦上对体": get_wuxing_relation(
            changed_upper_wx, ti_wuxing
        ),
    }

    # --- 旺衰判断 ---
    season_info = None
    if lunar_month is not None:
        ti_strength = get_season_strength(ti_wuxing, lunar_month)
        yong_strength = get_season_strength(yong_wuxing, lunar_month)
        season_info = {
            "lunar_month": lunar_month,
            "体卦旺衰": ti_strength,
            "用卦旺衰": yong_strength,
        }

    # --- 爻辞位置 ---
    yao_names = ["初", "二", "三", "四", "五", "上"]
    yao_yinyang = "九" if all_lines[moving_idx] == 1 else "六"
    moving_yao_name = f"{yao_yinyang}{yao_names[moving_idx]}"
    if moving_idx == 0:
        moving_yao_name = f"初{yao_yinyang}"
    elif moving_idx == 5:
        moving_yao_name = f"上{yao_yinyang}"

    # --- 方位汇总 ---
    direction_analysis = {
        "体卦方位": TRIGRAM_INFO[ti_trigram]["direction"],
        "用卦方位": TRIGRAM_INFO[yong_trigram]["direction"],
        "变卦上方位": TRIGRAM_INFO[changed_upper]["direction"],
        "变卦下方位": TRIGRAM_INFO[changed_lower]["direction"],
        "体卦环境": TRIGRAM_INFO[ti_trigram]["env"],
        "用卦环境": TRIGRAM_INFO[yong_trigram]["env"],
    }

    # --- 组装结果 ---
    return {
        "method": method,
        "params": params,

        "本卦": {
            "name": hex_info["name"],
            "sequence": hex_info["seq"],
            "gong": hex_info["gong"],
            "summary": hex_info["summary"],
            "upper": {
                "name": upper_name,
                "number": upper_num,
                "symbol": TRIGRAM_INFO[upper_name]["symbol"],
                "wuxing": TRIGRAM_INFO[upper_name]["wuxing"],
            },
            "lower": {
                "name": lower_name,
                "number": lower_num,
                "symbol": TRIGRAM_INFO[lower_name]["symbol"],
                "wuxing": TRIGRAM_INFO[lower_name]["wuxing"],
            },
            "lines": all_lines,
        },

        "动爻": {
            "position": moving_line,
            "name": moving_yao_name,
            "original": "阳" if all_lines[moving_idx] == 1 else "阴",
            "changed": "阴" if all_lines[moving_idx] == 1 else "阳",
        },

        "变卦": {
            "name": changed_hex_info["name"],
            "sequence": changed_hex_info["seq"],
            "gong": changed_hex_info["gong"],
            "summary": changed_hex_info["summary"],
            "upper": {
                "name": changed_upper,
                "symbol": TRIGRAM_INFO[changed_upper]["symbol"],
                "wuxing": TRIGRAM_INFO[changed_upper]["wuxing"],
            },
            "lower": {
                "name": changed_lower,
                "symbol": TRIGRAM_INFO[changed_lower]["symbol"],
                "wuxing": TRIGRAM_INFO[changed_lower]["wuxing"],
            },
            "lines": changed_lines,
        },

        "互卦": {
            "name": mutual_hex_info["name"],
            "sequence": mutual_hex_info["seq"],
            "gong": mutual_hex_info["gong"],
            "summary": mutual_hex_info["summary"],
            "upper": {
                "name": mutual_upper,
                "symbol": TRIGRAM_INFO[mutual_upper]["symbol"],
                "wuxing": TRIGRAM_INFO[mutual_upper]["wuxing"],
            },
            "lower": {
                "name": mutual_lower,
                "symbol": TRIGRAM_INFO[mutual_lower]["symbol"],
                "wuxing": TRIGRAM_INFO[mutual_lower]["wuxing"],
            },
        },

        "体用": wuxing_analysis,
        "旺衰": season_info,
        "方位": direction_analysis,
    }


# ============================================================
# 格式化输出（纯文本/Markdown）
# ============================================================

def format_hexagram_text(result: dict) -> str:
    """将卦象结果格式化为可读的文本报告"""

    lines = []
    lines.append(f"# 梅花易数起卦报告")
    lines.append(f"")
    lines.append(f"**起卦方式：** {result['method']}")
    lines.append(f"")

    # 本卦
    bk = result["本卦"]
    lines.append(f"## 本卦：{bk['name']}（第{bk['sequence']}卦）")
    lines.append(
        f"上卦 {bk['upper']['symbol']} {bk['upper']['name']}"
        f"（{bk['upper']['wuxing']}） / "
        f"下卦 {bk['lower']['symbol']} {bk['lower']['name']}"
        f"（{bk['lower']['wuxing']}）"
    )
    lines.append(f"卦辞：{bk['summary']}")
    lines.append(f"")

    # 爻象展示
    lines.append(f"### 爻象（从下到上）")
    lines.append(f"```")
    yao_names_display = ["初", "二", "三", "四", "五", "上"]
    for i in range(5, -1, -1):
        yao_val = bk["lines"][i]
        yao_str = "———— " if yao_val == 1 else "—— ——"
        yy = "九" if yao_val == 1 else "六"
        if i == 0:
            label = f"初{yy}"
        elif i == 5:
            label = f"上{yy}"
        else:
            label = f"{yy}{yao_names_display[i]}"
        moving_mark = "  ← 动爻" if (i + 1) == result["动爻"]["position"] else ""
        lines.append(f"  {label}  {yao_str}{moving_mark}")
    lines.append(f"```")
    lines.append(f"")

    # 动爻
    dy = result["动爻"]
    lines.append(
        f"**动爻：** 第{dy['position']}爻（{dy['name']}），"
        f"{dy['original']}变{dy['changed']}"
    )
    lines.append(f"")

    # 变卦
    bk2 = result["变卦"]
    lines.append(f"## 变卦：{bk2['name']}（第{bk2['sequence']}卦）")
    lines.append(
        f"上卦 {bk2['upper']['symbol']} {bk2['upper']['name']}"
        f"（{bk2['upper']['wuxing']}） / "
        f"下卦 {bk2['lower']['symbol']} {bk2['lower']['name']}"
        f"（{bk2['lower']['wuxing']}）"
    )
    lines.append(f"卦辞：{bk2['summary']}")
    lines.append(f"")

    # 互卦
    hk = result["互卦"]
    lines.append(f"## 互卦：{hk['name']}（第{hk['sequence']}卦）")
    lines.append(
        f"上卦 {hk['upper']['symbol']} {hk['upper']['name']}"
        f"（{hk['upper']['wuxing']}） / "
        f"下卦 {hk['lower']['symbol']} {hk['lower']['name']}"
        f"（{hk['lower']['wuxing']}）"
    )
    lines.append(f"")

    # 体用
    ty = result["体用"]
    lines.append(f"## 体用关系")
    lines.append(
        f"- 体卦：{ty['体卦']['trigram']}"
        f"（{ty['体卦']['wuxing']}，{ty['体卦']['position']}）"
    )
    lines.append(
        f"- 用卦：{ty['用卦']['trigram']}"
        f"（{ty['用卦']['wuxing']}，{ty['用卦']['position']}）"
    )
    lines.append(f"- 体用关系：体{ty['体用关系']}用")
    lines.append(f"")

    # 旺衰
    if result["旺衰"]:
        ws = result["旺衰"]
        lines.append(f"## 旺衰")
        lines.append(f"- 农历{ws['lunar_month']}月")
        lines.append(f"- 体卦（{ty['体卦']['wuxing']}）：{ws['体卦旺衰']}")
        lines.append(f"- 用卦（{ty['用卦']['wuxing']}）：{ws['用卦旺衰']}")
        lines.append(f"")

    # 方位
    fx = result["方位"]
    lines.append(f"## 方位分析")
    lines.append(f"- 体卦方位：{fx['体卦方位']}")
    lines.append(f"- 用卦方位：{fx['用卦方位']}")
    lines.append(f"- 变卦方位：{fx['变卦上方位']}（上）/ {fx['变卦下方位']}（下）")
    lines.append(f"- 体卦环境：{fx['体卦环境']}")
    lines.append(f"- 用卦环境：{fx['用卦环境']}")

    return "\n".join(lines)


# ============================================================
# JSON 输出
# ============================================================

def to_json(result: dict, indent: int = 2) -> str:
    """将结果输出为 JSON 字符串"""
    return json.dumps(result, ensure_ascii=False, indent=indent)


# ============================================================
# CLI 入口（可直接运行测试）
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 5:
        y, m, d, h = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        mi = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    else:
        # 默认使用当前时间
        now = datetime.now()
        y, m, d, h, mi = now.year, now.month, now.day, now.hour, now.minute
        print(f"[使用当前时间: {y}-{m:02d}-{d:02d} {h:02d}:{mi:02d}]")

    result = meihua_time_divination(y, m, d, h, mi)
    print(format_hexagram_text(result))
    print("\n" + "=" * 50)
    print("[JSON 数据]")
    print(to_json(result))
