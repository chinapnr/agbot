# @Time    : 2018/8/29  20:59
# @Desc    : 操作符
# @Author  : bin.zhang

from ast import literal_eval


class BinaryOperator:

    def __init__(self, env):
        self.env = env

    @property
    def mark(self):
        return ''

    @property
    def priority(self):
        return 0

    def apply(self, left, right):
        pass

    def __str__(self):
        return self.mark


class UnaryOperator:

    def __init__(self, env):
        self.env = env

    @property
    def mark(self):
        return ''

    @property
    def priority(self):
        return 0

    def apply(self, exp):
        pass

    def __str__(self):
        return self.mark


class LeftEvalBinaryOperator(BinaryOperator):
    pass


class Equal(BinaryOperator):

    @property
    def mark(self):
        return '=='

    @property
    def priority(self):
        return 7

    def apply(self, left, right):
        return str(left) == str(right)


class And(BinaryOperator):

    @property
    def mark(self):
        return '&'

    @property
    def priority(self):
        return 8

    def apply(self, left, right):
        return left and right


class Or(BinaryOperator):

    @property
    def mark(self):
        return '|'

    @property
    def priority(self):
        return 10

    def apply(self, left, right):
        return left or right


class Not(UnaryOperator):
    @property
    def mark(self):
        return '!'

    @property
    def priority(self):
        return 2

    def apply(self, exp):
        return not exp


class LessThan(BinaryOperator):

    @property
    def mark(self):
        return '<'

    @property
    def priority(self):
        return 6

    def apply(self, left, right):
        try:
            return float(left) < float(right)
        except ValueError:
            return str(left) < str(right)


class GreaterThan(BinaryOperator):

    @property
    def mark(self):
        return '>'

    @property
    def priority(self):
        return 6

    def apply(self, left, right):
        try:
            return float(left) > float(right)
        except ValueError:
            return str(left) > str(right)


class Plus(BinaryOperator):

    @property
    def mark(self):
        return '+'

    @property
    def priority(self):
        return 4

    def apply(self, left, right):
        return float(left) + float(right)


class Minus(BinaryOperator):

    @property
    def mark(self):
        return '-'

    @property
    def priority(self):
        return 4

    def apply(self, left, right):
        return float(left) - float(right)


class Multiply(BinaryOperator):

    @property
    def mark(self):
        return '*'

    @property
    def priority(self):
        return 3

    def apply(self, left, right):
        return float(left) * float(right)


class Divide(BinaryOperator):

    @property
    def mark(self):
        return '/'

    @property
    def priority(self):
        return 3

    def apply(self, left, right):
        return float(left) / float(right)


class Mode(BinaryOperator):

    @property
    def mark(self):
        return '%'

    @property
    def priority(self):
        return 3

    def apply(self, left, right):
        return int(left) % int(right)


class Access(LeftEvalBinaryOperator):

    @property
    def mark(self):
        return '.'

    @property
    def priority(self):
        return 1

    def apply(self, left, right):
        if left is None:
            return None
        else:
            if isinstance(left, dict):
                return left.get(right)
            elif isinstance(left, list):
                try:
                    return left[int(right)]
                except IndexError:
                    return None


# 判断是否是子集
class Subset(BinaryOperator):
    @property
    def mark(self):
        return '≤'

    @property
    def priority(self):
        return 7

    def apply(self, left, right):
        # 2019.3.26 新加子字符串也属于子集的情况
        if all([isinstance(left, str), isinstance(right, str)]):
            temp_left = left.replace(' ', '')
            temp_right = right.replace(' ', '')
            return temp_left in temp_right or temp_right in temp_left

        left_list = list()
        left_list = left_list if left_list else to_list(right)
        right_list = to_list(right)

        for i in range(0, len(right_list) - len(left_list) + 1):
            sub_right_list = []
            if not isinstance(right_list[i: i + len(left_list)], list):
                sub_right_list.append(right_list[i: i + len(left_list)])
            else:
                sub_right_list = right_list[i: i + len(left_list)]
            if left_list == sub_right_list:
                return True
        return False


# 判断是否属于
class Belong(BinaryOperator):
    @property
    def mark(self):
        return '∈'

    @property
    def priority(self):
        return 7

    def apply(self, left, right):
        left_str = str(left)
        right_str = str(right)
        if left_str in right_str:
            return True
        return False


def get_all_operator(env):
    all_operator = [
        Equal(env),
        And(env),
        Or(env),
        Not(env),
        LessThan(env),
        GreaterThan(env),
        Plus(env),
        Minus(env),
        Multiply(env),
        Divide(env),
        Mode(env),
        Access(env),
        Subset(env),
        Belong(env)
    ]
    return all_operator


# 转list
def to_list(value):
    if not isinstance(value, list):
        try:
            value_list = literal_eval(value)
        except Exception:
            raise Exception(str(value) + ',不符合list形式')
    else:
        value_list = value

    return value_list
