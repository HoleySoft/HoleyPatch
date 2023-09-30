
import numpy as np
from scipy.signal import savgol_filter


class StepWiseEvents:
    def __init__(self):
        pass

    def filter_consecutive(self, y_data, level_start, level_end, Z_sign=6):
        # Add the first start time, which must be true
        level_start_sign = [level_start[0]]
        level_end_sign = []
        for c in range(len(level_start) - 1):
            # Determine significance on the 50% percentile
            idx_1 = int((level_end[c] - level_start[c]) / 4)
            idx_2 = int((level_end[c + 1] - level_start[c + 1]) / 4)

            # Extract the 25-75% of data, exclude the extremes
            signal_1 = np.sort(y_data[level_start[c]:level_end[c]])[idx_1:-idx_1]
            signal_2 = np.sort(y_data[level_start[c + 1]:level_end[c + 1]])[idx_2:-idx_2]

            # Calulculate the Z-statistics
            x1 = np.mean(signal_1)
            x2 = np.mean(signal_2)
            var1 = np.std(signal_1) ** 2
            var2 = np.std(signal_2) ** 2
            Z = abs(x1 - x2) / np.sqrt(var1 + var2)

            # Only add the end time and start time if Z stats are significant
            if all([Z >= Z_sign, Z == Z]):
                level_end_sign += [level_end[c]]
                level_start_sign += [level_start[c + 1]]
        # Add the final end time, which must be true
        level_end_sign += [level_end[-1]]

        # Return the filtered start and end times
        return level_start_sign, level_end_sign

    def get_event_times(self, y_data, data, t0=0, t1=-1, dwelltime=0.01, sigma=0.5, savgol_n=11, savgol_order=2, Z_sign=2):
        # Determine the derivative squared of the data based on second-order Savitsky-Golay (SavGol)
        data_savgol = np.sqrt(savgol_filter(y_data[t0:t1], savgol_n, savgol_order, deriv=1) ** 2)

        # Determine the cut-off leveraged by the square
        cutoff = np.std(data_savgol) * sigma

        # Determine all indices where the SavGol
        a = np.where(data_savgol > cutoff)[0]
        a = [i for i in a if i != 0]
        idx = [i for c, i in enumerate(a) if i - 1 not in a]
        level_start = [0] + idx
        level_end = [i - 1 for i in idx] + [len(data_savgol)]

        idx = np.where(np.array(level_end) - np.array(level_start) > dwelltime * data.sampling_frequency)[0]
        level_start = [level_start[i] for i in idx]
        level_end = [i - 1 for i in level_start] + [len(data_savgol)]
        level_start = [0] + level_start

        k = -1
        i = 0

        while k != len(level_start):
            # k = len(level_start_sign)
            level_start, level_end = self.filter_consecutive(y_data, level_start, level_end, Z_sign=Z_sign)
            i += 1
            if i > 10:
                k = len(level_start)
        lse = []
        lee = []
        for ls, le in zip(level_start, level_end):
            lse += [ls + t0]
            lee += [le + t0]
        return lse, lee
