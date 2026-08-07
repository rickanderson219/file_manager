from pathlib import Path
import shutil

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

def main(src: Path):
    for item in src.iterdir():
        if not item.is_file():
            continue
        
        suf = item.suffix.lower()
        if suf not in CATEGORIES:  # 跳过未分类的扩展名
            continue
            
        target_dir = src / CATEGORIES[suf]
        target_dir.mkdir(exist_ok=True)
        target = unique_target(target_dir, item)
        shutil.move(str(item), target)
        print(f"移动：{item.name} -> {CATEGORIES[suf]}/{target.name}")

if __name__ == "__main__":
    main(Path("D:/test"))