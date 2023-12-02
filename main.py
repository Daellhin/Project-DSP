from math import *

import matplotlib.pyplot as plt
import scipy.fftpack as fftp
import scipy.io as sio
import scipy.signal as sig
import scipy.constants as consts
from numpy import *
from scipy import *


# -- Tests --
def plot_apdp_with_delay(apdp, delay1):
    """
    Plots the impulse response and marks the peaks
    """
    delay = [int(delay // 5e-10) for delay in delay1]
    plt.figure(figsize=(8, 6))
    plt.plot(apdp)
    plt.plot(delay, apdp[delay], "x", label="Peaks", color="red")
    plt.xlabel("Index")
    plt.ylabel("Amplitude")
    plt.title("Impulse Response with Peaks")
    plt.yscale('log')
    plt.legend()
    plt.grid(True)


# -- Bepalen reistijden van paden --
def channel2APDP(original_data: ndarray):
    """
    APDP: Averaged Power Delay Profile
    Data in form of: freq_tonen(200) x positions(25) x measurements(100)
    """
    data = transpose(original_data, (1, 2, 0))
    data = reshape(data, (25, 100, 200))
    # Data in nieuwe vorm: positions(25) x measurements(100) x freq_tonen(200)

    # TODO venster rond zetten
    ifft_amplitude = [[abs(fftp.ifft(meas)) for meas in arr] for arr in data]

    ifft_amplitude = transpose(ifft_amplitude, (0, 2, 1))
    ifft_amplitude = reshape(ifft_amplitude, (25, 200, 100))
    # Data in nieuwe vorm: positions(25) x freq_tonen(200) x measurements(100)

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
    Returns list of Tau1 and Tau2 Pairs
    """
    # fS = 1/Δt  -->  T = 1/Δf  -->  Δt = T / N = 1 / (Δf*N) = 10e-7s/200 = 5e-10 s
    fS = 5e-10

    delays = list()
    for APDP in APDPs:
        peakIndexes, _ = sig.find_peaks(APDP)
        max2peakIndexes = sorted(peakIndexes, key=lambda x: APDP[x], reverse=True)[:2]
        max2Delays = [peakIndex * fS for peakIndex in max2peakIndexes]
        delays.append(max2Delays)

    return delays


# -- Locatiebepaling --
def calculate_location(tau0: float, tau1: float):
    """
    tau0: reistijd direct propagatiepad
    tau1: reistijd gereflecteerde pad

    Coördinaten basisstation: (xB, yB) = (0m, 1m)
    """
    # print(tau0 < tau1, f"{tau0}<{tau1}")

    distance0 = tau0 * consts.speed_of_light
    distance1 = tau1 * consts.speed_of_light

    # Zoek positief y snijpunt van cirkels, en coresponderend x punt
    y = -(distance0**2 - distance1**2) / 4
    x = sqrt(distance1**2 - ((y - 1) ** 2))
    return (x, y)


def main():
    dataset_file = sio.loadmat("./Dataset_1.mat")
    data: ndarray = dataset_file["H"]

    apdps = channel2APDP(data)
    delays = calculate_delays(apdps)

    locations = [
        calculate_location(delayTuple[0], delayTuple[1]) for delayTuple in delays
    ]
    [print(locationTuple[0], locationTuple[1]) for locationTuple in locations]
    x_values, y_values = zip(*locations)
    plt.scatter(x_values, y_values)
    plt.show()

    # zonder Nans
    print("zonder nans")
    filteredLocations = [
        locationTuple for locationTuple in locations if locationTuple[0] >= 0
    ]
    [print(locationTuple[0], locationTuple[1]) for locationTuple in filteredLocations]
    x_values, y_values = zip(*filteredLocations)
    plt.plot(x_values, y_values)
    plt.show()

    # delay testing
    # [plot_apdp_with_delay(array(apdps[i]), delays[i]) for i in range(len(apdps))]
    # plt.show()


main()
