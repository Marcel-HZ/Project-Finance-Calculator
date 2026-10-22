"""输入辅助函数：支持百分号、'未知'、数字校验。"""


def get_value(name, description, is_rate=False):
    """
    询问用户一个变量的值。
    - 输入“未知”返回 None
    - is_rate=True 时，允许输入如 5% / 12.5% / -3%，自动转成小数
    - is_rate=False 时，只接受普通数字
    """
    while True:
        raw = input(f"请输入 {name}（{description}），如果未知请输入“未知”：").strip()

        if raw in ("未知", "未知数", "不知道", "unknown", "?", ""):
            return None

        if raw.endswith("%"):
            if not is_rate:
                print(f"输入无效：{name} 不是利率，不能使用百分号。")
                continue
            num_str = raw[:-1].strip()
            try:
                return float(num_str) / 100.0
            except ValueError:
                print("输入无效，百分号前必须是数字，例如 5% 或 12.5%。")
                continue

        try:
            val = float(raw)
        except ValueError:
            if is_rate:
                print("输入无效，请输入一个数字、百分数（如 5%）或“未知”。")
            else:
                print("输入无效，请输入一个数字或“未知”。")
            continue

        return val


def get_float(prompt):
    """简单读取一个浮点数，不带百分号。"""
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("输入无效，请输入一个数字。")


def get_rate(prompt):
    """读取一个利率，支持百分号。"""
    while True:
        raw = input(prompt).strip()
        if raw.endswith("%"):
            try:
                return float(raw[:-1].strip()) / 100.0
            except ValueError:
                print("输入无效，百分号前必须是数字。")
                continue
        try:
            return float(raw)
        except ValueError:
            print("输入无效，请输入一个数字或百分数（如 8%）。")


def get_cashflows(prompt):
    """读取逗号分隔的现金流序列。"""
    while True:
        raw = input(prompt).strip()
        parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
        try:
            return [float(p) for p in parts]
        except ValueError:
            print("输入无效，请用逗号分隔数字，例如：-1000, 300, 400, 500")


def get_dates(prompt):
    """读取逗号分隔的日期序列（YYYY-MM-DD）。"""
    from datetime import datetime
    while True:
        raw = input(prompt).strip()
        parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
        try:
            return [datetime.strptime(p, "%Y-%m-%d") for p in parts]
        except ValueError:
            print("输入无效，请用逗号分隔日期，格式 YYYY-MM-DD，例如：2024-01-01, 2024-07-01")

def get_int(prompt):
    """读取一个正整数"""
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw)
            if val <= 0:
                print("请输入正整数。")
                continue
            return val
        except ValueError:
            print("输入无效，请输入一个正整数。")