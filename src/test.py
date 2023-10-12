import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import tkinter as tk
from tkinter import ttk
import numpy as np

# Initialize serial communication with Arduino
ser = serial.Serial('COM3', 115200)  # Change 'COM3' to match your Arduino's serial port
muestreo = 50  # muestrear cada 10ms
delta_t = muestreo / 1000
g = 9.77589  # gravedad calculada en Costa Rica

class ArduinoDataPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Medidor de vibraciones")

        self.acceleration = []
        self.velocity = []
        self.position = []

        # Create a 2x3 grid of subplots for time and frequency domains
        self.figure, self.ax = plt.subplots(2, 3, figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()

        # Create a button to start plotting
        self.start_button = ttk.Button(root, text="Empezar a medir", command=self.start_plotting)
        self.start_button.pack()

        # Create a button to stop plotting and close the serial port
        self.stop_button = ttk.Button(root, text="Detener medición", command=self.stop_plotting)
        self.stop_button.pack()

        # Create a button to exit the application
        self.exit_button = ttk.Button(root, text="Salir", command=self.quit)
        self.exit_button.pack()

        self.plotting = False
        self.after_id = None

    def start_plotting(self):
        self.plotting = True
        self.read_data()

    def stop_plotting(self):
        self.plotting = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        ser.close()
        self.write_to_csv("Datos-tiempo.csv")

    def read_data(self):
        data = ser.readline().decode().strip()
        if data and self.plotting:
            print("Received data:", data)  # Debug output
            values = data.split(',')
            if len(values) == 2:
                try:
                    acceleration_x, acceleration_y = map(float, values)
                    acc_magnitude = ((acceleration_x * g) ** 2 + (acceleration_y * g) ** 2) ** 0.5
                    self.acceleration.append(acc_magnitude)
                    self.velocity.append(acc_magnitude * delta_t)
                    self.position.append(1000 * 0.5 * acc_magnitude * (delta_t ** 2))

                    if len(self.acceleration) % 1 == 0:
                        self.update_plot()

                except ValueError as e:
                    print("Error parsing data:", e)  # Debug output

        if self.plotting:
            self.after_id = self.root.after(muestreo, self.read_data)  # Read every 50ms

    def update_plot(self):
        time_window = range(len(self.acceleration))
        self.plotter(self.ax[0, 0], time_window, self.acceleration, 'Aceleracion [m/s^2]')
        self.plotter(self.ax[0, 1], time_window, self.velocity, 'Velocidad [m/s]')
        self.plotter(self.ax[0, 2], time_window, self.position, 'Posicion [mm]')

        # Calculate and update the frequency-domain plots
        self.plot_fft(self.ax[1, 0], self.acceleration, 'Aceleracion (Freq Domain)')
        self.plot_fft(self.ax[1, 1], self.velocity, 'Velocidad (Freq Domain)')
        self.plot_fft(self.ax[1, 2], self.position, 'Posicion (Freq Domain)')

        self.ax[0, 0].set_xlabel('Tiempo [ms]')
        self.ax[1, 0].set_xlabel('Frecuencia [Hz]')
        self.canvas.draw()

    def plotter(self, ax, time_window, data_type, _label):
        ax.clear()
        ax.plot(time_window, data_type, label=_label)
        ax.legend()
        ax.set_xlim(max(0, len(data_type) - muestreo), len(data_type))

    def plot_fft(self, ax, data, _label):
        N = len(data)
        if N > 0:
            freq = np.fft.fftfreq(N, d=delta_t)
            fft_values = np.abs(np.fft.fft(data)) / N

            ax.clear()
            ax.plot(freq[:N // 2], fft_values[:N // 2], label=_label)
            ax.legend()
            ax.set_xlabel('Frecuencia [Hz]')

    def write_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Aceleracion (m/s^2)", "Velocidad (m/s)", "Posicion (mm)"])  # Write headers
            for a, v, p in zip(self.acceleration, self.velocity, self.position):
                writer.writerow([a, v, p])

    def quit(self):
        self.root.destroy()
        exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoDataPlotter(root)
    root.mainloop()
