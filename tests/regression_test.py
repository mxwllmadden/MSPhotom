from MSPhotom.data import MSPData
import numpy as np
import random
import MSPhotom.analysis.regression as reg
import numpy as np
import pickle
import pandas as pd
#hey world
class FakeMSPData:
    def __init__(self):
        self.traces_by_run_signal_trial = {
            'run1': {
                'sig_region1_ch0': self.generate_signal_with_peaks(10, 100, 0.1, 2),  # Trials as columns
                'sig_region1_ch1': self.generate_residuals_with_unique_peaks(10, 100, 0.1, 3),  # Trials as columns
                'sig_corrsig_ch0': self.generate_signal_with_peaks(10, 100, 0.1, 2),  # Trials as columns
                'sig_corrsig_ch1': self.generate_signal_with_peaks(10, 100, 0.1, 3),  # Trials as columns
            }
        }

    def generate_signal_with_peaks(self, num_trials, num_points, noise_level, peak_height):
        time = np.arange(num_points)
        base_signal = np.sin(4 * np.pi * time / (num_points / 5))  # Sinusoidal signal
        base_signal = np.expand_dims(base_signal, axis=1)  # Shape: (num_points, 1)
        signal = base_signal + np.random.normal(0, noise_level,
                                                size=(num_points, num_trials))  # Shape: (num_points, num_trials)
        signal[::10, :] += peak_height  # Add peaks every 10th point
        return signal

    def generate_residuals_with_unique_peaks(self, num_trials, num_points, noise_level, peak_height):
        time = np.arange(num_points)
        base_signal = np.sin(4 * np.pi * time / (num_points / 5))  # Sinusoidal signal
        base_signal = np.expand_dims(base_signal, axis=1)  # Reshape to (num_points, 1)
        residuals = base_signal + np.random.normal(0, noise_level,
                                                   size=(num_points, num_trials))  # Shape: (num_points, num_trials)
        residuals[::10, :] += peak_height  # Add peaks every 5th point
        return residuals

def save_fake_data(filename):
    data = FakeMSPData()
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def save_to_csv(data):
    for run, signals in data.traces_by_run_signal_trial.items():
        for signal_name, signal_data in signals.items():
            # Convert numpy array to pandas DataFrame
            df = pd.DataFrame(signal_data)
            # Define the CSV filename
            csv_filename = f"{run}_{signal_name}.csv"
            # Save to CSV
            df.to_csv(csv_filename, index=False)
            print(f"Saved {signal_name} to {csv_filename}")

if __name__ == "__main__":
    # First, create and save the fake data
    save_fake_data('fake_data_with_peaks.pkl')

    # Now, load the saved data
    with open('fake_data_with_peaks.pkl', 'rb') as f:
        loaded_data = pickle.load(f)

    # Print keys to verify
    print(loaded_data.traces_by_run_signal_trial.keys())

    # Save the data to CSV files
    save_to_csv(loaded_data)

    # If you have a regression_main function, call it
    # binsize = 1
    # all_regressed_signals = regression_main(loaded_data)
