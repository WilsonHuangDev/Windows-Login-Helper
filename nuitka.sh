#!/usr/bin/env bash

echo "=== Windows-Login-Helper Nuitka 打包脚本 ==="
echo "正在执行打包操作，请稍候..."

echo "清理旧构建文件..."
rm -rf ./dist 2> /dev/null

python -m nuitka \
--standalone \
--mingw64 \
--enable-plugin=tk-inter \
--include-data-dir=PasswdChanger=PasswdChanger \
--include-data-dir=modules=modules \
--output-dir=dist \
--remove-output \
--show-progress \
./main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=== 打包成功 ==="
    echo "生成文件路径："$(cygpath -w $(pwd)/dist/main.dist)
    echo "可执行文件："$(cygpath -w $(pwd)/dist/main.dist/main.exe)
else
    echo ""
    echo "=== 打包失败 ==="
    exit 1
fi
