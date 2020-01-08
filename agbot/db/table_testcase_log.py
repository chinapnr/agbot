# @Time    : 2018/4/25 9:49
# @Desc    : Files description
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text

from .db_base import Base


# TabTcLog 自动化测试 tc 日志表
# 2018.4.20 create by yanan.wu #816769s
class TableTestCaseLog(Base):
    __tablename__ = 'table_testcase_log'

    tc_seq_id = Column(Integer, primary_key=True)
    sys_date = Column(String(8))
    task_id = Column(String(32))
    job_id = Column(String(32))
    tc_id = Column(String(10))
    test_result = Column(String(1))
    error_info = Column(String(1024))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    tc_flag = Column(String(300))
    tc_weight = Column(Integer)
    crt_datetime = Column(DateTime, default=datetime.now)
    upd_datetime = Column(DateTime, default=datetime.now)
    
    # 2019.6.5 edit by jun.hu
    placeholder_info = Column(Text)

    # 2019.3.8 edit by jun.hu
    def __repr__(self):
        repr_str = ("<TableTestCaseLog(tc_seq_id={tc_seq_id}, job_id={job_id}, tc_id={tc_id}"
                    "test_result={test_result},cost_time={cost_time},"
                    "error_info={error_info}, placeholder_info={placeholder_info}>")
        repr_dict = self.to_dict()
        return repr_str.format(**repr_dict)

    # 2019.3.8 edit by jun.hu
    def to_dict(self):
        return {'job_id': self.job_id,
                'tc_id': self.tc_id,
                'test_result': self.test_result,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'cost_time': (self.end_time - self.start_time).total_seconds() * 1000,
                'error_info': self.error_info if self.error_info else '',
                'placeholder_info': self.placeholder_info,
                'tc_seq_id': self.tc_seq_id}
