from math import *
from numpy import *
from scipy import *
import matplotlib.pyplot as plt
import scipy.signal as sig
import scipy.fftpack as fftp
import scipy.io as sio


# -- Bepalen reistijden van paden --
def channel2APDP(original_data):
    """
    APDP: Averaged Power Delay Profile
    Data in form of: freq_tonen x positions x measurements
    """
    print("channel2APDP")

    data = transpose(original_data, (1, 2, 0))
    data = reshape(data, (25, 100, 200))

    ifft_amplitude = [abs(fftp.ifft(arr)) for arr in data[:, :]]        #Hier moeten we ook nog eens een venster rond proberen zetten
    power = [amplitude*amplitude for amplitude in ifft_amplitude[:][:]]
    avg_power = [mean(power_values) for power_values in power]          #len25 array:)

    return avg_power

    # Uit de practica weet je nog dat de afstand tussen de opeenvolgende tijdssamples (∆T = 1/fS )
    # bepaalde wat de range van de samples in het frequentiedomein was (0 tot fS ) en hun
    # onderlinge afstand of frequentieresolutie (fS /N). Maak de analogie en denk na over de
    # range van de nu bekomen samples in het tijdsdomein (of hier delaydomein), welke delay
    # stelt elk sample voor (wat is de tijdsresolutie) en hoe linkt dit aan de afstand tussen de
    # opeenvolgende frequentietonen en aan de bandbreedte van het signaal?




def calculate_delays():
    print("calculate_delays")


# -- Locatiebepaling --
def calculate_location(tau0: number, tau1=number) -> (number, number):
    """
    tau0: reistijd direct propagatiepad
    tau1: reistijd gereflecteerde pad
    """
    print("calculate_location")


def main():
    print("main")

    dataset_file = sio.loadmat("./Dataset_1.mat")
    original_data = dataset_file["H"]

    apdp = channel2APDP(original_data)

    # print(apdp)

    plt.plot(apdp)
    plt.show()


main()
