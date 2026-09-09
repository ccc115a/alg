#!/bin/bash

IMG="test.img"
rm -f "$IMG"

INODEFS="./target/debug/inodefs"

echo "========================================"
echo "inodefs 指令測試腳本"
echo "========================================"

cargo build --quiet 2>/dev/null

echo ""
echo "=== 測試所有指令 (單一 session) ==="

$INODEFS << 'COMMANDS'
format test.img
ls
pwd
mkdir dir1
ls
touch file1.txt
touch file2.txt
ls
write file1.txt HelloWorld
cat file1.txt
chmod file1.txt 777
stat file1.txt
mkdir subdir
cd subdir
pwd
touch subfile.txt
write subfile.txt nested_content
cat subfile.txt
cd /
pwd
rm file2.txt
ls
cd dir1
mkdir subdira
ls
rmdir subdira
ls
cd /
pwd
sync
quit
COMMANDS

echo ""
echo "========================================"
echo "驗證資料持久化 (重新 mount) ==="
echo "========================================"

$INODEFS << 'COMMANDS'
mount test.img
cat file1.txt
ls
quit
COMMANDS

rm -f "$IMG"
echo ""
echo "測試完成"