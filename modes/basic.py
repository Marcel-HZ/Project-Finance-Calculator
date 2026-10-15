"""模式 1：基础复利 / 单利

复利：F = P × (1 + i)^n
单利：F = P × (1 + i × n)
"""
import math
from utils import get_value


# ============================================================
#  复利
# ============================================================

def solve_i_compound(F, P, n):
    """复利解 i，方程为 (1+i)^n = F/P，正确处理偶次方的双根"""
    if P == 0:
        return "无法计算 i：因为 P = 0，不能做分母。"

    ratio = F / P
    solutions = []

    if n % 2 == 1:
        if ratio >= 0:
            x = ratio ** (1 / n)
        else:
            x = -((-ratio) ** (1 / n))
        solutions.append(x)
    else:
        if ratio < 0:
            return "无法计算 i：F/P 为负数且 n 为偶数，实数范围内无解。"
        x_pos = ratio ** (1 / n)
        x_neg = -x_pos
        solutions.append(x_pos)
        if x_neg != x_pos:
            solutions.append(x_neg)

    i_values = [x - 1 for x in solutions]

    lines = [f"方程：(1 + i)^{n} = F / P = {F} / {P} = {ratio}"]
    lines.append(f"求解：1 + i = ±({ratio})^(1/{n})")
    lines.append("结果：")
    for idx, iv in enumerate(i_values, 1):
        lines.append(f"  解 {idx}: i = {iv:.6f}  （即 {iv * 100:.4f}%）")

    if len(i_values) > 1:
        lines.append("")
        lines.append("说明：n 为偶数时，方程有两个数学解。")
        lines.append("      其中使 i < -100% 的解在金融上通常无意义。")

    valid = [iv for iv in i_values if iv > -1]
    if valid:
        lines.append("")
        lines.append("金融上有意义的解（i > -100%）：")
        for iv in valid:
            lines.append(f"  i = {iv:.6f}  （即 {iv * 100:.4f}%）")

    return "\n".join(lines)


def solve_compound(F, P, i, n):
    """复利模式求解，返回 (结果字符串, 是否成功)"""
    unknowns = [name for name, val in
                [("F", F), ("P", P), ("i", i), ("n", n)] if val is None]

    if len(unknowns) == 0:
        return "所有变量均已知，无需计算。", True
    if len(unknowns) > 1:
        return f"未知变量过多（{', '.join(unknowns)}），无法计算。", False

    target = unknowns[0]

    try:
        if target == "F":
            result = P * (1 + i) ** n
            return (f"F = P × (1 + i)^n = {P} × (1 + {i})^{n} "
                    f"= {result:.6f}", True)

        elif target == "P":
            if (1 + i) == 0:
                return "无法计算 P：因为 (1 + i) = 0，不能做分母。", False
            result = F / ((1 + i) ** n)
            return (f"P = F / (1 + i)^n = {F} / (1 + {i})^{n} "
                    f"= {result:.6f}", True)

        elif target == "i":
            return solve_i_compound(F, P, n), True

        elif target == "n":
            if P == 0:
                return "无法计算 n：因为 P = 0，不能做分母。", False
            if F / P <= 0:
                return "无法计算 n：F/P 必须为正数才能取对数。", False
            if (1 + i) <= 0:
                return "无法计算 n：1 + i 必须为正数才能取对数。", False
            result = math.log(F / P) / math.log(1 + i)
            return (f"n = ln(F/P) / ln(1 + i) = "
                    f"ln({F}/{P}) / ln(1 + {i}) = {result:.6f}", True)

    except Exception as e:
        return f"计算过程中出现错误：{e}", False


# ============================================================
#  单利
# ============================================================

def solve_simple(F, P, i, n):
    """
    单利模式求解：F = P × (1 + i × n)
    四种变形：
        F = P(1 + i·n)
        P = F / (1 + i·n)
        i = (F/P - 1) / n
        n = (F/P - 1) / i
    单利没有双根问题，只有一个解。
    """
    unknowns = [name for name, val in
                [("F", F), ("P", P), ("i", i), ("n", n)] if val is None]

    if len(unknowns) == 0:
        return "所有变量均已知，无需计算。", True
    if len(unknowns) > 1:
        return f"未知变量过多（{', '.join(unknowns)}），无法计算。", False

    target = unknowns[0]

    try:
        if target == "F":
            result = P * (1 + i * n)
            return (f"F = P × (1 + i × n) = {P} × (1 + {i}×{n}) "
                    f"= {result:.6f}", True)

        elif target == "P":
            denom = 1 + i * n
            if denom == 0:
                return "无法计算 P：因为 1 + i×n = 0，不能做分母。", False
            result = F / denom
            return (f"P = F / (1 + i × n) = {F} / (1 + {i}×{n}) "
                    f"= {result:.6f}", True)

        elif target == "i":
            if n == 0:
                return "无法计算 i：因为 n = 0，不能做分母。", False
            result = (F / P - 1) / n
            return (f"i = (F/P - 1) / n = ({F}/{P} - 1) / {n} "
                    f"= {result:.6f}  （即 {result*100:.4f}%）", True)

        elif target == "n":
            if i == 0:
                return "无法计算 n：因为 i = 0，不能做分母。", False
            result = (F / P - 1) / i
            return (f"n = (F/P - 1) / i = ({F}/{P} - 1) / {i} "
                    f"= {result:.6f}", True)

    except Exception as e:
        return f"计算过程中出现错误：{e}", False


# ============================================================
#  交互式运行
# ============================================================

def run():
    """交互式运行基础模式（单利/复利二选一）"""
    print("基础模式")
    print("请选择计算方式：")
    print("  1 - 复利：F = P × (1 + i)^n")
    print("  2 - 单利：F = P × (1 + i × n)")
    while True:
        way = input("请输入 1 或 2：").strip()
        if way in ("1", "2"):
            break
        print("输入无效，请输入 1 或 2。")

    print()
    if way == "1":
        print("复利模式：F = P × (1 + i)^n")
    else:
        print("单利模式：F = P × (1 + i × n)")
    print()

    F = get_value("F", "终值/未来值")
    P = get_value("P", "现值/本金")
    i = get_value("i", "每期利率，可输入 0.05 或 5%", is_rate=True)
    n = get_value("n", "期数")

    print("\n" + "-" * 60)
    if way == "1":
        result, _ = solve_compound(F, P, i, n)
    else:
        result, _ = solve_simple(F, P, i, n)
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    run()