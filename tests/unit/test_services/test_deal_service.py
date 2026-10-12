"""Test deal service business rules"""

from decimal import Decimal

import pytest

from app.core.exceptions import ValidationException
from app.models.deal import DealStage
from app.services.deal import DealService


@pytest.mark.unit
class TestDealService:
    """Test deal service business rules"""

    def test_stage_order_qualification_first(self):
        """Test that qualification is first stage"""
        assert DealService.STAGE_ORDER[DealStage.QUALIFICATION] == 0

    def test_stage_order_closed_last(self):
        """Test that closed is last stage"""
        assert DealService.STAGE_ORDER[DealStage.CLOSED] == 3

    def test_stage_order_progression(self):
        """Test that stages are in correct order"""
        assert DealService.STAGE_ORDER[DealStage.QUALIFICATION] < \
               DealService.STAGE_ORDER[DealStage.PROPOSAL]
        assert DealService.STAGE_ORDER[DealStage.PROPOSAL] < \
               DealService.STAGE_ORDER[DealStage.NEGOTIATION]
        assert DealService.STAGE_ORDER[DealStage.NEGOTIATION] < \
               DealService.STAGE_ORDER[DealStage.CLOSED]

