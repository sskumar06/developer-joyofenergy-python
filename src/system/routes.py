from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/")
def root():
    return {"message": "Welcome to the JoyEnergy "}


@router.get("/health")
def health():
    return True


# add a function to calculate price plan cost using src/service/price_plan_service.py

