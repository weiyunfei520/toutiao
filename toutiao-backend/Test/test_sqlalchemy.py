from datetime import datetime
from flask import Flask, jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/toutiao'  # 数据库链接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库修改,开启后影响性能
    SQLALCHEMY_ECHO = True  # 开启后,可以在控制台打印底层执行的sql语句


app.config.from_object(Config)
app.config['JSON_AS_ASCII'] = False  # jsonify返回的值禁用ascii编码:uft8
# 创建数据库链接对象
db = SQLAlchemy(app)


class User(db.Model):
    """
    用户基本信息
    """
    __tablename__ = 'user_basic'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    id = db.Column('user_id', db.Integer, primary_key=True, doc='用户ID')
    mobile = db.Column(db.String, doc='手机号')
    password = db.Column(db.String, doc='密码')
    name = db.Column('user_name', db.String, doc='昵称')
    profile_photo = db.Column(db.String, doc='头像')
    last_login = db.Column(db.DateTime, doc='最后登录时间')
    is_media = db.Column(db.Boolean, default=False, doc='是否是自媒体')
    is_verified = db.Column(db.Boolean, default=False, doc='是否实名认证')
    introduction = db.Column(db.String, doc='简介')
    certificate = db.Column(db.String, doc='认证')
    article_count = db.Column(db.Integer, default=0, doc='发帖数')
    following_count = db.Column(db.Integer, default=0, doc='关注的人数')
    fans_count = db.Column(db.Integer, default=0, doc='被关注的人数（粉丝数）')
    like_count = db.Column(db.Integer, default=0, doc='累计点赞人数')
    read_count = db.Column(db.Integer, default=0, doc='累计阅读人数')

    account = db.Column(db.String, doc='账号')
    email = db.Column(db.String, doc='邮箱')
    status = db.Column(db.Integer, default=1, doc='状态，是否可用')
    # TODO 2. 声明一个字段，用db.relationship('UserProfile'）指向UserProfile模型类
    # 注意2.2： User.profile == UserProfile; User.profile.gender == UserProfile.gender
    # 注意2.3： User相当于UserProfile是【逻辑主表】
    # 注意2.1： uselist=False参数表示通过User.profile方式获取的只有一个数据对象
    #          uselist默认为True 表示通过User.profile方式获取是由数据对象组成的列表
    # profile = db.relationship('UserProfile', uselist=False)
    profile = db.relationship('UserProfile',
                              primaryjoin='User.id==foreign(UserProfile.id)',
                              uselist=False)


class UserProfile(db.Model):
    """
    用户资料表
    """
    __tablename__ = 'user_profile'

    class GENDER:
        MALE = 0
        FEMALE = 1

    # TODO 1. 第三个参数db.ForeignKey('user_basic.user_id')表示外键指向user_basic表的user_id
    # 注意1.1：这里必须用原生表名和原生字段名
    # 注意1.2：这只是代码逻辑规定的关联关系，并不能对原生数据表造成任何影响
    # 注意1.3：这里是代码逻辑层面上的从表，简称【逻辑从表】，user_profile.id既是user_profile表的主键，又是【逻辑外键】
    # id = db.Column('user_id', db.Integer, db.ForeignKey('user_basic.user_id'), primary_key=True, doc='用户ID')
    id = db.Column('user_id', db.Integer, primary_key=True, doc='用户ID')
    gender = db.Column(db.Integer, default=0, doc='性别')
    birthday = db.Column(db.Date, doc='生日')
    real_name = db.Column(db.String, doc='真实姓名')
    id_number = db.Column(db.String, doc='身份证号')
    id_card_front = db.Column(db.String, doc='身份证正面')
    id_card_back = db.Column(db.String, doc='身份证背面')
    id_card_handheld = db.Column(db.String, doc='手持身份证')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
    register_media_time = db.Column(db.DateTime, doc='注册自媒体时间')

    area = db.Column(db.String, doc='地区')
    company = db.Column(db.String, doc='公司')
    career = db.Column(db.String, doc='职业')


class Relation(db.Model):
    """
    用户关系表
    """
    __tablename__ = 'user_relation'

    class RELATION:
        DELETE = 0
        FOLLOW = 1
        BLACKLIST = 2

    id = db.Column('relation_id', db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user_basic.user_id'), doc='用户ID')
    # user_id = db.Column(db.Integer, doc='用户ID')
    target_user_id = db.Column(db.Integer, doc='目标用户ID')
    relation = db.Column(db.Integer, doc='关系')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')


@app.route('/')
def index():
    # 返回所有路由
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if
                    rule.endpoint not in ('route_map', 'static')})


@app.route('/add')
def add_data():
    """增加数据"""
    # 创建/实例化数据对象
    user = User(mobile='13161933310', name='金馆长1')
    # 将数据对象添加到链接对象的session(会话)中
    db.session.add(user)
    # 提交会话,此时add(user)写入数据才生效
    db.session.commit()
    # 先把user写入数据库后,user_basic表中才能有这个id
    profile = UserProfile(id=user.id)
    db.session.add(profile)
    db.session.commit()

    # 同时写入多条数据
    # user1 = User(mobile='13911224611', name='金馆长4')
    # user2 = User(mobile='13911224612', name='金馆长5')
    # user3 = User(mobile='13911224613', name='金馆长6')
    # db.session.add_all([user1, user2, user3])
    # db.session.commit()

    return 'add_data'


@app.route('/get_all')
def get_all():
    """查询所有"""
    # 返回由数据对象构成的列表
    users = User.query.all()
    # db.session.query(User).all()
    ret_dict = {}
    for user in users:
        ret_dict[user.mobile] = user.name
    return jsonify(ret_dict)


@app.route('/first')
def first():
    # 查询返回第一个
    user = User.query.first()
    # db.session.query(User).first()
    return jsonify({user.mobile: user.name})


@app.route('/get')
def get():
    # 根据主键id获取对象,若逐渐不存在返回none
    user = User.query.get(2)
    # db.session.query(User).get(2)
    return jsonify({user.mobile: user.name})


@app.route('/filter_by')
def filter_by():
    """过滤查询"""
    # User.query.filter_by(mobile='18516952650').first()
    # ret = User.query.filter_by(mobile='18516952650', id=1).first()
    ret = User.query.filter(User.mobile == '18516952650').first()
    print(type(ret))
    return ret.name


from sqlalchemy import or_


@app.route('/or')
def o_r():
    """or_逻辑或"""
    rets = User.query.filter(or_(User.mobile == '13911111111', User.name.endswith('号'))).all()
    ret_dict = {ret.mobile: ret.name for ret in rets}
    return jsonify(ret_dict)


from sqlalchemy import and_


@app.route('/and')
def an_d():
    """and_逻辑与"""
    rets = User.query.filter(and_(User.name != '13911111111', User.name.startswith('185'))).all()
    ret_dict = {ret.mobile: ret.name for ret in rets}
    return jsonify(ret_dict)


from sqlalchemy import not_


@app.route('/not')
def no_t():
    """not_逻辑非"""
    rets = User.query.filter(not_(User.mobile == '13911111111')).all()
    ret_dict = {ret.mobile: ret.name for ret in rets}
    return jsonify(ret_dict)


@app.route('/offset')
def offset():
    """offset偏移"""
    # 跳过两个,从第三个开始,offset(2)
    rets = User.query.offset(2).all()
    ret_dict = {ret.mobile: ret.name for ret in rets}
    return jsonify(ret_dict)


@app.route('/limit')
def limit():
    # 只选取n个:User.query.limit(n)
    rets = User.query.limit(2).all()
    ret_dict = {ret.mobile: ret.name for ret in rets}
    return jsonify(ret_dict)


@app.route('/order_by')
def order_by():
    """排序"""
    ret1 = User.query.order_by(User.id.desc()).all()  # 反序
    ret2 = User.query.order_by(User.id).all()  # 正序
    ret_dict = {'a': str(ret1), 'b': str(ret2)}
    return jsonify(ret_dict)


@app.route('/fuhe')
def fuhe():
    # 多个查询方法一起使用
    # name以13开头，倒序，跳过2个，从第三个开始，一共获取5个
    rets = User.query.filter(User.name.startswith('13')).order_by(User.id.desc()).offset(2).limit(5)
    ret_dict = {ret.mobile: ret.name for ret in rets}
    return jsonify(ret_dict)


from sqlalchemy.orm import load_only


@app.route('/youhua')
def youhua():
    print('====')
    # options表示选择要展示的字段，load_only表示只读取字段，不整条数据查询
    # 查询特定字段
    ret = User.query.options(load_only(User.name, User.mobile)).filter_by(id=1).first()
    # 查询所有字段
    User.query.filter(User.id == 1).first()
    print('====')
    return '{}:{}'.format(ret.name, ret.mobile)


from sqlalchemy import func


# 需求：查询关注别人的用户id，和他关注的总人数
@app.route('/juhe')
def juhe():
    """func聚合查询"""
    # sqlalchemy.func.count(xx) 表示对xx的数量进行求和
    rets = db.session.query(Relation.user_id, func.count(Relation.target_user_id)) \
        .filter(Relation.relation == Relation.RELATION.FOLLOW).group_by(Relation.user_id).all()
    # 去user_relation表中查询relation是1的数据，按user_id进行分组，
    # 并返回[(user_id和，user_id相同的target_user_id数量的和),...]
    # SELECT user_relation.user_id , count(user_relation.target_user_id)
    # FROM user_relation WHERE user_relation.relation = %s GROUP BY user_relation.user_id
    # rets = db.session.query(Relation.user_id, func.count(Relation.target_user_id))
    # print(rets)
    # rets = rets.filter(Relation.relation == Relation.RELATION.FOLLOW)
    # print(rets)
    # rets = rets.group_by(Relation.user_id).all()
    # print(rets)
    return str(rets)


# http://192.168.65.131:5000/gender?mobile=13161933310
# @app.route('/gender')
# def gender():
#     mobile = request.args.get('mobile', None)
#     if not mobile:
#         return '给个手机号，我再告诉你是男是女'
#     # 根据user_basic.moblie手机号查询user_profile.gender
#     users = User.query.filter(User.mobile==mobile).all()
#     print(users)
#     user = users[0]
#     return '{}, {}, {}'.format(user.mobile, user.name, str(user.profile.gender))

# http://192.168.65.131:5000/gender?mobile=13161933310
from sqlalchemy.orm import contains_eager


@app.route('/gender')
def gender():
    mobile = request.args.get('mobile', None)
    if not mobile:
        return '给个手机号，我再告诉你是男是女'
    rets = User.query.join(User.profile).options(load_only(User.mobile),
                                                 contains_eager(User.profile).load_only(UserProfile.gender)).filter(User.mobile == mobile).all()
    user = rets[0]
    return 'mobile={}, gender={}'.format(user.mobile, user.profile.gender)


@app.route('/update')
def update():
    # 方式1
    user = User.query.get(1)
    user.name = 'Python'
    db.session.add(user)
    db.session.commit()
    # 方式2
    input('sss')
    User.query.filter_by(id=1).update({'name': '黑马头条号'})
    db.session.commit()
    return 'update'


@app.route('/delete')
def delete():
    # 方式1
    user = User.query.order_by(User.id.desc()).first()
    db.session.delete(user)
    db.session.commit()
    # 方式2
    # User.query.filter(User.mobile=='18512345678').delete()
    # db.session.commit()


@app.route('/shiwu')
def shiwu():
    try:
        user = User(mobile='18911111111', name='itcast')
        db.session.add(user)
        db.session.flush()
        profile = UserProfile(id=user.id)
        db.session.add(profile)
        db.session.commit()
    except:
        db.session.rollback()
    return 'shiwu'

if __name__ == '__main__':
    app.run(debug=True)
