#coding=utf-8
#author=godpgf

from ..risk import StrategyAlpha
import numpy as np

class QuantPlot(object):

    @classmethod
    def show_quant_result(cls, title, br, ar):
        import matplotlib
        from matplotlib import gridspec
        import matplotlib.image as mpimg
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')

        ar_values = []
        br_values = []
        ai = 0
        bi = 0
        while True:
            ar_values.append(ar.values[ai])
            br_values.append(br.values[bi])
            if ar.index[ai] < br.index[bi]:
                ai += 1
            elif ar.index[ai] > br.index[bi]:
                bi += 1
            else:
                ai += 1
                bi += 1
            if ai >= len(ar.values) or bi >= len(br.values):
                break


        sa = StrategyAlpha(np.array(ar_values),np.array(br_values))

        red = "#aa4643"
        blue = "#4572a7"
        black = "#000000"

        figsize = (18, 6)
        f = plt.figure(title, figsize=figsize)
        gs = gridspec.GridSpec(10, 8)

        font_size = 12
        value_font_size = 11
        label_height, value_height = 0.8, 0.6
        label_height2, value_height2 = 0.35, 0.15

        fig_data = [
            (0.0, label_height, value_height, "Annual Returns", "{0:.3%}".format(StrategyAlpha.cal_year_returns(sa.total_ar)), red, black),
            (0.0, label_height2, value_height2, "Benchmark Annual", "{0:.3%}".format(StrategyAlpha.cal_year_returns(sa.total_br)), blue, black),

            (0.15, label_height, value_height, "Alpha", "{0:.4}".format(sa.cal_alpha()), black, black),
            (0.15, label_height2, value_height2, "Beta", "{0:.4}".format(sa.cal_beta()), black, black),
            (0.3, label_height, value_height, "Sharpe", "{0:.4}".format(sa.cal_sharpe_ratio()), black, black),
            (0.3, label_height2, value_height2, "Information Ratio", "{0:.4}".format(sa.cal_information_rate()), black, black),

            (0.45, label_height, value_height, "Volatility", "{0:.4}".format(sa.volability), black, black),
            (0.45, label_height2, value_height2, "MaxDrawdown", "{0:.3%}".format(sa.cal_max_drawdown()), black, black),
        ]

        ax = plt.subplot(gs[:3, :-1])
        ax.axis("off")
        for x, y1, y2, label, value, label_color, value_color in fig_data:
            ax.text(x, y1, label, color=label_color, fontsize=font_size)
            ax.text(x, y2, value, color=value_color, fontsize=value_font_size)

        # strategy vs benchmark
        ax = plt.subplot(gs[4:, :])

        ax.get_xaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.get_yaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.grid(b=True, which='minor', linewidth=.2)
        ax.grid(b=True, which='major', linewidth=1)

        ax.plot(br, label="benchmark", alpha=1, linewidth=2, color=blue)
        ax.plot(ar, label="strategy", alpha=1, linewidth=2, color=red)

        # manipulate
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])

        leg = plt.legend(loc="upper left")
        leg.get_frame().set_alpha(0.5)

        plt.show()