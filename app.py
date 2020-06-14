from flask import Flask, request, jsonify
import mysql.connector
import pytz


DB_HOST = 'mysql'
DB_USER = 'root'
DB_PSW = 'smartwatch'
DB_NAME = 'smartwatch'
TB_NAME = 'body_datas'

TIMEZONE = pytz.timezone('Asia/Shanghai')

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def post_datas():
    # return jsonify(request.form)
    sid = request.form.get('sid')
    T = request.form.get('T')
    hb = request.form.get('hb')
    bo = request.form.get('bo')

    mydb = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        passwd = DB_PSW,
        database = DB_NAME
    )

    mycursor = mydb.cursor()
    sql = 'INSERT INTO {} (sid, T, hb, bo) VALUES (%s, %s, %s, %s)'.format(TB_NAME)
    # tz_utc = timezone(timedelta(hours=8))
    # current_time_utc_8 = datetime.utcnow().replace(tzinfo=tz_utc)
    val = (sid, T, hb, bo)
    mycursor.execute(sql, val)
    mydb.commit()    

    return 'ok'

@app.route('/<sid>/<days>')
def get_temperature(sid, days):
    mydb = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        passwd = DB_PSW,
        database = DB_NAME
    )
    days *= 24 * 60
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    sql = 'SELECT * FROM {} WHERE sid=%s ORDER BY id DESC LIMIT %s'.format(TB_NAME)
    val = (sid, days)
    mycursor.execute(sql, val)
    res = mycursor.fetchall()
    if not res:
        return jsonify(res)

    ans = []
    today = res[0]['ctime'].day
    for i in range(len(res)):
        if res[i]['ctime'].day != today:
            break
        
        res[i]['ctime'] = str(res[i]['ctime'].astimezone(TIMEZONE))
        ans.append(res[i])
    
    return jsonify(ans)

@app.route('/analyze/<sid>')
def analyze(sid):
    mydb = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        passwd = DB_PSW,
        database = DB_NAME
    )
    days = 60 * 24
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    sql = 'SELECT * FROM {} WHERE sid=%s ORDER BY id DESC LIMIT %s'.format(TB_NAME)
    val = (sid, days)
    mycursor.execute(sql, val)
    res = mycursor.fetchall()

    if not res:
        return jsonify({
            'req_state' : 404
        })
    
    analyse = {
        'req_state' : 200
    }

    max_T, min_T = 0, 50
    min_BO = 100
    max_HB, min_HB = 0, 999

    fever_zone = []  
    fever_set = []
    low_temporate_zone = []
    low_temporate_set = []

    low_bo_zone = []
    low_bo_set = []

    high_hb_zone = []
    high_hb_set = []
    low_hb_zone = []
    low_hb_set = []    

    for i in range(len(res)):
        if res[i]['ctime'].day != res[0]['ctime'].day:
            break
        
        max_T = max(res[i]['T'], max_T)         # 最高体温
        min_T = min(res[i]['T'], min_T)         # 最低体温
        min_BO = min(res[i]['bo'], min_BO)      # 最低血氧
        max_HB = max(res[i]['hb'], max_HB)      # 最高心跳
        min_HB = min(res[i]['hb'], min_HB)      # 最低心跳

        res[i]['ctime'] = res[i]['ctime'].astimezone(TIMEZONE)
        
        # 体温区间
        if res[i]['T'] > 37:
            # 发热
            fever_set.append(res[i]['ctime'])    
        elif res[i]['T'] < 36:
            # 低温
            low_temporate_set.append(res[i]['ctime'])
        else:
            # 发热
            if fever_set:
                fever_set_temp = [
                    time_beautify(fever_set[-1].hour, fever_set[-1].minute),
                    time_beautify(fever_set[0].hour, fever_set[0].minute)
                ]
                fever_zone.append(fever_set_temp)
                fever_set.clear()
            # 低温
            elif low_temporate_set:
                low_temporate_set_temp = [
                    time_beautify(low_temporate_set[-1].hour, low_temporate_set[-1].minute),
                    time_beautify(low_temporate_set[0].hour, low_temporate_set[0].minute)
                ]
                low_temporate_zone.append(low_temporate_set_temp)
                low_temporate_set.clear()                

        # 低血氧区间
        if res[i]['bo'] < 90:
            low_bo_set.append(res[i]['ctime'])
        elif low_bo_set:
            low_bo_set_temp = [
                time_beautify(low_bo_set[-1].hour, low_bo_set[-1].minute),
                time_beautify(low_bo_set[0].hour, low_bo_set[0].minute)
            ]
            low_bo_zone.append(low_bo_set_temp)
            low_bo_set.clear()

        # 心跳区间
        if res[i]['hb'] < 40:
            low_hb_set.append(res[i]['ctime'])
        elif res[i]['hb'] > 100:
            high_hb_set.append(res[i]['ctime'])
        else:
            # 低心跳
            if low_hb_set:
                low_hb_set_temp = [
                    time_beautify(low_hb_set[-1].hour, low_hb_set[-1].minute),
                    time_beautify(low_hb_set[0].hour, low_hb_set[0].minute)
                ]
                low_hb_zone.append(low_hb_set_temp)
                low_hb_set.clear()
            # 高心跳
            elif high_hb_set:
                high_hb_set_temp = [
                    time_beautify(high_hb_set[-1].hour, high_hb_set[-1].minute),
                    time_beautify(high_hb_set[0].hour, high_hb_set[0].minute)
                ]
                high_hb_zone.append(high_hb_set_temp)
                high_hb_set.clear()


    # 发热
    if fever_set:
        fever_set_temp = [
            time_beautify(fever_set[-1].hour, fever_set[-1].minute),
            time_beautify(fever_set[0].hour, fever_set[0].minute)
        ]
        fever_zone.append(fever_set_temp)

    # 低温
    if low_temporate_set:
        low_temporate_set_temp = [
            time_beautify(low_temporate_set[-1].hour, low_temporate_set[-1].minute),
            time_beautify(low_temporate_set[0].hour, low_temporate_set[0].minute)
        ]
        low_temporate_zone.append(low_temporate_set_temp)

    # 低血氧
    if low_bo_set:
        low_bo_set_temp = [
            time_beautify(low_bo_set[-1].hour, low_bo_set[-1].minute),
            time_beautify(low_bo_set[0].hour, low_bo_set[0].minute)
        ]
        low_bo_zone.append(low_bo_set_temp)        

    # 低心跳
    if low_hb_set:
        low_hb_set_temp = [
            time_beautify(low_hb_set[-1].hour, low_hb_set[-1].minute),
            time_beautify(low_hb_set[0].hour, low_hb_set[0].minute)
        ]
        low_hb_zone.append(low_hb_set_temp)

    # 高心跳
    if high_hb_set:
        high_hb_set_temp = [
            time_beautify(high_hb_set[-1].hour, high_hb_set[-1].minute),
            time_beautify(high_hb_set[0].hour, high_hb_set[0].minute)
        ]
        high_hb_zone.append(high_hb_set_temp)

    analyse['fever_zone'] = fever_zone[::-1]
    analyse['low_temporate_zone'] = low_temporate_zone[::-1]
    analyse['temporate_diff'] = max_T - min_T
    analyse['low_bo_zone'] = low_bo_zone[::-1]
    analyse['low_bo'] = min_BO
    analyse['low_hb'] = min_HB
    analyse['high_hb'] = max_HB
    analyse['low_hb_zone'] = low_hb_zone[::-1]
    analyse['high_hb_zone'] = high_hb_zone[::-1]

    return jsonify(analyse)


def time_beautify(a,b):
    a = str(a)
    b = str(b)
    if len(a) < 2:
        a = "0" + a
    if len(b) < 2:
        b = "0" + b
    return a + ":" + b

# test
@app.route('/ts', methods=['POST'])
def ts():
    return jsonify(request.form) 

# @app.route('/ts')
# def ts():
#     mydb = mysql.connector.connect(
#         host = DB_HOST,
#         user = DB_USER,
#         passwd = DB_PSW,
#         database = DB_NAME
#     )

#     mycursor = mydb.cursor()
#     mycursor.execute('ALTER TABLE {} MODIFY bo INTEGER NOT NULL'.format(TB_NAME))
    

#     # res = mycursor.fetchone()
#     # res['ctime'] = res['ctime'].astimezone(TIMEZONE) 
#     return 'ok'


# @app.route('/all')
# def hello():
#     mydb = mysql.connector.connect(
#         host = DB_HOST,
#         user = DB_USER,
#         passwd = DB_PSW,
#         database = DB_NAME
#     )

#     mycursor = mydb.cursor(dictionary=True)
#     mycursor.execute('SELECT * FROM {}'.format(TB_NAME))
#     res = mycursor.fetchall()

#     return jsonify(res)
