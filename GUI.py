"""
Image Enchancment GUI, allows user to select images froma folder and prfoem enhcment and anylisis on them
"""
import os
import tkinter as t
from tkinter import ttk, scrolledtext, messagebox

"""
Varibales that need to be global
such as the window
And set up for window
"""
# setting up the capture GUI Frame or Window, captureWindow
enhanceWindow = t.Tk()

# set up our window, size, title, icon
enhanceWindow.geometry("1355x300")
enhanceWindow.title("Image Enhancement")
enhanceWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")  # make our own image

# directory to look for files
dir = t.Entry()

# list of files in directory
files = []
filesChosen=[]
# widget width and other aesthetic constants
width = 20
borderwidth = 2
font = "Helvetica"
fontSize = 12
titleBg = "dim gray"
titleRelief = "groove"
fg = "snow"
bg = "gray"
buttonRelief = "raised"
labelRelief = "flat"
padx = 5
pady = 5

# blank label
blankLabel = t.Label(enhanceWindow, text="")
blankLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)


def makeHelpMenu():
    """

    :return:
    """

    def rightClick(event):
        helpWindow = t.Toplevel(enhanceWindow)
        helpWindow.geometry("300x300")
        helpWindow.title("Help")
        helpWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(helpWindow, width=50, height=50)
        scrollInstruct.pack()
        scrollInstruct.insert(t.INSERT, "ADD SOME INSTRUCTIONS")
        helpWindow.mainloop()

    enhanceWindow.bind("<Button-3>", rightClick)


def makeFileColumn(column):
    """
    Makes a column that has a label asking for a folder, and entry box to enter folder path,
    a button to tell the program to search for that directory and place the file options in the
    drop down
    :param column: column to place
    :return: column increased  by 1
    """
    enterFileLabel = t.Label(enhanceWindow, text="Enter Directory", fg=fg, bg=titleBg)
    enterFileLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
    enterFileLabel.grid(column=column, row=0, padx=padx, pady=pady)
    dir.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
    dir.grid(column=column, row=1)
    blankLabel.grid(column=column, row=2)

    def getFiles():
        """
        This uses the entry box dir and reads the names of the tiff/tif files in that directory
        it then uses the names to make a serires of drop down menus where the user can chooses
        specific images to effect
        :return: None
        """
        # did the user put anything in the directory path box?, if not tell them and stop this function
        if dir.get() =="":
            messagebox.showinfo("ERROR", "Enter Directory")
            return

        # if the user put something in the dir box, is it a valid path?
        if os.path.isdir(dir.get()) == False:
            print(dir.get())
            messagebox.showinfo("ERROR", "Directory not found\n Enter Valid Directory")
            return

        # add a ALL option and a None option, if ALL is the first option the rest are ignored, none allows user
        # to chose less than the amount of images in the dir to effect
        files.append("ALL")
        files.append("None")

        # amount of tiff/tif images in the directory
        amount =0;

        for f in os.listdir(dir.get()):  # for each image in the folder images f is equal to the file name
            # we only want to act on our tiff images, dont want to try to do analysis on a txt file
            if f.endswith(".tiff") or f.endswith(".tif"):
                files.append(f)
                amount +=1

        # amount tells us how many tiff files there are, so we can check to make sure there our tiff files in the dir
        if(amount == 0):
            messagebox.showinfo("ERROR", "No tiff/tif files in directory: " + dir.get())
            return

        # we dont want like 20 drop downs, so we max out the amount at 12 or it stops at the amount of tiff files
        if(amount>12):
            amount = 12

        # place the drop downs
        for i in range(0, amount):
            filesChosen.append(ttk.Combobox(enhanceWindow))
            filesChosen[i].configure(font=(font, fontSize), width=width)
            filesChosen[i]['values'] = files
            filesChosen[i].grid(column=column, row=i + 3)
            filesChosen[i].current(1)

    loadFilesButton = t.Button(enhanceWindow, text="GO", fg=fg, bg=bg)
    loadFilesButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                              command=getFiles)
    loadFilesButton.grid(column=column, row=2, padx=padx, pady=pady)

def makeImageStitchButton(row):


def makeImageConnectionsButtons():
    """
    The second column will contain buttons that connect images in some way.
    This includes image stitching, Image Registration.
    :return:
    """
def makeWidgets():
    """
    calls functions that make widgets for the GUI
    :return:
    """
    column = 0
    makeHelpMenu()
    makeFileColumn(column)
    row=0
    column = makeImageConnectionsButtons()


def main():
    """
    Main function
    :return: NONE
    """
    makeWidgets()

    # Displays the captureWindow GUI
    enhanceWindow.mainloop()


if __name__ == '__main__':
    main()
