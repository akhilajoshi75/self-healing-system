# Program 5: Multiplication Table
n = int(input("Enter a number: "))
for i in range(1, 11):
    print(f"{n} * {i} = {n*i}")

# Program 6: Armstrong Number Check
n = int(input("Enter number to check for Armstrong: "))
n_str = str(n)
n_len = len(n_str)
sum = 0
for d in n_str:
    sum += int(d) ** n_len
if sum == n:
    print(f"{n} is an Armstrong number")
else:
    print("NO")

# Program 7: Palindrome Check
def is_palindrome(s):
    return s == s[::-1]
string = input("Enter string: ")
res = is_palindrome(string)
if res:
    print("Yes, Palindrome")
else:
    print("No")

# Program 8: Fibonacci Series (First n Terms)
n = int(input("Fibonacci terms: "))
a, b = 0, 1
print(a, b, end=" ")
for _ in range(2, n+1):
    c = a + b
    print(c, end=" ")
    a = b
    b = c

# Program 9: Right-Aligned Triangle Pattern
def tri(r):
    for i in range(1, r + 1):
        for j in range(r - i):
            print(" ", end="")
        for k in range(i):
            print("*", end=" ")
        print()
tri(7)

# Program 10: Diamond Star Pattern
def diamond(n):
    for i in range(1, n + 1):
        print(" " * (n - i), end="")
        print("* " * i)
    for i in range(n, 0, -1):
        print(" " * (n - i), end="")
        print("* " * i)
diamond(3)

# Program 11: Number Triangle Pattern
def num(r):
    for i in range(1, r + 1):
        for j in range(1, i + 1):
            print(j, end=" ")
        print()
num(5)

# Program 12: Perfect Number Check
n = int(input("Enter number to check for perfect: "))
sum = 0
for i in range(1, n):
    if n % i == 0:
        sum += i
if sum == n:
    print("Yes, perfect number")
else:
    print("No")

# Program 13: Prime Number Check
n = int(input("Enter number to check for prime: "))
for i in range(2, n):
    if n % i == 0:
        print("Not prime")
        break
else:
    print("Prime")

# Program 14: Amicable Numbers Check
x = int(input("Enter x: "))
y = int(input("Enter y: "))
s1 = 0
s2 = 0
for i in range(1, x):
    if x % i == 0:
        s1 += i
for j in range(1, y):
    if y % j == 0:
        s2 += j
if s1 == y and s2 == x:
    print("Amicable")
else:
    print("Not amicable")

# Program 15: Strong Number Check
def is_strong(n):
    temp = n
    sum = 0
    while n > 0:
        dig = n % 10
        fact = 1
        for i in range(1, dig + 1):
            fact *= i
        sum += fact
        n //= 10
    return sum == temp

num = int(input("Enter number to check for strong: "))
if is_strong(num):
    print("Yes, strong number")
else:
    print("No")

# Program 16: Roots of a Quadratic Equation
import cmath
a = int(input("Enter a: "))
b = int(input("Enter b: "))
c = int(input("Enter c: "))
d = (b * b) - (4 * a * c)
r1 = (-b + cmath.sqrt(d)) / (2 * a)
r2 = (-b - cmath.sqrt(d)) / (2 * a)
print(f"{r1} and {r2} are the roots of the equation")

# Program 17: Fibonacci using Function
def fibonacci(n):
    a, b = 0, 1
    print(a, b, end=" ")
    for _ in range(2, n + 1):
        c = a + b
        print(c, end=" ")
        a = b
        b = c
fibonacci(5)

# Program 18: Count Occurrence of Element in List
def count_lst(lst, x):
    count = 0
    for ele in lst:
        if ele == x:
            count += 1
    return count
print(count_lst([8, 10, 25, 8, 9, 8, 6], 6))

# Program 19: Transpose of a Matrix (User Input)
def transpose(m):
    t = []
    for i in range(len(m[0])):
        new_row = []
        for j in range(len(m)):
            new_row.append(m[j][i])
        t.append(new_row)
    return t

r = int(input("Rows: "))
c = int(input("Cols: "))
m = []
for i in range(r):
    rows = list(map(int, input(f"Enter elements of row {i + 1}: ").split()))
    m.append(rows)

print("Original Matrix:")
for row in m:
    print(row)
print("\nTransposed Matrix:")
transposed = transpose(m)
for row in transposed:
    print(row)

# Program 20: Matrix Multiplication (User Input)
def multiply_matrices(A, B):
    res = []
    for i in range(len(A)):
        new_row = []
        for j in range(len(B[0])):
            sum = 0
            for k in range(len(B)):
                sum += A[i][k] * B[k][j]
            new_row.append(sum)
        res.append(new_row)
    return res

r1 = int(input("Rows of A: "))
c1 = int(input("Cols of A: "))
r2 = int(input("Rows of B: "))
c2 = int(input("Cols of B: "))

if c1 != r2:
    print("Matrix multiplication is not possible")
    exit()

print("Enter matrix A:")
A = []
for i in range(r1):
    row = list(map(int, input(f"Enter elements of row {i + 1}: ").split()))
    A.append(row)

print("Enter matrix B:")
B = []
for i in range(r2):
    row = list(map(int, input(f"Enter elements of row {i + 1}: ").split()))
    B.append(row)

result = multiply_matrices(A, B)

print("Resultant Matrix:")
for row in result:
    print(row)