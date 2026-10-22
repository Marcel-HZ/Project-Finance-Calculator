"""模式 4：普通年金（后付年金）"""
import math
from utils import get_value


def annuity_fv(A, i, n):
    """普通年金终值：F = A × [((1+i)^n - 1) / i]"""
    if i == 0:
        return A * n
    return A * ((1 + i) ** n - 1) / i


def annuity_pv(A, i, n):
    """普通年金现值：P = A × [1 - (1+i)^(-n)] / i"""
    if i == 0:
        return A * n
    return A * (1 - (1 + i) ** (-n)) / i


def solve_annuity_i(target, A, n, fixed_value):
    """
    数值求解普通年金的利率 i（二分法）。
    - target: 'F' 用终值公式，'P' 用现值公式
    """
    def func(i):
        if target == "F":
            return annuity_fv(A, i, n) - fixed_value
        else:
            return annuity_pv(A, i, n) - fixed_value

    lo, hi = -0.9999, 10.0
    f_lo, f_hi = func(lo), func(hi)
    if f_lo * f_hi > 0:
        return None, "在合理利率范围内找不到满足条件的 i。"

    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = func(mid)
        if f_lo * f_mid <= 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid

    return (lo + hi) / 2, None


def solve_annuity_mode(mode, A, i, n, F, P):
    """
    普通年金模式迭代求解。
    - mode: 'FV' 终值公式；'PV' 现值公式
    """
    if mode == "FV":
        values = {"A": A, "i": i, "n": n, "F": F}
    else:
        values = {"A": A, "i": i, "n": n, "P": P}

    steps = []
    MAX_ITER = 10
    for _ in range(MAX_ITER):
        progress = False

        # 求终值 F 或现值 P
        if mode == "FV" and values["F"] is None:
            if values["A"] is not None and values["i"] is not None and values["n"] is not None:
                f_val = annuity_fv(values["A"], values["i"], values["n"])
                values["F"] = f_val
                if values["i"] == 0:
                    steps.append(
                        f"F = A × n = {values['A']} × {values['n']} = {f_val:.6f}（i = 0 特例）"
                    )
                else:
                    steps.append(
                        f"F = A × [((1+i)^n - 1) / i] = {values['A']} × "
                        f"[((1+{values['i']})^{values['n']} - 1) / {values['i']}] "
                        f"= {f_val:.6f}"
                    )
                progress = True

        if mode == "PV" and values["P"] is None:
            if values["A"] is not None and values["i"] is not None and values["n"] is not None:
                p_val = annuity_pv(values["A"], values["i"], values["n"])
                values["P"] = p_val
                if values["i"] == 0:
                    steps.append(
                        f"P = A × n = {values['A']} × {values['n']} = {p_val:.6f}（i = 0 特例）"
                    )
                else:
                    steps.append(
                        f"P = A × [1 - (1+i)^(-n)] / i = {values['A']} × "
                        f"[1 - (1+{values['i']})^(-{values['n']})] / {values['i']} "
                        f"= {p_val:.6f}"
                    )
                progress = True

        # 求年金 A
        if values["A"] is None:
            if mode == "FV" and values["F"] is not None \
                    and values["i"] is not None and values["n"] is not None:
                if values["i"] == 0:
                    a_val = values["F"] / values["n"]
                    values["A"] = a_val
                    steps.append(f"A = F / n = {values['F']} / {values['n']} = {a_val:.6f}（i = 0 特例）")
                    progress = True
                else:
                    denom = (1 + values["i"]) ** values["n"] - 1
                    if denom != 0:
                        a_val = values["F"] * values["i"] / denom
                        values["A"] = a_val
                        steps.append(
                            f"A = F × i / [(1+i)^n - 1] = {values['F']} × {values['i']} / "
                            f"[(1+{values['i']})^{values['n']} - 1] = {a_val:.6f}"
                        )
                        progress = True

            if mode == "PV" and values["P"] is not None \
                    and values["i"] is not None and values["n"] is not None:
                if values["i"] == 0:
                    a_val = values["P"] / values["n"]
                    values["A"] = a_val
                    steps.append(f"A = P / n = {values['P']} / {values['n']} = {a_val:.6f}（i = 0 特例）")
                    progress = True
                else:
                    denom = 1 - (1 + values["i"]) ** (-values["n"])
                    if denom != 0:
                        a_val = values["P"] * values["i"] / denom
                        values["A"] = a_val
                        steps.append(
                            f"A = P × i / [1 - (1+i)^(-n)] = {values['P']} × {values['i']} / "
                            f"[1 - (1+{values['i']})^(-{values['n']})] = {a_val:.6f}"
                        )
                        progress = True

        # 求期数 n
        if values["n"] is None and values["A"] is not None and values["i"] is not None:
            if values["i"] == 0:
                if mode == "FV" and values["F"] is not None:
                    n_val = values["F"] / values["A"]
                    values["n"] = n_val
                    steps.append(f"n = F / A = {values['F']} / {values['A']} = {n_val:.6f}（i = 0 特例）")
                    progress = True
                elif mode == "PV" and values["P"] is not None:
                    n_val = values["P"] / values["A"]
                    values["n"] = n_val
                    steps.append(f"n = P / A = {values['P']} / {values['A']} = {n_val:.6f}（i = 0 特例）")
                    progress = True
            else:
                if mode == "FV" and values["F"] is not None:
                    inner = 1 + values["F"] * values["i"] / values["A"]
                    if inner > 0 and (1 + values["i"]) > 0:
                        n_val = math.log(inner) / math.log(1 + values["i"])
                        values["n"] = n_val
                        steps.append(
                            f"n = ln(1 + F·i/A) / ln(1+i) = "
                            f"ln(1 + {values['F']}×{values['i']}/{values['A']}) / "
                            f"ln(1+{values['i']}) = {n_val:.6f}"
                        )
                        progress = True
                elif mode == "PV" and values["P"] is not None:
                    inner = 1 - values["P"] * values["i"] / values["A"]
                    if inner > 0 and (1 + values["i"]) > 0:
                        n_val = -math.log(inner) / math.log(1 + values["i"])
                        values["n"] = n_val
                        steps.append(
                            f"n = -ln(1 - P·i/A) / ln(1+i) = "
                            f"-ln(1 - {values['P']}×{values['i']}/{values['A']}) / "
                            f"ln(1+{values['i']}) = {n_val:.6f}"
                        )
                        progress = True

        # 求利率 i（数值法）
        if values["i"] is None and values["A"] is not None and values["n"] is not None:
            fixed_value = values["F"] if mode == "FV" else values["P"]
            if fixed_value is not None:
                i_val, err = solve_annuity_i(
                    "F" if mode == "FV" else "P",
                    values["A"], values["n"], fixed_value
                )
                if i_val is not None:
                    values["i"] = i_val
                    steps.append(
                        f"i 由数值法求解（二分法）：i = {i_val:.6f}  "
                        f"（即 {i_val*100:.4f}%）"
                    )
                    progress = True
                else:
                    # 关键修复：直接返回错误，不输出 nan
                    msg = f"无法计算 i：{err}"
                    if steps:
                        msg += "\n\n已完成的步骤：\n" + "\n".join(f"  {s}" for s in steps)
                    return msg, False

        if not progress:
            break

    remaining = [k for k, v in values.items() if v is None]

    if remaining:
        msg = f"未知变量过多（{', '.join(remaining)}），无法计算。"
        if steps:
            msg += "\n\n已完成的步骤：\n" + "\n".join(f"  {s}" for s in steps)
        return msg, False

    output = "求解过程：\n" + "\n".join(f"  {s}" for s in steps)
    output += "\n\n最终结果：\n"
    for k, v in values.items():
        if k == "i":
            output += f"  {k:4s} = {v:.6f}  （即 {v*100:.4f}%）\n"
        else:
            output += f"  {k:4s} = {v:.6f}\n"
    return output, True


def run():
    """交互式运行普通年金模式"""
    print("普通年金模式（后付年金）")
    print("请选择年金计算类型：")
    print("  1 - 终值型：F = A × [((1+i)^n - 1) / i]")
    print("  2 - 现值型：P = A × [1 - (1+i)^(-n)] / i")
    while True:
        sub = input("请输入 1 或 2：").strip()
        if sub in ("1", "2"):
            break
        print("输入无效，请输入 1 或 2。")

    print("\n提示：")
    print("  A = 年金（每期期末等额收付的金额）")
    print("  i = 每期利率，可输入 0.05 或 5%")
    print("  n = 期数")
    print("  未知的请输入“未知”。\n")

    A = get_value("A", "年金（每期金额）")
    i = get_value("i", "每期利率，可输入 0.05 或 5%", is_rate=True)
    n = get_value("n", "期数")

    if sub == "1":
        F = get_value("F", "年金终值")
        P = None
        mode_str = "FV"
    else:
        P = get_value("P", "年金现值")
        F = None
        mode_str = "PV"

    print("\n" + "-" * 60)
    result, _ = solve_annuity_mode(mode_str, A, i, n, F, P)
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    run()