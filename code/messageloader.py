import numpy as np



'''
根据站点信息生成路径图，每个站点到其他站点的路径和距离。
格式：dict()
road_info[station1][station2]['dist'] = 距离
road_info[station1][station2]['route'] = [经过的站点]
'''


class messageloader:
    def __init__(self, result):
        self.result = result


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
                    dis[i]['route']=dis[idx]['route'] + road_info[idx][i]['route']

        road_info[start] = dis
        return road_info



    def get_road_info(self, app_platform_info):
        stations = list(app_platform_info.keys())


        road_info = dict()
        for station in app_platform_info.keys():
            if  ',' in app_platform_info[station]['next_p_ids']:
                next_station = app_platform_info[station]['next_p_ids'].split(',')
            else:
                next_station = [app_platform_info[station]['next_p_ids']]
                print(next_station)
            if ',' in app_platform_info[station]['next_p_distances']:
                next_station_dist = app_platform_info[station]['next_p_distances'].split(',')
            else:
                next_station_dist = [app_platform_info[station]['next_p_distances']]
            road_info[station] = dict()
            for station1 in app_platform_info.keys():
                print(station, station1, next_station)
                if station1 == station:
                    road_info[station][station1] = dict()
                    road_info[station][station1]['dist'] = 0
                    road_info[station][station1]['route'] = []
                elif station1 not in next_station:
                    road_info[station][station1] = dict()
                    road_info[station][station1]['dist'] = np.inf
                    road_info[station][station1]['route'] = []
                else:
                    print('===')
                    road_info[station][station1] = dict()
                    road_info[station][station1]['dist'] = float(next_station_dist[next_station.index(station1)])
                    road_info[station][station1]['route'] = [station]


        for station in road_info.keys():
            road_info = self.startwith(station, road_info)

        return road_info
       

    def road_info_maker(self):
        app_platform_info = dict()
        for station_info in self.result:
            print(station_info)
            station_info['stationId'] = str(station_info['stationId'])
            app_platform_info[station_info['stationId']] = dict()
            app_platform_info[station_info['stationId']]['p_id'] = station_info['stationId']
            app_platform_info[station_info['stationId']]['c_code'] = station_info['cityCod']
            app_platform_info[station_info['stationId']]['p_name'] = station_info['stationName']
            app_platform_info[station_info['stationId']]['p_type'] = station_info['stationType']
            app_platform_info[station_info['stationId']]['p_route_type'] = station_info['stationRouteType']
            app_platform_info[station_info['stationId']]['longitude'] = station_info['staGps'].split(',')[0]
            app_platform_info[station_info['stationId']]['latitude'] = station_info['staGps'].split(',')[1]
            app_platform_info[station_info['stationId']]['next_p_ids'] = station_info['nextStaIds']
            app_platform_info[station_info['stationId']]['next_p_distances'] = station_info['nextStaDistances']
        print(app_platform_info)
        road_info = self.get_road_info(app_platform_info)
        return road_info,app_platform_info

def road_info_update(road_info1, app_platform_info1):
    global road_info
    road_info = road_info1
    global app_platform_info
    app_platform_info = app_platform_info1