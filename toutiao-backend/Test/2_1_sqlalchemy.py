from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# step 1. 配置sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@127.0.0.1:3306/test43' # 数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 是否追踪数据库修改, 开启后影响性能
app.config['SQLALCHEMY_ECHO'] = True  # 开启后, 可以在控制台打印底层执行的sql语句

# step 2. 创建数据库连接对象
db = SQLAlchemy(app)

# step 3. 建立映射模型  类->表  类属性->字段  对象->记录
# 此时数据库里一个表都没有
# class User(db.Model):
class t_user(db.Model):
   # __tablename__ = 't_user'  # 设置表名
   id = db.Column(db.Integer, primary_key=True)  # 主键  默认主键自增
   name = db.Column(db.String(20), unique=True)  # 设置唯一
   # age = db.Column(db.Integer, doc='年龄int') # doc字段说明，和数据表没有关联性
   age = db.Column(db.Integer)
   # gender = db.Column(db.SmallInteger, default=0, doc='性别，默认0')

@app.route('/')
def index():
    # db.drop_all()  # 删除所有继承自db.Model的表
    db.create_all()  # 创建所有继承自db.Model的表 # 在这里建立了表格
    return "index"

@app.route('/add')
def add_data():
    user = t_user(name='wyf', age=26)
    db.session.add(user)
    db.session.commit()
    return 'add_data'

if __name__ == '__main__':
    app.run(debug=False)
