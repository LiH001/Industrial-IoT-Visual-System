from datetime import datetime, timedelta
from random import choice, uniform
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/data", tags=["data"])


DeviceStatus = Literal["running", "stopped", "fault"]


class IndustrialDataPoint(BaseModel):
    """Industrial device data point."""

    device_id: str = Field(..., description="Device ID")
    status: DeviceStatus = Field(..., description="Device running status")
    temperature: float = Field(..., description="Temperature in Celsius")
    pressure: float = Field(..., description="Pressure in MPa")


class HistoricalDataPoint(BaseModel):
    """Historical industrial device data point."""

    timestamp: str = Field(..., description="Timestamp formatted as YYYY-MM-DD HH:mm:ss")
    device_id: str = Field(..., description="Device ID")
    temperature: float = Field(..., description="Temperature in Celsius")
    pressure: float = Field(..., description="Pressure in MPa")


def generate_mock_data(device_id: str) -> IndustrialDataPoint:
    """Generate one mock industrial data point."""
    return IndustrialDataPoint(
        device_id=device_id,
        status=choice(["running", "stopped", "fault"]),
        temperature=round(uniform(20, 100), 2),
        pressure=round(uniform(1, 5), 2),
    )


@router.get("/latest", response_model=list[IndustrialDataPoint])
async def get_latest_data() -> list[IndustrialDataPoint]:
    """Return latest mock industrial data for three devices."""
    return [
        generate_mock_data("plc_01"),
        generate_mock_data("plc_02"),
        generate_mock_data("plc_03"),
    ]


@router.get("/historical", response_model=list[HistoricalDataPoint])
async def get_historical_data(
    device_id: str | None = Query(default=None, description="Optional device ID"),
    limit: int = Query(default=50, ge=1, le=1000, description="Number of records"),
) -> list[HistoricalDataPoint]:
    """Return mock historical industrial data sorted by timestamp descending."""
    device_ids = ["plc_01", "plc_02", "plc_03"]
    now = datetime.now()

    historical_data = [
        HistoricalDataPoint(
            timestamp=(now - timedelta(minutes=index)).strftime("%Y-%m-%d %H:%M:%S"),
            device_id=device_id or choice(device_ids),
            temperature=round(uniform(20, 100), 2),
            pressure=round(uniform(1, 5), 2),
        )
        for index in range(limit)
    ]

    return sorted(historical_data, key=lambda item: item.timestamp, reverse=True)
