import os
import socket

import tkinter as tk
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import threading
import datetime

# OSC settings
OSC_IP = "192.168.3.112"  # replace with Live Link Face IP address iOS app
OSC_PORT = 9000  # replace with Live Link Face port number
client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

# UI settings
BUTTON_WIDTH = 35
BUTTON_HEIGHT = 1
LABEL_WIDTH = 35

current_take = 1

# create tkinter window
root = tk.Tk()
root.resizable(False, False) #make it fixed
root.title("Live Link Face Control")

# Set window icon
window_icon = tk.PhotoImage(file='C:\FaceControl\F.gif')
# Replace "path_to_icon_image.png" with the actual path to your icon image file
root.iconphoto(True, window_icon)

# Add logo image
logo_image = tk.PhotoImage(file='C:\FaceControl\innoflops.png')
logo_label = tk.Label(root, image=logo_image)
logo_label.pack()

# create battery, thermals, and recording status labels
battery_label = tk.Label(root, text="Battery level: N/A", width=LABEL_WIDTH)
battery_label.pack()

#Haven't figured out how to make thermal works!
#thermals_label = tk.Label(root, text="Thermal state: N/A", width=LABEL_WIDTH)
#thermals_label.pack()

recording_label = tk.Label(root, text="Not recording", width=LABEL_WIDTH, fg='#FFF', font='Arial 10 bold')
recording_label.config(bg="gray")
recording_label.pack()

# define button commands
def start_stream():
    client.send_message("/LiveLinkStreamStart", None)
    start_stream_button.config(state=tk.DISABLED)  # Disable the "Start Streaming" button
    stop_stream_button.config(state=tk.NORMAL)  # Enable the "Stop Streaming" button
    stop_stream_button.config(bg="orange")  	


def stop_stream():
    client.send_message("/LiveLinkStreamStop", None)
    start_stream_button.config(state=tk.NORMAL)  # Enable the "Start Streaming" button
    stop_stream_button.config(state=tk.DISABLED)  # Disable the "Stop Streaming" button
    stop_stream_button.config(bg="SystemButtonFace") #transparent

def start_recording():
    slate = slate_entry.get()
    take = int(take_entry.get())
    global current_take #necesitamos acceder a la variable global
    current_take = take
    client.send_message("/RecordStart", [slate, take])
    recording_label.config(text=f"Recording {slate} (take {take})...")
    recording_label.config(bg="red")
    start_recording_button.config(state=tk.DISABLED)  # Disable the "Start Recording" button
    start_recording_button.config(bg="SystemButtonFace")
    stop_recording_button.config(state=tk.NORMAL)  # Enable the "Stop Streaming" button
    stop_recording_button.config(bg="orange")    
    clear_slate_button.config(state=tk.DISABLED)  # Disable the "Clear Slate" button while recording	
    clear_take_button.config(state=tk.DISABLED)  # Disable the "Clear Take" button while recording

def stop_recording():
    global current_take #necesitamos acceder a la variable global
    current_take += 1
    take_entry.delete(0, tk.END)
    take_entry.insert(0, str(current_take))
    client.send_message("/RecordStop", None)
    start_recording_button.config(state=tk.NORMAL)  # Enable the "Start Recording" button
    start_recording_button.config(bg="red")
    recording_label.config(text="Not recording")
    recording_label.config(bg="gray")
    client.send_message("/Transport", ["192.168.3.106:9001", "C:/Users/i7/Downloads/osc"])
    stop_recording_button.config(bg="SystemButtonFace")
    stop_recording_button.config(state=tk.DISABLED)  # Disable the "Stop Streaming" button
    clear_slate_button.config(state=tk.NORMAL)  # Enable the "Clear Slate" button
    clear_take_button.config(state=tk.NORMAL)  # Enable the "Clear Take" button 


def query_battery():
    print("Query Battery button pressed")	
    client.send_message("/BatteryQuery", None)
	

def query_thermals():
    client.send_message("/ThermalsQuery", None)
    
def clear_slate_entry():
    slate_entry.delete(0, tk.END)

def clear_take_entry():
    global current_take #necesitamos acceder a la variable global
    take_entry.delete(0, tk.END)
    # reseteamos todo a 1
    take_entry.insert(1, "1")
    current_take = 1



# create slate and take number entry fields
slate_label = tk.Label(root, text="Slate:")
slate_label.pack()

slate_entry = tk.Entry(root, font=("arial", 17))
slate_entry.pack()
slate_entry.insert(0, "DefaultClip")
slate_entry.config(bg="lightgreen")

# create clear icons buttons
clear_slate_button = tk.Button(root, text="1 - [Clear Stale]", command=clear_slate_entry)
clear_slate_button.pack()

#break line
label = tk.Label(root, text="\n")
label.pack()

#take numbers
take_label = tk.Label(root, text="Take number:")
take_label.pack()
take_entry = tk.Entry(root, font=("arial", 17))
take_entry.pack()
take_entry.insert(0, "1")
current_take = int(take_entry.get())

# create clear take icons buttons
clear_take_button = tk.Button(root, text="2 - [Clear Take]", command=clear_take_entry)
clear_take_button.pack()
	
# create buttons
start_stream_button = tk.Button(root, text="Start Streaming", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=start_stream)
start_stream_button.pack()

stop_stream_button = tk.Button(root, text="Stop Streaming", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=stop_stream)
stop_stream_button.config(state=tk.DISABLED)  # Disable the "Stop Streaming" button
stop_stream_button.pack()

#break line
label = tk.Label(root, text="\n")
label.pack()

start_recording_button = tk.Button(root, text="Start Recording", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=start_recording, bg="red")
start_recording_button.pack()

stop_recording_button = tk.Button(root, text="Stop Recording", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=stop_recording)
stop_recording_button.config(state=tk.DISABLED)  # Disable the "Stop Recording" button
stop_recording_button.pack()

query_battery_button = tk.Button(root, text="Query Battery", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=query_battery)
query_battery_button.pack()

#footer
label = tk.Label(root, text="\nLive Link Face Remote Controller")
label.pack()

#query_thermals_button = tk.Button(root, text="Query Thermals", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=query_thermals)
#query_thermals_button.pack()

# create OSC server to receive messages
dispatcher = dispatcher.Dispatcher()
server = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 9001), dispatcher)

# define OSC message handlers
def handle_battery_query(address, level):
    battery_label.config(text=f"Battery level: {level * 100:.0f}%")
    print(f"Received battery level: {level * 100:.0f}%")
    root.update()

def handle_thermals(address, state):
    thermals_label.config(text=f"Thermal state: {state}")
    root.update()

def handle_record_start_confirm(address, timecode):
    timecode = datetime.datetime.strptime(timecode, "%H:%M:%S.%f")
    recording_label.config(text=f"Recording...")    
    root.update()

#def handle_record_stop_confirm(address, timecode, blendshapes_csv, reference_mov):
#    timecode_label.config(text=f"Timecode: {timecode}")
#    root.update()

"""
def transport_files(ip, port, path):
    # create TCP connection to specified IP address and port
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ip, port))

    # send path to app
    print(f"Sending path {path} to app")
    conn.sendall(path.encode())

    # receive file size
    size_bytes = conn.recv(4)
    size = int.from_bytes(size_bytes, byteorder='big')
    print(f"Received file size {size} for {path}")

    # receive file contents and save to disk
    filename = os.path.basename(path)
    destination = os.path.join("C:/Users/i7/Downloads/osc", filename)
    print(f"Saving file to {destination}")
    with open(destination, 'wb') as f:
        while size > 0:
            chunk = conn.recv(1024)
            if not chunk:
                break
            f.write(chunk)
            size -= len(chunk)
    print(f"Download complete for {path}")

    # close connection
    conn.close()
"""
	
def handle_record_stop_confirm(address, timecode, blendshapes_csv, reference_mov):
    print(f"Downloading {reference_mov} and {blendshapes_csv}")
    timecode_label.config(text=f"Timecode: {timecode}")
    root.update()

# map OSC messages to handlers
dispatcher.map("/Battery", handle_battery_query)
#dispatcher.map("/Thermals", handle_thermals)
dispatcher.map("/RecordStartConfirm", handle_record_start_confirm)


# start OSC server in a separate thread
def start_server_thread():
    server.serve_forever()

server_thread = threading.Thread(target=start_server_thread, daemon=True)
server_thread.start()

# run tkinter main loop
root.mainloop()

