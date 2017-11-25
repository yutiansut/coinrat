import datetime
from typing import List, Union, Tuple

import pytest
from flexmock import flexmock, Mock

from coinrat.domain import MarketPair, Market, StrategyConfigurationException
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy

BTC_USD_PAIR = MarketPair('USD', 'BTC')


@pytest.mark.parametrize(['error', 'markets'],
    [
        (True, []),
        (False, [flexmock()]),
        (True, [flexmock(), flexmock()]),
    ]
)
def test_number_of_markets_validation(error: bool, markets: List[Union[Market, Mock]]):
    if len(markets) == 1:  # Todo: Flexmock is not working properly with @pytest.mark.parametrize (MethodSignatureError)
        markets = [markets[0].should_receive('get_name').and_return('dummy_market_name').mock()]

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        flexmock().should_receive('mean').and_return(0).mock(),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=15),
        0,
        1
    )
    if error:
        with pytest.raises(StrategyConfigurationException):
            strategy.run(markets)
    else:
        strategy.run(markets)


@pytest.mark.parametrize(['expected_buy', 'expected_sell', 'mean_evolution'],
    [
        (0, 0, [(8000, 7800), (8000, 7900)]),  # Short average rise, but is still beneath long average
        (0, 0, [(8000, 7800), (8000, 7800)]),  # Short average lowers beneath long average
        (0, 0, [(8000, 8200), (8000, 8100)]),  # Short average lowers, but still uppers long average
        (0, 0, [(8000, 8100), (8000, 8200)]),  # Short average rise, uppers long

        (1, 0, [(8000, 7900), (8000, 8100)]),  # Short average rise, crossing long average
        (0, 1, [(8000, 8100), (8000, 7900)]),  # Short average lowers, crossing long average

        (0, 0, [(8000, 8000), (8000, 8000)]),  # Limit situations
        (0, 0, [(8000, 8000), (8000, 8001)]),  #
        (0, 0, [(8000, 8001), (8000, 8000)]),  #

        (0, 0, [(8000, 7999), (8000, 8000), (8000, 7999)]),  # just touching the crossing
        (0, 0, [(8000, 8001), (8000, 8000), (8000, 8001)]),  # just touching the crossing

        (1, 0, [(8000, 7999), (8000, 8000), (8000, 8001)]),  # very smooth crossing in more steps
        (0, 1, [(8000, 8001), (8000, 8000), (8000, 7999)]),  # very smooth crossing in more steps
    ]
)
def test_sending_signal(expected_buy: int, expected_sell: int, mean_evolution: List[Tuple[int, int]]):
    storage = flexmock()
    expectation = storage.should_receive('mean')
    for mean in mean_evolution:
        expectation.and_return(mean[0]).and_return(mean[1])

    market = flexmock()
    market.should_receive('get_name').and_return('dummy_market_name').mock()
    market.should_receive('buy_max_available').times(expected_buy)
    market.should_receive('sell_max_available').times(expected_sell)

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        storage,
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=15),
        0,
        len(mean_evolution)
    )
    strategy.run([market])