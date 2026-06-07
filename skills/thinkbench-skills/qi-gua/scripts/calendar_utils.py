"""
calendar_utils.py — 公历农历转换工具
========================================
基于 lunardate 库实现精确的公历 <-> 农历转换。
若 lunardate 不可用，则回退到 lunarcalendar 或 cnlunar。
"""

import sys
from datetime import datetime, date

# 尝试加载农历转换库（按优先级）
_LUNAR_LIB = None

try:
    from lunardate import LunarDate
    _LUNAR_LIB = "lunardate"
except ImportError:
    try:
        import cnlunar
        _LUNAR_LIB = "cnlunar"
    except ImportError:
        _LUNAR_LIB = None


def install_lunar_library():
    """尝试安装 lunardate 库"""
    import subprocess
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "lunardate",
             "--break-system-packages", "-q"]
        )
        global _LUNAR_LIB, LunarDate
        from lunardate import LunarDate
        _LUNAR_LIB = "lunardate"
        return True
    except Exception as e:
        print(f"[WARNING] Failed to install lunardate: {e}")
        return False


def solar_to_lunar(year: int, month: int, day: int) -> dict:
    """
    公历日期 -> 农历日期

    Returns:
        dict: {
            "lunar_year": int,
            "lunar_month": int,
            "lunar_day": int,
            "is_leap_month": bool,
            "lunar_month_cn": str,  # 中文月份
            "lunar_day_cn": str,    # 中文日期
            "ganzhi_year": str,     # 干支纪年
        }
    """
    global _LUNAR_LIB

    if _LUNAR_LIB is None:
        if not install_lunar_library():
            raise RuntimeError(
                "无法加载农历转换库。请手动安装：pip install lunardate --break-system-packages"
            )

    if _LUNAR_LIB == "lunardate":
        return _solar_to_lunar_lunardate(year, month, day)
    elif _LUNAR_LIB == "cnlunar":
        return _solar_to_lunar_cnlunar(year, month, day)
    else:
        raise RuntimeError("No lunar calendar library available")


def _solar_to_lunar_lunardate(year: int, month: int, day: int) -> dict:
    """使用 lunardate 库转换"""
    from lunardate import LunarDate
    ld = LunarDate.fromSolarDate(year, month, day)

    from .data_tables import TIANGAN, DIZHI, year_to_ganzhi

    tg, dz = year_to_ganzhi(ld.year)

    return {
        "lunar_year": ld.year,
        "lunar_month": ld.month,
        "lunar_day": ld.day,
        "is_leap_month": getattr(ld, 'isLeapMonth', False),
        "lunar_month_cn": _month_to_cn(ld.month),
        "lunar_day_cn": _day_to_cn(ld.day),
        "ganzhi_year": f"{tg}{dz}",
    }


def _solar_to_lunar_cnlunar(year: int, month: int, day: int) -> dict:
    """使用 cnlunar 库转换"""
    import cnlunar
    dt = datetime(year, month, day)
    ln = cnlunar.Lunar(dt)

    from .data_tables import year_to_ganzhi

    tg, dz = year_to_ganzhi(ln.lunarYear)

    return {
        "lunar_year": ln.lunarYear,
        "lunar_month": ln.lunarMonth,
        "lunar_day": ln.lunarDay,
        "is_leap_month": ln.isLunarLeapMonth,
        "lunar_month_cn": _month_to_cn(ln.lunarMonth),
        "lunar_day_cn": _day_to_cn(ln.lunarDay),
        "ganzhi_year": f"{tg}{dz}",
    }


# ============================================================
# 中文数字转换辅助
# ============================================================

_MONTH_CN = {
    1: "正月", 2: "二月", 3: "三月", 4: "四月",
    5: "五月", 6: "六月", 7: "七月", 8: "八月",
    9: "九月", 10: "十月", 11: "冬月", 12: "腊月",
}

_DAY_CN_UNITS = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

def _month_to_cn(month: int) -> str:
    return _MONTH_CN.get(month, f"{month}月")

def _day_to_cn(day: int) -> str:
    """农历日期数字转中文：初一~三十"""
    if day <= 10:
        return f"初{_DAY_CN_UNITS[day]}"
    elif day < 20:
        return f"十{_DAY_CN_UNITS[day - 10]}"
    elif day == 20:
        return "二十"
    elif day < 30:
        return f"廿{_DAY_CN_UNITS[day - 20]}"
    else:
        return "三十"


# ============================================================
# 时辰判断
# ============================================================

def time_to_shichen(hour: int, minute: int = 0) -> dict:
    """
    24小时制时间 -> 时辰信息

    Returns:
        dict: {
            "dizhi": str,      # 地支
            "number": int,     # 地支序数（子=1...亥=12）
            "name": str,       # 时辰名称
            "time_range": str, # 时间范围
        }
    """
    from .data_tables import DIZHI, DIZHI_NUMBER, SHICHEN_TIME, hour_to_dizhi

    dz = hour_to_dizhi(hour, minute)
    return {
        "dizhi": dz,
        "number": DIZHI_NUMBER[dz],
        "name": f"{dz}时",
        "time_range": SHICHEN_TIME[dz],
    }


# ============================================================
# 获取起卦所需的完整时间参数
# ============================================================

def get_divination_time_params(
    year: int, month: int, day: int,
    hour: int, minute: int = 0
) -> dict:
    """
    从公历日期时间获取梅花易数起卦所需的全部参数。

    Returns:
        dict: {
            "solar": {"year", "month", "day", "hour", "minute"},
            "lunar": {农历信息},
            "shichen": {时辰信息},
            "year_branch_number": int,  # 年支数（用于起卦计算）
            "lunar_month": int,          # 农历月数
            "lunar_day": int,            # 农历日数
            "shichen_number": int,       # 时辰数
        }
    """
    lunar = solar_to_lunar(year, month, day)
    shichen = time_to_shichen(hour, minute)

    from .data_tables import DIZHI_NUMBER, year_to_ganzhi

    _, year_branch = year_to_ganzhi(year)
    year_branch_num = DIZHI_NUMBER[year_branch]

    return {
        "solar": {
            "year": year, "month": month, "day": day,
            "hour": hour, "minute": minute,
        },
        "lunar": lunar,
        "shichen": shichen,
        "year_branch_number": year_branch_num,
        "lunar_month": lunar["lunar_month"],
        "lunar_day": lunar["lunar_day"],
        "shichen_number": shichen["number"],
    }


# ============================================================
# 日干支推算（六爻纳甲需要）
# ============================================================

def get_day_ganzhi(year: int, month: int, day: int) -> dict:
    """
    推算某公历日期的日干支。

    算法：以已知基准日推算。
    基准：2000年1月1日 = 甲辰日（干序0，支序4 in 60甲子序中为第40位，index=40）
    实际上 2000-01-01 是 庚辰日 (index=16 in 六十甲子)
    更精确：使用 Julian Day Number 方法

    Returns:
        dict: {
            "tiangan": str,   # 天干
            "dizhi": str,     # 地支
            "ganzhi": str,    # 干支组合
            "tiangan_idx": int,
            "dizhi_idx": int,
        }
    """
    from .data_tables import TIANGAN, DIZHI

    # 使用 Julian Day Number 计算
    # 公式: JDN = 367*Y - INT(7*(Y+INT((M+9)/12))/4) + INT(275*M/9) + D + 1721013.5
    # 简化：直接用 datetime 计算与基准日的差
    from datetime import date

    # 基准：1900年1月1日 = 甲子日 (在某些历法系统中)
    # 实际上需要一个精确的已知基准
    # 已知: 2024年1月1日 = 甲子日（六十甲子第0位, 天干序0甲, 地支序0子）
    # 来源：万年历网站交叉验证

    base_date = date(2024, 1, 1)
    base_tiangan_idx = 0   # 甲
    base_dizhi_idx = 0     # 子

    target_date = date(year, month, day)
    delta_days = (target_date - base_date).days

    tiangan_idx = (base_tiangan_idx + delta_days) % 10
    dizhi_idx = (base_dizhi_idx + delta_days) % 12

    return {
        "tiangan": TIANGAN[tiangan_idx],
        "dizhi": DIZHI[dizhi_idx],
        "ganzhi": f"{TIANGAN[tiangan_idx]}{DIZHI[dizhi_idx]}",
        "tiangan_idx": tiangan_idx,
        "dizhi_idx": dizhi_idx,
    }


def get_month_dizhi(year: int, month: int, day: int) -> str:
    """
    获取农历月建的地支。

    月建以节气为界：
    - 寅月（正月）: 立春后
    - 卯月（二月）: 惊蛰后
    - ...以此类推

    简化处理：基于农历月份直接映射。
    精确处理需要节气数据（v2.1 可优化）。

    Returns:
        str: 月建地支
    """
    lunar = solar_to_lunar(year, month, day)
    lunar_month = lunar["lunar_month"]

    # 农历月→月建地支：正月=寅, 二月=卯, ..., 十二月=丑
    month_dizhi_map = {
        1: "寅", 2: "卯", 3: "辰", 4: "巳",
        5: "午", 6: "未", 7: "申", 8: "酉",
        9: "戌", 10: "亥", 11: "子", 12: "丑",
    }

    return month_dizhi_map.get(lunar_month, "寅")


def get_liuyao_time_params(
    year: int, month: int, day: int,
    hour: int, minute: int = 0
) -> dict:
    """
    获取六爻排盘所需的完整时间参数。
    在梅花易数参数基础上，增加日干支和月建。

    Returns:
        dict: 包含梅花参数 + day_ganzhi + month_dizhi
    """
    base_params = get_divination_time_params(year, month, day, hour, minute)

    day_gz = get_day_ganzhi(year, month, day)
    month_dz = get_month_dizhi(year, month, day)

    base_params["day_ganzhi"] = day_gz
    base_params["month_dizhi"] = month_dz

    return base_params
