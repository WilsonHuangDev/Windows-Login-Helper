#!/bin/bash

# 构建脚本说明
echo "=== Windows-Login-Helper 打包脚本 ==="
echo "正在执行打包操作，请稍候..."

# 清理旧构建文件
echo "清理旧构建文件..."
rm -rf ./dist 2> /dev/null

# 执行打包命令（关键配置）
python -m nuitka \
--standalone \
--windows-console-mode=attach \
--windows-icon-from-ico=./Assets/icon.ico \
--company-name=Wilson.Huang \
--product-name="Windows 登录辅助工具" \
--include-package=PasswdChanger \
--include-package=modules \
--include-data-file="./Assets/**/*.ico=Assets/" \
--output-dir=./dist/Windows-Login-Helper \
--output-filename=WinLoginHelper \
--remove-output \
--show-progress \
--assume-yes-for-downloads \
./main.py

# 处理结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=== 打包成功 ==="

    # 移动并重命名文件
    echo "整理输出文件..."
    mv -fv ./dist/Windows-Login-Helper/main.dist/* ./dist/Windows-Login-Helper/

    # 清理临时文件
    rm -rf ./dist/Windows-Login-Helper/main.dist

    # 输出路径信息（转换为 Windows 格式）
    win_path=$(cygpath -w "$(pwd)/dist/Windows-Login-Helper")
    echo "程序路径：$win_path"
    echo "主程序：$win_path\\WinLoginHelper.exe"
else
    echo ""
    echo "=== 打包失败 ==="
    exit 1
fi

exit 0
