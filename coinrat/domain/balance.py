from decimal import Decimal
from typing import Dict, List


class Balance:
    """
    Amount of given Currency available on the given Market.
    """

    def __init__(self, market_name: str, currency: str, available_amount: Decimal) -> None:
        assert isinstance(available_amount, Decimal)

        self._market_name = market_name
        self._currency = currency
        self._available_amount = available_amount

    @property
    def market_name(self):
        return self._market_name

    @property
    def currency(self):
        return self._currency

    @property
    def available_amount(self) -> Decimal:
        return self._available_amount

    def __repr__(self):
        return '{0:.8f} {1}'.format(self._available_amount, self._currency)


def serialize_balance(balance: Balance) -> Dict[str, str]:
    return {
        'currency': balance.currency,
        'available_amount': str(balance.available_amount),
    }


def serialize_balances(balances: List[Balance]) -> List[Dict[str, str]]:
    return list(map(serialize_balance, balances))
