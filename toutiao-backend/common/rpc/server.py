import time

try:
    from . import reco_pb2
    from . import reco_pb2_grpc
except:
    import reco_pb2
    import reco_pb2_grpc


class UserRecommendServicer(reco_pb2_grpc.UserRecommendServicer):
    def user_recommend(self, request, context):
        # 1.解析请求对象中的参数
        user_id = request.user_id  # 用户id str类型
        channel_id = request.channel_id  # 频道id int类型
        article_num = request.article_num  # 推荐的文章数量 向推荐系统索要推荐文章的数量 int类型
        time_stamp = request.time_stamp # 推荐的时间戳 单位秒 int类型

        """这里根据请求参数做了一些操作"""

        # 2.构造相应对象,并返回
        response = reco_pb2.ArticleResponse()
        response.expousre = 'sssss'
        response.time_stamp = round(time.time()*1000) # round() py内置函数 四舍五入取整

        recommends_list = []
        for i in range(article_num):
            article = reco_pb2.Article()
            article.article_id = i+1
            article.track.click = 'click'
            article.track.collect = 'collect'
            article.track.share = 'share'
            article.track.read = 'read'
            recommends_list.append(article)

        response.recommends.extend(recommends_list)
        return response

import grpc
from concurrent.futures import ThreadPoolExecutor

def serve():
    server = grpc.server(ThreadPoolExecutor(max_workers=3))
    reco_pb2_grpc.add_UserRecommendServicer_to_server(UserRecommendServicer(), server)
    server.add_insecure_port('0.0.0.0:8888')
    server.start() # 启动rpc服务,但不会阻塞当前程序

    while True:
        time.sleep(100)

if __name__ == '__main__':
    serve()
