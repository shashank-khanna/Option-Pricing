# coding=utf-8
import datetime
import logging

import numpy as np
import scipy.stats as stats

from option_pricing.base_option_pricing import OptionPricingBase

logging.basicConfig(format='%(level_name)s: %(message)s', level=logging.DEBUG)


class EuropeanOptionPricing(OptionPricingBase):
    """
    This class uses the classic Black-Scholes method to calculate prices for European Call and Put options

    I have made an attempt to include dividends in the calcultion of these options. However, still need to perform
    some testing.
    """

    def __init__(self, ticker, expiry_date, strike, dividend=0.0):
        super(EuropeanOptionPricing, self).__init__(ticker, expiry_date, strike, dividend=dividend)
        logging.info("European Option Pricing. Initializing variables")

        # Get/Calculate all the required underlying parameters, ex. Volatility, Risk-free rate, etc.
        self.initialize_variables()
        self.log_parameters()

    def _calculate_d1(self):
        """ Famous d1 variable from Black-Scholes model calculated as shown in:

                https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model
        :return: <float>
        """
        d1 = (np.log(self.spot_price / self.strike_price) +
              (self.risk_free_rate - self.dividend + 0.5 * self.volatility ** 2) * self.time_to_maturity) / \
             (self.volatility * np.sqrt(self.time_to_maturity))
        logging.debug("Calculated value for d1 = %f" % d1)
        return d1

    def _calculate_d2(self):
        """ Famous d2 variable from Black-Scholes model calculated as shown in:

                https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model
        :return: <float>
        """
        d2 = (np.log(self.spot_price / self.strike_price) +
              (self.risk_free_rate - self.dividend - 0.5 * self.volatility ** 2) * self.time_to_maturity) / \
             (self.volatility * np.sqrt(self.time_to_maturity))
        logging.debug("Calculated value for d2 = %f" % d2)
        return d2

    def calculate_option_prices(self):
        """ Calculate Call and Put option prices based on the below equations from Black-Scholes.
        If dividend is not zero, then it is subtracted from the risk free rate in the below calculations.

            CallOptionPrice =SpotPrice*N(d1) − Strike*exp(−r(T−t))*N(d2))
            PutOptionPrice  = Strike*exp(−r(T−t)) *N(−d2) − SpotPrice*N(−d1)
        :return: <float>, <float> Calculated price of Call & Put options
        """
        d1 = self._calculate_d1()
        d2 = self._calculate_d2()
        call = ((self.spot_price * np.exp(-1 * self.dividend * self.time_to_maturity)) * stats.norm.cdf(d1, 0.0, 1.0) -
                (self.strike_price * np.exp(-1 * self.risk_free_rate * self.time_to_maturity) *
                 stats.norm.cdf(d2, 0.0, 1.0)))
        logging.info("##### Calculated value for European Call Option is %f " % call)
        put = (self.strike_price * np.exp(-1 * self.risk_free_rate * self.time_to_maturity) *
               stats.norm.cdf(-1 * d2, 0.0, 1.0) - (
                       self.spot_price * np.exp(-1 * self.dividend * self.time_to_maturity)) *
               stats.norm.cdf(-1 * d1, 0.0, 1.0))
        logging.info("##### Calculated value for European Put Option is %f " % put)
        return call, put


if __name__ == '__main__':
    # pricer = EuropeanOptionPricing('AAPL', datetime.datetime(2020, 6, 19), 190, dividend=0.0157)
    pricer = EuropeanOptionPricing('TSLA', datetime.datetime(2018, 8, 31), 300)
    call_price, put_price = pricer.calculate_option_prices()
    parity = pricer.is_call_put_parity_maintained(call_price, put_price)
    print("Parity = %s" % parity)
