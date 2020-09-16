import csv
import json
import sys
import datetime
from collections import OrderedDict

CAR_MODEL_TYPES = {
    0: 'Porsche 911 (991) GT3 R',
    1: 'Mercedes-AMG GT3',
    2: 'Ferrari 488 GT3',
    3: 'Audi R8 LMS',
    4: 'Lamborghini Huracán GT3',
    5: 'McLaren 650S GT3',
    6: 'Nissan GT-R Nismo GT3 (2018)',
    7: 'BMW M6 GT3',
    8: 'Bentley Continental GT3 (2018)',
    9: 'Porsche 911.2 GT3 Cup',
    10: 'Nissan GT-R Nismo GT3 (2017)',
    11: 'Bentley Continental GT3 (2016)',
    12: 'Aston Martin Racing V12 Vantage GT3',
    13: 'Lamborghini Gallardo R-EX',
    14: 'Jaguar G3',
    15: 'Lexus RC F GT3',
    16: 'Lamborghini Huracan Evo (2019)',
    17: 'Honda/Acura NSX GT3',
    18: 'Lamborghini Huracán Super Trofeo (2015)',
    19: 'Audi R8 LMS Evo (2019)',
    20: 'AMR V8 Vantage (2019)',
    21: 'Honda NSX Evo (2019)',
    22: 'McLaren 720S GT3 (Special)',
    23: 'Porsche 911 II GT3 R (2019)',
    50: 'Alpine A110 GT4',
    51: 'Aston Martin Vantage GT4',
    52: 'Audi R8 LMS GT4',
    53: 'BMW M4 GT4',
    55: 'Chevrolet Camaro GT4',
    56: 'Ginetta G55 GT4',
    57: 'KTM X-Bow GT4',
    58: 'Maserati MC GT4',
    59: 'McLaren 570S GT4',
    60: 'Mercedes AMG GT4',
    61: 'Porsche 718 Cayman GT4'
}

CUP_CATEGORIES = {
    0: 'Pro',
    1: 'ProAM',
    2: 'AM',
    3: 'Silver',
    4: 'National'
}

SCORING = {
    0: 50,
    1: 45,
    2: 40,
    3: 36,
    4: 33,
    5: 30,
    6: 27,
    7: 24,
    8: 21,
    9: 19,
    10: 17,
    11: 15,
    12: 13,
    13: 11,
    14: 10,
    15: 9,
    16: 8,
    17: 7,
    18: 6,
    19: 5,
    20: 4,
    21: 3,
    22: 2
}

RACE_MULTIPLIERS = {
    'sprint': .5,
    'enduro': 1
}


class Driver:
    def __init__(self, driver_index, car_data):
        self.index = driver_index
        self.model = CAR_MODEL_TYPES.get(car_data['car']["carModel"])
        self.name = car_data['car']['drivers'][driver_index]['firstName'] + ' ' + \
            car_data['car']['drivers'][driver_index]['lastName']
        self.steam_id = car_data['car']['drivers'][driver_index]['playerId']
        self.car_lap_total = car_data['timing']['lapCount']
        self.total_time = car_data['timing']['totalTime']
        self.category = CUP_CATEGORIES.get(car_data['car']['cupCategory'])
        self.car_id = car_data['car']['carId']
        self.overall_points = 1
        self.category_points = 1


def main(args):
    race_type = args[0]
    path = args[1]
    # get in results file
    results_file = open(
        path, "rb")
    # parse it
    results_file_stringify = results_file.read()
    results_file.close()
    results_json = json.loads(results_file_stringify, strict=False)
    leader_board_lines = results_json["sessionResult"]["leaderBoardLines"]
    drivers = create_driver_dict(leader_board_lines)
    pros = []
    silvers = []
    ams = []
    sorted_driver_ids = sorted(drivers, key=lambda k: (-drivers.get(k).car_lap_total, drivers.get(k).total_time))
    for i in range(0, min(22, len(sorted_driver_ids))):
        driver = drivers.get(sorted_driver_ids[i])
        driver.overall_points = SCORING.get(i) * RACE_MULTIPLIERS.get(race_type)
        if driver.category == CUP_CATEGORIES.get(3):
            silvers.append(driver)
        elif driver.category == CUP_CATEGORIES.get(2):
            ams.append(driver)
        else:
            pros.append(driver)

    # and now loop through each class individually because that's probably just more straight forward and the same big O

    for i in range(0, min(22, len(pros))):
        pros[i].category_points = SCORING.get(i) * RACE_MULTIPLIERS.get(race_type)

    for i in range(0, min(22, len(silvers))):
        silvers[i].category_points = SCORING.get(i) * RACE_MULTIPLIERS.get(race_type)

    for i in range(0, min(22, len(ams))):
        ams[i].category_points = SCORING.get(i) * RACE_MULTIPLIERS.get(race_type)

    # now write to one giant csv with all the points
    with open('raceScoring.csv', 'a', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        writer.writerow([f'RACE: {race_type} on {datetime.date.today()}'])
        writer.writerow(['OVERALL'])
        writer.writerow(['DRIVER', 'POINTS'])
        for driver_id in sorted_driver_ids:
            writer.writerow([drivers.get(driver_id).name, drivers.get(driver_id).overall_points])
        writer.writerow([])
        writer.writerow(['PROS'])
        for driver in pros:
            writer.writerow([driver.name, driver.category_points])
        writer.writerow([])
        writer.writerow(['SILVERS'])
        for driver in silvers:
            writer.writerow([driver.name, driver.category_points])
        writer.writerow([])
        writer.writerow(['AMS'])
        for driver in ams:
            writer.writerow([driver.name, driver.category_points])


def create_driver_dict(leader_board_lines) -> dict:
    drivers = {}
    for leader_board_line in leader_board_lines:
        for i in range(0, len(leader_board_line['car']['drivers'])):
            driver = Driver(i, leader_board_line)
            drivers[str(driver.car_id) + ':' + str(driver.index)] = driver
    return drivers


if __name__ == '__main__':
    main(sys.argv[1:])
