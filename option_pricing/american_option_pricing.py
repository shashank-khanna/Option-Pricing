# coding=utf-8
import datetime
import logging
from random import gauss

import numpy as np

from option_pricing.base_option_pricing import OptionPricingBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)


class AmericanOptionPricing(OptionPricingBase):
    """
    This class uses Monte-Carlo simulation to calculate prices for American Call and Put Options.

    TODO: Will create a separate class to calculate prices using Binomial Trees
    """
    SIMULATION_COUNT = 100000  # Number of Simulations to be performed for Brownian motion

    def __init__(self, ticker, expiry_date, strike, dividend=0.0):
        super(AmericanOptionPricing, self).__init__(ticker, expiry_date, strike, dividend=dividend)
        logging.info("American Option Pricing. Initializing variables")

        # Get/Calculate all the required underlying parameters, ex. Volatility, Risk-free rate, etc.
        self.initialize_variables()
        self.log_parameters()

    def _generate_asset_price(self):
        """ Calculate predicted Asset Price at the time of Option Expiry date.
        It used a random variable based on Gaus model and then calculate price using the below equation.

            St = S * exp((r− 0.5*σ^2)(T−t)+σT−t√ϵ)

        :return: <float> Expected Asset Price
        """
        expected_price = self.spot_price * np.exp(
            (self.risk_free_rate - 0.5 * self.volatility ** 2) * self.time_to_maturity +
            self.volatility * np.sqrt(self.time_to_maturity) * gauss(0.0, 1.0))
        # logging.debug("expected price %f " % expected_price)
        return expected_price

    def _call_payoff(self, expected_price):
        """ Calculate payoff of the call option at Option Expiry Date assuming the asset price
        is equal to expected price. This calculation is based on below equation:

            Payoff at T = max(0,ExpectedPrice−Strike)

        :param expected_price: <float> Expected price of the underlying asset on Expiry Date
        :return: <float> payoff
        """
        return max(0, expected_price - self.strike_price)

    def _put_payoff(self, expected_price):
        """ Calculate payoff of the put option at Option Expiry Date assuming the asset price
        is equal to expected price. This calculation is based on below equation:

            Payoff at T = max(0,Strike-ExpectedPrice)

        :param expected_price: <float> Expected price of the underlying asset on Expiry Date
        :return: <float> payoff
        """
        return max(0, self.strike_price - expected_price)

    def _generate_simulations(self):
        """ Perform Brownian motion simulation to get the Call & Put option payouts on Expiry Date

        :return: <list of call-option payoffs>, <list of put-option payoffs>
        """
        call_payoffs, put_payoffs = [], []
        for _ in xrange(self.SIMULATION_COUNT):
            expected_asset_price = self._generate_asset_price()
            call_payoffs.append(self._call_payoff(expected_asset_price))
            put_payoffs.append(self._put_payoff(expected_asset_price))
        return call_payoffs, put_payoffs

    def calculate_option_prices(self):
        """ Calculate present-value of of expected payoffs and their average becomes the price of the respective option.
        Calculations are performed based on below equations:

            Ct=PV(E[max(0,PriceAtExpiry−Strike)])

            Pt=PV(E[max(0,Strike−PriceAtExpiry)])

        :return: <float>, <float> Calculated price of Call & Put options
        """
        call_payoffs, put_payoffs = self._generate_simulations()
        discount_factor = np.exp(-1 * self.risk_free_rate * self.time_to_maturity)
        call_price = discount_factor * (sum(call_payoffs) / len(call_payoffs))
        put_price = discount_factor * (sum(put_payoffs) / len(put_payoffs))
        logging.info("### Call Price calculated at %f " % call_price)
        logging.info("### Put Price calculated at %f " % put_price)
        return call_price, put_price


if __name__ == '__main__':
    # pricer = AmericanOptionPricing('AAPL', datetime.datetime(2019, 1, 19), 190, dividend=0.0157)
    pricer = AmericanOptionPricing('TSLA', datetime.datetime(2018, 8, 31), 300)
    call, put = pricer.calculate_option_prices()
    parity = pricer.is_call_put_parity_maintained(call, put)
    print("Parity = %s" % parity)
