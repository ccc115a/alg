from group_axioms import *

# 6. 分配律 (Distributivity)
def check_distributivity(f):
    """檢驗乘法對加法的分配律"""
    print("--- 檢驗分配律 ---")
    for _ in range(NUM_TEST_CASES):
        a = f.add_group.random_generate()
        b = f.add_group.random_generate()
        c = f.add_group.random_generate()

        # 左分配律: a * (b + c) = (a * b) + (a * c)
        lhs = f.mul_group.operation(a, f.add_group.operation(b, c))
        rhs = f.add_group.operation(f.mul_group.operation(a, b), f.mul_group.operation(a, c))
        assert lhs == rhs, \
            f"Left distributivity failed: {a} * ({b} + {c}) != ({a} * {b}) + ({a} * {c})"

        # 右分配律: (a + b) * c = (a * c) + (b * c)
        lhs = f.mul_group.operation(f.add_group.operation(a, b), c)
        rhs = f.add_group.operation(f.mul_group.operation(a, c), f.mul_group.operation(b, c))
        assert lhs == rhs, \
            f"Right distributivity failed: ({a} + {b}) * {c} != ({a} * {c}) + ({b} * {c})"
    print("分配律通過！")

def check_field_axioms(f):
    """
    檢驗一個有限體的完整公理。
    需要傳入加法和乘法模組物件。
    """
    check_commutative_group(f.add_group)
    print("-" * 30)
    check_commutative_group(f.mul_group)
    print("-" * 30)
    check_distributivity(f)
    print("\n恭喜！所有有限體公理檢驗成功！")
