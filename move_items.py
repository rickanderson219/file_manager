from pathlib import Path
import shutil
from datetime import datetime
import json

LOG_FILE = Path(__file__).parent / "log.jsonl"

# 扩展名和目标文件夹名的对应关系：
DEFAULT_CATEGORIES = {
    ".jpg": "图片", ".png": "图片",
    ".txt": "文档", ".md": "文档", ".pdf": "文档", ".docx": "文档",
    ".mp4": "视频", ".mkv": "视频",
}
CONFIG_FILE = LOG_FILE.parent / "config.json"

def load_categories() -> dict:
    """读取 config.json 的分类规则：缺失时按默认值创建损坏时回退到内置默认值"""
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"categories": DEFAULT_CATEGORIES}, f, 
                      ensure_ascii=False, indent=2)
        print(f"未找到配置文件，已生成默认配置：{CONFIG_FILE}")
        return DEFAULT_CATEGORIES
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["categories"]
    except (json.JSONDecodeError, KeyError, OSError):
        print("警告：配置文件损坏，使用默认分类")
        return DEFAULT_CATEGORIES

categories = load_categories()

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
        if suf not in categories:
            continue
        target_dir = src / categories[suf]
        target = unique_target(target_dir, item)
        moves.append((item, target, categories[suf]))
    return moves

def confirm_prompt(moves: list) -> bool:
    """计算出所有移动关系，输出，确认是否要打印"""
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
    """执行移动操作，并写入日志"""
    batch_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取时间
    for item, target, cat in moves:
        target.parent.mkdir(exist_ok=True)
        shutil.move(item, target)
        write_log(item, target, batch_ts)
        print(f"移动：{item.name} -> {cat}/{target.name}")

def write_log(item: Path, target: Path, ts: str):
    """将操作写入一个 json 日志"""
    record = {
        "op": "move",                       # 操作类型：移动
        "time": ts,                         # 批次时间戳
        "src": str(item.resolve()),         # 原路径（转为字符串绝对路径）
        "dst": str(target.resolve()),       # 目标路径
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def main(src: Path):
    if not src.is_dir():
        print(f"错误：目录不存在或不是文件夹：{src}")
        return
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
    while True:
        raw = input("请输入要整理的文件夹路径（输入 q 退出）：").strip().strip('"').strip("'")
        if raw.lower() in ("q", "quit", "exit"):
            print("已退出")
            break
        src = Path(raw)
        if src.is_dir():
            main(src)
            break
        print(f"目录不存在或不是文件夹：{src}")