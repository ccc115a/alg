;;; ============================================================
;;;  Mini-Lisp 解譯器 — 用 Common Lisp 實作
;;;  功能：lambda、define、if、cond、let、let*、quote、
;;;        quasiquote、begin、apply、map、基本算術與比較
;;; ============================================================

(defpackage :mini-lisp
  (:use :cl)
  (:export :repl :eval-expr :make-global-env))

(in-package :mini-lisp)

;;; ─── 資料結構 ──────────────────────────────────────────────

;; 環境：關聯串列的鏈結
(defstruct env
  bindings   ; alist: (name . value)
  parent)    ; 上層環境

(defun env-lookup (name env)
  "在環境鏈中查找變數名稱"
  (cond
    ((null env)
     (error "未定義的變數: ~A" name))
    ((assoc name (env-bindings env))
     (cdr (assoc name (env-bindings env))))
    (t
     (env-lookup name (env-parent env)))))

(defun env-set! (name value env)
  "修改已存在的變數綁定"
  (cond
    ((null env)
     (error "未定義的變數: ~A" name))
    ((assoc name (env-bindings env))
     (setf (cdr (assoc name (env-bindings env))) value))
    (t
     (env-set! name value (env-parent env)))))

(defun env-define (name value env)
  "在目前環境層定義新變數"
  (let ((pair (assoc name (env-bindings env))))
    (if pair
        (setf (cdr pair) value)
        (push (cons name value) (env-bindings env))))
  value)

(defun extend-env (names values parent)
  "建立新環境，將 names 綁定到 values"
  (when (/= (length names) (length values))
    (error "參數數量不符：預期 ~A 個，得到 ~A 個"
           (length names) (length values)))
  (make-env :bindings (mapcar #'cons names values)
            :parent parent))

;;; ─── Lambda（閉包）───────────────────────────────────────

(defstruct closure
  params   ; 參數列表
  body     ; 函數主體（可多個表達式）
  env)     ; 定義時的環境（詞法作用域）

(defmethod print-object ((c closure) stream)
  (format stream "#<lambda (~{~A~^ ~})>" (closure-params c)))

;;; ─── 詞法分析器（Tokenizer）──────────────────────────────

(defun tokenize (input)
  "將字串切成 token 串列"
  (let ((tokens '())
        (i 0)
        (len (length input)))
    (loop while (< i len) do
      (let ((ch (char input i)))
        (cond
          ;; 跳過空白
          ((member ch '(#\Space #\Tab #\Newline #\Return))
           (incf i))
          ;; 跳過行尾註解
          ((char= ch #\;)
           (loop while (and (< i len)
                            (not (char= (char input i) #\Newline)))
                 do (incf i)))
          ;; 括號
          ((char= ch #\()
           (push "(" tokens) (incf i))
          ((char= ch #\))
           (push ")" tokens) (incf i))
          ;; quote 糖衣語法
          ((char= ch #\')
           (push "'" tokens) (incf i))
          ;; quasiquote
          ((char= ch #\`)
           (push "`" tokens) (incf i))
          ;; unquote-splicing
          ((and (char= ch #\,)
                (< (1+ i) len)
                (char= (char input (1+ i)) #\@))
           (push ",@" tokens) (incf i) (incf i))
          ;; unquote
          ((char= ch #\,)
           (push "," tokens) (incf i))
          ;; 字串
          ((char= ch #\")
           (incf i)
           (let ((start i))
             (loop while (and (< i len) (not (char= (char input i) #\")))
                   do (incf i))
             (push (format nil "\"~A\"" (subseq input start i)) tokens)
             (incf i)))
          ;; 一般 token（符號或數字）
          (t
           (let ((start i))
             (loop while (and (< i len)
                              (not (member (char input i)
                                           '(#\Space #\Tab #\Newline #\Return
                                             #\( #\) #\' #\` #\,))))
                   do (incf i))
             (push (subseq input start i) tokens))))))
    (nreverse tokens)))

;;; ─── 解析器（Parser）──────────────────────────────────────

(defun parse-atom (token)
  "將 token 字串轉換成 Lisp 物件"
  (cond
    ;; 整數
    ((every #'digit-char-p
            (if (and (> (length token) 0) (char= (char token 0) #\-))
                (subseq token 1) token))
     (if (> (length token) 0) (parse-integer token :junk-allowed t) nil))
    ;; 浮點數
    ((handler-case (progn (parse-float token) t) (t () nil))
     (read-from-string token))
    ;; 字串
    ((and (> (length token) 1)
          (char= (char token 0) #\")
          (char= (char token (1- (length token))) #\"))
     (subseq token 1 (1- (length token))))
    ;; 布林
    ((string= token "#t") t)
    ((string= token "#f") nil)
    ((string= token "nil") '())
    ;; 符號
    (t (intern (string-upcase token) :mini-lisp))))

(defun parse-tokens (tokens)
  "從 token 串列解析出 S 表達式，回傳 (expr . remaining-tokens)"
  (when (null tokens)
    (error "意外的輸入結束"))
  (let ((token (car tokens))
        (rest  (cdr tokens)))
    (cond
      ;; quote 糖衣
      ((string= token "'")
       (destructuring-bind (expr . remaining) (parse-tokens rest)
         (cons (list 'quote expr) remaining)))
      ;; quasiquote
      ((string= token "`")
       (destructuring-bind (expr . remaining) (parse-tokens rest)
         (cons (list 'quasiquote expr) remaining)))
      ;; unquote-splicing
      ((string= token ",@")
       (destructuring-bind (expr . remaining) (parse-tokens rest)
         (cons (list 'unquote-splicing expr) remaining)))
      ;; unquote
      ((string= token ",")
       (destructuring-bind (expr . remaining) (parse-tokens rest)
         (cons (list 'unquote expr) remaining)))
      ;; 左括號 → 解析串列
      ((string= token "(")
       (let ((elems '())
             (remaining rest))
         (loop
           (when (null remaining)
             (error "括號未閉合"))
           (when (string= (car remaining) ")")
             (return (cons (nreverse elems) (cdr remaining))))
           (destructuring-bind (elem . new-remaining) (parse-tokens remaining)
             (push elem elems)
             (setf remaining new-remaining)))))
      ;; 右括號 → 錯誤
      ((string= token ")")
       (error "多餘的右括號"))
      ;; 原子
      (t
       (cons (parse-atom token) rest)))))

(defun parse-float (s)
  "嘗試解析浮點數，失敗時拋出錯誤"
  (let ((n (read-from-string s)))
    (unless (numberp n) (error "不是數字"))
    n))

(defun read-expr (input)
  "解析字串，回傳第一個 S 表達式"
  (car (parse-tokens (tokenize input))))

(defun read-all-exprs (input)
  "解析字串中的所有 S 表達式"
  (let ((tokens (tokenize input))
        (exprs '()))
    (loop while tokens do
      (destructuring-bind (expr . remaining) (parse-tokens tokens)
        (push expr exprs)
        (setf tokens remaining)))
    (nreverse exprs)))

;;; ─── 求值器（Evaluator）───────────────────────────────────

(defun mini-eval (expr env)
  "對 expr 在 env 中求值（尾遞迴迴圈）"
  (loop
    (typecase expr
      ;; 自求值：數字、字串、布林
      ((or number string (eql t) null)
       (return expr))

      ;; 符號 → 環境查找
      (symbol
       (return (env-lookup expr env)))

      ;; 串列 → 特殊形式或函數呼叫
      (list
       (let ((head (car expr))
             (args (cdr expr)))
         (cond

           ;; (quote x)
           ((eq head 'quote)
            (return (car args)))

           ;; (quasiquote x)
           ((eq head 'quasiquote)
            (return (expand-quasiquote (car args) env)))

           ;; (if 條件 then else?)
           ((eq head 'if)
            (let ((test (mini-eval (car args) env)))
              (setf expr (if test (cadr args)
                               (if (cddr args) (caddr args) '())))
              ;; 繼續迴圈（尾呼叫最佳化）
              ))

           ;; (cond (測試 expr...) ...)
           ((eq head 'cond)
            (setf expr (expand-cond args))
            )

           ;; (and expr...)
           ((eq head 'and)
            (setf expr (expand-and args)))

           ;; (or expr...)
           ((eq head 'or)
            (setf expr (expand-or args)))

           ;; (when 條件 body...)
           ((eq head 'when)
            (setf expr `(if ,(car args) (begin ,@(cdr args)) '())))

           ;; (unless 條件 body...)
           ((eq head 'unless)
            (setf expr `(if ,(car args) '() (begin ,@(cdr args)))))

           ;; (define 名稱 值) 或 (define (fn args...) body...)
           ((eq head 'define)
            (cond
              ;; (define (f x y) body...)  →  縮寫語法
              ((listp (car args))
               (let* ((fname  (caar args))
                      (params (cdar args))
                      (body   (cdr args))
                      (fn     (make-closure :params params :body body :env env)))
                 (return (env-define fname fn env))))
              ;; (define x val)
              (t
               (let ((val (mini-eval (cadr args) env)))
                 (return (env-define (car args) val env))))))

           ;; (set! 名稱 值)
           ((eq head 'set!)
            (let ((val (mini-eval (cadr args) env)))
              (env-set! (car args) val env)
              (return val)))

           ;; (lambda (params...) body...)
           ((eq head 'lambda)
            (return (make-closure :params (car args)
                                  :body   (cdr args)
                                  :env    env)))

           ;; (begin expr...)
           ((eq head 'begin)
            (when (null args) (return '()))
            (loop for tail on args
                  when (null (cdr tail))
                    do (setf expr (car tail)) (loop-finish)
                  else
                    do (mini-eval (car tail) env)))

           ;; (let ((x v)...) body...)
           ((eq head 'let)
            (let* ((bindings (car args))
                   (body     (cdr args))
                   (names    (mapcar #'car bindings))
                   (vals     (mapcar (lambda (b) (mini-eval (cadr b) env)) bindings))
                   (new-env  (extend-env names vals env)))
              (setf env new-env
                    expr `(begin ,@body))))

           ;; (let* ((x v)...) body...)
           ((eq head 'let*)
            (let ((bindings (car args))
                  (body     (cdr args))
                  (cur-env  env))
              (dolist (b bindings)
                (let ((val (mini-eval (cadr b) cur-env)))
                  (setf cur-env (extend-env (list (car b)) (list val) cur-env))))
              (setf env  cur-env
                    expr `(begin ,@body))))

           ;; (letrec ((f (lambda...))...) body...)
           ((eq head 'letrec)
            (let* ((bindings (car args))
                   (body     (cdr args))
                   (names    (mapcar #'car bindings))
                   (new-env  (extend-env names (make-list (length names)) env)))
              (dolist (b bindings)
                (env-define (car b) (mini-eval (cadr b) new-env) new-env))
              (setf env  new-env
                    expr `(begin ,@body))))

           ;; (do ((var init step)...) (test result...) body...)
           ((eq head 'do)
            (return (eval-do args env)))

           ;; 函數呼叫
           (t
            (let ((fn   (mini-eval head env))
                  (vals (mapcar (lambda (a) (mini-eval a env)) args)))
              (setf expr (apply-fn fn vals env)))
            ))))

      (t (return expr)))))

(defun apply-fn (fn args env)
  "呼叫函數，若為閉包回傳 (body . new-env) 以便尾遞迴，
   若為內建函數直接執行"
  (cond
    ((functionp fn)
     ;; 內建函數：直接呼叫，回傳一個自求值的結果包裝
     (apply fn args))
    ((closure-p fn)
     ;; 用戶定義閉包：設置環境並繼續求值
     (let ((new-env (extend-env (closure-params fn) args (closure-env fn))))
       ;; 回傳 (begin body...) 的 cons，讓 mini-eval 尾遞迴
       `(begin ,@(closure-body fn) . ,new-env)))  ; 特殊回傳格式
    (t (error "不是可呼叫的函數: ~A" fn))))

;; 注意：為了真正的尾呼叫最佳化，我們需要調整 apply-fn
;; 讓 mini-eval 能接收並繼續迴圈
;; 以下重新定義 mini-eval 使用 trampoline 風格

(defun mini-eval (expr env)
  "對 expr 在 env 中求值（帶尾呼叫最佳化的迴圈）"
  (loop
    (typecase expr
      ((or number string (eql t) null)
       (return expr))
      (symbol
       (return (env-lookup expr env)))
      (list
       (let ((head (car expr))
             (args (cdr expr)))
         (cond
           ((eq head 'quote)  (return (car args)))

           ((eq head 'quasiquote) (return (expand-quasiquote (car args) env)))

           ((eq head 'if)
            (let ((test (mini-eval (car args) env)))
              (setf expr (if test (cadr args)
                               (if (cddr args) (caddr args) '())))))

           ((eq head 'cond) (setf expr (expand-cond args)))

           ((eq head 'and)  (setf expr (expand-and args)))
           ((eq head 'or)   (setf expr (expand-or args)))

           ((eq head 'when)
            (setf expr `(if ,(car args) (begin ,@(cdr args)) nil)))

           ((eq head 'unless)
            (setf expr `(if ,(car args) nil (begin ,@(cdr args)))))

           ((eq head 'define)
            (cond
              ((listp (car args))
               (let* ((fname  (caar args))
                      (params (cdar args))
                      (body   (cdr args))
                      (fn     (make-closure :params params :body body :env env)))
                 (return (env-define fname fn env))))
              (t
               (return (env-define (car args) (mini-eval (cadr args) env) env)))))

           ((eq head 'set!)
            (let ((val (mini-eval (cadr args) env)))
              (env-set! (car args) val env)
              (return val)))

           ((eq head 'lambda)
            (return (make-closure :params (car args) :body (cdr args) :env env)))

           ((eq head 'begin)
            (when (null args) (return nil))
            (loop for tail on args
                  if (null (cdr tail))
                    do (setf expr (car tail)) (loop-finish)
                  else
                    do (mini-eval (car tail) env)))

           ((eq head 'let)
            (destructuring-bind (bindings &rest body) args
              (let* ((names   (mapcar #'car bindings))
                     (vals    (mapcar (lambda (b) (mini-eval (cadr b) env)) bindings))
                     (new-env (extend-env names vals env)))
                (setf env new-env expr `(begin ,@body)))))

           ((eq head 'let*)
            (destructuring-bind (bindings &rest body) args
              (let ((cur env))
                (dolist (b bindings)
                  (setf cur (extend-env (list (car b))
                                        (list (mini-eval (cadr b) cur))
                                        cur)))
                (setf env cur expr `(begin ,@body)))))

           ((eq head 'letrec)
            (destructuring-bind (bindings &rest body) args
              (let* ((names   (mapcar #'car bindings))
                     (new-env (extend-env names (make-list (length names)) env)))
                (dolist (b bindings)
                  (env-define (car b) (mini-eval (cadr b) new-env) new-env))
                (setf env new-env expr `(begin ,@body)))))

           ;; 函數呼叫：若是閉包則尾遞迴，否則直接呼叫
           (t
            (let ((fn   (mini-eval head env))
                  (vals (mapcar (lambda (a) (mini-eval a env)) args)))
              (cond
                ((closure-p fn)
                 (setf env (extend-env (closure-params fn) vals (closure-env fn))
                       expr (if (= 1 (length (closure-body fn)))
                                (car (closure-body fn))
                                `(begin ,@(closure-body fn)))))
                ((functionp fn)
                 (return (apply fn vals)))
                (t
                 (error "不是可呼叫的物件: ~A" fn))))))))
      (t (return expr)))))

;;; ─── 輔助展開函數 ─────────────────────────────────────────

(defun expand-cond (clauses)
  "(cond (t1 e1) (t2 e2) ...) → 巢狀 if"
  (if (null clauses)
      'nil
      (let* ((clause  (car clauses))
             (test    (car clause))
             (body    (cdr clause)))
        (if (eq test 'else)
            `(begin ,@body)
            `(if ,test
                 (begin ,@body)
                 ,(expand-cond (cdr clauses)))))))

(defun expand-and (exprs)
  "(and e1 e2 ...) → 巢狀 if"
  (cond
    ((null exprs) t)
    ((null (cdr exprs)) (car exprs))
    (t `(if ,(car exprs) ,(expand-and (cdr exprs)) nil))))

(defun expand-or (exprs)
  "(or e1 e2 ...) → let 暫存避免重複求值"
  (cond
    ((null exprs) nil)
    ((null (cdr exprs)) (car exprs))
    (t (let ((tmp (gensym "OR")))
         `(let ((,tmp ,(car exprs)))
            (if ,tmp ,tmp ,(expand-or (cdr exprs))))))))

(defun expand-quasiquote (form env)
  "展開 quasiquote 形式"
  (cond
    ((atom form) form)
    ((and (listp form) (eq (car form) 'unquote))
     (mini-eval (cadr form) env))
    ((and (listp form) (listp (car form))
          (eq (caar form) 'unquote-splicing))
     (let ((spliced (mini-eval (cadar form) env))
           (rest    (expand-quasiquote (cdr form) env)))
       (append spliced rest)))
    (t
     (cons (expand-quasiquote (car form) env)
           (expand-quasiquote (cdr form) env)))))

;;; ─── 全域環境（內建函數）──────────────────────────────────

(defun make-global-env ()
  "建立包含所有內建函數的初始環境"
  (let ((env (make-env :bindings '() :parent nil)))

    ;; 算術
    (dolist (pair
             `((+ . ,#'+) (- . ,#'-) (* . ,#'*) (/ . ,#'/)
               (mod . ,#'mod) (remainder . ,#'rem)
               (abs . ,#'abs) (max . ,#'max) (min . ,#'min)
               (expt . ,#'expt) (sqrt . ,#'sqrt)
               (floor . ,#'floor) (ceiling . ,#'ceiling)
               (round . ,#'round) (truncate . ,#'truncate)
               (number->string . ,(lambda (n) (format nil "~A" n)))
               (string->number . ,(lambda (s) (or (ignore-errors (parse-integer s))
                                                   (ignore-errors (parse-float s))
                                                   nil)))))
      (push pair (env-bindings env)))

    ;; 比較
    (dolist (pair
             `((= . ,#'=) (< . ,#'<) (> . ,#'>) (<= . ,#'<=) (>= . ,#'>=)
               (equal? . ,#'equal) (eq? . ,#'eq) (eqv? . ,#'eql)
               (zero? . ,#'zerop) (positive? . ,#'plusp)
               (negative? . ,#'minusp) (odd? . ,#'oddp) (even? . ,#'evenp)))
      (push pair (env-bindings env)))

    ;; 布林
    (dolist (pair
             `((not . ,#'not)
               (boolean? . ,(lambda (x) (or (eq x t) (null x))))))
      (push pair (env-bindings env)))

    ;; 串列操作
    (dolist (pair
             `((cons . ,#'cons)
               (car . ,#'car) (cdr . ,#'cdr)
               (cadr . ,#'cadr) (caddr . ,#'caddr)
               (list . ,#'list)
               (null? . ,#'null) (pair? . ,#'consp)
               (list? . ,#'listp)
               (length . ,#'length)
               (append . ,#'append)
               (reverse . ,#'reverse)
               (list-ref . ,#'nth)
               (list-tail . ,#'nthcdr)
               (assoc . ,#'assoc)
               (member . ,#'member)
               (map . ,(lambda (fn lst) (mapcar (lambda (x) (funcall-closure fn (list x))) lst)))
               (for-each . ,(lambda (fn lst) (mapc (lambda (x) (funcall-closure fn (list x))) lst) nil))
               (filter . ,(lambda (fn lst) (remove-if-not (lambda (x) (funcall-closure fn (list x))) lst)))
               (reduce . ,(lambda (fn init lst) (reduce (lambda (a b) (funcall-closure fn (list a b))) lst :initial-value init)))
               (apply . ,(lambda (fn &rest args)
                           (let* ((all  (apply #'list args))
                                  (last (car (last all)))
                                  (head (butlast all)))
                             (funcall-closure fn (append head last)))))))
      (push pair (env-bindings env)))

    ;; 字串
    (dolist (pair
             `((string=? . ,#'string=)
               (string<? . ,#'string<)
               (string>? . ,#'string>)
               (string-length . ,#'length)
               (string-append . ,#'(lambda (&rest ss) (apply #'concatenate 'string ss)))
               (substring . ,#'subseq)
               (string-ref . ,#'char)
               (string-upcase . ,#'string-upcase)
               (string-downcase . ,#'string-downcase)
               (string? . ,#'stringp)
               (number? . ,#'numberp)
               (symbol? . ,#'symbolp)
               (procedure? . ,(lambda (x) (or (functionp x) (closure-p x))))))
      (push pair (env-bindings env)))

    ;; I/O 與雜項
    (dolist (pair
             `((display . ,(lambda (x) (format t "~A" (lisp->string x)) nil))
               (newline . ,(lambda () (terpri) nil))
               (write . ,(lambda (x) (format t "~S" x) nil))
               (print . ,(lambda (x) (format t "~%~A" (lisp->string x)) nil))
               (error . ,(lambda (msg &rest args)
                           (error (apply #'format nil msg args))))
               (gensym . ,#'gensym)
               (void . ,(lambda () nil))))
      (push pair (env-bindings env)))

    ;; 常數
    (env-define 'pi (* 4 (atan 1)) env)
    (env-define 'e  (exp 1)        env)
    (env-define 't  t              env)
    (env-define 'nil nil           env)

    env))

(defun funcall-closure (fn args)
  "呼叫閉包或內建函數"
  (cond
    ((closure-p fn)
     (mini-eval `(begin ,@(closure-body fn))
                (extend-env (closure-params fn) args (closure-env fn))))
    ((functionp fn)
     (apply fn args))
    (t (error "不是函數: ~A" fn))))

;;; ─── 輸出格式化 ───────────────────────────────────────────

(defun lisp->string (val)
  "將 Lisp 值轉成可讀字串"
  (cond
    ((null val)    "()")
    ((eq val t)    "#t")
    ((stringp val) (format nil "~S" val))
    ((closure-p val)
     (format nil "#<lambda (~{~A~^ ~})>" (closure-params val)))
    ((listp val)
     (format nil "(~{~A~^ ~})" (mapcar #'lisp->string val)))
    (t (format nil "~A" val))))

;;; ─── REPL ──────────────────────────────────────────────────

(defvar *global-env* nil)

(defun repl ()
  "互動式 Read-Eval-Print Loop"
  (setf *global-env* (make-global-env))
  (format t "~%Mini-Lisp 解譯器~%輸入 (quit) 退出~%~%")
  (loop
    (format t "lisp> ")
    (force-output)
    (let ((line (read-line *standard-input* nil nil)))
      (when (or (null line) (string= (string-trim " " line) "(quit)"))
        (format t "~%再見！~%")
        (return))
      (when (string= (string-trim " " line) "")
        (next-iteration))
      (handler-case
          (let* ((exprs (read-all-exprs line))
                 (result (reduce (lambda (acc e)
                                   (declare (ignore acc))
                                   (mini-eval e *global-env*))
                                 exprs :initial-value nil)))
            (format t "=> ~A~%" (lisp->string result)))
        (error (e)
          (format t "錯誤: ~A~%" e))))))

;;; ─── 主程式入口 ───────────────────────────────────────────

(defun main ()
  (repl))