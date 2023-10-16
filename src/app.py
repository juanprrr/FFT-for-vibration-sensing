import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import csv

# Frecuencia de muestreo de 50 (muestrear cada 10 ms)
muestreo = 50
delta_t = muestreo / 1000  # Intervalo de tiempo en segundos

class AnimationPlot:
    def __init__(self):
        """
        Inicializa la clase AnimationPlot.
        """
        self.dataList = []
        self.x_integral = 0
        self.y_integral = 0
        self.z_integral = 0
        self.velocity_x = []  # Limita la longitud de los datos para evitar problemas de memoria
        self.velocity_y = []
        self.velocity_z = []
        self.fig, self.axes = plt.subplots(2, 3, figsize=(12, 8))  # Crea 2 filas y 3 columnas de subtramas
        self.getPlotFormat()
        self.ser = serial.Serial("COM3", 115200)  # Coincide con la velocidad de baudios del Arduino

    def animate(self, i):
        """
        Función que se llama en cada iteración de la animación.
        """
        self.ser.write(b'g')
        arduinoData_string = self.ser.readline().decode('ascii').strip()
        arduinoData = arduinoData_string.split(',')
        if len(arduinoData) == 3:
            try:
                acceleration_x, acceleration_y, acceleration_z = map(float, arduinoData)
                self.x_integral = acceleration_x * delta_t
                self.y_integral = acceleration_y * delta_t
                self.z_integral = acceleration_z * delta_t

                self.velocity_x.append(self.x_integral)
                self.velocity_y.append(self.y_integral)
                self.velocity_z.append(self.z_integral)

                self.plot_fft(self.velocity_x, self.axes[1, 0], "FFT X")
                self.plot_fft(self.velocity_y, self.axes[1, 1], "FFT Y")
                self.plot_fft(self.velocity_z, self.axes[1, 2], "FFT Z")

                # Guardar los datos en archivos CSV
                self.save_time_data()
                self.save_fft_data()

            except ValueError as e:
                print("Error al analizar los datos:", e)  # Salida de depuración

        # Limita la longitud de los datos a 50
        self.velocity_x = self.velocity_x[-50:]
        self.velocity_y = self.velocity_y[-50:]
        self.velocity_z = self.velocity_z[-50:]

        self.axes[0, 0].clear()
        self.axes[0, 1].clear()
        self.axes[0, 2].clear()
        self.getPlotFormat()

        self.axes[0, 0].plot(self.velocity_x)
        self.axes[0, 0].set_title("VelocidadX [m/s]")
        self.axes[0, 1].plot(self.velocity_y)
        self.axes[0, 1].set_title("VelocidadY [m/s]")
        self.axes[0, 2].plot(self.velocity_z)
        self.axes[0, 2].set_title("VelocidadZ [m/s]")

    def getPlotFormat(self):
        for ax in self.axes[0]:
            ax.set_ylabel("Velocidad")
            ax.set_xlim(max(0, len(self.velocity_x) - 50), len(self.velocity_x))

    def plot_fft(self, data, ax, title):
        """
        Calcula y grafica la Transformada Rápida de Fourier (FFT) de los datos.
        """
        N = len(data)
        freq = np.fft.fftfreq(N, d=delta_t)
        fft_values = np.abs(np.fft.fft(data)) / N

        ax.clear()
        ax.plot(freq[:N // 2], fft_values[:N // 2], label=title)
        ax.legend()
        ax.set_title(title)
        ax.set_xlabel('Frecuencia [Hz]')
        ax.set_ylabel("Magnitud")

    def save_time_data(self):
        # Guardar los datos de velocidad en el tiempo (velocidad_x, velocidad_y, velocidad_z)
        with open('velocidad_tiempo.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.velocity_x[-1], self.velocity_y[-1], self.velocity_z[-1]])

    def save_fft_data(self):
        # Guardar los datos de FFT (frecuencia y magnitud) para cada eje en archivos separados
        N = len(self.velocity_x)
        freq = np.fft.fftfreq(N, d=delta_t)
        fft_values_x = np.abs(np.fft.fft(self.velocity_x)) / N
        fft_values_y = np.abs(np.fft.fft(self.velocity_y)) / N
        fft_values_z = np.abs(np.fft.fft(self.velocity_z)) / N

        with open('fft_x.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            for f, mag in zip(freq[:N // 2], fft_values_x[:N // 2]):
                writer.writerow([f, mag])

        with open('fft_y.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            for f, mag in zip(freq[:N // 2], fft_values_y[:N // 2]):
                writer.writerow([f, mag])

        with open('fft_z.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            for f, mag in zip(freq[:N // 2], fft_values_z[:N // 2]):
                writer.writerow([f, mag])

def main():
    realTimePlot = AnimationPlot()
    time.sleep(2)

    ani = animation.FuncAnimation(realTimePlot.fig, realTimePlot.animate, frames=100, interval=100)
    plt.tight_layout()  # Ajusta las subtramas para un mejor espaciado
    plt.show()

    realTimePlot.ser.close()

if __name__ == "__main__":
    main()
