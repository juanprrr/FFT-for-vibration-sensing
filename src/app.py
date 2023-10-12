import tkinter as tk
from tkinter import ttk
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# Initialize serial communication with Arduino
ser = serial.Serial('COM3', 115200)  # Change 'COM3' to match your Arduino's serial port
muestreo = 50 # muestrear cada 10ms
delta_t  = muestreo/1000
g        = 9.77589 # gravedad calculada en costa rica https://revistas.ucr.ac.cr/index.php/ingenieria/article/view/7750

class ArduinoDataPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Medidor de vibraciones")
        
        self.acceleration = []
        self.velocity = []
        self.position = []

        # Create a plot
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()

        # Create a button to start plotting
        self.start_button = ttk.Button(root, text="Empezar a medir", command=self.start_plotting)
        self.start_button.pack()

        # Create a button to stop plotting and close the serial port
        self.stop_button = ttk.Button(root, text="Detener medición", command=self.stop_plotting)
        self.stop_button.pack()

        self.exit_button = ttk.Button(root, text="Salir", command=self.quit).pack()

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
                    self.update_plot()
                except ValueError as e:
                    print("Error parsing data:", e)  # Debug output
        if self.plotting:
            self.after_id = self.root.after(muestreo, self.read_data)  # Read every 50ms


    def update_plot(self):
        self.ax.clear()
        time_window = range(len(self.acceleration))
        self.plotter(time_window, self.acceleration, 'Aceleracion [m/s^2]')
        self.plotter(time_window, self.velocity, 'Velocidad [m/s]')
        self.plotter(time_window, self.position, 'Posicion  [mm]')
        self.ax.set_xlabel('Tiempo [ms]')
        self.canvas.draw()

    def quit(self):
        self.root.destroy()
        exit()
    
    def plotter(self, time_window, data_type, _label):
        self.ax.plot(time_window, data_type, label=_label)
        self.ax.legend()
        self.ax.set_xlim(max(0, len(self.acceleration) - muestreo), len(self.acceleration))  
    
    def write_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Aceleracion (m/s^2)", "Velocidad (m/s)", "Posicion (mm)"])  # Write headers

            for a, v, p in zip(self.acceleration, self.velocity, self.position):
                writer.writerow([a, v, p])

        
if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoDataPlotter(root)
    root.mainloop()
    
