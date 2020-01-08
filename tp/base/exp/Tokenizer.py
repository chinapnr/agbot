# @Time    : 2018/8/29  20:59
# @Desc    : 表达式切割器
# @Author  : bin.zhang

class Tokenizer:

    def __init__(self, all_operator):
        self.all_operator = all_operator

    def __op_start_idx(self, ce):
        for c in ['(', ')', '{', '}']:
            idx = ce.find(c[0])
            if idx != -1:
                return c, idx
        for op in self.all_operator:
            idx = ce.find(op.mark[0])
            if idx != -1:
                return op.mark, idx

    def __op_idx(self, ce, oi):
        for c in ['(', ')', '{', '}']:
            if c == ce or c.startswith(oi[0]):
                return c, oi[1]
        for op in self.all_operator:
            if op.mark == ce:
                return op.mark, oi[1]
            elif op.mark.startswith(oi[0]):
                hit_mark = ce[0: len(op.mark)]
                if hit_mark == op.mark:
                    return op.mark, oi[1]

    def tokenizer(self, exp):
        tokens = []
        not_op = []
        i = 0
        while i < len(exp):
            ce = exp[i]
            if len(ce.strip()) == 0:
                i = i + 1
                continue
            oi = self.__op_start_idx(ce)
            if oi is None:
                not_op.append(ce)
                i = i + 1
            else:
                if len(not_op) > 0:
                    tk0 = ''.join(not_op)
                    not_op.clear()
                    tokens.append(tk0)
                ce_ex = exp[i: i + 2]
                oi_ex = self.__op_idx(ce_ex, oi)
                if oi_ex is None:
                    not_op.append(ce)
                    i = i + len(ce)
                else:
                    tk1 = oi_ex[0]
                    tokens.append(tk1)
                    i = i + len(oi_ex[0])
        if len(not_op) > 0:
            tokens.append(''.join(not_op))
        return tokens
