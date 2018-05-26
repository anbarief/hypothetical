# encoding=utf-8

import numpy as np
import numpy_indexed as npi
from scipy.stats import rankdata, norm
from hypy.critical import w_critical_value


def mann_whitney(y1, y2=None, group=None, continuity=True):
    r"""
    Performs the nonparametric Mann-Whitney U test of two independent sample groups.

    Parameters
    ----------
    y1
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, list, or dictionary)
        designating first sample
    y2
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, list, or dictionary)
        designating second sample to compare to first
    continuity
        Boolean, optional. If True, apply the continuity correction of :math:`\frac{1}{2}` to the
        mean rank.

    Returns
    -------
    namedtuple
        Namedtuple of following entries that contain resulting Mann-Whitney test statistics.
        Mann-Whitney U Test Statistic: The U Statistic of the Mann-Whitney test
        Mean Rank: The mean rank of U statistic
        Sigma: the standard deviation of U
        z-value: The standardized value of U
        p-value: p-value of U statistic compared to critical value

    Notes
    -----
    The Mann-Whitney U test is a nonparametric hypothesis test that tests the null hypothesis that
    there is an equally likely chance that a randomly selected observation from one sample will be
    less than or greater than a randomly selected observation from a second sample. Nonparametric
    methods are so named since they do not rely on the assumption of normality of the data.

    The test statistic in the Mann-Whitney setting is denoted as :math:`U` and is the minimum of
    the summed ranks of the two samples. The null hypothesis is rejected if :math:`U \leq U_0`,
    where :math:`U_0` is found in a table for small sample sizes. For larger sample sizes,
    :math:`U` is approximately normally distributed.

    The test is nonparametric in the sense it uses the ranks of the values rather than the values
    themselves. Therefore, the values are ordered then ranked from 1 (smallest value) to the largest
    value. Ranks of tied values get the mean of the ranks the values would have received. For example,
    for a set of data points :math:`\{4, 7, 7, 8\}` the ranks are :math:`\{1, 2.5, 2.5, 4\}`. The
    :math:`2.5` rank comes from :math:`2 + 3 = 5 / 2`. The ranks are then added for the values for
    both samples. The sum of the ranks for each sample are typically denoted by :math:`R_k` where
    :math:`k` is a sample indicator.

    :math:`U` for the two samples in the test, is given by:

    References
    ----------
    Mann–Whitney U test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
        From https://en.wikipedia.org/w/index.php?title=Mann%E2%80%93Whitney_U_test&oldid=786593885

    """
    return MannWhitney(y1=y1, y2=y2, group=group, continuity=continuity)


class MannWhitney(object):

    def __init__(self, y1, y2=None, group=None, continuity=True):

        if group is None:
            self.y1 = y1
            self.y2 = y2
        else:
            if len(group.unique()) > 2:
                raise ValueError('there cannot be more than two groups')

            obs_matrix = npi.group_by(group, y1)
            self.y1 = obs_matrix[1][0]
            self.y2 = obs_matrix[1][1]

        self.n1 = len(self.y1)
        self.n2 = len(self.y2)
        self.n = self.n1 + self.n2

        self.continuity = continuity
        self._ranks = self._rank()
        self.U = self._u()
        self.meanrank = self._mu()
        self.sigma = self._sigma()
        self.z_value = self._zvalue()
        self.p_value = self._pvalue()

    def _rank(self):
        ranks = np.concatenate((self.y1, self.y2))

        ranks = rankdata(ranks, 'average')

        ranks = ranks[:self.n1]

        return ranks

    def _u(self):
        u1 = self.n1 * self.n2 + (self.n1 * (self.n1 + 1)) / 2. - np.sum(self._ranks)
        u2 = self.n1 * self.n2 - u1

        u = np.minimum(u1, u2)

        return u

    def _mu(self):

        mu = (self.n1 * self.n2) / 2. + (0.5 * self.continuity)

        return mu

    def _sigma(self):
        rankcounts = np.unique(self._ranks, return_counts=True)[1]

        sigma = np.sqrt(((self.n1 * self.n2) * (self.n + 1)) / 12. * (
                    1 - np.sum(rankcounts ** 3 - rankcounts) / float(self.n ** 3 - self.n)))

        return sigma

    def _zvalue(self):
        z = (np.absolute(self.U - self.meanrank)) / self.sigma

        return z

    def _pvalue(self):
        p = 1 - norm.cdf(self.z_value)

        return p * 2

    def summary(self):
        mw_results = {
            'continuity': self.continuity,
            'U': self.U,
            'mu meanrank': self.meanrank,
            'sigma': self.sigma,
            'z-value': self.z_value,
            'p-value': self.p_value,
            'test description': 'Mann-Whitney U test'
        }

        return mw_results


class WilcoxonTest(object):

    def __init__(self, y1, y2=None, paired=False, mu=0, continuity=True, alpha=0.05, alternative='two-sided'):
        self.y1 = y1
        self.n = len(self.y1)
        self.paired = paired
        self.mu = mu
        self.continuity = continuity

        if paired:
            self.test_description = 'Wilcoxon signed rank test'
            if y2 is None:
                raise ValueError('sample 2 is missing for paired test')

            self.y1 = np.array(y1) - np.array(y2)

        else:
            self.V = self._one_sample_test()
            self.test_description = 'Wilcoxon signed rank test'

        if self.n > 30:
            self.z = self._zvalue()
        else:
            self.alpha = alpha
            self.alternative = alternative
            if alpha not in (0.01, 0.05):
                raise ValueError('alpha must be 0.05, or 0.01 when sample size is less than 30.')

            if self.alternative == 'two-sided':
                alt = 'two-tail'
            elif self.alternative in ('greater', 'less'):
                alt = 'one-tail'

            w_crit = w_critical_value(self.n, self.alpha, alt)



    def summary(self):
        test_results = {
            'V': self.V,
            'z-value': self.z,
            'test description': self.test_description
        }

        return test_results

    def _one_sample_test(self):
        y_mu_signed = self.y1 - self.mu
        y_mu_unsigned = np.absolute(y_mu_signed)

        ranks_signed = rankdata(y_mu_signed, 'average')
        ranks_unsigned = rankdata(y_mu_unsigned, 'average')

        z = np.where(ranks_signed > 0, 1, 0)

        v = np.sum(np.multiply(ranks_unsigned, z))

        return v

    def _zvalue(self):
        sigma_w = np.sqrt((self.n * (self.n + 1) * (2 * self.n + 1)) / 6.)

        z = self.V / sigma_w

        return z

    def _pvalue(self):
        p = 1 - norm.cdf(np.abs(self.z))

        return p * 2
