#include <algorithm>        // std::transform
#include <cctype>           // std::tolower
#include <filesystem>       // C++17 文件系统库，对应 Python 的 pathlib
#include <iostream>
#include <string>
#include <unordered_map>

namespace fs = std::filesystem;

// 扩展名 -> 目标文件夹名（对应 Python 版的 CATEGORIES 字典）
const std::unordered_map<std::string, std::string> CATEGORIES = {
    {".jpg", "图片"}, {".png", "图片"},
    {".txt", "文档"}, {".md", "文档"}, {".pdf", "文档"}, {".docx", "文档"},
    {".mp4", "视频"}, {".mkv", "视频"},
};

// 转小写（对应 Python 的 .lower()）
std::string toLower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return s;
}

// 返回不冲突的目标路径，冲突时自动加 _1、_2...
// 对应 Python 版的 unique_target() 函数
fs::path uniqueTarget(const fs::path& dir, const fs::path& name) {
    fs::path target = dir / name.filename();
    int n = 1;
    while (fs::exists(target)) {
        std::string newName = name.stem().string() + "_" + std::to_string(n)
                            + name.extension().string();
        target = dir / newName;
        ++n;
    }
    return target;
}

int main() {
    // L"" 是宽字符串，Windows 下处理中文路径要用它
    const fs::path src = L"D:/test";

    for (const auto& entry : fs::directory_iterator(src)) {
        if (!entry.is_regular_file())   // 跳过文件夹
            continue;

        std::string suf = toLower(entry.path().extension().string());
        auto it = CATEGORIES.find(suf);
        if (it == CATEGORIES.end())     // 跳过未分类的扩展名
            continue;

        fs::path targetDir = src / it->second;
        fs::create_directories(targetDir);   // 对应 mkdir(exist_ok=True)

        fs::path target = uniqueTarget(targetDir, entry.path());
        fs::rename(entry.path(), target);    // 对应 shutil.move

        // 输出中文需要 std::wcout + .wstring()
        std::wcout << L"移动：" << entry.path().filename().wstring()
                   << L" -> " << it->second << L"/"
                   << target.filename().wstring() << std::endl;
    }
    return 0;
}
