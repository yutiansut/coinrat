Build: [![CircleCI](https://circleci.com/gh/Achse/coinrat.svg?style=svg&circle-token=33676128239f1d0da010339bfbfb34a0d42576b0)](https://circleci.com/gh/Achse/coinrat)

> **Note**: This project was started as a Thesis project at ČVUT FIT. [Assignment of diploma thesis here](docs/cvut.md) (and used as semester work for [Python Course](http://naucse.python.cz/2017/mipyt-zima/)).

# CoinRat
Coinrat is modular auto-trading platform focused on crypto-currencies. This repository is contains platform itself
and also default plugins for basic usage and inspiration. There is also [UI-App](https://github.com/achse/coinrat_ui)
to help with running simulations and to visualize results. 

## Security warning 
> :squirrel: **DISCLAIMER**: The software is provided "as is", without warranty of any kind. For more see: [LICENSE](LICENSE)

* :bangbang: Be very cautious what you run against real Stock Market account. **Test your strategy and configuration well before real trading.**  
* :bangbang: **Protect API KEYS** make sure you **NEVER expose `.env`** file to anyone. If you run this on server, make sure it's well secured.
* :bangbang: **Never expose UI nor port for socket connection on the production server.** 
    * If you need running socket server in production, **ALWAYS** run UI-App locally and use [ssh tunnel](https://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html). 
    * Make sure that socket server is **NEVER** accessible from the internet.

## Installation
* Coinrat core-platform has dependency on **Python** :snake: (and bunch of packages), MySQL :memo: and **RabbitMQ** :rabbit:.
    * Minimum Python version : **3.6.3**!
    * Following [official instructions](https://www.rabbitmq.com/install-debian.html) to install RabbitMQ.
    * Install your preferred MySQL database (MySQL, MariaDB, Percona, ...) and create `coinrat` database and user wit write access for it. Add configuration into `.env`

* If you want to use default storage plugins (recommended), you will need **Influx DB**.
    * Install by the instructions: [here](https://portal.influxdata.com/downloads#influxdb) or [here](https://github.com/influxdata/influxdb)
    * Start: `sudo service influxdb start`
    * `curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE DATABASE coinrat"`
    * For development usage you can use `root`, but **always create separate user with limited access per database** in PRODUCTION:
        * Create user: `curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE USER coinrat WITH PASSWORD '<password>'"`
        * Grand this user with R+W access to the database: `curl -XPOST "http://localhost:8086/query" --data-urlencode 'q=GRANT ALL ON "coinrat" TO "coinrat"'`

* Create [virtual-env](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and install Python dependencies:
    * `python3.6 -m venv __venv__` (Python 3.6.3 minimum!)
    * `. __venv__/bin/activate`
    * `python -m pip install --upgrade git+https://github.com/ericsomdahl/python-bittrex.git` ([Package on Pypi](https://pypi.python.org/pypi/bittrex/0.1.4) is not up to date.) 
    * `python -m pip install -r requirements.txt`
    * `python setup.py install` (or `python setup.py develop` if you want to develop the thing)
    * `cp .env_example .env`
    * Setup your configuration in `.env`
    
## Plugins
Platform has five plugin types that are registered in `setup.py`: 
* **`coinrat_market_plugins`** - This plugin provides one or more **stock-market connections** (Bitfinex, Bittrex, ...) and platform uses those plugin to create order, check balances, ...
    * You can check available markets by: `python -m coinrat markets`
* **`coinrat_candle_storage_plugins`** - This plugin provides **storage for candles** (stock-market price data).
    * You can check available candle storages by: `python -m coinrat candle_storages`
* **`coinrat_order_storage_plugins`** - This plugin provides **storage for orders** that are created by strategies in platform.
    * You can check available order storages by: `python -m coinrat order_storages`
* **`coinrat_synchronizer_plugins`** - This plugin is responsible for **pumping stock-market data (candles) into platform**. Usually one module contains both market and synchronizer plugin (for stock-market modules). But for read only sources (eg. cryptocompare.com) can be provided solely in the module.
    * You can check available synchronizers by: `python -m coinrat synchronizers`
* **`coinrat_strategy_plugins`** - Most interesting plugins. Contains **trading strategies**. Strategy runs with one instance of candle and order storage, but can use multiple markets (for [Market Arbitrage](https://www.investopedia.com/terms/m/marketarbitrage.asp), etc...)
    * You can check available strategies by: `python -m coinrat strategies`

## Configuration for markets and strategies
Each strategy (or market) can have special configuration. You can see it by running 
`python -m coinrat market <market_name>` / `python -m coinrat strategy <strategy_name>`.

You can create JSON file with specific properties and provide it via `-c` option to `run_strategy` command.

> (Markets have configuration, but providing it into `run_strategy` command is not implemented yet. See [#18](https://github.com/Achse/coinrat/issues/18) for more info and workaround.)

## Feed data from stock markets
Fist, we need stock-market data. There are two synchronizers in default plugins:
* `python -m coinrat synchronize bittrex USD BTC`
* `python -m coinrat synchronize cryptocompare USD BTC`

This process must always be running to keep you with current stock-market data.

## Usage for simulations and visualisation in UI-App
Once we have data you can see them in the UI-App.

* Start socket server: `python -m coinrat start_server` and keep it running (You can configure the port of the socket server in `.env`)  .
* For strategy simulation started from UI-App, we need to have process that will handle them. Start one by: `python -m coinrat start_task_consumer`.
* Follow [instructions here](https://github.com/achse/coinrat_ui) to install and run the UI-App.

## Basic usage against real market
> :bangbang: **This will execute strategy against real market!** One good option for testing (if market does not provide test account) is to create separate account on the stock-market with **very** limited resources on it.

Run one of default strategies with this command: `python -m coinrat run_strategy double_crossover USD BTC bittrex --candle_storage influx_db --order_storage influx_db_orders-A` 

## Troubleshooting
* During installation I got: `OSError: mysql_config not found`
    * You need to install: `sudo apt-get install libmysqlclient-dev`

* `ERROR: For market "bittrex" no candles in storage "influx_db".` 
    * Strategy has no data for given market in given storage.
    * Make sure you have synchronizer running. 
    * Or, that you have data in the storage for given time period in case you are attempting to run simulation.
    * Or, your time interval somewhere is too small.
   
* In UI-App (1-minute view) every second candle is missing.
    * You are using `bittrex` synchronizer that uses native Bittrex API. This is known issue, see [#29](https://github.com/Achse/coinrat/issues/29) for more info and workaround.

## Additional tips & tricks
* There is visualization tool for Influx DB called [Chronograf](https://github.com/influxdata/chronograf), it can be usefull for visualizing data too.

## Development
* Run `python setup.py develop` (instead of `python setup.py install`)
* In `_scripts` there are some useful tools for development.
* For more information how to add your plugin, see [Pluggy](https://github.com/pytest-dev/pluggy) - plugin system that is used here.
