"""模式 5：投资项目评价（NPV、IRR、PI、回收期、AAR、XNPV）"""
import math
from utils import get_float, get_rate, get_cashflows, get_dates


# ============================================================
#  单项指标计算函数
# ============================================================

def calc_aar(net_profits, initial_investment):
    """
    平均收益率 AAR = 年平均净利润 / 初始投资额
    - net_profits: 各年净利润列表
    - initial_investment: 初始投资额（正数）
    返回 (AAR, 错误信息)
    """
    if initial_investment == 0:
        return None, "初始投资为 0，无法计算 AAR。"
    avg = sum(net_profits) / len(net_profits)
    return avg / abs(initial_investment), None


def calc_payback(cashflows, initial_investment):
    """
    回收期（未贴现）。
    - cashflows: 第 1 期起的各期现金流
    - initial_investment: 初始投资额（正数）
    返回 (回收期, 错误信息)
    """
    cum = 0.0
    for t, cf in enumerate(cashflows, start=1):
        prev_cum = cum
        cum += cf
        if cum >= initial_investment:
            if cf == 0:
                return t, f"第 {t} 年现金流为 0，无法插值。"
            frac = (initial_investment - prev_cum) / cf
            return t - 1 + frac, None
    return None, "累计现金流入始终未达到初始投资，无法回收。"


def calc_discounted_payback(cashflows, initial_investment, r):
    """
    贴现回收期。
    - cashflows: 第 1 期起的各期现金流
    - initial_investment: 初始投资额（正数）
    - r: 贴现率
    返回 (贴现回收期, 错误信息)
    """
    cum = 0.0
    for t, cf in enumerate(cashflows, start=1):
        pv = cf / (1 + r) ** t
        prev_cum = cum
        cum += pv
        if cum >= initial_investment:
            if pv == 0:
                return t, f"第 {t} 年贴现现金流为 0，无法插值。"
            frac = (initial_investment - prev_cum) / pv
            return t - 1 + frac, None
    return None, "累计贴现现金流始终未达到初始投资，无法回收。"


def calc_npv(cashflows, initial_investment, r):
    """
    NPV = 各期现金流贴现之和 - |初始投资|
    返回 (NPV, PV)
    """
    pv = sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows, start=1))
    return pv - abs(initial_investment), pv


def calc_irr(cashflows, initial_investment):
    """
    内部收益率：使 NPV = 0 的折现率。
    用二分法在 (-0.9999, 10) 内搜索。
    不需要输入贴现率。
    返回 (IRR, 错误信息)
    """
    def npv_at(r):
        pv = sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows, start=1))
        return pv - abs(initial_investment)

    lo, hi = -0.9999, 10.0
    f_lo, f_hi = npv_at(lo), npv_at(hi)
    if f_lo * f_hi > 0:
        return None, "在合理利率范围内找不到使 NPV = 0 的折现率。"

    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv_at(mid)
        if f_lo * f_mid <= 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid

    return (lo + hi) / 2, None


def calc_xnpv(cashflows, dates, r):
    """
    XNPV：不定期现金流净现值。
    以第一个日期为基准，按 (d_i - d_1).days / 365 年折算。
    返回 (XNPV, 错误信息)
    """
    if len(cashflows) != len(dates):
        return None, "现金流与日期数量不一致。"
    if len(dates) == 0:
        return None, "日期为空。"

    d0 = dates[0]
    npv = 0.0
    for cf, d in zip(cashflows, dates):
        years = (d - d0).days / 365.0
        npv += cf / (1 + r) ** years
    return npv, None


def calc_level_npv(A, n, r, initial_investment):
    """
    等额现金流 NPV = 年金现值 - |初始投资|
    NPV = A × [1 - (1+r)^(-n)] / r - |CF0|
    返回 (NPV, PV)
    """
    if r == 0:
        pv = A * n
    else:
        pv = A * (1 - (1 + r) ** (-n)) / r
    return pv - abs(initial_investment), pv


# ============================================================
#  交互式运行
# ============================================================

def run():
    """交互式运行投资项目评价模式"""
    print("投资项目评价模式")
    print("请选择要计算的指标：")
    print("  1  - 平均收益率 AAR")
    print("  2  - 回收期")
    print("  3  - 贴现回收期")
    print("  4  - 净现值 NPV")
    print("  5  - 盈利指数 PI（NPV / |CF0|）")
    print("  6  - 现值指数 PI（现值 / |CF0|）")
    print("  7  - XNPV（不定期现金流）")
    print("  8  - 内部收益率 IRR（不需要输入贴现率）")
    print("  9  - 全部指标（一次算完）")
    print("  10 - 等额现金流 NPV（年金现值 - 初始投资）")

    while True:
        sub = input("请输入 1-10：").strip()
        if sub in [str(i) for i in range(1, 11)]:
            break
        print("输入无效，请输入 1-10。")

    print()

    # ============================================================
    # 选项 1：AAR（单独处理，需要净利润）
    # ============================================================
    if sub == "1":
        raw = input("请输入各年净利润（逗号分隔）：").strip()
        parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
        profits = [float(p) for p in parts]
        init = get_float("请输入初始投资额：")
        aar, err = calc_aar(profits, init)
        print("\n" + "-" * 60)
        if err:
            print(err)
        else:
            avg = sum(profits) / len(profits)
            print(f"年平均净利润 = {avg:.6f}")
            print(f"AAR = 年平均净利润 / |初始投资| = "
                  f"{avg:.6f} / {abs(init):.6f} = {aar:.6f}  （即 {aar*100:.4f}%）")
        print("-" * 60)
        return

    # ============================================================
    # 选项 7：XNPV（单独处理，需要日期）
    # ============================================================
    if sub == "7":
        cashflows = get_cashflows("请输入各期现金流（逗号分隔）：")
        dates = get_dates("请输入对应日期（YYYY-MM-DD，逗号分隔）：")
        r = get_rate("请输入折现率（如 7.5% 或 0.075）：")
        xnpv, err = calc_xnpv(cashflows, dates, r)
        print("\n" + "-" * 60)
        if err:
            print(err)
        else:
            print(f"XNPV = {xnpv:.6f}")
        print("-" * 60)
        return

    # ============================================================
    # 选项 10：等额现金流 NPV（单独处理）
    # ============================================================
    if sub == "10":
        A = get_float("请输入每年等额现金流 A：")
        n = get_float("请输入经济年限 n：")
        r = get_rate("请输入贴现率（如 7.5% 或 0.075）：")
        init = get_float("请输入初始投资额（正数）：")
        npv, pv = calc_level_npv(A, n, r, init)
        print("\n" + "-" * 60)
        print(f"年金现值 PV = A × [1 - (1+r)^(-n)] / r")
        print(f"            = {A} × [1 - (1+{r})^(-{n})] / {r}")
        print(f"            = {pv:.6f}")
        print(f"初始投资 |CF0| = {abs(init):.6f}")
        print(f"NPV = PV - |CF0| = {npv:.6f}")
        print("-" * 60)
        return

    # ============================================================
    # 其余选项：回收期、贴现回收期、NPV、PI、IRR、全部
    # ============================================================
    cashflows = get_cashflows("请输入第 1 期起的各期现金流（逗号分隔）：")
    init = get_float("请输入初始投资额（正数）：")

    # 只有需要贴现率的指标才询问 r
    # - 2 回收期：不需要
    # - 8 IRR：不需要
    # - 3, 4, 5, 6, 9：需要
    r = None
    if sub in ("3", "4", "5", "6", "9"):
        r = get_rate("请输入必要收益率 / 资本成本率（如 7.5% 或 0.075）：")

    print("\n" + "-" * 60)

    # ---------- 回收期 ----------
    if sub in ("2", "9"):
        pb, err = calc_payback(cashflows, abs(init))
        if err:
            print(f"回收期：{err}")
        else:
            print(f"回收期 = {pb:.6f} 年")

    # ---------- 贴现回收期 ----------
    if sub in ("3", "9"):
        dpb, err = calc_discounted_payback(cashflows, abs(init), r)
        if err:
            print(f"贴现回收期：{err}")
        else:
            print(f"贴现回收期 = {dpb:.6f} 年")

    # ---------- NPV、PI ----------
    if sub in ("4", "5", "6", "9"):
        npv, pv = calc_npv(cashflows, abs(init), r)
        print(f"现金流入现值 PV = {pv:.6f}")
        print(f"初始投资 |CF0| = {abs(init):.6f}")
        print(f"NPV = PV - |CF0| = {npv:.6f}")

        if sub in ("5", "9"):
            pi_npv = npv / abs(init) if init != 0 else None
            if pi_npv is not None:
                print(f"盈利指数 PI = NPV / |CF0| = {pi_npv:.6f}")

        if sub in ("6", "9"):
            pi_pv = pv / abs(init) if init != 0 else None
            if pi_pv is not None:
                print(f"现值指数 PI = PV / |CF0| = {pi_pv:.6f}")

    # ---------- IRR（不需要 r） ----------
    if sub in ("8", "9"):
        irr, err = calc_irr(cashflows, abs(init))
        if err:
            print(f"IRR：{err}")
        else:
            print(f"IRR = {irr:.6f}  （即 {irr*100:.4f}%）")

    print("-" * 60)


# ============================================================
#  直接运行本文件时的入口
# ============================================================

if __name__ == "__main__":
    run()