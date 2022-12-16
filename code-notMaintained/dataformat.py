import pandas as pd
import pymysql
import numpy as np


'''
读取数据的函数的函数，目前已经弃用
之后可能用新的函数，也可能不需要了
'''


class dataloader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_sql(self, sql_path):
        sql = open(sql_path, 'r', encoding = 'utf8')
        sqltxt = sql.readlines()
        sql.close()
        return sqltxt

    def process_raw_sqltxt(self, sqltxt, info_dict):
        for n, info in enumerate(sqltxt):
            #info_dict[n] = dict()
            #print(info)
            names = info.split('(')[1].split(')')[0]
            value = info.split('(')[2].split(')')[0]
            names = names.split(', ')
            value = value.split(', ')
            info_dict[value[0]] = dict()
            for key, num in zip(names, value):
                if key[0] == '`':
                    key = key[1:-1]
                if num[0] == '`' or num[0] == '\'':
                    num = num[1:-1]
                info_dict[value[0]][key] = num
        return info_dict

    def load_info(self, file_path):
        sql_path = self.file_path + '/' + file_path
        sqltxt = self.load_sql(sql_path)
        info = dict()
        info = self.process_raw_sqltxt(sqltxt, info)
        return info

    def load_all_info(self):
        app_car_info = self.load_info('ivs_app_car_info20210421.sql')
        app_city_info = self.load_info('ivs_app_city_info20210421.sql')
        app_platform_info = self.load_info('ivs_app_platform_info.sql')
        road_info = self.get_road_info(app_platform_info)
        #app_user_info = self.load_info('ivs_app_user_info20210421.sql')
        return app_car_info, app_city_info, app_platform_info, road_info


    def startwith(self, start, road_info):
        passed = [start]
        nopass = list(road_info.keys())
        nopass.remove(start)
        dis = road_info[start]
        
        while len(nopass):
            idx = nopass[0]
            for i in nopass:
                if dis[i]['dist'] < dis[idx]['dist']: idx = i
            nopass.remove(idx)
            passed.append(idx)
            
            for i in nopass:
                if dis[idx]['dist'] + road_info[idx][i]['dist'] < dis[i]['dist']:
                    dis[i]['dist'] = dis[idx]['dist'] + road_info[idx][i]['dist']
                    dis[i]['route'] = dis[idx]['route'] + [idx]
                    
        road_info[start] = dis
        return road_info


    def get_road_info(self, app_platform_info):
        stations = list(app_platform_info.keys())
        for station in stations:
            if app_platform_info[station]['c_code'] != '1003':
                del app_platform_info[station]

        road_info = dict()
        for station in app_platform_info.keys():
            next_station = app_platform_info[station]['next_p_ids'].split(',')
            if ',' in app_platform_info[station]['next_p_distances']:
                next_station_dist = app_platform_info[station]['next_p_distances'].split(',')
            else:
                next_station_dist = app_platform_info[station]['next_p_distances'].split('，')
            road_info[station] = dict()
            for station1 in app_platform_info.keys():
                if station1 == station:
                    road_info[station][station1] = dict()
                    road_info[station][station1]['dist'] = 0
                    road_info[station][station1]['route'] = []
                elif station1 not in next_station:
                    road_info[station][station1] = dict()
                    road_info[station][station1]['dist'] = np.inf
                    road_info[station][station1]['route'] = []
                else:
                    road_info[station][station1] = dict()
                    road_info[station][station1]['dist'] = float(next_station_dist[next_station.index(station1)])
                    road_info[station][station1]['route'] = [station]


        for station in road_info.keys():
            road_info = self.startwith(station, road_info)

        return road_info
        



'''
    

app_car_info, app_city_info, app_platform_info, road_info = dataloader('C:\\Users\\XTY\\Desktop\\交运\\基础数据同步（20210421）').load_all_info()
print(road_info)
lon = []
lat = []
p_id = []

for i in app_platform_info.keys():
    lon.append(float(app_platform_info[i]['longitude']))
    lat.append(float(app_platform_info[i]['latitude']))
    p_id.append(app_platform_info[i]['p_id'])

print(max(lon), min(lon))
print(max(lat), min(lat))
print(p_id)
#print(app_user_info[0])

'''

'''
sql_path = 'C:\\Users\\XTY\\Desktop\\交运\\基础数据同步（20210421）\\ivs_app_platform_info（20210415更新）.sql'
sql = open(sql_path, 'r', encoding = 'utf8')

sqltxt = sql.readlines()

sql.close()
app_platform_info = dict()
### 处理sql 文件内容初始化表格
for n, info in enumerate(sqltxt):
    app_platform_info[n] = dict()
    #print(info)
    names = info.split('(')[1].split(')')[0]
    value = info.split('(')[2].split(')')[0]
    names = names.split(', ')
    value = value.split(', ')
    for key, num in zip(names, value):
        if key[0] == '`':
            key = key[1:-1]
        if num[0] == '`' or num[0] == '\'':
            num = num[1:-1]
        app_platform_info[n][key] = num
'''
#print(app_platform_info[0])

    