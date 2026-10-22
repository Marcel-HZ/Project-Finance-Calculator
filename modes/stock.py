"""模式 6：股票估值（零增长、固定增长、非固定增长、时间加权收益率）"""
import math
from utils import get_value, get_float, get_int, get_rate


# ============================================================
#  零增长：V = D / r
# ============================================================

def solve_zero_growth(V, D, r):
    """零增长股票估值：V = D / r"""
    values = {"V": V, "D": D, "r": r}
    steps = []

    if values["V"] is None and values["D"] is not None and values["r"] is not None:
        if values["r"] == 0:
            return values, steps, False, ["r（r=0 不能做分母）"]
        values["V"] = values["D"] / values["r"]
        steps.append(f"V = D / r = {values['D']} / {values['r']} = {values['V']:.6f}")

    if values["D"] is None and values["V"] is not None and values["r"] is not None:
        values["D"] = values["V"] * values["r"]
        steps.append(f"D = V × r = {values['V']} × {values['r']} = {values['D']:.6f}")

    if values["r"] is None and values["V"] is not None and values["D"] is not None:
        if values["V"] == 0:
            return values, steps, False, ["V（V=0 不能做分母）"]
        values["r"] = values["D"] / values["V"]
        steps.append(f"r = D / V = {values['D']} / {values['V']} = {values['r']:.6f}")

    remaining = [k for k, v in values.items() if v is None]
    if remaining:
        return values, steps, False, remaining
    return values, steps, True, []


# ============================================================
#  固定增长：V = D1 / (r - g)
# ============================================================

def solve_constant_growth(V, D1, r, g):
    """固定增长股票估值（Gordon 模型）：V = D1 / (r - g)，要求 r > g"""
    values = {"V": V, "D1": D1, "r": r, "g": g}
    steps = []

    if values["V"] is None and values["D1"] is not None \
            and values["r"] is not None and values["g"] is not None:
        if values["r"] <= values["g"]:
            return values, steps, False, ["r ≤ g（固定增长模型要求 r > g，否则 V → ∞）"]
        values["V"] = values["D1"] / (values["r"] - values["g"])
        steps.append(
            f"V = D1 / (r - g) = {values['D1']} / "
            f"({values['r']} - {values['g']}) = {values['V']:.6f}"
        )

    if values["D1"] is None and values["V"] is not None \
            and values["r"] is not None and values["g"] is not None:
        values["D1"] = values["V"] * (values["r"] - values["g"])
        steps.append(
            f"D1 = V × (r - g) = {values['V']} × "
            f"({values['r']} - {values['g']}) = {values['D1']:.6f}"
        )

    if values["r"] is None and values["V"] is not None \
            and values["D1"] is not None and values["g"] is not None:
        if values["V"] == 0:
            return values, steps, False, ["V（V=0 不能做分母）"]
        values["r"] = values["D1"] / values["V"] + values["g"]
        steps.append(
            f"r = D1 / V + g = {values['D1']} / {values['V']} + "
            f"{values['g']} = {values['r']:.6f}"
        )

    if values["g"] is None and values["V"] is not None \
            and values["D1"] is not None and values["r"] is not None:
        if values["V"] == 0:
            return values, steps, False, ["V（V=0 不能做分母）"]
        values["g"] = values["r"] - values["D1"] / values["V"]
        steps.append(
            f"g = r - D1 / V = {values['r']} - {values['D1']} / "
            f"{values['V']} = {values['g']:.6f}"
        )

    remaining = [k for k, v in values.items() if v is None]
    if remaining:
        return values, steps, False, remaining
    return values, steps, True, []


# ============================================================
#  非固定增长（两阶段）
# ============================================================

def calc_nonconstant_value(dividends, r, g):
    """非固定增长股票估值，返回 (V, PV_stage1, PV_stage2, D_{n+1})"""
    n = len(dividends)
    pv_stage1 = sum(d / (1 + r) ** t for t, d in enumerate(dividends, start=1))
    d_next = dividends[-1] * (1 + g)

    if r <= g:
        return None, pv_stage1, None, d_next
    terminal_value = d_next / (r - g)
    pv_stage2 = terminal_value / (1 + r) ** n

    return pv_stage1 + pv_stage2, pv_stage1, pv_stage2, d_next


def solve_nonconstant(dividends, r, g, V):
    """非固定增长求解"""
    values = {"dividends": dividends, "r": r, "g": g, "V": V}
    steps = []

    if any(d is None for d in dividends):
        return values, steps, False, ["股利序列中有未知（当前仅支持求 V）"]

    if values["V"] is None and values["r"] is not None and values["g"] is not None:
        if values["r"] <= values["g"]:
            return values, steps, False, ["r ≤ g（永续增长阶段要求 r > g）"]
        v, pv1, pv2, d_next = calc_nonconstant_value(
            values["dividends"], values["r"], values["g"]
        )
        values["V"] = v
        steps.append(f"D_{{n+1}} = D_n × (1+g) = {dividends[-1]} × (1+{g}) = {d_next:.6f}")
        steps.append(f"第一阶段现值 PV1 = Σ Dt/(1+r)^t = {pv1:.6f}")
        steps.append(f"第二阶段现值 PV2 = D_{{n+1}} / [(r-g)(1+r)^n] = {pv2:.6f}")
        steps.append(f"V = PV1 + PV2 = {v:.6f}")
        return values, steps, True, []

    if values["r"] is None and values["V"] is not None and values["g"] is not None:
        def f(r):
            v, _, _, _ = calc_nonconstant_value(values["dividends"], r, values["g"])
            if v is None:
                return float("inf")
            return v - values["V"]

        lo, hi = values["g"] + 1e-6, 10.0
        f_lo, f_hi = f(lo), f(hi)
        if f_lo * f_hi > 0:
            return values, steps, False, ["在合理 r 范围内找不到使 V = 目标值的 r"]
        for _ in range(200):
            mid = (lo + hi) / 2
            f_mid = f(mid)
            if f_lo * f_mid <= 0:
                hi = mid
                f_hi = f_mid
            else:
                lo = mid
                f_lo = f_mid
        values["r"] = (lo + hi) / 2
        steps.append(f"r 由二分法求解：r = {values['r']:.6f}  （即 {values['r']*100:.4f}%）")
        return values, steps, True, []

    remaining = [k for k, v in values.items() if v is None]
    if remaining:
        return values, steps, False, remaining
    return values, steps, True, []


# ============================================================
#  时间加权收益率（价格 + 股利）
# ============================================================

def calc_time_weighted_returns(prices, dividends, initial_price):
    """
    时间加权收益率（TWR）的四种口径。
    - prices: 各期期末价格列表
    - dividends: 各期股利列表（与 prices 对应）
    - initial_price: 第 0 期价格

    返回 dict：
        {
            "returns": 逐期百分比收益率,
            "log_returns": 逐期对数收益率,
            "arith_pct": 算术平均（百分比）,
            "arith_log_raw": 算术平均（对数，原值，不转回百分比）,
            "arith_log_pct": 算术平均（对数，转回百分比）,
            "geo": 几何平均收益率（百分比）,
            "irr": 内部收益率（基于完整现金流）,
            "cashflows": IRR 使用的完整现金流序列,
        }
    """
    if len(prices) != len(dividends):
        return None, "价格与股利数量不一致。"
    if len(prices) == 0:
        return None, "数据为空。"

    returns = []
    log_returns = []
    prev = initial_price
    for p, d in zip(prices, dividends):
        r = (p - prev + d) / prev
        returns.append(r)
        log_returns.append(math.log(1 + r))
        prev = p

    n = len(returns)

    # 1. 算术平均（百分比）
    arith_pct = sum(returns) / n

    # 2. 算术平均（对数，原值）
    arith_log_raw = sum(log_returns) / n

    # 3. 算术平均（对数，转回百分比）——与几何平均等价
    arith_log_pct = math.exp(arith_log_raw) - 1

    # 4. 几何平均收益率
    prod = 1.0
    for r in returns:
        prod *= (1 + r)
    geo = prod ** (1 / n) - 1

    # 5. 内部收益率 IRR
    # 正确现金流：第 0 期 -initial_price，
    # 中间期只有股利，最后一期 = 股利 + 卖出价格
    full_cashflows = [-initial_price]
    for t, (p, d) in enumerate(zip(prices, dividends), start=1):
        if t == len(prices):
            full_cashflows.append(d + p)
        else:
            full_cashflows.append(d)

    def npv_at(r):
        return sum(cf / (1 + r) ** t for t, cf in enumerate(full_cashflows))

    lo, hi = -0.9999, 10.0
    f_lo, f_hi = npv_at(lo), npv_at(hi)
    irr = None
    if f_lo * f_hi <= 0:
        for _ in range(200):
            mid = (lo + hi) / 2
            f_mid = npv_at(mid)
            if f_lo * f_mid <= 0:
                hi = mid
                f_hi = f_mid
            else:
                lo = mid
                f_lo = f_mid
        irr = (lo + hi) / 2

    return {
        "returns": returns,
        "log_returns": log_returns,
        "arith_pct": arith_pct,
        "arith_log_raw": arith_log_raw,
        "arith_log_pct": arith_log_pct,
        "geo": geo,
        "irr": irr,
        "cashflows": full_cashflows,
    }, None


# ============================================================
#  交互式运行
# ============================================================

def run():
    """交互式运行股票估值模式"""
    print("股票估值模式")
    print("请选择估值情形：")
    print("  1 - 零增长（永续年金）：V = D / r")
    print("  2 - 固定增长（Gordon）：V = D1 / (r - g)")
    print("  3 - 非固定增长（两阶段）：V = Σ Dt/(1+r)^t + D_{n+1}/((r-g)(1+r)^n)")
    print("  4 - 时间加权收益率（价格 + 股利）")

    while True:
        sub = input("请输入 1-4：").strip()
        if sub in ("1", "2", "3", "4"):
            break
        print("输入无效，请输入 1-4。")

    print()

    # ---------- 选项 1：零增长 ----------
    if sub == "1":
        print("零增长股票估值：V = D / r")
        print("未知的请输入“未知”。")
        print()

        V = get_value("V", "股票价值", is_rate=False)
        D = get_value("D", "每期固定股利", is_rate=False)
        r = get_value("r", "必要收益率", is_rate=True)

        values, steps, success, remaining = solve_zero_growth(V, D, r)

        print()
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

        print("=" * 60)
        print("零增长股票估值结果：")
        print(f"  股票价值 V = {values['V']:.6f}")
        print(f"  每期股利 D = {values['D']:.6f}")
        print(f"  必要收益率 r = {values['r']:.6f}  （即 {values['r']*100:.4f}%）")
        print("=" * 60)
        return

    # ---------- 选项 2：固定增长 ----------
    if sub == "2":
        print("固定增长股票估值（Gordon 模型）：V = D1 / (r - g)")
        print("要求 r > g，否则 V → ∞。")
        print("未知的请输入“未知”。")
        print()

        V = get_value("V", "股票价值", is_rate=False)
        D1 = get_value("D1", "下一期股利（D1）", is_rate=False)
        r = get_value("r", "必要收益率", is_rate=True)
        g = get_value("g", "股利永续增长率", is_rate=True)

        values, steps, success, remaining = solve_constant_growth(V, D1, r, g)

        print()
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

        print("=" * 60)
        print("固定增长股票估值结果：")
        print(f"  股票价值 V = {values['V']:.6f}")
        print(f"  下一期股利 D1 = {values['D1']:.6f}")
        print(f"  必要收益率 r = {values['r']:.6f}  （即 {values['r']*100:.4f}%）")
        print(f"  永续增长率 g = {values['g']:.6f}  （即 {values['g']*100:.4f}%）")
        print("=" * 60)
        return

    # ---------- 选项 3：非固定增长 ----------
    if sub == "3":
        print("非固定增长股票估值（两阶段）")
        print("第一阶段：D1..Dn 按给定序列；第二阶段：D_{n+1} 起永续增长 g。")
        print()

        raw = input("请输入非固定增长阶段的股利序列 D1..Dn（逗号分隔）：").strip()
        parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
        try:
            dividends = [float(p) for p in parts]
        except ValueError:
            print("输入无效，请用逗号分隔数字。")
            return

        if len(dividends) < 1:
            print("至少输入一期股利。")
            return

        print()
        r = get_value("r", "必要收益率", is_rate=True)
        g = get_value("g", "第二阶段永续增长率", is_rate=True)
        V = get_value("V", "股票价值（若未知请输入未知）", is_rate=False)

        values, steps, success, remaining = solve_nonconstant(dividends, r, g, V)

        print()
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

        print("=" * 60)
        print("非固定增长股票估值结果：")
        print(f"  非固定增长阶段股利：{dividends}")
        print(f"  必要收益率 r = {values['r']:.6f}  （即 {values['r']*100:.4f}%）")
        print(f"  永续增长率 g = {values['g']:.6f}  （即 {values['g']*100:.4f}%）")
        print(f"  股票价值 V = {values['V']:.6f}")
        print("=" * 60)
        return

    # ---------- 选项 4：时间加权收益率 ----------
    if sub == "4":
        print("时间加权收益率（TWR）：从价格和股利计算逐期收益率")
        print()
        raw_p = input("请输入各期期末价格（逗号分隔）：").strip()
        parts_p = [p.strip() for p in raw_p.replace("，", ",").split(",") if p.strip()]
        try:
            prices = [float(p) for p in parts_p]
        except ValueError:
            print("价格输入无效。")
            return

        raw_d = input("请输入各期股利（逗号分隔，与价格对应）：").strip()
        parts_d = [p.strip() for p in raw_d.replace("，", ",").split(",") if p.strip()]
        try:
            dividends = [float(p) for p in parts_d]
        except ValueError:
            print("股利输入无效。")
            return

        initial_price = get_float("请输入第 0 期价格（买入价）：")

        result, err = calc_time_weighted_returns(prices, dividends, initial_price)
        print("\n" + "-" * 60)
        if err:
            print(err)
            print("-" * 60)
            return

        print("逐期收益率：")
        print(f"{'期数':<6}{'百分比收益率':<16}{'对数收益率':<16}")
        print("-" * 40)
        for t, (r, lr) in enumerate(zip(result["returns"], result["log_returns"]), start=1):
            print(f"{t:<6}{r*100:+.4f}%        {lr*100:+.4f}%")
        print("-" * 40)
        print()
        print("四种收益率：")
        print(f"  1. 算术平均（百分比）        = {result['arith_pct']:.6f}  "
              f"（即 {result['arith_pct']*100:.4f}%）")
        print(f"     说明：单期收益率不宜累加、不宜算术平均，仅作描述性统计。")
        print()
        print(f"  2. 算术平均（对数，原值）    = {result['arith_log_raw']:.6f}")
        print(f"     说明：可直接累加、求平均；假设期间现金流按以后各期的对数利率再投资。")
        print()
        print(f"  3. 算术平均（对数，转百分比）= {result['arith_log_pct']:.6f}  "
              f"（即 {result['arith_log_pct']*100:.4f}%）")
        print(f"     说明：与几何平均等价。")
        print()
        print(f"  4. 几何平均收益率            = {result['geo']:.6f}  "
              f"（即 {result['geo']*100:.4f}%）")
        print(f"     说明：复利收益率的特殊形式；假设期间现金流按以后各期的真实利率再投资。")
        print()
        if result["irr"] is not None:
            print(f"  5. 内部收益率 IRR            = {result['irr']:.6f}  "
                  f"（即 {result['irr']*100:.4f}%）")
            print(f"     说明：复利收益率的特殊形式；假设期间现金流按 IRR 再投资。")
            print(f"     IRR 使用的现金流序列：{result['cashflows']}")
        else:
            print("  5. 内部收益率 IRR：无解（现金流可能全部同号）")
        print("-" * 60)
        return


if __name__ == "__main__":
    run()