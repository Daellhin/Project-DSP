from math import *
import matplotlib.pyplot as plt
import scipy.constants as consts
import scipy.fftpack as fftp
import scipy.io as sio
import scipy.signal as sig
from numpy import *
from scipy import *


# -- Bepalen reistijden van paden --
def channel2APDP(original_data: ndarray, use_window=False):
    """
    APDP: Averaged Power Delay Profile
    Data in vorm: Dataset1(freq_tonen(200) x positions(25) x measurements(100))
    """
    # Data in nieuwe vorm: Dataset1(positions(25) x measurements(100) x freq_tonen(200))
    s0 = size(original_data, 0)  # 200
    s1 = size(original_data, 1)  # 25
    s2 = size(original_data, 2)  # 100
    data = transpose(original_data, (1, 2, 0))
    data = reshape(data, (s1, s2, s0))

    # Venster rond zetten(26 voor Dataset1, 130 voor Dataset2)
    filter = sig.windows.gaussian(s0, 26 if s0 == 200 else 130)

    # plt.plot(filter)
    # plt.show()

    if use_window:
        data = [[meas * filter for meas in arr] for arr in data]

    ifft_amplitude = [[abs(fftp.ifft(meas)) for meas in arr] for arr in data]

    # Data in nieuwe vorm: Dataset1(positions(25) x freq_tonen(200) x measurements(100))
    ifft_amplitude = transpose(ifft_amplitude, (0, 2, 1))
    ifft_amplitude = reshape(ifft_amplitude, (s1, s0, s2))

    power = [
        [
            [measurement * measurement for measurement in freq_tonen]
            for freq_tonen in positions
        ]
        for positions in ifft_amplitude
    ]
    avg_power = [[mean(power_values) for power_values in pos] for pos in power]

    return avg_power


def calculate_delays(APDPs: ndarray, manual_sort):
    """
    Returns list of Tau1 and Tau2 Pairs
    """
    # Er zijn samples om de 10 MHz. Via onderstaande logica kunnen we de tijdsafstand tussen samples bepalen.
    # fS = 1/Δt  -->  T = 1/Δf  -->  Δt = T / N = 1 / (Δf*N) = 1e-7s/200 = 5e-10 s
    dT = 1e-7 / size(APDPs, 1)

    delays = list()
    if not manual_sort:
        for APDP in APDPs:
            peakIndexes, _ = sig.find_peaks(APDP)
            max2peakIndexes = sorted(peakIndexes, key=lambda x: APDP[x], reverse=True)[
                :2
            ]
            max2Delays = [peakIndex * dT for peakIndex in max2peakIndexes]
            delays.append(max2Delays)

    # Om te garanderen dat het rechtstreekse signaal steeds het kortste is. Zonder window is dit voor sommige waarden nodig.
    # Na testen schijnt echter dat voor deze waarden nog grotere problemen van tel zijn (Wortel van een negatief getal),
    # en deze extra stap dus geen verbetering geeft op het eindresultaat. (De eerstvolgende waarde op de Hoofdpiek ligt op te grote afstand.)
    if manual_sort:
        for APDP in APDPs:
            peakIndexes, _ = sig.find_peaks(APDP)
            sortedPeakIndexes = sorted(peakIndexes, key=lambda x: APDP[x], reverse=True)
            i = 0
            while sortedPeakIndexes[i + 1] < sortedPeakIndexes[i]:
                i += 1
            max2peakIndexes = sortedPeakIndexes[i], sortedPeakIndexes[i + 1]
            max2Delays = [peakIndex * dT for peakIndex in max2peakIndexes]
            delays.append(max2Delays)

    return delays


# -- Locatiebepaling --
def calculate_location(tau0: float, tau1: float):
    """
    tau0: reistijd direct propagatiepad
    tau1: reistijd gereflecteerde pad

    Coördinaten basisstation: (xB, yB) = (0m, 1m)
    """
    # print(tau0 < tau1, f"{tau0}<{tau1}")  --> Met Window komt de reflectie steeds na de hoofdpiek!!

    # Er worden 2 cirkels gedefinieerd.
    # Één cirkel tussen het basisstation en de rechtstreekse afstand tot de drone.
    # Een andere tussen het denkbeeldige basisstation gereflecteerd over de x-as, en de gereflecteerde afstand tot de drone.

    r0 = tau0 * consts.speed_of_light  # Rechtstreekse afstand tot drone
    r1 = tau1 * consts.speed_of_light  # Gereflecteerde afstand tot drone

    d = 2  # Afstand tussen Middelpunten van 2 denkbeeldige cirkels m0=(0,1) en m1=(0,-1)

    # Vervolgens wordt het snijpunt gezocht tussen deze 2 cirkels:

    y = (r1**2 - r0**2) / (
        2 * d
    )  # Vergelijking van rechte die door de intersectiepunten gaat. Hier ook rechtstreeks y-coördinaat van gezochte punt.
    x = sqrt(
        r0**2 - (y - 1) ** 2
    )  # We zijn steeds opzoek naar het strikt positieve snijpunt, dus uitkomst na sqrt volstaat.

    return (x, y)


# -- Tests --
def plot_apdp_with_delay(apdp, delays):
    """
    Plots the impulse response and marks the peaks
    """
    delay = [int(delay / 5e-10) for delay in delays]
    plt.figure(figsize=(8, 6))
    plt.plot(apdp)
    plt.plot(delay, apdp[delay], "x", label="Peaks", color="red")
    plt.xlabel("Index")
    plt.ylabel("Amplitude")
    plt.title("Impulse Response with Peaks")
    plt.yscale("log")
    plt.legend()
    plt.grid(True)


def mediaan_van_fout_op_lokalisatie(locations, known_trajectory):
    """
    Vergelijk de gevonden coordinaten met het effectief afgelopen pad.
    """
    x, y = zip(*locations)
    xk, yk = zip(*known_trajectory)
    xfouten = []
    yfouten = []
    for i in range(len(locations)):
        xfouten.append(abs(x[i] - xk[i]))
        yfouten.append(abs(y[i] - yk[i]))

    return median(xfouten), median(yfouten)


def calculate_theoretical_trajectory(length):
    """
    Bereken het theoretisch afgelopen pad:
    t = 0,1,...,24
    x = 2 + (t/2)
    y = (t²/32) - (t/2) + 6
    """
    return [((2 + (i / 2)), (((i**2) / 32) - (i / 2) + 6)) for i in range(length)]


def analyse_dataset(dataset, use_window, manual_sort):
    print(f"-- Dataset: '{dataset}' (windowing: '{use_window}') --")

    dataset_file = sio.loadmat(dataset)
    data: ndarray = dataset_file["H"]

    apdps = channel2APDP(data, use_window)
    delays = calculate_delays(apdps, manual_sort)

    locations = [
        calculate_location(delayTuple[0], delayTuple[1]) for delayTuple in delays
    ]

    i = 1
    for locationTuple in locations:
        print(f"x{i}: {locationTuple[0]}m    y{i}: {locationTuple[1]}m")
        i += 1

    known_locations = calculate_theoretical_trajectory(len(locations))

    print("mediaanfout =", mediaan_van_fout_op_lokalisatie(locations, known_locations))

    # Calculated:
    x_values, y_values = zip(*known_locations)
    plt.scatter(x_values, y_values, color="red")
    plt.plot(x_values, y_values, label="Theoretical", color="red")

    # Measured:
    x_values, y_values = zip(*locations)
    plt.scatter(x_values, y_values, color="blue")
    plt.plot(x_values, y_values, label="Measured", color="blue")
    plt.xlim((0, 17))
    plt.ylim((0, 15))
    plt.ylim(bottom=0)

    plt.legend()
    plt.show()


def main():
    use_window = True
    analyse_dataset("./Dataset_1.mat", use_window, False)
    print()
    analyse_dataset("./Dataset_2.mat", use_window, True)


main()
