"""复利、年金、债券、股票与投资项目评价计算器 —— 统一入口"""
from modes import basic, ear, continuous, annuity, bond, investment, stock


def print_menu():
    print("=" * 60)
    print("  复利、年金、债券、股票与投资项目评价计算器")
    print("  模式 1（基础）：    复利 F = P(1+i)^n / 单利 F = P(1+i·n)")
    print("  模式 2（EAR）：     EAR = (1 + R/M)^M - 1")
    print("  模式 3（连续复利）：F = P × e^(rt)")
    print("  模式 4（普通年金）：F = A × [((1+i)^n - 1) / i]")
    print("  模式 5（债券）：    静态分析、动态分析、期望 YTM")
    print("  模式 6（股票）：    零增长、固定增长、非固定增长")
    print("  模式 7（投资项目）：NPV、IRR、MIRR、PI、回收期等")
    print("=" * 60)
    print("请选择模式：")
    print("  1 - 基础模式（复利 / 单利）")
    print("  2 - EAR 模式（F, P, R, M, EAR, t）")
    print("  3 - 连续复利模式（F, P, r, t）")
    print("  4 - 普通年金模式（A, i, n, F 或 P）")
    print("  5 - 债券分析（静态、动态、期望 YTM）")
    print("  6 - 股票估值（零增长、固定增长、非固定增长）")
    print("  7 - 投资项目评价（NPV、IRR、MIRR、PI、回收期等）")
    print("  0 - 退出")
    print()
    print("提示：利率类变量可以直接输入百分数，例如 5% 或 12.5%")
    print("      投资项目评价的现金流请输入完整序列（第 0 期起）")


def pause():
    input("\n按回车键返回主菜单...")


def main():
    while True:
        print_menu()
        mode = input("请输入 0-7：").strip()

        if mode == "0":
            print("再见！")
            break

        print()
        if mode == "1":
            basic.run()
            pause()
        elif mode == "2":
            ear.run()
            pause()
        elif mode == "3":
            continuous.run()
            pause()
        elif mode == "4":
            annuity.run()
            pause()
        elif mode == "5":
            bond.run()
            pause()
        elif mode == "6":
            stock.run()
            pause()
        elif mode == "7":
            investment.run()
            pause()
        else:
            print("输入无效，请输入 0-7。")
            pause()

        print()


if __name__ == "__main__":
    main()