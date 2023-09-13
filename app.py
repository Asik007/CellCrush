import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import serial
from Reader import ReadLine
from input import Form
import customtkinter

def evaluate(data: int) -> np.ndarray:
    """Evaluate and process data."""
    return np.array([int((time.time() - str_time) * 1e6), data])

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.create_widgets()

    def create_widgets(self):
        """Create widgets for the application."""
        Form(master=self, questions=["Port?", "Baud?", "test3"])

    def connect(self):
        """Establish a serial connection."""
        port = self.data.get("Port?")
        if port:
            baud = self.data.get("Baud?", 9600)
            try:
                self.comm = serial.Serial(port=port, baudrate=baud)
                self.Reader = ReadLine(self.comm)
                print("Successful serial connection")
                self.np_data = np.array([0, 0], int)
                self.grapher = ContinuousGraphApp(self)
                self.display = customtkinter.CTkLabel(self)
                self.display.pack()
                # self.grapher.after(10, update())
            except serial.SerialException:
                print("Failed to establish a serial connection")
                exit()
        else:
            print("No port specified")
            exit()

    def readserial(self):
        """Read data from the serial port and update the graph."""
        i = 0
        while True:
            try:
                raw_data = int(self.comm.readline().decode('utf-8').strip("\r\n"))
                data = evaluate(raw_data)
                with self.lock:
                    self.np_data = np.vstack((self.np_data, data))
                    # print(self.np_data)
                self.grapher.update_data(data)

                self.display.configure(text=f"Data: {raw_data}")
            except ValueError:
                print("errorerd")
                pass

    def mainApp(self):
        """Start the main application and read data in a separate thread."""
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.readserial)
        self.thread.start()

class ContinuousGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Continuous Updating Graph")

        self.frame = customtkinter.CTkFrame(root)
        self.frame.pack(padx=10, pady=10, fill=customtkinter.BOTH, expand=True)

        self.fig, self.ax = plt.subplots()
        self.fig.tight_layout()
        # self.ax.set_xlim(0, 200000000)
        # self.ax.set_ylim(0, 100)
        self.line, = self.ax.plot([], [], lw=2)


        self.x_data = []
        self.y_data = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=customtkinter.BOTH, expand=True)

    def update_data(self, data):
        # print("update")
        """Update the graph with new data."""
        global i
        i += 1
        self.x_data.append(data[0])
        self.y_data.append(data[1])
        # print(self.x_data)
        if i > 100:
            self.x_data =
        self.line.set_data(self.x_data, self.y_data)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()
        return



class question(customtkinter.CTkFrame):
    entries = []
    def __init__(self, master, question_messages):
        self.msgs = question_messages
        super().__init__(master, fg_color="#217a61")
        self.create_widgets(question_messages)

    def create_widgets(self, quest_msgs):
        for index, msg in enumerate(quest_msgs):
            msg = customtkinter.CTkLabel(self,text=msg)
            input = customtkinter.CTkEntry(self)
            self.entries.append(input)
            msg.grid(row=index, column=0, padx= 10, pady =10)
            input.grid(row=index, column=1, pady =10, padx =10)
        return
    def done(self):
        data = [entry.get() for entry in self.entries]
        self.destroy()
        self.data = dict(zip(self.msgs, data))
        return dict(zip(self.msgs, data))
class Form():
    def __init__(self,master,questions):
        self.questions = questions
        self.master = master
        self.create_widgets()
        #rest of code
        # self.mainloop()

    def _getresponse(self, outside, button):
        self.response_data = outside.done()
        # print(self.response_data)
        button.destroy()
        self.master.data = self.response_data
        self.master.connect()
        self.master.mainApp()
    def create_widgets(self):
        outside = question(self.master, self.questions)
        enter = customtkinter.CTkButton(self.master, text="submit", command=lambda: self._getresponse(outside, enter))
        outside.pack(padx=10, pady=10)
        enter.pack(padx=10, pady=10)
        return



global str_time
str_time = time.time()
i=0
if __name__ == "__main__":
    tk = App()
    tk.mainloop()
