# @Time    : 2018/4/25 9:47
# @Desc    : Files description

from datetime import datetime

from fishbase.fish_logger import logger
from sqlalchemy import Column, String, Integer, DateTime

from .db_base import Base
from .db_tool import DBUtils


# TabTaskLog 自动化测试 task 日志表
# 2018.4.20 create by yanan.wu #816769
class TableTaskLog(Base):
    __tablename__ = 'table_task_log'
    
    task_seq_id = Column(Integer, primary_key=True)
    sys_date = Column(String(8))
    task_id = Column(String(32))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    cost_time = Column(Integer)
    task_src = Column(String(256))
    job_list = Column(String(1024))
    task_status = Column(String(1))
    crt_datetime = Column(DateTime, default=datetime.now)
    upd_datetime = Column(DateTime, default=datetime.now)
    crt_sys = Column(String(16))
    crt_user = Column(String(16))
    # 2019.6.13 添加 task 错误信息
    error_info = Column(String, default='')
    
    # 2019.3.8 edit by jun.hu
    def __repr__(self):
        repr_str = ("<TableTaskLog(task_seq_id={task_seq_id}, task_status={task_status}, "
                    "cost_time={cost_time})>")
        repr_dict = self.to_dict()
        return repr_str.format(**repr_dict)

    # 2019.3.8 edit by jun.hu
    def to_dict(self):
        return {'task_id': self.task_id,
                'task_status': self.task_status,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'cost_time': self.cost_time,
                'task_seq_id': self.task_seq_id}


# 依据 task_id 进行 Task 运行日志更新函数
# 输入：
# task_log_dict: Task 运行日志信息字典
# ---
# 2018.3.22 create by yanan.wu #737836
# 2018.4.24 edit by jie.lu  #820798
# 2019.3.1 edit by jun.hu
def update_task_with_task_id(task_log_dict):
    # 构造查询条件,即取唯一索引
    # 构造 Job 数据库写入模型
    filter_dict = {'task_id': task_log_dict.pop('task_id')}
    flag, task_log_list = DBUtils.query(TableTaskLog, filter_dict=filter_dict)
    
    if not (flag and task_log_list):
        logger.info('TableTaskLog is not found:task_id=',
                    filter_dict['task_id'])
        pass
    
    task_log = task_log_list[0]
    task_log_dict.update({'cost_time': (task_log_dict['end_time'] - task_log.start_time).total_seconds() * 1000})
    
    DBUtils.update(TableTaskLog, filter_dict=filter_dict, update_dict=task_log_dict)

