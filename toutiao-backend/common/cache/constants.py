import random


class BaseCacheTTL():
    """缓存有效期,单位秒,要防止雪崩"""
    TTL = 60 * 60 * 2  # 2小时,基础值
    MAX_DELTA = 10 * 60  # 有效期上限

    # todo 改为类方法之后,可以不实例化就直接调用cls.func
    @classmethod
    def get_ttl(cls):
        # 返回有效期时间范围内的随机值
        return cls.TTL + random.randrange(0, cls.MAX_DELTA)


# todo 为防止缓存雪崩,在对不同的数据设置缓存有效期时采用设置不同有效期的方案,所以采用继承的方式


class UserProfileCahceTTL(BaseCacheTTL):
    """用户信息缓存数据的有效期,单位秒"""
    pass


# todo 对于不存在的用户,缓存有效期稍微短一些
class UserNotExistsCacheTTL(BaseCacheTTL):
    TTL = 5 * 60
    MAX_DELTA = 10 * 60
