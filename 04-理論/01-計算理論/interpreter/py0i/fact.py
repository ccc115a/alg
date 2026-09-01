def factorial(n: int) -> int:
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

result: int = factorial(5)
print("factorial(5)=", result)