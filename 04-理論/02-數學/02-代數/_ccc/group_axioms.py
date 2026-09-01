
NUM_TEST_CASES = 100

# 1. 封閉性 (Closure)
def check_closure(g):
    for _ in range(NUM_TEST_CASES):
        a = g.random_generate()
        b = g.random_generate()
        result = g.operation(a, b)
        assert g.include(result), f"Closure failed: {a} op {b} = {result} is not in G"

# 2. 結合性 (Associativity)
def check_associativity(g):
    for _ in range(NUM_TEST_CASES):
        a = g.random_generate()
        b = g.random_generate()
        c = g.random_generate()
        assert g.operation(g.operation(a, b), c) == g.operation(a, g.operation(b, c)), \
            f"Associativity failed: ({a} op {b}) op {c} != {a} op ({b} op {c})"

# 3. 單位元素 (Identity Element)
def check_identity_element(g):
    for _ in range(NUM_TEST_CASES):
        a = g.random_generate()
        # 左單位元素
        assert g.operation(a, g.identity) == a, \
            f"Left identity failed: {a} op {g.identity} != {a}"
        # 右單位元素
        assert g.operation(g.identity, a) == a, \
            f"Right identity failed: {identity} op {a} != {a}"

# 4. 反元素 (Inverse Element)
def check_inverse_element(g):
    for _ in range(NUM_TEST_CASES):
        a = g.random_generate()
        # 加法的反元素是負號
        # 這裡我們需要一個函式來計算反元素，因為它不是固定的運算

        a_inverse = g.inverse(a)

        # 檢查反元素是否也在集合 G 中 (對於整數，-a 仍然是整數)
        assert g.include(a_inverse), f"Inverse {a_inverse} for {a} is not in G"

        # 檢查左反元素
        assert g.operation(a, a_inverse) == g.identity, \
            f"Left inverse failed: {a} op {a_inverse} != {g.identity}"
        # 檢查右反元素
        assert g.operation(a_inverse, a) == g.identity, \
            f"Right inverse failed: {a_inverse} op {a} != {g.identity}"

# 5. 交換性 (Commutativity)
def check_commutativity(g):
    for _ in range(NUM_TEST_CASES):
        a = g.random_generate()
        b = g.random_generate()
        assert g.operation(a, b) == g.operation(b, a), \
            f"Commutativity failed: {a} op {b} != {b} op {a}"
            
def check_group_axioms(g):
    check_closure(g)
    check_associativity(g)
    check_identity_element(g)
    check_inverse_element(g)
    print("All group axioms passed!")

def check_commutative_group(g):
    check_closure(g)
    check_associativity(g)
    check_identity_element(g)
    check_inverse_element(g)
    check_commutativity(g)
    print("交換群公理全部通過！")