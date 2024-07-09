from datetime import datetime, timedelta
from functools import reduce

from ..repository.price_plan_repository import price_plan_repository
from .electricity_reading_service import ElectricityReadingService
from .time_converter import time_elapsed_in_hours
from ..service.account_service import AccountService


def calculate_time_elapsed(readings):
    min_time = min(map(lambda r: r.time, readings))
    max_time = max(map(lambda r: r.time, readings))
    return time_elapsed_in_hours(min_time, max_time)

class LastWeekUsageService:
    def __init__(self, reading_repository):
        self.electricity_reading_service = ElectricityReadingService(reading_repository)

    def get_cost_last_week_usage(self, smart_meter_id, limit=None):
        readings = self.electricity_reading_service.retrieve_readings_for(smart_meter_id)
        if len(readings) < 1 or "Meter Not Found" in readings:
            return ["No Readings Found"]

        # Calculate the date one week ago from today
        one_week_ago = datetime.now() - timedelta(weeks=1)

        # Filter readings to include only those from the last week
        readings_last_week = [reading for reading in readings if datetime.fromtimestamp(reading.time) > one_week_ago]

        if len(readings_last_week) < 1:
            return ["No Readings Found for last week"]

        average = self.calculate_average_reading(readings_last_week)
        time_elapsed = calculate_time_elapsed(readings_last_week)
        consumed_energy = average / time_elapsed

        account_service = AccountService()
        price_plan_id = account_service.get_price_plan(smart_meter_id)

        price_plans_all = price_plan_repository.get()
        price_plans = [pricePlan for pricePlan in price_plans_all if pricePlan.name==price_plan_id]

        def cost_from_plan(price_plan):
            cost = {}
            cost[price_plan.name] = consumed_energy * price_plan.unit_rate
            return cost

        list_of_spend = list(map(cost_from_plan, self.cheapest_plans_first(price_plans)))
        return list_of_spend[:limit]

    def cheapest_plans_first(self, price_plans):
        return list(sorted(price_plans, key=lambda plan: plan.unit_rate))

    def calculate_average_reading(self, readings):
        sum = reduce((lambda p, c: p + c), map(lambda r: r.reading, readings), 0)
        return sum / len(readings)
