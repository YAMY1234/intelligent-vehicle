import numpy as np
import random
from process import *

'''
生成假数据的函数，目前已经弃用
之后可能用新的函数，也可能不需要了
'''

class fakedatamaker:
    def __init__(self, car_num, lat_scale, lon_scale, app_platform_info):
         self.car_num = car_num
         self.lat_scale = lat_scale
         self.lon_scale = lon_scale
         self.app_platform_info = app_platform_info

    def makefakecarpos(self):
        car_info = dict()
        SEAT = [4, 14, 22]
        stations = list(self.app_platform_info.keys())
        for car in range(self.car_num):
            station = stations[random.randint(0, len(stations)-1)]
            car_info[car] = dict()
            car_info[car]['vehicleId'] = car
            car_info[car]['plateNo'] = '沪A' + str(99999 - car)
            #car_info[car]['lat'] = self.lat_scale[1] + (self.lat_scale[0] - self.lat_scale[1]) * random.random()
            #car_info[car]['lng'] = self.lon_scale[1] + (self.lon_scale[0] - self.lon_scale[1]) * random.random()
            car_info[car]['lat'] = self.app_platform_info[station]['latitude']
            car_info[car]['lng'] = self.app_platform_info[station]['longitude']
            '''
            0 可以用
            1 被预约
            2 其它故障
            '''
            car_info[car]['seat'] = SEAT[random.randint(0,2)]
            car_info[car]['status'] = random.randint(0,2)
            if car_info[car]['status'] == 0:
                car_info[car]['startTime'] = -1
                car_info[car]['end_time'] = -1
            else:
                car_info[car]['startTime'] = -1
                car_info[car]['end_time'] = -1                
            ### 其他的信息

        return car_info
    
    def car_group_data(self):
        car_group_info = dict()
        stations = list(self.app_platform_info.keys())
        for car in range(self.car_num):
            station = stations[random.randint(0, len(stations)-1)]
            car_info = dict()
            car_info['carId'] = car
            lng = self.app_platform_info[station]['longitude']
            lat = self.app_platform_info[station]['latitude']
            car_info['car_gps'] = str(lng) + ',' + str(lat)
            car_info['marshalling_list'] = []
            car_group_info[car] = car_info
        return car_group_info
'''
        
lon_scale = [121.32345, 106.481107]
lat_scale = [31.390933, 29.583584]
car_num = 10
ans = fakedatamaker(car_num, lat_scale, lon_scale).makefakecarpos()
print(ans)
'''

def init_group_car(car_group_data):
    center = dict()
    for car in car_group_data.keys():
        car_gps = car_group_data[car]['car_gps']
        lng = float(car_gps.split(',')[0])
        lat = float(car_gps.split(',')[1])
        if car_gps not in center.keys():
            center[car_gps] = [car]
        else:
            for pos in center.keys():
                lng1 = float(car_gps.split(',')[0])
                lat1 = float(car_gps.split(',')[1])
                dist = compute_dist(lng, lat, lng1, lat1)
                if dist < 30:
                    print(dist)
                    center[pos].append(car)
                    break
    if len(center) > 0:
        for pos in center.keys():
            for car in center[pos]:
                car_group_data[car]['marshalling_list'] = center[pos]
