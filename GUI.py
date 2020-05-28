"""
Image Enchancment GUI, allows user to select images froma folder and prfoem enhcment and anylisis on them
"""
import os
import tkinter as t
from tkinter import ttk, scrolledtext, messagebox
import numpy as np
import cv2
import imutils
from PIL import Image  # module that makes this code possible
from PIL import ImageOps

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
filesOptions = []

filesChosen = []
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
count = 0

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


def getFiles():
    """
    This uses the entry box dir and reads the names of the tiff/tif files in that directory
    it then uses the names to make a series of drop down menus where the user can chooses
    specific images to effect
    :return: None
    """
    # did the user put anything in the directory path box?, if not tell them and stop this function
    if dir.get() == "":
        messagebox.showinfo("ERROR", "Enter Directory")
        return

    # if the user put something in the dir box, is it a valid path?
    if not os.path.isdir(dir.get()):
        messagebox.showinfo("ERROR", "Directory not found\n Enter Valid Directory")
        return

    # add a ALL option and a None option, if ALL is the first option the rest are ignored, none allows user
    # to chose less than the amount of images in the dir to effect
    filesOptions.append("ALL")
    filesOptions.append("None")

    for f in os.listdir(dir.get()):  # for each image in the folder images f is equal to the file name
        # we only want to act on our tiff images, dont want to try to do analysis on a txt file
        if f.endswith(".tiff") or f.endswith(".tif"):
            if f not in files:
                files.append(f)
                filesOptions.append(f)

    if len(files)==0:
        messagebox.showinfo("ERROR", "Directory did not contain tiff or tif files")
        return
    # place the drop downs
    for i in range(0, 12):
        if i == len(files):
            break
        filesChosen.append(ttk.Combobox(enhanceWindow))
        filesChosen[i].configure(font=(font, fontSize), width=width)
        filesChosen[i]['values'] = filesOptions
        filesChosen[i].grid(column=0, row=i + 3)
        filesChosen[i].current(1)


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

    loadFilesButton = t.Button(enhanceWindow, text="GO", fg=fg, bg=bg)
    loadFilesButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                              command=getFiles)
    loadFilesButton.grid(column=column, row=2, padx=padx, pady=pady)
    return column + 1


def getFilesInDrop():
    """
    gets a list of files selected, to avoid duplicates or emptyness
    :return:
    """
    names = []
    if len(filesChosen) == 0:
        return ["No files available"]
    for f in filesChosen:
        fName = f.get()
        if fName not in names:
            if fName == "ALL":
                return files
            if fName != "None":
                names.append(fName)
    if len(names) == 0:
        return ["No files chosen"]
    return names


def makeCropButton(column, row):
    """
    makes button to crop image, and action even for button
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def cropButtonPushed():
        """
        when the crop button is pushed we want to open another window that asks for the crop factor
        the excecutes croping
        :return:
        """
        cropWindow = t.Toplevel(enhanceWindow)
        cropWindow.geometry("300x300")
        cropWindow.title("Crop")
        cropWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(cropWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a crop factor. The pixel \nwidth and height of the image will\nbe divide by "
                              "this factor and the\nresult removed from each side.")
        cropFactor = t.Entry(cropWindow)
        cropFactor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        cropFactor.grid(column=0, row=1)

        def cropPushed():
            """
            Get factor, check if files are there and crop
            :return:
            """
            listOfNames = getFilesInDrop()
            toCrop = [];
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            else:
                toCrop = listOfNames
            for x in toCrop:
                if len(x) > 0:
                    image1 = Image.open(dir.get() + "\\" + x)
                    image2 = ImageOps.crop(image1, image1.size[1] // int(cropFactor.get()))
                    image2.save(dir.get() + "\\" + "cropped-" + cropFactor.get() + "-" + x)
            getFiles()
            cropWindow.destroy()

        cropButton = t.Button(cropWindow, text="Crop", fg=fg, bg=bg)
        cropButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                             command=cropPushed)
        cropButton.grid(column=0, row=2, padx=padx, pady=pady)
        cropWindow.mainloop()

    cropWindowButton = t.Button(enhanceWindow, text="Crop Menu", fg=fg, bg=bg)
    cropWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                               command=cropButtonPushed)
    cropWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row +1


def makeImageStitchButton(column, row):
    """
    makes button to stitch images, and action even for button
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """
    def stitchButtonPushed():
        """
        when the stitch button is pushed we want to open another window that asks for the
        name of the output image, then executes stitching
        :return:
        """
        stitchWindow = t.Toplevel(enhanceWindow)
        stitchWindow.geometry("300x300")
        stitchWindow.title("Image Stitching")
        stitchWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(stitchWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a output file Name without\nextension. Images chosen will be\nstitched together.")
        name = t.Entry(stitchWindow)
        name.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        name.grid(column=0, row=1)

        def stitchPushed():
            """
            Get name, check that theirs file to stitch and a name
            :return:
            """
            listOfNames = getFilesInDrop()
            images=[]
            if len(name.get()) < 1:
                messagebox.showinfo("ERROR", "Enter Image Name")
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            else:
                toStitch = listOfNames
            for i in toStitch:
                image = cv2.imread(dir.get() + "\\"+ i)
                images.append(image)
                stitcher = cv2.Stitcher_create() if imutils.is_cv3() else cv2.Stitcher_create()
                (status, stitched) = stitcher.stitch(images)

                # if the status is '0', then OpenCV successfully performed image
                # stitching
                if status == 0:
                    # write the output stitched image to disk
                    cv2.imwrite(dir.get() + "\\stiched"+ name.get() + ".tif")
                    img = cv2.resize(stitched, (964, 922))
                    # display the output stitched image to our screen
                    cv2.imshow("Stitched", img)
                    cv2.waitKey(0)

                # otherwise the stitching failed, likely due to not enough keypoints)
                # being detected
                else:
                    print("[INFO] image stitching failed ({})".format(status))
            getFiles()
            stitchWindow.destroy()

        cropButton = t.Button(stitchWindow, text="Stitch", fg=fg, bg=bg)
        cropButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                             command=stitchPushed)
        cropButton.grid(column=0, row=2, padx=padx, pady=pady)
        stitchWindow.mainloop()

    stitchWindowButton = t.Button(enhanceWindow, text="Stitch Menu", fg=fg, bg=bg)
    stitchWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                               command=stitchButtonPushed)
    stitchWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row +1


def makeImageRegButton(column, row):
    """
    makes button to register images together, and action even for button
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def regButtonPushed():
        """
        when the register menu button is pushed we want to open another window that asks for the
        name of the folder to put images in to and the file to register the rest too, then executes registration
        :return:
        """
        regWindow = t.Toplevel(enhanceWindow)
        regWindow.geometry("300x300")
        regWindow.title("Image Stitching")
        regWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(regWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a output file Name without\nextension. Images chosen will be\nstitched together.")
        folderLabel = t.Label(regWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=1, padx=padx, pady=pady)
        folder = t.Entry(regWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=2)
        mainImgLabel = t.Label(regWindow, text="Enter Main Image", fg=fg, bg=titleBg)
        mainImgLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        mainImgLabel.grid(column=0, row=3, padx=padx, pady=pady)
        mainImg = t.Entry(regWindow)
        mainImg.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        mainImg.grid(column=0, row=4)

        def regPushed():
            """
            Get name, check that theirs file to stitch and a name
            :return:
            """
            listOfNames = getFilesInDrop()
            images = []
            if len(folder.get()) < 1 or len(mainImg.get())<1:
                messagebox.showinfo("ERROR", "Enter a folder and main image")
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            else:
                toReg = listOfNames
            for x in range(1, len(toReg)):
                MAX_FEATURES = 500
                GOOD_MATCH_PERCENT = 0.05

                img1 = cv2.imread(dir.get() + "\\" + mainImg.get())
                img1gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                img1eq = cv2.equalizeHist(img1gray)

                img2 = cv2.imread(dir.get() + "\\" + toReg[x])
                img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                img2eq = cv2.equalizeHist(img2gray)

                # Detect ORB features and compute descriptors.
                orb = cv2.ORB_create(MAX_FEATURES)
                keypoints1, descriptors1 = orb.detectAndCompute(img1eq, None)
                keypoints2, descriptors2 = orb.detectAndCompute(img2eq, None)

                # Match features.
                matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
                matches = matcher.match(descriptors1, descriptors2, None)

                # Sort matches by score
                matches.sort(key=lambda x: x.distance, reverse=False)

                # Remove not so good matches
                numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
                matches = matches[:numGoodMatches]
                name = (toReg[x])
                # Draw top matches
                imMatches = cv2.drawMatches(img1eq, keypoints1, img2eq, keypoints2, matches, None)
                cv2.imwrite(folder.get() + "\\" + "matches.jpg", imMatches)

                # Extract location of good matches
                points1 = np.zeros((len(matches), 2), dtype=np.float32)
                points2 = np.zeros((len(matches), 2), dtype=np.float32)

                for i, match in enumerate(matches):
                    points1[i, :] = keypoints1[match.queryIdx].pt
                    points2[i, :] = keypoints2[match.trainIdx].pt

                # Find homography
                h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

                # Use homography
                height, width, channels = img1.shape
                im2Reg = cv2.warpPerspective(img2, h, (width, height))
                name = (folder.get() + "\\" + "reg-" + toReg[x])
                cv2.imwrite(name, im2Reg)
            getFiles()
            regWindow.destroy()

        regButton = t.Button(regWindow, text="Register", fg=fg, bg=bg)
        regButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                             command=regPushed)
        regButton.grid(column=0, row=5, padx=padx, pady=pady)
        regWindow.mainloop()

    regWindowButton = t.Button(enhanceWindow, text="Register Menu", fg=fg, bg=bg)
    regWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                 command=regButtonPushed)
    regWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeImageConnectionsButtons(column):
    """
    The second column will contain buttons that connect images in some way.
    This includes cropping, image stitching, Image Registration and PCA.
    These buttons should be all preformed in series before PCA
    :return:
    """
    row = 0
    row = makeCropButton(column, row)
    row = makeImageStitchButton(column, row)
    row = makeImageRegButton(column, row)


# row = makeImageRegButton(column, row)
# row = makePCAButton(column, row)
def makeWidgets():
    """
    calls functions that make widgets for the GUI
    :return:
    """
    column = 0
    makeHelpMenu()
    column = makeFileColumn(column)
    column = makeImageConnectionsButtons(column)


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
