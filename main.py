#!/usr/bin/env python3

# papà consiglia https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog


def open_file_selector():
    print("Open file selector")
    filename = filedialog.askopenfilename()
    print(filename)

def main():
    root = tk.Tk()
    root.title("ASIM Reborn")
    root.geometry("800x600")
    a = tk.Label(root, text="Hello, World!")
    a.grid()
    btn = tk.Button(root, text="Open file selector", command=open_file_selector)
    btn.grid(column=0, row=1)
    root.mainloop()

if __name__ == "__main__":
    main()
