# encoding=utf8

"""
Functions for performing classical hypothesis testing.

Hypothesis Testing
------------------

.. autosummary::
    :toctree: generated/

    BinomialTest
    tTest

References
----------
Rencher, A. C., & Christensen, W. F. (2012). Methods of multivariate analysis (3rd Edition).

Siegel, S. (1956). Nonparametric statistics: For the behavioral sciences.
    McGraw-Hill. ISBN 07-057348-4

Student's t-test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
    From https://en.wikipedia.org/w/index.php?title=Student%27s_t-test&oldid=786562367

Wikipedia contributors. (2018, July 14). Binomial proportion confidence interval.
    In Wikipedia, The Free Encyclopedia. Retrieved 15:03, August 10, 2018,
    from https://en.wikipedia.org/w/index.php?title=Binomial_proportion_confidence_interval&oldid=850256725

"""

import numpy as np
import numpy_indexed as npi
from scipy.stats import beta, chi2, norm, t
from scipy.special import comb


class BinomialTest(object):
    r"""
    Performs a one-sample binomial test.

    Parameters
    ----------
    x : int
        Number of successes out of :math:`n` trials.
    n : int
        Number of trials
    p : float, optional
        Expected probability of success
    alternative: str, {'two-sided', 'greater', 'lesser'}, optional
        Specifies the alternative hypothesis :math:`H_1`. Must be one of 'two-sided' (default), 'greater',
        or 'less'.
    alpha : float, optional
        Significance level
    continuity: bool, optional
        If True, the continuity corrected version of the Wilson score interval is used.

    Attributes
    ----------
    x : int
        Number of successes out of :math:`n` trials.
    n : int
        Number of trials
    p : float
        Expected probability of success
    q : float
        Defined as :math:`1 - p`
    alternative : str
        Specifies the alternative hypothesis :math:`H_1`. Must be one of 'two-sided' (default), 'greater',
        or 'less'.
    alpha : float
        Significance level
    continuity : bool
        If True, the continuity corrected version of the Wilson score interval is used.
    p_value : float
        Computed p-value
    z : float
        z-score used in computation of intervals
    clopper_pearson_interval : dict
        Dictionary of the Clopper-Pearson lower and upper intervals and probability of success.
    wilson_score_interval : dict
        Dictionary of the Wilson Score lower and upper intervals and probability of success.
    agresti_coull_interval : dict
        Dictionary of the Agresti-Coull lower and upper intervals and probability of success.
    arcsine_transform_interval : dict
        Dictionary of the arcsine transformation lower and upper intervals and probability of success.
    test_summary : dict
        Dictionary containing test summary statistics.

    Raises
    ------
    ValueError
        If number of successes :math:`x` is greater than the number of trials :math:`n`.
    ValueError
        If expected probability :math:`p` is greater than 1.
    ValueError
        If parameter :code:`alternative` is not one of {'two-sided', 'greater', 'lesser'}

    Notes
    -----


    Examples
    --------


    References
    ----------
    Siegel, S. (1956). Nonparametric statistics: For the behavioral sciences.
        McGraw-Hill. ISBN 07-057348-4

    Wikipedia contributors. (2018, July 14). Binomial proportion confidence interval.
        In Wikipedia, The Free Encyclopedia. Retrieved 15:03, August 10, 2018,
        from https://en.wikipedia.org/w/index.php?title=Binomial_proportion_confidence_interval&oldid=850256725

    """
    def __init__(self, n, x, p=0.5, alternative='two-sided', alpha=0.05, continuity=True):

        if x > n:
            raise ValueError('number of successes cannot be greater than number of trials.')

        if p > 1.0:
            raise ValueError('expected probability of success cannot be greater than 1.')

        if alternative not in ('two-sided', 'greater', 'lesser'):
            raise ValueError("'alternative must be one of 'two-sided' (default), 'greater', or 'lesser'.")

        self.n = n
        self.x = x
        self.p = p
        self.q = 1.0 - self.p
        self.alpha = alpha
        self.alternative = alternative
        self.continuity = continuity
        self.p_value = self._p_value()
        self.z = norm.ppf(1 - self.alpha / 2)
        self.clopper_pearson_interval = self._clopper_pearson_interval()
        self.wilson_score_interval = self._wilson_score_interval()
        self.agresti_coull_interval = self._agresti_coull_interval()
        self.arcsine_transform_interval = self._arcsine_transform_interval()
        self.test_summary = self._generate_test_summary()

    def _p_value(self):

        successes = np.arange(self.x + 1)

        pval = np.sum(comb(self.n, successes) * self.p ** successes * self.q ** (self.n - successes))

        if self.alternative == 'two-sided':
            other_tail = np.arange(self.x + 1, self.n + 1)

            y = comb(self.n, self.x) * (self.p ** self.x) * self.q ** (self.n - self.x)

            p_othertail = comb(self.n, other_tail) * self.p ** other_tail * self.q ** (self.n - other_tail)
            p_othertail = np.sum(p_othertail[p_othertail <= y])

            pval += p_othertail

        return pval

    def _clopper_pearson_interval(self):
        r"""

        References
        ----------
        Wikipedia contributors. (2018, July 14). Binomial proportion confidence interval.
            In Wikipedia, The Free Encyclopedia. Retrieved 00:40, August 15, 2018,
            from https://en.wikipedia.org/w/index.php?title=Binomial_proportion_confidence_interval&oldid=850256725

        """
        p = self.x / self.n

        lower_bound = beta.ppf(self.alpha / 2, self.x, self.n - self.x + 1)
        upper_bound = beta.ppf(1 - self.alpha / 2, self.x + 1, self.n - self.x)

        clopper_pearson_interval = {
            'probability of success': p,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

        return clopper_pearson_interval

    def _wilson_score_interval(self):
        r"""

        References
        ----------
        Wikipedia contributors. (2018, July 14). Binomial proportion confidence interval.
            In Wikipedia, The Free Encyclopedia. Retrieved 00:40, August 15, 2018,
            from https://en.wikipedia.org/w/index.php?title=Binomial_proportion_confidence_interval&oldid=850256725

        """
        p = (self.p + (self.z ** 2 / (2. * self.n))) / (1. + (self.z ** 2. / self.n))

        if self.continuity:
            lower = (2. * self.n * self.p + self.z ** 2. - (self.z * np.sqrt(
                self.z ** 2. - (1. / self.n) + 4. * self.n * self.p * self.q + (4. * self.p - 2.) + 1.))) / \
                    (2. * (self.n + self.z ** 2.))

            upper = (2. * self.n * self.p + self.z ** 2. + (self.z * np.sqrt(
                self.z ** 2. - (1. / self.n) + 4. * self.n * self.p * self.q + (4. * self.p - 2.) + 1))) / (2. * (
                                      self.n + self.z ** 2.))

            upper_bound, lower_bound = np.minimum(1.0, upper), np.maximum(0.0, lower)

        else:
            bound = (self.z / (1. + self.z ** 2. / self.n)) * \
                    np.sqrt(((self.p * self.q) / self.n) + (self.z ** 2. / (4. * self.n ** 2.)))

            upper_bound, lower_bound = p + bound, p - bound

        wilson_interval = {
            'probability of success': p,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

        return wilson_interval

    def _agresti_coull_interval(self):
        r"""

        References
        ----------
        Agresti, Alan; Coull, Brent A. (1998). "Approximate is better than 'exact' for interval estimation of binomial
            proportions". The American Statistician. http://users.stat.ufl.edu/~aa/articles/agresti_coull_1998.pdf

        Wikipedia contributors. (2018, July 14). Binomial proportion confidence interval.
            In Wikipedia, The Free Encyclopedia. Retrieved 00:40, August 15, 2018,
            from https://en.wikipedia.org/w/index.php?title=Binomial_proportion_confidence_interval&oldid=850256725

        """
        nbar = self.n + self.z ** 2

        p = (1 / nbar) * (self.x + self.z ** 2 / 2)

        bound = self.z * np.sqrt((p / nbar) * (1 - p))

        upper_bound, lower_bound = p + bound, p - bound

        agresti_coull_interval = {
            'probability of success': p,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

        return agresti_coull_interval

    def _arcsine_transform_interval(self):
        r"""

        References
        ----------
        Wikipedia contributors. (2018, July 14). Binomial proportion confidence interval.
            In Wikipedia, The Free Encyclopedia. Retrieved 00:40, August 15, 2018,
            from https://en.wikipedia.org/w/index.php?title=Binomial_proportion_confidence_interval&oldid=850256725

        """
        p = self.clopper_pearson_interval['probability of success']

        p_var = (p * (1 - p)) / self.n

        lower_bound = np.sin(np.arcsin(np.sqrt(p)) - (self.z / (2. * np.sqrt(self.n)))) ** 2
        upper_bound = np.sin(np.arcsin(np.sqrt(p)) + (self.z / (2. * np.sqrt(self.n)))) ** 2

        arcsine_transform_interval = {
            'probability of success': p,
            'probability variance': p_var,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

        return arcsine_transform_interval

    def _generate_test_summary(self):
        results = {
            'Number of Successes': self.x,
            'Number of Trials': self.n,
            'p-value': self.p_value,
            'alpha': self.alpha,
            'intervals': {
                'Clopper-Pearson': self.clopper_pearson_interval,
                'Wilson Score': self.wilson_score_interval,
                'Agresti-Coull': self.agresti_coull_interval,
                'Arcsine Transform': self.arcsine_transform_interval
            }
        }

        return results


class ChiSquareTest(object):
    r"""
    Performs the one-sample Chi-Square goodness-of-fit test.

    Parameters
    ----------

    Attributes
    ----------

    Notes
    -----

    Examples
    --------

    References
    ----------
    Weisstein, Eric W. "Chi-Squared Test." From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/Chi-SquaredTest.html

    Wikipedia contributors. (2018, July 5). Chi-squared test. In Wikipedia, The Free Encyclopedia. Retrieved 13:56,
        August 19, 2018, from https://en.wikipedia.org/w/index.php?title=Chi-squared_test&oldid=848986171

    """
    def __init__(self, observed, expected=None, continuity=True, degrees_freedom=1):

        if not isinstance(observed, np.ndarray):
            self.observed = np.array(observed)
        else:
            self.observed = observed

        if expected is None:
            obs_mean = np.mean(self.observed)
            self.expected = np.full_like(self.observed, obs_mean)

        else:
            if not isinstance(expected, np.ndarray):
                self.expected = np.array(expected)
            else:
                self.expected = expected

            if self.observed.shape[0] != self.expected.shape[0]:
                raise ValueError('number of observations must be of the same length as expected values.')

        self.degrees_of_freedom = degrees_freedom
        self.continuity_correction = continuity
        self.n = self.observed.shape[0]
        self.chi_square = self._chisquare_value()
        self.p_value = self._p_value()
        self.test_summary = {
            'chi-square': self.chi_square,
            'p-value': self.p_value,
            'degrees of freedom': self.degrees_of_freedom,
            'continuity correction': self.continuity_correction
        }

    def _chisquare_value(self):
        x2 = np.sum((np.absolute(self.observed - self.expected) - (0.5 * self.continuity_correction)) ** 2 /
                    self.expected)

        return x2

    def _p_value(self):
        pval = chi2.cdf(self.chi_square, self.degrees_of_freedom)

        return pval


class tTest(object):
    r"""
    Performs one and two-sample t-tests.

    Parameters
    ----------
    y1 : array-like
        One-dimensional array-like object (list, numpy array, pandas DataFrame or pandas Series) containing
        the observed sample values.
    y2 : array-like, optional
        One-dimensional array-like object (list, numpy array, pandas DataFrame or pandas Series) containing
        the observed sample values. Not necessary to include when performing one-sample t-tests.
    group : array-like, optional
        Optional group vector array denoting class membership. Cannot contain more than two unique groups
        and must be the same length as :code:`y1`.
    mu : float, optional
        True mean to test difference when performing a one-sample t-test.
    var_equal : bool, optional
        If True, the two samples are assumed to have equal variances and Student's t-test is performed.
        Defaults to False, which performs Welch's t-test for unequal sample variances.
    paired : bool, optional
        If True, performs a paired t-test.
    alternative : str, {'two-sided', 'greater', 'less'}
        Specifies the alternative hypothesis :math:`H_1`. Must be one of 'two-sided' (default), 'greater',
        or 'less'.
    alpha : float, default 0.05
        The alpha-level for computing the confidence intervals.

    Attributes
    ----------
    y1 : array-like
        First sample observation vector.
    y2 : array-like or None
        Second sample observation vector, if passed. Otherwise, :code:`None`.
    group : array-like or None
        The corresponding group vector denoting group sample membership. Will return :code:`None` if not passed.
    paired : bool
        If True, a paired t-test with the two sample observation vectors is performed.
    alternative : str, {'two-sided', 'greater', 'less'}
        Specifies the alternative hypothesis. Must be one of 'two-sided' (default), 'greater', or 'lesser'.
    mu : float
        Specifies the 'true' mean of the population being tested if a one-sample test is being performed.
    var_equal : bool
        If True, treats the sample observation vectors as having equal variances and the Studentized t-test is
        performed. Defaults to False, which treats the sample observation vectors as having unequal variances and
        Welch's t-test is performed.
    method : str
        String denoting the test performed.
    sample_statistics : dict
        Dictionary containing the pertinent statistics (mean, number of observations, variance) of the
        sample observations.
    parameter : float
        Degrees of freedom. If :code:`var_equal` is False, The Welch-Satterthwaite degrees of freedom approximation
        is used.
    t_statistic : float
        Computed t-statistic.
    p_value : float
        p-value of the computed t-statistic.
    confidence_interval : tuple
        Tuple of the low and high confidence interval.

    Raises
    ------
    ValueError
        If :code:`alternative` is not one of ('two-sided', 'greater', or 'lesser')
    ValueError
        If :code:`paired` is True and a second sample, :code:`y2` is not passed.
    ValueError
        If :code:`paired` is True and the number of sample observations in :code:`y1` and :code:`y2`
        are not equal.

    Notes
    -----
    Welch's t-test is an adaption of Student's t test and is more performant when the
    sample variances and size are unequal. The test still depends on the assumption of
    the underlying population distributions being normally distributed.

    Welch's t test is defined as:

    .. math::

        t = \frac{\bar{X_1} - \bar{X_2}}{\sqrt{\frac{s_{1}^{2}}{N_1} + \frac{s_{2}^{2}}{N_2}}}

    where:

    :math:`\bar{X}` is the sample mean, :math:`s^2` is the sample variance, :math:`n` is the sample size

    If the :code:`var_equal` argument is True, Student's t-test is used, which assumes the two samples
    have equal variance. The t statistic is computed as:

    .. math::

        t = \frac{\bar{X}_1 - \bar{X}_2}{s_p \sqrt{\frac{1}{n_1} + \frac{1}{n_2}}

    where:

    .. math::

        s_p = \sqrt{\frac{(n_1 - 1)s^2_{X_1} + (n_2 - 1)s^2_{X_2}}{n_1 + n_2 - 2}

    Examples
    --------
    Similar to other inference methods, there are generally two ways of performing a t-test. The first is to pass
    a group vector with the :code:`group` parameter and the corresponding observation vector as below.

    The data used in this example is a subset of the professor salary dataset found in Fox and
    Weisberg (2011).

    >>> professor_discipline = ['B', 'B', 'B', 'B', 'B',
    ...                         'A', 'A', 'A', 'A', 'A']
    >>> professor_salary = [139750, 173200, 79750, 11500, 141500,
    ...                     103450, 124750, 137000, 89565, 102580]
    >>> ttest = tTest(professor_salary, group=professor_discipline)
    >>> ttest.test_summary
    {'Sample 1 Mean': 111469.0,
     'Sample 2 Mean': 109140.0,
     'alternative': 'two-sided',
     'confidence interval': (-67873.67468585065, 72531.67468585065),
     'degrees of freedom': 4.698886994702439,
     'p-value': 0.9342936060799869,
     't-statistic': 0.08695024086399619,
     'test description': "Two-Sample Welch's t-test"}

    The other approach is to pass each group sample vector similar to the below.

    >>> sal_a = [139750, 173200, 79750, 11500, 141500]
    >>> sal_b = [103450, 124750, 137000, 89565, 102580]
    >>> ttest2 = tTest(sal_a, sal_b)
    >>> ttest2.test_summary
    {'Sample 1 Mean': 109140.0,
     'Sample 2 Mean': 111469.0,
     'alternative': 'two-sided',
     'confidence interval': (-72531.67468585065, 67873.67468585065),
     'degrees of freedom': 4.698886994702439,
     'p-value': 0.9342936060799869,
     't-statistic': -0.08695024086399619,
     'test description': "Two-Sample Welch's t-test"}

    References
    ----------
    Fox J. and Weisberg, S. (2011) An R Companion to Applied Regression, Second Edition Sage.

    Rencher, A. C., & Christensen, W. F. (2012). Methods of multivariate analysis (3rd Edition).

    Student's t-test. (2017, June 20). In Wikipedia, The Free Encyclopedia.
        From https://en.wikipedia.org/w/index.php?title=Student%27s_t-test&oldid=786562367

    """
    def __init__(self, y1, y2=None, group=None, mu=None, var_equal=False, paired=False,
                 alternative='two-sided', alpha=0.05):

        self.group = group
        self.paired = paired
        self.alpha = alpha

        if alternative not in ('two-sided', 'greater', 'less'):
            raise ValueError("alternative must be one of 'two-sided', 'greater', or 'lesser'")

        self.alternative = alternative

        if self.paired and y2 is None:
            raise ValueError('second sample is missing for paired test')

        self.mu = mu

        if var_equal:
            self.method = "Student's t-test"
            self.var_equal = True
        else:
            self.method = "Welch's t-test"
            self.var_equal = var_equal

        if self.paired:
            self.test_description = 'Paired t-test'
            self.y1 = self._paired(y1, y2)
            self._y1_summary_stat_name = 'Sample Difference'
            self.y2 = None
            self.sample_statistics = {self._y1_summary_stat_name: self._sample_stats(self.y1)}

        elif y2 is None and group is None:
            self.test_description = 'One-Sample t-test'
            self._y1_summary_stat_name = 'Sample 1'
            self.y1, self.y2 = y1, None
            self.sample_statistics = {self._y1_summary_stat_name: self._sample_stats(self.y1)}

        else:
            self.test_description = 'Two-Sample' + ' ' + self.method
            self._y1_summary_stat_name = 'Sample 1'

            if group is None:
                self.y1, self.y2 = y1, y2
            else:
                self.y1, self.y2 = self._split_groups(y1)

            self.sample_statistics = {self._y1_summary_stat_name: self._sample_stats(self.y1)}

            self.sample_statistics['Sample 2'] = self._sample_stats(self.y2)

        self.parameter = self._degrees_of_freedom()
        self.t_statistic = self._test_statistic()
        self.p_value = self._pvalue()
        self.confidence_interval = self._conf_int()
        self.test_summary = self._generate_result_summary()

    def _degrees_of_freedom(self):
        r"""
        Computes the degrees of freedom of one or two samples.

        Returns
        -------
        float
            the degrees of freedom

        Notes
        -----
        When Welch's t test is used, the Welch-Satterthwaite equation for approximating the degrees
        of freedom should be used and is defined as:

        .. math::

            \large v \approx \frac{\left(\frac{s_{1}^2}{N_1} +
            \frac{s_{2}^2}{N_2}\right)^2}{\frac{\left(\frac{s_1^2}{N_1^{2}}\right)^2}{v_1} +
            \frac{\left(\frac{s_2^2}{N_2^{2}}\right)^2}{v_2}}

        If the two samples are assumed to have equal variance, the degrees of freedoms become simply:

        .. math::

            v = n_1 + n_2 - 2

        In the case of one sample, the degrees of freedom are:

        .. math::

            v = n - 1

        References
        ----------
        Rencher, A. C., & Christensen, W. F. (2012). Methods of multivariate analysis (3rd Edition).

        Welch's t-test. (2017, June 16). In Wikipedia, The Free Encyclopedia.
            From https://en.wikipedia.org/w/index.php?title=Welch%27s_t-test&oldid=785961228

        """
        n1, s1 = self.sample_statistics[self._y1_summary_stat_name]['obs'], \
                 self.sample_statistics[self._y1_summary_stat_name]['variance']

        v1 = n1 - 1

        if self.y2 is not None:
            n2, s2 = self.sample_statistics['Sample 2']['obs'], \
                     self.sample_statistics['Sample 2']['variance']

            v2 = n2 - 1

            if self.var_equal:
                v = n1 + n2 - 2
            else:
                v = np.power((s1 / n1 + s2 / n2), 2) / (np.power((s1 / n1), 2) / v1 + np.power((s2 / n2), 2) / v2)

        else:
            v = v1

        return float(v)

    def _test_statistic(self):
        r"""
        Computes Student's t-statistic.

        Returns
        -------
        tval : float
            The calculated Student's t-statistic

        Notes
        -----
        The :math:`t`-statistic in Welch's test is defined as:

        .. math::

            t = \frac{\bar{X_1} - \bar{X_2}}{\sqrt{\frac{s_{1}^{2}}{N_1} + \frac{s_{2}^{2}}{N_2}}}

        where:

        :math:`\bar{X}` is the sample mean, :math:`s^2` is the sample variance, :math:`n` is the sample size

        If the :code:`var_equal` argument is True, Student's t-test is used, which assumes the two samples
        have equal variance. The :math:`t`-statistic is computed as:

        .. math::

            t = \frac{\bar{X}_1 - \bar{X}_2}{s_p \sqrt{\frac{1}{n_1} + \frac{1}{n_2}}

        where:

        .. math::

            s_p = \sqrt{\frac{(n_1 - 1)s^2_{X_1} + (n_2 - 1)s^2_{X_2}}{n_1 + n_2 - 2}

        References
        ----------
        Rencher, A. C., & Christensen, W. F. (2012). Methods of multivariate analysis (3rd Edition).

        Wikipedia contributors. (2018, June 7). Student's t-test. In Wikipedia, The Free Encyclopedia.
            From https://en.wikipedia.org/w/index.php?title=Student%27s_t-test&oldid=844823171

        Wikipedia contributors. (2018, June 4). Welch's t-test. In Wikipedia, The Free Encyclopedia.
            From https://en.wikipedia.org/w/index.php?title=Welch%27s_t-test&oldid=844375720

        """
        n1, s1, ybar1 = self.sample_statistics[self._y1_summary_stat_name]['obs'], \
                        self.sample_statistics[self._y1_summary_stat_name]['variance'], \
                        self.sample_statistics[self._y1_summary_stat_name]['mean']

        if self.y2 is not None:
            n2, s2, ybar2 = self.sample_statistics['Sample 2']['obs'], \
                            self.sample_statistics['Sample 2']['variance'], \
                            self.sample_statistics['Sample 2']['mean']

            if self.var_equal:
                sp = np.sqrt(((n1 - 1.) * s1 + (n2 - 1.) * s2) / (n1 + n2 - 2.))
                tval = float((ybar1 - ybar2) / (sp * np.sqrt(1. / n1 + 1. / n2)))
            else:
                tval = float((ybar1 - ybar2) / np.sqrt(s1 / n1 + s2 / n2))

        else:

            if self.mu is None:
                mu = 0.0
            else:
                mu = self.mu

            tval = float((ybar1 - mu) / np.sqrt(s1 / n1))

        return tval

    def _pvalue(self):
        r"""
        Returns the p-value.

        Returns
        -------
        p : float

        Notes
        -----
        The p-value is calculated by finding the probability that the critical value of :math:`t` is
        greater than the absolute value of the computed t statistic . This is known as the rejection
        region and can be written as:

        .. math::

             \left|t_{obs}\right| > t_{\alpha/2, n_1+n_2-2}

        The p-value is then found by plotting the Student's :math:`t` distribution and finding where
        the :math:`t`-statistic lands on the plot with the given degrees of freedom. Written formally:

        .. math::

            P(\left|t_{obs}\right|)

        References
        ----------
        Rencher, A. C., & Christensen, W. F. (2012). Methods of multivariate analysis (3rd Edition).

        """
        p = t.cdf(self.t_statistic, self.parameter)

        if self.alternative == 'two-sided':
            p *= 2.
        elif self.alternative == 'greater':
            p = 1 - p

        if 1.0 < p < 2.0:
            p = 2 - p

        if p == 2.0:
            p = np.finfo(float).eps

        return p

    def _conf_int(self):
        r"""
        Computes the confidence interval.

        Returns
        -------
        intervals : tuple
            Tuple containing the low and high confidence interval.

        Notes
        -----
        Confidence intervals are reported as a proportion, denoted by :math:`1 - \alpha`, which
        represents the ratio of intervals that would contain the population parameter if samples
        were redrawn and tested with the same procedure. A confidence level is the interval reported
        as a percentage, :math:`(1 - \alpha) * 100\%`. The width of the :math:`(1 - \alpha) * 100\%`
        interval has several dependencies:

        1. The confidence level. As :math:`1 - \alpha` increases, so does the width of the interval.
        2. As the sample size :math:`n` increases, the smaller the standard error and thus a narrower interval.
        3. If the standard deviation is large, then the interval will also be large.

        The computation of the intervals uses Welch's t-interval which extends the two-sample pooled
        t-interval for unequal population variances and sample sizes.

        .. math::

            \left(\bar{X_1} - \bar{X_2}\right) \pm t_{\alpha / 2, r} \sqrt{\frac{s_{x_1}^2}{n_1} + \frac{s_{x_2}^2}{n_2}}

        References
        ----------
        Rencher, A. C., & Christensen, W. F. (2012). Methods of multivariate analysis (3rd Edition).

        """
        xn, xvar, xbar = self.sample_statistics[self._y1_summary_stat_name]['obs'], \
                         self.sample_statistics[self._y1_summary_stat_name]['variance'], \
                         self.sample_statistics[self._y1_summary_stat_name]['mean']

        if self.y2 is not None:
            yn, yvar, ybar = self.sample_statistics['Sample 2']['obs'], \
                             self.sample_statistics['Sample 2']['variance'], \
                             self.sample_statistics['Sample 2']['mean']

            low_interval = (xbar - ybar) + t.ppf(self.alpha / 2., self.parameter) * np.sqrt(xvar / xn + yvar / yn)
            high_interval = (xbar - ybar) - t.ppf(self.alpha / 2., self.parameter) * np.sqrt(xvar / xn + yvar / yn)

        else:
            low_interval = xbar + 1.96 * np.sqrt(xvar / xn)
            high_interval = xbar - 1.96 * np.sqrt(xvar / xn)

        if self.alternative == 'greater':
            intervals = np.inf, float(high_interval)
        elif self.alternative == 'less':
            intervals = -np.inf, float(low_interval)
        else:
            intervals = float(low_interval), float(high_interval)

        return intervals

    def _generate_result_summary(self):
        r"""
        Returns a dictionary of the t-test results.

        Returns
        -------
        test_results : dict

        """
        test_results = {
            't-statistic': self.t_statistic,
            'p-value': self.p_value,
            'confidence interval': self.confidence_interval,
            'degrees of freedom': self.parameter,
            'alternative': self.alternative,
            'test description': self.test_description,
            self._y1_summary_stat_name + ' Mean': self.sample_statistics[self._y1_summary_stat_name]['mean']
        }

        if self.y2 is not None:
            test_results['Sample 2 Mean'] = self.sample_statistics['Sample 2']['mean']

        if self.mu is not None:
            test_results['mu'] = self.mu

        return test_results

    def _split_groups(self, x):
        if len(np.unique(self.group)) > 2:
            raise ValueError('there cannot be more than two groups')

        obs_matrix = npi.group_by(self.group, x)

        y1 = obs_matrix[1][0]
        self.sample_statistics = {'y1_sample_statistics': self._sample_stats(y1)}

        if len(obs_matrix[0]) == 2:
            y2 = obs_matrix[1][1]
            self.sample_statistics['y2_sample_statistics'] = self._sample_stats(y2)
        else:
            y2 = None

        return y1, y2

    @staticmethod
    def _paired(y1, y2):

        if len(y1) != len(y2):
            raise ValueError('paired samples must have the same number of observations')

        x = np.array(y1) - np.array(y2)

        return x

    @staticmethod
    def _sample_stats(sample_vector):
        sample_stats = {
            'obs': int(len(sample_vector)),
            'variance': float(np.var(sample_vector)),
            'mean': float(np.mean(sample_vector))
        }

        return sample_stats
