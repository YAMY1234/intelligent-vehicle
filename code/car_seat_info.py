'''
输入：
无
输出：
car_seat_info：车辆的位置信息
说明：
生成车辆的座位表。用于车辆座位的分配

'''

def make_car_seat_info():
    car_seat_info = dict()
    car_seat_info[4] = dict()
    car_seat_info[4][0,'C'] = True
    car_seat_info[4][1,'A'] = True
    car_seat_info[4][1,'B'] = True
    car_seat_info[4][1,'C'] = True
    car_seat_info[14] = dict()
    car_seat_info[14][0,'C'] = True
    car_seat_info[14][0,'D'] = True
    car_seat_info[14][1,'A'] = True
    car_seat_info[14][1,'B'] = True
    car_seat_info[14][2,'A'] = True
    car_seat_info[14][2,'B'] = True
    car_seat_info[14][2,'D'] = True
    car_seat_info[14][3,'A'] = True
    car_seat_info[14][3,'B'] = True
    car_seat_info[14][3,'D'] = True
    car_seat_info[14][4,'A'] = True
    car_seat_info[14][4,'B'] = True
    car_seat_info[14][4,'C'] = True
    car_seat_info[14][4,'D'] = True
    car_seat_info[22] = dict()
    car_seat_info[22][0,'C'] = True
    car_seat_info[22][0,'D'] = True
    car_seat_info[22][1,'A'] = True
    car_seat_info[22][1,'B'] = True
    car_seat_info[22][2,'A'] = True
    car_seat_info[22][2,'B'] = True
    car_seat_info[22][3,'A'] = True
    car_seat_info[22][3,'B'] = True
    car_seat_info[22][3,'D'] = True
    car_seat_info[22][4,'A'] = True
    car_seat_info[22][4,'B'] = True
    car_seat_info[22][4,'D'] = True
    car_seat_info[22][5,'A'] = True
    car_seat_info[22][5,'B'] = True
    car_seat_info[22][5,'D'] = True
    car_seat_info[22][6,'A'] = True
    car_seat_info[22][6,'B'] = True
    car_seat_info[22][6,'D'] = True
    car_seat_info[22][7,'A'] = True
    car_seat_info[22][7,'B'] = True
    car_seat_info[22][7,'C'] = True
    car_seat_info[22][7,'D'] = True
    return car_seat_info