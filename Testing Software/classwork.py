# a = [1, 2, 3, 4, 5, 6]
#
# b = a[:]
#
# print(a)
# print(b)
#
# b[2] = 0
#
# print(a)
# print(b)
#
#
# sentence = "Hello, I am Anshu Gupta"
#
# def consonent(letter):
#     vowel = "aeiou"
#     return letter.isaplpha() and letter.lower() in vowel

# # Generator
#
# def number_n(n):
#     for i in range(n):
#         yield i

# a = list(number_n(5))
# print(a)

# class Student():
#     rollno = None
#     name = None
#     age = None
#     address = None
#     branch = None
#     def __init__(self, rollno, name, age, address, branch):
#         self.rollno = rollno
#         self.name = name
#         self.age = age
#         self.address = address
#         self.branch = branch
#
#
# s1 = Student()

class Account():
    def __init__(self, accNo, accBalance):
        self.__accNo = accNo
        self.__accBalance = accBalance

    def set_accNo(self, accNo):
        self.__accNo = accNo

    def get_accNo(self):
        return self.__accNo

    def set_accBalance(self, accBalance):
        self.__accBalance = accBalance

    def get_accBalance(self):
        return f"{self.__accNo} {self.__accBalance}"

    def creditAmount(self, amount):
        self.__accBalance += amount
        return "Amount Successfully Credited"

    def debitAmount(self, amount):
        if self.__accBalance <= amount:
            return "Low Balance"

        self.__accBalance -= amount

        if self.__accBalance <= 1000:
            return "Minimum Balance"

        return "Amount Successfully Debited"

    def transfer(self, name, amount):
        value = self.debitAmount(amount)

        if value == "Low Balance":
            return "Insufficient Funds"

        name.creditAmount(amount)
        return "Amount Successfully Debited"

Ag = Account(1, 5000)
Paras = Account(2, 6000)



print(Ag.transfer(Paras, 200))

print(Ag.get_accBalance())
print(Paras.get_accBalance())


def add_string(str1):
    print(str1[-3:])
    if len(str1) < 3:
        return str1
    if str1[-3:] == "ing":
        str1 += "ly"
    else:
        str1 += "ing"

    return str1

str1 = "coming"
print(add_string(str1))


# lex_auth_0127135773590405121141

def bracket_pattern(input_str):
    if input_str[0] == ")" or input_str[len(input_str) - 1] == "(":
        return False

    dic = {"(": 0}
    for i in input_str:
        print(i)
        if i == "(":
            dic[i] += 1
        else:
            dic["("] -= 1

    if dic["("] != 0:
        return False
    return True


input_str = "(())()"
print(bracket_pattern(input_str))


# lex_auth_0127135787454873601143

def create_new_dictionary(prices):
    new_dict = {}

    for i in prices:
        if prices[i] > 200:
            new_dict[i] = prices[i]

    return new_dict


prices = {'ACME': 45.23, 'AAPL': 612.78, 'IBM': 205.55, 'HPQ': 37.20, 'FB': 10.75}
print(create_new_dictionary(prices))


# lex_auth_0127135811649044481146

def find_nine(nums):
    if 9 in nums[0:4]:
        return True
    return False


nums = [1, 9, 4, 5, 6]
print(find_nine(nums))


def list123(nums):

    for i in range(0, len(nums)-3):
        if i == 1:
            for j in range(i, i+4):
                pass



nums = [1, 2, 3, 4, 5]
print(list123(nums))

# Aggregation
class Account:
    def __init__(self, acc_no, acc_name):
        self.acc_num = acc_no
        self.acc_name = acc_name

class Customer:
    def __init__(self, custid, custname):
        self.custid = custid
        self.custname = custname

class Bank:

    customer = None

    def __init__(self, accobj):
        self.account = accobj
    def print_account_details(self):
        print()
acc1 = Account(1, 'abc')

cust1 = Customer(1, 'XYZ')

B1 = Bank(acc1)
B1.customer = cust1

print(B1.__dict__)
print(B1.customer)

# Single level inheritance

class Person:
    def __init__(self, name, age, sex):
        self.name = name
        self.age = age
        self.sex = sex

class Student(Person):
    def __init__(self):
        print('student')


s1 = Student()