from enum import Enum

from operator import and_, or_, xor


class ValidatorBinOp(Enum):
    AND = {
        "func": and_,
        "initial": True
    }
    OR = {
        "func": or_,
        "initial": False
    }
    XOR = {
        "func": xor,
        "initial": False
    }

    @property
    def func(self):
        return self.value["func"]

    @property
    def initial(self):
        return self.value["initial"]
