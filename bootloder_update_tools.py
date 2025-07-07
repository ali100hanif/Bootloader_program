import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import socket
import threading
import struct
import os
from tkinter import messagebox
import time

clicked_btn = 'a1'
is_server_started=False
selected_page=1;
program_flag=0
program_sts=1
flash_bufer=[]
prom_bufer=[]
prom_bufer=[]
serial_versin_bufer=[]
conected_device_msg=[]

def on_closing():
    global app_state
    #print("Application is closing...")
    app_state = "not running"
    root.destroy()


    
def test_server():
    # Create a socket object
    global is_server_started
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Get local machine name
    host = '192.168.60.20'
    port = 9997
    
    # Connection to hostname on the port
    try:
        client_socket.connect((host, port))
        client_socket.send("aaa".encode('utf-8'))
        response = client_socket.recv(255)#.decode('utf-8')
        response=list(response)
        #print(response)
        if response[0]==97 and response[1]==97 and response[2]==97 :
            is_server_started=True
        client_socket.close()
    except:
        is_server_started=False
        client_socket.close()

def show_message(sub,mess):
    messagebox.showinfo(sub, mess)

def start_server():
    global flash_bufer
    global prom_bufer
    global program_flag
    global program_sts
    global serial_versin_bufer
    global conected_device_msg
    global selected_page
    global app_state
    global is_server_started
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = '192.168.60.20'
    port = 9997
    server_socket.bind((host, port))
    server_socket.listen(5)
    #print("Server is listening...")
    program_sts=0
    while app_state == "running":
        #print('1')
        client_socket, addr = server_socket.accept()
        if str(addr).split('.')[-1][0:3]=='120':
            is_server_started=1
            
              
        if len(conected_device_msg)>5:
            conected_device_msg=[]
        conected_device_msg.append(f"Connection from {addr} has been established.")
        frame1.show_connected_device()
        while app_state == "running":
            try:
                #print('2')
                data = client_socket.recv(1024)
                data=list(data)
                #print(data)
                numbers = [i&0xff for i in range(1024)]
                if data[0]==97 and data[1]==97 and data[2]==97 :
                    client_socket.send("aaa".encode('utf-8'))
                elif data[0]==97 and data[1]==99 and data[2]==122 :
                    #print('len_flashbufer',len(flash_bufer))
                    numbers[0:3]=data[0:3]
                    if data[3]==0:
                        numbers[3]=program_sts
                        numbers[4]=program_flag
                        numbers[5]=selected_page
                        packed_data = struct.pack('!1024B', *numbers)
                        client_socket.send(packed_data)
                    elif data[3]==1:
                        #print('lenfiush=',len(flash_bufer))
                        numbers[3]=len(flash_bufer)//256
                        numbers[4]=len(flash_bufer)&0xff
                        numbers[5]=data[4]
                        numbers[6]=data[5]
                        numbers[7:519]=flash_bufer[(data[4]*256+data[5])]
                        #print('a=',data[4], data[5])
                        frame2.prgraming_show(1,((data[4]*256+data[5])*100)//len(flash_bufer))
                        frame2.prgraming_show_label(1,str(((data[4]*256+data[5])*100)//len(flash_bufer)))
                        packed_data = struct.pack('!1024B', *numbers)
                        client_socket.send(packed_data)
                    elif data[3]==2:
                        numbers[3]=len(prom_bufer)
                        numbers[4]=data[4]
                        #print('numbers[4]',numbers[4],'numbers[3]',numbers[3])
                        numbers[5:517]=prom_bufer[data[4]]
                        frame3.prgraming_show(1,((data[4])*100)//len(prom_bufer))
                        frame3.prgraming_show_label(1,str(((data[4])*100)//len(prom_bufer)))
                        packed_data = struct.pack('!1024B', *numbers)
                        client_socket.send(packed_data)
                    elif data[3]==3:
                        #print('hhhhhhhhhhh',serial_versin_bufer)
                        numbers[4]=ord('d')
                        numbers[5:517]=serial_versin_bufer
                        #print(numbers)
                        packed_data = struct.pack('!1024B', *numbers)
                        client_socket.send(packed_data)
                    elif data[3]==4:
                        flash_bufer=[]
                        prom_bufer=[]
                        serial_versin_bufer=[]
                        program_sts=0
                        program_flag=0
                        numbers[3]=data[4]
                        if data[4]==3:
                            frame2.prgraming_show(0,0)
                            frame2.prgraming_show_label(0,str('r'))
                            packed_data = struct.pack('!1024B', *numbers)
                            client_socket.send(packed_data)
                            message_thread = threading.Thread(target=show_message, args=("secssess",
                                                                                         "Flash memory programing is done"))
                            message_thread.start()
                        elif data[4]==4:
                            frame3.prgraming_show(0,0)
                            frame3.prgraming_show_label(0,str('r'))
                            packed_data = struct.pack('!1024B', *numbers)
                            client_socket.send(packed_data)
                            message_thread = threading.Thread(target=show_message, args=("secssess",
                                                                                         'E2prom memory programing is done'))
                            message_thread.start()
                            
                        elif data[4]==5:
                            packed_data = struct.pack('!1024B', *numbers)
                            client_socket.send(packed_data)
                            message_thread = threading.Thread(target=show_message, args=("secssess",
                                                                                         'Serial/HW version is changed'))
                            message_thread.start()

                    elif data[3]==5:
                        flash_bufer=[]
                        prom_bufer=[]
                        serial_versin_bufer=[]
                        program_sts=0
                        program_flag=0
                        numbers[3]=data[4]
                        if data[4]==3:
                            frame2.prgraming_show(0,0)
                            frame2.prgraming_show_label(0,str('r'))
                            packed_data = struct.pack('!1024B', *numbers)
                            client_socket.send(packed_data)
                            message_thread = threading.Thread(target=show_message, args=("Failure",
                                                                                         'Flash memory programing is Failed'))
                            message_thread.start()                        
                            messagebox.showinfo("Failure", 'Flash memory programing is Failed')
                        elif data[4]==4:
                            frame3.prgraming_show(0,0)
                            frame3.prgraming_show_label(0,str('r'))
                            packed_data = struct.pack('!1024B', *numbers)
                            client_socket.send(packed_data)
                            message_thread = threading.Thread(target=show_message, args=("Failure",
                                                                                         'E2prom memory programing is Failed'))
                            message_thread.start()
                            
                        elif data[4]==5:
                            packed_data = struct.pack('!1024B', *numbers)
                            client_socket.send(packed_data)
                            message_thread = threading.Thread(target=show_message, args=("Failure",
                                                                                         'Serial/HW version changing is Failed'))
                            message_thread.start()
                            messagebox.showinfo("Failure", 'Serial/HW version changing is Failed')
                else:
                    numbers = [i&0xff for i in range(1024)]
                    packed_data = struct.pack('!1024B', *numbers)
                    client_socket.send(packed_data)
            except:
                client_socket.close()
                is_server_started=0
                break
    server_socket.close()

class Page_select(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        
        self.a3 = tk.Button(self,name='a1', bd=5, borderwidth=0, text="Start Server", bg='lightblue',
                            font=("Helvetica", 12), anchor="center", justify="center")
        self.a4 = tk.Button(self,name='a2', bd=5, borderwidth=0, text="Flash program", bg='lightgreen', 
                            font=("Helvetica", 12), anchor="center", justify="center")
        self.a5 = tk.Button(self,name='a3', bd=5, borderwidth=0, text="Eeprom Program", bg='lightgreen', 
                            font=("Helvetica", 12), anchor="center", justify="center")
        self.a6 = tk.Button(self,name='a4', bd=5, borderwidth=0, text="Write Version", bg='lightgreen', 
                            font=("Helvetica", 12), anchor="center", justify="center")
        
        self.a6.place(x=0, y=220, width=200, height=40)
        self.a5.place(x=0, y=180, width=200, height=40)
        self.a4.place(x=0, y=140, width=200, height=40)
        self.a3.place(x=0, y=100, width=200, height=40)
        
        self.a6.bind("<Enter>", self.on_enter)
        self.a6.bind("<Leave>", self.on_leave)
        self.a5.bind("<Enter>", self.on_enter)
        self.a5.bind("<Leave>", self.on_leave)
        self.a4.bind("<Enter>", self.on_enter)
        self.a4.bind("<Leave>", self.on_leave)
        self.a3.bind("<Enter>", self.on_enter)
        self.a3.bind("<Leave>", self.on_leave)
        
        self.a6.bind("<Button-1>", self.btnclc)
        self.a5.bind("<Button-1>", self.btnclc)
        self.a4.bind("<Button-1>", self.btnclc)
        self.a3.bind("<Button-1>", self.btnclc)
        
    def btnclc(self, event):
        global clicked_btn
        global selected_page
        global program_sts
        if program_sts ==0:
            clicked_btn = str(event.widget._name)
            selected_page=int(clicked_btn.split('a')[1])
            self.a3.config(bg="lightgreen")
            self.a4.config(bg="lightgreen")
            self.a5.config(bg="lightgreen")
            self.a6.config(bg="lightgreen")
            event.widget.configure(bg="lightblue")
            if selected_page==1:
                frame0.pack(side="left", fill="both", expand=True)
                frame1.pack(side="right", fill="both", expand=True)
                frame2.pack_forget()
                frame3.pack_forget()
                frame4.pack_forget()
            elif selected_page==2:
                frame0.pack(side="left", fill="both", expand=True)
                frame1.pack_forget()
                frame2.pack(side="right", fill="both", expand=True)
                frame3.pack_forget()
                frame4.pack_forget()
            elif selected_page==3:
                frame0.pack(side="left", fill="both", expand=True)
                frame1.pack_forget()
                frame2.pack_forget()
                frame3.pack(side="right", fill="both", expand=True)
                frame4.pack_forget()
            elif selected_page==4:
                frame0.pack(side="left", fill="both", expand=True)
                frame1.pack_forget()
                frame2.pack_forget()
                frame3.pack_forget()
                frame4.pack(side="right", fill="both", expand=True)

            
    def on_enter(self, event):
        event.widget.configure(bg="white")
        
    def on_leave(self, event):
        global clicked_btn
        if clicked_btn != event.widget._name:
            event.widget.configure(bg="lightgreen")
        else:
            event.widget.configure(bg="lightblue")

class Page_fram1(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.b1=tk.Label(self, text="FARA-AFRAND Co", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.b2=tk.Label(self, text="BootLoder Update tools", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.b3=tk.Label(self, text="Please change your ip to 192.168.60.20", bg='lightblue', fg="red",
                         font=("Helvetica", 12))
        self.b4 = tk.Label(self, text="Please Click the button to start server", bg='lightblue', fg="red",
                           font=("Helvetica", 12))
        self.b5 = tk.Button(self, bd=20, borderwidth=5, text="Start Server", bg='gray',
                            font=("Helvetica", 12), anchor="center", justify="center")
        #self.b6 = tk.Button(self, bd=20, borderwidth=5, text="Test Server", bg='gray',
        #                    font=("Helvetica", 12), anchor="center", justify="center")
        self.b7=tk.Label(self, text="", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.b1.place(x=150, y=15)
        self.b2.place(x=140, y=40)
        self.ip =self.get_ethernet_ip()
        if self.ip[0]=='192' and self.ip[1]=='168' and self.ip[2]=='60' and self.ip[3]=='20':
            self.b4.place(x=140, y=80)
            self.b5.place(x=100, y=150, width=300, height=40)
            self.b5.bind("<Button-1>", self.btnserver)
            #self.b6.place(x=100, y=150, width=300, height=40)
            self.b7.place(x=50, y=220,anchor="nw")
            #self.b6.bind("<Button-1>", self.btnserver2)
        else:
            self.b3.place(x=140, y=80)
    def get_ethernet_ip(self):
        hostname = socket.gethostname()
        ethernet_ip = socket.gethostbyname(hostname)
        return ethernet_ip.split('.')
    def btnserver(self, event):
        event.widget.configure(bg="lightgreen")
        event.widget.configure(text="Server Started")
        self.start_server_thread()
    def btnserver2(self, event):
        event.widget.configure(bg="lightgreen")
        event.widget.configure(text="Server tested")
        self.test_server_thread()
    def start_server_thread(self):
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
    def test_server_thread(self):
        test_server_thread = threading.Thread(target=test_server)
        test_server_thread.daemon = True
        test_server_thread.start()
    def show_connected_device(self):
        global conected_device_msg
        txt=''
        for i in  conected_device_msg:
            txt=txt+i+'\n' 
        self.b7.config(text=txt)
        self.b7.update_idletasks()

        

class Page_fram2(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.c1=tk.Label(self, text="FARA-AFRAND Co", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.c2=tk.Label(self, text="BootLoder Update tools", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.c3=tk.Label(self, text="1. Please Select your HEX file", bg='lightblue', fg="red", font=("Helvetica", 10))
        self.c4 = tk.Label(self, text="2. Clic on program buuton ", bg='lightblue', fg="red", font=("Helvetica", 10))
        self.c5 = tk.Label(self, text="3. Wait until programing is DONE" , bg='lightblue', fg="red",
                           font=("Helvetica", 10))
        self.c6 = tk.Entry(self)
        self.c7 = tk.Button(self, bd=20, borderwidth=5, text="Select HEX file", bg='gray',
                            font=("Helvetica", 9), anchor="center", justify="center",command=self.select_file)
        self.c8 = tk.Button(self, bd=20, borderwidth=3, text="Program flash memory", bg='gray',
                            font=("Helvetica", 9), anchor="center", justify="center",command=self.program_file)
        self.progress_var = tk.IntVar()
        self.c9= ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.c10 = tk.Label(self, text="jhgjgjg" , bg='lightblue', fg="red", font=("Helvetica", 10))
        
        self.c1.place(x=150, y=15)
        self.c2.place(x=140, y=40)
        self.c3.place(x=110, y=95)
        self.c4.place(x=110, y=115)
        self.c5.place(x=110, y=135)
        self.c6.place(x=40, y=175, width=400, height=30)
        self.c7.place(x=450, y=175, width=120, height=30)
        self.c8.place(x=430, y=315, width=140, height=30)
        self.c9.place(x=40, y=315, width=370, height=30)
        self.c10.place(x=230, y=355)
        self.c9.place_forget()
        self.c10.place_forget()
        #self.c7.bind("<Button-1>", self.select_file)
        #self.b6.place(x=100, y=150, width=300, height=40)
        #self.b6.bind("<Button-1>", self.btnserver2)
    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.c6.delete(0, tk.END)
            self.c6.insert(0, file_path)
    def program_file(self):
        global is_server_started
        global program_flag
        global program_sts
        global flash_bufer
        alarm=''
        #ib=1
        
        if is_server_started==False:
            alarm=' Server is Not run \n or not connected to board'
        #    ib=ib+1
        file_path = self.c6.get()
        if (os.path.isfile(file_path))==False:
            alarm=alarm+' the file is not exist'
        if alarm !='':
            messagebox.showinfo("ERROR MASSAGE", alarm)
        else:
            aa=[]
            with open(file_path, "r") as file:
                for line in file:
                    if(line[7:9]=='00'):
                        hhh=2*int(line[1:3],16)
                        for i in range(hhh//2):
                            aa.append(int(line[2*i+9:2*i+11], 16))
            if (len(aa)%512) !=0:
                for i in range(512-(len(aa)%512)):
                    aa.append(0xff)
            flash_bufer=[aa[i:i+512] for i in range(0, len(aa), 512)]
            if len(flash_bufer)==0:
                alarm='the file is empty'
                messagebox.showinfo("ERROR MASSAGE", alarm)
            elif len(flash_bufer)>256:
                alarm='the selected file is large'
                messagebox.showinfo("ERROR MASSAGE", alarm)
            else:
                program_flag=1
                program_sts=1
            
    def prgraming_show(self,show_flag,present):
        if show_flag :
            #if self.c9.winfo_ismapped():
             #   self.c9.place(x=40, y=315, width=370, height=30)
            self.progress_var.set(present)
            self.update_idletasks()
            self.c9.place(x=40, y=315, width=370, height=30)
        else:
            self.c9.place_forget()
    def prgraming_show_label(self,show_flag,txt):
        if show_flag:
            self.c10.config(text=txt)
            self.c10.update_idletasks()
            self.c10.place(x=230, y=355)
            
        else:
            self.c10.place_forget()
            


            
            
class Page_fram3(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.d1=tk.Label(self, text="FARA-AFRAND Co", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.d2=tk.Label(self, text="BootLoder Update tools", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.d3=tk.Label(self, text="1. Please Select your EEPROM file", bg='lightblue', fg="red", font=("Helvetica", 10))
        self.d4 = tk.Label(self, text="2. Clik on program buton ", bg='lightblue', fg="red", font=("Helvetica", 10))
        self.d5 = tk.Label(self, text="3. Wait until programing is DONE" , bg='lightblue', fg="red",
                           font=("Helvetica", 10))
        self.d6 = tk.Entry(self)
        self.d7 = tk.Button(self, bd=20, borderwidth=5, text="Select EEP file", bg='gray',
                            font=("Helvetica", 9), anchor="center", justify="center",command=self.select_file)
        self.d8 = tk.Button(self, bd=20, borderwidth=3, text="Program eeprom memory", bg='gray',
                            font=("Helvetica", 9), anchor="center", justify="center",command=self.program_file)
        self.progress_var2 = tk.IntVar()
        self.d9= ttk.Progressbar(self, variable=self.progress_var2, maximum=100)
        self.d10 = tk.Label(self, text="jhgjgjg" , bg='lightblue', fg="red", font=("Helvetica", 10))
        
        
        self.d1.place(x=150, y=15)
        self.d2.place(x=140, y=40)
        self.d3.place(x=110, y=95)
        self.d4.place(x=110, y=115)
        self.d5.place(x=110, y=135)
        self.d6.place(x=40, y=175, width=400, height=30)
        self.d7.place(x=450, y=175, width=120, height=30)
        self.d8.place(x=440, y=315, width=150, height=30)
        self.d9.place(x=40, y=315, width=370, height=30)
        self.d10.place(x=230, y=355)
        self.d9.place_forget()
        self.d10.place_forget()
        #self.c7.bind("<Button-1>", self.select_file)
        #self.b6.place(x=100, y=150, width=300, height=40)
        #self.b6.bind("<Button-1>", self.btnserver2)
    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.d6.delete(0, tk.END)
            self.d6.insert(0, file_path)
    def program_file(self):
        global is_server_started
        global program_flag
        global program_sts
        global prom_bufer
        alarm=''
        #ib=1
        if is_server_started==False:
            alarm=' Server is Not run \n or not connected to board'
            #ib=ib+1
        file_path = self.d6.get()
        if (os.path.isfile(file_path))==False:
            alarm=alarm+'the file is not exist'
        if alarm !='':
            messagebox.showinfo("ERROR MASSAGE", alarm)
        else:
            aa=[]
            with open(file_path, "r") as file:
                for line in file:
                    if(line[7:9]=='00'):
                        hhh=2*int(line[1:3],16)
                        for i in range(hhh//2):
                            aa.append(int(line[2*i+9:2*i+11], 16))
            if (len(aa)%512) !=0:
                for i in range(512-(len(aa)%512)):
                    aa.append(0xff)
            prom_bufer=[aa[i:i+512] for i in range(0, len(aa), 512)]
            
            #print('len',len(prom_bufer),prom_bufer)
            if len(prom_bufer)==0:
                alarm='the file is empty'
                messagebox.showinfo("ERROR MASSAGE", alarm)
            elif len(prom_bufer)>6:
                alarm='the Selected file is not valid'
                messagebox.showinfo("ERROR MASSAGE", alarm)
            else:
                program_flag=2
                program_sts=1
            
    def prgraming_show(self,show_flag,present):
        if show_flag :
            #if self.c9.winfo_ismapped():
             #   self.c9.place(x=40, y=315, width=370, height=30)
            self.progress_var2.set(present)
            self.update_idletasks()
            self.d9.place(x=40, y=315, width=370, height=30)
        else:
            self.d9.place_forget()
    def prgraming_show_label(self,show_flag,txt):
        if show_flag:
            self.d10.config(text=txt)
            self.d10.update_idletasks()
            self.d10.place(x=230, y=355)
            
        else:
            self.d10.place_forget()
            

            
            
class Page_fram4(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.vcmd = (self.register(self.validate_input), '%P')
        self.vcmd2 = (self.register(self.validate_input2), '%P')
        
        self.e1=tk.Label(self, text="FARA-AFRAND Co", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.e2=tk.Label(self, text="BootLoder Update tools", bg='lightblue', fg="red", font=("Helvetica", 12))
        self.e3=tk.Label(self, text="1. Please enter  the hardware version and serial number", bg='lightblue',
                         fg="red", font=("Helvetica", 10))
        self.e4 = tk.Label(self, text="2. Clik on update buton ", bg='lightblue', fg="red", font=("Helvetica", 10))
        self.e5 = tk.Label(self, text="3. Wait until updating is DONE" , bg='lightblue', fg="red", font=("Helvetica", 10))
        self.e6 = tk.Label(self, text="Hardware Version:" , bg='lightblue', fg="red", font=("Helvetica", 10))
        self.e7 = tk.Entry(self, validate='key', borderwidth=0, validatecommand=self.vcmd)
        self.e8 = tk.Label(self,bd=0, text="." , bg='white', fg="red", font=("Helvetica", 20),
                           borderwidth=0 ,anchor="center", justify="center")
        self.e9 = tk.Entry(self, validate='key', borderwidth=0, validatecommand=self.vcmd)
        self.e10 = tk.Label(self, text="Serial Number:" , bg='lightblue', fg="red", font=("Helvetica", 10))
        self.e11 = tk.Entry(self, validate='key', validatecommand=self.vcmd2)
        self.e12 = tk.Button(self, bd=20, borderwidth=3, text="Update", bg='gray',
                            font=("Helvetica", 9), anchor="center", justify="center",command=self.Update)
        
        
        self.e1.place(x=150, y=15)
        self.e2.place(x=140, y=40)
        self.e3.place(x=110, y=95)
        self.e4.place(x=110, y=115)
        self.e5.place(x=110, y=135)
        self.e6.place(x=50, y=193)
        self.e8.place(x=178, y=190, width=12, height=30)
        self.e7.place(x=160, y=190, width=20, height=30)
        self.e9.place(x=188, y=190, width=20, height=30)
        self.e10.place(x=50, y=235)
        self.e11.place(x=140, y=232, width=70, height=30)
        self.e12.place(x=430, y=315, width=140, height=30)
        
        
        
            
    def validate_input(self,new_value):
        #if (len(new_value) < 3  and new_value.isdigit()) or new_value==None:
        if (len(new_value) < 3  and new_value.isdigit()) or new_value=='':
            return True
        return False
    
    def validate_input2(self,new_value):
        #if (len(new_value) < 3  and new_value.isdigit()) or new_value==None:
        if (len(new_value) < 6  and new_value.isdigit()) or new_value=='':
            return True
        return False
    def Update(self):
        global serial_versin_bufer
        global program_flag
        global program_sts
        alarm=''
        if is_server_started==False:
            alarm=' Server is Not run \n'
            #ib=ib+1
        val1  = self.e7.get()
        val2  = self.e9.get()
        val3  = self.e11.get()
        if (val1)=='' or (val2)=='' :
            alarm=alarm+' Hardware version  not entered. \n'
        if (val3)=='':
            alarm=alarm+' Serial code not entered. \n'
        if alarm !='':
            messagebox.showinfo("ERROR MASSAGE", alarm)
        else:
            value1=int(val1)
            value2=int(val2)
            value3=int(val3)
            serial_versin_bufer=[0xff for i in range(512)]
            serial_versin_bufer[0x11:0x15]= [value1//10,value1%10,value2//10,value2%10]       
            serial_versin_bufer[0x1b:0x20]=[(value3//10000),(value3//1000)%10,(value3//100)%10,(value3//10)%10,(value3)%10]
            program_flag=3
            program_sts=1
            
            
            
            
            
root = tk.Tk()
root.wm_title("Bootlooder Update Tools")
root.geometry("800x500")
root['bg'] = 'lightblue'

frame0 = Page_select(root , bg= 'lightgreen', width=0, height=300)
frame1 = Page_fram1( root ,  bg= 'lightblue'  , width=400, height=300)
frame2 = Page_fram2( root ,  bg= 'lightblue'  , width=400, height=300)
frame3 = Page_fram3( root ,  bg= 'lightblue'  , width=400, height=300)
frame4 = Page_fram4( root ,  bg= 'lightblue'  , width=400, height=300)
app_state ="running"
frame0.pack(side="left", fill="both", expand=True)
frame1.pack(side="right", fill="both", expand=True)

#frame2.pack_forget()
root.protocol("WM_DELETE_WINDOW", on_closing)

  
root.mainloop()