import time
from typing import Union

from coinrat.domain.candle import CandleStorage
from coinrat.domain import MarketStateSynchronizer, Pair
from coinrat.event_emitter import EventEmitter
from .market import BittrexMarket


class BittrexSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        market: BittrexMarket,
        storage: CandleStorage,
        event_emitter: EventEmitter,
        delay: int = 30,
        number_of_runs: Union[int, None] = None
    ):
        self._market = market
        self._storage = storage
        self._event_emitter = event_emitter
        self._delay = delay
        self._number_of_runs = number_of_runs

    def synchronize(self, pair: Pair):
        self._import_historical_data(pair)

        while self._number_of_runs is None or self._number_of_runs > 0:

            candle = self._market.get_last_candle(pair)
            self._storage.write_candle(candle)
            self._event_emitter.emit_new_candles([candle])

            if self._number_of_runs is not None:  # pragma: no cover
                self._number_of_runs -= 1

            time.sleep(self._delay)

    def _import_historical_data(self, pair: Pair):
        candles = self._market.get_candles(pair)
        self._storage.write_candles(candles)
