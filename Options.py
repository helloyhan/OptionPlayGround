import math
import datetime
import numpy as np

from scipy import stats
from abc import abstractmethod


class Option:
    def __init__(self, S, K, sigma, T, r, drift):
        self.S = S
        self.K = K
        self.sigma = sigma
        self.T = T
        self.r = r
        self.drift = drift
        # Calculate delta t
        dt = np.busday_count(datetime.date.today(), T) / 252
        # Calculate d1
        self.d1 = self.get_d1(S, K, r, sigma, dt)
        # Calculate d2
        self.d2 = self.get_d2(self.d1, sigma, dt)
        self.dt = dt

    @classmethod
    def get_d1(cls, S, K, r, sigma, dt):
        return (math.log(S/K) + (r + math.pow(sigma, 2) / 2) * dt) / (sigma * math.sqrt(dt))

    @classmethod
    def get_d2(cls, d1, sigma, dt):
        return d1 - (sigma * math.sqrt(dt))

    @classmethod
    def N(cls, x):
        '''
        calculate the N(x)
        :param x: float
        :return:  float
        '''
        return stats.norm.cdf(x)

    @classmethod
    def NPrime(cls, x):
        '''
        calculate the N'(x)
        :param x: float
        :return:  float
        '''
        return stats.norm.pdf(x)

    @abstractmethod
    def price(self):
        pass

    @abstractmethod
    def delta(self):
        pass

    @abstractmethod
    def gamma(self):
        pass

    @abstractmethod
    def theta(self):
        pass

    @abstractmethod
    def vega(self):
        pass


class EuropeanCall(Option):
    '''
    A plain European call option on a non-dividend-paying stock
    '''
    def __init__(self, S, K, sigma, T, r, drift):
        Option.__init__(self, S, K, sigma, T, r, drift)

    @property
    def price(self):
        # Calculate NormalCDF for d1 & d2
        n1 = Option.N(self.d1)
        n2 = Option.N(self.d2)
        # Calculate call option price
        return self.S*n1 - self.K*(math.exp(-(self.r*self.dt)))*n2

    @property
    def delta(self):
        return Option.N(self.d1)

    @property
    def gamma(self):
        return Option.NPrime(self.d1) / (self.S * self.sigma * np.sqrt(self.dt))

    @property
    def theta(self):
        p1 = -self.S*Option.NPrime(self.d1)*self.sigma / (2*np.sqrt(self.dt))
        p2 = -self.r*self.K*np.exp(-self.r*self.dt)*Option.N(self.d2)
        return p1 + p2

    @property
    def vega(self):
        return self.S*np.sqrt(self.dt)*Option.NPrime(self.d1)

    @property
    def exercise_prob(self):
        return 1 - Option.N(((self.K - self.S) - (self.drift*self.S*self.dt))/((self.sigma*self.S)*(self.dt**.5)))


class EuropeanPut(Option):

    def __init__(self, S, K, sigma, T, r, drift):
        Option.__init__(self, S, K, sigma, T, r, drift)

    @property
    def price(self):
        # Calculate NormalCDF for d1 & d2
        n1 = Option.N(-self.d1)
        n2 = Option.N(-self.d2)
        # Calculate call option price
        return self.K*(math.exp(-(self.r*self.dt)))*n2 - self.S*n1

    @property
    def delta(self):
        return Option.N(self.d1) - 1

    @property
    def gamma(self):
        return Option.NPrime(self.d1) / (self.S * self.sigma * np.sqrt(self.dt))

    @property
    def theta(self):
        p1 = -self.S*Option.NPrime(self.d1)*self.sigma / (2*np.sqrt(self.dt))
        p2 = self.r*self.K*np.exp(-self.r*self.dt)*Option.N(-self.d2)
        return p1 + p2

    @property
    def vega(self):
        return self.S*np.sqrt(self.dt)*Option.NPrime(self.d1)

    @property
    def exercise_prob(self):
        return Option.N(((self.K - self.S) - (self.drift*self.S*self.dt))/((self.sigma*self.S)*(self.dt**.5)))

