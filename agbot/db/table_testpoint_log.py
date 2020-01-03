# @Time    : 2018/4/25 9:50
# @Desc    : Files description
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Column, Text

from .db_base import Base


# TabTpLog 自动化测试 tp 日志表
# 2018.4.20 create by yanan.wu #816769
class TableTestPointLog(Base):
    __tablename__ = 'table_testpoint_log'

    tp_seq_id = Column(Integer, primary_key=True)
    sys_date = Column(String(8))
    task_id = Column(String(32))
    tc_seq_id = Column(Integer)
    tp_type = Column(String(10))
    tp_id = Column(String(32))
    tp_result = Column(String(1))
    result_value = Column(String(4096))
    error_info = Column(String(1024))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    crt_datetime = Column(DateTime, default=datetime.now)
    upd_datetime = Column(DateTime, default=datetime.now)
    requ_param = Column(String(4096))
    resp_code = Column(String(3))
    tp_name = Column(String(100))
    placeholder_info = Column(Text)
    assertion_info = Column(Text)
    
    # 2019.3.8 edit by jun.hu
    def __repr__(self):
        repr_str = ("<TableTestPointLog(tp_seq_id={tp_seq_id}, tp_type={tp_type}, tp_id={tp_id}"
                    "error_info={error_info},requ_param={requ_param}, result_value={result_value},"
                    "tp_name={tp_name},cost_time={cost_time},tp_result={tp_result},"
                    "placeholder_info={placeholder_info}>, placeholder_data={placeholder_data},"
                    "assertion_info={assertion_info}>")
        repr_dict = self.to_dict()
        return repr_str.format(**repr_dict)

    # 2019.3.8 edit by jun.hu
    def to_dict(self):
        return {'tp_id': self.tp_id,
                'tp_result': self.tp_result,
                'tp_type': self.tp_type,
                'requ_param': self.requ_param,
                'result_value': self.result_value,
                'error_info': self.error_info,
                'tp_name': self.tp_name,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'cost_time': (self.end_time - self.start_time).total_seconds() * 1000,
                'placeholder_info': self.placeholder_info,
                'assertion_info': self.assertion_info,
                'tp_seq_id': self.tp_seq_id,
                'tc_seq_id': self.tc_seq_id}
