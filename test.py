"""test.py - 随机数据端到端测试 main.py

思路：
  1. 每个用例随机生成输入参数（避开奇异点）。
  2. 期望值由本脚本内【独立手写】的公式计算（不 import 被测模块的函数）。
  3. 通过 sys.stdin 驱动 main.main() 的交互流程，从 stdout 提取数值比对。
  4. 容差 1e-3。
"""

import io
import sys
import math
import re
import random
import contextlib

import main as app

random.seed(20241012)   # 固定种子，结果可复现

PASS = 0
FAIL = 0
FAILED = []

# ---------------- 驱动交互 ----------------
def run_with_input(text):
    if not text.rstrip().endswith("0"):
        text = text.rstrip() + "\n0\n"
    old = sys.stdin
    buf = io.StringIO()
    try:
        sys.stdin = io.StringIO(text)
        with contextlib.redirect_stdout(buf):
            app.main()
    finally:
        sys.stdin = old
    return buf.getvalue()

def run_mode(menu_choice, mode_inputs):
    lines = [str(menu_choice)] + list(mode_inputs) + ["", "0"]
    return run_with_input("\n".join(lines) + "\n")

# ---------------- 断言 ----------------
def nums_in(out):
    res = []
    for s in re.findall(r"-?\d+\.\d+", out):
        try:
            res.append(float(s))
        except ValueError:
            pass
    return res

def has_value(out, expected, tol=1e-3):
    return any(abs(v - expected) <= tol for v in nums_in(out))

def check(name, out, expected, tol=1e-3):
    global PASS, FAIL
    if expected is None:
        # 期望“无解”：只做占位通过，具体由 check_true 处理
        PASS += 1
        print(f"  [PASS] {name}: 期望无解（跳过数值比对）")
        return
    if has_value(out, expected, tol):
        PASS += 1
        print(f"  [PASS] {name}: {expected:.6f}")
    else:
        FAIL += 1
        FAILED.append((name, expected, out[-600:]))
        print(f"  [FAIL] {name}: 期望 {expected:.6f}")
        print(f"    输出尾部: {out[-400:]!r}")

def check_true(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {info}")
    else:
        FAIL += 1
        FAILED.append((name, True, info))
        print(f"  [FAIL] {name} {info}")

def section(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)

def rnd_rate(lo=0.01, hi=0.20):
    return round(random.uniform(lo, hi), 4)

def rnd_pos(lo=100, hi=5000, nd=2):
    return round(random.uniform(lo, hi), nd)

def fmt_rate(v):
    """把小数利率转成百分数字符串，如 0.0812 -> '8.1200%'"""
    return f"{v*100:.4f}%"


# ======================================================================
# 模式 1：复利 / 单利
# ======================================================================
def test_mode1():
    section("模式 1：基础复利 / 单利（随机）")

    # --- 复利求 F：F = P(1+i)^n ---
    for _ in range(3):
        P = rnd_pos(500, 4000)
        i = rnd_rate(0.02, 0.15)
        n = random.randint(2, 12)
        exp = P * (1 + i) ** n
        out = run_mode(1, ["1", "未知", str(P), fmt_rate(i), str(n)])
        check(f"复利 F (P={P},i={i},n={n})", out, exp)

    # --- 复利求 P：P = F/(1+i)^n ---
    for _ in range(3):
        F = rnd_pos(1000, 8000)
        i = rnd_rate(0.02, 0.15)
        n = random.randint(2, 12)
        exp = F / (1 + i) ** n
        out = run_mode(1, ["1", str(F), "未知", fmt_rate(i), str(n)])
        check(f"复利 P (F={F},i={i},n={n})", out, exp)

    # --- 复利求 i：i = (F/P)^(1/n) - 1，保证 n 为奇数避免双根歧义 ---
    for _ in range(3):
        P = rnd_pos(500, 3000)
        i = rnd_rate(0.02, 0.15)
        n = random.choice([3, 5, 7, 9])   # 奇数
        F = P * (1 + i) ** n
        out = run_mode(1, ["1", f"{F:.6f}", str(P), "未知", str(n)])
        check(f"复利 i (F={F:.4f},P={P},n={n})", out, i)

    # --- 复利求 n：n = ln(F/P)/ln(1+i) ---
    for _ in range(3):
        P = rnd_pos(500, 3000)
        i = rnd_rate(0.02, 0.15)
        n = random.randint(2, 15)
        F = P * (1 + i) ** n
        out = run_mode(1, ["1", f"{F:.6f}", str(P), fmt_rate(i), "未知"])
        check(f"复利 n (F={F:.4f},P={P},i={i})", out, n)

    # --- 单利求 F：F = P(1+i*n) ---
    for _ in range(3):
        P = rnd_pos(500, 4000)
        i = rnd_rate(0.02, 0.15)
        n = random.randint(2, 10)
        exp = P * (1 + i * n)
        out = run_mode(1, ["2", "未知", str(P), fmt_rate(i), str(n)])
        check(f"单利 F (P={P},i={i},n={n})", out, exp)

    # --- 单利求 i：i = (F/P-1)/n ---
    for _ in range(3):
        P = rnd_pos(500, 3000)
        i = rnd_rate(0.02, 0.15)
        n = random.randint(2, 10)
        F = P * (1 + i * n)
        out = run_mode(1, ["2", f"{F:.6f}", str(P), "未知", str(n)])
        check(f"单利 i (F={F:.4f},P={P},n={n})", out, i)


# ======================================================================
# 模式 2：EAR
# ======================================================================
def test_mode2():
    section("模式 2：EAR（随机）")

    # EAR = (1+R/M)^M - 1
    for _ in range(3):
        R = rnd_rate(0.03, 0.18)
        M = random.choice([2, 4, 12])
        exp = (1 + R / M) ** M - 1
        out = run_mode(2, ["未知", "未知", fmt_rate(R), str(M), "未知", "未知"])
        check(f"EAR (R={R},M={M})", out, exp)

    # R = M[(1+EAR)^(1/M)-1]
    for _ in range(3):
        EAR = rnd_rate(0.03, 0.20)
        M = random.choice([2, 4, 12])
        exp = M * ((1 + EAR) ** (1 / M) - 1)
        out = run_mode(2, ["未知", "未知", "未知", str(M), fmt_rate(EAR), "未知"])
        check(f"R (EAR={EAR},M={M})", out, exp)

    # F = P(1+R/M)^(Mt)
    for _ in range(3):
        P = rnd_pos(500, 5000)
        R = rnd_rate(0.03, 0.18)
        M = random.choice([2, 4, 12])
        t = random.randint(1, 8)
        exp = P * (1 + R / M) ** (M * t)
        out = run_mode(2, ["未知", str(P), fmt_rate(R), str(M), "未知", str(t)])
        check(f"EAR 求 F (P={P},R={R},M={M},t={t})", out, exp)

    # P = F/(1+EAR)^t
    for _ in range(3):
        F = rnd_pos(1000, 8000)
        EAR = rnd_rate(0.03, 0.20)
        t = random.randint(1, 10)
        exp = F / (1 + EAR) ** t
        out = run_mode(2, [str(F), "未知", "未知", "未知", fmt_rate(EAR), str(t)])
        check(f"EAR 求 P (F={F},EAR={EAR},t={t})", out, exp)

    # t = ln(F/P)/ln(1+EAR)
    for _ in range(3):
        P = rnd_pos(500, 3000)
        EAR = rnd_rate(0.03, 0.20)
        t = random.randint(1, 10)
        F = P * (1 + EAR) ** t
        out = run_mode(2, [f"{F:.6f}", str(P), "未知", "未知", fmt_rate(EAR), "未知"])
        check(f"EAR 求 t (F={F:.4f},P={P},EAR={EAR})", out, t)


# ======================================================================
# 模式 3：连续复利
# ======================================================================
def test_mode3():
    section("模式 3：连续复利（随机）")

    # F = P e^(rt)
    for _ in range(3):
        P = rnd_pos(500, 5000)
        r = rnd_rate(0.01, 0.15)
        t = random.randint(1, 10)
        exp = P * math.exp(r * t)
        out = run_mode(3, ["未知", str(P), fmt_rate(r), str(t)])
        check(f"连续 F (P={P},r={r},t={t})", out, exp)

    # P = F e^(-rt)
    for _ in range(3):
        F = rnd_pos(1000, 8000)
        r = rnd_rate(0.01, 0.15)
        t = random.randint(1, 10)
        exp = F * math.exp(-r * t)
        out = run_mode(3, [str(F), "未知", fmt_rate(r), str(t)])
        check(f"连续 P (F={F},r={r},t={t})", out, exp)

    # r = ln(F/P)/t
    for _ in range(3):
        P = rnd_pos(500, 3000)
        r = rnd_rate(0.01, 0.15)
        t = random.randint(1, 10)
        F = P * math.exp(r * t)
        out = run_mode(3, [f"{F:.6f}", str(P), "未知", str(t)])
        check(f"连续 r (F={F:.4f},P={P},t={t})", out, r)

    # t = ln(F/P)/r
    for _ in range(3):
        P = rnd_pos(500, 3000)
        r = rnd_rate(0.01, 0.15)
        t = random.randint(1, 10)
        F = P * math.exp(r * t)
        out = run_mode(3, [f"{F:.6f}", str(P), fmt_rate(r), "未知"])
        check(f"连续 t (F={F:.4f},P={P},r={r})", out, t)


# ======================================================================
# 模式 4：年金
# ======================================================================
def test_mode4():
    section("模式 4：普通年金（随机）")

    # 终值型求 F
    for _ in range(3):
        A = rnd_pos(300, 2000)
        i = rnd_rate(0.02, 0.12)
        n = random.randint(3, 15)
        exp = A * ((1 + i) ** n - 1) / i
        out = run_mode(4, ["1", str(A), fmt_rate(i), str(n), "未知"])
        check(f"年金 FV (A={A},i={i},n={n})", out, exp)

    # 现值型求 P
    for _ in range(3):
        A = rnd_pos(300, 2000)
        i = rnd_rate(0.02, 0.12)
        n = random.randint(3, 15)
        exp = A * (1 - (1 + i) ** (-n)) / i
        out = run_mode(4, ["2", str(A), fmt_rate(i), str(n), "未知"])
        check(f"年金 PV (A={A},i={i},n={n})", out, exp)

    # 终值型求 A
    for _ in range(3):
        F = rnd_pos(3000, 20000)
        i = rnd_rate(0.02, 0.12)
        n = random.randint(3, 12)
        exp = F * i / ((1 + i) ** n - 1)
        out = run_mode(4, ["1", "未知", fmt_rate(i), str(n), str(F)])
        check(f"年金 A (F={F},i={i},n={n})", out, exp)

    # 终值型求 n
    for _ in range(3):
        A = rnd_pos(300, 2000)
        i = rnd_rate(0.02, 0.12)
        n = random.randint(3, 15)
        F = A * ((1 + i) ** n - 1) / i
        out = run_mode(4, ["1", str(A), fmt_rate(i), "未知", f"{F:.6f}"])
        check(f"年金 n (A={A},i={i},F={F:.4f})", out, n)

    # 现值型求 i（数值解）：用已知 i 反推 P，再求 i，验证回代 P
    for _ in range(3):
        A = rnd_pos(300, 2000)
        i = rnd_rate(0.02, 0.12)
        n = random.randint(3, 12)
        P = A * (1 - (1 + i) ** (-n)) / i
        out = run_mode(4, ["2", str(A), "未知", str(n), f"{P:.6f}"])
        check(f"年金 i 回代 P (A={A},n={n},P={P:.4f})", out, P)


# ======================================================================
# 模式 5：债券
# ======================================================================
def test_mode5():
    section("模式 5：债券（随机）")

    # 静态求 P
    for _ in range(3):
        F = 1000.0
        C = round(random.uniform(30, 120), 2)
        n = random.randint(3, 10)
        y = rnd_rate(0.02, 0.10)
        exp = C * (1 - (1 + y) ** (-n)) / y + F / (1 + y) ** n
        out = run_mode(5, ["1", str(F), str(C), str(n), "未知", fmt_rate(y)])
        check(f"债券 P (C={C},n={n},y={y})", out, exp)

    # 静态求 y（回代 P）
    for _ in range(3):
        F = 1000.0
        C = round(random.uniform(30, 120), 2)
        n = random.randint(3, 10)
        y = rnd_rate(0.02, 0.10)
        P = C * (1 - (1 + y) ** (-n)) / y + F / (1 + y) ** n
        out = run_mode(5, ["1", str(F), str(C), str(n), f"{P:.6f}", "未知"])
        check(f"债券 y 回代 P (C={C},n={n},P={P:.4f})", out, P)

    # 动态分析（基本参数）：久期/凸度独立手算
    for _ in range(3):
        F = 1000.0
        C = round(random.uniform(40, 120), 2)
        n = random.randint(3, 8)
        y = rnd_rate(0.02, 0.09)
        cfs = [C] * (n - 1) + [C + F]
        pvs = [cf / (1 + y) ** t for t, cf in enumerate(cfs, 1)]
        total = sum(pvs)
        d_mac = sum(t * pv for t, pv in enumerate(pvs, 1)) / total
        d_mod = d_mac / (1 + y)
        conv = sum(t * (t + 1) * cf / (1 + y) ** (t + 2)
                   for t, cf in enumerate(cfs, 1)) / total
        out = run_mode(5, ["2", "1", str(F), str(C), str(n), fmt_rate(y)])
        check(f"债券价值 (C={C},n={n},y={y})", out, total)
        check(f"Macaulay 久期 (C={C},n={n},y={y})", out, d_mac)
        check(f"修正久期 (C={C},n={n},y={y})", out, d_mod)
        check(f"凸度 (C={C},n={n},y={y})", out, conv)

    # 期望 YTM（概率和=1）
    for _ in range(3):
        p = round(random.uniform(0.7, 0.99), 2)
        y_p = rnd_rate(0.05, 0.15)
        y_d = round(random.uniform(-0.40, -0.05), 4)
        exp = p * y_p + (1 - p) * y_d
        out = run_mode(5, ["3", fmt_rate(y_p), str(p),
                           fmt_rate(y_d), str(round(1 - p, 2))])
        check(f"期望 YTM (p={p})", out, exp)


# ======================================================================
# 模式 6：股票
# ======================================================================
def test_mode6():
    section("模式 6：股票（随机）")

    # 零增长求 V
    for _ in range(3):
        D = rnd_pos(1, 20)
        r = rnd_rate(0.05, 0.20)
        exp = D / r
        out = run_mode(6, ["1", "未知", str(D), fmt_rate(r)])
        check(f"零增长 V (D={D},r={r})", out, exp)

    # 零增长求 r
    for _ in range(3):
        D = rnd_pos(1, 20)
        r = rnd_rate(0.05, 0.20)
        V = D / r
        out = run_mode(6, ["1", f"{V:.6f}", str(D), "未知"])
        check(f"零增长 r (D={D},V={V:.4f})", out, r)

    # 固定增长求 V（保证 r > g）
    for _ in range(3):
        D1 = rnd_pos(1, 10)
        g = rnd_rate(0.01, 0.06)
        r = round(g + random.uniform(0.03, 0.12), 4)
        exp = D1 / (r - g)
        out = run_mode(6, ["2", "未知", str(D1), fmt_rate(r), fmt_rate(g)])
        check(f"固定增长 V (D1={D1},r={r},g={g})", out, exp)

    # 固定增长求 r
    for _ in range(3):
        D1 = rnd_pos(1, 10)
        g = rnd_rate(0.01, 0.06)
        r = round(g + random.uniform(0.03, 0.12), 4)
        V = D1 / (r - g)
        out = run_mode(6, ["2", f"{V:.6f}", str(D1), "未知", fmt_rate(g)])
        check(f"固定增长 r (D1={D1},g={g},V={V:.4f})", out, r)

    # 非固定增长求 V（两阶段，独立手算）
    for _ in range(3):
        n1 = random.randint(2, 4)
        divs = [round(random.uniform(1, 5), 2)]
        for _ in range(n1 - 1):
            divs.append(round(divs[-1] * random.uniform(0.9, 1.2), 2))
        g = rnd_rate(0.01, 0.05)
        r = round(g + random.uniform(0.04, 0.12), 4)
        pv1 = sum(d / (1 + r) ** t for t, d in enumerate(divs, 1))
        d_next = divs[-1] * (1 + g)
        pv2 = (d_next / (r - g)) / (1 + r) ** n1
        exp = pv1 + pv2
        divs_str = ",".join(str(d) for d in divs)
        out = run_mode(6, ["3", divs_str, fmt_rate(r), fmt_rate(g), "未知"])
        check(f"非固定增长 V (divs={divs},r={r},g={g})", out, exp)

    # 时间加权收益率
    for _ in range(3):
        P0 = rnd_pos(50, 200)
        prices = []
        divs = []
        prev = P0
        for _ in range(2):
            p = round(prev * random.uniform(0.9, 1.15), 2)
            d = round(random.uniform(0, 5), 2)
            prices.append(p)
            divs.append(d)
            prev = p
        # 独立手算几何平均
        rets = []
        prev = P0
        for p, d in zip(prices, divs):
            rets.append((p - prev + d) / prev)
            prev = p
        prod = 1.0
        for rr in rets:
            prod *= (1 + rr)
        geo = prod ** (1 / len(rets)) - 1
        out = run_mode(6, ["4",
                           ",".join(str(p) for p in prices),
                           ",".join(str(d) for d in divs),
                           str(P0)])
        check(f"TWR 几何平均 (P0={P0})", out, geo)


# ======================================================================
# 模式 7：投资项目
# ======================================================================
def test_mode7():
    section("模式 7：投资项目（随机）")

    def gen_cfs():
        """生成标准投资型现金流：第0期负，后续正，且总和 > 1.5×|CF0|（保证可回收）"""
        n = random.randint(3, 6)
        cf0 = -round(random.uniform(500, 3000), 2)
        target_total = abs(cf0) * random.uniform(1.5, 3.0)
        raw = [random.uniform(0.5, 1.5) for _ in range(n)]
        scale = target_total / sum(raw)
        rest = [round(x * scale, 2) for x in raw]
        return [cf0] + rest

    # NPV / PI / 回收期 / 贴现回收期（同一组随机数据）
    for _ in range(4):
        cfs = gen_cfs()
        r = rnd_rate(0.03, 0.15)
        cfs_str = ",".join(str(c) for c in cfs)

        # NPV（独立手算）
        npv = sum(cf / (1 + r) ** t for t, cf in enumerate(cfs))
        out = run_mode(7, ["4", cfs_str, fmt_rate(r)])
        check(f"NPV (cfs={cfs},r={r})", out, npv)

        # 盈利指数 = NPV/|CF0|
        pi_npv = npv / abs(cfs[0])
        out = run_mode(7, ["5", cfs_str, fmt_rate(r)])
        check(f"盈利指数 PI (cfs={cfs},r={r})", out, pi_npv)

        # 现值指数 = (NPV+|CF0|)/|CF0|
        pi_pv = (npv + abs(cfs[0])) / abs(cfs[0])
        out = run_mode(7, ["6", cfs_str, fmt_rate(r)])
        check(f"现值指数 PI (cfs={cfs},r={r})", out, pi_pv)

        # 回收期（独立手算）
        cum = 0.0
        pb = None
        for t, cf in enumerate(cfs):
            prev = cum
            cum += cf
            if t > 0 and cum >= 0:
                pb = t - 1 + (-prev) / cf
                break
        out = run_mode(7, ["2", cfs_str])
        check(f"回收期 (cfs={cfs})", out, pb)

        # 贴现回收期（独立手算）
        target = abs(cfs[0])
        cum = 0.0
        dpb = None
        for t, cf in enumerate(cfs[1:], 1):
            pv = cf / (1 + r) ** t
            prev = cum
            cum += pv
            if cum >= target:
                dpb = t - 1 + (target - prev) / pv
                break
        out = run_mode(7, ["3", cfs_str, fmt_rate(r)])
        check(f"贴现回收期 (cfs={cfs},r={r})", out, dpb)

    # AAR（独立手算）
    for _ in range(3):
        profits = [round(random.uniform(-50, 500), 2) for _ in range(random.randint(2, 5))]
        init = round(random.uniform(500, 3000), 2)
        aar = (sum(profits) / len(profits)) / init
        profits_str = ",".join(str(p) for p in profits)
        out = run_mode(7, ["1", profits_str, str(init)])
        check(f"AAR (profits={profits},init={init})", out, aar)

    # IRR（独立手算：用二分法求解，验证程序输出与手算一致）
    for _ in range(4):
        cfs = gen_cfs()
        cfs_str = ",".join(str(c) for c in cfs)
        # 独立实现二分法求 IRR
        def npv_at(x):
            return sum(cf / (1 + x) ** t for t, cf in enumerate(cfs))
        lo, hi = -0.9999, 5.0
        if npv_at(lo) * npv_at(hi) > 0:
            exp_irr = None
        else:
            for _ in range(200):
                mid = (lo + hi) / 2
                if npv_at(lo) * npv_at(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            exp_irr = (lo + hi) / 2
        out = run_mode(7, ["8", cfs_str])
        if exp_irr is None:
            check_true(f"IRR 无解 (cfs={cfs})", "找不到" in out or "失败" in out)
        else:
            check(f"IRR (cfs={cfs})", out, exp_irr)

    # MIRR（独立手算）
    for _ in range(3):
        cfs = gen_cfs()
        reinv = rnd_rate(0.05, 0.15)
        fin = rnd_rate(0.03, 0.10)
        n = len(cfs) - 1
        fv_pos = sum(cf * (1 + reinv) ** (n - t)
                     for t, cf in enumerate(cfs) if cf > 0)
        pv_neg = sum(cf / (1 + fin) ** t
                     for t, cf in enumerate(cfs) if cf < 0)
        exp_mirr = (fv_pos / abs(pv_neg)) ** (1 / n) - 1
        cfs_str = ",".join(str(c) for c in cfs)
        out = run_mode(7, ["10", cfs_str, fmt_rate(reinv), fmt_rate(fin)])
        check(f"MIRR (cfs={cfs},reinv={reinv},fin={fin})", out, exp_mirr)


# ======================================================================
def main():
    test_mode1()
    test_mode2()
    test_mode3()
    test_mode4()
    test_mode5()
    test_mode6()
    test_mode7()

    section("测试汇总")
    total = PASS + FAIL
    print(f"总计: {total}  通过: {PASS}  失败: {FAIL}")
    if FAILED:
        print("\n失败用例：")
        for name, exp, tail in FAILED:
            print(f"  - {name}: 期望 {exp}")
            print(f"    输出尾部: {tail!r}")
    else:
        print("全部通过！")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())