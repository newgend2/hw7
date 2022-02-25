import pandas as pd
import numpy as np
import decimal
from matplotlib import legend

""" RANDOM PROCESS CHECKERS """

def get_outcome_prob(n_tries, outcome, function, *args):
    outputs = {}
    for i in np.arange(n_tries):
        out = function(*args)
        if out not in outputs.keys():
            outputs[out] = 1
        else:
            outputs[out] += 1
    return outputs[out] / n_tries

def get_outcome_mean_std(n_tries, function, *args):
    outputs = []
    for i in np.arange(n_tries):
        out = function(*args)
        outputs.append(out)
    return np.mean(outputs), 3 * np.std(outputs)

'''
IMPORTANT: Function input parameter must return the sum_stats of an array.
'''
def get_sumstat_means_stds(n_times, function, *args):
    lists = [[], [], [], [], [], [], []]
    for i in range(n_times):
        out = function(*args)
        for idx, o in enumerate(out):
            lists[idx].append(o)
    return np.mean(lists, axis = 1), 3 * np.std(lists, axis = 1)


""" DATAFRAME CHECKERS """

"""
Gives statistical summary of input list
Returns a tuple containing:
(min, 25% quantile, median, 75% quantile, max, mean, standard deviation)

Best used to compare two different lists and see if they are the same without looping through every value.
"""
def sum_stats(inp):
    if type(inp) == list:
        inp = np.array(inp)
    inp = if_dt_return_int(inp)
    inp = inp[np.logical_not(np.isnan(inp))]
    m, qu, med = round(np.min(inp), 2), round(np.quantile(inp, 0.25), 2), round(np.quantile(inp, 0.5), 2)
    thr_qu, ma, mean = round(np.quantile(inp, 0.75), 2), round(np.max(inp), 2), round(np.mean(inp), 2)
    stand = float(round(decimal.Decimal(np.std(inp)), 2))
    return m, qu, med, thr_qu, ma, mean, stand


"""
"""
def if_dt_return_int(array):
    def timestamp_val(ts):
        return ts.value
    
    if type(array) == list or type(array) == pd.core.series.Series:
        array = np.array(array)
    if type(array[0]) == np.datetime64:
        return array.astype(int)
    elif  type(array[0]) == pd._libs.tslibs.timestamps.Timestamp:
        return np.array([ts.value for ts in array])
    else:
        return array


"""
Compares a list of values to a specified column in a given dataframe.
ONLY WORKS FOR NUMERICAL COLUMNS

Useful to check if the dataframe column was computed accurately.
"""
def check_array_vs_df_col(list_in, df, colname):
    return sum_stats(list_in) == sum_stats(df[colname])


"""
Checks if a given column in a given dataframe is sorted.
Can check for both asending and descending values.

Returns True if sorted, False otherwise.
"""
def check_numerical_col_is_sorted(df, colname, ascending = True):
    colvals = df[colname]
    diffs = np.diff(colvals)
    cumsum = np.cumsum(diffs)
    for val in cumsum:
        if ascending and val < 0:
            return False
        if not ascending and val > 0:
            return False
    if ascending and cumsum.max() == colvals[len(colvals) - 1] - colvals[0]:
        return True
    if not ascending and cumsum.min() == colvals[len(colvals) - 1] - colvals[0]:
        return True
    return False

"""

"""
def check_df_for_unique_values(df, column, *args):
    found_mismatch = False
    uniques = list(df[column].unique())
    for val in uniques:
        if val not in args:
            found_mismatch = True
    for arg in args:
        if arg not in uniques:
            found_mismatch = True
    return not found_mismatch


""" MATPLOTLIB PYPLOT CHECKERS """

"""
"""
def check_sumstats_for_all_lines(axes, expected_stats):
    stats = []
    for line in axes.lines:
        for axis in line.get_data():
            if len(axis) != 1:
                stats.append(sum_stats(if_dt_return_int(axis)))
    allclose = True
    for stat in stats:
        close_found = False
        for expected in expected_stats:
            if np.allclose(stat, expected):
                close_found = True
                print(f"Matched {stat}, {expected}")
                break
            else:
                print(f"Could not match {stat}, {expected}")
        if not close_found:
            allclose = False
            break
    print(stats, expected)
    return allclose



"""
Checks given axes and checks if it has a line plotted from the given columns in the given dataframe.

Returns true if the line is found, False otherwise.
"""
def check_axlines_for_df_data(axes, df, x_col, y_col):
    for line in axes.lines:
        data = line.get_data()
        if list(data[0]) == df[x_col].to_list() and list(data[1]) == df[y_col].to_list():
            return True
    else:
        return False
    
"""
Checks given axes and checks if it has a line plotted from the given columns in the given dataframe.

Returns true if the line is found, False otherwise.
"""
def check_axlines_for_data(axes, x_vals, y_vals):
    for line in axes.lines:
        data = line.get_data()
        if list(data[0]) == x_vals and list(data[1]) == y_vals:
            return True
    else:
        return False

    
"""
Checks given axes for given points.
Points should be paramaterized size 2 tuples separated by commas in *args.
First value in each tuple should be x value, second should be y value.

Returns True if all provided points are found on the axes, False otherwise.
"""
def check_graph_for_points(axes, *args):
    missing_points = False
    for arg in args:
        x, y = arg
        for line in axes.lines:
            data = line.get_data()
            if len(data[0]) != 1 or len(data[1]) != 1:
                continue
            if np.isclose(data[0], x) and np.isclose(data[1], y):
                break
        else:
            missing_points = True
    return not missing_points



"""
Checks if there is a vertical line on the provided axes.

Returns True if there is a vertical line, False otherwise.
"""
def axhline_check(axes):
    straight = False
    horizontal = False
    for line in axes.lines:
        data = line.get_data()
        if len(data[0]) == 2 and len(data[1]) == 2:
            straight = True
            if data[1][0] == data[1][1]:
                horizontal = True
    if not straight:
        raise IndexError("Graph did not contain a straight line")
    if not horizontal:
        raise ValueError("Straight line in graph was not horizontal")
    return True


"""
Checks if there is a horizontal line on the axes.
Also checks that the horizontal line is at the spcified value.

Returns True if there is a horizontal line and it is at the right value, False otherwise.
"""
def axhline_value_check(axes, value):
    straight = False
    horizontal = False
    correct_value = False
    for line in axes.lines:
        data = line.get_data()
        if len(data[0]) == 2 and len(data[1]) == 2:
            straight = True
            if data[1][0] == data[1][1]:
                horizontal = True
                if data[1][0] == value:
                    correct_value = True
    if not straight:
        raise IndexError("Graph did not contain a straight line")
    if not horizontal:
        raise ValueError("Straight line in graph was not horizontal")
    if not correct_value:
        raise ValueError("Horizontal line was not graphed at correct y value")
    return True

"""
Checks if there is a vertical line on the axes.
Also checks that the vertical line is at the spcified value.

Returns True if there is a vertical line and it is at the right value, False otherwise.
"""
def axvline_value_check(axes, value):
    straight = False
    vertical = False
    correct_value = False
    for line in axes.lines:
        data = line.get_data()
        if len(data[0]) == 2 and len(data[1]) == 2:
            straight = True
            if data[0][0] == data[0][1]:
                vertical = True
                if np.isclose(data[0][0], value):
                    correct_value = True
    if not straight:
        raise IndexError("Graph did not contain a straight line")
    if not vertical:
        raise ValueError("Straight line in graph was not vertical")
    if not correct_value:
        raise ValueError("Horizontal line was not graphed at correct y value")
    return True


"""
Checks if provided axes contain a legend or legend substitute (text).
If legend is not found, checks that number of text objects matches provided integer.

Returns true if legend or text-legend found, False otherwise.
"""
def check_legend(axes, num_text):
    return type(axes.get_legend()) == legend.Legend or len(axes.texts) == num_text

def check_legibility(axes):
    item_list = [axes.get_xlabel(), axes.get_ylabel()]
    if '' not in item_list:
        return True
    else:
        return False

"""

"""
def check_text_coords(ax, expected_text, x, y):
    for text in ax.texts:
        if text.get_text() == expected_text:
            new_x = text._x.values[0] if type(text._x) == pd.core.series.Series else text._x
            new_y = text._y.values[0] if type(text._y) == pd.core.series.Series else text._y
            if new_x == x and new_y == y:
                return True
            else:
                raise ValueError(f"Text {expected_text} did not have expected x and y values")
                return False
    else:
        raise ValueError(f"Could not find text object with string {expected_text}")
        return False    