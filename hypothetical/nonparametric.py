# encoding=utf8

"""
Functions for performing nonparametric statistical inference. The classes listed in this module are intended to
act as 'back-ends' to their respective functions.

Nonparametric Inference Methods
-------------------------------

The functions listed here are the primary interfaces and are meant to be used over their respective classes.

.. autosummary::
    :toctree: generated/

    kruskal_wallis
    mann_whitney
    wilcoxon_test

The following classes contain the implementations of the algorithms and methods used in the respective
nonparametric inference methods.

.. autosummary::
    :toctree: generated/

    KruskalWallis
    MannWhitney
    WilcoxonTest

Other Functions
---------------

.. autosummary::
    :toctree: generated/

    tie_correction

References
----------
Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
    Wiley. ISBN 978-1118840313.

Fox J. and Weisberg, S. (2011) An R Companion to Applied Regression, Second Edition Sage.

Mann–Whitney U test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
    From https://en.wikipedia.org/w/index.php?title=Mann%E2%80%93Whitney_U_test&oldid=786593885

Wikipedia contributors. (2018, May 21). Kruskal–Wallis one-way analysis of variance.
        In Wikipedia, The Free Encyclopedia. From
        https://en.wikipedia.org/w/index.php?title=Kruskal%E2%80%93Wallis_one-way_analysis_of_variance&oldid=842351945

"""

import numpy as np
import numpy_indexed as npi
from scipy.stats import rankdata, norm, chi2, t

from hypothetical._lib import build_des_mat
from hypothetical.summary import var


def kruskal_wallis(*args, group=None, alpha=0.05):
    r"""
    Performs the nonparametric one-way anaylsis of variance Kruskal-Wallis test for two or
    more groups.

    Parameters
    ----------
    group_sample1, group_sample2, ... : array-like
        Corresponding observation vectors of the group samples. Must be the same length
        as the group parameter. If the group parameter is None, each observation vector
        will be treated as a group sample vector.
    group: array-like, optional
        One-dimensional array (Numpy ndarray, Pandas Series, list) that defines the group
        membership of the dependent variable(s). Must be the same length as the observation vector.
    alpha : float
        Desired alpha level for testing for significance.

    Returns
    -------
    kw : KruskalWallis class object
        :code:`KruskalWallis` class containing the fitted results. Please see the
        :code:`KruskalWallis` documentation for available attributes and methods.

    Notes
    -----
    The Kruskal-Wallis test extends the Mann-Whitney U test for more than two groups and can be
    considered the nonparametric equivalent of the one-way analysis of variance (ANOVA) method.
    The test is nonparametric similar to the Mann-Whitney test and as such does not
    assume the data are normally distributed and can, therefore, be used when the assumption
    of normality is violated.

    The Kruskal-Wallis test proceeds by ranking the data from 1 (the smallest) to the largest
    with ties replaced by the mean of the ranks the values would have received. The sum of
    the ranks for each treatment is typically denoted $T_i$ or $R_i$.

    The test statistic is denoted :code:`H` and can be defined as the following when the
    ranked data does not contain ties.

    .. math::

        H = \frac{12}{N(N + 1)} \left[ \frac{\sum_{i=1}^k T_{i}^2}{n_i} - 3(N + 1) \right]

    If the ranked data contains ties, a correction can be used by dividing :code:`H` by:

    .. math::

        1 - \frac{\sum_{t=1}^G (t_i^3 - t_i)}{N^3 - N}

    Where :code:`G` is the number of groups of tied ranks and :code:`t_i` is the number of
    tied values within the :code:`i^{th}` group. The p-value is usually approximated using
    a Chi-Square distribution as calculating exact probabilities can be computationally
    intensive for larger sample sizes.

    See Also
    --------
    KruskalWallis : class containing the implementation of the algorithms and methods used
    when performing thr Kruskal-Wallis test.

    Examples
    --------
    There are several ways to perform the Kruskal-Wallis test with the :code:`kruskal_wallis` function.
    Similar to the parametric one-way ANOVA method implemented by the :code:`anova_one_way` function,
    one approach is to pass a group vector with the :code:`group` parameter and the corresponding
    observation vector as below.

    The data used in this example is a subset of the data obtained from the plant growth
    dataset given in Dobson (1983).

    >>> group_vector = ['ctrl', 'ctrl', 'ctrl',
    ...                 'trt1', 'trt1', 'trt1',
    ...                 'trt2', 'trt2', 'trt2']
    >>> observation_vec = [4.17, 5.58, 5.18,
    ...                    4.81, 4.17, 4.41,
    ...                    5.31, 5.12, 5.54]
    >>> kw = kruskal_wallis(observation_vec, group=group_vector)
    >>> kw.summary()
    {'alpha': 0.05,
     'critical chisq value': 3.1148459383753497,
     'degrees of freedom': 2,
     'least significant difference': 4.916428084371546,
     'p-value': 0.21067829669685478,
     't-value': 2.4469118487916806,
     'test description': 'Kruskal-Wallis rank sum test'}

    The other approach is to pass each group sample vector similar to the below.

    >>> ctrl = [4.17, 5.58, 5.18]
    >>> trt1 = [4.81, 4.17, 4.41]
    >>> trt2 = [5.31, 5.12, 5.54]
    >>> kw2 = kruskal_wallis(ctrl, trt1, trt2)
    >>> kw2.summary()
    {'alpha': 0.05,
     'critical chisq value': 3.1148459383753497,
     'degrees of freedom': 2,
     'least significant difference': 4.916428084371546,
     'p-value': 0.21067829669685478,
     't-value': 2.4469118487916806,
     'test description': 'Kruskal-Wallis rank sum test'}

    References
    ----------
    Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
        Wiley. ISBN 978-1118840313.

    Wikipedia contributors. (2018, May 21). Kruskal–Wallis one-way analysis of variance.
        In Wikipedia, The Free Encyclopedia. From
        https://en.wikipedia.org/w/index.php?title=Kruskal%E2%80%93Wallis_one-way_analysis_of_variance&oldid=842351945

    """
    kw = KruskalWallis(*args, group=group, alpha=alpha)

    return kw


def mann_whitney(y1, y2=None, group=None, continuity=True):
    r"""
    Performs the nonparametric Mann-Whitney U test of two independent sample groups.

    Parameters
    ----------
    y1 : array-like
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating first sample observation vector.
    y2 : array-like, optional
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating second sample observation vector.
    group : array-like, optional
        One-dimensional array (Numpy ndarray, Pandas Series or DataFrame, or list) that defines
        the group membership of the sample vector(s). Must be the same length as the observation vector.
    continuity : bool
        If True, apply the continuity correction of :math:`\frac{1}{2}` to the
        mean rank.

    Returns
    -------
    res : MannWhitney or WilcoxonTest class object
        :code:`MannWhitney` class object containing the fitted results. If only one sample vector
        is passed, a Wilcoxon Signed Rank Test is performed and a :code:`WilcoxonTest` class
        object containing the fitted results is returned.

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

    .. math::

        U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}
        U_2 = R_2 - \frac{n_2(n_2 + 1)}{2}

    Where :math:`R_1` and :math:`R_2` are the sum of the ranks of the two samples.

    Examples
    --------
    Similar to the :code:`anova_one_way` function, there are several ways to perform a Mann-Whitney
    U test with the :code:`mann_whitney` function. One of these approaches is to pass the sample data
    vector and a group vector of the same length denoting group membership of the sample observations.

    The data used in this example is a subset of the professor salary dataset found in Fox and
    Weisberg (2011).

    >>> professor_discipline = ['B', 'B', 'B', 'B', 'B',
    ...                         'A', 'A', 'A', 'A', 'A']
    >>> professor_salary = [139750, 173200, 79750, 11500, 141500,
    ...                     103450, 124750, 137000, 89565, 102580]
    >>> mw = mann_whitney(group=professor_discipline, y1=professor_salary)
    >>> mw.summary()
    {'U': 10.0,
     'continuity': True,
     'mu meanrank': 13.0,
     'p-value': 0.5308693039685082,
     'sigma': 4.7871355387816905,
     'test description': 'Mann-Whitney U test',
     'z-value': 0.6266795614405122}

    The other approach is to pass each group sample observation vector.

    >>> sal_a = [139750, 173200, 79750, 11500, 141500]
    >>> sal_b = [103450, 124750, 137000, 89565, 102580]
    >>> mw2 = mann_whitney(sal_a, sal_b)
    >>> mw2.summary()
    {'U': 10.0,
     'continuity': True,
     'mu meanrank': 13.0,
     'p-value': 0.5308693039685082,
     'sigma': 4.7871355387816905,
     'test description': 'Mann-Whitney U test',
     'z-value': 0.6266795614405122}

    References
    ----------
    Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
        Wiley. ISBN 978-1118840313.

    Fox J. and Weisberg, S. (2011) An R Companion to Applied Regression, Second Edition Sage.

    Mann–Whitney U test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
        From https://en.wikipedia.org/w/index.php?title=Mann%E2%80%93Whitney_U_test&oldid=786593885

    """
    if y2 is None and group is None:
        res = WilcoxonTest(y1=y1)
    else:
        res = MannWhitney(y1=y1, y2=y2, group=group, continuity=continuity)

    return res


def wilcoxon_test(y1, y2=None, paired=False, mu=0):
    r"""
    Performs one-sample Wilcoxon Rank Sum tests.

    Parameters
    ----------
    y1 : array-like
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating first sample observation vector.
    y2 : array-like, optional
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating second sample observation vector.
    paired : bool, optional
        If True, performs a paired Wilcoxon Rank Sum test.
    mu : float, optional
        Optional parameter to specify the value to form the null hypothesis.

    Returns
    -------
    res : WilcoxonTest or MannWhitney class object containing the fitted model results.
        If only one sample vector is passed (or two sample vectors with the :code:`paired` parameter
        set to :code:`True`), a fitted :code:`WilcoxonTest` class object containing the
        test results is returned. Otherwise, a Mann-Whitney U-test is performed and a
        :code:`MannWhitney` class object containing the fitted test results is returned.

    Notes
    -----
    The Wilcoxon Rank Sum test is the nonparametric equivalent to a one-sample t-test and is also closely
    related to the Mann Whitney U-test for independent samples. In fact, the Wilcoxon Rank Sum test for two
    independent samples is equivalent to the Mann Whitney U-test. The respective test statistics :math:`W`
    (Mann-Whitney) and :math:`U` (Wilcoxon Rank Sum) are related in the following way:

    .. math::

        U = W - \frac{n_1 (n_1 + 1)}{2}



    When two sample observation vectors are passed into the :code:`wilcoxon_test` function, the Mann-Whitney
    U-test is performed.

    See Also
    --------
    WilcoxonTest : class containing the implemented algorithms and methods used when conducting the Wilcoxon
        Rank Sum test.
    mann_whitney : related nonparametric test for two independent samples.

    Examples
    --------
    The data used in this example is a subset of the professor salary dataset found in Fox and
    Weisberg (2011).

    >>> professor_salary = [139750, 173200, 79750, 11500, 141500,
    ...                     103450, 124750, 137000, 89565, 102580]

    References
    ----------
    Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
        Wiley. ISBN 978-1118840313.

    Fox J. and Weisberg, S. (2011) An R Companion to Applied Regression, Second Edition Sage.

    """
    if y2 is not None and paired is False:
        res = MannWhitney(y1=y1, y2=y2)
    else:
        res = WilcoxonTest(y1=y1, y2=y2, paired=paired, mu=mu)

    return res


class KruskalWallis(object):
    r"""
    Class containing the algorithms and methods used in the construction and conduction of the
    Kruskal-Wallis H-test.

    Attributes
    ----------
    design_matrix : array-like
        Numpy ndarray representing the data matrix for the analysis.
    ranked_matrix : array-like
        Numpy ndarray representing the data matrix with the ranked observations.
    alpha : float
        Alpha level for determining significance.
    n : int
        Number of sample observations.
    k : int
        Number of treatment groups.
    dof : int
        Degrees of freedom, defined as :math:`k - 1`.
    H : float
        Calculated Kruskal-Wallis H-statistic.
    t_value : float
        The critical t-value for computing the Least Significant Difference.
    p_value : float
        Corresponding p-value of the :math:`H`-statistic. The distribution of :math:`H` is approximated
        by the chi-square distribution.
    least_significant_difference : float
        Calculated Least Significant Difference for determining if treatment group means are significantly
        different from each other.
    test_description : str
        String describing the performed test. By default, the test description will be Kruskal-Wallis rank sum test

    Parameters
    ----------
    group_sample1, group_sample2, ... : array-like
        Corresponding observation vectors of the group samples. Must be the same length
        as the group parameter. If the group parameter is None, each observation vector
        will be treated as a group sample vector.
    group: array-like, optional
        One-dimensional array (Numpy ndarray, Pandas Series, list) that defines the group
        membership of the dependent variable(s). Must be the same length as the observation vector.
    alpha : float
        Desired alpha level for testing for significance.

    Raises
    ------
    ValueError
        As the Kruskal-Wallis is a univariate test, only one sample observation vector should be passed
        when including a group vector in the :code:`group` parameter.

    See Also
    --------
    kruskal_wallis : function that acts as an 'interface' to the :code:`KruskalWallis` class and its
        implementations of the test.
    AnovaOneWay : class containing the implementations of the algorithms and methods used in the
        conduction of the one-way analysis of variance procedure. The Kruskal-Wallis test can be
        considered the nonparametric equivalent of the one-way analysis of variance method.

    """
    def __init__(self, *args, group=None, alpha=0.05):

        if group is not None and len(args) > 1:
            raise ValueError('Only one sample vector should be passed when including a group vector')

        self.design_matrix = build_des_mat(*args, group=group)

        if group is not None:
            self.group = group
        else:
            self.group = self.design_matrix[:, 0]

        self.ranked_matrix = self._rank()
        self.group_rank_sums = self._group_rank_sums()
        self.alpha = alpha
        self.n = self.design_matrix.shape[0]
        self.k = len(np.unique(self.design_matrix[:, 0]))
        self.dof = self.k - 1
        self.H = self.h_statistic()
        self.p_value = self.p_val()
        self.t_value = self.t_val()
        self.least_significant_difference = self.lsd()
        self.test_description = 'Kruskal-Wallis rank sum test'

    def h_statistic(self):
        r"""
        Computes the Kruskal-Wallis :math:`H`-statistic.

        Returns
        -------
        h : float
            Computed Kruskal-Wallis :math:`H`-statistic.

        Notes
        -----
        The Kruskal-Wallis :math:`H`-statistic is defined as the following when the ranked data does not
        contain ties.

        .. math::

            H = \frac{12}{N(N + 1)} \left[ \frac{\sum_{i=1}^k T_{i}^2}{n_i} - 3(N + 1) \right]

        If the ranked data contains ties, a correction can be used by dividing :code:`H` by:

        .. math::

            1 - \frac{\sum_{t=1}^G (t_i^3 - t_i)}{N^3 - N}

        Where :code:`G` is the number of groups of tied ranks and :code:`t_i` is the number of
        tied values within the :code:`i^{th}` group.

        The tie correction is automatically applied in the computation of the :math:`H`-statistic.

        References
        ----------
        Wikipedia contributors. (2018, May 21). Kruskal–Wallis one-way analysis of variance.
            In Wikipedia, The Free Encyclopedia. From
            https://en.wikipedia.org/w/index.php?title=Kruskal%E2%80%93Wallis_one-way_analysis_of_variance&oldid=842351945

        """
        group_observations = npi.group_by(self.design_matrix[:, 0], self.design_matrix[:, 1:], len)

        group_observations = np.array([i for _, i in group_observations])

        group_summed_ranks = np.array([i for _, i in self.group_rank_sums])

        h1 = 12. / (self.n * (self.n + 1))
        h2 = np.sum(group_summed_ranks ** 2 / group_observations)

        h = h1 * h2 - (3 * (self.n + 1))

        # Apply tie correction
        h /= tie_correction(self.ranked_matrix[:, 2])

        return h

    def p_val(self):
        r"""
        Computes the p-value of the :math:`H`-statistic approximated by the chi-square distribution.

        Returns
        -------
        p : float
            The computed p-value.

        Notes
        -----
        The :math:`p`-value is approximated by a chi-square distribution with :math:`k - 1` degrees
        of freedom.

        .. math::

            Pr(\chi^2_{k - 1} \geq H)

        References
        ----------
        Wikipedia contributors. (2018, May 21). Kruskal–Wallis one-way analysis of variance.
            In Wikipedia, The Free Encyclopedia. From
            https://en.wikipedia.org/w/index.php?title=Kruskal%E2%80%93Wallis_one-way_analysis_of_variance&oldid=842351945

        """
        p = 1 - chi2.cdf(self.H, self.dof)

        return p

    def t_val(self):
        r"""
        Returns the critical t-statistic given the input alpha-level (defaults to 0.05).

        Returns
        -------
        tval : float
            The critical t-value for using in computing the Least Significant Difference.

        Notes
        -----
        Scipy's :code:`t.ppf` method is used to compute the critical t-value.

        """
        tval = t.ppf(1 - self.alpha / 2, self.n - self.k)

        return tval

    def lsd(self):
        r"""
        Returns the Least Significant Difference statistic used for determining if treatment group
        means are significantly different from each other.

        Returns
        -------
        lsd : float
            The calculated Least Significant Difference.

        Notes
        -----
        The Least Significant Difference is a test statistic developed by Ronald Fisher. The basic
        idea of the LSD is to find the smallest difference between two sample means and conclude a
        significant difference if a comparison between two other group means exceeds the LSD. The
        Least Significant Difference is defined as:

        .. math::

            t_{\alpha, N-k} \sqrt{MSE \frac{2}{n}}

        Where :math:`t_{\alpha, N-k}` is the critical t-value given the input alpha-level and :math:`MSE`
        is the mean error sum of squares as in the one-way analysis of variance procedure.

        References
        ----------
        Fisher’s Least Significant Difference (LSD) Test. (2010). [ebook] Thousand Oaks.
            Available at: https://www.utd.edu/~herve/abdi-LSD2010-pretty.pdf [Accessed 11 Jun. 2018].

        """
        lsd = self.t_value * np.sqrt(self._mse() * 2 / (self.n / self.k))

        return lsd

    def summary(self):
        r"""
        Returns a summary of the Kruskal-Wallis test as a dictionary.

        Returns
        -------
        test_results : dict
            Dictionary containing the fitted Kruskal-Wallis :math:`H`-test results.

        """
        test_results = {'test description': self.test_description,
                        'critical chisq value': self.H,
                        'p-value': self.p_value,
                        'least significant difference': self.least_significant_difference,
                        't-value': self.t_value,
                        'alpha': self.alpha,
                        'degrees of freedom': self.dof
        }

        return test_results

    def _rank(self):

        ranks = rankdata(self.design_matrix[:, 1], 'average')

        ranks = np.column_stack([self.design_matrix, ranks])

        return ranks

    def _group_rank_sums(self):
        rank_sums = npi.group_by(self.ranked_matrix[:, 0], self.ranked_matrix[:, 2], np.sum)

        return rank_sums

    def _mse(self):
        group_variance = npi.group_by(self.ranked_matrix[:, 0], self.ranked_matrix[:, 2], var)
        group_n = npi.group_by(self.ranked_matrix[:, 0], self.ranked_matrix[:, 2], len)

        sse = 0

        for i, j in zip(group_n, group_variance):
            sse += (i[1] - 1) * j[1]

        return sse / (self.n - self.k)


class MannWhitney(object):
    r"""
    Class containing the implementations of the algorithms and methods used for performing a
    Mann-Whitney U-test. Acts as an internal 'back-end' for the :code:`mann_whitney` function.

    Parameters
    ----------
    y1 : array-like
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating first sample observation values.
    y2 : array-like, optional
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating second sample observation values.
    group : array-like, optional
        One-dimensional array (Numpy ndarray, Pandas Series or DataFrame, or list) that defines
        the group membership of the sample vector(s). Must be the same length as the observation vector.
    continuity : bool
        If True, apply the continuity correction of :math:`\frac{1}{2}` to the
        mean rank.

    Attributes
    ----------
    y1 : array-like
        First sample observation vector.
    y2 : array-like or None
        Second sample observation vector, if passed. Otherwise, will return None.
    n1 : int
        Number of sample observations in the first sample vector.
    n2 : int or None
        Number of sample observations in the second sample vector. If no second observation vector was
        passed, will return None.
    n : int
        Total number of sample observations (sum of :code:`n1` and :code:`n2`.
    continuity : bool
        If True, continuity correction is applied.
    U : int
        Computed U-statistic.
    meanrank : float
        The mean of the ranked sample observations.
    sigma : float
        The calculated standard deviation, :math:`\sigma_U`.
    z_value : float
        Standardized :math:`z` value.
    p_value : float
        Computed p-value.
    effect_size : float
        Calculated estimated Cohen's effect size.

    Notes
    -----
    The :code:`MannWhitney` class contains the implementations of the algorithms and methods used in the
    computation of the test. The function :code:`mann_whitney` that acts as an interface to the class
    is meant to be called rather than the class itself.

    See Also
    --------
    mann_whitney : function for performing the Mann-Whitney U-test.

    """
    def __init__(self, y1, y2=None, group=None, continuity=True):

        if group is None:
            self.y1 = y1
            self.y2 = y2
        else:
            if len(np.unique(group)) > 2:
                raise ValueError('there cannot be more than two groups')

            obs_matrix = npi.group_by(group, y1)
            self.y1 = obs_matrix[1][0]
            self.y2 = obs_matrix[1][1]

        self.n1 = len(self.y1)
        self.n2 = len(self.y2)
        self.n = self.n1 + self.n2

        self.continuity = continuity
        self._ranks = self._rank()
        self.u_statistic = self.u()
        self.meanrank = self.mu()
        self.sigma = self.sigma_val()
        self.z_value = self.z()
        self.p_value = self.p_val()
        self.effect_size = self.eff_size()

    def u(self):
        r"""
        Calculates the Mann-Whitney U statistic.

        Returns
        -------
        u : float

        Notes
        -----
        The chosen :code:`U` statistic is the smaller of the two statistics. The :code:`U`-statistic
        for sample :code:`k` is defined as:

        .. math::

            U_k = n_1 n_2 + \frac{n_k (n_k + 1)}{2} - \sum{R_k}

        Where :code:`n` is the number of sample observations and :code:`\sum{R_k}` is the sum of the
        ranked sample observations.

        The second sample :code:`U`-statistic can also be found by:

        .. math::

            U_1 + U_2 = n_1 n_2

        References
        ----------
        Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
            Wiley. ISBN 978-1118840313.

        """
        u1 = self.n1 * self.n2 + (self.n1 * (self.n1 + 1)) / 2. - np.sum(self._ranks)
        u2 = self.n1 * self.n2 - u1

        u = np.minimum(u1, u2)

        return u

    def mu(self):
        r"""
        Computes the mean of the ranked sample observations.

        Returns
        -------
        mu_rank : float
            The mean of the ranked sample values.

        Notes
        -----
        The mean of the ranked samples is defined as:

        .. math::

            m_u = \frac{n_1 n_2}{2}

        References
        ----------
        Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
            Wiley. ISBN 978-1118840313.

        Mann–Whitney U test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
            From https://en.wikipedia.org/w/index.php?title=Mann%E2%80%93Whitney_U_test&oldid=786593885

        """
        mu_rank = (self.n1 * self.n2) / 2. + (0.5 * self.continuity)

        return mu_rank

    def sigma_val(self):
        r"""
        Calculates the standard deviation of the ranked sample observations.

        Returns
        -------
        sigma : float
            The standard deviation of the ranked sample values.

        Notes
        -----
        If there are no tied sample ranks, the standard deviation, :math:`\sigma_U`, can be calculated as
        the following:

        .. math::

            \sigma_U = \sqrt{\frac{n_1 n_2 (n_1 + n_2 + 1)}{12}}

        When tied ranks are present, the corrected standard deviation formula should be used instead.

        .. math::

            \sigma_{U_corr} = \sqrt{\frac{n_1 n_2}{12} \large((n + 1) - \sum_{i=1}^k \frac{t^3 - t_i}{n(n - 1)}\large)}

        Where :math:`n_1` and :math:`n_2` are the number of sample observations of group one and two, :math:`t_i` is
        the number of values sharing rank :math:`i` and :math:`k` is the number of unique ranks.

        References
        ----------
        Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
            Wiley. ISBN 978-1118840313.

        Mann–Whitney U test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
            From https://en.wikipedia.org/w/index.php?title=Mann%E2%80%93Whitney_U_test&oldid=786593885

        """
        rankcounts = np.unique(self._ranks, return_counts=True)[1]

        sigma = np.sqrt(((self.n1 * self.n2) * (self.n + 1)) / 12. * (
                    1 - np.sum(rankcounts ** 3 - rankcounts) / float(self.n ** 3 - self.n)))

        return sigma

    def z(self):
        r"""
        Computes the standardized :math:`z` value.

        Returns
        -------
        z : float
            The standardized value.

        Notes
        -----
        The standardized value is found by the following formula:

        .. math::

            z = \frac{U - m_u}{\sigma_u}

        References
        ----------
        Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
            Wiley. ISBN 978-1118840313.

        Mann–Whitney U test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
            From https://en.wikipedia.org/w/index.php?title=Mann%E2%80%93Whitney_U_test&oldid=786593885

        """
        z = (np.absolute(self.u_statistic - self.meanrank)) / self.sigma

        return z

    def p_val(self):
        r"""
        Returns the p-value.

        Returns
        -------
        p : float
            The computed p value.

        Notes
        -----
        When sample sizes are large enough (:math:`n > 20`), the distribution of :math:`U` is normally
        distributed.

        """
        p = 1 - norm.cdf(self.z_value)

        return p * 2

    def eff_size(self):
        r"""
        Computes the effect size for determining the degree of association between groups.

        Returns
        -------
        es : float
            The effect size.

        Notes
        -----
        The effect size is defined as:

        .. math::

            ES = \frac{|z|}{\sqrt{n}}

        Effect sizes range from 0 to 1. A handy reference provided by Cohen (1988) defined the 'strength'
        of the effect size as:

        1. small = 0.10
        2. medium = 0.30
        3. large = 0.50

        References
        ----------
        Corder, G.W.; Foreman, D.I. (2014). Nonparametric Statistics: A Step-by-Step Approach.
            Wiley. ISBN 978-1118840313.

        """
        es = np.abs(self.z_value) / np.sqrt(self.n)

        return es

    def summary(self):
        r"""
        Method for returning the relevant statistics and information from a fitted Mann-Whitney U-test.

        Returns
        -------
        mw_results : dict
            Dictionary containing the fitted Mann-Whitney test results.

        """
        mw_results = {
            'continuity': self.continuity,
            'U': self.u_statistic,
            'mu meanrank': self.meanrank,
            'sigma': self.sigma,
            'z-value': self.z_value,
            'effect size': self.effect_size,
            'p-value': self.p_value,
            'test description': 'Mann-Whitney U test'
        }

        return mw_results

    def _rank(self):
        ranks = np.concatenate((self.y1, self.y2))

        ranks = rankdata(ranks, 'average')

        ranks = ranks[:self.n1]

        return ranks


class WilcoxonTest(object):
    r"""
    Class containing the implementations of the algorithms and methods used in the conduction of the
    Wilcoxon Signed Rank test. Acts as an internal 'back-end' to the :code:`wilcoxon_test` function.

    Parameters
    ----------
    y1 : array-like
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating first sample observation values.
    y2 : array-like, optional
        One-dimensional array-like (Pandas Series or DataFrame, Numpy array, or list)
        designating second sample observation values.
    paired : bool, optional
        If True, performs a paired Wilcoxon Rank Sum test.
    mu : float, optional
        Optional parameter to specify the value to form the null hypothesis.

    Attributes
    ----------
    y1 : array-like
        First sample observation vector.
    y2 : array-like or None
        Second sample observation vector, if passed. Otherwise, will return None.
    n : int
        Number of sample observations.
    V : float
        Wilcoxon :math:`V`-statistic (also denoted :math:`W` and :math:`U` in some literature).
    z : float
        The standardized z-statistic.
    p : float
        p-value.
    effect_size : float
        The estimated effect size.

    Notes
    -----
    The 'front-end' function :code:`wilcoxon_test` is meant to be used over the :code:`WilcoxonTest` class.

    See Also
    --------
    wilcoxon_test : function for performing Wilcoxon signed rank tests that acts as an interface to the
        :code:`WilcoxonTest`.

    """
    def __init__(self, y1, y2=None, paired=False, mu=0, alpha=0.05, alternative='two-sided'):
        self.paired = paired
        self.median = mu
        self.alternative = alternative
        self.test_description = 'Wilcoxon signed rank test'

        if paired:
            if y2 is None:
                raise ValueError('sample 2 is missing for paired test')
            if len(y1) != len(y2):
                raise ValueError('samples must have same length for paired test')

            self.y1 = np.array(y1) - np.array(y2)

        else:
            self.y1 = np.array(y1)

        self.n = len(self.y1)

        self.V = self.v_statistic()

        self.z = self.zvalue()
        self.p = self.pvalue()
        self.effect_size = self.eff_size()

        # if self.n > 10:
        #     self.z = self._zvalue()
        # else:
        #     self.alpha = alpha
        #     self.alternative = alternative
        #
        #     if self.alternative == 'two-sided':
        #         alt = 'two-tail'
        #     else:
        #         alt = 'one-tail'
        #
        #     w_crit = w_critical_value(self.n, self.alpha, alt)

    def v_statistic(self):
        r"""


        Returns
        -------

        Notes
        -----

        References
        ----------

        """
        if self.paired:
            y_median_signed = self.y1
        else:
            y_median_signed = self.y1 - self.median

        y_median_unsigned = np.absolute(y_median_signed)

        ranks_signed = rankdata(y_median_signed, 'average')
        ranks_unsigned = rankdata(y_median_unsigned, 'average')

        z = np.where(ranks_signed > 0, 1, 0)

        v = np.sum(np.multiply(ranks_unsigned, z))

        return v

    def zvalue(self):
        sigma_w = np.sqrt((self.n * (self.n + 1) * (2 * self.n + 1)) / 6.)

        z = self.V / sigma_w

        return z

    def pvalue(self):
        p = (1 - norm.cdf(np.abs(self.z)))

        if self.alternative == 'two-sided':
            p *= 2
        elif self.alternative == 'greater':
            p = 1 - p

        if p == 0:
            p = np.finfo(float).eps

        return p

    def eff_size(self):
        es = np.abs(self.z) / np.sqrt(self.n)

        return es

    def summary(self):
        test_results = {
            'V': self.V,
            'z-value': self.z,
            'p-value': self.p,
            'effect size': self.effect_size,
            'test description': self.test_description
        }

        return test_results


def tie_correction(rank_array):
    r"""
    Computes the tie correction factor used in Mann-Whitney and Kruskal-Wallis tests.

    Parameters
    ----------
    rank_array : array-like
        1-d array (numpy array, list, pandas DataFrame or Series) of ranks.

    Returns
    -------
    corr : float
        The correction factor for :math:`H` (or :math:`U` for the Mann-Whitney U-test).

    Notes
    -----
    The tie correction factor is defined as:

    .. math::

            1 - \frac{\sum_{t=1}^G (t_i^3 - t_i)}{N^3 - N}

    Where :code:`G` is the number of groups of tied ranks and :code:`t_i` is the number of
    tied values within the :code:`i^{th}` group.

    Examples
    --------
    The ranked values of an observation vector can be easily found using Scipy's :code:`tiecorrect`
    function.

    >>> obs = [4.17, 5.58, 5.18, 4.81, 4.17, 4.41, 5.31, 5.12, 5.54]
    >>> ranked_obs = rankdata(obs)
    >>> ranked_obs
    array([1.5, 9. , 6. , 4. , 1.5, 3. , 7. , 5. , 8. ])

    >>> tie_correction(ranked_obs)
    0.9916666666666667

    References
    ----------
    Wikipedia contributors. (2018, May 21). Kruskal–Wallis one-way analysis of variance.
            In Wikipedia, The Free Encyclopedia. From
            https://en.wikipedia.org/w/index.php?title=Kruskal%E2%80%93Wallis_one-way_analysis_of_variance&oldid=842351945

    """
    tied_groups = np.unique(rank_array, return_counts=True)[1]
    tied_groups = tied_groups[tied_groups > 1]

    corr = 1 - np.sum((tied_groups ** 3 - tied_groups)) / (rank_array.shape[0] ** 3 -
                                                           rank_array.shape[0])

    return corr
