import argparse
from pathlib import Path

import move_items
import undo

def cli_move(args):
    """整理：调用 move_items 的完整流程"""
    move_items.main(Path(args.source))

def cli_undo(args):
    """撤销：调用 undo 的完整流程"""
    undo.main()

def interactive_menu() -> None:
    """无参数双击时的交互菜单"""
    while True:
        print("\n=== 文件整理工具 ===")
        print("1. 整理文件（按扩展名分类）")
        print("2. 撤销某次整理")
        print("q. 退出")
        choice = input("请选择: ").strip().lower()

        if choice == "1":
            src = input("请输入要整理的文件夹路径: ").strip().strip('"').strip("'")
            move_items.main(Path(src))
        elif choice == "2":
            undo.main()
        elif choice in ("q", "quit"):
            break
        else:
            print("无效输入，请重新输入")


def main():
    parser = argparse.ArgumentParser(description="文件管理器：按扩展名分类及对应撤销操作")
    sub = parser.add_subparsers(dest="command")   # 无参数时 args.command 为 None，进入交互菜单

    # 移动操作的子命令解析器对象
    p_move = sub.add_parser("move", help="按扩展名整理文档")
    p_move.add_argument("--source", "-s", required=True, help="要整理的文件夹路径")
    p_move.set_defaults(func=cli_move)   # 这行的作用是设置该解析器对象的函数（比写一堆 if 好的多）

    # 撤回操作的子命令解析器对象
    p_undo = sub.add_parser("undo", help="撤销某次操作")
    p_undo.set_defaults(func=cli_undo)

    # 解析命令行参数
    args = parser.parse_args()
    if args.command is None:
        interactive_menu()      # 无子命令（如双击 exe）→ 交互菜单
    else:
        args.func(args)         # 有子命令 → 执行对应的处理函数

if __name__ == "__main__":
    main()