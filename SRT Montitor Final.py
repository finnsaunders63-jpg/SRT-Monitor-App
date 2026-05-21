import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests
import hashlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import os
import tkinter.font as tkFont
import ctypes

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tooltip, add="+")
        self.widget.bind("<Leave>", self.hide_tooltip, add="+")
    
    def show_tooltip(self, event=None):
        if self.tipwindow or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes('-topmost', True)
            label = tk.Label(tw, text=self.text, background="lightgrey", relief="solid", borderwidth=1, padx=5, pady=2, justify=tk.LEFT)
            label.pack()
        except:
            pass
    
    def hide_tooltip(self, event=None):
        if self.tipwindow:
            try:
                self.tipwindow.destroy()
            except:
                pass
            self.tipwindow = None

# Set Windows taskbar icon BEFORE creating window
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SRTMonitor")
except:
    pass

main_window = tk.Tk()

# Window Settings
App_Title = "SRT Monitor"
x_value = 650
y_value = 360

# Creating the Window
main_window.title(f"{App_Title}")
main_window.geometry(f"{x_value}x{y_value}")
main_window.configure(background="snow")
icon_path = os.path.join(os.path.dirname(__file__), "SRT_Monitor.ico")
if os.path.exists(icon_path):
    main_window.iconbitmap(icon_path)



cpu_temp = 0
box_name = "Encoder"
ip_address = "N/A"
main_codec = "N/A"
current_bps = 0
target_bps = 0
stream_name = "Unspecified Encoder"
buffer = 0
packet_loss = 0
rtt_time = 0
stream_status = 0
stream_type = 0
stream_uptime = 0
sdi_status = 0
cx = 0
cy = 0
interlaced = 0
frame_rate = 0
dest_ip = 0
dest_port = 0
current_packet_loss = 0
previous_packet_loss = 0
first_packet_loss_update = True
bars5 = None
error_label = None



def home_screen():
    global error_label
    # New Encoder IP
    encode_ip=Entry(main_window, width=20, borderwidth=2, justify=tk.CENTER)
    encode_ip.place(relx=0.5, rely= 0.3, anchor="center")
    encode_ip_label=Label(main_window, text="Enter Encoder IP Address")
    encode_ip_label.place(relx=0.5, rely=0.25, anchor="center")

    # New Encoder Username
    encode_user=Entry(main_window, width=20, borderwidth=2, fg="dark grey", justify=tk.CENTER)
    encode_user.place(relx=0.5, rely= 0.5, anchor="center")
    encode_user.insert(0, "Admin")
    encode_user_label=Label(main_window, text="Enter Encoder Username")
    encode_user_label.place(relx=0.5, rely=0.45, anchor="center")

    # New Encoder Password
    encode_pass=Entry(main_window, width=20, borderwidth=2, fg="dark grey", justify=tk.CENTER)
    encode_pass.place(relx=0.5, rely= 0.7, anchor="center")
    encode_pass.insert(0, "Admin")
    encode_pass_label=Label(main_window, text="Enter Encoder Password")
    encode_pass_label.place(relx=0.5, rely=0.65, anchor="center")

    # Set Encoder Button
    add_encoder = tk.Button(main_window, text="Add", width=10, command=lambda: set_home_window(encode_ip, encode_user, encode_pass))
    add_encoder.place(relx=0.5, rely=0.8, anchor="center")
    
    # Bind Enter key to the button
    encode_ip.bind("<Return>", lambda event: set_home_window(encode_ip, encode_user, encode_pass))
    encode_user.bind("<Return>", lambda event: set_home_window(encode_ip, encode_user, encode_pass))
    encode_pass.bind("<Return>", lambda event: set_home_window(encode_ip, encode_user, encode_pass))
    
    # Error label for connection issues
    error_label = tk.Label(main_window, text="",bg="snow", fg="red", font=("Arial", 10, "bold"))
    error_label.place(relx=0.5, rely=0.18, anchor="center")

def update_data(device_ip, username, password):

    global current_bps, buffer, packet_loss, rtt_time, stream_name, stream_status, stream_type, stream_uptime, cpu_temp, box_name, ip_address, main_codec, target_bps, sdi_status, cx, cy, frame_rate, interlaced, dest_ip, dest_port

    try:
        session = requests.Session()

        # Authenticate first
        password_hash = hashlib.md5(password.encode()).hexdigest()
        login_url = f"http://{device_ip}/usapi?method=login&id={username}&pass={password_hash}"
        
        # Actually perform the login
        login_response = session.get(login_url, timeout=5)
        login_data = login_response.json()
        
        # Check if login was successful (result should be 0)
        if login_data.get("result") != 0:
            print(f"Login failed. Response: {login_data}")
            raise Exception("Authentication failed")
        
        
    
        
        # Now get the status using the authenticated session
        status_url = f"http://{device_ip}/usapi?method=get-status"
        r = session.get(status_url, timeout=5)
        data = r.json()

        # Encoder Info
        cpu_temp = data.get("cpu-temperature", 0)
        box_name = data.get("box-name", "Encoder")
        ip_address = data.get("eth", {}).get("ip", "N/A")

        # Codec Info
        main_codec = data.get("codec", {}).get("main-stream", {})
        current_bps = main_codec.get("cur-bps", 0) / 1000000
        target_bps = main_codec.get("kbps", 0) / 1000
        # Current bps info
        # Input Signal Status
        sdi = data.get("input-signal", {}).get("sdi", {})

        if sdi:
            sdi_status = sdi.get("status", 0)
            cx = sdi.get("cx", 0)
            cy = sdi.get("cy", 0)
            interlaced = sdi.get("interlaced", 0)
            frame_rate = sdi.get("frame-rate", 0)
        else:
            pass

        # Livestream Info
        live_list = data.get("live-status", {}).get("live", [])
        if live_list and len(live_list) > 0:
            live = live_list[0]
            stream_name = live.get("name", "Unspecified Encoder")
            buffer = live.get("buf-ms", 0)
            packet_loss = live.get("pkt-loss-total", 0)
            rtt_time = live.get("rrt-ms", 0)
            stream_status = live.get("result", 0)
            stream_type = live.get("type", 900)
            stream_uptime = live.get("run-ms", 0)
            dest_ip = live.get("ip-addr", 0)
            dest_port = live.get("port", 0)
        else:
            # No active streams
            stream_name = "No Active Stream"
            buffer = 0
            rtt_time = 0
            stream_status = 0
            stream_type = 900
            stream_uptime = 0

    except requests.exceptions.Timeout:
        print("Request timed out.")
        reset_to_defaults()
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the device.")
        reset_to_defaults()
    except ValueError as e:
        print(f"Failed to decode JSON from the response: {e}")
        reset_to_defaults()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        reset_to_defaults()

    return current_bps, target_bps, buffer, packet_loss, rtt_time, stream_name, stream_status, stream_type, stream_uptime, cpu_temp, box_name, ip_address

def reset_to_defaults():
    global cpu_temp, box_name, ip_address, main_codec, stream_name, current_bps, buffer, packet_loss, rtt_time, stream_status, stream_type, stream_uptime
    cpu_temp = 0
    box_name = "Encoder"
    ip_address = "N/A"
    main_codec = {}
    stream_name = "Unspecified Encoder"
    buffer = 0
    packet_loss = 0
    rtt_time = 0
    stream_status = 0
    stream_type = 900
    stream_uptime = 0

def clear_all_inside_frame():
    for widget in main_window.winfo_children():
        widget.destroy()

def set_home_window(encode_ip, encode_user, encode_pass):
    global current_bps, target_bps, buffer, packet_loss, rtt_time, selected_time, time_selection, stream_name, stream_status, stream_type, stream_uptime, cpu_temp, box_name, ip_address, times, bits_per_second, target_bits_per_second, packet_loss_list, current_packet_loss, previous_packet_loss, bars5, error_label
    flashing = False
    stream_flashing = False

    device_ip = encode_ip.get()
    username = encode_user.get()
    password = encode_pass.get()
    current_packet_loss = 0

    try:
        session = requests.Session()

        # Authenticate first
        password_hash = hashlib.md5(password.encode()).hexdigest()
        login_url = f"http://{device_ip}/usapi?method=login&id={username}&pass={password_hash}"
        login_response = session.get(login_url, timeout=5)
        login_data = login_response.json()

        # Check login result properly
        if login_data.get("result") != 0:
            print(f"Login failed. Error: {login_data}")
            error_label.config(text="Invalid IP or incorrect credentials")
            return
        
        # Clear error label on successful login
        error_label.config(text="")
        print("Login successful.")

    except requests.exceptions.Timeout:
        print("Request timed out.")
        error_label.config(text="Invalid IP - Connection timed out")
        return
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the device.")
        error_label.config(text="Invalid IP - Please enter a valid IP")
        return
    except ValueError:
        print("Failed to decode JSON from the response.")
        error_label.config(text="Invalid IP - Cannot connect to this IP")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_label.config(text="Invalid IP - Connection failed")
        return

    clear_all_inside_frame()
    update_data(device_ip, username, password)

    def set_y_axis(Y_axis):
        Y_axis = int(float(Y_axis))
        encoder1.set_ylim(0, Y_axis)
        ticks = np.arange(0, Y_axis + 1, 1)
        encoder1.set_yticks(ticks)
        encoder1.set_yticklabels([str(int(tick)) for tick in ticks])
        encoder_graph.draw()

    # Reset the time-series data
   
    times = []
    bits_per_second = []
    target_bits_per_second = []
    rtt_list = []
    buffer_list = []
    packet_loss_list = []   
    # Creating the Title Bar variable
    title = tk.StringVar()
    title.set(f"{box_name} - {ip_address} - {stream_name}")
    
    # Title Bar
    title_bar = tk.Label(main_window, textvariable=title, font=tkFont.Font(size=9, weight="bold"), relief="solid", borderwidth=1)
    title_bar.place(relx=0.483, rely=0.005, anchor="n")

    # Creating the time combobox for window selection
    selected_time = tk.StringVar()
    time_selection = ttk.Combobox(main_window, width=8, state="readonly", textvariable=selected_time, 
                                  values=["1 Min", "10 Mins", "30 Mins", "1 Hour", "3 Hours", "12 Hours"])
    time_selection.place(relx=1, rely=1, anchor="se")
    time_selection.current(0)

    # Creating the CPU Temp variable
    temp = tk.StringVar()
    temp.set(f"CPU Temp: {cpu_temp / 1000:.1f}°C")

    # Creating the Temperature label
    temperature = tk.Label(main_window, textvariable=temp)
    temperature.place(relx=0.4, rely=0.98, anchor="sw")

    # Creating the Stream Type variable
    stream_type_var = tk.StringVar()
    if stream_type == 120:
        stream_type_var.set(f"Stream Type: SRT Caller")
    elif stream_type == 0:
        stream_type_var.set(f"Stream Type: RTMP")
    elif stream_type == 1:
        stream_type_var.set(f"Stream Type: Twitch")
    elif stream_type == 2:
        stream_type_var.set(f"Stream Type: YouTube")
    elif stream_type == 3:
        stream_type_var.set(f"Stream Type: Facebook")
    elif stream_type == 100:
        stream_type_var.set(f"Stream Type: RTSP")
    elif stream_type == 121:
        stream_type_var.set(f"Stream Type: SRT Listener")
    elif stream_type == 130:
        stream_type_var.set(f"Stream Type: NDI HX")
    elif stream_type == 131:
        stream_type_var.set(f"Stream Type: HLS")
    elif stream_type == 132:
        stream_type_var.set(f"Stream Type: TS over UDP")
    elif stream_type == 133:
        stream_type_var.set(f"Stream Type: TS over RTP")
    else: 
        stream_type_var.set(f"Stream Type: No Stream")

    # Creating the Stream Type label
    type_label = tk.Label(main_window, textvariable=stream_type_var)
    type_label.place(relx=1, rely=0.82, anchor="ne")

        # Creating the Uptime variable
    uptime = tk.StringVar()
    uptime_sec = stream_uptime / 1000  # Convert milliseconds to seconds
    
    if uptime_sec < 60:
        uptime.set(f"Stream Uptime: {int(uptime_sec)} secs")
    elif uptime_sec < 3600:
        minutes = int(uptime_sec // 60)
        seconds = int(uptime_sec % 60)
        uptime.set(f"Stream Uptime: {minutes}m {seconds}s")
    else:
        hours = int(uptime_sec // 3600)
        minutes = int((uptime_sec % 3600) // 60)
        uptime.set(f"Stream Uptime: {hours}h {minutes}m")# Creating the Uptime variable
    
    # Creating the Stream Uptime label
    uptime_label = tk.Label(main_window, textvariable=uptime)
    uptime_label.place(relx=1, rely=0.88, anchor="ne")

    # Creating the Stream Status variable
    status = tk.StringVar()
    if stream_status == 22: 
        status.set(f"Stream Status: Connected")
    else: 
        status.set(f"Stream Status: Disconnected")
    
    # Creating the Stream Status label
    status_label = tk.Label(main_window, textvariable=status)
    status_label.place(relx=1, rely=0.76, anchor="ne")
    
    # Create the Back button
    back_button = tk.Button(main_window, text="Back", width=10, command=lambda: [clear_all_inside_frame(), home_screen()])
    back_button.place(relx=0.01, rely=0.01, anchor="nw")

    # Creating Input Status variable

    inputstatus = tk.StringVar()
    if sdi_status == 1:
        inputstatus.set(f"SDI Signal: Connected")
    else: 
        inputstatus.set(f"SDI Signal: Disconnected")
    
    # Creating SDI Signal Status Label
    input_status = tk.Label(main_window, textvariable=inputstatus)
    input_status.place(relx=0.99, rely=0.02, anchor="ne")

    # Creating SDI Signal Resolution and Frame Rate Signal Variable
    SDI_signal = tk.StringVar()
    if sdi_status == 1:
        if interlaced == 1:
            SDI_signal.set(f"Resolution: {cx}x{cy}i {int(frame_rate)}")
        elif interlaced == 0: 
            SDI_signal.set(f"Resolution: {cx}x{cy}P {int(frame_rate)}")
        else: 
            SDI_signal.set(f"Resolution: {cx}x{cy} {int(frame_rate)}")
    else:
        SDI_signal.set(f"Resolution: No Signal")

    # Creating SDI Signal Resolution and Frame Rate Signal Label
    SDI_Resolution = tk.Label(main_window, textvariable=SDI_signal)
    SDI_Resolution.place(relx=0.99, rely=0.08, anchor="ne")

    # Creating Destination IP and Port varible
    ip_port = tk.StringVar()
    
    if dest_ip and dest_port != 0:
        ip_port.set(f"Destination IP: {dest_ip}\n Destination Port: {dest_port}      ")
    else: 
        ip_port.set(f"Destination IP: N/A\n Destination Port: N/A")

    # Creating Destination IP and port label
    Destination = tk.Label(main_window, textvariable=ip_port)
    Destination.place(relx=0.99, rely=0.16, anchor="ne")
    
    # Creating Packet Loss Counter Variable
    pkt_loss_count=tk.StringVar()
    pkt_loss_count.set(f"Total Packets Lost: {packet_loss}")

    # Placing Packet Loss Counter
    pkt_loss_counter = tk.Label(main_window, textvariable=pkt_loss_count)
    pkt_loss_counter.place(relx=0.02, rely=0.98, anchor="sw")

    current_mbps_on = tk.BooleanVar(master=main_window, value=True)
    current_mbps_button = tk.Checkbutton(main_window, text="Current Mbps", variable=current_mbps_on)
    current_mbps_button.var = current_mbps_on
    current_mbps_button.place(relx=0.78, rely=0.29, anchor="nw")
    Tooltip(current_mbps_button, "This is the bitrate the encoder is currently outputting.")
    
    target_mbps_on = tk.BooleanVar(master=main_window)
    target_mbps_button = tk.Checkbutton(main_window, text="Target Mbps", variable=target_mbps_on)
    target_mbps_button.place(relx=0.78, rely=0.38, anchor="nw")
    Tooltip(target_mbps_button, "This is the bitrate the encoder is set to output.")

    rtt_on = tk.BooleanVar(master=main_window)
    rtt_button = tk.Checkbutton(main_window, text="Round Trip Time", variable=rtt_on)
    rtt_button.place(relx=0.78, rely=0.47, anchor="nw")
    Tooltip(rtt_button, "This is the time in milliseconds it takes for a \npacket to travel to the destination and back again.")

    buffer_on = tk.BooleanVar(master=main_window)
    buffer_button = tk.Checkbutton(main_window, text="Buffer", variable=buffer_on)
    buffer_button.place(relx=0.78, rely=0.56, anchor="nw")
    Tooltip(buffer_button, "This is how many milliseconds of video the \nencoder is currently holding in its buffer.")

    packet_loss_on = tk.BooleanVar(master=main_window)
    packet_loss_button = tk.Checkbutton(main_window, text="Packet Loss", variable=packet_loss_on)
    packet_loss_button.place(relx=0.78, rely=0.65, anchor="nw")
    Tooltip(packet_loss_button, "This is the number of packets lost since the last query.")

    # Create the Y Axis Scale
    Yaxis_scale = Scale(main_window, from_=12, to=0, length=275, sliderlength=25, command=set_y_axis)
    Yaxis_scale.set(10)
    Yaxis_scale.place(relx=0.001, rely=0.10)

    # Create the graph
    graph1 = Figure(dpi=50)
    encoder1 = graph1.add_subplot()
    
  
    
    encoder1.set_title(f"{stream_name} Data", fontsize=20)
    encoder1.set_xlabel("Time", fontsize=15)
    encoder1.set_ylabel("Bitrate (Mbps)", fontsize=15)
    encoder1.grid(True, alpha=0.3)
    
    ax2 = encoder1.twinx()
    ax2.set_ylabel("Time (ms)/ Packets Lost", fontsize=15)
    ax2.set_ylim(0, 100)


    # Create line object
    line, = encoder1.plot([], [], 'b-', linewidth=1)
    line2, = encoder1.plot([], [], 'r-', linewidth=1)
    line3, = ax2.plot([], [], 'g-', linewidth=1)
    line4, = ax2.plot([],[], 'y-', linewidth=1)
    bars5 = None  # Will be created/updated dynamically for bar chart


    # Format x-axis to show time
    encoder1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    
    # Set initial y-axis
    encoder1.set_ylim(0, 10)
    encoder1.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    encoder1.set_yticklabels(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])

    # Creating the Legend
    encoder1.legend([line, line2, line3, line4], ["Current Mbps", "Target Mbps", "RTT", "Buffer", "Packet Loss"], loc="upper left", borderpad=0.5, prop={"size":13})

    encoder_graph = FigureCanvasTkAgg(graph1, master=main_window)
    encoder_graph.get_tk_widget().place(relx=0.06, rely=0.9, anchor="sw", relwidth=0.7, relheight=0.8)
    encoder_graph.draw()
    
    def update_home_screen():
        nonlocal flashing
        nonlocal stream_flashing
        global current_packet_loss, previous_packet_loss, first_packet_loss_update

        title.set(f"{box_name} - {ip_address} - {stream_name}")
        temp.set(f"CPU Temp: {cpu_temp / 1000:.1f}°C")
        encoder1.set_title(f"{stream_name} Data", fontsize=20)
        

        
        if stream_type == 120:
            stream_type_var.set(f"Stream Type: SRT Caller")
        elif stream_type == 0:
            stream_type_var.set(f"Stream Type: RTMP")
        elif stream_type == 1:
            stream_type_var.set(f"Stream Type: Twitch")
        elif stream_type == 2:
            stream_type_var.set(f"Stream Type: YouTube")
        elif stream_type == 3:
            stream_type_var.set(f"Stream Type: Facebook")
        elif stream_type == 100:
            stream_type_var.set(f"Stream Type: RTSP")
        elif stream_type == 121:
            stream_type_var.set(f"Stream Type: SRT Listener")
        elif stream_type == 130:
            stream_type_var.set(f"Stream Type: NDI HX")
        elif stream_type == 131:
            stream_type_var.set(f"Stream Type: HLS")
        elif stream_type == 132:
            stream_type_var.set(f"Stream Type: TS over UDP")
        elif stream_type == 133:
            stream_type_var.set(f"Stream Type: TS over RTP")
        else: 
            stream_type_var.set(f"Stream Type: No Stream") 

        if (stream_uptime/1000) < 60:
            uptime.set(f"Stream Uptime: {int(stream_uptime/1000)} secs")
        elif 60 < (stream_uptime/1000) < 3600:
            minutes = int((stream_uptime/1000) // 60)
            seconds = int((stream_uptime/1000) % 60)
            uptime.set(f"Stream Uptime: {minutes}m {seconds}s")
        else:
            hours = int((stream_uptime/1000) // 3600)
            minutes = int(((stream_uptime/1000) % 3600) // 60)
            uptime.set(f"Stream Uptime: {hours}h {minutes}m")

        if sdi_status == 1:
            if interlaced == 1:
                SDI_signal.set(f"Resolution: {cx}x{cy}i {int(frame_rate)}")
            elif interlaced == 0: 
                SDI_signal.set(f"Resolution: {cx}x{cy}P {int(frame_rate)}")
            else: 
                SDI_signal.set(f"Resolution: {cx}x{cy} {int(frame_rate)}")
        else:
            SDI_signal.set(f"Resolution: NO SIGNAL")

        
        if dest_ip and dest_port != 0:
            ip_port.set(f"Destination IP: {dest_ip}\n Destination Port: {dest_port}      ")
        else: 
            ip_port.set(f"Destination IP: N/A\n Destination Port: N/A")
        
        pkt_loss_count.set(f"Total Packets Lost: {packet_loss}")

        def SDI_flash():
            nonlocal flashing  # Add this line
            if not flashing:
                return
            
            current = input_status.cget("bg")
            new_colour = "red" if current == "#F0F0F0" else "#F0F0F0"
            input_status.config(bg=new_colour)
            SDI_Resolution.config(bg=new_colour)
            main_window.after(500, SDI_flash)

        # Inside your update loop:
        if sdi_status == 1:
            flashing = False
            inputstatus.set("SDI Signal: Connected")
            input_status.config(bg="#7EF197")
            SDI_Resolution.config(bg="#F0F0F0")

        elif sdi_status == 0:
            inputstatus.set("SDI Signal: Disconnected")
            input_status.config(bg="#F0F0F0")

            if not flashing:
                flashing = True
                SDI_flash()

        else:
            pass

        def Stream_flash():
            nonlocal stream_flashing  # Add this line
            if not stream_flashing:
                return
            
            stream_current = status_label.cget("bg")
            new_colour = "red" if stream_current == "#F0F0F0" else "#F0F0F0"
            status_label.config(bg=new_colour)
            main_window.after(500, Stream_flash)

        # Inside your update loop:
        if stream_status == 22:
            stream_flashing = False
            status.set(f"Stream Status: Connected")
            status_label.config(bg="#7EF197")
            

        else:
            status.set(f"Stream Status: Disconnected")
            status_label.config(bg="#F0F0F0")

            if not stream_flashing:
                stream_flashing = True
                Stream_flash()

            else:
                pass

        if first_packet_loss_update:
            current_packet_loss = 0
            previous_packet_loss = packet_loss
            first_packet_loss_update = False
        else:
            current_packet_loss = packet_loss - previous_packet_loss
            previous_packet_loss = packet_loss
        

    def get_window_seconds():
        """Convert selected time to seconds"""
        time_str = selected_time.get()
        if time_str == "1 Min":
            return 60
        elif time_str == "10 Mins":
            return 600
        elif time_str == "30 Mins":
            return 1800
        elif time_str == "1 Hour":
            return 3600
        elif time_str == "3 Hours":
            return 10800
        elif time_str == "12 Hours":
            return 43200
        return 60  # Default to 1 minute

    def plot_graph():
        global times, bits_per_second, current_bps, target_bps, target_bits_per_second, rtt_time, current_packet_loss
        
        
        # Update data from encoder
        update_data(device_ip, username, password)
        update_home_screen()
        
        # Always add new data point
        now = datetime.now()
        times.append(now)
        bits_per_second.append(current_bps)
        target_bits_per_second.append(target_bps)
        rtt_list.append(rtt_time)
        buffer_list.append(buffer)
        packet_loss_list.append(current_packet_loss)
        
        # Only start removing old data once we exceed 43200 points (12 hours at 1-second intervals)
        MAX_DATA_POINTS = 43200
        if len(times) > MAX_DATA_POINTS:
            times.pop(0)
            bits_per_second.pop(0)
            target_bits_per_second.pop(0)
            rtt_list.pop(0)
            buffer_list.pop(0)
            packet_loss_list.pop(0)
        
        # Get the time window for display
        window_seconds = get_window_seconds()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Find the index where visible data should start
        start_idx = 0
        for i, t in enumerate(times):
            if t >= cutoff:
                start_idx = i
                break
        
        # Slice the data for plotting (only the visible window)
        visible_times = times[start_idx:]
        visible_bps = bits_per_second[start_idx:]
        visible_target = target_bits_per_second[start_idx:]
        visible_rtt = rtt_list[start_idx:]
        visible_buffer = buffer_list[start_idx:]
        visible_packet_loss = packet_loss_list[start_idx:]

        # Update the line data with only visible portion
        line.set_data(visible_times, visible_bps)
        line2.set_data(visible_times, visible_target)
        line3.set_data(visible_times, visible_rtt)
        line4.set_data(visible_times, visible_buffer)
        
        # Update bar chart for packet loss
        global bars5
        if bars5:
            try:
                for bar in bars5:
                    bar.remove()
            except:
                pass
        if packet_loss_on.get() and visible_packet_loss:
            # Use a small fixed bar width (in days, matplotlib's time unit)
            bar_width = 0.00001  # Very small width for bars
            bars5 = ax2.bar(visible_times, visible_packet_loss, width=bar_width, color='m', alpha=0.6)
        
        # Show or hide the line based on checkbox state
        line.set_visible(current_mbps_on.get())
        line2.set_visible(target_mbps_on.get())
        line3.set_visible(rtt_on.get())
        line4.set_visible(buffer_on.get())
        if not packet_loss_on.get() and bars5:
            try:
                for bar in bars5:
                    bar.remove()
            except:
                pass
            bars5 = None
        
        # Scroll x-axis to show the time window
        encoder1.set_xlim(cutoff, now)
        
        # Auto-scale y-axis based on visible data
        if rtt_on.get() or buffer_on.get() or packet_loss_on.get():
            # Collect all visible data for ax2
            ax2_data = []
            if rtt_on.get() and visible_rtt:
                ax2_data.extend(visible_rtt)
            if buffer_on.get() and visible_buffer:
                ax2_data.extend(visible_buffer)
            if packet_loss_on.get() and visible_packet_loss:
                ax2_data.extend(visible_packet_loss)
            
            if ax2_data:
                # Add some padding (10%) to the limits
                max_val = max(ax2_data)
                padding = max_val * 0.1 if max_val > 0 else 10
                
                # Calculate new max, ensuring minimum range of 100
                new_max = max_val + padding
                final_max = max(100, new_max)
                
                # Always start at 0
                ax2.set_ylim(0, final_max)
            else:
                ax2.set_ylim(0, 100)  # Default range if no data
        else:
            ax2.set_ylim(0, 100)  # Reset to default when both are off
                    
        # Format the x-axis dates
        graph1.autofmt_xdate()
        
        encoder_graph.draw_idle()
        
        # Schedule next update
        main_window.after(1000, plot_graph)
    
    # Bind combobox to redraw when time window changes
    def on_time_change(event):
        # Just trigger a redraw with the new window - plot_graph handles it
        pass
    
    time_selection.bind('<<ComboboxSelected>>', on_time_change)
    
    # Start the update loop
    plot_graph()
    
    return device_ip, username, password

home_screen()

# End
main_window.mainloop()