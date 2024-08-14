from MSPhotom.data import MSPData
import numpy as np
import random
import MSPhotom.analysis.regression as reg
import pickle
import pandas as pd

class FakeData(MSPData):
    def __init__(self):
        super().__init__()
        v_laser_fluct = self.sig_s(6000, 4)
        b_laser_fluct= self.sig_s(6000, 5)
        v_noise = self.randpeaks(6000, 400)
        true_sig = self.randpeaks(6000, 200)
        self.true_sig = true_sig
        self.v_noise = v_noise
        self.traces_by_run_signal_trial = {
            'run1' : {
                'sig_region1_ch0': (v_laser_fluct + v_noise),
                'sig_region1_ch1': (b_laser_fluct + v_noise+true_sig),
                'sig_corrsig_ch0': v_laser_fluct,
                'sig_corrsig_ch1': b_laser_fluct,
            }
        }
    @staticmethod
    def sig_s(num_points, const):
        time = np.arange(num_points)
        return np.sin(const * np.pi * time / (num_points))

    @staticmethod
    def randpeaks(num_points, num_peaks):
        time = np.zeros(num_points)
        for i in range(num_peaks):
            time[random.randint(0, num_points-1)] = 10
        return time

def save_fake_data(filename , data):
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

def save_vnoise_true(data : FakeData):
    df1 = pd.DataFrame(data.v_noise)
    df2 = pd.DataFrame(data.true_sig)

    df1.to_csv("v_noise.csv", index=False)
    df2.to_csv("true_sig.csv", index=False)
    #
    # def save_to_csv(data):
    #     for run, signals in data.regressed_signals.items():
    #         for signal_name, signal_data in signals.items():
    #             # Convert numpy array to pandas DataFrame
    #             df = pd.DataFrame(signal_data)
    #             # Define the CSV filename
    #             csv_filename = f"{run}_{signal_name}.csv"
    #             # Save to CSV
    #             df.to_csv(csv_filename, index=False)
    #             print(f"Saved {signal_name} to {csv_filename}")

binsize = 1
if __name__ == '__main__':
    f_dat = FakeData()
    out_trace = reg.regression_main(f_dat)

    save_fake_data('f_dat.pkl', f_dat)

    save_vnoise_true(f_dat)

    #
    # with open('output_trace.pkl', 'rb') as f:
    #     loaded_data = pickle.load(f)
    #
    # # Print keys to verify
    # print(loaded_data.traces_by_run_signal_trial.keys())
    #
    # # Save the data to CSV files
    # reg.save_list_to_csv(loaded_data, 'regressed1')
