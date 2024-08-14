"""
Perform Studentized Residual Regression from organized trace data
"""
from typing import Dict
import numpy as np
from MSPhotom.data import MSPData


def regression_main(data: MSPData, controller=None):
    """
    Perform regression on the data traces organized by runs and return regressed signals.

    Args:
        data (MSPData): The data object containing traces organized by runs.
        controller (optional): Controller object to update data if provided.

    Returns:
        Dict: A dictionary containing dictionaries of regressed signals for each run.
    """
    # Initializes the main dictionaries
    regressed_traces_by_run_signal_trial = {}
    corrsig_reg_results = {}

    # Extracts the data we need
    traces_by_run = data.traces_by_run_signal_trial
    binsize = data.bin_size
    # Iterate through each run in the nested dictionary
    for run_key, run_dict in traces_by_run.items():
        # Assign the nested dictionary (traces within each run) to `traces`
        traces = run_dict
        region_names = [key.split('_')[1] for key in traces.keys()
                        if key.split('_')[1] != 'corrsig']

        channel_names = [key.split('_')[2] for key in traces.keys()]

        channel_names_ch0_removed = [key.split('_')[2] for key in traces.keys()
                                     if key.split('_')[2] != 'ch0']

        # Removes duplicate channel and region names
        unique_channels = unique_list(channel_names)
        unique_regions = unique_list(region_names)
        unique_channels_ch0_removed = unique_list(channel_names_ch0_removed)

        # Does the regression and outputs regression dictionary
        regressed_signals, corrsig_reg_results = regression_func(traces, binsize, unique_channels, unique_regions,
                                                                 unique_channels_ch0_removed)
        regressed_traces_by_run_signal_trial[run_key] = regressed_signals
        corrsig_reg_results[run_key] = corrsig_reg_results

    # Temp data updating
    data.regressed_traces_by_run_signal_trial = regressed_traces_by_run_signal_trial
    data.corrsig_reg_results = corrsig_reg_results

    if controller is not None:
        controller.view.update_state('RG - Regression Done Ready to Graph')
        controller.view.regression_tab.runprog['value'] = 100


def regression_func(traces, binsize, unique_channels, unique_regions, unique_channels_ch0_removed):
    """
    Perform regression analysis on traces to remove correction fibers and channel 0.

    Parameters
    ----------
    traces : dict
        Dictionary of traces keyed by signal names.

    Returns
    -------
    dict
        Dictionary containing residuals for each region and channel combination.
    """

    # Initializes blank dictionaries to be filled by regression
    regions_correction_fiber_regressed_b = {}
    regions_correction_fiber_regressed_b_r = {}
    region_residuals_ch0_regressed = {}
    corrsig_reg_results = {}
    # This first for loop regresses the correction fiber out
    for channel in unique_channels:
        # Assigns the control trace
        control_trace = traces[f'sig_corrsig_{channel}']
        # Transposes the array to have trials as columns instead of rows
        control_trace = np.transpose(control_trace)
        # bins the control trace
        control_trace_b, control_trace_b_r = bin_trials(control_trace,
                                                        binsize)

        # For each unique region, the correction fiber is regressed out of the binned traces
        for region in unique_regions:
            # Assigns the target trace for regression
            target_trace = traces[f'sig_{region}_{channel}']
            target_trace = np.transpose(target_trace)
            # Bins the target trace by binsize
            # _b = binned & _r = remainder trials
            target_trace_b, target_trace_b_r = bin_trials(
                target_trace, binsize)
            # This Calculates the studentized residuals which regresses the correction fiber out
            res_studentized_b = calculate_studentized_residuals(
                control_trace_b, target_trace_b)
            res_studentized_b_r = calculate_studentized_residuals(
                control_trace_b_r, target_trace_b_r)

            res_studentized_debinned = debin_me(res_studentized_b, res_studentized_b_r, binsize)
            corrsig_reg_results[f'{region}_{channel}'] = res_studentized_debinned
            # Saves the studentized residuals to a dictionary for further regression
            regions_correction_fiber_regressed_b[f'{region}_{channel}_b'] = res_studentized_b
            regions_correction_fiber_regressed_b_r[f'{region}_{channel}_b_r'] = res_studentized_b_r

    # This for loop regresses ch0 out to output residuals for each region by channel
    for region in unique_regions:
        # Assigns ch0 as the control channel to be regressed out
        control_channel_b = regions_correction_fiber_regressed_b[f'{region}_ch0_b']
        control_channel_b_r = regions_correction_fiber_regressed_b_r[f'{region}_ch0_b_r']

        for channel in unique_channels_ch0_removed:
            # Identifies the target channel for regression
            target_channel_b = regions_correction_fiber_regressed_b[f'{region}_{channel}_b']
            target_channel_b_r = regions_correction_fiber_regressed_b_r[f'{region}_{channel}_b_r']
            # Regresses the control channel from the target channel
            res_studentized_b = calculate_studentized_residuals(
                control_channel_b, target_channel_b)
            res_studentized_b_r = calculate_studentized_residuals(
                control_channel_b_r, target_channel_b_r)
            # Debins the residuals to create a unified dataset
            debinned_region_residuals = debin_me(res_studentized_b, res_studentized_b_r, binsize)

            # Saves the output residuals into a dictionary
            region_residuals_ch0_regressed[f'{region}_{channel}'] = debinned_region_residuals

    return region_residuals_ch0_regressed, corrsig_reg_results


def unique_list(iterable):
    """
    Return unique elements from an iterable while preserving order.

    Parameters
    ----------
    iterable : iterable
        Iterable object to extract unique elements from.

    Returns
    -------
    list
        List of unique elements in the same order as first encountered.
    """
    new_list = []
    for obj in iterable:
        if obj not in new_list:
            new_list.append(obj)
    return new_list


def bin_trials(signal: np.ndarray, binsize):
    """
    Bin trials of a signal into groups for noise reduction.

    Parameters
    ----------
    signal : numpy.ndarray
        Array of signals where trials are columns.
    binsize : int
        Number of trials to bin together.

    Returns
    -------
    binned_signal : numpy.ndarray
        array containing binned signal.
    binned_remainder : numpy.ndarray
        array containing remainder trial signals.
    """
    # Take an arbitrary amount of trials and bin them together for less noisy processing
    match signal.shape:
        case (trial_length, num_trials):
            pass  # num_trials is already assigned
        case (trial_length, ):
            num_trials = 1
            binned_signal = signal[:, np.newaxis]
            return binned_signal, None

    # Calculates new amount of columns for reshaping the binned data
    num_binned_columns = num_trials // binsize
    remainder_columns = num_trials % binsize

    # Calculates the number of rows in the reshaped array
    trimmed_signal_length = binsize * num_binned_columns

    # Initializes new arrays to be reshaped
    trimmed_signal = signal[:, :trimmed_signal_length]
    signal_remainder = signal[:, trimmed_signal_length:]

    # Reshapes the arrays into properly binned data with the remaining trials in a new array
    if remainder_columns == 0:
        binned_signal = trimmed_signal.reshape(
            (binsize * trial_length, num_binned_columns), order='F')
        return binned_signal, None

    # This step confirms the arrays are the right size
    binned_signal = trimmed_signal.reshape(
        (binsize * trial_length, num_binned_columns), order='F')
    binned_remainder = signal_remainder.reshape(
        (remainder_columns * trial_length, 1), order='F')

    return binned_signal, binned_remainder


def calculate_studentized_residuals(X, Y):
    # This logic is here to quickly exit the function if there is no binned remainder
    """
    This Function calculates internally studentized residuals and externally
    (deleted) studentized residuals.

    This function has also been checked against the statsmodels package 0.14.0.
    Below are some useful links to understand studentization:
    Course : https://online.stat.psu.edu/stat501/lesson/11/11.4
    Math-works documentation : https://www.mathworks.com/help/stats/residuals.html
    My guide(w/alt code) :
        https://docs.google.com/document/d/1jdNCPeF1ypVtrNURi7vPDkrronKRizYWAypq6DhHYMk/edit?usp=sharing

    Parameters
    ----------
    X (numpy.ndarray): an array with columns being trails(binned) or to be regressed out
    Y (numpy.ndarray) : The dependent variable array
    Returns
    -------
    Studentized Residuals (numpy.ndarray) :
        The residuals divided by an estimator of their error to standardize them on a z-score scale
    """
    # This logic is here to skip None type objects getting through
    try:
        X.shape
    except AttributeError:
        return None
    # Logic is here to extract num_trials from a 1 and 2 dimensional array
    match X.shape:
        case (trial_length, num_trials):
            pass  # num_trials is already assigned
        case (trial_length, ):
            num_trials = 1

    # Initializes Blank arrays
    studentized_residuals = np.full(Y.shape, np.nan, dtype=np.float64)
    internally_studentized_residuals = np.full(Y.shape, np.nan, dtype=np.float64)
    # For loop to go trial by trial
    for i in range(num_trials):
        # Do calculations using valid values(not nans)
        valid_mask = ~np.isnan(X[:, i]) & ~np.isnan(Y[:, i])
        # Masks are used to ensure data does not lose its position when removing nans
        X_valid = X[valid_mask, i]
        Y_valid = Y[valid_mask, i]

        # Calculate means for further calculations
        mean_X = np.nanmean(X[:, i])
        mean_Y = np.nanmean(Y[:, i])

        # This calculates the residuals(not studentized yet)
        n = len(X_valid)
        diff_mean_sqr = np.dot((X_valid - mean_X), (X_valid - mean_X))
        beta1 = np.dot((X_valid - mean_X), (Y_valid - mean_Y)) / diff_mean_sqr
        beta0 = mean_Y - beta1 * mean_X
        y_hat = beta0 + beta1 * X_valid
        residuals_valid = Y_valid - y_hat

        # Calculates the leverage value
        h_ii = (X_valid - mean_X) ** 2 / diff_mean_sqr + (1 / n)

        # Calculates the internally studentized MSE(current value included)
        MSE = sum((Y_valid - y_hat) ** 2) / (n - 2)
        SE_regression = ((MSE * (1 - h_ii)) ** 0.5)

        # np.where logic is to ensure residuals get encoded as zero instead of 
        # nans if sum((Y_valid - y_hat) = 0
        internally_studentized_residuals_valid = np.where(SE_regression != 0, residuals_valid / SE_regression, 0)
        # Returns internally studentized residuals to their correct location using the valid mask
        internally_studentized_residuals[valid_mask, i] = internally_studentized_residuals_valid

        # Converts internally studentized residuals to externally studentized residuals Note: Formula found in links
        r = internally_studentized_residuals_valid
        n = len(r)
        studentized_residuals_valid = [r_i * np.sqrt((n - 2 - 1) / (n - 2 - r_i ** 2)) for r_i in r]
        studentized_residuals[valid_mask, i] = studentized_residuals_valid

    return studentized_residuals.flatten() if studentized_residuals.ndim == 1 else studentized_residuals


def debin_me(binned_signal, binned_signal_remainder, binsize):
    """
    Debin binned signals back to the original structure.

    Parameters
    ----------
    binned_signal : numpy.ndarray
        Binned signal array.
    binned_signal_remainder : numpy.ndarray
        Remainder of binned signals.
    binsize : int
        Number of trials originally binned together.

    Returns
    -------
    numpy.ndarray
        Debinned signal array.
    """
    # This converts the binned signals back to initial array structure
    # Logic is here to extract num_bin_trials from a 1 and 2 dimensional array
    match binned_signal.shape:
        case (bin_length, num_bin_trials):
            pass  # num_bin_trials is already assigned
        case (bin_length, ):
            num_bin_trials = 1
            pass

    # Calculations to get the correct array sizes to ensure proper concatenation
    trial_length = bin_length // binsize
    total_trials = num_bin_trials * binsize

    # Reshapes the arrays to have equal row lengths equal to the initial trial lengths
    net_res_reshaped = binned_signal.reshape(
        (trial_length, total_trials), order='F')
    if binned_signal_remainder is None:
        return net_res_reshaped

    # More reshaping math
    r_bin_length = binned_signal_remainder.shape[0]
    r_total_trials = r_bin_length // trial_length

    # Combines the remainder array back into the primary array.
    net_res_reshaped_r = binned_signal_remainder.reshape(
        (trial_length, r_total_trials), order='F')
    net_res_debinned = np.concatenate(
        [net_res_reshaped, net_res_reshaped_r], axis=1)
    return net_res_debinned
