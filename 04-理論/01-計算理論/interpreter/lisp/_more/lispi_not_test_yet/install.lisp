(load "quicklisp.lisp")
(quicklisp-quickstart:install)
(ql:add-to-init-file) ; 這會讓 SBCL 每次啟動都自動載入 Quicklisp