import pytest
import hypy
import pandas as pd
import numpy as np
import os
from scipy.stats import t


@pytest.fixture
def test_data():
    datapath = os.path.dirname(os.path.abspath(__file__))
    salaries = pd.read_csv(os.path.join(datapath, 'test_data/Salaries.csv'))

    return salaries


def test_two_sample_welch_test(test_data):
    sal_a = test_data.loc[test_data['discipline'] == 'A']['salary']
    sal_b = test_data.loc[test_data['discipline'] == 'B']['salary']

    ttest = hypy.t_test(y1=sal_a, y2=sal_b)

    test_summary = ttest.summary()

    np.testing.assert_almost_equal(test_summary['Sample 1 Mean'], np.mean(sal_a))
    np.testing.assert_almost_equal(test_summary['Sample 2 Mean'], np.mean(sal_b))
    np.testing.assert_almost_equal(test_summary['t-statistic'], -3.1386989278486013)
    np.testing.assert_almost_equal(test_summary['degrees of freedom'], 377.89897288941387)
    np.testing.assert_almost_equal(test_summary['p-value'], t.cdf(test_summary['t-statistic'],
                                                                  test_summary['degrees of freedom']) * 2)

    assert test_summary['alternative'] == 'two-sided'
    assert test_summary['test description'] == "Two-Sample Welch's t-test"


def test_two_sample_students_test(test_data):
    sal_a = test_data.loc[test_data['discipline'] == 'A']['salary']
    sal_b = test_data.loc[test_data['discipline'] == 'B']['salary']

    ttest = hypy.t_test(y1=sal_a, y2=sal_b, var_equal=True)

    test_summary = ttest.summary()

    np.testing.assert_almost_equal(test_summary['Sample 1 Mean'], np.mean(sal_a))
    np.testing.assert_almost_equal(test_summary['Sample 2 Mean'], np.mean(sal_b))
    np.testing.assert_almost_equal(test_summary['t-statistic'], -3.1485647713976195)
    np.testing.assert_almost_equal(test_summary['p-value'], t.cdf(test_summary['t-statistic'],
                                                                  test_summary['degrees of freedom']) * 2)

    assert test_summary['alternative'] == 'two-sided'
    assert test_summary['test description'] == "Two-Sample Student's t-test"

    assert len(sal_a) + len(sal_b) - 2 == test_summary['degrees of freedom']


def test_one_sample_test(test_data):
    sal_a = test_data.loc[test_data['discipline'] == 'A']['salary']

    ttest = hypy.t_test(y1=sal_a)

    test_summary = ttest.summary()

    np.testing.assert_almost_equal(test_summary['Sample 1 Mean'], np.mean(sal_a))
    np.testing.assert_almost_equal(test_summary['t-statistic'], 47.95382017797468)
    np.testing.assert_almost_equal(test_summary['p-value'], 2.220446049250313e-16)

    assert test_summary['alternative'] == 'two-sided'
    assert test_summary['test description'] == 'One-Sample t-test'

    assert len(sal_a) - 1 == test_summary['degrees of freedom']


def test_paired_sample_test(test_data):
    sal_a = test_data.loc[test_data['discipline'] == 'A']['salary']
    sal_b = test_data.loc[test_data['discipline'] == 'B']['salary']
    sal_b2 = sal_b[0:len(sal_a)]

    ttest = hypy.t_test(y1=sal_a, y2=sal_b2, paired=True)

    test_summary = ttest.summary()

    np.testing.assert_almost_equal(test_summary['Sample Difference Mean'], np.mean(np.array(sal_a) - np.array(sal_b2)))
    np.testing.assert_almost_equal(test_summary['t-statistic'], -2.3158121700626406)
    np.testing.assert_almost_equal(test_summary['p-value'], t.cdf(test_summary['t-statistic'],
                                                                  test_summary['degrees of freedom']) * 2)

    assert test_summary['alternative'] == 'two-sided'
    assert test_summary['test description'] == 'Paired t-test'

    assert len(sal_a) - 1 == test_summary['degrees of freedom']


def test_ttest_exceptions(test_data):
    sal_a = test_data.loc[test_data['discipline'] == 'A']['salary']
    sal_b = test_data.loc[test_data['discipline'] == 'B']['salary']

    with pytest.raises(ValueError):
        hypy.t_test(y1=sal_a, paired=True)

    with pytest.raises(ValueError):
        hypy.t_test(y1=sal_a, y2=sal_b, paired=True)

    with pytest.raises(ValueError):
        hypy.t_test(sal_a, sal_b, alternative='asdh')
