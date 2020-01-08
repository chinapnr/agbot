from .AST import AST
from .Operator import get_all_operator
from .Tokenizer import Tokenizer


def run(exp, env):
    """
    执行断言
    :param exp:  断言条件
    :param env:  api 返回
    :return:
    """
    ao = get_all_operator(env)
    tokens = Tokenizer(ao).tokenizer(exp)
    return AST(ao, tokens).eval(env)


def get_ast(exp, env):
    ao = get_all_operator(env)
    tokens = Tokenizer(ao).tokenizer(exp)
    return AST(ao, tokens)


# 用于判断是否包含表达式符号
def is_exp(exp):
    ao = get_all_operator('')
    for i in range(0, len(ao)):
        if '.' != ao[i].mark and ao[i].mark in exp:
            return True
    return False
