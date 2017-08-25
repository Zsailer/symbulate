"""Data structures for storing the results of a simulation.

This module provides data structures for storing the
results of a simulation, either outcomes from a
probability space or realizations of a random variable /
random process.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from numbers import Number

from .sequences import TimeFunction
from .table import Table
from .utils import is_scalar, is_vector, get_dimension
from .plot import configure_axes, get_next_color
from statsmodels.graphics.mosaicplot import mosaic
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import NullFormatter

plt.style.use('ggplot')

def is_hashable(x):
    return x.__hash__ is not None

def count_var(x):
    counts = {}
    for val in x:
        if val in counts:
            counts[val] += 1
        else:
            counts[val] = 1
    return counts

class Results(list):

    def __init__(self, results):
        for result in results:
            self.append(result)

    def apply(self, fun):
        """Apply a function to each outcome of a simulation.

        Args:
          fun: A function to apply to each outcome.

        Returns:
          Results: A Results object of the same length,
            where each outcome is the result of applying
            the function to each outcome from the original
            Results object.
        """
        return type(self)(fun(x) for x in self)

    def __getitem__(self, i):
        return self.apply(lambda x: x[i])

    def get(self, i):
        for j, x in enumerate(self):
            if j == i:
                return x

    def _get_counts(self):
        counts = {}
        for x in self:
            if is_hashable(x):
                y = x
            elif isinstance(x, list) and all(is_hashable(i) for i in x):
                y = tuple(x)
            else:
                y = str(x)
            if y in counts:
                counts[y] += 1
            else:
                counts[y] = 1
        return counts

    def tabulate(self, outcomes=None, normalize=False):
        """Counts up how much of each outcome there were.

        Args:
          outcomes (list): A list of outcomes to tabulate.
            By default, will tabulate all outcomes that
            appear in the Results.  Use this option if
            you want to include outcomes that could
            potentially not appear in the Results.
          normalize (bool): If True, return the relative
            frequency. Otherwise, return the counts.
            Defaults to False.

        Returns:
          Table: A Table with each of the observed
            outcomes and their freuencies.
        """
        table = Table(self._get_counts(), outcomes)
        if normalize:
            return table / len(self)
        else:
            return table


    # The following functions return a Results object
    # with the outcomes that satisfy a given criterion.

    def filter(self, fun):
        """Filters the results of a simulation and
             returns only those outcomes that satisfy
             a given criterion.

        Args:
          fun (outcome -> bool): A function that
            takes in an outcome and returns a
            True / False. Only the outcomes that
            return True will be kept; the others
            will be filtered out.

        Returns:
          Results: Another Results object containing
            only those outcomes for which the function
            returned True.
        """
        return type(self)(x for x in self if fun(x))

    def filter_eq(self, value):
        return self.filter(lambda x: x == value)

    def filter_neq(self, value):
        return self.filter(lambda x: x != value)

    def filter_lt(self, value):
        return self.filter(lambda x: x < value)

    def filter_leq(self, value):
        return self.filter(lambda x: x <= value)

    def filter_gt(self, value):
        return self.filter(lambda x: x > value)

    def filter_geq(self, value):
        return self.filter(lambda x: x >= value)


    # The following functions return an integer indicating
    # how many outcomes passed a given criterion.

    def count(self, fun=lambda x: True):
        """Counts the number of outcomes that satisfied
             a given criterion.

        Args:
          fun (outcome -> bool): A function that
            takes in an outcome and returns a
            True / False. Only the outcomes that
            return True will be counted.

        Returns:
          int: The number of outcomes for which
            the function returned True.
        """
        return len(self.filter(fun))

    def count_eq(self, value):
        return len(self.filter_eq(value))

    def count_neq(self, value):
        return len(self.filter_neq(value))

    def count_lt(self, value):
        return len(self.filter_lt(value))

    def count_leq(self, value):
        return len(self.filter_leq(value))

    def count_gt(self, value):
        return len(self.filter_gt(value))

    def count_geq(self, value):
        return len(self.filter_geq(value))


    # The following functions define vectorized operations
    # on the Results object.

    def __eq__(self, other):
        return self.apply(lambda x: x == other)

    def __ne__(self, other):
        return self.apply(lambda x: x != other)

    def __lt__(self, other):
        return self.apply(lambda x: x < other)

    def __le__(self, other):
        return self.apply(lambda x: x <= other)

    def __gt__(self, other):
        return self.apply(lambda x: x > other)

    def __ge__(self, other):
        return self.apply(lambda x: x >= other)


    def plot(self):
        raise Exception("Only simulations of random variables (RV) "
                        "can be plotted, but you simulated from a " 
                        "probability space. You must first define a RV "
                        "on your probability space and simulate it. "
                        "Then call .plot() on those simulations.")
 
    def mean(self):
        raise Exception("You can only call .mean() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        "a RV on your probability space and simulate it "
                        "Then call .mean() on those simulations.")

    def var(self):
        raise Exception("You can only call .var() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .var() on those simulations.")

    def sd(self):
        raise Exception("You can only call .sd() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .sd() on those simulations.")

    def corr(self):
        raise Exception("You can only call .corr() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .corr() on those simulations.")
   
    def cov(self):
        raise Exception("You can only call .cov() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .cov() on those simulations.")


    def _repr_html_(self):

        table_template = '''
    <table>
      <thead>
        <th width="10%">Index</th>
        <th width="90%">Result</th>
      </thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
    '''
        row_template = '''
        <tr>
          <td>%s</td><td>%s</td>
        </tr>
        '''

        def truncate(result):
            if len(result) > 100:
                return result[:100] + "..."
            else:
                return result

        table_body = ""
        for i, x in enumerate(self):
            table_body += row_template % (i, truncate(str(x)))
            # if we've already printed 9 rows, skip to end
            if i >= 8:
                table_body += "<tr><td>...</td><td>...</td></tr>"
                i_last = len(self) - 1
                table_body += row_template % (i_last, truncate(str(self.get(i_last))))
                break
        return table_template.format(table_body=table_body)


class RVResults(Results):

    def plot(self, type=None, alpha=None, normalize=True, jitter=False, 
        bins=30, **kwargs):
        if type is None:
            pass
        elif isinstance(type, str):
            type = (type,)
        elif not isinstance(type, (tuple, list)):
            raise Exception("I don't know how to plot a " + str(type))
            
        
        dim = get_dimension(self)
        if dim == 1:
            counts = self._get_counts()
            if type is None:
                heights = counts.values()
                if sum([(i > 1) for i in heights]) > .8 * len(heights):
                    type = ("impulse",)
                else:
                    type = ("hist",)
            if alpha is None:
                alpha = .5
            if all(x in ("hist",) for x in type):
                df = pd.DataFrame({'X':self})
                ax = df['X'].plot(kind='hist', normed=normalize, alpha=alpha, bins=bins)
                ax.set_ylabel('')
            elif all(x in ("density",) for x in type):
                df = pd.DataFrame({'X':self})
                ax = df['X'].plot(kind='density', alpha=alpha)
                ax.set_ylabel('')
            elif all(x in ("rug",) for x in type):
                fig, ax = plt.subplots()
                ax.plot(list(self), [0.001]*len(self), '|', color='k')
            elif all(x in ("hist", "density") for x in type):
                df = pd.DataFrame({'X':self})
                ax = df['X'].plot(kind='hist', normed=normalize, alpha=alpha, bins=bins)
                df['X'].plot(kind='kde', ax=ax)
                ax.set_ylabel('')
            elif all(x in ("hist", "rug") for x in type):
                fig, ax = plt.subplots()
                ax.hist(self, normed=normalize, alpha=alpha, bins=bins, **kwargs)
                ax.plot(list(self), [0.001]*len(self), '|', color='k')
            elif all(x in ("impulse",) for x in type):
                x = list(counts.keys())
                y = list(counts.values())
                if alpha is None:
                    alpha = .7
                if normalize:
                    y_tot = sum(y)
                    y = [i / y_tot for i in y]
                if jitter:
                    a = .02 * (max(x) - min(x))
                    noise = np.random.uniform(low=-a, high=a)
                    x = [i + noise for i in x]
                # get next color in cycle
                axes = plt.gca()
                color = get_next_color(axes)
                # plot the impulses
                plt.vlines(x, 0, y, color=color, alpha=alpha, **kwargs)
                
                configure_axes(axes, x, y, ylabel = "Relative Frequency" if normalize else "Count")
            else:
                raise Exception("Histogram must have type='impulse' or 'bar'.")
        elif dim == 2:
            x, y = zip(*self)

            x_count = count_var(x)
            y_count = count_var(y)
            x_height = x_count.values()
            y_height = y_count.values()
            
            discrete_x = sum([(i > 1) for i in x_height]) > .8 * len(x_height)
            discrete_y = sum([(i > 1) for i in y_height]) > .8 * len(y_height)

            discrete_both = discrete_x and discrete_y
            continuous_both = not discrete_x and not discrete_y

            if type is None:
                type = ("scatter",)

            if alpha is None:
                alpha = .5

            if all(x in ("scatter") for x in type):
                if jitter:
                    x += np.random.normal(loc=0, scale=.01 * (max(x) - min(x)), size=len(x))
                    y += np.random.normal(loc=0, scale=.01 * (max(y) - min(y)), size=len(y))
                nullfmt = NullFormatter() #removes labels on fig
                fig, ax = plt.subplots(1, 1)
                ax.scatter(x, y, alpha=alpha, c='b')
            elif all(x in ("scatter", "marginal") for x in type):
                if jitter:
                    x += np.random.normal(loc=0, scale=.01 * (max(x) - min(x)), size=len(x))
                    y += np.random.normal(loc=0, scale=.01 * (max(y) - min(y)), size=len(y))
                nullfmt = NullFormatter() #removes labels on fig
                fig = plt.figure()
                gs = GridSpec(4, 4)
                ax_joint = fig.add_subplot(gs[1:4, 0:3])
                ax_marg_x = fig.add_subplot(gs[0, 0:3])
                ax_marg_y = fig.add_subplot(gs[1:4, 3])
                ax_joint.scatter(x, y, alpha=alpha)
                ax_marg_x.hist(x)
                ax_marg_y.hist(y, orientation='horizontal')
                plt.setp(ax_marg_x.get_xticklabels(), visible=False)
                plt.setp(ax_marg_y.get_yticklabels(), visible=False)
            elif all(x in ("hist2d", ) for x in type) and continuous_both:
                nullfmt = NullFormatter() #removes labels on fig
                fig, ax = plt.subplots(1, 1)
                ax.hist2d(x, y, bins=bins, cmap='Blues')
            elif all(x in ("hist2d", "marginal") for x in type) and continuous_both:
                nullfmt = NullFormatter() #removes labels on fig
                fig = plt.figure()
                gs = GridSpec(4, 4)
                ax_joint = fig.add_subplot(gs[1:4, 0:3])
                ax_marg_x = fig.add_subplot(gs[0, 0:3])
                ax_marg_y = fig.add_subplot(gs[1:4, 3])
                ax_joint.hist2d(x, y, bins=bins, cmap='Blues')
                ax_marg_x.hist(x, color='b')
                ax_marg_y.hist(y, color='b', orientation='horizontal')
                plt.setp(ax_marg_x.get_xticklabels(), visible=False)
                plt.setp(ax_marg_y.get_yticklabels(), visible=False)
            elif all(x in ("tile", ) for x in type) and discrete_both:
                res = pd.DataFrame({'X': x, 'Y': y})
                res['num'] = 1
                res_pivot = pd.pivot_table(res, values='num', index=['Y'],
                    columns=['X'], aggfunc=np.sum)
                res_pivot = res_pivot / len(x)
                res_pivot[np.isnan(res_pivot)] = 0
                fig, ax = plt.subplots(1, 1)
                hm = plt.pcolor(res_pivot, cmap=plt.cm.Blues)
                cbar = plt.colorbar(mappable=hm, ax=ax)
            elif all(x in ("mosaic", ) for x in type) and discrete_both:
                res = pd.DataFrame({'X': x, 'Y': y})
                ct = pd.crosstab(res['Y'], res['X'])
                ctplus = ct + 1e-8
                labels = lambda k: ""
                fig, ax = plt.subplots(1, 1)
                mosaic(ctplus.unstack(), ax=ax, labelizer=labels, axes_label=False)
            elif discrete_x and discrete_y:
                raise Exception("Must have type='mosaic', 'tile', or 'scatter' if discrete.")
            elif all(x in ("violin", ) for x in type) and discrete_x and not discrete_y:
                fig, ax = plt.subplots(1, 1)
                res = pd.DataFrame({'X': x, 'Y': y})
                values = []
                positions = sorted(list(x_count.keys()))
                for i in positions:
                    values.append(list(res[res.X == i]['Y']))
                violins = ax.violinplot(dataset=values, showmedians=True)
                for part in violins['bodies']:
                    part.set_edgecolor('black')
                    part.set_alpha(alpha)
                for part in ('cbars', 'cmins', 'cmaxes', 'cmedians'):
                    vp = violins[part]
                    vp.set_edgecolor('black')
                    vp.set_linewidth(1)
                ax.set_xticks(np.array(positions) + 1)
                ax.set_xticklabels(positions)
            elif all(x in ("violin", ) for x in type) and not discrete_x and discrete_y:
                fig, ax = plt.subplots(1, 1)
                res = pd.DataFrame({'X': x, 'Y': y})
                values = []
                positions = sorted(list(y_count.keys()))
                for i in positions:
                    values.append(list(res[res.Y == i]['X']))
                violins = ax.violinplot(dataset=values, vert=False, showmedians=True)
                for part in violins['bodies']:
                    part.set_edgecolor('black')
                    part.set_alpha(alpha)
                for part in ('cbars', 'cmins', 'cmaxes', 'cmedians'):
                    vp = violins[part]
                    vp.set_edgecolor('black')
                    vp.set_linewidth(1)
                ax.set_yticks(np.array(positions) + 1)
                ax.set_yticklabels(positions)
            else:
                raise Exception("I don't know how to plot these variables.")
        else:
            if alpha is None:
                alpha = .1
            for x in self:
                if not hasattr(x, "__iter__"):
                    x = [x]
                plt.plot(x, 'k.-', alpha=alpha, **kwargs)

    def cov(self, **kwargs):
        if get_dimension(self) == 2:
            return np.cov(self, rowvar=False)[0, 1]
        elif get_dimension(self) > 0:
            return np.cov(self, rowvar=False)
        else:
            raise Exception("Covariance requires that the simulation results have consistent dimension.")

    def corr(self, **kwargs):
        if get_dimension(self) == 2:
            return np.corrcoef(self, rowvar=False)[0, 1]
        elif get_dimension(self) > 0:
            return np.corrcoef(self, rowvar=False)
        else:
            raise Exception("Correlation requires that the simulation results have consistent dimension.")

    def mean(self):
        if all(is_scalar(x) for x in self):
            return np.array(self).mean()
        elif get_dimension(self) > 0:
            return tuple(np.array(self).mean(0))
        else:
            raise Exception("I don't know how to take the mean of these values.")

    def var(self):
        if all(is_scalar(x) for x in self):
            return np.array(self).var()
        elif get_dimension(self) > 0:
            return tuple(np.array(self).var(0))
        else:
            raise Exception("I don't know how to take the variance of these values.")

    def sd(self):
        if all(is_scalar(x) for x in self):
            return np.array(self).std()
        elif get_dimension(self) > 0:
            return tuple(np.array(self).std(0))
        else:
            raise Exception("I don't know how to take the variance of these values.")

    def standardize(self):
        mean_ = self.mean()
        sd_ = self.sd() 
        if all(is_scalar(x) for x in self):
            return RVResults((x - mean_) / sd_ for x in self)
        elif get_dimension(self) > 0:
            return RVResults((np.asarray(self) - mean_) / sd_)


class RandomProcessResults(Results):

    def __init__(self, results, timeIndex):
        self.timeIndex = timeIndex
        super().__init__(results)

    def __getitem__(self, t):
        return RVResults(x[t] for x in self)

    def plot(self, tmin=0, tmax=10, alpha=.1, **kwargs):
        if self.timeIndex.fs == float("inf"):
            ts = np.linspace(tmin, tmax, 200)
            style = "k-"
        else:
            nmin = int(np.floor(tmin * self.timeIndex.fs))
            nmax = int(np.ceil(tmax * self.timeIndex.fs))
            ts = [self.timeIndex[n] for n in range(nmin, nmax)]
            style = "k.--"
        for x in self:
            y = [x[t] for t in ts]
            plt.plot(ts, y, style, alpha=alpha, **kwargs)
        plt.xlabel("Time (t)")

        # expand the y-axis slightly
        axes = plt.gca()
        ymin, ymax = axes.get_ylim()
        buff = .05 * (ymax - ymin)
        plt.ylim(ymin - buff, ymax + buff)

    def mean(self):
        def fun(t):
            return self[t].mean()
        return TimeFunction(fun, self.timeIndex)

    def var(self):
        def fun(t):
            return self[t].var()
        return TimeFunction(fun, self.timeIndex)

    def sd(self):
        def fun(t):
            return self[t].sd()
        return TimeFunction(fun, self.timeIndex)

