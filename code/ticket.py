import numpy as np 
import math
import datetime
import random
from fakedata import *
from dataformat import *
from process import *
from arrange import * 


station_id = ['1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '1010', '1011', '1012', '1101', '1102', '1103', '1104', '1105', \
    '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1115', '1116', '1201', '1202', '1203', '1204', '1205', '1206', \
    '1207', '1208', '1209', '1210', '1211', '1212', '1301', '1302', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1310', '1311']

ticket = dict()
ticket['oId'] = '000001'
ticket['fromId'] = station_id[random.randint(0,50)]
ticket['toId'] = station_id[random.randint(0,50)]
ticket['startTime'] = '{0:%Y-%m-%d-%H-%M}'.format(datetime.datetime.now())
ticket['ticketNumber'] = 13

#print(ticket)

lon_scale = [121.32345, 121.227864]
lat_scale = [31.390933, 31.286396]
car_num = 100
global car_info

car_info = fakedatamaker(car_num, lat_scale, lon_scale).makefakecarpos()

#print(car_info)

app_car_info, app_city_info, app_platform_info = dataloader('C:\\Users\\XTY\\Desktop\\交运\\基础数据同步（20210421）').load_all_info()

start_pos = [float(app_platform_info[ticket['fromId']]['longitude']), float(app_platform_info[ticket['fromId']]['latitude'])]

empty_car_4 = dict()
empty_car_14= dict()
empty_car_22 = dict()

for car in car_info.keys():
    if car_info[car]['status'] == 0 and car_info[car]['seat'] == 4:
        empty_car_4[car] = car_info[car]
    elif car_info[car]['status'] == 0 and car_info[car]['seat'] == 14:
        empty_car_14[car] = car_info[car]
    elif car_info[car]['status'] == 0 and car_info[car]['seat'] == 22:
        empty_car_22[car] = car_info[car]


#print(empty_car_5)
#print(empty_car_14)
#print(empty_car_22)
#print('============================')

passengers = ticket['ticketNumber']
car_rest_info = {4:len(empty_car_4.keys()), 14:len(empty_car_14.keys()), 22:len(empty_car_22.keys())}
car_book_info = {4:0, 14:0, 22:0}
print(car_rest_info)

rest_seat = 0
for key,value in car_rest_info.items():
    rest_seat += key*value


car_book_info = arrange_car(passengers, car_rest_info, car_book_info, rest_seat)

global cars 
cars = []

if car_book_info:
    if car_book_info[4] > 0:
        cars = cars + select_car(empty_car_4, car_book_info[4], start_pos)
    if car_book_info[14] > 0:
        cars = cars + select_car(empty_car_14, car_book_info[14], start_pos)
    if car_book_info[22] > 0:
        cars = cars + select_car(empty_car_22, car_book_info[22], start_pos)



print(car_book_info)
print(cars)
print(car_info[cars[0]])
'''
if ticket['ticketNumber'] > 22:
    continue
else:
    continue
'''



for car in car_info.keys():
    car_dist_info = dict()
    if car_info[car]['status'] == 0 and car_info[car]['seat']:
        car_lat = car_info[car]['lat']
        car_lng = car_info[car]['lng']
        dist = compute_dist(car_lng, car_lat, start_pos[0], start_pos[1])
        car_dist_info = 0

    else:
        continue

#print(car_lat, car_lng)

#print(select_car(empty_car_4, 5, start_pos))