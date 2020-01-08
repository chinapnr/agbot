# @Time    : 2018/4/24 21:15
# @Desc    : Files description
from datetime import datetime

from fishbase.fish_logger import logger
from sqlalchemy import Column, String, DateTime, Integer

from .db_base import Base
from .db_tool import DBUtils


# TabJobLog 自动化测试 job 日志表
# 2018.4.20 create by yanan.wu #816769
class TableJobLog(Base):
    __tablename__ = 'table_job_log'

    job_seq_id = Column(Integer, primary_key=True)
    sys_date = Column(String(8))
    task_id = Column(String(32))
    job_id = Column(String(32))
    job_desc = Column(String(512))
    job_status = Column(String(1))
    error_info = Column(String(1024))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    cost_time = Column(Integer)
    crt_datetime = Column(DateTime, default=datetime.now)
    upd_datetime = Column(DateTime, default=datetime.now)
    job_score = Column(String(10))
    pass_rate = Column(String(10))
    key_unpass_num = Column(String(10))
    
    # 2019.3.8 edit by jun.hu
    def __repr__(self):
        repr_str = ("<TableJobLog(job_seq_id={job_seq_id}, job_id={job_id}, pass_rate={pass_rate}"
                    "job_status={job_status},cost_time={cost_time}, job_desc={job_desc}>")
        repr_dict = self.to_dict()
        return repr_str.format(**repr_dict)

    # 2019.3.8 edit by jun.hu
    def to_dict(self):
        return {'job_id': self.job_id,
                'job_status': self.job_status,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'cost_time': self.cost_time,
                'job_desc': self.job_desc,
                'pass_rate': self.pass_rate,
                'error_info': self.error_info,
                'job_seq_id': self.job_seq_id, }


# 依据 task_id 与 job_id 进行 Job 运行日志更新函数
# 输入：
# job_log_dict: job 运行日志信息字典
# ---
# 2018.3.22 create by yanan.wu #737836
# 2018.4.24 edit by jie.lu  #820566
def update_job(job_log_dict):
    # 构造查询条件,即取唯一索引
    # 构造 Job 数据库写入模型
    # job_log_ = TableJobLog.query.filter_by(task_id=job_log_dict['task_id'],
    #                                        job_id=job_log_dict[
    #                                           'job_id']).first()
    filter_dict = {'task_id': job_log_dict.pop('task_id'),
                   'job_id': job_log_dict.pop('job_id')}
    _, job_log_list = DBUtils.query(TableJobLog, filter_dict=filter_dict)

    if not job_log_list:
        logger.info('TableJobLog is not found:')
        return

    job_log = job_log_list[0]

    end_time = job_log_dict['end_time']
    job_log_dict.update({'cost_time': (end_time - job_log.start_time).total_seconds() * 1000})

    DBUtils.update(TableJobLog, filter_dict=filter_dict, update_dict=job_log_dict)
