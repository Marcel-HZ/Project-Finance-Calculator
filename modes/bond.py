"""模式 5：债券分析（静态分析 + 动态分析 + 期望 YTM）"""
import math
from utils import get_value, get_float, get_int, get_rate


# ============================================================
#  核心计算函数
# ============================================================

def calc_bond_value(coupon, face_value, n, y):
    """债券价值 = 利息年金现值 + 面值复利现值"""
    if y == 0:
        pv_coupon = coupon * n
    else:
        pv_coupon = coupon * (1 - (1 + y) ** (-n)) / y
    pv_face = face_value / (1 + y) ** n
    return pv_coupon + pv_face


def solve_y(coupon, face_value, n, price):
    """已知 F、C、n、P，求 y（每期收益率），二分法"""
    def f(y):
        return calc_bond_value(coupon, face_value, n, y) - price

    lo, hi = -0.9999, 10.0
    f_lo, f_hi = f(lo), f(hi)
    if f_lo * f_hi > 0:
        return None, "在合理利率范围内找不到使债券价值 = 市场价格的 y。"

    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = f(mid)
        if f_lo * f_mid <= 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid

    return (lo + hi) / 2, None


def solve_n(coupon, face_value, price, y):
    """已知 F、C、P、y，求 n，二分法"""
    def f(n):
        return calc_bond_value(coupon, face_value, n, y) - price

    lo, hi = 0.001, 1000.0
    f_lo, f_hi = f(lo), f(hi)
    if f_lo * f_hi > 0:
        return None, "在合理期数范围内找不到使债券价值 = 市场价格的 n。"

    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = f(mid)
        if f_lo * f_mid <= 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid

    return (lo + hi) / 2, None


def solve_coupon(face_value, n, price, y):
    """已知 F、n、P、y，求 C"""
    if y == 0:
        return price / n - face_value / n, None
    pv_face = face_value / (1 + y) ** n
    annuity_factor = (1 - (1 + y) ** (-n)) / y
    if annuity_factor == 0:
        return None, "年金因子为 0，无法计算 C。"
    return (price - pv_face) / annuity_factor, None


def solve_face_value(coupon, n, price, y):
    """已知 C、n、P、y，求 F"""
    if y == 0:
        pv_coupon = coupon * n
    else:
        pv_coupon = coupon * (1 - (1 + y) ** (-n)) / y
    return (price - pv_coupon) * (1 + y) ** n, None


def calc_coupon_yield(coupon, face_value):
    """票面收益率 = 每期利息 / 面值"""
    if face_value == 0:
        return None
    return coupon / face_value


def calc_amortized_cost(face_value, coupon, n, initial_cost, effective_rate):
    """摊余成本表"""
    n = int(n)
    table = []
    begin = initial_cost
    for t in range(1, n + 1):
        interest_income = begin * effective_rate
        cash_inflow = coupon
        end = begin + interest_income - cash_inflow
        table.append({
            "period": t,
            "begin": begin,
            "interest_income": interest_income,
            "cash_inflow": cash_inflow,
            "end": end,
        })
        begin = end
    return table


# ---------- 动态分析：久期、凸度、利率敏感性 ----------

def calc_duration_convexity(coupon, face_value, n, y):
    """
    Macaulay 久期、修正久期、凸度。
    y 是每期收益率，n 是总期数。
    """
    n = int(n)
    value = 0.0
    weighted_t = 0.0
    weighted_tt = 0.0

    for t in range(1, n + 1):
        cf = coupon + (face_value if t == n else 0)
        pv = cf / (1 + y) ** t
        value += pv
        weighted_t += t * pv
        weighted_tt += t * (t + 1) * cf / (1 + y) ** (t + 2)

    if value == 0:
        return None, None, None, 0.0

    d_mac = weighted_t / value
    d_mod = d_mac / (1 + y)
    convexity = weighted_tt / value
    return d_mac, d_mod, convexity, value


def calc_rate_sensitivity(coupon, face_value, n, y, d_mod, convexity):
    """利率敏感性对比表"""
    v0 = calc_bond_value(coupon, face_value, n, y)
    results = []
    for pct in [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]:
        dy = pct / 100.0
        v_new = calc_bond_value(coupon, face_value, n, y + dy)
        exact_pct = (v_new - v0) / v0 * 100 if v0 != 0 else 0
        first_order = -d_mod * dy * 100
        second_order = (-d_mod * dy + 0.5 * convexity * dy ** 2) * 100
        results.append({
            "dy_pct": pct,
            "value": v_new,
            "exact_pct": exact_pct,
            "first": first_order,
            "second": second_order,
        })
    return results


# ============================================================
#  统一求解（静态分析）
# ============================================================

def solve_bond(F, C, n, P, y):
    """统一求解债券五变量，返回 (values, steps, success, remaining)"""
    values = {"F": F, "C": C, "n": n, "P": P, "y": y}
    steps = []

    MAX_ITER = 10
    for _ in range(MAX_ITER):
        progress = False

        if values["P"] is None:
            if all(values[k] is not None for k in ("F", "C", "n", "y")):
                p = calc_bond_value(values["C"], values["F"], values["n"], values["y"])
                values["P"] = p
                steps.append(f"P = C × [1-(1+y)^(-n)]/y + F/(1+y)^n = {p:.6f}")
                progress = True

        if values["y"] is None:
            if all(values[k] is not None for k in ("F", "C", "n", "P")):
                y_val, err = solve_y(values["C"], values["F"], values["n"], values["P"])
                if y_val is not None:
                    values["y"] = y_val
                    steps.append(f"y 由二分法求解：y = {y_val:.6f}  （即 {y_val*100:.4f}%）")
                    progress = True

        if values["n"] is None:
            if all(values[k] is not None for k in ("F", "C", "P", "y")):
                n_val, err = solve_n(values["C"], values["F"], values["P"], values["y"])
                if n_val is not None:
                    values["n"] = n_val
                    steps.append(f"n 由二分法求解：n = {n_val:.6f}")
                    progress = True

        if values["C"] is None:
            if all(values[k] is not None for k in ("F", "n", "P", "y")):
                c_val, err = solve_coupon(values["F"], values["n"], values["P"], values["y"])
                if c_val is not None:
                    values["C"] = c_val
                    steps.append(f"C = (P - F/(1+y)^n) / [1-(1+y)^(-n)]/y = {c_val:.6f}")
                    progress = True

        if values["F"] is None:
            if all(values[k] is not None for k in ("C", "n", "P", "y")):
                f_val, err = solve_face_value(values["C"], values["n"], values["P"], values["y"])
                if f_val is not None:
                    values["F"] = f_val
                    steps.append(f"F = (P - C × [1-(1+y)^(-n)]/y) × (1+y)^n = {f_val:.6f}")
                    progress = True

        if not progress:
            break

    remaining = [k for k, v in values.items() if v is None]
    if remaining:
        return values, steps, False, remaining
    return values, steps, True, []


# ============================================================
#  输出辅助
# ============================================================

def print_amortized_table(table):
    """逐行输出摊余成本表"""
    print("-" * 60)
    for row in table:
        print(f"第 {row['period']} 期：")
        print(f"  期初摊余成本 = {row['begin']:.6f}")
        print(f"  利息收入     = {row['interest_income']:.6f}")
        print(f"  现金流入     = {row['cash_inflow']:.6f}")
        print(f"  期末摊余成本 = {row['end']:.6f}")
        print()
    print("-" * 60)


def print_static_results(values):
    """输出静态分析结果"""
    F, C, n, P, y = (values["F"], values["C"], values["n"],
                      values["P"], values["y"])

    print()
    print("=" * 60)
    print("静态分析结果：")
    print(f"  面值 F     = {F:.6f}")
    print(f"  每期利息 C = {C:.6f}")
    print(f"  期数 n     = {n:.6f}")
    print(f"  市场价格 P = {P:.6f}")
    print(f"  每期收益率 y = {y:.6f}  （即 {y*100:.4f}%）")

    cy = calc_coupon_yield(C, F)
    if cy is not None:
        print()
        print(f"票面收益率 CY = {cy:.6f}  （即 {cy*100:.4f}%）")

    if F is not None and P is not None:
        print()
        if abs(P - F) < 1e-6:
            print("债券类型：平价（市场价格 = 面值）")
        elif P > F:
            print("债券类型：溢价（市场价格 > 面值）")
        else:
            print("债券类型：折价（市场价格 < 面值）")

    if all(v is not None for v in (F, C, n, P, y)):
        print()
        print("摊余成本表（实际利率 = y）：")
        table = calc_amortized_cost(F, C, n, P, y)
        print_amortized_table(table)

    print("=" * 60)


def print_dynamic_results_from_basic(F, C, n, y):
    """从基本参数输出动态分析结果"""
    d_mac, d_mod, conv, value = calc_duration_convexity(C, F, n, y)
    if d_mac is None:
        print("无法计算久期与凸度：债券价值为 0。")
        return

    print()
    print("=" * 60)
    print("动态分析结果（从债券基本参数计算）：")
    print(f"  面值 F     = {F:.6f}")
    print(f"  每期利息 C = {C:.6f}")
    print(f"  期数 n     = {n:.6f}")
    print(f"  每期收益率 y = {y:.6f}  （即 {y*100:.4f}%）")
    print(f"  债券价值 V = {value:.6f}")

    print()
    print("久期与凸度：")
    print(f"  Macaulay 久期 = {d_mac:.6f} 年")
    print(f"  修正久期      = {d_mod:.6f}")
    print(f"  凸度          = {conv:.6f}")

    results = calc_rate_sensitivity(C, F, n, y, d_mod, conv)
    print()
    print("收益率变化对债券价值的影响：")
    print("-" * 70)
    print(f"{'Δy':<10}{'精确值V(y+Δy)':<18}{'精确ΔV/V':<14}"
          f"{'一阶近似':<14}{'二阶近似':<14}")
    print("-" * 70)
    for r in results:
        print(f"{r['dy_pct']:+.2f}%    "
              f"{r['value']:<18.6f}"
              f"{r['exact_pct']:+.4f}%      "
              f"{r['first']:+.4f}%      "
              f"{r['second']:+.4f}%")
    print("-" * 70)
    print("说明：")
    print("  精确值：用债券价值公式直接计算")
    print("  一阶近似：-D_mod × Δy")
    print("  二阶近似：-D_mod × Δy + 0.5 × C × (Δy)^2")
    print("  凸度为正时，二阶近似比一阶更接近精确值")
    print("=" * 60)


def print_dynamic_results_from_duration(d_mod, convexity, y, changes_pct):
    """已知修正久期和凸度，输出动态分析结果"""
    print()
    print("=" * 60)
    print("动态分析结果（已知久期和凸度）：")
    print(f"  修正久期 D_mod = {d_mod:.6f}")
    print(f"  凸度 C         = {convexity:.6f}")
    print(f"  当前每期收益率 y = {y:.6f}  （即 {y*100:.4f}%）")
    print()
    print("收益率变化对债券价值变化率的影响：")
    print("-" * 70)
    print(f"{'Δy':<10}{'只考虑久期':<18}{'久期+凸度':<18}")
    print("-" * 70)
    for pct in changes_pct:
        dy = pct / 100.0
        first_order = -d_mod * dy * 100
        second_order = (-d_mod * dy + 0.5 * convexity * dy ** 2) * 100
        print(f"{pct:+.2f}%    "
              f"{first_order:+.4f}%          "
              f"{second_order:+.4f}%")
    print("-" * 70)
    print("说明：")
    print("  只考虑久期：ΔV/V ≈ -D_mod × Δy")
    print("  久期+凸度：ΔV/V ≈ -D_mod × Δy + 0.5 × C × (Δy)^2")
    print("=" * 60)


# ============================================================
#  交互式运行
# ============================================================

def run():
    """交互式运行债券分析模式"""
    print("债券分析模式")
    print("请选择：")
    print("  1 - 静态分析（F、C、n、P、y 五变量，未知填“未知”）")
    print("  2 - 动态分析（久期、凸度、利率敏感性）")
    print("  3 - 期望 YTM（考虑违约概率）")

    while True:
        sub = input("请输入 1-3：").strip()
        if sub in ("1", "2", "3"):
            break
        print("输入无效，请输入 1-3。")

    print()

    # ---------- 选项 1：静态分析 ----------
    if sub == "1":
        print("请输入债券五变量（未知的请输入“未知”）：")
        print("  F = 面值")
        print("  C = 每期票面利息")
        print("  n = 剩余期数")
        print("  P = 市场价格（债券价值）")
        print("  y = 每期收益率（与付息频率一致；若每年付息一次，则 y = YTM）")
        print()

        F = get_value("F", "面值", is_rate=False)
        C = get_value("C", "每期票面利息", is_rate=False)
        n = get_value("n", "剩余期数", is_rate=False)
        P = get_value("P", "市场价格", is_rate=False)
        y = get_value("y", "每期收益率", is_rate=True)

        print()
        values, steps, success, remaining = solve_bond(F, C, n, P, y)

        if steps:
            print("求解过程：")
            for s in steps:
                print(f"  {s}")
            print()

        if not success:
            print("=" * 60)
            print(f"无法完成求解，缺少：{', '.join(remaining)}")
            print("=" * 60)
            return

        print_static_results(values)
        return

    # ---------- 选项 2：动态分析 ----------
    if sub == "2":
        print("动态分析：久期、凸度、利率敏感性")
        print("请选择输入方式：")
        print("  1 - 从债券基本参数算（F、C、n、y）")
        print("  2 - 已知修正久期和凸度，直接算价值变化率")

        while True:
            way = input("请输入 1 或 2：").strip()
            if way in ("1", "2"):
                break
            print("输入无效，请输入 1 或 2。")

        print()

        if way == "1":
            F = get_float("请输入面值 F：")
            C = get_float("请输入每期利息 C：")
            n = get_int("请输入剩余期数 n：")
            y = get_rate(
                "请输入每期收益率 y（与付息频率一致；若每年付息一次，则 y = YTM）："
            )
            print_dynamic_results_from_basic(F, C, n, y)
            return

        else:
            d_mod = get_float("请输入修正久期 D_mod：")
            convexity = get_float("请输入凸度 C：")
            y = get_rate("请输入当前每期收益率 y（如 5% 或 0.05）：")

            print()
            print("请输入收益率变化幅度（逗号分隔，单位 %）：")
            print("例如：-1, 0, 1")
            raw = input("变化幅度（%）：").strip()
            parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
            try:
                changes_pct = [float(p) for p in parts]
            except ValueError:
                print("输入无效，请用逗号分隔数字。")
                return

            print_dynamic_results_from_duration(d_mod, convexity, y, changes_pct)
            return

    # ---------- 选项 3：期望 YTM ----------
    if sub == "3":
        print("期望 YTM = 承诺 YTM × 承诺概率 + 违约 YTM × 违约概率")
        print()
        ytm_promise = get_rate("承诺情形下的 YTM（如 9% 或 0.09）：")
        prob_promise = get_float("承诺情形的概率（如 0.95）：")
        ytm_default = get_rate("违约情形下的 YTM（如 -20% 或 -0.20）：")
        prob_default = get_float("违约情形的概率（如 0.05）：")

        total = prob_promise + prob_default
        if abs(total - 1.0) > 1e-6:
            print("\n" + "-" * 60)
            print(f"概率之和必须为 1（当前为 {total}）。")
            print("-" * 60)
            return

        exp_ytm = prob_promise * ytm_promise + prob_default * ytm_default
        print("\n" + "-" * 60)
        print(f"期望 YTM = {prob_promise} × {ytm_promise} + "
              f"{prob_default} × {ytm_default}")
        print(f"         = {exp_ytm:.6f}  （即 {exp_ytm*100:.4f}%）")
        print("-" * 60)
        return


if __name__ == "__main__":
    run()