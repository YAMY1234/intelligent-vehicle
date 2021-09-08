import numpy as np
from process import *
import datetime
import time

''' 
输入:
passengers: 乘客数量 int 
car_rest_info：剩余的车辆情况 dict() eg: {4:1, 14:20, 22:0} 1个四座车，20个14座车
car_book_info：本次订单车辆的分配 dict() 初始{4:0, 14:0, 22:0}
rest_seat：剩下的空位 int
输出：
car_book_info: 本次订单车辆的分配 dict() 初始{4:1, 14:0, 22:0} 分配一辆四座车
说明：
针对剩余车辆的情况和订单信息对车辆进行分配。
'''

def arrange_car(passengers, car_rest_info, car_book_info, rest_seat):
    car_book_info = dict()
    for seats in [22, 14, 4]:
        car_book_info[seats] = dict()
        car_book_info[seats]['num'] = 0
        car_book_info[seats]['seat_info'] = []

    if rest_seat < passengers:
        print('to many passengers')
        return None
    while(passengers > 0):
        if passengers > 14:
            if car_rest_info[22] > 0:
                car_book_info[22]['num'] += 1
                car_rest_info[22] -= 1
                if passengers >= 22:
                    car_book_info[22]['seat_info'].append(22)
                else:
                    car_book_info[22]['seat_info'].append(passengers)
                passengers -= 22
            elif car_rest_info[14] > 0:
                car_book_info[14]['num'] += 1
                car_rest_info[14] -= 1
                car_book_info[14]['seat_info'].append(14)
                passengers -= 14
            elif car_rest_info[4] > 0:
                car_book_info[4]['num'] += 1
                car_rest_info[4] -= 1
                car_book_info[4]['seat_info'].append(4)
                passengers -= 3 # 4
        elif passengers > 3: # 4
            if car_rest_info[14] > 0:
                car_book_info[14]['num'] += 1
                car_rest_info[14] -= 1
                car_book_info[14]['seat_info'].append(passengers)
                passengers -= 14
            elif car_rest_info[4] > 0:
                car_book_info[4]['num'] += 1
                car_rest_info[4] -= 1
                car_book_info[4]['seat_info'].append(3)# 4
                passengers -= 3 # 4
            elif car_rest_info[22] > 0:
                car_book_info[22]['num'] += 1
                car_rest_info[22] -= 1
                car_book_info[22]['seat_info'].append(passengers)
                passengers -= 22
        else:
            if car_rest_info[4] > 0:
                car_book_info[4]['num'] += 1
                car_rest_info[4] -= 1
                car_book_info[4]['seat_info'].append(passengers)
                passengers -= 3 # 4
            elif car_rest_info[14] > 0:
                car_book_info[14]['num'] += 1
                car_rest_info[14] -= 1
                car_book_info[14]['seat_info'].append(passengers)
                passengers -= 14
            elif car_rest_info[22] > 0:
                car_book_info[22]['num'] += 1
                car_rest_info[22] -= 1
                car_book_info[22]['seat_info'].append(passengers)
                passengers -= 22
    return car_book_info



### 根据经纬度计算直线距离匹配

def select_car1(car_info, num, start_pos):
    car_dist_info = dict()
    for car in car_info.keys():
        car_lat = car_info[car]['lat']
        car_lng = car_info[car]['lng']
        dist = compute_dist(car_lng, car_lat, start_pos[0], start_pos[1])
        car_dist_info[car] = dist
    print(car_dist_info)
    car_dist_info = dict(sorted(car_dist_info.items(), key = lambda x:x[1], reverse=False))
    #print(car_dist_info)
    cars = list(car_dist_info.keys())[:num]

    return cars



def compute_dist_map(road_info, app_platform_info, car_lat, car_lng, start_pos):
    dist = np.inf
    tar = ''
    for station in app_platform_info.keys():
        #chengprint(car_lng, car_lat, app_platform_info[station]['longitude'], app_platform_info[station]['latitude'])
        print(car_lng, car_lat, app_platform_info[station]['longitude'], app_platform_info[station]['latitude'])
        temp = compute_dist(float(car_lng), float(car_lat), float(app_platform_info[station]['longitude']), float(app_platform_info[station]['latitude']))
        if temp < dist:
            dist = temp
            tar = station
    dist = road_info[tar][start_pos]['dist']

    return dist

'''
输入：
car_info 待使用的车的车辆的信息 dict()
num：需要使用的车的数量
road_info：道路信息
app_platform_info：站台信息
start_pos：车辆的起始位置
输出：
cars：最后需要的车辆信息
说明：
根据车辆距离和之前计算得出的车辆位置得出具体需要调度的车辆。
'''

def timeEmitate(dist,start_time):
    # stamp = int(time.time())
    # now_time=time.strftime("%Y-%m-%d %H:%M",time.localtime(stamp))
    now_time=time.time()
    start_time='2021-09-08 15:07:18'
    start_time = time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
    t_real=float(start_time)-float(now_time)
    t_est=dist/(30/3.6)
    return t_est<t_real

### 根据站点信息的地图进行匹配
def select_car(car_info, num, road_info, app_platform_info, start_pos,start_time):
    car_dist_info = dict()
    for car in car_info.keys():
        if 'busy' not in car_info[car].keys():
            car_info[car]['busy'] = 0
        if car_info[car]['busy']==0 and ('status' in car_info[car].keys() and car_info[car]['status']==0): # 新增这个，避免重复派车
            car_lat = car_info[car]['lat']
            car_lng = car_info[car]['lng']
            dist = compute_dist_map(road_info, app_platform_info, car_lat, car_lng, start_pos)
            # 在这里做一个判断哈，就是说当前的时间与票预期的时间进行一个比较哈
            # if(timeEmitate(dist,start_time)):
            #     car_dist_info[car] = dist
            car_dist_info[car] = dist
    print(car_dist_info)
    car_dist_info = dict(sorted(car_dist_info.items(), key = lambda x:x[1], reverse=False))
    # print(car_dist_info)
    cars = list(car_dist_info.keys())[:num]
    for car in cars:
        car_info[car]['busy']=1 # 新增这个，避免重复派车
    return cars


'''
输入：
car_info 待使用的车的车辆的信息 dict()，这是一个全局变量
ticket：订单信息
road_info：道路信息
app_platform_info：站台信息
start_pos：车辆的起始位置
输出：
cars：最后需要的车辆信息
说明：
根据订单信息得到车辆指派的结果。
'''


def get_cars(car_info, ticket, start_pos, start_time,road_info, app_platform_info, car_group_data):
    empty_car_4 = dict()
    # empty_car_6= dict()
    empty_car_14 = dict()
    empty_car_22 = dict()
    # 修改：在这里面就去掉30分钟之内无法进行派车的车辆
    for car in car_info.keys():
        if (car in car_group_data.keys()) and car_info[car]['seat'] == 4:
            empty_car_4[car] = car_info[car]
        elif (car in car_group_data.keys()) and car_info[car]['seat'] == 14:
            empty_car_14[car] = car_info[car]
        elif (car in car_group_data.keys()) and car_info[car]['seat'] == 22:
            empty_car_22[car] = car_info[car]

    passengers = int(ticket['ticketNumber'])
    car_rest_info = {4: len(empty_car_4.keys()), 14: len(empty_car_14.keys()), 22: len(empty_car_22.keys())}
    car_book_info = {4: 0, 14: 0, 22: 0}
    print(car_rest_info)

    rest_seat = 0
    for key, value in car_rest_info.items():
        rest_seat += (key-1) * value

    car_book_info = arrange_car(passengers, car_rest_info, car_book_info, rest_seat)
    print(car_book_info)
    cars = []

    if car_book_info:
        if car_book_info[4]['num'] > 0:
            cars = cars + select_car(empty_car_4, car_book_info[4]['num'], road_info, app_platform_info, start_pos,start_time)
        if car_book_info[14]['num'] > 0:
            cars = cars + select_car(empty_car_14, car_book_info[14]['num'], road_info, app_platform_info, start_pos,start_time)
        if car_book_info[22]['num'] > 0:
            cars = cars + select_car(empty_car_22, car_book_info[22]['num'], road_info, app_platform_info, start_pos,start_time)

        seat = car_book_info[4]['seat_info'] + car_book_info[14]['seat_info'] + car_book_info[22]['seat_info']
        return cars, seat
    else:
        return None, None

#
# def get_cars(car_info, ticket, start_pos, road_info, app_platform_info, car_group_data):
#     empty_car_4 = dict()
#     #empty_car_6= dict()
#     empty_car_14= dict()
#     empty_car_22 = dict()
#     # 修改：在这里面就去掉30分钟之内无法进行派车的车辆
#     for car in car_info.keys():
#         if (car in car_group_data.keys()) and car_info[car]['seat'] == 4:
#             empty_car_4[car] = car_info[car]
#         #elif car_info[car]['status'] == 0 and car_info[car]['seat'] == 6:
#             #empty_car_6[car] = car_info[car]
#         elif (car in car_group_data.keys()) and car_info[car]['seat'] == 14:
#             empty_car_14[car] = car_info[car]
#         elif (car in car_group_data.keys()) and car_info[car]['seat'] == 22:
#             empty_car_22[car] = car_info[car]
#
#     passengers = int(ticket['ticketNumber'])
#     car_rest_info = {4:len(empty_car_4.keys()), 14:len(empty_car_14.keys()), 22:len(empty_car_22.keys())}
#     car_book_info = {4:0, 14:0, 22:0}
#     print(car_rest_info)
#
#     rest_seat = 0
#     for key,value in car_rest_info.items():
#         rest_seat += key*value
#
#     car_book_info = arrange_car(passengers, car_rest_info, car_book_info, rest_seat)
#     print(car_book_info)
#     cars = []
#
#     if car_book_info:
#         if car_book_info[4]['num'] > 0:
#             cars = cars + select_car(empty_car_4, car_book_info[4]['num'], road_info, app_platform_info, start_pos)
#         if car_book_info[14]['num'] > 0:
#             cars = cars + select_car(empty_car_14, car_book_info[14]['num'], road_info, app_platform_info, start_pos)
#         if car_book_info[22]['num'] > 0:
#             cars = cars + select_car(empty_car_22, car_book_info[22]['num'], road_info, app_platform_info, start_pos)
#
#         seat = car_book_info[4]['seat_info'] + car_book_info[14]['seat_info'] + car_book_info[22]['seat_info']
#         return cars, seat
#     else:
#         return None, None

'''
输入：
car_seat：车辆的座位信息 dict() {座位号：乘客} 如果没人的话乘客为''
prefer_seat：用户希望的座位 list
u_id：用户的id信息
输出：
car_seat: 车辆座位信息，考虑了prefer_seat 以及 u_id
说明：
将特定的u_id 综合 prefer_seat 指派到车辆的座位上
'''

def arrange4(car_seat, prefer_seat, u_id):
    if prefer_seat == [1,3]:
        for pos1 in [1, 0]:
            for pos2 in ['A', 'C', 'B']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    elif prefer_seat == [1,4]:
        for pos1 in [1, 0]:
            for pos2 in ['B', 'A', 'C']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    elif prefer_seat == [2,3]:
        for pos1 in [0, 1]:
            for pos2 in ['A', 'C', 'B']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    else:
        for pos1 in [0, 1]:
            for pos2 in ['B', 'A', 'C']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    return car_seat

'''
输入：
car_seat：车辆的座位信息 dict() {座位号：乘客} 如果没人的话乘客为''
prefer_seat：用户希望的座位 list
u_id：用户的id信息
输出：
car_seat: 车辆座位信息，考虑了prefer_seat 以及 u_id
说明：
将特定的u_id 综合 prefer_seat 指派到车辆的座位上
'''

def arrange14(car_seat, prefer_seat, u_id):
    if prefer_seat == [1,3]:
        for pos1 in [4,3,2,1,0]:
            for pos2 in ['A', 'D', 'C', 'B']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    elif prefer_seat == [1,4]:
        for pos1 in [4,3,2,1,0]:
            for pos2 in ['C', 'B', 'A', 'D']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    elif prefer_seat == [2,3]:
        for pos1 in [0, 1 ,2, 3, 4]:
            for pos2 in ['A', 'D', 'C', 'B']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    else:
        for pos1 in [0, 1 ,2, 3, 4]:
            for pos2 in ['C', 'B', 'A', 'D']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    return car_seat


'''
输入：
car_seat：车辆的座位信息 dict() {座位号：乘客} 如果没人的话乘客为''
prefer_seat：用户希望的座位 list
u_id：用户的id信息
输出：
car_seat: 车辆座位信息，考虑了prefer_seat 以及 u_id
说明：
将特定的u_id 综合 prefer_seat 指派到车辆的座位上
'''

def arrange22(car_seat, prefer_seat, u_id):
    if prefer_seat == [1,3]:
        for pos1 in [7,6,5,4,3,2,1,0]:
            for pos2 in ['A', 'D', 'C', 'B']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    elif prefer_seat == [1,4]:
        for pos1 in [7,6,5,4,3,2,1,0]:
            for pos2 in ['C', 'B', 'A', 'D']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    elif prefer_seat == [2,3]:
        for pos1 in [0, 1 ,2, 3, 4,5,6,7]:
            for pos2 in ['A', 'D', 'C', 'B']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    else:
        for pos1 in [0, 1 ,2, 3, 4,5,6,7]:
            for pos2 in ['C', 'B', 'A', 'D']:
                if (pos1, pos2) in car_seat.keys() and car_seat[(pos1, pos2)] == True:
                    car_seat[(pos1, pos2)] = str(u_id)
                    return car_seat
    return car_seat

'''
输入：
ticket：订单信息 dict() 
task：任务信息
car_seat_info：每一种车的座位表dict()
car_info：车辆信息
输出：
seat_arrange: 车辆
说明：
将特定的u_id 综合 prefer_seat 指派到车辆的座位上
'''


def arrange_seat_2_seat(ticket, task, car_seat_info, car_info):
    prefer = dict()
    user_id = []
    #print(ticket)
    all_user = ticket['orderUserId']
    for u_id in all_user:
        user_id = user_id + u_id['userId'].split(',')
    for info in ticket['userPreference']:
        prefer[info['userId']] = info['seatPreference'].split(',')

    car_seat = car_seat_info[car_info[task['carId']]['seat']]
    if len(prefer) > 0:
        for u_id in prefer.keys():
            prefer_seat = prefer[u_id]
            if len(car_seat) == 4:
                car_seat = arrange4(car_seat, prefer_seat, u_id)
            elif len(car_seat) == 14:
                car_seat = arrange14(car_seat, prefer_seat, u_id)
            else:
                car_seat = arrange22(car_seat, prefer_seat, u_id)
    for u_id in user_id:
        if u_id not in prefer.keys():
            for key in car_seat.keys():
                if car_seat[key] == True:
                    car_seat[key] = str(u_id)
                    break
    car_arrange = dict()
    for key in car_seat.keys():
        if car_seat[key] != True:
            car_arrange[car_seat[key]] = key
    seat_arrange = dict()
    seat_arrange['carId'] = ticket['carId']
    #task['seat_preferences'] = car_arrange
    #tasks[task_id] = task
    temp = []
    for user in car_arrange.keys():
        temp.append({"userId":user, "seat":car_arrange[user][1]+str(car_arrange[user][0])})
    seat_info = dict()
    seat_info['orderId'] = ticket['orderUserId'][0]['orderId']
    seat_info['seatId'] = temp
    seat_arrange['correspondSeatId'] = [seat_info]

    return seat_arrange

        


