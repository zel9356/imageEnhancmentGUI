"""
Image Enchancment GUI, allows user to select images froma folder and prfoem enhcment and anylisis on them
"""
import os
import tkinter as t
from tkinter import ttk, scrolledtext, messagebox
import numpy as np
import cv2
import imutils
from PIL import Image, ImageEnhance
from PIL import ImageOps

"""
Varibales that need to be global
such as the window
And set up for window
"""
# setting up the capture GUI Frame or Window, captureWindow
enhanceWindow = t.Tk()

# set up our window, size, title, icon
enhanceWindow.geometry("700x550")
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
    filesOptions.clear()
    filesOptions.append("ALL")
    filesOptions.append("None")
    files.clear()

    for f in os.listdir(dir.get()):  # for each image in the folder images f is equal to the file name
        # we only want to act on our tiff images, dont want to try to do analysis on a txt file
        if f.endswith(".tiff") or f.endswith(".tif"):
            if f not in files:
                files.append(f)
                filesOptions.append(f)

    if len(files) == 0:
        messagebox.showinfo("ERROR", "Directory did not contain tiff or tif files")
        return
    # place the drop downs
    for i in range(0, 12):
        if i == len(files):
            break
        filesChosen.append(ttk.Combobox(enhanceWindow))
        filesChosen[i].configure(font=(font, fontSize), width=width, )
        filesChosen[i]['values'] = filesOptions
        filesChosen[i].grid(column=0, row=i + 3, padx=padx, pady=pady)
        filesChosen[i].current(1)


def folderCheckCreation(folderPath):
    """
    For a given directory, the function checks to make sure the dir exists
    if it doesnt exist, it creates it.
    This can fail if it does it will return False to to tell the function that called it to quit,
    if it succeeds it returns True.
    :param: folderPath: string of dir of folder
    :return: Boolean True if successful, False otherwise
    """
    if not os.path.isdir(folderPath):
        try:
            os.makedirs(folderPath)
        except OSError:
            return False
    else:
        return True
    return True


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
        cropLabel = t.Label(cropWindow, text="Enter crop factor", fg=fg, bg=titleBg)
        cropLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        cropLabel.grid(column=0, row=1, padx=padx, pady=pady)
        cropFactor = t.Entry(cropWindow)
        cropFactor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        cropFactor.grid(column=0, row=2)
        folderLabel = t.Label(cropWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(cropWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def cropPushed():
            """
            Get factor, check if files are there and crop
            :return:
            """
            listOfNames = getFilesInDrop()
            toCrop = []
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            else:
                toCrop = listOfNames
            for x in toCrop:
                if len(x) > 0:
                    image1 = Image.open(dir.get() + "\\" + x)
                    image2 = ImageOps.crop(image1, image1.size[1] // int(cropFactor.get()))
                    image2.save(folder.get() + "\\" + "cropped-" + cropFactor.get() + "-" + x)
            getFiles()
            cropWindow.destroy()

        cropButton = t.Button(cropWindow, text="Crop", fg=fg, bg=bg)
        cropButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                             command=cropPushed)
        cropButton.grid(column=0, row=5, padx=padx, pady=pady)
        cropWindow.mainloop()

    cropWindowButton = t.Button(enhanceWindow, text="Crop Menu", fg=fg, bg=bg)
    cropWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                               command=cropButtonPushed)
    cropWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


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
        nameLabel = t.Label(stitchWindow, text="Enter image name", fg=fg, bg=titleBg)
        nameLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        nameLabel.grid(column=0, row=1, padx=padx, pady=pady)
        name = t.Entry(stitchWindow)
        name.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        name.grid(column=0, row=2)
        folderLabel = t.Label(stitchWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(stitchWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def stitchPushed():
            """
            Get name, check that theirs file to stitch and a name
            :return:
            """
            listOfNames = getFilesInDrop()
            images = []
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            if len(name.get()) < 1:
                messagebox.showinfo("ERROR", "Enter Image Name")
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            else:
                toStitch = listOfNames
            for i in toStitch:
                image = cv2.imread(dir.get() + "\\" + i)
                images.append(image)
                stitcher = cv2.Stitcher_create() if imutils.is_cv3() else cv2.Stitcher_create()
                (status, stitched) = stitcher.stitch(images)

                # if the status is '0', then OpenCV successfully performed image
                # stitching
                if status == 0:
                    # write the output stitched image to disk
                    cv2.imwrite(folder.get() + "\\" + name.get() + ".tif", image)
                    img = cv2.resize(stitched, (964, 922))
                    # display the output stitched image to our screen
                    # cv2.imshow("Stitched", img)
                    # cv2.waitKey(0)

                # otherwise the stitching failed, likely due to not enough keypoints)
                # being detected
                else:
                    if status == 1:
                        messagebox.showinfo("ERROR",
                                            "ERR_NEED_MORE_IMGS\n[INFO] image stitching failed({})".format(status))
                    if status == 2:
                        messagebox.showinfo("ERROR",
                                            "ERR_HOMOGRAPHY_EST_FAIL\n[INFO] image stitching failed({})".format(status))
                    if status == 3:
                        messagebox.showinfo("ERROR",
                                            "ERR_CAMERA_PARAMS_ADJUST_FAIL\n[INFO] image stitching failed({})".format(
                                                status))
                    return
            getFiles()
            stitchWindow.destroy()

        stitchButton = t.Button(stitchWindow, text="Stitch", fg=fg, bg=bg)
        stitchButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                               command=stitchPushed)
        stitchButton.grid(column=0, row=5, padx=padx, pady=pady)
        stitchWindow.mainloop()

    stitchWindowButton = t.Button(enhanceWindow, text="Stitch Menu", fg=fg, bg=bg)
    stitchWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                 command=stitchButtonPushed)
    stitchWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


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
                              "Enter a main image name with\nextension. Images chosen will be\nregistered together.")
        mainImgLabel = t.Label(regWindow, text="Enter Main Image", fg=fg, bg=titleBg)
        mainImgLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        mainImgLabel.grid(column=0, row=1, padx=padx, pady=pady)
        mainImg = t.Entry(regWindow)
        mainImg.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        mainImg.grid(column=0, row=2)
        folderLabel = t.Label(regWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(regWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def regPushed():
            """
            Get name, check that theirs file to stitch and a name
            :return:
            """
            listOfNames = getFilesInDrop()
            images = []
            if len(folder.get()) < 1 or len(mainImg.get()) < 1:
                messagebox.showinfo("ERROR", "Enter a folder and main image")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            else:
                toReg = listOfNames
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
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


def makePCAButton(column, row):
    """
    makes button to preform on images, and action even for button
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def PCAButtonPushed():
        """
        when the PCA menu button is pushed we want to open another window that asks for the
        name of the folder to put images in to, then executes PCA
        :return:
        """
        PCAWindow = t.Toplevel(enhanceWindow)
        PCAWindow.geometry("300x300")
        PCAWindow.title("Image Stitching")
        PCAWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(PCAWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a folder path. Images chosen\nwill be used for PCA and the\nresults will be placed in the\nfolder.")
        folderLabel = t.Label(PCAWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=1, padx=padx, pady=pady)
        folder = t.Entry(PCAWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=2)

        def PCAPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            # TODO PCA function
            getFiles()
            PCAWindow.destroy()

        pcaButton = t.Button(PCAWindow, text="PCA", fg=fg, bg=bg)
        pcaButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                            command=PCAPushed)
        pcaButton.grid(column=0, row=5, padx=padx, pady=pady)
        PCAWindow.mainloop()

    pcaWindowButton = t.Button(enhanceWindow, text="PCA Menu", fg=fg, bg=bg)
    pcaWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                              command=PCAButtonPushed)
    pcaWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeBrightnessButton(column, row):
    """
    Makes button to open brightness menu, when its pressed the brightness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def brightnessWindowPushed():
        """
        Places instructions for brightness, a label and entry box for the factor, a label and
        entry for a folder a preview button and a brightness
        button to preform the alterations
        :return:
        """
        brightnessWindow = t.Toplevel(enhanceWindow)
        brightnessWindow.geometry("300x300")
        brightnessWindow.title("Brightness")
        brightnessWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(brightnessWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a brightness factor:\n0 will result in a black image\n1 will result in the orginal image\nabove 1 will be a brighter image\nEnter a folder path to place the\nresults in.")
        factorLabel = t.Label(brightnessWindow, text="Enter factor", fg=fg, bg=titleBg)
        factorLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        factorLabel.grid(column=0, row=1, padx=padx, pady=pady)
        factor = t.Entry(brightnessWindow)
        factor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        factor.grid(column=0, row=2)
        folderLabel = t.Label(brightnessWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(brightnessWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def brightnessPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = Image.open(dir.get() + "\\" + i)
                temp = ImageEnhance.Brightness(image1)
                image2 = temp.enhance(float(factor.get()))
                image2.save(folder.get() + "\\brightness-" + factor.get() + "-" + i)
            # TODO PCA function
            getFiles()
            brightnessWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])  # image 1 is our original image
            temp = ImageEnhance.Brightness(image1)  # temp is a var we can perform a brightness enhancement on
            image2 = temp.enhance(
                float(factor.get()))  # Preform enhancement with a factor of 1.6 and set that new enhance image
            # equal to image two
            image2.show()  # display image 2

        brightnessPreviewButton = t.Button(brightnessWindow, text="Preview", fg=fg, bg=bg)
        brightnessPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                          relief=buttonRelief,
                                          command=previewPushed)
        brightnessPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        brightnessButton = t.Button(brightnessWindow, text="Brightness", fg=fg, bg=bg)
        brightnessButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=brightnessPushed)
        brightnessButton.grid(column=0, row=6, padx=padx, pady=pady)
        brightnessWindow.mainloop()

    brightnessWindowButton = t.Button(enhanceWindow, text="Brightness Menu", fg=fg, bg=bg)
    brightnessWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                     command=brightnessWindowPushed)
    brightnessWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeContrastButton(column, row):
    """
    Makes button to open brightness menu, when its pressed the brightness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def constrastWindowPushed():
        """
        Places instructions for contrast, a label and entry box for the factor, a label and
        entry for a folder a preview button and a contrast
        button to preform the alterations
        :return:
        """
        contrastWindow = t.Toplevel(enhanceWindow)
        contrastWindow.geometry("300x300")
        contrastWindow.title("Contrast")
        contrastWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(contrastWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a contrast factor:\n0 will result in a grey image\n1 will result in the orginal "
                              "image\nabove 1 will be a higher contrast\nimage\nEnter a folder path to place "
                              "the\nresults in.")
        factorLabel = t.Label(contrastWindow, text="Enter factor", fg=fg, bg=titleBg)
        factorLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        factorLabel.grid(column=0, row=1, padx=padx, pady=pady)
        factor = t.Entry(contrastWindow)
        factor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        factor.grid(column=0, row=2)
        folderLabel = t.Label(contrastWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(contrastWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def contrastPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = Image.open(dir.get() + "\\" + i)
                temp = ImageEnhance.Contrast(image1)
                image2 = temp.enhance(float(factor.get()))
                image2.save(folder.get() + "\\contrast-" + factor.get() + "-" + i)
            # TODO PCA function
            getFiles()
            contrastWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])  # image 1 is our original image
            temp = ImageEnhance.Contrast(image1)  # temp is a var we can perform a brightness enhancement on
            image2 = temp.enhance(
                float(factor.get()))  # Preform enhancement with a factor of 1.6 and set that new enhance image
            # equal to image two
            image2.show()  # display image 2

        brightnessPreviewButton = t.Button(contrastWindow, text="Preview", fg=fg, bg=bg)
        brightnessPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                          relief=buttonRelief,
                                          command=previewPushed)
        brightnessPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        brightnessButton = t.Button(contrastWindow, text="Contrast", fg=fg, bg=bg)
        brightnessButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=contrastPushed)
        brightnessButton.grid(column=0, row=6, padx=padx, pady=pady)
        contrastWindow.mainloop()

    brightnessWindowButton = t.Button(enhanceWindow, text="Contrast Menu", fg=fg, bg=bg)
    brightnessWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                     command=constrastWindowPushed)
    brightnessWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeSharpnessButton(column, row):
    """
    Makes button to open brightness menu, when its pressed the brightness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def sharpWindowPushed():
        """
        Places instructions for contrast, a label and entry box for the factor, a label and
        entry for a folder a preview button and a contrast
        button to preform the alterations
        :return:
        """
        sharpWindow = t.Toplevel(enhanceWindow)
        sharpWindow.geometry("300x300")
        sharpWindow.title("Sharpness")
        sharpWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(sharpWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a sharpness factor:\n0 will result in a blurred image\n1 will result in the "
                              "orginal "
                              "image\nabove 1 will be sharper image\nEnter a folder path to place "
                              "the\nresults in.")
        factorLabel = t.Label(sharpWindow, text="Enter factor", fg=fg, bg=titleBg)
        factorLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        factorLabel.grid(column=0, row=1, padx=padx, pady=pady)
        factor = t.Entry(sharpWindow)
        factor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        factor.grid(column=0, row=2)
        folderLabel = t.Label(sharpWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(sharpWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def sharpPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = Image.open(dir.get() + "\\" + i)
                temp = ImageEnhance.Sharpness(image1)
                image2 = temp.enhance(float(factor.get()))
                image2.save(folder.get() + "\\sharper-" + factor.get() + "-" + i)
            # TODO PCA function
            getFiles()
            sharpWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])  # image 1 is our original image
            temp = ImageEnhance.Sharpness(image1)  # temp is a var we can perform a brightness enhancement on
            image2 = temp.enhance(
                float(factor.get()))  # Preform enhancement with a factor of 1.6 and set that new enhance image
            # equal to image two
            image2.show()  # display image 2

        brightnessPreviewButton = t.Button(sharpWindow, text="Preview", fg=fg, bg=bg)
        brightnessPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                          relief=buttonRelief,
                                          command=previewPushed)
        brightnessPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        brightnessButton = t.Button(sharpWindow, text="Sharpness", fg=fg, bg=bg)
        brightnessButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=sharpPushed)
        brightnessButton.grid(column=0, row=6, padx=padx, pady=pady)
        sharpWindow.mainloop()

    brightnessWindowButton = t.Button(enhanceWindow, text="Sharpness Menu", fg=fg, bg=bg)
    brightnessWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                     command=sharpWindowPushed)
    brightnessWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeEqualizeButton(column, row):
    """
    Makes button to open brightness menu, when its pressed the brightness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def equalWindowPushed():
        """
        Places instructions for contrast, a label and entry box for the factor, a label and
        entry for a folder a preview button and a contrast
        button to preform the alterations
        :return:
        """
        equalWindow = t.Toplevel(enhanceWindow)
        equalWindow.geometry("300x300")
        equalWindow.title("Equalize")
        equalWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(equalWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Equalize will equalize the image\nhistogram. This function applies a\nnon-linear "
                              "mapping to the input\nimage, in order to create a uniform\ndistribution of grayscale "
                              "values\nin the output image.\nEnter a folder path to place "
                              "the\nresults in.")
        folderLabel = t.Label(equalWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=1, padx=padx, pady=pady)
        folder = t.Entry(equalWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=2)

        def equalPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = Image.open(dir.get() + "\\" + i)
                image2 = ImageOps.equalize(image1)
                image2.save(folder.get() + "\\-equalized-" + i)
            # TODO PCA function
            getFiles()
            equalWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])  # image 1 is our original image
            temp = ImageEnhance.Sharpness(image1)  # temp is a var we can perform a brightness enhancement on
            image2 = ImageOps.equalize(image1)
            # equal to image two
            image2.show()  # display image 2

        equalPreviewButton = t.Button(equalWindow, text="Preview", fg=fg, bg=bg)
        equalPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                          relief=buttonRelief,
                                          command=previewPushed)
        equalPreviewButton.grid(column=0, row=3, padx=padx, pady=pady)
        equalButton = t.Button(equalWindow, text="Equalize", fg=fg, bg=bg)
        equalButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=equalPushed)
        equalButton.grid(column=0, row=4, padx=padx, pady=pady)
        equalWindow.mainloop()

    brightnessWindowButton = t.Button(enhanceWindow, text="Equalize Menu", fg=fg, bg=bg)
    brightnessWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                     command=equalWindowPushed)
    brightnessWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeColorizeButton(column, row):
    """
    Makes button to open brightness menu, when its pressed the brightness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def colorWindowPushed():
        """
        Places instructions for contrast, a label and entry box for the factor, a label and
        entry for a folder a preview button and a contrast
        button to preform the alterations
        :return:
        """
        colorWindow = t.Toplevel(enhanceWindow)
        colorWindow.geometry("300x300")
        colorWindow.title("Colorize")
        colorWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(colorWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Colorize grayscale image function calculates a color wedge mapping all black pixels in "
                              "the source image to the "
                              "first color, and all white pixels to the second color.\nEnter a folder path to place "
                              "the\nresults in.")
        colorOneLabel = t.Label(colorWindow, text="Enter first color", fg=fg, bg=titleBg)
        colorOneLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        colorOneLabel.grid(column=0, row=1, padx=padx, pady=pady)
        colorOne = t.Entry(colorWindow)
        colorOne.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        colorOne.grid(column=0, row=2)
        colorTwoLabel = t.Label(colorWindow, text="Enter first color", fg=fg, bg=titleBg)
        colorTwoLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        colorTwoLabel.grid(column=0, row=3, padx=padx, pady=pady)
        colorTwo = t.Entry(colorWindow)
        colorTwo.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        colorTwo.grid(column=0, row=4)
        folderLabel = t.Label(colorWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=5, padx=padx, pady=pady)
        folder = t.Entry(colorWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=6)

        def colorPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(colorOne.get()) == 0 or len(colorTwo.get())==0:
                messagebox.showinfo("ERROR", "Enter a valid color")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = Image.open(dir.get() + "\\" + i)
                image2 = ImageOps.colorize(image1, colorOne, colorTwo)
                image2.save(folder.get() + "\\-equalized-" + i)
            # TODO PCA function
            getFiles()
            colorWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(colorOne.get()) == 0 or len(colorTwo.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a valid color")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])
            image2 = ImageOps.colorize(image1, colorOne, colorTwo)
            # equal to image two
            image2.show()  # display image 2

        equalPreviewButton = t.Button(colorWindow, text="Preview", fg=fg, bg=bg)
        equalPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                          relief=buttonRelief,
                                          command=previewPushed)
        equalPreviewButton.grid(column=0, row=7, padx=padx, pady=pady)
        equalButton = t.Button(colorWindow, text="Solarize", fg=fg, bg=bg)
        equalButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=colorPushed)
        equalButton.grid(column=0, row=8, padx=padx, pady=pady)
        colorWindow.mainloop()

    brightnessWindowButton = t.Button(enhanceWindow, text="Solarize Menu", fg=fg, bg=bg)
    brightnessWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                     command=colorWindowPushed)
    brightnessWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeSolarizeButton(column, row):
    """
    Makes button to open brightness menu, when its pressed the brightness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def solarizeWindowPushed():
        """
        Places instructions for contrast, a label and entry box for the factor, a label and
        entry for a folder a preview button and a contrast
        button to preform the alterations
        :return:
        """
        solarWindow = t.Toplevel(enhanceWindow)
        solarWindow.geometry("300x300")
        solarWindow.title("Solarize")
        solarWindow.iconbitmap("imagesForGUI\\bitchlasagna.ico")
        scrollInstruct = scrolledtext.ScrolledText(solarWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Solarize will invert all pixel values above a threshold.\n Enter a threshold between 0 "
                              "and 256\nEnter a folder path to place "
                              "the\nresults in.")
        thresholdLabel = t.Label(solarWindow, text="Enter threshold", fg=fg, bg=titleBg)
        thresholdLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        thresholdLabel.grid(column=0, row=1, padx=padx, pady=pady)
        threshold = t.Entry(solarWindow)
        threshold.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        threshold.grid(column=0, row=2)
        folderLabel = t.Label(solarWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=3, padx=padx, pady=pady)
        folder = t.Entry(solarWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=4)

        def solarPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(threshold.get()) == 0 or int(threshold.get()) < 0 or int(threshold.get())>256:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = Image.open(dir.get() + "\\" + i)
                image2 = ImageOps.solarize(image1, int(threshold.get()))
                image2.save(folder.get() + "\\-equalized-" + i)
            # TODO PCA function
            getFiles()
            solarWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(threshold.get()) == 0 or int(threshold.get()) < 0 or int(threshold.get())>256:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])
            image2 = ImageOps.solarize(image1, int(threshold.get()))
            # equal to image two
            image2.show()  # display image 2

        equalPreviewButton = t.Button(solarWindow, text="Preview", fg=fg, bg=bg)
        equalPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                          relief=buttonRelief,
                                          command=previewPushed)
        equalPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        equalButton = t.Button(solarWindow, text="Solarize", fg=fg, bg=bg)
        equalButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=solarPushed)
        equalButton.grid(column=0, row=6, padx=padx, pady=pady)
        solarWindow.mainloop()

    brightnessWindowButton = t.Button(enhanceWindow, text="Solarize Menu", fg=fg, bg=bg)
    brightnessWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                     command=solarizeWindowPushed)
    brightnessWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
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
    row = makePCAButton(column, row)
    return column + 1


def makeImageAffectButtons(column):
    """
    This column effects indivdual images rather than comining the whole in some way.
    This inculdes Contrast, Brightness, sharpness, equalize, solarize(invert pixels) maybe colorize
    openCV, threshold, edge dection, gradients
    :param column:
    :return:
    """
    row = 0
    row = makeBrightnessButton(column, row)
    row = makeContrastButton(column, row)
    row = makeSharpnessButton(column, row)
    row = makeEqualizeButton(column, row)
    row = makeSolarizeButton(column, row)
    row = makeColorizeButton()
    return column + 1


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
    column = makeImageAffectButtons(column)


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
