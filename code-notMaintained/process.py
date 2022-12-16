import numpy as np 
import pandas as pd
import math

def compute_dist(long1, lat1, long2, lat2):
    R = 6371393.0
    lat1 = lat1 * math.pi / 180.0
    lat2 = lat2 * math.pi / 180.0
    a = lat1 - lat2
    b = (long1 - long2) * math.pi / 180.0
    sa2 = math.sin(a / 2.0)
    sb2 = math.sin(b / 2.0)
    return 2 * R * math.asin( math.sqrt(sa2 * sa2 + math.cos(lat1) * math.cos(lat2) * sb2 * sb2))


def car_arrange(num_people):
    return None

#print(compute_dist(113.9248001575, 22.5323483070,113.9152836800,22.5322492086))

def car_info_update(cars, car_info):
    if cars != None:
        for car in cars:
            car_info[car]['status'] = 1

    return car_info

def generate(ticket):
    return None

'''
输入：
tickets 原始收到的订单信息
输出：
new_tickets：按照起点和终点的信息归并得到的订单
说明：
将原始订单按照起点和终点信息进行合并以便于之后派车

'''
def merge_to_newtickets(tickets):
    new_tickets = dict()
    odpair = []
    for i in tickets.keys():
        if (tickets[i]['fromId'], tickets[i]['toId']) not in odpair:
            odpair.append((tickets[i]['fromId'], tickets[i]['toId']))
    ticket_group = pd.DataFrame(tickets).transpose().groupby(['fromId', 'toId'])
    for pair in odpair:
        group_temp = ticket_group.get_group(pair)
        #print(group_temp)
        new_ticket = dict()
        new_ticket['fromId'] = pair[0]
        new_ticket['toId'] = pair[1]
        new_ticket['correspondOrderId'] = list(group_temp['oId'])
        new_ticket['ticketNumber'] = group_temp['ticketNumber'].sum()
        new_ticket['startTime'] = list(group_temp['startTime'])[0]
        new_tickets[pair] = new_ticket
    return new_tickets
