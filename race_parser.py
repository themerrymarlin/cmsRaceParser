import csv
import json

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


class Driver:
    def __init__(self, driver_index, car_data):
        self.index = driver_index
        self.model = CAR_MODEL_TYPES.get(car_data['car']["carModel"])
        self.name = car_data['car']['drivers'][driver_index]['firstName'] + ' ' + \
            car_data['car']['drivers'][driver_index]['lastName']
        self.steam_id = car_data['car']['drivers'][driver_index]['playerId']
        self.car_lap_total = car_data['timing']['lapCount']
        self.car_id = car_data['car']['carId']
        self.laps = []


def main(path):
    # get in results file
    results_file = open(
        path, "rb")
    # parse it
    results_file_stringify = results_file.read()
    results_file.close()
    results_json = json.loads(results_file_stringify, strict=False)
    leader_board_lines = results_json["sessionResult"]["leaderBoardLines"]
    laps = results_json["laps"]
    drivers = create_driver_dict(leader_board_lines)
    add_laps(drivers, laps)

    # now for each driver (who has proper lap times) we need to sort ascending and filter any with fewer than 10 laps
    drivers_to_pop = []
    for driver_key in drivers:
        driver = drivers.get(driver_key)
        if len(driver.laps) < 10:
            drivers_to_pop.append(str(driver.car_id) + ':' + str(driver.index))
        else:
            driver.laps.sort()
            del driver.laps[10:]

    # pop, lock drop (this is the actual removal)
    for popper in drivers_to_pop:
        drivers.pop(popper)

    # and then we write to a csv, I can do this later
    with open('raceSummary.csv', 'a', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        for driver_key in drivers:
            driver = drivers.get(driver_key)
            writer.writerow(
                [driver.name, driver.model, driver.steam_id, driver.car_lap_total, ':'.join(map(str, driver.laps))]
            )


def add_laps(drivers, laps):
    for lap in laps:
        if lap['isValidForBest']:
            driver = drivers[str(lap['carId']) + ':' + str(lap['driverIndex'])]
            driver.lap_times.append(lap['laptime'])


def create_driver_dict(leader_board_lines) -> dict:
    drivers = {}
    for leader_board_line in leader_board_lines:
        for i in range(0, len(leader_board_line['car']['drivers'])):
            driver = Driver(i, leader_board_line)
            drivers[str(driver.car_id) + ':' + str(driver.index)] = driver
    return drivers
