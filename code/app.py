from flask import Flask
from flask import request
from messageloader import *
import json
# from  ticket import *
from cancel_ticket import *
from fakedata import *
from dataformat import *
from process import *
from arrange import *
from task import *
from share_car import *
from CancelCharterCar import CancelCharterCar
import requests
import json
from car_seat_info import *
from ReturnRequest import *
import itertools
import pickle
import pandas as pd
import openpyxl

'''
CAR_INFO_node
  "14": {
    "vehicleId": "14",
    "seat": 4,
    "carType": 1,
    "carOperatonStatus": 0,
    "lng": "114.371986",
    "lat": "22.708854",
    "status": 0,
    "driverId": "10010003"
  },
'''

car_seat_info = make_car_seat_info()
all_arranges = []

station_id = ['1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '1010', '1011', '1012', '1101',
              '1102', '1103', '1104', '1105', \
              '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1115', '1116', '1201', '1202',
              '1203', '1204', '1205', '1206', \
              '1207', '1208', '1209', '1210', '1211', '1212', '1301', '1302', '1303', '1304', '1305', '1306', '1307',
              '1308', '1309', '1310', '1311']

lon_scale = [121.32345, 121.227864]
lat_scale = [31.390933, 31.286396]
car_num = 5
tasks_all = dict()
tickets_buffer = dict()

app_car_info, app_city_info, app_platform_info, road_info = dataloader('data/data').load_all_info()
car_info = fakedatamaker(car_num, lat_scale, lon_scale, app_platform_info).makefakecarpos()
car_group_data = fakedatamaker(car_num, lat_scale, lon_scale, app_platform_info).car_group_data()


global time_count


with open('data/app_platform_info.pkl', 'rb') as f:
    app_platform_info = pickle.load(f)
f.close()
with open('data/road_info.pkl', 'rb') as f:
    road_info = pickle.load(f)
f.close()
with open('data/car_info.pkl', 'rb') as f:
    car_info = pickle.load(f)
f.close()
with open('data/car_group_data.pkl', 'rb') as f:
    car_group_data = pickle.load(f)
f.close()

print(car_info)
print(car_group_data)
init_group_car(car_group_data)
# print(road_info)
print(car_group_data)
print(car_info)


############################### 日志编写函数  ########################
def log_writer(route, info, res):
    try:
        f = "data/log.txt"
        with open(f, encoding='utf-8', mode='a') as file:  # 只需要将之前的”w"改为“a"即可，代表追加内容
            try:
                stamp = int(time.time())
                log = "################################################################"
                log = log + time.strftime("%Y-%m-%d %H:%M",
                                          time.localtime(stamp)) + "\n" + "请求路由:\n" + route + "\n" + "请求信息内容:\n" + str(
                    info) + "\n返回信息内容:\n" + str(res) + "\n\n"
                log += "----------当前车辆状态：\n CAR_GROUP_DATA:\n" + str(car_group_data) + "\nCAR_INO\n" + str(car_info)
                file.write("\n\n")
                file.write(log)
                file.close()
                return "ok"
            except:
                file.write("!!!!!!!!!!!!!!\n\n" + "LOG INFO PROBLEM\n\n")
                return "NOT OK"
    except:
        print("LOG OPEN PROBLEM!!!!")
        return "NOT OK"


## 1 将车辆信息和站点绑定
## 2 分配车辆时考虑车辆的位置
## 3 得到车辆的行驶轨迹
## 4 假订单生成的程序

app = Flask(__name__)


# 建立一个测试函数
@app.route('/print_roadinfo', methods=['GET', 'POST'])
def print_roadinfo():
    df_index = pd.DataFrame.from_dict(road_info, orient='index')
    df_index.to_excel("data/road_info.xlsx")
    log_writer("print_roadinfo", "null", "null")
    return json.dumps({"status": 1, "suggust": 'ok'})


# 路网信息更新系统接口
@app.route('/info_update', methods=['GET', 'POST', 'DELECT'])
def info_update():
    if request.method == 'POST':
        try:
            result = request.json
            print(request.json)
            print(result)
            road_info1, app_platform_info1 = messageloader(result).road_info_maker()
            road_info_update(road_info1, app_platform_info1)
            global road_info
            road_info = road_info1
            global app_platform_info
            app_platform_info = app_platform_info1
            print(road_info)
            global time_count
            time_count = 0

            with open('data/app_platform_info.pkl', 'wb') as f:
                pickle.dump(app_platform_info, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            with open('data/road_info.pkl', 'wb') as f:
                pickle.dump(road_info, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            log_writer("info_update", request.json, json.dumps({"status": 1, "suggust": ''}))
            return json.dumps({"status": 1, "suggust": ''})
        except:
            log_writer("info_update", request.json, json.dumps({"status": 0, "suggust": ''}))
            return json.dumps({"status": 0, "suggust": ''})


# 新增算法系统接口
# 接口地址							http://47.111.139.187:5000/algorithm
# 返回格式							Json数组
# 请求方式							基于FLASK框架；请求方式：POST
# 输入参数	参数名		参数含义		字段名		数据类型	数据含义		实例(备注)
# 	df_1(orderData)		订单表数据		o_id	oId	str	订单唯一表示ID
# 					from_p_id	fromId	int(str)	出发站ID
# 					to_p_id	toId	int(str)	到达站ID
# 					start_time	startTime	datetime	出发时刻
# 					ticket_number	ticketNumber	int	车票数量
# 						orderStatus	int	订单状态		1为提前预约成功的，0为其他订单
# 					order_time	orderTime	datetime	下单时间
# 					set_time	setTime	int	设置时间阈值
# 输出参数	status		状态参数		status	status	int	状态参数		1：有输入数据但都有车，0：无输入数据，2：有输入数据部分有车；3：有输入数据全部无车
# 	task		新发布的调度信息表数据
# 					it_number	itNumber	int	乘车总人数
# 					car_id	carId	int(str)	车辆ID
# 					from_p_id	fromId	int(str)	起始站点ID
# 					from_order_name	fromName	str	起始站点名称
# 					to_p_id 	toId	int(str)	目的站点ID
# 					to_order_name	toName	str	目的站点名称
# 					park_id	parkId	int(str)	中间停站站点ID
# 					park_name	parkName	str	中间停站站点名称
# 					start_time	startTime	str	行程开始时间
# 					correspond_order_id	correspondOrderId	str	调度任务对应的订单编号
# 					correspond_order_number	correspondNumber	str	每个订单对应上车人数		如：“101:3,102:4”表示订单号为101的有3人上车，订单号为102的有4人上车
# 					travel_id	travelId	str	调度命令ID
# 					driver_id	driverId	int(str)	司机ID
# 					driver_content	driverContent	str	司机提示信息
# 					all_travel_plat	travelPlat	str	车辆行驶路径列表
# 					expected_time	expectedTime	int	全程预计时长		单位秒
# 					arrive_time	arriveTime	str	预计到站时间
# 					distance	distance	int	车辆预计行驶距离
# 					modify_id	modifyOrderId	str	是否修改命令		命令链接到要修改的travel_id
# 					warning	warning	str	警告		若OD两地之间不连接，提示“目的地错误，两地之间没有通路”

@app.route('/algorithm', methods=['GET', 'POST', 'DELECT'])
def get_name():
    if request.method == 'POST':
        # try:
        global time_count
        print(car_group_data)
        print(car_info)
        tickets_json = request.json

        print(request.json)
        tickets = dict()
        for num, ticket in enumerate(tickets_json):
            tickets[ticket["oId"]] = ticket
        tasks = dict()
        status = []
        new_tickets = merge_to_newtickets(tickets)
        print(new_tickets)
        counter=0
        for name in new_tickets.keys():
            ticket = new_tickets[name]
            start_pos = ticket['fromId']
            cars, seat = get_cars(car_info, ticket, start_pos, road_info, app_platform_info, car_group_data)
            print(cars, seat, ticket['ticketNumber'])
            if cars and counter<len(cars):
                counter += 1
                if len(tasks) == 0:
                    begin_id = len(tasks_all)
                else:
                    begin_id = len(tasks_all) + len(tasks)
                print(ticket)
                tasks = arrange_task(tasks, cars, seat, car_info, ticket, road_info, app_platform_info, begin_id,
                                     tickets,time_count)
                time_count+=1
                for i in range(len(cars)):
                    status.append(1)
            else:
                # return 'car is not enough'
                status.append(3)
            car_info_update(cars, car_info)

        final_info = []
        flag = 0
        final_task = dict()
        final_task['task'] = []
        final_task['line'] = []
        for num, sta in enumerate(status):
            if sta == 3:
                if 1 not in status:#如果说有车可以派车那就不用管了
                    final_task['status'] = 3
            else:
                final_task['status'] = 1
                final_task['task'].append(tasks[list(tasks.keys())[flag]])
                flag += 1
        final_info = final_task
        add_new_task_to_all(tasks, tasks_all)
        result = json.dumps(final_info, ensure_ascii=False).encode('utf8')
        log_writer("/algorithm", request.json, result)
        return result


# 车辆信息更新系统接口
# 接口地址			http://47.111.139.187:5000/carinfo_update
# 返回格式			Json
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义	实例(备注)
# 	c_id	carId	int(str)	车辆ID	只传c_status=1的
# 	car_seat_number	carSeatNumber	int	车辆座位数
# 	car_type	carType	int	车辆类型
# 	  c_code                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                	cityType	int	城市类型	根据大数据要求传，传编码为城市的
# 		carOperationStatus	int	车辆启用状态	1禁用，0启用
# 输出参数	status	status	int 	更新状态参数	1：更新成功；0：更新失败

@app.route('/carinfo_update', methods=['GET', 'POST', 'DELECT'])
def carinfo_update():
    if request.method == 'POST':
        try:
            global car_info
            car_info = dict()
            global car_group_data
            car_group_data = dict()
            new_car_info = request.json
            print(request.json)
            print(car_group_data)
            for car in new_car_info:
                temp_car_info = dict()
                temp_car_info['vehicleId'] = car['carId']
                temp_car_info['seat'] = car['carSeatNumber'] - 1
                temp_car_info['carType'] = car['carType']
                temp_car_info['carOperatonStatus'] = car['carOperatonStatus']
                # temp_car_info['driverId'] = car['driverId']
                car_info[car['carId']] = temp_car_info
                init_group_car(car_group_data)
                print(car_info)
            with open('data/car_info.pkl', 'wb') as f:
                pickle.dump(car_info, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            log_writer("/carinfo_update", request.json, json.dumps({"status": 1}))
            return json.dumps({"status": 1})
        except:
            log_writer("/carinfo_update", request.json, json.dumps({"status": 0}))
            return json.dumps({"status": 0})


# 车辆状态更新系统接口
# 接口地址		http://47.111.139.187:5000/carStatusUp
# 返回格式		Json
# 请求方式		基于FLASK框架；请求方式：POST
# "输入参数
# （数组）"		数据类型	数据含义	实例(备注)
# 	cityType	str	城市类型	根据大数据要求传，传编码为城市的
# 	carId	str	车辆ID
# 	carType	int	车辆类型
# 	carSeatNumber	int	车辆座位数
# 	carLoc	str	车辆GPS数据	,分隔经纬度，不可用时为空
# 	carStatus	int	车辆状态	0不可用，1可用
# 	driverid	str	司机id	不可用时为空
# 输出参数	status	int 	更新状态参数	1：更新成功；0：更新失败

@app.route('/carStatusup', methods=['GET', 'POST', 'DELECT'])
def carStatusup():
    if request.method == 'POST':
        try:
            new_car_info = request.json
            print(request.json)
            print(new_car_info)
            for car in new_car_info:
                car_id = car['carId']
                if car_id not in car_info.keys():
                    return json.dumps({"status": 0})
                car_info['busy'] = 0
                temp_car_info = car_info[car_id]
                temp_car_info['lng'] = car['carLoc'].split(',')[0]
                temp_car_info['lat'] = car['carLoc'].split(',')[1]
                temp_car_info['status'] = abs(1 - car['carStatus'])
                temp_car_info['driverId'] = car['driverId']
                temp_car_info['busy'] = 0
                if temp_car_info['status'] == 1:
                    temp_car_info['busy'] = 1
                car_info[car_id] = temp_car_info
                if car['carStatus'] == 1 and car_id not in car_group_data.keys():
                    car_group_data[car_id] = dict()
                    car_group_data[car_id]['carId'] = car_id
                    car_group_data[car_id]['car_gps'] = car['carLoc']
                    car_group_data[car_id]['marshalling_list'] = []
                elif car['carStatus'] == 1 and car_id in car_group_data.keys():
                    car_group_data[car_id]['car_gps'] = car['carLoc']
                if car['carStatus'] == 0 and car_id in car_group_data.keys():
                    del car_group_data[car_id]
            init_group_car(car_group_data)
            with open('data/car_info.pkl', 'wb') as f:
                pickle.dump(car_info, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            with open('data/car_group_data.pkl', 'wb') as f:
                pickle.dump(car_group_data, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            log_writer("/carStatusup", request.json, json.dumps({"status": 1}))
            return json.dumps({"status": 1})
        except:
            log_writer("/carStatusup", request.json, json.dumps({"status": 0}))
            return json.dumps({"status": 0})


@app.route('/carpos_update', methods=['GET', 'POST', 'DELECT'])
def carpos_update():
    if request.method == 'POST':
        try:
            new_car_info = request.json
            print(request.json)
            print(new_car_info)
            for car in new_car_info:
                car_id = car['carId']
                if car_id not in car_info.keys() or car_id not in car_group_data.keys():
                    return json.dumps({"status": 0})
                temp_car_info = car_info[car_id]
                temp_car_info['lng'] = car['carLoc'].split(',')[0]
                temp_car_info['lat'] = car['carLoc'].split(',')[1]
                car_info[car_id] = temp_car_info
                car_group_data[car_id]['car_gps'] = car['carLoc']
            init_group_car(car_group_data)
            log_writer("/carpos_update", request.json, json.dumps({"status": 1}))
            return json.dumps({"status": 1})
        except:
            log_writer("/carpos_update", request.json, json.dumps({"status": 0}))
            return json.dumps({"status": 0})


@app.route('/test', methods=['GET', 'POST', 'DELECT'])
def test():
    if request.method == 'POST':
        new_car_info = request.json
        print(app_platform_info)
        print(car_group_data)
        print(car_info)
        print(tasks_all)
        log_writer('/test', request.json, json.dumps({"status": 1}))
        return json.dumps({"status": 1})


# 预约快速响应算法系统接口
# 接口地址			http://47.111.139.187:5000/ReturnRequest
# 返回格式			Json数组
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义		实例(备注)
# 	o_id	oId	str	订单唯一表示ID
# 	from_p_id	fromId	int(str)	出发站ID
# 	to_p_id	toId	int(str)	到达站ID
# 	start_time	startTime	datetime	出发时刻
# 	ticket_number	ticketNumber	int	车票数量
# 输出参数	status	status	int	状态参数		201成功；301-305都为失败，原因都不同
# 	suggest	suggest	str	建议

@app.route('/algorithmD', methods=['GET', 'POST', 'DELECT'])
def ReturnRequest1():
    if request.method == 'POST':
        print(request.json)
        tasks_in = request.json
        res = ReturnRequest(tasks_in)
        log_writer('/algorithmD',request.json,res)
        return res


# 司机信息更新系统接口
# 接口地址			http://47.111.139.187:5000/driverinfo_update
# 返回格式			Json
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义		实例(备注)
# 	cityType	cityType	int	城市类型		根据大数据要求传
# 	u_id	userId	int（str）	用户ID		只传司机信息
# 	u_name	userName	str	用户名
# 输出参数	status	status	int 	更新状态参数		1：更新成功；0：更新失败

@app.route('/driverinfo_update', methods=['GET', 'POST', 'DELECT'])
def driverinfo_update():
    if request.method == 'POST':
        print(request.json)
        driver_info = request.json
    log_writer('/driverinfo_update', request.json, json.dumps([1]))
    return json.dumps([1])


# 新增行程座位分配系统接口
# 接口地址			http://47.111.139.187:5000/seat_allocation
# 返回格式			Json
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义		实例(备注)
# 	travel_id	travelId	str	调度命令ID
# 	modifyOrderId	modifyOrderId	str		对应的旧的调度命令ID	可以为""
# 	car_id	carId	int (str)	车辆ID
# 	correspond_order_id	correspondOrderId	str	调度任务对应的订单编号
# 	correspond_order_number	correspondNumber	str	每个订单对应的上车人数		“101:2,102:3”
# 	order_u_id	orderUserId	jsonarr	各订单包含的所有乘客的uid		"[{""orderId"":""订单id"", ""userId"":""621,622,623""}，
# {""orderId"":""订单id"",""userId"":""所有用户id""}]
# "
# 	user_preference	userPreference	jsonarr	订单包含的乘客及其座位偏好信息		"[{""userId"":""621"",""seatPreference"":""1，3""}，
# {""userId"":""乘客编号"",""seatPreference"":""第一组，第二组""}]
# "
# 	carType	carType	int	是否包车		1：包车。0不包车
# 输出参数	car_id	carId	int(str)	车辆ID
# 	correspond_seat_id	correspondSeatId	jsonarr	每个订单中各乘客与对应的座位号		"[
# {""orderId"":""订单id"",
# ""seatId"":[{""userId"":""621"",""seat"":""A1""}，
# {""userId"":""乘客编号"",""seat"":""座位号""}]
# }
# ]
# "
@app.route('/seat_allocation', methods=['GET', 'POST', 'DELECT'])
def seat_allocation():
    if request.method == 'POST':
        tickets_json = request.json
        print(tickets_json)
        tickets = dict()
        arranges = []
        for num, ticket in enumerate(tickets_json):
            tickets[str(ticket["travelId"])] = ticket
        for name in tickets.keys():
            task = tasks_all[name]
            ticket = tickets[name]
            seat_arrange = arrange_seat_2_seat(ticket, task, car_seat_info, car_info)
            arranges.append(seat_arrange)
            all_arranges.append(seat_arrange)
    log_writer("/seat_allocation", request.json, json.dumps({"status": 1}))
    return json.dumps(arranges)


# 加入行程算法系统接口
# 接口地址						http://47.111.139.187:5000/algorithmA
# 返回格式						Json数组
# 请求方式						基于FLASK框架；请求方式：POST
# 输入参数	参数名		参数含义			数据类型	数据含义		实例(备注)
# 	orderData		新增订单数据		oId	str	订单唯一表示ID
# 					fromId	str	出发站ID
# 					toId	str	到达站ID
# 					startTime	datetime	出发时刻
# 					ticketNumber	int	车票数量
# 					orderUserId	str	订单包含的所有乘客id		如：“621，622”
# 					userPreference	jsonarr	订单包含的乘客及其座位偏好信息		如[{"userId":"621","seatPreference":"1，3"}，{"userId":"乘客编号","seatPreference":"第一组，第二组"}]
# 	travelId					str	行程id
# 	correspondSeatId					jsonarr	每个订单中各乘客与对应的座位号		"如[{""userId"":""621"",""seat"":""A1""}，
# {""userId"":""乘客编号"",""seat"":""座位号""}]
# }]"
# 输出参数	status		状态参数		status	int	状态参数		1成功，0失败
# 	task		反馈指令		travelId	str	行程id
# 					itNumber	int	乘车总人数
# 					correspondNumber	str	每个订单对应上车人数		（增加了新加入订单信息）
# 					correspondSeatId	dict	每个订单中各乘客uid列表与对应的座位号列表		（增加了新加入订单信息）

@app.route('/algorithmA', methods=['GET', 'POST', 'DELECT'])
def share_car():
    if request.method == 'POST':
        tickets = [request.json]
        print(request.json)
        tasks = dict()
        # new_tickets = merge_to_newtickets(tickets)
        for ticket in tickets:
            start = ticket['fromId']
            if app_platform_info[start]['p_route_type'] == '2':
                task_id = share_car_task_arrange(tasks_all, ticket, car_info, app_platform_info)
        return_info = []
        for name in range(len(tickets)):
            start = tickets[name]['fromId']
            if app_platform_info[start]['p_route_type'] == '2':
                ticket = tickets[name]
                return_message = share_car_task_arrange(tasks_all, ticket, car_info, app_platform_info)
                return_info.append(return_message)
        log_writer("/algorithmA", request.json, json.dumps(return_info))
        return json.dumps(return_info)


# 取消行程算法系统接口
# 接口地址						http://47.111.139.187:5000/algorithmC
# 返回格式						Json数组
# 请求方式						基于FLASK框架；请求方式：POST
# 输入参数	参数名		参数含义			数据类型	数据含义		实例(备注)
# 	orderData		删除订单数据		oId	str	订单唯一表示ID
# 					fromId	str	出发站ID
# 					toId	str	到达站ID
# 					startTime	datetime	出发时刻
# 					ticketNumber	str	车票数量		如："1/2"
# 					orderUserId	str	订单包含的删除乘客id		如：“621，622”
# 	travelId					str	行程id
# 	correspondSeatId					jsonarr	每个订单中各乘客与对应的座位号		"如[{""userId"":""621"",""seat"":""A1""}，
# {""userId"":""乘客编号"",""seat"":""座位号""}]
# }]"
# 输出参数	status		状态参数			int	状态参数		1成功，0失败
# 	task		指定调度指令记录		travelId	str	行程id
# 					inNumber	int	乘车总人数
# 					carId	str	车辆ID
# 					fromId	str	起始站点ID
# 					fromName	str	起始站点名称
# 					toId	str	目的站点ID
# 					toName	str	目的站点名称
# 					parkId	str	中间停站站点ID
# 					parkName	str	中间停站站点名称
# 					startTime	str	行程开始时间
# 					correspondOrderId	str	调度任务对应的订单编号
# 					correspondNumber	str	每个订单对应上车人数		如：“101:3,102:4”表示订单号为101的有3人上车，订单号为102的有4人上车
# 					driverId	int	司机ID
# 					driverContent	str	司机提示信息
# 					travelPlat	str	车辆行驶路径列表
# 					expectedTime	int	全程预计时长
# 					distance	int	车辆预计行驶距离
# 					modifyOrderId	int	是否修改命令		命令链接到要修改的travel_id
# 					warning	str	警告		提示无车，有几人未上车
# 	correspondSeatId					jsonarr	每个订单中各乘客与对应的座位号		（删除取消预约乘客后）

@app.route('/algorithmC', methods=['GET', 'POST', 'DELECT'])
def delete_ticket():
    if request.method == 'POST':
        tickets = request.json
        print(request.json)
        return_info = []
        all_user = []
        for ticket in tickets:
            all_user = ticket['orderUserId'].split(',')
        task_user = dict()
        for user in all_user:
            for x, arrange in enumerate(all_arranges):
                temp = []
                for n, user_info in enumerate(arrange['correspondSeatId']):
                    if user == user_info['u_id']:
                        if arrange['carId'] not in task_user.keys():
                            task_user[arrange['carId']] = [user]
                        else:
                            task_user[arrange['carId']].append(user)
                        continue
                    temp.append(n)
                remain_user = [all_arranges[x]['correspondSeatId'][i] for i in temp]
                all_arranges[x]['correspondSeatId'] = remain_user
        print(task_user)
        for carId in task_user.keys():
            for arrange in all_arranges:
                if arrange['carId'] == carId:
                    correspondSeatId = arrange['correspondSeatId']
            status = 1
            for n in tasks_all.keys():
                task = tasks_all[n]
                if task['carId'] == carId:
                    task['itNumber'] -= len(task_user[carId])
                    if task['itNumber'] <= 0:
                        car_info[carId]['status'] = 0
                        del tasks_all[n]
                        break
                # else:
                # for ticket in tickets:
                # for user in task_user[carId]:
                # if user in ticket['orderUserId'].split(','):
                #    task['correspondNumber'][ticket['oId']]-=1
                #    if task['correspondNumber'][ticket['oId']]<=0:
                #        del task['correspondNumber'][ticket['oId']]
                #    break

            tasks_all[n] = task
            return_info.append({'status': status, 'task': task, 'correspondSeatId': correspondSeatId})
        log_writer("/algorithmC", request.json, json.dumps(return_info))
        return json.dumps(return_info)


@app.route('/marshalling', methods=['GET', 'POST', 'DELECT'])
def marshalling():
    if request.method == 'POST':
        print(request.json)
        car_return = dict()
        car_info = request.json
        car_return['carId'] = car_info['carId']
        car_gps = car_info['car_gps']
        lng = float(car_gps.split(',')[0])
        lat = float(car_gps.split(',')[1])
        for car in car_group_data:
            car_gps = car_group_data[car]['car_gps']
            lng1 = float(car_gps.split(',')[0])
            lat1 = float(car_gps.split(',')[1])
            if compute_dist(lng, lat, lng1, lat1) < 30:
                car_info['marshalling_list'] = car_group_data[car]['marshalling_list']
                car_info['marshalling_list'].append(car_info['carId'])
                car_group_data[car_info['carId']] = car_info
                init_group_car(car_group_data)
                print(car_group_data)
                car_return['car_status'] = 1
                car_return['new_marshalling_list'] = car_info['marshalling_list']
                return car_return
        car_group_data[car_info['carId']] = car_info
        init_group_car(car_group_data)
        car_return['car_status'] = 0
        car_return['new_marshalling_list'] = []
        print(car_group_data)
        log_writer("/marshalling", request.json, car_return)
        return car_return


# 包车算法系统接口
# 接口地址			http://47.111.139.187:5000/CharterCar
# 返回格式			Json数组
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义		实例(备注)
# 	o_id	oId	str	订单唯一表示ID
# 	from_p_id	fromId	str	出发站ID
# 	to_p_id	toId	str	到达站ID
# 	start_time	startTime	datetime	出发时刻
# 	chartered_bus	charteredBus	str	包车类型
# 	it_number	ticketNumber	str	车票数量
# 输出参数	code	status	int	状态参数		201成功；301为失败
# 	message	suggest	str	建议
# 	task（数组）	itNumber	int	包车订单信息（失败时无此字段）
# 		carId	str
# 		fromId	str
# 		fromName	str
# 		toId	str
# 		toName	str
# 		parkId	str
# 		parkName	str
# 		startTime	str
# 		correspondOrderId	str
# 		correspondNumber	str
# 		travelId	str
# 		driverId	str
# 		driverContent	str
# 		travelPlat	str
# 		expectedTime	int
# 		arriveTime	str
# 		distance	int

@app.route('/CharterCar', methods=['GET', 'POST', 'DELECT'])
def chartercar():
    if request.method == 'POST':
        print(request.json)
        tasks = dict()
        message = request.json
        tickets = dict()
        for ticket in message:
            ticket['itNumber'] = ticket['charteredBus']
            ticket['ticketNumber'] = ticket['itNumber']
            ticket['correspondOrderId'] = [ticket['oId']]
            tickets[ticket['oId']] = ticket
        status = []
        # print(tickets)
        for oId in tickets.keys():
            ticket = tickets[oId]
            print(ticket)
            start_pos = ticket['fromId']
            cars, seat = get_cars(car_info, ticket, start_pos, road_info, app_platform_info)
            if cars:
                if len(tasks) == 0:
                    begin_id = len(tasks_all)
                else:
                    begin_id = len(tasks_all) + len(tasks)
                    print(ticket)
                tasks = arrange_task(tasks, cars, seat, car_info, ticket, road_info, app_platform_info, begin_id,
                                     tickets,time_count)
                status.append(201)
            else:
                # return 'car is not enough'
                status.append(301)
            car_info_update(cars, car_info)
        final_info = []
        flag = 0
        for num, sta in enumerate(status):
            if sta == 301:
                final_task = dict()
                final_task['code'] = 301
                final_task['task'] = []
                final_task['message'] = []
                final_info.append(final_task)
            else:
                final_task = dict()
                final_task['code'] = 201
                final_task['task'] = tasks[list(tasks.keys())[flag]]
                final_task['message'] = []
                final_info.append(final_task)
                flag += 1
        add_new_task_to_all(tasks, tasks_all)
        print(tasks_all)
        log_writer("/CharterCar", request.json, json.dumps(final_info))
        return json.dumps(final_info)


# 包车算法系统接口
# 接口地址			http://47.111.139.187:5000/CancelCharterCar
# 返回格式			Json数组
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义		实例(备注)
# 	o_id	oId	str	订单唯一表示ID
# 	from_p_id	fromId	str	出发站ID
# 	to_p_id	toId	str	到达站ID
# 	start_time	startTime	datetime	出发时刻
# 	chartered_bus	charteredBusNum	str	车号		-1为不包车，其他为包车单的车号
# 	it_number	ticketNumber	str	车票数量
# 输出参数	code	status	int	状态参数		201成功；301为失败
# 	message	suggest	str	建议

@app.route('/CancelCharterCar', methods=['GET', 'POST', 'DELECT'])
def CancelCharterCar2():
    if request.method=='POST':
        print(request.json)
        res = CancelCharterCar(request.json)
        log_writer('/CancelCharterCar', request.json, res)
        return res




# def CancelCharterCar():
#     if request.method == 'POST':
#         print(request.json)
#         tasks = dict()
#         message = [request.json]
#         tickets = dict()
#         for num, ticket_info in enumerate(message):
#             ticket = dict()
#             ticket['oId'] = ticket_info['oId']
#             ticket['fromId'] = ticket_info['oId']
#             ticket['toId'] = ticket_info['toId']
#             ticket['startTime'] = ticket_info['startTime']
#             ticket['charteredBusNum'] = ticket_info['charteredBusNum']
#             ticket['ticketNumber'] = ticket_info['ticketNumber']
#             tickets[num] = ticket
#         print(car_info)
#
#         return_info = []
#         for Id in tickets.keys():
#             ticket = tickets[Id]
#             carId = ticket['charteredBusNum']
#             flag = 0
#             for task_id in tasks_all.keys():
#                 task = tasks_all[task_id]
#                 if carId != task['carId']:
#                     continue
#                 else:
#                     del tasks_all[task_id]
#                     flag = 1
#                     car_info[carId]['status'] = 0
#                     return_message = dict()
#                     return_message['status'] = 201
#                     return_message['suggest'] = ''
#                     return_info = return_message
#                     break
#             if flag != 1:
#                 return_message = dict()
#                 return_message['status'] = 301
#                 return_message['suggest'] = ''
#                 return_info = return_message
#         log_writer("/CancelCharterCar", request.json, return_info)
#         return json.dumps(return_info)


# 包车行程座位分配系统接口(在接口表现上和新增行程座位分配没有区别，是否输入参数加个type区分？)
# 接口地址			http://47.111.139.187:5000/seat_allocation_for_charetercar
# 返回格式			Json
# 请求方式			基于FLASK框架；请求方式：POST
# 输入参数	字段名		数据类型	数据含义		实例(备注)
# 	travel_id	travelId	str	调度命令ID
# 	car_id	carId	int (str)	车辆ID
# 	correspond_order_id	correspondOrderId	str	调度任务对应的订单编号
# 	correspond_order_number	correspondNumber	str	:每个订单对应的上车人数		“101:2,102:3”
# 	order_u_id	orderUserId	jsonarr	各订单包含的所有乘客的uid		"[{""orderId"":""订单id"", ""userId"":""621,622,623""}，
# {""orderId"":""订单id"",""userId"":""所有用户id""}]
# "
# 	user_preference	userPreference	jsonarr	订单包含的乘客及其座位偏好信息		"[{""u_id"":""621"",""seat_preference"":""1，3""}，
# {""u_id"":""乘客编号"",""seat_preference"":""第一组，第二组""}]
# "
# 输出参数	carId	carId	int (str)	车辆ID
# 	correspond_seat_id	correspondSeatId	jsonarr	每个订单中各乘客与对应的座位号		"[
# {""orderId"":""订单id"",
# ""seatId"":[{""u_id"":""621"",""seat"":""A1""}，
# {""u_id"":""乘客编号"",""seat"":""座位号""}]
# }
# ]
# "

@app.route('/seat_allocation_for_charetercar', methods=['GET', 'POST', 'DELECT'])
def seat_allocation_for_charetercar():
    if request.method == 'POST':
        print(request.json)
        tickets_json = request.json
        tickets = dict()
        arranges = []
        for num, ticket in enumerate(tickets_json):
            tickets[ticket["travelId"]] = ticket
        for name in tickets.keys():
            task = tasks_all[name]
            ticket = tickets[name]
            seat_arrange = arrange_seat_2_seat(ticket, task, car_seat_info, car_info)
            arranges.append(seat_arrange)
    log_writer("/seat_allocation_for_charetercar", request.json, json.dumps(arranges))
    return json.dumps(arranges)


# 路径规划与距离计算系统接口
# 接口地址		http://47.111.139.187:5000/path_planning
# 返回格式		Json
# 请求方式		基于FLASK框架；请求方式：POST
# 输入参数	字段名	数据类型	数据含义		实例(备注)
# 	fromId	str	起点站ID
# 	toId	str	终点站ID
# 	wayId	str	中间站ID		以;隔开
# 输出参数	status	int	状态参数		1成功，0失败
# 	travelPlat	str	路径站点编号信息
# 	distance	int	距离

@app.route('/path_planning', methods=['GET', 'POST', 'DELECT'])
def path_planning():
    if request.method == 'POST':
        print(request.json)
        # print(road_info)
        tasks = dict()
        message = [request.json]
        return_info = []
        for path_info in message:
            fromId = path_info['fromId']
            toId = path_info['toId']
            wayId = path_info['wayId'].split(',')
            if wayId[0] == '':
                info = dict()
                info['status'] = 1
                info['distance'] = road_info[fromId][toId]['dist']
                info['travelPlat'] = ",".join(road_info[fromId][toId]['route'] + [toId])
                return_info = info
            else:
                info = dict()
                min_dist = 9999999999999
                sta = []
                for stations in itertools.permutations(wayId):
                    stations = list(stations)
                    pre = [fromId] + stations
                    back = stations + [toId]
                    dist = 0
                    for st1, st2 in zip(pre, back):
                        dist += road_info[st1][st2]['dist']
                        # stations = road_info[st1][st2]['route']
                    if dist < min_dist:
                        sta = stations
                        min_dist = dist
                route = []
                pre = [fromId] + stations
                back = stations + [toId]
                for st1, st2 in zip(pre, back):
                    route = route + [st1] + road_info[st1][st2]['route']
                info['status'] = 1
                info['distance'] = min_dist
                info['travelPlat'] = ",".join(route + [toId])
                return_info = info
        log_writer("/seat_allocation_for_charetercar", request.json, json.dumps(return_info))
        return json.dumps(return_info)


'''
新增接口
去除掉car_info当中的信息同时进行同步
'''

if __name__ == '__main__':
    time_count = 0
    try:
        app.run(host='0.0.0.0', port=80)
    except:
        app.run(host='0.0.0.0', port=83)
