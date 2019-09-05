import time
try:
    from . import  reco_pb2
except:
    import reco_pb2


def get_grpc_func_ret(stub):
    # 1.构造情趣参数对象
    user_request = reco_pb2.UserRequest()
    user_request.user_id = '1'
    user_request.channel_id = 1
    user_request.article_num = 10
    user_request.time_stamp = round(time.time()*1000)

    # 2.通过参数stub调用远程服务端的函数,获取返回的响应对象
    rpc_response = stub.user_recommend(user_request)
    print(rpc_response)
    print(rpc_response.recommends[0].track.read)
    return rpc_response


import grpc
try:
    from . import reco_pb2_grpc
except:
    import reco_pb2_grpc

def run():
    # 1.通过上下文环境链接rpc服务端
    with grpc.insecure_channel('127.0.0.1:8888') as channel:
        # 2.实例化stub对象
        stub = reco_pb2_grpc.UserRecommendStub(channel)
        # 3.通过stub调用远端函数获取结果
        rpc_response = get_grpc_func_ret(stub)
    return rpc_response

if __name__ == '__main__':
    run()