import tkinter as tk
from ui.layout import AppLayout

def main():
    root = tk.Tk()
    app  = AppLayout(root)
    root.mainloop()

if __name__ == "__main__":
    main()