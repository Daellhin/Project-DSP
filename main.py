from math import *

import matplotlib.pyplot as plt
import scipy.fftpack as fftp
import scipy.io as sio
import scipy.signal as sig
from numpy import *
from scipy import *


# -- Bepalen reistijden van paden --
def channel2APDP(original_data: ndarray):
    """
    APDP: Averaged Power Delay Profile
    Data in form of: freq_tonen x positions x measurements
    """
    data = transpose(original_data, (1, 2, 0))
    data = reshape(data, (25, 100, 200))

    ifft_amplitude = [
        [abs(fftp.ifft(meas)) for meas in arr] for arr in data
    ]  # Hier moeten we ook nog eens een venster rond proberen zetten

    ifft_amplitude = transpose(ifft_amplitude, (0, 2, 1))
    ifft_amplitude = reshape(ifft_amplitude, (25, 200, 100))

    power = [
        [
            [measurement * measurement for measurement in freq_tonen]
            for freq_tonen in positions
        ]
        for positions in ifft_amplitude
    ]

    avg_power = [[mean(power_values) for power_values in pos] for pos in power]

    return avg_power

    # Uit de practica weet je nog dat de afstand tussen de opeenvolgende tijdssamples (∆T = 1/fS )  --> Tot 3Ghz dus Fs=6Ghz?
    # bepaalde wat de range van de samples in het frequentiedomein was (0 tot fS ) en hun
    # onderlinge afstand of frequentieresolutie (fS /N). Maak de analogie en denk na over de
    # range van de nu bekomen samples in het tijdsdomein (of hier delaydomein), welke delay
    # stelt elk sample voor (wat is de tijdsresolutie) en hoe linkt dit aan de afstand tussen de
    # opeenvolgende frequentietonen en aan de bandbreedte van het signaal?


def calculate_delays(APDPs: ndarray):
    """
    Returns list of two largest local maxima
    """
    delays = list()
    for APDP in APDPs:
        peaks, _ = sig.find_peaks(APDP, height=0)
        max2peaks = sorted(peaks, key=lambda x: APDP[x], reverse=True)[:2]
        delays.append(max2peaks)
    return delays


# -- Locatiebepaling --
def calculate_location(tau0: number, tau1=number):
    """
    tau0: reistijd direct propagatiepad
    tau1: reistijd gereflecteerde pad
    """
    return (0.0, 0.0)


def main():
    dataset_file = sio.loadmat("./Dataset_1.mat")
    data: ndarray = dataset_file["H"]
    print(type(data))

    apdps = channel2APDP(data)
    delays = calculate_delays(apdps)

    apdp = array(apdps[0])
    delay = delays[0]

    # Plot the impulse response and mark the peaks
    plt.figure(figsize=(8, 6))
    plt.plot(apdp)
    plt.plot(delay, apdp[delay], "x", label="Peaks", color="red")
    plt.xlabel("Index")
    plt.ylabel("Amplitude")
    plt.title("Impulse Response with Peaks")
    plt.legend()
    plt.grid(True)
    plt.show()


main()
