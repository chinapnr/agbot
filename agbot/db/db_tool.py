from datetime import datetime

from fishbase.fish_common import SingleTon
from fishbase.fish_logger import logger as log


# 发生异常时由 session_scope 完成回滚
class DBUtils(SingleTon):
    session_scope = None

    @staticmethod
    def init_session_scope(session):
        DBUtils.session_scope = session

    @staticmethod
    def check_session_scope():
        assert DBUtils.session_scope, 'session_scope must init ! Please check and try again.'

    @staticmethod
    def add(table_object, data_dict, is_flush=False):
        """
        新增数据, 单条插入
        :param table_object: 表对象
        :param data_dict: dict, 插入单条数据
        :param is_flush: bool, 插入数据后是否立即提交
        :return:
        """
        DBUtils.check_session_scope()
        obj = None
        with DBUtils.session_scope(is_flush) as session:
            try:
                obj = table_object(**data_dict)
                session.add(obj)
            except Exception as e:
                log.error("数据库插入错误: {0}".format(str(e)))
                log.exception('write {} error: {}; cause {}'.format(str(table_object.__name__),
                                                                    str(data_dict), str(e)))
        if is_flush:
            return obj

    @staticmethod
    def add_all(table_object, data_list):
        """
        新增数据, 批量插入
        :param table_object: 表对象
        :param data_list: list, 批量插入的数据
        :return:
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:
            try:
                table_object_list = []
                for x in data_list:
                    table_object_list.append(table_object(**x))
                session.add_all(table_object_list)
            except Exception as e:
                log.error("数据库插入错误: {0}".format(str(e)))
                log.exception('write {} error: {}; cause {}'.format(str(table_object.__name__),
                                                                    str(data_list), str(e)))

    @staticmethod
    def delete(table_object, filter_data):
        """
        删除数据
        :param table_object: 表对象
        :param filter_data: dict, 删除条件
        :return:
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:
            try:
                session.query(table_object).filter_by(**filter_data).delete()
            except Exception as e:
                log.error("数据库删除错误: {0}".format(str(e)))
                # raise CustomFlaskErr(const.INSERT_DATA_TO_DB_ERROR.format('删除'))

    @staticmethod
    def update(table_object, filter_dict, update_dict):
        """
        修改操作
        :param table_object: 表对象
        :param filter_dict: dict, 修改条件
        :param update_dict: dict, 修改的值
        :return:
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:  # type: scoped_session
            try:
                # synchronize_session
                # 可选值：'evaluate' 默认值, 会同时修改当前 session 中的对象属性
                # 'fetch' 修改前, 会先通过 select 查询条目的值.
                # False 不修改当前 session 中的对象属性
                query_obj = session.query(table_object).filter_by(**filter_dict)

                if query_obj:
                    update_dict.update({'upd_datetime': datetime.now()})
                    query_obj.update(update_dict)
                else:
                    filter_str = ','.join(['{}={}'.format(str(k), str(v)) for k, v in filter_dict.items()])
                    log.exception('{} is not found: {}'.format(table_object.__name__, filter_str))
            except Exception as e:
                log.exception('modify {} error filter_dict: {} update_dict: {}; cause {}'.
                              format(str(table_object.__name__), str(filter_dict),
                                     str(update_dict), str(e)))

    @staticmethod
    def query(table_object, filter_dict=None, first=True, order_dict=None):
        """
        数据查询，支持 第一条数据、排序查询
        :param table_object: 表 orm 对象
        :param filter_dict: 查询字典 eg: {'task_id': '20180428005'}
        :param first: 是否查询第一条数据，默认为 True
        :param order_dict: 排序字典，目前仅支持一个字段的排序查询 键为需要排序的字段，值为排序规则(asc desc)
        eg: {'crt_datetime': 'desc'}
        :return: flag(bool): 查询是否发生异常
                 data_list(list): [table_obj] （查询对象结果列表）
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:  # type: scoped_session
            try:
                if filter_dict is None:
                    filter_result = session.query(table_object)
                else:
                    filter_result = session.query(table_object).filter_by(**filter_dict)
                if order_dict:
                    for k, v in order_dict.items():
                        if v == 'asc':
                            filter_result = filter_result.order_by(getattr(table_object, k).asc())
                        else:
                            filter_result = filter_result.order_by(getattr(table_object, k).desc())
                if first:
                    res = filter_result.first()
                    session.expunge_all()
                    # 保持接口返回数据类型一致
                    res_list = [res] if res else []
                    return True, res_list
                # 解除查询对象和 session 的绑定关系，解决 obj not bound on Session
                result_list = filter_result.all()
                session.expunge_all()
                return True, result_list

            except Exception as ex:
                log.exception('query {} error filter_dict: {} first: {} order_dict {}; cause {}'.
                              format(str(table_object.__name__), str(filter_dict), first,
                                     str(order_dict), str(ex)))
                return False, []

    @staticmethod
    def query_(table_object, first=True, start=None, end=None, **filter_dict):
        """
        简单条件查询, 支持查询所有数据, 第一条, 最后一条和切片操作
        :param table_object: 表对象
        :param first: 是否是获取第一条数据
        :param start: 开始截取位置
        :param end: 结束位置
        :param filter_dict: 过滤条件
        :return:
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:
            try:
                if first:
                    return session.query(table_object).filter_by(**filter_dict).first(), 'success'
                elif start and end:
                    return session.query(table_object).filter_by(**filter_dict).all()[start:end], 'success'
            except Exception as e:
                log.error('query {} ; cause {}'.format(str(table_object.__name__), str(e)))
                return None, str(e)

    @staticmethod
    def create_table(all_table=False, table_name=None):
        """
        创建表
        :param all_table:  创建所有表
        :param table_name:  创建指定表
        :return:
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:
            if all_table:
                session.create_all()
            elif table_name:
                pass

    @staticmethod
    def delete_table(all_table=False, table_name=None):
        """
        删除表
        :param all_table: 删除所有的表
        :param table_name:  删除指定表
        :return:
        """
        DBUtils.check_session_scope()
        with DBUtils.session_scope() as session:
            if all_table:
                session.drop_all()
            elif table_name:
                pass

    @staticmethod
    def object_search(table_object, filter_object):
        with DBUtils.session_scope() as session:
            ret = None
            try:
                ret = session.query(table_object).filter(filter_object)
            except Exception as e:
                log.error("数据库查询错误: {0}".format(str(e)))
            return ret

    # TODO 待完善like, and, or, 排序, 分组等

# if __name__ == '__main__':
    # from application import db
    # db_util = DBUtils(db)
    #  创建表
    #  db_util.create_table(all_table=True)

    #  新增单条记录
    # data = {
    #     'id': 1,
    #     'type': 'test',
    #     'file_name': 'file_name',
    #     'file_token': 'xxxxx'
    # }
    # db_util.add(TemplateInfo, filter_data=data)

    # 批量添加
    # import random
    # data1 = {
    #     'id': random.randint(1, 1000),
    #     'type': 'test',
    #     'file_name': 'file_name',
    #     'file_token': 'xxxxx'
    # }
    # data2 = {
    #     'id': random.randint(1, 1000),
    #     'type': 'test',
    #     'file_name': 'file_name',
    #     'file_token': 'xxxxx'
    # }
    # table_object_list = [data1, data2]
    # db_util.add(TemplateInfo, *table_object_list)

    # 删除数据
    # data = {
    #     'id': 1
    # }
    # db_util.delete(TemplateInfo, **data)

    # 修改
    # filter_dict = {'type': 'test'}
    # update_dict = {'file_name': '22'}
    # db_util.modify(TemplateInfo, filter_dict=filter_dict, update_dict=update_dict)

    # 查询
    # filter_dict = {'id': 50}
    # re = db_util.search(TemplateInfo, **filter_dict)         # 根据条件查询 TemplateInfo 的所有数据
    # re = db_util.search(TemplateInfo, result_range='first')  # 查询 TemplateInfo 的第一条数据
    # re = db_util.search(TemplateInfo, result_range='last')   # 查询 TemplateInfo 的最后一条数据
    # re = db_util.search(TemplateInfo, start=1, end=2)        # 对结果切片
    # print(re)
