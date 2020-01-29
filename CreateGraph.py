import datetime
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta
from matplotlib.animation import FuncAnimation
from OptionPlayGround.Options import EuropeanCall, EuropeanPut


class OptionsGraph:

    def __init__(self, eo, type):
        self.index = 0
        self.S = eo.S
        self.K = eo.K
        self.sigma = eo.sigma
        self.T = eo.T
        self.r = eo.r
        self.drift = eo.drift
        self.type = type
        self.index_set = []
        self.option_prices = []
        self.asset_prices = [eo.S]
        # greeks
        self.deltas = []
        self.gammas = []
        self.thetas = []
        self.vegas = []

        # plt.style.use('dark_background')
        self.fig, self.axs = plt.subplots(6, figsize=(14, 12))
        self.axs = []
        self.axs.append(plt.subplot(221))  # for price
        self.axs.append(plt.subplot(223))  # for option price
        self.axs.append(plt.subplot(422))  # the left are for greeks
        self.axs.append(plt.subplot(424))
        self.axs.append(plt.subplot(426))
        self.axs.append(plt.subplot(428))

    def plot_res(self):
        for i in range(len(self.axs)):
            self.axs[i].cla()

        self.axs[1].plot(self.index_set, self.option_prices, label='Black-Scholes Option Price', c='b', linewidth=2)
        title = 'Strike:{s:.2f} Volatility:{v:.2f} InterestRate:{r:.2f}'.format(s=self.K, v=self.sigma, r=self.r)
        self.axs[1].set_title(title)
        self.axs[2].plot(self.index_set, self.deltas, label='Delta', color='blue', alpha=0.2, linewidth=2)
        self.axs[3].plot(self.index_set, self.gammas, label='Gamma', color='blue', alpha=0.2, linewidth=2)
        self.axs[4].plot(self.index_set, self.thetas, label='Theta', color='blue', alpha=0.2, linewidth=2)
        self.axs[5].plot(self.index_set, self.vegas, label='Vega', color='blue', alpha=0.2, linewidth=2)

        # Plot the asset price and strike price on the 3rd plot, blue if in the money red if out of the money
        if self.type == 'call':
            if self.K <= self.asset_prices[self.index]:
                self.axs[0].plot(self.index_set, self.asset_prices, label='Asset Price', color='green', linewidth=2)
                self.axs[0].axhline(y=self.K, label='Call Strike Price', c='blue')
            else:
                self.axs[0].plot(self.index_set, self.asset_prices, label='Asset Price', color='red', linewidth=2)
                self.axs[0].axhline(y=self.K, label='Call Strike Price', c='red')
        elif self.type == 'put':
            if self.K < self.asset_prices[self.index]:
                self.axs[0].plot(self.index_set, self.asset_prices, label='Asset Price', color='red', linewidth=2)
                self.axs[0].axhline(y=self.K, label='Put Strike Price', c='red')
            else:
                self.axs[0].plot(self.index_set, self.asset_prices, label='Asset Price', color='green', linewidth=2)
                self.axs[0].axhline(y=self.K, label='Put Strike Price', c='blue')

        for i in range(len(self.axs)):
            self.axs[i].legend(loc='upper left')


class StaticOptionsGraph(OptionsGraph):

    def __init__(self, eo, type):
        OptionsGraph.__init__(self, eo, type)

    def generate_sample(self):
        cnt = 0
        today = datetime.date.today()
        while today < self.T:
            dt = 1 / 252
            last_price = self.asset_prices[self.index] + np.random.normal(0, self.sigma * self.asset_prices[
                self.index] * dt ** (1 / 2))
            if self.type == 'call':
                eo = EuropeanCall(last_price, self.K, self.sigma, self.T, self.r, self.drift)
            elif self.type == 'put':
                eo = EuropeanPut(last_price, self.K, self.sigma, self.T, self.r, self.drift)
            else:
                raise ValueError(self.type + ' not implemented yet.')
            self.option_prices.append(eo.price)
            self.deltas.append(eo.delta)
            self.gammas.append(eo.gamma)
            self.thetas.append(eo.theta)
            self.vegas.append(eo.vega)
            self.index_set.append(self.index)
            # self.index_set.append((today + datetime.timedelta(days=cnt)).strftime('%Y-%m-%d'))
            cnt += 1

            self.asset_prices.append(eo.S)
            self.index += 1
            self.T = self.T - timedelta(days=1)

        self.asset_prices.pop()
        self.index -= 1
        self.plot_res()
        plt.show()


class LiveOptionsGraph(OptionsGraph):

    def __init__(self, eo, type):
        OptionsGraph.__init__(self, eo, type)
        self.ani = FuncAnimation(plt.gcf(), self.time_step, 500)
        plt.tight_layout()
        plt.show()

    def time_step(self, z):
        # Calculate dt so we can draw from a normal distribution to model the asset price
        dt = 1 / 252
        last_price = self.asset_prices[self.index] + np.random.normal(0, self.sigma * self.asset_prices[
            self.index] * dt ** (1 / 2))
        if self.type == 'call':
            eo = EuropeanCall(last_price, self.K, self.sigma, self.T, self.r, self.drift)
        elif self.type == 'put':
            eo = EuropeanPut(last_price, self.K, self.sigma, self.T, self.r, self.drift)
        else:
            raise ValueError(self.type + ' not implemented yet.')
        self.option_prices.append(eo.price)
        self.deltas.append(eo.delta)
        self.gammas.append(eo.gamma)
        self.thetas.append(eo.theta)
        self.vegas.append(eo.vega)
        self.index_set.append(self.index)

        self.plot_res()

        self.asset_prices.append(eo.S)
        self.index += 1
        # Helps display time decay
        self.T = self.T - timedelta(days=1)


if __name__ == '__main__':
    c = input('Mannual input(y/n, default n)?')
    if c == 'y':
        print('-------- Please input --------')
        Type = input('Option type(call or put):') or 'call'
        S = float(input('Current spot price:') or 9500)
        K = float(input('Strike price:') or 9500)
        sigma = float(input('Volatility(annually):') or 0.5)
        T = datetime.datetime.strptime(input('Expiration date(yyyy-mm-dd)') or '2020-03-27', '%Y-%m-%d').date()
        r = float(input('Interest rate:') or .02)
        drift = float(input('Expected drift of the underlying(default 0):') or 0.0)
    else:
        Type = 'call'
        S = 9500
        K = 9500
        sigma = 0.1
        T = datetime.date(2020, 5, 27)
        r = .02
        drift = .0

    initial_ec = EuropeanCall(S=S, K=K, sigma=sigma, T=T, r=r, drift=drift)

    if (input('Live(y/n, default n)?') or 'n') == 'y':
        lg = LiveOptionsGraph(initial_ec, Type)
    else:
        sg = StaticOptionsGraph(initial_ec, Type)
        sg.generate_sample()
