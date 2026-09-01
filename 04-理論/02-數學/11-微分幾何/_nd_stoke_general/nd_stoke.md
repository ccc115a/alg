# 向量微積分-廣義史托克定理

* 向量微積分-廣義史托克定理
    * 對話 -- https://gemini.google.com/app/80717f346aa181db
    * 分享 -- https://gemini.google.com/share/3faa664554cc
    * 程式 -- https://aistudio.google.com/prompts/1sQq5exslz6-iNfAD9tCQqkPY7LaYZ_-w
    * 程式解說 -- https://gemini.google.com/app/b76a8e6971917162

## Q: 廣義斯托克斯定理的數學表達式如下：$$\int_{M} d\omega = \int_{\partial M} \omega$$

我想寫一個 python 函數，可以計算 $\int_{M} d\omega$ ，另外再寫一個計算  $\int_{\partial M} \omega$ ，然後驗證兩者相等

但由於需要定義 M, 還有積分函數 f, 以及 $\omega$ ，這些可以當成參數傳進去，

...

然後經過一系列對話，AI 寫出了習題中的 nd_stoke.py 程式，其中核心的積分函數如下

```py
# ==============================================================================
# 2. 通用積分引擎 (支援 k-維積分)
# ==============================================================================
def integrate_form_on_manifold(
    omega: DifferentialForm,
    manifold_map: List[sp.Expr], 
    bounds: List[Tuple[float, float]]
) -> float:
    """
    計算 ∫_M ω。使用 Pullback 與 Jacobian。
    """
    k = omega.degree
    dim = omega.dim
    
    # 確保參數化是 SymPy 物件
    manifold_map = [sp.sympify(m) for m in manifold_map]
    
    # 定義符號
    X = [sp.symbols(f'x{i}') for i in range(dim)]
    # 參數符號 u0, u1, ...
    U = [sp.symbols(f'u{i}') for i in range(k)]
    
    # 替換字典 x -> phi(u)
    subs_map = {X[i]: manifold_map[i] for i in range(dim)}
    
    # --- 特殊情況: k=0 (點積分 / 函數求值) ---
    if k == 0:
        # 0-form 只有一項: {(): expression}
        val = 0
        for _, expr in omega.data.items():
            val += float(expr.subs(subs_map))
        return val

    # --- 一般情況: k > 0 ---
    # 計算 Jacobian 矩陣 J[i][j] = dx_i / du_j
    J = sp.Matrix([[sp.diff(m, U[j]) for j in range(k)] for m in manifold_map])
    
    total_integrand = 0
    
    for indices, expr in omega.data.items():
        # indices 對應 dx_i ^ dx_j ...
        # 提取 Jacobian 對應的列 (rows) 構成子矩陣
        sub_matrix = J[list(indices), :]
        det_J = sub_matrix.det()
        
        # Pullback: f(phi(u))
        coeff_pulled = expr.subs(subs_map)
        
        total_integrand += coeff_pulled * det_J
        
    if total_integrand == 0: return 0.0

    # 使用 scipy.integrate.nquad
    # nquad 要求 bounds 順序對應 u0, u1...
    func_np = sp.lambdify(U, total_integrand, 'numpy')
    
    # 包裝函數處理常數返回
    def safe_func(*args):
        return func_np(*args)

    ranges = [[b[0], b[1]] for b in bounds]
    val, _ = integrate.nquad(safe_func, ranges)
    return val
```

## ccc: 請說明上述 integrate_form_on_manifold 函數對應的數學，各個參數對應到什麼變數，代表的意義是什麼等等

這是一個非常核心的問題。`integrate_form_on_manifold` 這個函數本質上是在實作微分幾何中的 **「拉回」（Pullback）** 運算與積分定義。

數學上，我們計算的是一個 **$k$-維微分形式 $\omega$** 在一個參數化的 **$k$-維流形 $M$** 上的積分：

$$ \int_M \omega $$

為了計算這個積分，我們必須將物理空間（例如 $\mathbb{R}^N$）中的 $\omega$ **拉回** 到參數空間（$\mathbb{R}^k$）中，變成一個標準的黎曼積分。公式如下：

$$ \int_M \omega = \int_D \Phi^* \omega $$

以下是程式碼參數與數學概念的詳細對照：

---

### 1. 函數參數對照表

#### (1) `omega: DifferentialForm`
*   **數學符號**：$\omega$ (微分形式)
*   **數學定義**：
    $$ \omega = \sum_{I} f_I(x_1, \dots, x_N) \, dx_{i_1} \wedge dx_{i_2} \wedge \dots \wedge dx_{i_k} $$
    其中 $I = (i_1, \dots, i_k)$ 是索引組合。
*   **程式意義**：
    *   `omega.dim` 是嵌入空間維度 $N$。
    *   `omega.degree` 是積分維度 $k$。
    *   `omega.data` 儲存了每一項的係數函數 $f_I$。
    *   **例子**：在 3D 中的通量形式 $P \, dy \wedge dz$，這裡 $f=P$, $I=(1, 2)$（對應 $y, z$）。

#### (2) `manifold_map: List[sp.Expr]`
*   **數學符號**：$\Phi(u_1, \dots, u_k)$ (參數化映射)
*   **數學定義**：這是一個從參數區域 $D \subset \mathbb{R}^k$ 到流形 $M \subset \mathbb{R}^N$ 的映射：
    $$ \Phi: (u_1, \dots, u_k) \mapsto (x_1, \dots, x_N) $$
    $$ x_i = \phi_i(u_1, \dots, u_k) $$
*   **程式意義**：這是一個列表，第 $i$ 個元素代表座標 $x_i$ 如何用參數 $u$ 表示。
*   **例子**：球面參數化 $x = \sin\phi \cos\theta, y = \sin\phi \sin\theta, z = \cos\phi$。

#### (3) `bounds: List[Tuple[float, float]]`
*   **數學符號**：$D$ (積分區域 / 參數域)
*   **數學定義**：參數 $u_1, \dots, u_k$ 的積分範圍。
    $$ D = [a_1, b_1] \times [a_2, b_2] \times \dots \times [a_k, b_k] $$
*   **程式意義**：決定了定積分的上下限。

---

### 2. 函數內部的數學邏輯

函數的核心任務是計算 $\Phi^* \omega$（$\omega$ 的拉回）。這包含三個步驟，對應程式碼中的關鍵行：

#### 步驟 A：計算全雅可比矩陣 (Jacobian Matrix)
*   **程式碼**：
    ```python
    J = sp.Matrix([[sp.diff(m, U[j]) for j in range(k)] for m in manifold_map])
    ```
*   **數學意義**：計算切向量矩陣。
    $$ J = \frac{\partial(x_1, \dots, x_N)}{\partial(u_1, \dots, u_k)} = \begin{pmatrix} 
    \frac{\partial x_1}{\partial u_1} & \dots & \frac{\partial x_1}{\partial u_k} \\
    \vdots & \ddots & \vdots \\
    \frac{\partial x_N}{\partial u_1} & \dots & \frac{\partial x_N}{\partial u_k}
    \end{pmatrix} $$
    這是一個 $N \times k$ 的矩陣。每一列 (column) 代表一個切向量 $\frac{\partial \mathbf{r}}{\partial u_j}$。

#### 步驟 B：基底形式的拉回 (Pullback of Basis Forms)
*   **程式碼**：
    ```python
    sub_matrix = J[list(indices), :]
    det_J = sub_matrix.det()
    ```
*   **數學意義**：
    根據微分形式的拉回規則：
    $$ \Phi^*(dx_{i_1} \wedge \dots \wedge dx_{i_k}) = \det\left( \frac{\partial(x_{i_1}, \dots, x_{i_k})}{\partial(u_1, \dots, u_k)} \right) du_1 \wedge \dots \wedge du_k $$
    *   我們需要計算 $dx_{i_1} \wedge \dots \wedge dx_{i_k}$ 如何變換成 $du_1 \wedge \dots \wedge du_k$。
    *   這等於是從全雅可比矩陣 $J$ 中，挑出對應的 $k$ 個列 (rows, 即 $i_1 \dots i_k$)，組成一個 $k \times k$ 的子矩陣。
    *   計算這個子矩陣的**行列式 (Determinant)**，這就是變換係數（也就是廣義的面積/體積放大率）。

#### 步驟 C：係數函數的代換 (Substitution)
*   **程式碼**：
    ```python
    coeff_pulled = expr.subs(subs_map)
    total_integrand += coeff_pulled * det_J
    ```
*   **數學意義**：
    將形式前面的係數函數 $f(x)$ 中的 $x$ 替換為參數 $\Phi(u)$。
    $$ \Phi^*(f(x) \, dx_I) = f(\Phi(u)) \cdot \det(J_I) \, du_1 \wedge \dots \wedge du_k $$

#### 步驟 D：數值積分
*   **程式碼**：
    ```python
    val, _ = integrate.nquad(safe_func, ranges)
    ```
*   **數學意義**：
    最後，所有的微分項都變成了 $du_1 \wedge \dots \wedge du_k$（即標準體積元素 $du_1 \dots du_k$），我們只需對前面的純量函數進行多重積分：
    $$ \int_{a_k}^{b_k} \dots \int_{a_1}^{b_1} \left( \sum_I f_I(\Phi(u)) \det(J_I) \right) \, du_1 \dots du_k $$

---

### 3. 舉例說明 (以高斯定理的左式為例)

假設我們要計算高斯定理中的 $\int_M d\omega$，其中 $M$ 是一個 3D 立方體 ($k=3, N=3$)。

1.  **微分形式**：假設 $d\omega = \text{div}(\mathbf{F}) \, dx \wedge dy \wedge dz$。
    *   `omega.data` 對應 `{ (0, 1, 2): div(F) }`。
2.  **參數化**：$x=u, y=v, z=w$ (單位變換)。
3.  **雅可比矩陣**：
    $$ J = \begin{pmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{pmatrix} $$
4.  **拉回計算**：
    *   取出 rows (0, 1, 2)，這就是 $J$ 本身。
    *   `det_J` = $\det(I) = 1$。
    *   被積函數 = $\text{div}(\mathbf{F})(u,v,w) \times 1$。
5.  **積分**：對 $\text{div}(\mathbf{F})$ 進行三重積分。

這正是高斯散度定理中 $\iiint_V (\nabla \cdot \mathbf{F}) \, dV$ 的定義。

## Q: 接著說明驗證函數 def verify_stokes_general(name, dim, k, omega_data, M_map, bounds): 的設計原理，要先用數學講解，然後說明程式碼

這段程式碼的設計核心在於**「如何將抽象的幾何邊界，轉化為程式可以迭代的代數運算」**。

`verify_stokes_general` 的功能是同時計算等號兩邊並進行比對。我們分兩部分來講解：先講數學原理，再對照程式碼實作。

---

### 第一部分：數學原理

廣義斯托克斯定理的公式為：
$$ \int_M d\omega = \int_{\partial M} \omega $$

#### 1. 左式 (LHS)：$\int_M d\omega$
這部分相對直觀。
*   **幾何意義**：計算微分形式的外微分 $d\omega$ 在整個流形 $M$ 內部的積分。
*   **操作步驟**：
    1.  對 $\omega$ 進行微分運算得到 $d\omega$ (階數從 $k-1$ 升到 $k$)。
    2.  將 $M$ 參數化為 $k$ 維的參數區域（例如 $N$ 維空間中的一個 $k$ 維超立方體）。
    3.  直接進行 $k$ 重積分。

#### 2. 右式 (RHS)：$\int_{\partial M} \omega$ (設計難點)
這部分最困難的是**「如何定義並遍歷邊界 $\partial M$」**。

在參數空間中，我們的流形 $M$ 通常定義為一個 **$k$-維超立方體 (Hypercube)**：
$$ D = [a_0, b_0] \times [a_1, b_1] \times \dots \times [a_{k-1}, b_{k-1}] $$

一個 $k$ 維超立方體的邊界 $\partial M$ 由 **$2k$ 個 $(k-1)$ 維的面 (Faces)** 組成。
*   對於每一個參數 $u_i$ (其中 $i=0 \dots k-1$)，都有兩個面：
    1.  **下界面 (Min Face)**：$u_i = a_i$
    2.  **上界面 (Max Face)**：$u_i = b_i$

**定向 (Orientation) 規則**：
邊界積分不是簡單的加總，必須考慮方向（法向量朝外）。根據數學上的誘導定向規則，第 $i$ 個參數方向的邊界符號為：
$$ \partial M = \sum_{i=0}^{k-1} (-1)^i \left( M|_{u_i=b_i} - M|_{u_i=a_i} \right) $$

*   **$u_i = b_i$ (Max Face)** 的係數是 $(-1)^i$
*   **$u_i = a_i$ (Min Face)** 的係數是 $- (-1)^i = (-1)^{i+1}$

---

### 第二部分：程式碼對照與實作

現在我們來看 `verify_stokes_general` 函數的內部邏輯，看看它如何實現上述數學。

```python
def verify_stokes_general(name, dim, k, omega_data, M_map, bounds):
```
*   **`dim`**: 嵌入空間維度 $N$。
*   **`k`**: 流形維度。
*   **`M_map`**: 參數化映射 $\Phi(u_0, \dots, u_{k-1})$。

#### 1. 左式計算 (LHS)
```python
    # 1. 建構微分形式 ω ((k-1)-form)
    omega = DifferentialForm(dim, k-1, omega_data)
    
    # 2. 計算外微分 dω (變成 k-form)
    d_omega = omega.exterior_derivative()
    
    # 3. 在 M 上積分 (k 維積分)
    lhs = integrate_form_on_manifold(d_omega, M_map, bounds)
```
*   **對應數學**：直接對應 $\int_M d\omega$。利用 `DifferentialForm` 類別自動處理了 $d\omega$ 的複雜符號運算，再傳給積分器。

#### 2. 右式計算 (RHS) - 邊界的迴圈
這是程式的精華所在。我們不需要手動寫出邊界的參數化，而是透過**降維 (Parameter Reduction)** 動態生成。

```python
    rhs = 0.0
    U = [sp.symbols(f'u{i}') for i in range(k)] # 原始參數 [u0, u1, ... uk-1]
    
    # 遍歷每一個維度 i (從 0 到 k-1)
    for i in range(k):
        u_min, u_max = bounds[i]
        
        # 定義邊界的參數 V，數量比 U 少一個 (k-1 個)
        # 也就是把 U[i] 抽掉後剩下的參數
        V = [sp.symbols(f'u{j}') for j in range(k-1)] 
        
        # 輔助函數：建立「參數代換字典」
        # 將 U[i] 固定為常數 (boundary_val)，其餘 U[j] 映射到新的參數 V
        def make_subs(fixed_val):
            mapping = {}
            v_idx = 0
            for j in range(k):
                if j == i: mapping[U[j]] = fixed_val # 固定第 i 個參數
                else: 
                    mapping[U[j]] = V[v_idx]         # 其餘參數依序填入 V
                    v_idx += 1
            return mapping
```

**解釋：**
如果 $M$ 是 3D 立方體 ($u, v, w$)，我們現在處理 $i=0$ (即 $u$) 的邊界。
*   `make_subs` 會把 $u$ 變成常數（例如 0 或 1）。
*   剩下的 $v, w$ 會被視為新平面的參數 $u'_0, u'_1$。

#### 3. 計算上下界面的積分與符號

```python
        # --- 下界面 (Face Min): u_i = u_min ---
        # 1. 將 M_map 中的 u_i 替換為常數 u_min
        M_min = [m.subs(make_subs(u_min)) for m in M_map]
        
        # 2. 積分範圍也要降維 (移除第 i 個範圍)
        bounds_sub = bounds[:i] + bounds[i+1:]
        
        # 3. 計算積分 (遞迴概念：這是 k-1 維積分)
        val_min = integrate_form_on_manifold(omega, M_min, bounds_sub)
        
        # --- 上界面 (Face Max): u_i = u_max ---
        M_max = [m.subs(make_subs(u_max)) for m in M_map]
        val_max = integrate_form_on_manifold(omega, M_max, bounds_sub)
        
        # --- 符號法則 (Orientation) ---
        # 下界面係數 (-1)^(i+1)，上界面係數 (-1)^i
        rhs += ((-1)**(i+1)) * val_min + ((-1)**i) * val_max
```

**符號驗證 (以 2D 格林定理為例)**：
設 $u_0=x, u_1=y$。
*   **$i=0$ (x方向)**:
    *   **Max ($x=1$, 右邊界)**: 係數 $(-1)^0 = +1$。積分方向向上 $dy>0$。 (符合)
    *   **Min ($x=0$, 左邊界)**: 係數 $(-1)^{0+1} = -1$。積分方向 $dy>0$，但幾何上左邊界應該向下走 ($dy<0$)。這裡我們的參數 $V$ (即 $y$) 仍是從 0 到 1 積分，所以積分值是正的，乘上係數 $-1$ 代表「反向/向下」。 (符合)
*   **$i=1$ (y方向)**:
    *   **Max ($y=1$, 上邊界)**: 係數 $(-1)^1 = -1$。幾何上需向左走 ($dx<0$)。參數 $V$ ($x$) 0 到 1 積分為正，乘上 $-1$ 變負。 (符合)
    *   **Min ($y=0$, 下邊界)**: 係數 $(-1)^{1+1} = +1$。幾何上向右走 ($dx>0$)。 (符合)

### 總結

`verify_stokes_general` 的設計美學在於它**沒有寫死任何幾何形狀**。它利用：
1.  **SymPy 的 `subs`**：實現了數學上的「限制映射」($\Phi|_{\partial M}$)。
2.  **迴圈與列表切片**：實現了對 $2k$ 個邊界的遍歷。
3.  **`(-1)**i`**：精確實現了同調代數中的邊界算子 (Boundary Operator) $\partial$。

這使得同一段程式碼既能算線積分，也能算 5 維超體積的表面通量，完全體現了廣義斯托克斯定理的統一性。