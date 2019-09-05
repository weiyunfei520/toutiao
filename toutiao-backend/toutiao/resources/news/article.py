import grpc
import time
from flask import g
from flask_restful.reqparse import RequestParser
from flask_restful import Resource
from rpc import reco_pb2, reco_pb2_grpc

from utils.decorators import login_required


class ArticleListResource(Resource):
    # 当前用户获取推荐文章
    method_decorators = [login_required]

    def _get_rpc_article_list(self, stub,
                              user_id,
                              channel_id:int,
                              time_stamp=round(time.time()*1000),
                              article_num=10):
        user_requset = reco_pb2.UserRequest()
        print(type(user_id), user_id)
        user_requset.user_id = str(user_id)
        user_requset.channel_id = int(channel_id)
        user_requset.time_stamp = time_stamp
        user_requset.article_num = article_num

        # 通过参数stub调用远程服务端的函数,获取返回的响应对象
        rpc_response = stub.user_recommend(user_requset)
        print(rpc_response)
        print(rpc_response.recommends[0].track.read)
        return rpc_response

    def get(self):
        # 接收请求参数
        parser = RequestParser()
        parser.add_argument('channel_id', location='args', required=True, help='频道id int')
        args = parser.parse_args()
        # 通过rpc调用远端推荐系统的函数,返回响应对象(包含了推荐的文章)
        # 1.通过上下文环境链接rpc服务端
        with grpc.insecure_channel('127.0.0.1:8888') as channel:
            # 2.实例化stub对象
            stub = reco_pb2_grpc.UserRecommendStub(channel)
            # 3.通过stub调用远程函数获取结果
            rpc_response = self._get_rpc_article_list(stub, g.user_id, channel_id=args.channel_id)

            # 构造数据并返回
            recommends_list = []
            for article in rpc_response.recommends:
                article_dict = {}
                article_dict['article_id'] = article.article_id
                article_dict['track'] = dict()
                article_dict['track']['click'] = article.track.click
                article_dict['track']['collect'] = article.track.collect
                article_dict['track']['share'] = article.track.share
                article_dict['track']['read'] = article.track.read
                recommends_list.append(article_dict)
            return {
                'expousre': rpc_response.expousre,
                'time_stamp': rpc_response.time_stamp,
                'recommends': recommends_list
            }