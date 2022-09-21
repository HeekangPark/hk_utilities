from tkinter import *
from tkinter.ttk import *

import timer
import threading

import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class RepetitiveTimer(Frame):
    def __init__(self, root, **kw):
        Frame.__init__(self, root)

        root.title("Rep Timer")  # Repetitive Timer
        root.resizable(False, False)
        root.iconbitmap(resource_path("icon.ico"))

        self.pack(fill="both", expand="true")

        # data
        self.timers = []

        # variables
        self.selectedTimer = None
        self.new_timer_idx = 1
        self.repeat = IntVar()
        self.thread = None
        self.display_timer_str = StringVar()
        self.display_timer_str.set("Start!")

        # variables - views
        self.treeview = None
        self.treeview_scrollbar = None
        self.treeview_frame = None
        self.addTimerBtn = None
        self.delTimerBtn = None
        self.upTimerBtn = None
        self.downTimerBtn = None
        self.onceRadioBtn = None
        self.continuallyRadioBtn = None
        self.startBtn = None
        self.stopBtn = None
        self.timeIndicator_frame = None

        # draw
        self.drawTreeviewFrame()
        self.drawTreeviewBtnsFrame()
        self.drawRepeatRadioBtnsFrame()
        self.drawControlBtnsFrame()
        self.drawTimeIndicator()

        self.updateTreeview()
        self.hideTimeIndicator()

    def drawTreeviewFrame(self):
        frame = Frame(self)
        frame.pack(anchor="center", expand="true", padx=10, pady=(10, 0))

        # treeview
        treeview = Treeview(frame, columns=["name", "time"], displaycolumns=["name", "time"], selectmode="browse")
        treeview.pack(side="left")
        treeview.tag_configure("current_timer", background="yellow")

        treeview["show"] = "headings"

        treeview.column("name", width=100, anchor="w")
        treeview.heading("name", text="Name", anchor="center")

        treeview.column("time", width=100, anchor="e")
        treeview.heading("time", text="Time", anchor="center")

        treeview.bind("<<TreeviewSelect>>", func=self.onTreeviewSelected)

        # scrollbar
        treeview_scrollbar = Scrollbar(frame, orient="vertical")
        treeview_scrollbar.pack(side="right", fill="y")

        treeview_scrollbar.configure(command=treeview.yview)
        treeview.configure(yscrollcommand=treeview_scrollbar.set)

        self.treeview = treeview
        self.treeview_scrollbar = treeview_scrollbar
        self.treeview_frame = frame

    def drawTreeviewBtnsFrame(self):
        frame = Frame(self)
        frame.pack(anchor="e", expand="true", padx=10, pady=(0, 10))

        left_frame = Frame(frame)
        left_frame.grid(row=0, column=0)

        addTimerBtn = Button(left_frame, text="+", width="3", command=self.onAddTimerBtnClicked)
        addTimerBtn.grid(row=0, column=0)

        delTimerBtn = Button(left_frame, text="-", width="3", command=self.onDelTimerBtnClicked)
        delTimerBtn.grid(row=0, column=1)

        right_frame = Frame(frame)
        right_frame.grid(row=0, column=1)

        upTimerBtn = Button(right_frame, text="△", width="3", command=self.onUpTimerBtnClicked)
        upTimerBtn.grid(row=0, column=0)

        downTimerBtn = Button(right_frame, text="▽", width="3", command=self.onDownTimerBtnClicked)
        downTimerBtn.grid(row=0, column=1)

        self.addTimerBtn = addTimerBtn
        self.delTimerBtn = delTimerBtn
        self.upTimerBtn = upTimerBtn
        self.downTimerBtn = downTimerBtn

    def drawRepeatRadioBtnsFrame(self):
        frame = Frame(self)
        frame.pack(anchor="center", expand="true", padx=10, pady=(0, 10))

        label = Label(frame, text="Repeat")
        label.pack()

        onceRadioBtn = Radiobutton(frame, text="Once", value=0, variable=self.repeat)
        onceRadioBtn.pack(side="left", padx=(0, 5))

        continuallyRadioBtn = Radiobutton(frame, text="Continually", value=1, variable=self.repeat)
        continuallyRadioBtn.pack(side="right", padx=(5, 0))

        onceRadioBtn.invoke()

        self.onceRadioBtn = onceRadioBtn
        self.continuallyRadioBtn = continuallyRadioBtn

    def drawControlBtnsFrame(self):
        frame = Frame(self)
        frame.pack(anchor="center", expand="true", padx=10, pady=10)

        # Start
        startBtn = Button(frame, text="Start", width="10", command=self.onStartBtnClicked)
        startBtn.pack(side="left")

        # Stop
        stopBtn = Button(frame, text="Stop", width="10", state="disabled", command=self.onStopBtnClicked)
        stopBtn.pack(side="left")

        self.startBtn = startBtn
        self.stopBtn = stopBtn

    def drawTimeIndicator(self):
        frame = Frame(self)

        label = Label(frame, textvariable=self.display_timer_str)
        label.pack()

        self.timeIndicator_frame = frame

    def showTimeIndicator(self):
        self.display_timer_str.set("Start!")
        self.timeIndicator_frame.pack(anchor="center", expand="true", padx=10, pady=(0, 10))

    def hideTimeIndicator(self):
        self.timeIndicator_frame.pack_forget()

    def addTimerPopup(self):
        def validate_time(action, prior_text, new_text):
            if action == '1':  # filter only if inserting
                if len(prior_text) == 0:
                    valid_nums = "123456789"
                else:
                    valid_nums = "0123456789"

                if new_text in valid_nums:
                    return True
                else:
                    return False
            else:
                return True

        def onOKBtnClicked():
            global clicked_btn
            clicked_btn = "OK"
            popup.destroy()

        def onCancelBtnClicked():
            global clicked_btn
            clicked_btn = "Cancel"
            popup.destroy()

        def onEnterKeyPressed(event):
            onOKBtnClicked()

        global clicked_btn
        clicked_btn = None

        popup = Toplevel()
        popup.resizable(False, False)
        popup.title("Add Timer")
        popup.transient(self)  # parent보다 항상 위에 있도록
        popup.grab_set()  # modal
        popup.focus_set()  # window 열릴 때 focus 가져오도록

        # name
        name = StringVar()
        name.set("timer " + str(self.new_timer_idx))

        name_frame = Frame(popup)
        name_frame.pack(padx=5, pady=5)

        label = Label(name_frame, text="Name")
        label.grid(row=0, column=0, sticky="w")

        name_entry = Entry(name_frame, width=50, textvariable=name)
        name_entry.grid(row=1, column=0)

        # time
        time = StringVar()
        time.set("30")

        time_frame = Frame(popup)
        time_frame.pack(padx=5, pady=5)

        label = Label(time_frame, text="Time")
        label.grid(row=0, column=0, sticky="w")

        time_entry = Entry(time_frame, width=47, textvariable=time, validate="key",
                           validatecommand=(popup.register(validate_time), "%d", "%s", "%S"))
        time_entry.bind("<Return>", onEnterKeyPressed)
        time_entry.grid(row=1, column=0)

        label = Label(time_frame, width=3, text="sec", anchor="e")
        label.grid(row=1, column=1)

        # btns
        btn_frame = Frame(popup)
        btn_frame.pack(anchor="e", padx=5, pady=5)

        ok_btn = Button(btn_frame, text="Add", width=8, command=onOKBtnClicked)
        ok_btn.pack(side="left", padx=(0, 5))

        cancel_btn = Button(btn_frame, text="Cancel", width=8, command=onCancelBtnClicked)
        cancel_btn.pack(side="right")

        popup.wait_window()

        if len(name.get()) == 0:
            name.set("timer " + str(self.new_timer_idx))

        if clicked_btn == "OK":
            if len(time.get()) == 0:
                time.set("0")
        else:
            time.set("-1")

        return name.get(), time.get()

    def updateTreeview(self):
        # delete all items
        self.treeview.delete(*self.treeview.get_children())

        # redraw all items
        for i in range(len(self.timers)):
            self.treeview.insert(parent='', index=i, values=self.timers[i], iid=i)

        if self.selectedTimer is None:
            # disable btns as selection reset
            self.delTimerBtn.configure(state="disabled")
            self.upTimerBtn.configure(state="disabled")
            self.downTimerBtn.configure(state="disabled")
        else:
            iid = self.timers.index(self.selectedTimer)
            self.treeview.selection_set(iid)

    def onAddTimerBtnClicked(self):
        name, time = self.addTimerPopup()
        time = int(time)

        if time >= 0:
            self.timers.append((name, time))
            self.new_timer_idx += 1
            self.selectedTimer = self.timers[-1]
            self.updateTreeview()

    def onDelTimerBtnClicked(self):
        if self.selectedTimer is None:
            return

        self.timers.remove(self.selectedTimer)
        self.selectedTimer = None
        self.updateTreeview()

    def onUpTimerBtnClicked(self):
        if self.selectedTimer is None:
            return

        cur_idx = self.timers.index(self.selectedTimer)
        if cur_idx == 0:
            return

        # swap
        up_idx = cur_idx - 1
        self.timers[up_idx], self.timers[cur_idx] = self.timers[cur_idx], self.timers[up_idx]

        self.updateTreeview()

    def onDownTimerBtnClicked(self):
        if self.selectedTimer is None:
            return

        cur_idx = self.timers.index(self.selectedTimer)
        if cur_idx == len(self.timers) - 1:
            return

        # swap
        down_idx = cur_idx + 1
        self.timers[cur_idx], self.timers[down_idx] = self.timers[down_idx], self.timers[cur_idx]

        self.updateTreeview()

    def onStartBtnClicked(self):
        if len(self.timers) == 0:
            return

        # disable repeat radio btns
        self.onceRadioBtn.configure(state="disabled")
        self.continuallyRadioBtn.configure(state="disabled")

        # disable treeview btns as timer starts
        self.addTimerBtn.configure(state="disabled")
        self.delTimerBtn.configure(state="disabled")
        self.upTimerBtn.configure(state="disabled")
        self.downTimerBtn.configure(state="disabled")

        # enable time indicator
        self.showTimeIndicator()

        # run thread
        self.thread = threading.Thread(target=timer.Timer, args=(self.timers, self.repeat.get(), lambda: True if self.thread is None else False, self.onTick, self.onNext, self.onComplete))
        self.thread.start()

        # disable start btn, enable stop btn
        self.startBtn.configure(state="disabled")
        self.stopBtn.configure(state="normal")

    def onStopBtnClicked(self):
        if self.thread is None:
            return

        # disable time indicator
        self.hideTimeIndicator()

        # stop thread
        self.thread = None

        # enable repeat radio btns
        self.onceRadioBtn.configure(state="normal")
        self.continuallyRadioBtn.configure(state="normal")

        # enable treeview btns as timer stops
        self.addTimerBtn.configure(state="normal")
        self.delTimerBtn.configure(state="normal")
        self.upTimerBtn.configure(state="normal")
        self.downTimerBtn.configure(state="normal")

        # enable start btn, disable stop btn
        self.startBtn.configure(state="normal")
        self.stopBtn.configure(state="disabled")

    def onTreeviewSelected(self, event):
        if self.thread is None:
            selected_iid = event.widget.selection()[0]
            self.selectedTimer = self.timers[int(selected_iid)]

            # enable treeview btns as selection set
            self.delTimerBtn.configure(state="normal")
            self.upTimerBtn.configure(state="normal")
            self.downTimerBtn.configure(state="normal")

    def onNext(self):
        def playSound():
            import playsound
            playsound.playsound(resource_path("sound.wav"), block=False)

        playSound()

    def onTick(self, timer_name, sec, total_sec):
        self.display_timer_str.set(str(timer_name) + " : " + str(sec) + "/" + str(total_sec) + " sec")

    def onComplete(self):
        # disable time indicator
        self.hideTimeIndicator()

        # stop thread
        self.thread = None

        # enable repeat radio btns
        self.onceRadioBtn.configure(state="normal")
        self.continuallyRadioBtn.configure(state="normal")

        # enable treeview btns as timer stops
        self.addTimerBtn.configure(state="normal")
        self.delTimerBtn.configure(state="normal")
        self.upTimerBtn.configure(state="normal")
        self.downTimerBtn.configure(state="normal")

        # enable start btn, disable stop btn
        self.startBtn.configure(state="normal")
        self.stopBtn.configure(state="disabled")
