from math import *
from numpy import *
from scipy import *
import matplotlib.pyplot as plt
import scipy.signal as sig
import scipy.fftpack as fftp
import scipy.io as sio


# -- Bepalen reistijden van paden --
def channel2APDP(data):
    """
    APDP: Averaged Power Delay Profile
    """
    print("channel2APDP")


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

data = transpose(original_data, (1, 2, 0))
data = reshape(data, (25, 100, 200))

ifft = [abs(real(fftp.ifft(arr))) for arr in data[:, :]]

plt.plot(ifft[0][0])
plt.plot(ifft[0][1])
plt.plot(ifft[0][3])
plt.plot(ifft[1][0])
plt.plot(ifft[1][1])
plt.plot(ifft[1][3])
plt.show()

main()
