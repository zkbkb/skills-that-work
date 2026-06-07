"""
yao_interpreter.py — 爻辞解读提示生成器（通用版）
================================================
基于爻位语义 × 阴阳属性 × 所属经卦物象，程序化生成每一爻的解读提示。
适用于任意占问场景，不限于寻物。

继承自 divination-lost-items v2.2.1，泛化为通用解读框架。
"""

from .data_tables import (
    TRIGRAM_INFO, TRIGRAM_LINES, LINES_TO_TRIGRAM,
    HEXAGRAM_TABLE, XIANTIAN_NUMBER,
)


# ============================================================
# 一、爻位基础语义（通用场景）
# ============================================================

POSITION_SEMANTICS = {
    1: {
        "spatial": "最低处、地面附近、基础位置",
        "temporal": "事情刚开始、初期阶段",
        "general": "事情的根基和出发点；力量尚弱，宜蓄势不宜冒进",
        "person": "基层人员、最年轻的人、初次接触者",
        "level": "基础/起步",
    },
    2: {
        "spatial": "室内、中低位置、内部空间",
        "temporal": "事情发展中、中间偏早阶段",
        "general": "内部稳固的中心；得中得正则吉，偏则有内部纠纷",
        "person": "女性、母亲、家中主要照顾者、中层",
        "level": "内部/中位",
    },
    3: {
        "spatial": "内外交界处、门口、过渡区域",
        "temporal": "事情的转折点、内外切换的时刻",
        "general": "内卦之极，即将跨入外部；进退两难的关键节点",
        "person": "邻居、同住者、进出频繁的人",
        "level": "门槛/转折",
    },
    4: {
        "spatial": "外部空间的入口、离内不远处",
        "temporal": "事情已发展到外部阶段",
        "general": "初入外部领域，靠近核心但尚未到达；需谨慎行事",
        "person": "外部的熟人、同事、近臣",
        "level": "外部/接近核心",
    },
    5: {
        "spatial": "较远处、外部核心区域、高位",
        "temporal": "事情发展到中后期",
        "general": "君位、核心决策层；得此爻动多为关键变化",
        "person": "权威人物、领导、能力强的决策者",
        "level": "核心/领导",
    },
    6: {
        "spatial": "最高处或最远处",
        "temporal": "事情的末期、极端阶段",
        "general": "事态之极，物极必反；过度则有反转风险",
        "person": "陌生人、远方的人、退休者、旁观者",
        "level": "极端/终结",
    },
}


# ============================================================
# 二、阴阳属性的通用语义
# ============================================================

YINYANG_SEMANTICS = {
    "阳": {
        "visibility": "明显、显露、在较明亮或开放的状态",
        "state": "积极、主动、有力、外向",
        "energy": "主动出击有效、阳刚之力占主导",
    },
    "阴": {
        "visibility": "隐蔽、含蓄、在暗处或封闭状态",
        "state": "被动、守静、柔和、内敛",
        "energy": "等待时机或借助他人力量更有效",
    },
}


# ============================================================
# 三、阳变阴 / 阴变阳 的动态语义
# ============================================================

CHANGE_SEMANTICS = {
    "阳变阴": {
        "trend": "从显到隐、从外到内、从动到静、从盛到衰",
        "general": "事态正在从活跃期进入收敛期，能量在减退",
        "advice": "宜在变化完成前抓住现有窗口，不宜拖延",
    },
    "阴变阳": {
        "trend": "从隐到显、从内到外、从静到动、从衰到盛",
        "general": "事态正在从蛰伏期进入活跃期，新的能量在涌现",
        "advice": "保持关注，转机可能正在酝酿或即将到来",
    },
}


# ============================================================
# 四、核心生成函数
# ============================================================

def generate_yao_hint(
    hexagram_name: str,
    line_position: int,
    line_yinyang: str,
    is_moving: bool = False,
    changed_yinyang: str = None,
    upper_trigram: str = None,
    lower_trigram: str = None,
) -> dict:
    """
    为某一爻生成通用解读提示。

    Args:
        hexagram_name: 卦名
        line_position: 爻位 (1-6)
        line_yinyang: '阳' 或 '阴'
        is_moving: 是否为动爻
        changed_yinyang: 变化后的阴阳（仅动爻）
        upper_trigram: 上卦名
        lower_trigram: 下卦名

    Returns:
        dict: {
            "position_hint": str,
            "yinyang_hint": str,
            "trigram_hint": str,
            "change_hint": str,
            "combined": str,
        }
    """
    pos_sem = POSITION_SEMANTICS[line_position]
    yy_sem = YINYANG_SEMANTICS[line_yinyang]

    # 确定该爻所属的经卦
    if line_position <= 3:
        trigram_name = lower_trigram
    else:
        trigram_name = upper_trigram

    trigram_info = TRIGRAM_INFO.get(trigram_name, {})
    trigram_env = trigram_info.get("env", "")
    trigram_nature = trigram_info.get("nature", "")

    # 构建各维度提示
    position_hint = (
        f"爻位在第{line_position}位（{pos_sem['level']}）："
        f"{pos_sem['spatial']}。{pos_sem['general']}。"
    )
    yinyang_hint = f"此爻为{line_yinyang}爻：{yy_sem['state']}。"

    trigram_hint = ""
    if trigram_name:
        trigram_hint = (
            f"此爻属{trigram_name}卦（{trigram_nature}）范畴，"
            f"环境/物象特征：{trigram_env}。"
        )

    change_hint = ""
    if is_moving and changed_yinyang:
        change_key = f"{line_yinyang}变{changed_yinyang}"
        ch_sem = CHANGE_SEMANTICS.get(change_key, {})
        change_hint = (
            f"动爻{change_key}：{ch_sem.get('trend', '')}。"
            f"趋势：{ch_sem.get('general', '')}。"
            f"建议：{ch_sem.get('advice', '')}。"
        )

    parts = [position_hint]
    if yinyang_hint:
        parts.append(yinyang_hint)
    if trigram_hint:
        parts.append(trigram_hint)
    if change_hint:
        parts.append(change_hint)

    combined = " ".join(parts)

    return {
        "position_hint": position_hint,
        "yinyang_hint": yinyang_hint,
        "trigram_hint": trigram_hint,
        "change_hint": change_hint,
        "combined": combined,
    }


def generate_moving_line_analysis(hexagram_result: dict) -> dict:
    """
    为给定卦象的动爻生成完整的解读提示。

    Args:
        hexagram_result: meihua_time_divination() 等函数的输出

    Returns:
        dict: {
            "yao_name": str,
            "position": int,
            "hint": dict (from generate_yao_hint),
            "all_lines_context": list
        }
    """
    ben_gua = hexagram_result["本卦"]
    dong_yao = hexagram_result["动爻"]
    upper = ben_gua["upper"]["name"]
    lower = ben_gua["lower"]["name"]
    lines = ben_gua["lines"]

    moving_pos = dong_yao["position"]
    moving_yy = dong_yao["original"]
    changed_yy = dong_yao["changed"]

    moving_hint = generate_yao_hint(
        hexagram_name=ben_gua["name"],
        line_position=moving_pos,
        line_yinyang=moving_yy,
        is_moving=True,
        changed_yinyang=changed_yy,
        upper_trigram=upper,
        lower_trigram=lower,
    )

    all_context = []
    for i in range(6):
        pos = i + 1
        yy = "阳" if lines[i] == 1 else "阴"
        hint = generate_yao_hint(
            hexagram_name=ben_gua["name"],
            line_position=pos,
            line_yinyang=yy,
            is_moving=(pos == moving_pos),
            changed_yinyang=changed_yy if pos == moving_pos else None,
            upper_trigram=upper,
            lower_trigram=lower,
        )
        all_context.append({
            "position": pos,
            "yinyang": yy,
            "is_moving": pos == moving_pos,
            "brief": hint["position_hint"],
        })

    return {
        "yao_name": dong_yao["name"],
        "position": moving_pos,
        "hint": moving_hint,
        "all_lines_context": all_context,
    }
