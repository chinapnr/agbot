from typing import List, Dict

weight_high = 10
weight_low = 1
weight_medial = 5

weight_alias = {
    'l': weight_low,
    'm': weight_medial,
    'h': weight_high
}


class TcDetail:

    def __init__(self,
                 id: str,
                 flag_list: List[str],
                 weight: int,
                 data: Dict):
        self.id = id
        self.flag_list = flag_list
        self.weight = weight
        self.data = data

    def __str__(self):
        repr_str = ("<TcDetail("
                    "id={id}"
                    ")>".format(
            id=self.id))
        return repr_str

    def __repr__(self):
        return self.__str__()


