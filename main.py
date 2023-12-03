from math import *

import matplotlib.pyplot as plt
import scipy.fftpack as fftp
import scipy.io as sio
import scipy.signal as sig
import scipy.constants as consts
from numpy import *
from scipy import *



# -- Bepalen reistijden van paden --
def channel2APDP(original_data: ndarray):
    """
    APDP: Averaged Power Delay Profile
    Data in form of: freq_tonen(200) x positions(25) x measurements(100)
    """
    data = transpose(original_data, (1, 2, 0))
    data = reshape(data, (25, 100, 200))
    # Data in nieuwe vorm: positions(25) x measurements(100) x freq_tonen(200)

    # Venster rond zetten:
    filter = sig.windows.gaussian(200,26)

    # plt.plot(filter)
    # plt.show()

    data_windowed = [[meas*filter for meas in arr] for arr in data]

    ifft_amplitude = [[abs(fftp.ifft(meas)) for meas in arr] for arr in data_windowed]

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



def calculate_delays(APDPs: ndarray):
    """
    Returns list of Tau1 and Tau2 Pairs
    """
    # Er zijn samples om de 10 MHz. Via onderstaande logica kunnen we de tijdsafstand tussen samples bepalen.
    # fS = 1/Δt  -->  T = 1/Δf  -->  Δt = T / N = 1 / (Δf*N) = 10e-7s/200 = 5e-10 s
    dT = 5e-10

    delays = list()
    for APDP in APDPs:
        peakIndexes, _ = sig.find_peaks(APDP)
        max2peakIndexes = sorted(peakIndexes, key=lambda x: APDP[x], reverse=True)[:2]
        print(max2peakIndexes)
        max2Delays = [peakIndex * dT for peakIndex in max2peakIndexes]
        delays.append(max2Delays)

    # Om te garanderen dat het rechtstreekse signaal steeds het kortste is. Zonder window is dit voor sommige waarden nodig.
    # Na testen schijnt echter dat voor deze waarden nog grotere problemen van tel zijn (Wortel van een negatief getal),
    # en deze extra stap dus geen verbetering geeft op het eindresultaat. (De eerstvolgende waarde op de Hoofdpiek ligt op te grote afstand.)
    # for APDP in APDPs:
    #     peakIndexes, _ = sig.find_peaks(APDP)
    #     sortedPeakIndexes = sorted(peakIndexes, key=lambda x: APDP[x], reverse=True)
    #     i=0
    #     while sortedPeakIndexes[i+1]<sortedPeakIndexes[i]:
    #         i+=1
    #     max2peakIndexes = sortedPeakIndexes[i],sortedPeakIndexes[i+1]
    #     print(max2peakIndexes)
    #     max2Delays = [peakIndex * dT for peakIndex in max2peakIndexes]
    #     delays.append(max2Delays)

    return delays



# -- Locatiebepaling --
def calculate_location(tau0: float, tau1: float):
    """
    tau0: reistijd direct propagatiepad
    tau1: reistijd gereflecteerde pad

    Coördinaten basisstation: (xB, yB) = (0m, 1m)
    """
    #print(tau0 < tau1, f"{tau0}<{tau1}")  --> Met Window komt de reflectie steeds na de main!!

    # Er worden 2 cirkels gedefinieerd. 
    # Één cirkel tussen het basisstation en de rechtstreekse afstand tot de drone. 
    # Een andere tussen het denkbeeldige basisstation gereflecteerd over de x-as, en de gereflecteerde afstand tot de drone.
 
    r0 = tau0 * consts.speed_of_light   # Rechtstreekse afstand tot drone
    r1 = tau1 * consts.speed_of_light   # Gereflecteerde afstand tot drone

    y0 = 1      # y-coordinaat basisstation
    y1 = -1     # y-coordinaat gereflecteerde basisstation
    d = 2       # Afstand tussen Middelpunten van 2 denkbeeldige cirkels m0=(0,1) en m1=(0,-1)

    # Vervolgens wordt het snijpunt gezocht tussen deze 2 cirkels:
    a=(r0**2-r1**2+d**2)/(2*d)  # Afstand van m0 tot het snijpunt van de lijn tussen de twee cirkelcentra en de loodlijn hierop die door de intersectiepunten gaat.
    x=sqrt(r0**2-a**2)*(y0-y1)/d
    y=y0+a*(y1-y0)/d   

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
    plt.yscale('log')
    plt.legend()
    plt.grid(True)


def mediaan_van_fout_op_lokalisatie(locations):
    """
    Vergelijk de gevonden coordinaten met het effectief afgelopen pad:
        t = 0,1,...,24
        x = 2 + (t/2)
        y = (t²/32) - (t/2) + 6
    """



    return (0.0)



def main():
    dataset_file = sio.loadmat("./Dataset_1.mat")
    data: ndarray = dataset_file["H"]

    apdps = channel2APDP(data)
    delays = calculate_delays(apdps)

    locations = [calculate_location(delayTuple[0], delayTuple[1]) for delayTuple in delays]

    i = 1
    for locationTuple in locations:
        print(f"x{i}: {locationTuple[0]}m    y{i}: {locationTuple[1]}m")
        i += 1
    
    x_values, y_values = zip(*locations)
    plt.scatter(x_values, y_values)
    plt.plot(x_values, y_values)
    plt.xlim((0,16))
    plt.ylim((0,14))
    plt.ylim(bottom=0)
    plt.show()



main()










'''
Previous code for reference:

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
    plt.legend()
    plt.grid(True)
    plt.show()


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
        peakIndexes, _ = sig.find_peaks(APDP, height=0)
        max2peakIndexes = sorted(peakIndexes, key=lambda x: APDP[x], reverse=True)[:2]
        max2Delays = [peakIndex * fS for peakIndex in max2peakIndexes]
        delays.append(max2Delays)

    return delays


# -- Locatiebepaling --
def calculate_location(tau0: float64, tau1: float64):
    """
    tau0: reistijd direct propagatiepad
    tau1: reistijd gereflecteerde pad

    Coördinaten basisstation: (xB, yB) = (0m, 1m)
    """
    print(tau0 < tau1, f"{tau0}<{tau1}")
    receiver_position = (0, 1)



    distance_direct = tau0 * consts.speed_of_light
    distance_reflected = tau1 * consts.speed_of_light

    # The sending point is on the circle centered at the receiver with radius equal to the direct path distance
    # The reflected point is on the circle centered at the origin with radius equal to the reflected path distance
    # The sending point is the intersection of these two circles

    # Solve the system of equations to find the intersection points
    d = distance_direct
    r = distance_reflected
    y = receiver_position[1]

    x = (d**2 - r**2 + y**2) / (2 * y)
    y = sqrt(abs(d**2 - x**2))

    return (x, y)


def main():
    dataset_file = sio.loadmat("./Dataset_1.mat")
    data: ndarray = dataset_file["H"]

    apdps = channel2APDP(data)
    delays = calculate_delays(apdps)
    locations = [
        calculate_location(delayTuple[0], delayTuple[1]) for delayTuple in delays
    ]
    x_values, y_values = zip(*locations)
    plt.scatter(x_values, y_values)
    plt.show()

    # plot_apdp_with_delay(array(apdps[0]), delays[0])


main()

'''