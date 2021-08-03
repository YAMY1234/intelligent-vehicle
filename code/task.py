'''
将生成的订单派单信息，加入任务信息，并且按照接口的返回格式进行整理。
'''
import time
import string
import datetime
import random

def arrange_task(tasks, cars, seat, car_info, ticket, road_info, app_platform_info, begin_id, tickets, time_count):
    oId = ticket['correspondOrderId']
    #u_id = []
    #for o in oId:
        #u_id = u_id + tickets[o]['u_ids']
    flag = 0 
    for num, car in enumerate(cars):
        task = dict()
        task['travelId'] = int(100000*time.time())
        task['driverId'] = car_info[car]['driverId']
        task['driverContent'] = ''
        task['itNumber'] = int(seat[num])
        task['carId'] = car
        task['fromId'] = ticket['fromId']
        task['fromName'] = app_platform_info[ticket['fromId']]['p_name']
        task['toId'] = ticket['toId']
        task['toName'] = app_platform_info[ticket['toId']]['p_name']
        task['startTime'] = ticket['startTime']

        task['travelPlat'] = ",".join(road_info[task['fromId']][task['toId']]['route']) + "," + task['toId']
        task['correspondOrderId'] = ','.join(ticket['correspondOrderId'])
        correspondNumber = [id + ':' + str(tickets[id]['ticketNumber']) for id in ticket['correspondOrderId']]
        task['correspondNumber'] = ','.join(correspondNumber)

        task['parkId'] = 0
        task['parkName'] = 0
        task['distance'] = road_info[task['fromId']][task['toId']]['dist']
        task['expectedTime'] = task['distance']/18
        task['arriveTime'] = task['distance']/18
        task['modifyOrderId'] = ''
        task['warning'] = ''

        # 每个站预计时间
        t_arrive=[]
        aa=task['travelPlat'].split(',')
        t_change = datetime.datetime.strptime(ticket['startTime'], "%Y-%m-%d %H:%M:%S")
        for it in range(len(aa)-1):
                one=str(aa[it])
                two=str(aa[it+1])
                delta=road_info[one][two]['dist']/18               
                offset = datetime.timedelta(seconds=delta)
                t_change=t_change+offset
                t_str=datetime.datetime.strftime(t_change, '%Y-%m-%d %H:%M:%S')
                t_arrive.append(t_str)
        t_arrive=str(t_arrive)
        t_arrive=t_arrive.replace('[','').replace(']','').replace('\'','')
        task['arriveTime'] = t_arrive

        # 行程号生成代码
        # task['travelId'] = 'XC07550' + '{0:%Y%m%d%H%M}'.format(datetime.datetime.now())[2:] + "".join(random.choices(string.digits, k=4))
        # 行程号生成代码
        task['travelId'] = 'XC07550' + '{0:%Y%m%d%H%M%S}'.format(datetime.datetime.now())[2:] + "".join(
            str(time_count).zfill(3))
        #task['u_ids'] = u_id[flag: flag+task['itNumber']]
        tasks[str(task['travelId'])] = task
        flag += task['itNumber']
    
    return tasks



        # task = dict()
        # task['travelId'] = int(100000*time.time())
        # task['driverId'] = car_info[car]['driverId']
        # task['driverContent'] = ''
        # task['itNumber'] = int(seat[num])
        # task['carId'] = car
        # task['fromId'] = ticket['fromId']
        # task['fromName'] = app_platform_info[ticket['fromId']]['p_name']
        # task['toId'] = ticket['toId']
        # task['toName'] = app_platform_info[ticket['toId']]['p_name']
        # task['startTime'] = ticket['startTime']

        # task['travelPlat'] = ",".join(road_info[task['fromId']][task['toId']]['route'])
        # task['correspondOrderId'] = ','.join(ticket['correspondOrderId'])
        # correspondNumber = [id + ':' + str(tickets[id]['ticketNumber']) for id in ticket['correspondOrderId']]
        # task['correspondNumber'] = ','.join(correspondNumber)

        # task['parkId'] = 0
        # task['parkName'] = 0
        # task['distance'] = road_info[task['fromId']][task['toId']]['dist']
        # task['expectedTime'] = task['distance']/18
        # task['arriveTime'] = task['distance']/18
        # task['modifyOrderId'] = ''
        # task['warning'] = ''
        # #task['u_ids'] = u_id[flag: flag+task['itNumber']]
        # tasks[task['travelId']] = task
        # flag += task['itNumber']


'''
将新拍的任务加入整体任务
'''

def add_new_task_to_all(tasks, tasks_all):
    for key in tasks.keys():
        if key not in list(tasks_all.keys()):
            tasks_all[key] = tasks[key]


'''
将车辆编组信息加入任务
'''

def group_car(tasks):
    car_group = dict()
    for task in tasks:
        if task['fromId'] not in car_group.keys():
            car_group[task['fromId']] = [task['i_id']]
        else:
            car_group[task['fromId']].append(task['i_id'])
    return car_group