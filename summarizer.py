import csv
import sys


class Driver:
    def __init__(self, name, model, steam_id, lap_count, lap_string):
        self.name = name
        self.model = model
        self.steam_id = steam_id
        self.lap_count = lap_count
        self.lap_times = list(map(int, lap_string.split(':')))
        self.average = sum(self.lap_times) / len(self.lap_times)
        self.driver_rating = 0.0


def main(argv):
    stints = []
    with open(argv[0], newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            stints.append(Driver(row[0], row[1], row[2], row[3], row[4]))
    rateable_drivers = get_driver_avg(stints)
    rated_drivers = rate_drivers(rateable_drivers)
    with open('driver_ratings.csv', 'a', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        for driver_key in rated_drivers:
            driver = rated_drivers.get(driver_key)
            writer.writerow(
                [driver.name, driver.model, driver.steam_id, driver.lap_count, ':'.join(map(str, driver.lap_times)),
                 driver.average, driver.driver_rating]
            )


def rate_drivers(drivers) -> dict:
    sorted_drivers = dict(sorted(drivers.items(), key=lambda item: item[1].average))
    fastest_average = sorted_drivers.get(next(iter(sorted_drivers))).average
    cutoff = fastest_average * 1.1
    rating_range = cutoff - fastest_average
    for driver_key in sorted_drivers:
        driver = sorted_drivers.get(driver_key)
        if driver.average < cutoff:
            diff_to_lead = driver.average - fastest_average
            driver.driver_rating = 100 * (1 - diff_to_lead / rating_range)
    return sorted_drivers


def get_driver_avg(stints) -> dict:
    drivers = {}
    for stint in stints:
        if stint.steam_id in drivers:
            drivers[stint.steam_id] = add_laps(drivers[stint.steam_id], stint)
        else:
            drivers[stint.steam_id] = stint
    return drivers


def add_laps(driver, stint) -> Driver:
    driver.lap_count += stint.lap_count
    driver.lap_times.extend(stint.lap_times)
    driver.lap_times.sort()
    del driver.lap_times[10:]
    driver.average = sum(driver.lap_times) / len(driver.lap_times)
    return driver


if __name__ == '__main__':
    main(sys.argv[1:])
