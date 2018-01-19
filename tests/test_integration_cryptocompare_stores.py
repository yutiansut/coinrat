import pytest
import requests
from flexmock import flexmock
from influxdb import InfluxDBClient

from coinrat.domain import Pair
from coinrat_cryptocompare.synchronizer import CryptocompareSynchronizer
from coinrat_influx_db_storage.candle_storage import CandleInnoDbStorage


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


@pytest.mark.skip(reason="")  # Todo: unskip
def test_candle_ticks_are_stored(influx_database: InfluxDBClient):
    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_candles')
    synchronizer = CryptocompareSynchronizer(
        'bittrex',
        CandleInnoDbStorage(influx_database),
        emitter_mock,
        requests.Session(),
        delay=0,
        number_of_runs=1
    )
    synchronizer.synchronize(Pair('USD', 'BTC'))

    stored_candles = _get_all_from_influx_db(influx_database)
    assert 2 == len(stored_candles)

    # Test that same data won't be stored twice
    synchronizer.synchronize(Pair('USD', 'BTC'))
    second_sample = _get_all_from_influx_db(influx_database)
    assert stored_candles == second_sample


def _get_all_from_influx_db(influx_database: InfluxDBClient):
    return list(influx_database.query('SELECT * FROM "candles"').get_points())
