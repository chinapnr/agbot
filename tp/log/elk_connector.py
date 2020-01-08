# @Time    : 2018/3/21 16:55
# @Desc    : Files description


from elasticsearch import Elasticsearch

from fishbase.fish_common import SingleTon


# Elk 日志请求
# 2018.6.12 edit by yanan.wu #748921
class Es(SingleTon):

    # 类初始化过程
    # 2018.6.12 create by yanan.wu  #822485
    def __init__(self, server_ip, server_port, auth_user, auth_password):
        SingleTon.__init__(self)
        self.es = Elasticsearch(
            [server_ip],
            http_auth=(auth_user, auth_password),
            scheme="http",
            port=int(server_port),
            retry_on_timeout=True
        )

    def search_match(self, index, time_start, time_end, size, match_message):
        """
        :param index: 索引名
        :param time_start: 开始时间
        :param time_end: 结束时间
        :param size: 日志条数
        :param match_message: 关键字，用空格断开
        :return:
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {
                            "@timestamp": {
                                "gte": time_start,
                                "lte": time_end,
                            }
                        }},
                        {"match": {
                            "message": {
                                "query": match_message,
                                "operator": "and",
                                "zero_terms_query": "all"
                            }
                        }}
                    ],
                }
            },
            "size": size,
            "timeout": "5s",
        }

        ping = self.es.ping()
        if not ping:
            raise RuntimeError("ping {}, elasticsearch 未连接上".format(ping))

        search = self.es.search(index=index, body=body)
        print("search %d Hits:" % search['hits']['total'])
        for hit in search['hits']['hits']:
            print("%(loglevel)s %(@timestamp)s %(message)s" % hit["_source"])
        return search

