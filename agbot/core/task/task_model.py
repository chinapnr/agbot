from typing import Dict


class TaskModel:
    id: str

    def __init__(self,
                 id: str,
                 task_src: str,
                 global_var: Dict
                 ):
        self.id = id
        self.task_src = task_src
        self.global_var = global_var
        self.crt_sys = None
        self.crt_user = None
        self.job_concurrency = 8
        self.pass_through = {}

    def __str__(self):
        repr_str = ("<TaskContentConfig(id={id},"
                    "task_src={task_src}, global_var={global_var})>".
                    format(
                        id=self.id,
                        task_src=self.task_src,
                        global_var=self.global_var))
        return repr_str

    def __repr__(self):
        return self.__str__()



