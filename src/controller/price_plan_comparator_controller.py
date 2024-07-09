from http import HTTPStatus
from typing import Dict, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Query

from ..service.account_service import AccountService
from ..service.last_week_usage import LastWeekUsageService
from ..service.day_of_week_calc import DayOfWeekCalcService
from ..service.price_plan_service import PricePlanService
from .electricity_reading_controller import repository as readings_repository
from .models import OPENAPI_EXAMPLES, PricePlanComparisons

router = APIRouter(
    prefix="/price-plans",
    tags=["Price Plan Comparator Controller"],
)


@router.get(
    "/compare-all/{smart_meter_id}",
    response_model=PricePlanComparisons,
    description="Compare prices for all plans for a given meter",
)
def compare(smart_meter_id: str = Path(openapi_examples=OPENAPI_EXAMPLES)):
    price_plan_service = PricePlanService(readings_repository)
    account_service = AccountService()
    list_of_spend_against_price_plans = price_plan_service.get_list_of_spend_against_each_price_plan_for(smart_meter_id)

    if len(list_of_spend_against_price_plans) < 1:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    else:
        return {
            "pricePlanId": account_service.get_price_plan(smart_meter_id),
            "pricePlanComparisons": list_of_spend_against_price_plans,
        }


@router.get(
    "/recommend/{smart_meter_id}",
    response_model=List[Dict],
    description="View recommended price plans for usage",
)
def recommend(
    smart_meter_id: str = Path(openapi_examples=OPENAPI_EXAMPLES),
    limit: int = Query(description="Number of items to return", default=None),
):
    price_plan_service = PricePlanService(readings_repository)
    list_of_spend_against_price_plans = price_plan_service.get_list_of_spend_against_each_price_plan_for(
        smart_meter_id, limit=limit
    )
    return list_of_spend_against_price_plans

@router.get(
    "/last-week-usage/{smart_meter_id}",
)
def calculate(smart_meter_id: str = Path(openapi_examples=OPENAPI_EXAMPLES)):
    last_week_usage_service = LastWeekUsageService(readings_repository)
    account_service = AccountService()
    last_week_spend = last_week_usage_service.get_cost_last_week_usage(smart_meter_id)

    if len(last_week_spend) < 1 or "No Readings Found" in last_week_spend or "No Readings Found for last week" in last_week_spend:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    else:
        return {
            "pricePlanId": account_service.get_price_plan(smart_meter_id),
            "lastWeekSpend": last_week_spend,
        }

@router.get(
    "/day-of-week/{smart_meter_id}/{day}",
)
def calculate_dayofweek(smart_meter_id: str = Path(openapi_examples=OPENAPI_EXAMPLES), day: str = datetime.now().strftime("%A")):
    day_of_week_calc_service = DayOfWeekCalcService(readings_repository)
    account_service = AccountService()
    day_spend = day_of_week_calc_service.get_cost_by_day(smart_meter_id, day)

    if len(day_spend) < 1 or "No Readings Found" in day_spend or "No Readings Found for the day" in day_spend:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    else:
        return {
            "pricePlanId": account_service.get_price_plan(smart_meter_id),
            "lastWeekSpend": day_spend,
        }
