"""
cross_validation.py — 梅花易数×六爻纳甲 交叉验证引擎（通用版 v1.2）
====================================================================
将同一卦象的两个体系分析结果进行程序化对比，
从五个维度提取信号、判断一致性、生成综合报告。

五维度模型：
  1. 总体吉凶 — 体用关系 × 用神旺衰+世应
  2. 方位/方向 — 用卦方位 × 六神方位
  3. 核心动态 — 动爻归属(体/用) × 动爻六亲/六神
  4. 潜在风险 — 互卦/变卦信号 × 伏神/月破/日冲
  5. 时间/应期 — 卦数应期 × 地支冲合应期

设计原则：
  - 代码层只做客观的信号提取和数值对比，不引入场景判断
  - 场景化的含义修正通过 scene_notes 字段传递给 Claude
  - 一致则增强确信度，矛盾则以六爻为准但如实呈现差异
"""

from .data_tables import (
    TRIGRAM_INFO, WUXING_SHENG, WUXING_KE,
    get_wuxing_relation,
)
from .liuyao_data import (
    LIUSHEN_MEANING, LIUQIN_MEANING,
    GONG_WUXING, DIZHI_CHONG, DIZHI_WUXING,
)


# ============================================================
# 通用场景评分校准值
# ============================================================

# 梅花体用评分（通用场景）
# 对比寻物版：体克用从0上调至+1（通用场景中体克用是正面信号）
#            比和从+1下调至0（通用场景中是真正的中性）
#            用克体从-1下调至-2（通用场景中是明确负面）
TIYONG_SCORE_MAP = {
    "被生": 2,     # 用生体 → 吉
    "克":   1,     # 体克用 → 小吉（我有主动权）
    "比和":  0,    # 体用比和 → 中性
    "生":   -1,    # 体生用 → 小凶（我在消耗）
    "被克": -2,    # 用克体 → 凶
}

# 体克用在特定场景下的歧义提示
TIYONG_SCENE_NOTES = {
    "克": (
        "注意：体克用在通用场景下判为小吉（我方有主动权），"
        "但在感情占问中可能偏中性（我方主导=对方感到压力），"
        "在求财占问中则偏正面（我克财=得财）。"
        "请结合占问内容和 interpretation-guide §4.4 校准。"
    ),
    "生": (
        "注意：体生用在通用场景下判为小凶（我方消耗），"
        "但程度因场景而异——求财时意味着投入大于回报，"
        "感情时意味着一方付出过多。"
    ),
}

# 一致性标签定义
ALIGN_AGREE = "一致"        # 方向相同且强度相近
ALIGN_COMPLEMENT = "互补"    # 不同角度的信息，无方向矛盾
ALIGN_DIFFER = "不同"        # 方向或强度有实质差异


# ============================================================
# 核心入口
# ============================================================

def cross_validate(meihua_result: dict, liuyao_result: dict,
                   yingqi_result: dict = None) -> dict:
    """
    梅花×六爻交叉验证。

    Returns:
        dict with keys: fortune, direction, dynamics, risk, timing, overall
    """
    fortune = _compare_fortune(meihua_result, liuyao_result)
    direction = _compare_direction(meihua_result, liuyao_result)
    dynamics = _compare_dynamics(meihua_result, liuyao_result)
    risk = _compare_risk(meihua_result, liuyao_result)
    timing = _compare_timing(meihua_result, liuyao_result, yingqi_result)
    overall = _synthesize(fortune, direction, dynamics, risk, timing)

    return {
        "fortune": fortune,
        "direction": direction,
        "dynamics": dynamics,
        "risk": risk,
        "timing": timing,
        "overall": overall,
        # 兼容旧接口（部分引用了 recoverability/environment）
        "recoverability": fortune,
        "environment": {
            "combined_status": dynamics.get("summary", ""),
            "status_confidence": dynamics.get("alignment", ""),
            "note": dynamics.get("note", ""),
        },
    }


# ============================================================
# 维度一：总体吉凶
# ============================================================

def _compare_fortune(meihua: dict, liuyao: dict) -> dict:
    """
    梅花：体用生克 + 旺衰修正 → 数值评分
    六爻：用神旺衰 + 世应关系 + 伏藏扣分 → 数值评分
    """
    # ---- 梅花信号 ----
    ti_yong = meihua["体用"]
    ti_yong_rel = ti_yong["体用关系"]
    ti_strength = meihua.get("旺衰", {}).get("体卦旺衰", "未知")

    meihua_score = TIYONG_SCORE_MAP.get(ti_yong_rel, 0)

    # 旺衰修正
    if ti_strength in ("旺", "相"):
        meihua_score += 1
    elif ti_strength in ("囚", "死"):
        meihua_score -= 1

    meihua_label = _score_to_label(meihua_score)

    # 场景注释
    scene_notes = TIYONG_SCENE_NOTES.get(ti_yong_rel, "")

    # ---- 六爻信号 ----
    yongshen = liuyao["yongshen"]
    ys_type = yongshen["type"]
    ys_strength = yongshen.get("month_strength", "未知")
    ys_moving = yongshen.get("is_moving", False)
    shi_pos = liuyao["shi_yao"]

    liuyao_score = 0

    # 用神旺衰
    if ys_strength in ("旺", "相"):
        liuyao_score += 2
    elif ys_strength == "休":
        liuyao_score += 0
    elif ys_strength in ("囚", "死"):
        liuyao_score -= 1

    # 用神伏藏——显式扣分（改进方案 A1 修复点）
    if ys_type == "伏神":
        liuyao_score -= 1
    elif ys_type == "缺失":
        liuyao_score -= 2

    # 用神持世
    ys_at_shi = (ys_type == "卦中" and yongshen.get("position") == shi_pos)
    if ys_at_shi:
        liuyao_score += 2

    # 用神发动
    if ys_moving:
        liuyao_score += 1

    # 月破检查
    if ys_type == "卦中":
        ys_pos = yongshen["position"]
        ys_line = liuyao["lines"][ys_pos - 1]
        if ys_line.get("yuepo"):
            liuyao_score -= 3

    liuyao_label = _score_to_label(liuyao_score)

    # ---- 一致性判断（改进方案 A1 修复：伏藏时不误标为"互补"）----
    alignment = _compute_alignment(meihua_label, liuyao_label)

    # 伏藏特殊处理：如果梅花判为正面但六爻用神伏藏，升级为"不同"
    if ys_type == "伏神" and meihua_score > 0 and liuyao_score < 0:
        alignment = ALIGN_DIFFER

    return {
        "meihua": {
            "assessment": meihua_label,
            "basis": f"体用关系={ti_yong_rel}，体卦旺衰={ti_strength}",
            "score": meihua_score,
        },
        "liuyao": {
            "assessment": liuyao_label,
            "basis": f"用神={yongshen['description']}，月建状态={ys_strength}",
            "score": liuyao_score,
            "details": {
                "ys_type": ys_type,
                "ys_strength": ys_strength,
                "ys_at_shi": ys_at_shi,
                "ys_moving": ys_moving,
            },
        },
        "alignment": alignment,
        "combined_assessment": (
            meihua_label if alignment == ALIGN_AGREE else
            liuyao_label  # 矛盾时以六爻为准
        ),
        "scene_notes": scene_notes,
        "note": (
            f"梅花判断「{meihua_label}」（{ti_yong_rel}，体{ti_strength}），"
            f"六爻判断「{liuyao_label}」（{yongshen['description']}）。"
            + (_alignment_text(alignment, meihua_label, liuyao_label))
        ),
    }


# ============================================================
# 维度二：方位/方向
# ============================================================

def _compare_direction(meihua: dict, liuyao: dict) -> dict:
    """梅花：用卦/变卦方位。六爻：用神临六神方位。"""
    yong_trigram = meihua["体用"]["用卦"]["trigram"]
    yong_dir = TRIGRAM_INFO[yong_trigram]["direction"]

    changed_upper = meihua["变卦"]["upper"]["name"]
    changed_dir = TRIGRAM_INFO[changed_upper]["direction"]

    meihua_dirs = [yong_dir]
    if changed_dir != yong_dir:
        meihua_dirs.append(changed_dir)

    # 六爻方位
    yongshen = liuyao["yongshen"]
    liuyao_dir = None
    liuyao_shen = None

    if yongshen["type"] == "卦中":
        ys_pos = yongshen["position"]
        ys_line = liuyao["lines"][ys_pos - 1]
        liuyao_shen = ys_line.get("liushen", "")
        shen_info = LIUSHEN_MEANING.get(liuyao_shen, {})
        liuyao_dir = shen_info.get("direction", "")

    # 一致性
    if liuyao_dir and liuyao_dir in meihua_dirs:
        alignment = ALIGN_AGREE
    elif liuyao_dir and liuyao_dir == "中":
        alignment = ALIGN_COMPLEMENT
    elif liuyao_dir:
        alignment = ALIGN_DIFFER
    else:
        alignment = ALIGN_COMPLEMENT  # 六爻方位不可用时不算矛盾

    all_dirs = list(set(meihua_dirs + ([liuyao_dir] if liuyao_dir else [])))

    return {
        "meihua": {
            "primary": yong_dir,
            "secondary": changed_dir if changed_dir != yong_dir else None,
        },
        "liuyao": {
            "direction": liuyao_dir,
            "liushen": liuyao_shen,
        },
        "alignment": alignment,
        "combined_directions": all_dirs,
        "note": (
            f"梅花指向{yong_dir}"
            + (f"（变卦补充{changed_dir}）" if changed_dir != yong_dir else "")
            + (f"，六爻用神临{liuyao_shen}指向{liuyao_dir}" if liuyao_dir else "")
            + "。"
        ),
    }


# ============================================================
# 维度三：核心动态
# ============================================================

def _compare_dynamics(meihua: dict, liuyao: dict) -> dict:
    """
    梅花：动爻在体卦还是用卦 → 变化的主体
    六爻：动爻的六亲和六神 → 变化的性质和来源
    """
    dong_yao = meihua["动爻"]
    dong_pos = dong_yao["position"]
    dong_in_ti = (dong_pos >= 4) == (meihua["体用"]["体卦"]["trigram"] ==
                                      meihua["本卦"]["upper"]["name"])
    # 动爻在体卦 → 我方在变；动爻在用卦 → 外部/事态在变
    meihua_driver = "体卦（我方在变化）" if dong_in_ti else "用卦（外部/事态在变化）"

    # 六爻动爻信息
    liuyao_moving = []
    for line in liuyao["lines"]:
        if line.get("is_moving"):
            liuyao_moving.append({
                "position": line["position"],
                "liuqin": line["liuqin"],
                "liushen": line.get("liushen", ""),
                "dizhi": line["dizhi"],
                "wuxing": line["wuxing"],
            })

    # 动爻六亲含义
    moving_liuqin_summary = ""
    if liuyao_moving:
        lq = liuyao_moving[0]["liuqin"]
        ls = liuyao_moving[0]["liushen"]
        LIUQIN_DYNAMICS = {
            "官鬼": "外部压力或权威介入",
            "妻财": "财务或所求之事正在变化",
            "父母": "文书/庇护/制度层面的变化",
            "子孙": "解决方案在出现，或享乐因素变化",
            "兄弟": "竞争加剧或同辈干扰",
        }
        moving_liuqin_summary = LIUQIN_DYNAMICS.get(lq, "")

    # 变卦趋势
    bian_gua = meihua["变卦"]["name"]
    hu_gua = meihua["互卦"]["name"]

    return {
        "meihua": {
            "driver": meihua_driver,
            "dong_in_ti": dong_in_ti,
        },
        "liuyao": {
            "moving_lines": liuyao_moving,
            "moving_summary": moving_liuqin_summary,
        },
        "bian_gua": bian_gua,
        "hu_gua": hu_gua,
        "summary": (
            f"变化驱动：{meihua_driver}。"
            + (f"六爻动爻为{liuyao_moving[0]['liuqin']}临{liuyao_moving[0]['liushen']}——{moving_liuqin_summary}。"
               if liuyao_moving and moving_liuqin_summary else "")
            + f"变卦{bian_gua}，互卦{hu_gua}。"
        ),
        "alignment": ALIGN_COMPLEMENT,  # 两体系在此维度天然互补
        "note": (
            f"动爻在{meihua_driver}"
            + (f"六爻中{liuyao_moving[0]['liuqin']}爻发动（{moving_liuqin_summary}）。"
               if liuyao_moving and moving_liuqin_summary else "。")
            + f"事态从{meihua['本卦']['name']}经{hu_gua}走向{bian_gua}。"
        ),
    }


# ============================================================
# 维度四：潜在风险
# ============================================================

def _compare_risk(meihua: dict, liuyao: dict) -> dict:
    """
    梅花：互卦/变卦对体卦的生克 → 过程和结果中的风险
    六爻：伏神/月破/日冲/官鬼动 → 具体风险信号
    """
    # ---- 梅花风险信号 ----
    ti_wuxing = meihua["体用"]["体卦"]["wuxing"]
    bian_upper_wx = meihua["变卦"]["upper"]["wuxing"]
    bian_lower_wx = meihua["变卦"]["lower"]["wuxing"]
    hu_upper_wx = meihua["互卦"]["upper"]["wuxing"]
    hu_lower_wx = meihua["互卦"]["lower"]["wuxing"]

    meihua_risks = []

    # 变卦克体 → 结果走向不利
    for wx in [bian_upper_wx, bian_lower_wx]:
        rel = get_wuxing_relation(wx, ti_wuxing)
        if rel == "克":
            meihua_risks.append(f"变卦{wx}克体卦{ti_wuxing}（结果趋势不利）")

    # 互卦克体 → 过程有阻碍
    for wx in [hu_upper_wx, hu_lower_wx]:
        rel = get_wuxing_relation(wx, ti_wuxing)
        if rel == "克":
            meihua_risks.append(f"互卦{wx}克体卦{ti_wuxing}（过程有阻碍）")

    # ---- 六爻风险信号 ----
    liuyao_risks = []

    yongshen = liuyao["yongshen"]

    # 用神伏藏
    if yongshen["type"] == "伏神":
        fushen = liuyao.get("fushen", {}).get("妻财")
        if fushen:
            liuyao_risks.append(
                f"用神伏藏于第{fushen['position']}爻"
                f"{fushen['host_liuqin']}之下（所求之事尚未显现）"
            )
        else:
            liuyao_risks.append("用神伏藏（所求之事尚未显现）")

    # 月破
    if yongshen["type"] == "卦中":
        ys_line = liuyao["lines"][yongshen["position"] - 1]
        if ys_line.get("yuepo"):
            liuyao_risks.append("用神月破（力量极弱，短期不利）")
        if ys_line.get("ri_chong"):
            ys_str = yongshen.get("month_strength", "")
            if ys_str in ("旺", "相"):
                liuyao_risks.append("用神日冲（旺相逢冲，冲起为动，可能是触发点）")
            else:
                liuyao_risks.append("用神日冲（休囚逢冲，冲散，不利）")

    # 官鬼发动
    for line in liuyao["lines"]:
        if line["liuqin"] == "官鬼" and line.get("is_moving"):
            shen = line.get("liushen", "")
            liuyao_risks.append(
                f"官鬼爻发动（第{line['position']}爻临{shen}）"
                f"——外部压力或变数介入"
            )

    # 综合风险等级
    total_risk_count = len(meihua_risks) + len(liuyao_risks)
    if total_risk_count == 0:
        risk_level = "低"
    elif total_risk_count <= 2:
        risk_level = "中"
    else:
        risk_level = "高"

    return {
        "meihua_risks": meihua_risks,
        "liuyao_risks": liuyao_risks,
        "risk_level": risk_level,
        "alignment": (
            ALIGN_AGREE if (meihua_risks and liuyao_risks) or
                           (not meihua_risks and not liuyao_risks)
            else ALIGN_COMPLEMENT
        ),
        "note": (
            f"风险等级：{risk_level}。"
            + (f"梅花信号：{'；'.join(meihua_risks)}。" if meihua_risks else "")
            + (f"六爻信号：{'；'.join(liuyao_risks)}。" if liuyao_risks else "")
            + ("两个体系均未发现明显风险信号。" if total_risk_count == 0 else "")
        ),
    }


# ============================================================
# 维度五：时间/应期
# ============================================================

def _compare_timing(meihua: dict, liuyao: dict, yingqi: dict = None) -> dict:
    """梅花：卦数应期。六爻：用神地支冲合应期。"""
    # ---- 梅花应期 ----
    meihua_timing = {}
    if yingqi:
        meihua_timing = {
            "urgency": yingqi.get("urgency", "未知"),
            "number_hints": yingqi.get("number_hints", []),
            "practical_window": yingqi.get("practical_window", ""),
        }

    # ---- 六爻应期 ----
    yongshen = liuyao["yongshen"]
    liuyao_timing = {}

    if yongshen["type"] == "卦中":
        ys_dizhi = yongshen["dizhi"]
        ys_strength = yongshen.get("month_strength", "休")
        ys_wx = yongshen["wuxing"]

        chong_dz = DIZHI_CHONG.get(ys_dizhi, "")

        # 生用神的五行
        sheng_ys_wx = None
        for wx_name in ["金", "木", "水", "火", "土"]:
            if WUXING_SHENG.get(wx_name) == ys_wx:
                sheng_ys_wx = wx_name
                break

        sheng_dizhi = [dz for dz, wx in DIZHI_WUXING.items()
                       if wx == sheng_ys_wx] if sheng_ys_wx else []

        if ys_strength in ("旺", "相"):
            liuyao_timing = {
                "method": "旺相逢冲",
                "key_dizhi": chong_dz,
                "description": f"用神{ys_dizhi}({ys_wx})旺相，逢{chong_dz}日/月应事",
                "urgency": "near",
            }
        else:
            liuyao_timing = {
                "method": "休囚逢生",
                "key_dizhi": sheng_dizhi,
                "description": (
                    f"用神{ys_dizhi}({ys_wx})休囚，"
                    f"逢{'/'.join(sheng_dizhi)}日（{sheng_ys_wx}生{ys_wx}）应事"
                    if sheng_dizhi else
                    f"用神{ys_dizhi}({ys_wx})休囚，等待生旺之时"
                ),
                "urgency": "far",
            }
    elif yongshen["type"] == "伏神":
        fushen = liuyao.get("fushen", {}).get("妻财")
        if fushen:
            host_dz = fushen["host_dizhi"]
            chong_host = DIZHI_CHONG.get(host_dz, "")
            liuyao_timing = {
                "method": "伏神出现",
                "key_dizhi": chong_host,
                "description": f"伏神藏于{host_dz}之下，逢{chong_host}日冲开飞神",
                "urgency": "far",
            }

    # ---- 一致性 ----
    urgency_map = {
        "urgent": "近", "moderate": "中", "relaxed": "远",
        "near": "近", "far": "远", "unknown": "未知",
    }
    m_urg = urgency_map.get(meihua_timing.get("urgency", "unknown"), "未知")
    l_urg = urgency_map.get(liuyao_timing.get("urgency", "unknown"), "未知")

    if m_urg == l_urg and m_urg != "未知":
        alignment = ALIGN_AGREE
    elif m_urg == "未知" or l_urg == "未知":
        alignment = ALIGN_COMPLEMENT
    else:
        alignment = ALIGN_DIFFER

    return {
        "meihua": meihua_timing,
        "liuyao": liuyao_timing,
        "alignment": alignment,
        "note": (
            (f"梅花应期：{meihua_timing.get('practical_window', '无数据')}。"
             if meihua_timing else "梅花应期：无数据。")
            + (f"六爻应期：{liuyao_timing.get('description', '无数据')}。"
               if liuyao_timing else "")
            + f"时间节奏{alignment}。"
        ),
    }


# ============================================================
# 综合评价
# ============================================================

def _synthesize(fortune, direction, dynamics, risk, timing) -> dict:
    """汇总五个维度的一致性，生成总评"""

    alignments = [
        fortune["alignment"],
        direction["alignment"],
        dynamics["alignment"],
        risk["alignment"],
        timing["alignment"],
    ]

    agree = sum(1 for a in alignments if a == ALIGN_AGREE)
    complement = sum(1 for a in alignments if a == ALIGN_COMPLEMENT)
    differ = sum(1 for a in alignments if a == ALIGN_DIFFER)

    if agree >= 3:
        confidence = "高"
        note = "梅花与六爻在多数维度一致，分析结论可信度高。"
    elif differ >= 2:
        confidence = "低"
        note = "梅花与六爻在多个维度存在差异，建议审慎对待，以六爻为主。"
    else:
        confidence = "中"
        note = "梅花与六爻部分一致、部分互补，以六爻精细判断为主、梅花宏观方向为辅。"

    return {
        "confidence": confidence,
        "agree_count": agree,
        "complement_count": complement,
        "differ_count": differ,
        "note": note,
        "combined_assessment": fortune["combined_assessment"],
        "combined_directions": direction["combined_directions"],
        "risk_level": risk["risk_level"],
    }


# ============================================================
# 格式化输出
# ============================================================

def format_cross_validation(cv: dict) -> str:
    """将交叉验证结果格式化为可读文本"""

    lines = []
    lines.append("## 梅花×六爻 交叉验证报告")
    lines.append("")

    overall = cv["overall"]
    lines.append(f"**综合确信度：{overall['confidence']}**")
    lines.append(f"（{overall['agree_count']}项一致 / "
                 f"{overall['complement_count']}项互补 / "
                 f"{overall['differ_count']}项不同）")
    lines.append("")
    lines.append(overall["note"])
    lines.append("")

    # 维度一：总体吉凶
    fort = cv["fortune"]
    lines.append("### 总体吉凶判断")
    lines.append("")
    lines.append(f"| 体系 | 判断 | 依据 |")
    lines.append(f"|------|------|------|")
    lines.append(f"| 梅花 | {fort['meihua']['assessment']} | {fort['meihua']['basis']} |")
    lines.append(f"| 六爻 | {fort['liuyao']['assessment']} | {fort['liuyao']['basis']} |")
    lines.append(f"| **综合** | **{fort['combined_assessment']}** | {fort['alignment']} |")
    if fort.get("scene_notes"):
        lines.append(f"")
        lines.append(f"> {fort['scene_notes']}")
    lines.append("")

    # 维度二：方位
    dir_ = cv["direction"]
    lines.append("### 方位指向")
    lines.append("")
    lines.append(dir_["note"])
    dirs = "、".join(dir_["combined_directions"])
    lines.append(f"综合方位：**{dirs}**")
    lines.append("")

    # 维度三：核心动态
    dyn = cv["dynamics"]
    lines.append("### 核心动态")
    lines.append("")
    lines.append(dyn["summary"])
    lines.append("")

    # 维度四：潜在风险
    rsk = cv["risk"]
    lines.append("### 潜在风险")
    lines.append("")
    lines.append(rsk["note"])
    lines.append("")

    # 维度五：时间
    tim = cv["timing"]
    lines.append("### 时间预判")
    lines.append("")
    lines.append(tim["note"])
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 辅助函数
# ============================================================

def _score_to_label(score: int) -> str:
    if score >= 2:
        return "高"
    elif score >= 0:
        return "中"
    else:
        return "低"


def _compute_alignment(label_a: str, label_b: str) -> str:
    if label_a == label_b:
        return ALIGN_AGREE
    levels = {"低": 0, "中": 1, "高": 2}
    diff = abs(levels.get(label_a, 1) - levels.get(label_b, 1))
    if diff == 1:
        return ALIGN_COMPLEMENT
    return ALIGN_DIFFER


def _alignment_text(alignment: str, m_label: str, l_label: str) -> str:
    if alignment == ALIGN_AGREE:
        return "两者一致，确信度高。"
    elif alignment == ALIGN_COMPLEMENT:
        return f"两者基本趋同（{m_label} vs {l_label}），以六爻为主。"
    else:
        return f"两者有差异（梅花{m_label} vs 六爻{l_label}），以六爻为准但保留两种判断。"
