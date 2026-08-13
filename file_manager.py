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

def main():
    parser = argparse.ArgumentParser(description="文件管理器：按扩展名分类及对应撤销操作")
    sub = parser.add_subparsers(dest="command", required=True)  # 必须写子命令

    # 移动操作的子命令解析器对象
    p_move = sub.add_parser("move", help="按扩展名整理文档")
    p_move.add_argument("--source", "-s", required=True, help="要整理的文件夹路径")
    p_move.set_defaults(func=cli_move)   # 这行的作用是设置该解析器对象的函数（比写一堆 if 好的多）

    # 撤回操作的子命令解析器对象
    p_undo = sub.add_parser("undo", help="撤销某次操作")
    p_undo.set_defaults(func=cli_undo)

    # 解析命令行参数
    args = parser.parse_args()
    args.func(args)   # 这行代码会执行 func 函数，并把参数 args 传进去

if __name__ == "__main__":
    main()