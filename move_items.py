from pathlib import Path
import shutil
from datetime import datetime

LOG_FILE = Path(__file__).parent / "move_log.txt"

# 扩展名和目标文件夹名的对应关系：
CATEGORIES = {
    ".jpg": "图片", ".png": "图片",
    ".txt": "文档", ".md": "文档", ".pdf": "文档", ".docx": "文档",
    ".mp4": "视频", ".mkv": "视频",
}

def unique_target(dir: Path, file: Path) -> Path:
    """找到不冲突的目标路径，冲突时自动加后缀序号 _1、_2..."""
    target = dir / file.name
    n = 1
    while target.exists():
        target = dir / f"{file.stem}_{n}{file.suffix}"
        n += 1
    return target

def plan(src: Path) -> list:
    """算出每个文件应该放到哪里，返回一个 [(源, 目标, 分类), ...] 的列表，但不进行实际文件操作"""
    moves = []
    for item in src.iterdir():
        if not item.is_file():
            continue
        suf = item.suffix.lower()
        if suf not in CATEGORIES:
            continue
        target_dir = src / CATEGORIES[suf]
        target = unique_target(target_dir, item)
        moves.append((item, target, CATEGORIES[suf]))
    return moves

def confirm_prompt(moves: list) -> bool:
    print(f"将移动 {len(moves)} 个文件：")
    for item, target, cat in moves:
        print(f"    {item.name} -> {cat} / {target.name}")
    while True:
        ans = input("确认执行？(y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("请输入 y 或 n")

def execute_move(moves: list) -> None:
    batch_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取时间
    for item, target, cat in moves:
        target.parent.mkdir(exist_ok=True)
        shutil.move(item, target)
        write_log(item, target, batch_ts)
        print(f"移动：{item.name} -> {cat}/{target.name}")

def write_log(item: Path, target: Path, ts: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{item.resolve()}\t{target.resolve()}\n")  # 记录移动的绝对路径

def main(src: Path):
    moves = plan(src)
    if not moves:
        print("没有需要整理的文件")
        return
    if not confirm_prompt(moves):
        print("已取消：未移动任何文件")
        return
    execute_move(moves)
    print(f"完成移动")
    
if __name__ == "__main__":
    main(Path("D:/test"))