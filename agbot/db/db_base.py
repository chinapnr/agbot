from contextlib import contextmanager

from fishbase.fish_logger import logger
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

Base = declarative_base()


class ParserSessionScope(object):
    session_factory = None

    # 2019.01.24 created by jun.hu
    # 使用 session_scope 来解决 sqlalchemy 线程安全的问题
    @staticmethod
    def _checkout_listener(db_con, con_record, con_proxy):
        """
        :param db_con:
        :param con_record:
        :param con_proxy:
        :return:
        """
        try:
            try:
                db_con.ping(False)
            except TypeError as ex:
                logger.info(" db_con.ping TypeError: {}".format(str(ex)))
                db_con.ping()
        except db_con.OperationalError as exc:
            if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
                raise DisconnectionError()
            else:
                raise
    
    @staticmethod
    def get_engine(sql_uri, pool_conf_dict):
        kw = {
            'poolclass': QueuePool
        }
        kw.update(pool_conf_dict)
        engine = create_engine(sql_uri, **kw)
        return engine

    @staticmethod
    def get_session_scope(sql_uri, db_type='mysql', pool_conf_dict=None):
        is_sqlite = db_type == 'sqlite'
        # 非 sqlite（目前仅 mysql） 类型的数据库需要制定编码
        if (not is_sqlite) and (not sql_uri.endswith('?charset=utf8')):
            sql_uri = sql_uri + '?charset=utf8'

        # sqlite 类型数据库需要加上 check_same_thread=False 避免多线程查询时候的错误
        if is_sqlite:
            sql_uri = sql_uri + '?check_same_thread=False'
        engine = ParserSessionScope.get_engine(sql_uri, pool_conf_dict)
        # 创建 session 工厂
        if not is_sqlite:
            event.listen(engine, 'checkout', ParserSessionScope._checkout_listener)

        ParserSessionScope.session_factory = sessionmaker(bind=engine)
        return ParserSessionScope._session_scope

    # 创建上下文管理器
    @staticmethod
    @contextmanager
    def _session_scope(is_flush=False):
        # is_flush 是否在 commit 之后立即刷新
        session = scoped_session(ParserSessionScope.session_factory)
        try:
            yield session             # 每次数据库操作返回一个 session 对象
            session.commit()          # 自动 commit, commit 之后连接会归还到连接池
            if is_flush:
                session.flush()
        except Exception as ex:
            logger.error("contextmanager session_scope error: {}".format(str(ex)))
            session.rollback()        # 自动 rollback
            raise
        finally:
            pass
