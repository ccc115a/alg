gcc -Wall -Wextra -o lispEval lispEval.c
./lispEval          # 互動 REPL
./lispEval -d       # 執行 McCarthy 範例 demo
./lispEval -e '(CAR (QUOTE (A B C)))'   # 求值單一程式