import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.stop_flag = None
        self.initial_widgets()

    def initial_widgets(self):
        """Create widgets for the application."""
        Form(master=self, questions=["Port?", "Baud?", "test3"])  # add questions here

    def stop_serial(self):
        """Stop serial communication and close the serial port."""
        try:
            if self.comm.is_open:
                print("close thread")
                self.stop_flag = True
                self.thread.join()
                print("closed")
                self.comm.flushInput()
                self.comm.flushOutput()
                self.comm.close()
                print("Serial port closed successfully.")
            else:
                print("Serial port is already closed.")
        except Exception as e:
            print(f"Error while closing serial port: {str(e)}")

    def start_serial(self):
        """Stop serial communication and close the serial port."""
        try:
            if not self.comm.is_open:
                self.comm.open()
                self.stop_flag = False
                self.thread.start()
                print("Serial port opened successfully.")
            else:
                print("Serial port is already open.")
        except Exception as e:
            print(f"Error while opening serial port: {str(e)}")

    def connect(self):
        """Establish a serial connection."""
        port = self.data.get("Port?")
        if port:
            baud = self.data.get("Baud?", 9600)
            try:
                # runs when serial port is ready to read (when the actual code starts)
                self.comm = serial.Serial(port=port, baudrate=baud)
                self.reader = ReadLine(self.comm)
                print("Successful serial connection")
                self.init_app()
            except serial.SerialException:
                print("Failed to establish a serial connection")
                exit()
        else:
            print("No port specified")
            exit()

    def start_data_reading_thread(self):
        """Start a thread to read data from the serial port and update the graph."""
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.read_serial)
        self.thread.start()
        self.stop_flag = False

    def init_app(self):
        self.np_data = np.array([0, 0], int)
        self.grapher = ContinuousGraphApp(self)
        self.display = customtkinter.CTkLabel(self)
        self.stop = customtkinter.CTkButton(self, command=self.stop_serial, text="Stop")
        self.start = customtkinter.CTkButton(self, command=self.start_serial, text="Start")
        self.stop.pack()
        self.start.pack()
        self.display.pack()
        self.start_data_reading_thread()
        # self.bind("WM_DELETE_WINDOW", self.stop_serial)
        # self.bind("WM_DELETE_WINDOW", self.destroy)


    def read_serial(self):
        """Read data from the serial port and update the graph."""
        i = 0
        j = 0
        while True:
            if not self.stop_flag:
                try:
                    raw_data = int(self.reader.readline().decode('utf-8').strip("\r\n"))
                    print(raw_data)
                    j += 1
                    data = self.evaluate(raw_data)
                    with self.lock:
                        self.np_data = np.vstack((self.np_data, data))
                    if j >= 100:
                        self.df = pd.df
                    self.grapher.update_data(data)
                    self.display.configure(text=f"Data: {raw_data}")
                    print(time.thread_time())
                except ValueError:
                    print("Error reading data")
                    pass

    def evaluate(self, data: int) -> np.ndarray:
        """Evaluate and process data."""
        global i
        i += 1
        # return np.array([(time.thread_time()*1e4), data])
        return np.array([i, data])


class ContinuousGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Continuous Updating Graph")

        self.frame = customtkinter.CTkFrame(root)
        self.frame.pack(padx=10, pady=10, fill=customtkinter.BOTH, expand=True)

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Time (Epoch)')
        self.ax.set_ylabel('Data')

        self.fig.tight_layout()
        self.line, = self.ax.plot([], [], lw=2)

        self.x_data = []
        self.y_data = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=customtkinter.BOTH, expand=True)

    def update_data(self, data):
        self.x_data.append(data[0])
        self.y_data.append(data[1])
        if len(self.x_data) > 100:
            self.x_data.pop(0)
            self.y_data.pop(0)
        self.line.set_data(self.x_data, self.y_data)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()


class question(customtkinter.CTkFrame):
    def __init__(self, master, question_messages):
        self.msgs = question_messages
        super().__init__(master, fg_color="#217a61")
        self.create_widgets(question_messages)

    def create_widgets(self, quest_msgs):
        self.entries = []
        for index, msg in enumerate(quest_msgs):
            msg = customtkinter.CTkLabel(self, text=msg)
            input = customtkinter.CTkEntry(self)
            self.entries.append(input)
            msg.grid(row=index, column=0, padx=10, pady=10)
            input.grid(row=index, column=1, pady=10, padx=10)

    def done(self):
        data = [entry.get() for entry in self.entries]
        self.destroy()
        self.data = dict(zip(self.msgs, data))
        return self.data


class Form:
    def __init__(self, master, questions):
        self.questions = questions
        self.master = master
        self.create_widgets()

    def _get_response(self, outside, button):
        self.response_data = outside.done()
        button.destroy()
        self.master.data = self.response_data
        self.master.connect()

    def create_widgets(self):
        outside = question(self.master, self.questions)
        enter = customtkinter.CTkButton(self.master, text="Submit", command=lambda: self._get_response(outside, enter))
        self.master.bind('<Return>', lambda event=None: self._get_response(outside, enter))
        outside.pack(padx=10, pady=10)
        enter.pack(padx=10, pady=10)


class ReadLine:
    LINE_BREAK = b'\r\n'

    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        r = self.s.readline().strip(self.LINE_BREAK)
        print(r)
        return r

if __name__ == "__main__":
    global i
    i = 0
    str_time = time.time()
    tk = App()
    tk.mainloop()
