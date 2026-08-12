from pathlib import Path
import shutil
import json
from paths import LOG_FILE

def read_log() -> list:
    records = []
    if not LOG_FILE.exists():
        print("未找到日志文件，请先运行 move_items.py")
        return records
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()   # 去掉开头结尾的空白
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print(f"警告：跳过无法解析的行：{line}")
                continue
            if not isinstance(rec, dict):
                print(f"警告：跳过非对象行：{line}")
                continue
            if rec.get("op") != "move":
                print(f"警告：跳过不支持的操作：{rec.get('op')}")
                continue
            records.append((rec["time"], Path(rec["src"]), Path(rec["dst"])))
    return records

def group_by_batch(records: list) -> dict:
    """按时间戳分组，返回 {时间戳: [(旧路径, 新路径), ...]}"""
    batches = {}
    for ts, old, new in records:
        batches.setdefault(ts, []).append((old, new))   # 时间戳相同的归为一批
    return batches

def unique_restore_target(target: Path) -> Path:
    """旧位置被占用时，加后缀 _restored1、_restored2..."""
    n = 1
    while target.exists():
        target = target.with_name(f"{target.stem}_restored{n}{target.suffix}")
        n += 1
    return target

def undo_batch(records: list) -> None:
    """把一批文件从新路径移回旧路径"""
    success, fail = 0, 0
    for old, new in records:
        if not new.exists():        # 新路径文件可能被删除/移走/重命名
            print(f"跳过：文件不存在 {new}")
            fail += 1
            continue
        target = unique_restore_target(old)  # 获得可用的旧位置（原本的可能已被占用）
        old.parent.mkdir(exist_ok=True)      # 旧目录也可能不存在了
        shutil.move(new, target)
        print(f"撤回：{new.name} -> {target}")
        success += 1
    print(f"本批撤回完成：成功 {success} 个，失败 {fail} 个")

def main() -> None:
    records = read_log()
    if not records:
        return

    batches = group_by_batch(records)
    keys = list(batches.keys())
    print("可撤销的批次：")
    for i, ts in enumerate(keys, 1):
        print(f"  {i}. {ts} ({len(batches[ts])} 个文件)")
    print(f"  {len(keys) + 1}. 全部撤销")

    while True:
        choice = input("请输入编号：").strip()
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(keys):
                undo_batch(batches[keys[n-1]])
                return
            if n == len(keys) + 1:
                for ts in keys:
                    undo_batch(batches[ts])
                return
        print("无效编号，请重新输入")

if __name__ == "__main__":
    main()