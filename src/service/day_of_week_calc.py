from datetime import datetime, timedelta
from functools import reduce
from dateutil.parser import parse

from ..repository.price_plan_repository import price_plan_repository
from .electricity_reading_service import ElectricityReadingService
from .time_converter import time_elapsed_in_hours
from ..service.account_service import AccountService


def calculate_time_elapsed(readings):
    min_time = min(map(lambda r: r.time, readings))
    max_time = max(map(lambda r: r.time, readings))
    return time_elapsed_in_hours(min_time, max_time)

class DayOfWeekCalcService:
    def __init__(self, reading_repository):
        self.electricity_reading_service = ElectricityReadingService(reading_repository)

    def get_cost_by_day(self, smart_meter_id, day, limit=None):
        readings = self.electricity_reading_service.retrieve_readings_for(smart_meter_id)
        print(readings)
        if len(readings) < 1 or "Meter Not Found" in readings:
            return ["No Readings Found"]

        # Calculate the date one week ago from today
        day = parse(day)
        prev_day = day - timedelta(days=1)
        next_day = day + timedelta(days=1)
        print(prev_day)
        print(next_day)
        print(day)
        # Filter readings to include only those from the last week
        readings_day = [reading for reading in readings
                        if (datetime.fromtimestamp(reading.time) > prev_day) and
                        (datetime.fromtimestamp(reading.time) < next_day)]
        print(readings_day)
        if len(readings_day) < 1:
            return ["No Readings Found for the day"]

        average = self.calculate_average_reading(readings_day)
        time_elapsed = calculate_time_elapsed(readings_day)
        consumed_energy = average / time_elapsed

        account_service = AccountService()
        price_plan_id = account_service.get_price_plan(smart_meter_id)

        price_plans = price_plan_repository.get()


        def cost_from_plan(price_plan):
            cost = {}
            cost[price_plan.name] = consumed_energy * price_plan.get_price(day)
            return cost

        list_of_spend = list(map(cost_from_plan, self.cheapest_plans_first(price_plans, day)))
        return list_of_spend[:limit]

    def cheapest_plans_first(self, price_plans, day):
        return list(sorted(price_plans, key=lambda plan: plan.get_price(day)))

    def calculate_average_reading(self, readings):
        sum = reduce((lambda p, c: p + c), map(lambda r: r.reading, readings), 0)
        return sum / len(readings)
