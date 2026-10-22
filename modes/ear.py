"""模式 2：有效年利率  EAR = (1 + R/M)^M - 1"""
import math
from utils import get_value


def solve_ear_mode(F, P, R, M, EAR, t):
    """EAR 模式迭代求解。变量：F, P, R, M, EAR, t"""
    values = {"F": F, "P": P, "R": R, "M": M, "EAR": EAR, "t": t}
    steps = []

    MAX_ITER = 10
    for _ in range(MAX_ITER):
        progress = False

        # 求 EAR
        if values["EAR"] is None and values["R"] is not None and values["M"] is not None:
            if values["M"] != 0:
                ear = (1 + values["R"] / values["M"]) ** values["M"] - 1
                values["EAR"] = ear
                steps.append(
                    f"EAR = (1 + R/M)^M - 1 = "
                    f"(1 + {values['R']}/{values['M']})^{values['M']} - 1 "
                    f"= {ear:.6f}  （即 {ear*100:.4f}%）"
                )
                progress = True

        # 求 R
        if values["R"] is None and values["EAR"] is not None and values["M"] is not None:
            if values["M"] != 0 and values["EAR"] > -1:
                r = values["M"] * ((1 + values["EAR"]) ** (1 / values["M"]) - 1)
                values["R"] = r
                steps.append(
                    f"R = M × [(1+EAR)^(1/M) - 1] = "
                    f"{values['M']} × [(1+{values['EAR']})^(1/{values['M']}) - 1] "
                    f"= {r:.6f}  （即 {r*100:.4f}%）"
                )
                progress = True

        # 求 F
        if values["F"] is None and values["P"] is not None:
            if values["EAR"] is not None and values["t"] is not None:
                f_val = values["P"] * (1 + values["EAR"]) ** values["t"]
                values["F"] = f_val
                steps.append(
                    f"F = P × (1+EAR)^t = {values['P']} × "
                    f"(1+{values['EAR']})^{values['t']} = {f_val:.6f}"
                )
                progress = True
            elif (values["R"] is not None and values["M"] is not None
                  and values["t"] is not None):
                i = values["R"] / values["M"]
                n = values["M"] * values["t"]
                f_val = values["P"] * (1 + i) ** n
                values["F"] = f_val
                steps.append(
                    f"F = P × (1+R/M)^(Mt) = {values['P']} × "
                    f"(1+{values['R']}/{values['M']})^"
                    f"({values['M']}×{values['t']}) = {f_val:.6f}"
                )
                progress = True

        # 求 P
        if values["P"] is None and values["F"] is not None:
            if values["EAR"] is not None and values["t"] is not None:
                if (1 + values["EAR"]) != 0:
                    p_val = values["F"] / (1 + values["EAR"]) ** values["t"]
                    values["P"] = p_val
                    steps.append(
                        f"P = F / (1+EAR)^t = {values['F']} / "
                        f"(1+{values['EAR']})^{values['t']} = {p_val:.6f}"
                    )
                    progress = True
            elif (values["R"] is not None and values["M"] is not None
                  and values["t"] is not None):
                if (1 + values["R"] / values["M"]) != 0:
                    i = values["R"] / values["M"]
                    n = values["M"] * values["t"]
                    p_val = values["F"] / (1 + i) ** n
                    values["P"] = p_val
                    steps.append(
                        f"P = F / (1+R/M)^(Mt) = {values['F']} / "
                        f"(1+{values['R']}/{values['M']})^"
                        f"({values['M']}×{values['t']}) = {p_val:.6f}"
                    )
                    progress = True

        # 求 t
        if values["t"] is None and values["F"] is not None and values["P"] is not None:
            if values["P"] != 0 and values["F"] / values["P"] > 0:
                if values["EAR"] is not None and (1 + values["EAR"]) > 0:
                    t_val = math.log(values["F"] / values["P"]) / math.log(1 + values["EAR"])
                    values["t"] = t_val
                    steps.append(
                        f"t = ln(F/P) / ln(1+EAR) = "
                        f"ln({values['F']}/{values['P']}) / "
                        f"ln(1+{values['EAR']}) = {t_val:.6f} 年"
                    )
                    progress = True
                elif (values["R"] is not None and values["M"] is not None
                      and (1 + values["R"] / values["M"]) > 0):
                    n_val = math.log(values["F"] / values["P"]) / math.log(1 + values["R"] / values["M"])
                    t_val = n_val / values["M"]
                    values["t"] = t_val
                    steps.append(
                        f"n = ln(F/P) / ln(1+R/M) = {n_val:.6f}，"
                        f"t = n / M = {n_val:.6f} / {values['M']} = {t_val:.6f} 年"
                    )
                    progress = True

        if not progress:
            break

    # ---------- 检查结果 ----------
    # 关键修复：如果 EAR 已知，R 和 M 为 None 是正常的
    if values["EAR"] is not None:
        remaining = [k for k, v in values.items()
                     if v is None and k not in ("R", "M")]
    else:
        remaining = [k for k, v in values.items() if v is None]

    if remaining:
        msg = f"未知变量过多（{', '.join(remaining)}），无法计算。"
        if steps:
            msg += "\n\n已完成的步骤：\n" + "\n".join(f"  {s}" for s in steps)
        return msg, False

    output = "求解过程：\n" + "\n".join(f"  {s}" for s in steps)
    output += "\n\n最终结果：\n"
    for k, v in values.items():
        if v is None:
            continue
        if k in ("R", "EAR"):
            output += f"  {k:4s} = {v:.6f}  （即 {v*100:.4f}%）\n"
        else:
            output += f"  {k:4s} = {v:.6f}\n"
    return output, True


def run():
    """交互式运行 EAR 模式"""
    print("EAR 模式：EAR = (1 + R/M)^M - 1，F = P × (1 + EAR)^t")
    print("提示：")
    print("  R   = 名义年利率，可输入 0.12 或 12%")
    print("  M   = 每年复利次数，例如 12 表示按月复利")
    print("  EAR = 有效年利率，可输入 0.1268 或 12.68%")
    print("  t   = 年数，例如 2 表示 2 年")
    print("  未知的请输入“未知”。\n")

    F   = get_value("F",   "终值/未来值")
    P   = get_value("P",   "现值/本金")
    R   = get_value("R",   "名义年利率，可输入 0.12 或 12%", is_rate=True)
    M   = get_value("M",   "每年复利次数")
    EAR = get_value("EAR", "有效年利率，可输入 0.1268 或 12.68%", is_rate=True)
    t   = get_value("t",   "年数")
    print("\n" + "-" * 60)
    result, _ = solve_ear_mode(F, P, R, M, EAR, t)
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    run()