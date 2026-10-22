"""模式 7：投资项目评价（AAR、回收期、NPV、IRR、MIRR、PI、XNPV）"""
import math
from utils import get_value, get_float, get_rate, get_cashflows, get_dates


# ============================================================
#  输入辅助：完整现金流序列（含第 0 期）
# ============================================================

def get_full_cashflows(prompt="请输入完整现金流序列（第 0 期起，逗号分隔）："):
    """读取完整现金流序列，返回 (full, cf0, future)"""
    while True:
        raw = input(prompt).strip()
        parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
        try:
            full = [float(p) for p in parts]
        except ValueError:
            print("输入无效，请用逗号分隔数字，例如：-100, 5, 15, 30")
            continue

        if len(full) < 2:
            print("请至少输入两期现金流（第 0 期和至少 1 期后续）。")
            continue

        return full, full[0], full[1:]


# ============================================================
#  单项指标计算函数
# ============================================================

def calc_aar(net_profits, initial_investment):
    """
    平均收益率 AAR = 年平均净利润 / 初始投资额
    - net_profits: 各年净利润列表
    - initial_investment: 初始投资额（正数）
    """
    if initial_investment == 0:
        return None, "初始投资为 0，无法计算 AAR。"
    if len(net_profits) == 0:
        return None, "净利润序列为空。"
    avg = sum(net_profits) / len(net_profits)
    return avg / abs(initial_investment), None


def calc_payback(full_cashflows):
    """回收期（未贴现）"""
    cum = 0.0
    for t, cf in enumerate(full_cashflows):
        prev_cum = cum
        cum += cf
        if t == 0:
            continue
        if cum >= 0:
            if cf == 0:
                return t, f"第 {t} 期现金流为 0，无法插值。"
            frac = -prev_cum / cf
            return t - 1 + frac, None
    return None, "累计现金流始终未转正，无法回收。"


def calc_discounted_payback(full_cashflows, r):
    """贴现回收期"""
    cf0 = full_cashflows[0]
    target = abs(cf0)
    cum = 0.0
    for t, cf in enumerate(full_cashflows[1:], start=1):
        pv = cf / (1 + r) ** t
        prev_cum = cum
        cum += pv
        if cum >= target:
            if pv == 0:
                return t, f"第 {t} 期贴现现金流为 0，无法插值。"
            frac = (target - prev_cum) / pv
            return t - 1 + frac, None
    return None, "累计贴现现金流始终未达到初始投资，无法回收。"


def calc_npv(full_cashflows, r):
    """NPV = Σ_{t=0}^{n} CF_t / (1+r)^t，返回 (NPV, PV_future)"""
    npv = sum(cf / (1 + r) ** t for t, cf in enumerate(full_cashflows))
    pv_future = npv - full_cashflows[0]
    return npv, pv_future


def calc_pi(full_cashflows, r):
    """计算两种 PI：盈利指数（NPV型）和现值指数（现值型）"""
    cf0 = full_cashflows[0]
    if cf0 == 0:
        return None, None, "第 0 期现金流为 0，无法计算 PI。"
    npv, pv_future = calc_npv(full_cashflows, r)
    return npv / abs(cf0), pv_future / abs(cf0), None


def count_sign_changes(full_cashflows):
    """统计完整现金流序列的符号变化次数（忽略 0）"""
    signs = [1 if cf > 0 else (-1 if cf < 0 else 0) for cf in full_cashflows]
    signs = [s for s in signs if s != 0]
    changes = 0
    for i in range(1, len(signs)):
        if signs[i] != signs[i - 1]:
            changes += 1
    return changes


def classify_irr(full_cashflows):
    """判断 IRR 是收益率还是成本率"""
    first_nonzero = next((cf for cf in full_cashflows if cf != 0), None)
    if first_nonzero is None:
        return "无现金流"
    if first_nonzero < 0:
        return "投资型（IRR 为收益率）"
    else:
        return "融资型（IRR 为成本率）"


def calc_irr(full_cashflows):
    """内部收益率：使 Σ CF_t / (1+r)^t = 0 的 r"""
    def npv_at(r):
        return sum(cf / (1 + r) ** t for t, cf in enumerate(full_cashflows))

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


def calc_irr_with_diagnosis(full_cashflows):
    """计算 IRR 并给出诊断信息，返回 (IRR, 诊断, 错误)"""
    changes = count_sign_changes(full_cashflows)
    irr_type = classify_irr(full_cashflows)

    diag_lines = []
    diag_lines.append(f"现金流符号变化次数：{changes}")
    diag_lines.append(f"IRR 类型：{irr_type}")

    if changes == 0:
        diag_lines.append("警告：现金流全部同号，不存在 IRR。")
    elif changes == 1:
        diag_lines.append("现金流符号只变号一次，IRR 唯一。")
    else:
        diag_lines.append(f"警告：符号多次变号（{changes} 次），")
        diag_lines.append("      可能存在多个 IRR，也可能没有 IRR。")
        diag_lines.append("      建议使用 MIRR 或 NPV 作为决策依据。")

    irr, err = calc_irr(full_cashflows)
    if err:
        diag_lines.append(f"IRR 求解失败：{err}")
        return None, "\n".join(diag_lines), err

    return irr, "\n".join(diag_lines), None


def calc_mirr(full_cashflows, reinvest_rate, finance_rate):
    """修正内部收益率 MIRR"""
    n = len(full_cashflows) - 1
    if n <= 0:
        return None, 0, 0, "现金流序列长度不足，无法计算 MIRR。"

    fv_positive = sum(
        cf * (1 + reinvest_rate) ** (n - t)
        for t, cf in enumerate(full_cashflows) if cf > 0
    )
    pv_negative = sum(
        cf / (1 + finance_rate) ** t
        for t, cf in enumerate(full_cashflows) if cf < 0
    )

    if pv_negative == 0:
        return None, fv_positive, pv_negative, \
               "负现金流现值为 0，无法计算 MIRR。"

    ratio = fv_positive / abs(pv_negative)
    if ratio < 0:
        return None, fv_positive, pv_negative, \
               "FV / |PV| 为负数，无法计算 MIRR。"

    mirr = ratio ** (1 / n) - 1
    return mirr, fv_positive, pv_negative, None


def calc_xnpv(cashflows, dates, r):
    """XNPV：不定期现金流净现值"""
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


# ============================================================
#  交互式运行
# ============================================================

def run():
    """交互式运行投资项目评价模式"""
    print("投资项目评价模式")
    print("请选择要计算的指标：")
    print("  1  - 平均收益率 AAR（用净利润）")
    print("  2  - 回收期")
    print("  3  - 贴现回收期")
    print("  4  - 净现值 NPV")
    print("  5  - 盈利指数 PI（NPV / |CF0|）")
    print("  6  - 现值指数 PI（现值 / |CF0|）")
    print("  7  - XNPV（不定期现金流）")
    print("  8  - 内部收益率 IRR")
    print("  9  - 全部指标")
    print("  10 - 修正内部收益率 MIRR")

    while True:
        sub = input("请输入 1-10：").strip()
        if sub in [str(i) for i in range(1, 11)]:
            break
        print("输入无效，请输入 1-10。")

    print()

    # ---------- 选项 1：AAR（用净利润） ----------
    if sub == "1":
        raw = input("请输入各年净利润（逗号分隔）：").strip()
        parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
        try:
            profits = [float(p) for p in parts]
        except ValueError:
            print("输入无效，请用逗号分隔数字。")
            return
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

    # ---------- 选项 7：XNPV ----------
    if sub == "7":
        cashflows = get_cashflows("请输入各期现金流（含第 0 期，逗号分隔）：")
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

    # ---------- 选项 10：MIRR ----------
    if sub == "10":
        full, cf0, _ = get_full_cashflows(
            "请输入完整现金流序列（第 0 期起，逗号分隔）："
        )
        reinvest_rate = get_rate("请输入再投资收益率（如 10% 或 0.10）：")
        finance_rate = get_rate("请输入融资成本率（如 8% 或 0.08）：")
        mirr, fv_pos, pv_neg, err = calc_mirr(full, reinvest_rate, finance_rate)
        print("\n" + "-" * 60)
        if err:
            print(err)
        else:
            n = len(full) - 1
            print(f"再投资收益率 = {reinvest_rate:.6f}  （即 {reinvest_rate*100:.4f}%）")
            print(f"融资成本率   = {finance_rate:.6f}  （即 {finance_rate*100:.4f}%）")
            print(f"期数 n = {n}")
            print()
            print(f"正现金流终值 FV = {fv_pos:.6f}")
            print(f"负现金流现值 PV = {pv_neg:.6f}")
            print()
            print(f"MIRR = (FV / |PV|)^(1/n) - 1")
            print(f"     = ({fv_pos:.6f} / {abs(pv_neg):.6f})^(1/{n}) - 1")
            print(f"     = {mirr:.6f}  （即 {mirr*100:.4f}%）")
        print("-" * 60)
        return

    # ---------- 选项 9：全部指标（支持未知） ----------
    if sub == "9":
        full, cf0, _ = get_full_cashflows(
            "请输入完整现金流序列（第 0 期起，逗号分隔）："
        )
        print()
        print("以下利率若未知，可直接回车或输入“未知”：")
        r = get_value("必要收益率", "用于贴现回收期、NPV、PI", is_rate=True)
        reinvest_rate = get_value("再投资收益率", "用于 MIRR", is_rate=True)
        finance_rate = get_value("融资成本率", "用于 MIRR", is_rate=True)

        print()
        print("AAR 需要净利润数据（与现金流不同）：")
        raw_profit = input("请输入各年净利润（逗号分隔，若未知直接回车跳过）：").strip()
        profits = None
        if raw_profit:
            parts = [p.strip() for p in raw_profit.replace("，", ",").split(",") if p.strip()]
            try:
                profits = [float(p) for p in parts]
            except ValueError:
                print("净利润输入无效，将跳过 AAR。")
                profits = None

        print("\n" + "-" * 60)

        # AAR
        if profits is not None:
            aar, err = calc_aar(profits, abs(cf0))
            if err:
                print(f"AAR：{err}")
            else:
                avg = sum(profits) / len(profits)
                print(f"AAR = {avg:.6f} / {abs(cf0):.6f} = {aar:.6f}  "
                      f"（即 {aar*100:.4f}%）")
        else:
            print("AAR：跳过（缺少净利润数据）")

        # 回收期
        print()
        pb, err = calc_payback(full)
        if err:
            print(f"回收期：{err}")
        else:
            print(f"回收期 = {pb:.6f} 年")

        # 贴现回收期
        if r is not None:
            dpb, err = calc_discounted_payback(full, r)
            if err:
                print(f"贴现回收期：{err}")
            else:
                print(f"贴现回收期 = {dpb:.6f} 年")
        else:
            print("贴现回收期：跳过（缺少必要收益率 r）")

        # NPV、PI
        if r is not None:
            npv, pv_future = calc_npv(full, r)
            print(f"现金流入现值 PV = {pv_future:.6f}")
            print(f"初始投资 |CF0| = {abs(cf0):.6f}")
            print(f"NPV = PV - |CF0| = {npv:.6f}")

            pi_npv, pi_pv, err = calc_pi(full, r)
            if err:
                print(f"PI：{err}")
            else:
                print(f"盈利指数 PI = NPV / |CF0| = {pi_npv:.6f}")
                print(f"现值指数 PI = PV / |CF0| = {pi_pv:.6f}")
        else:
            print("NPV：跳过（缺少必要收益率 r）")
            print("PI：跳过（缺少必要收益率 r）")

        # IRR
        print()
        irr, diag, err = calc_irr_with_diagnosis(full)
        print(diag)
        if err:
            print(f"IRR 求解失败：{err}")
        else:
            print(f"IRR = {irr:.6f}  （即 {irr*100:.4f}%）")

        # MIRR
        print()
        if reinvest_rate is not None and finance_rate is not None:
            mirr, fv_pos, pv_neg, err = calc_mirr(
                full, reinvest_rate, finance_rate
            )
            if err:
                print(f"MIRR：{err}")
            else:
                print(f"再投资收益率 = {reinvest_rate:.6f}  "
                      f"（即 {reinvest_rate*100:.4f}%）")
                print(f"融资成本率   = {finance_rate:.6f}  "
                      f"（即 {finance_rate*100:.4f}%）")
                print(f"正现金流终值 FV = {fv_pos:.6f}")
                print(f"负现金流现值 PV = {pv_neg:.6f}")
                print(f"MIRR = {mirr:.6f}  （即 {mirr*100:.4f}%）")
        else:
            print("MIRR：跳过（缺少再投资收益率或融资成本率）")

        print("-" * 60)
        return

    # ---------- 其余选项（单项指标） ----------
    full, cf0, _ = get_full_cashflows(
        "请输入完整现金流序列（第 0 期起，逗号分隔）："
    )

    r = None
    if sub in ("3", "4", "5", "6"):
        r = get_rate("请输入必要收益率 / 资本成本率（如 7.5% 或 0.075）：")

    print("\n" + "-" * 60)

    if sub == "2":
        pb, err = calc_payback(full)
        if err:
            print(f"回收期：{err}")
        else:
            print(f"回收期 = {pb:.6f} 年")

    elif sub == "3":
        dpb, err = calc_discounted_payback(full, r)
        if err:
            print(f"贴现回收期：{err}")
        else:
            print(f"贴现回收期 = {dpb:.6f} 年")

    elif sub == "4":
        npv, pv_future = calc_npv(full, r)
        print(f"现金流入现值 PV = {pv_future:.6f}")
        print(f"初始投资 |CF0| = {abs(cf0):.6f}")
        print(f"NPV = PV - |CF0| = {npv:.6f}")

    elif sub == "5":
        pi_npv, pi_pv, err = calc_pi(full, r)
        if err:
            print(f"PI：{err}")
        else:
            print(f"盈利指数 PI = NPV / |CF0| = {pi_npv:.6f}")

    elif sub == "6":
        pi_npv, pi_pv, err = calc_pi(full, r)
        if err:
            print(f"PI：{err}")
        else:
            print(f"现值指数 PI = PV / |CF0| = {pi_pv:.6f}")

    elif sub == "8":
        irr, diag, err = calc_irr_with_diagnosis(full)
        print(diag)
        if err:
            print(f"IRR 求解失败：{err}")
        else:
            print(f"IRR = {irr:.6f}  （即 {irr*100:.4f}%）")

    print("-" * 60)


if __name__ == "__main__":
    run()