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
enhanceWindow.geometry("850x550")
enhanceWindow.title("Image Enhancement")
enhanceWindow.iconbitmap("imagesForGUI\\guiIcon.ico")  # make our own image

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
    makes a help gui that pops up when enhancement gui is right clicked
    this gui gives instruction on how to use the image enhancement GUI
    :return:
    """

    def rightClick(event):
        helpWindow = t.Toplevel(enhanceWindow)
        helpWindow.geometry("300x300")
        helpWindow.title("Help")
        helpWindow.iconbitmap("imagesForGUI\\helpMenu.ico")
        scrollInstruct = scrolledtext.ScrolledText(helpWindow, width=50, height=50)
        scrollInstruct.pack()
        # TODO add instructions
        scrollInstruct.insert(t.INSERT, "Enter a full path directory to a folder of tif/tiff images. Clicking the "
                                        "load button will load and tif/tiff images in that folder not within another "
                                        "folder.\nSelecting 'All' in the first drop down box will cause all images in" 
                                        " the folder to be used for enhancement or analysis. Repeat selected images "
                                        "will be ignored\nClicking an image enhancement button will open up another "
                                        "window asking for any need parameters and will allow the user to preview the "
                                        "first image in the column of image drop downs. All will ask for an out folder"
                                        "to put the resultant image in.\nIf the folder does not exist it will be "
                                        "created if possible.")
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

    loadFilesButton = t.Button(enhanceWindow, text="Load Images", fg=fg, bg=bg)
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
        cropWindow.iconbitmap("imagesForGUI\\crop.ico")
        scrollInstruct = scrolledtext.ScrolledText(cropWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a crop factor. The pixel \nwidth and height of the image will\nbe divide by "
                              "this factor and the\nresult removed from each side. \nEnter a folder path to place "
                              "the\nresults in.")
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
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) < 1:
                messagebox.showinfo("ERROR", "Enter a folder directory")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return

            for x in listOfNames:
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
        stitchWindow.iconbitmap("imagesForGUI\\imagestitching.ico")
        scrollInstruct = scrolledtext.ScrolledText(stitchWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a output file Name without\nextension. Images chosen will be\nstitched together. \nEnter a folder path to place "
                              "the\nresults in.")
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
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) < 1:
                messagebox.showinfo("ERROR", "Enter a folder directory")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            if len(name.get()) < 1:
                messagebox.showinfo("ERROR", "Enter Image Name")
            for i in listOfNames:
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
        regWindow.title("Image Registration")
        regWindow.iconbitmap("imagesForGUI\\imageReg.ico")
        scrollInstruct = scrolledtext.ScrolledText(regWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a main image name with\nextension. Images chosen will be\nregistered together.\nEnter a folder path to place "
                              "the\nresults in.")
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
            Get name, check that theirs images to register and a folder to put the result and the mai image
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if mainImg.get() == 0 or mainImg.get() not in listOfNames:
                messagebox.showinfo("ERROR", "Enter a valid main image")
                return
            if len(folder.get()) < 1:
                messagebox.showinfo("ERROR", "Enter a folder directory")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for x in range(1, len(listOfNames)):
                MAX_FEATURES = 500
                GOOD_MATCH_PERCENT = 0.05

                img1 = cv2.imread(dir.get() + "\\" + mainImg.get())
                img1gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                img1eq = cv2.equalizeHist(img1gray)

                img2 = cv2.imread(dir.get() + "\\" + listOfNames[x])
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
                name = (listOfNames[x])
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
                name = (folder.get() + "\\" + "reg-" + listOfNames[x])
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
        PCAWindow.title("PCA")
        PCAWindow.iconbitmap("imagesForGUI\\PCA3DSpace.ico")
        scrollInstruct = scrolledtext.ScrolledText(PCAWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a folder path. Images chosen\nwill be used for PCA. \nEnter a folder path to place "
                              "the\nresults in.")
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
        brightnessWindow.iconbitmap("imagesForGUI\\brightness.ico")
        scrollInstruct = scrolledtext.ScrolledText(brightnessWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a brightness factor:\n0 will result in a black image\n1 will result in the original"
                              " image\nabove 1 will be a brighter image\nEnter a folder path to place the\nresults in.")
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
            Check requirements and preform and save brightness changes
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(factor.get()) == 0 or float(factor.get()) < 0:
                messagebox.showinfo("ERROR", "Enter a valid factor")
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
                temp = ImageEnhance.Brightness(image1)
                image2 = temp.enhance(float(factor.get()))
                image2.save(folder.get() + "\\brightness-" + factor.get() + "-" + i)
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
    Makes button to open contrast menu, when its pressed the contrast menu is opened
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
        contrastWindow.iconbitmap("imagesForGUI\\contrast.ico")
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
            checks for requirments and preforms contrast changes when button is pressed
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
            getFiles()
            contrastWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the contrast factor applied
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

        contrastPreviewButton = t.Button(contrastWindow, text="Preview", fg=fg, bg=bg)
        contrastPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                        relief=buttonRelief,
                                        command=previewPushed)
        contrastPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        contrastButton = t.Button(contrastWindow, text="Brightness", fg=fg, bg=bg)
        contrastButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                 command=contrastPushed)
        contrastButton.grid(column=0, row=6, padx=padx, pady=pady)
        contrastWindow.mainloop()

    contrastWindowButton = t.Button(enhanceWindow, text="Contrast Menu", fg=fg, bg=bg)
    contrastWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=constrastWindowPushed)
    contrastWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeSharpnessButton(column, row):
    """
    Makes button to open sharpness menu, when its pressed the sharpness menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def sharpWindowPushed():
        """
        Places instructions for sharpness, and required labels and entries
        button to preform the alterations
        :return:
        """
        sharpWindow = t.Toplevel(enhanceWindow)
        sharpWindow.geometry("300x300")
        sharpWindow.title("Sharpness")
        sharpWindow.iconbitmap("imagesForGUI\\sharpness.ico")
        scrollInstruct = scrolledtext.ScrolledText(sharpWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Enter a sharpness factor:\n0 will result in a blurred image\n1 will result in the "
                              "original "
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
            check for requirments and preform sharpness changes when pushed
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

        sharpPreviewButton = t.Button(sharpWindow, text="Preview", fg=fg, bg=bg)
        sharpPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                     relief=buttonRelief,
                                     command=previewPushed)
        sharpPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        sharpButton = t.Button(sharpWindow, text="Sharpness", fg=fg, bg=bg)
        sharpButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                              command=sharpPushed)
        sharpButton.grid(column=0, row=6, padx=padx, pady=pady)
        sharpWindow.mainloop()

    sharpWindowButton = t.Button(enhanceWindow, text="Sharpness Menu", fg=fg, bg=bg)
    sharpWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                command=sharpWindowPushed)
    sharpWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeEqualizeButton(column, row):
    """
    Makes button to open equalize menu, when its pressed the equalize menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def equalWindowPushed():
        """
        Places instructions for equalize, and required fields and widgets
        :return:
        """
        equalWindow = t.Toplevel(enhanceWindow)
        equalWindow.geometry("300x300")
        equalWindow.title("Equalize")
        equalWindow.iconbitmap("imagesForGUI\\equalize.ico")
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
            check for requirements and preform equalize changes and save
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
            getFiles()
            equalWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with equalization applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])  # image 1 is our original image
            image2 = ImageOps.equalize(image1)
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

    equalWindowButton = t.Button(enhanceWindow, text="Equalize Menu", fg=fg, bg=bg)
    equalWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                command=equalWindowPushed)
    equalWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeColorizeButton(column, row):
    """
    Makes button to open colorize menu, when its pressed the colorized menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def colorWindowPushed():
        """
        Places reqiured fields and widgets for colorization
        :return:
        """
        colorWindow = t.Toplevel(enhanceWindow)
        colorWindow.geometry("300x600")
        colorWindow.title("Colorize")
        colorWindow.iconbitmap("imagesForGUI\\colorize.ico")
        scrollInstruct = scrolledtext.ScrolledText(colorWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Colorize is three-color mapping.\nSpecify black, mid and white\narguments should color "
                              "names.\nSpecify mapping positions for the\ncolors, these parameters are the\ninteger value "
                              "corresponding to\nwhere the corresponding color\nshould be mapped. These parameters\nmust "
                              "have logical order, such that\nblackpoint<=midpoint<=whitepoint\n(if mid is "
                              "specified). "
                              "\nEnter a folder path to place "
                              "the\nresults in.")
        blackColorLabel = t.Label(colorWindow, text="Enter black input color", fg=fg, bg=titleBg)
        blackColorLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        blackColorLabel.grid(column=0, row=1, padx=padx, pady=pady)
        blackColor = t.Entry(colorWindow)
        blackColor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        blackColor.grid(column=0, row=2)
        blackValueLabel = t.Label(colorWindow, text="Enter black int value", fg=fg, bg=titleBg)
        blackValueLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        blackValueLabel.grid(column=0, row=3, padx=padx, pady=pady)
        blackValue = t.Entry(colorWindow)
        blackValue.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        blackValue.grid(column=0, row=4)
        midColorLabel = t.Label(colorWindow, text="Enter midpoint input color", fg=fg, bg=titleBg)
        midColorLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        midColorLabel.grid(column=0, row=5, padx=padx, pady=pady)
        midColor = t.Entry(colorWindow)
        midColor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        midColor.grid(column=0, row=6)
        midValueLabel = t.Label(colorWindow, text="Enter midpoint int value", fg=fg, bg=titleBg)
        midValueLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        midValueLabel.grid(column=0, row=7, padx=padx, pady=pady)
        midValue = t.Entry(colorWindow)
        midValue.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        midValue.grid(column=0, row=8)
        whiteColorLabel = t.Label(colorWindow, text="Enter white input color", fg=fg, bg=titleBg)
        whiteColorLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        whiteColorLabel.grid(column=0, row=9, padx=padx, pady=pady)
        whiteColor = t.Entry(colorWindow)
        whiteColor.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        whiteColor.grid(column=0, row=10)
        whiteValueLabel = t.Label(colorWindow, text="Enter white int value", fg=fg, bg=titleBg)
        whiteValueLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        whiteValueLabel.grid(column=0, row=11, padx=padx, pady=pady)
        whiteValue = t.Entry(colorWindow)
        whiteValue.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        whiteValue.grid(column=0, row=12)
        folderLabel = t.Label(colorWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=13, padx=padx, pady=pady)
        folder = t.Entry(colorWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=14)

        def colorPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(blackColor.get()) == 0 or len(whiteColor.get()) == 0 or len(midColor.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a valid colors")
                return
            if len(blackValue.get()) == 0 or len(midValue.get()) == 0 or len(whiteValue.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a valid int values (0-255)")
                return
            blk = int(blackValue.get())
            wht = int(whiteValue.get())
            mid = int(midValue.get())
            if blk > 255 or blk < 0 or wht > 255 or wht < 0 or mid > 255 or mid < 0:
                messagebox.showinfo("ERROR", "Enter a valid int values (0-255)")
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
                image2 = ImageOps.colorize(image1, black=blackColor.get(), white=whiteColor.get(), mid=mid,
                                           blackpoint=blk, whitepoint=wht)
                image2.save(folder.get() + "\\-colorized-" + i)
            getFiles()
            colorWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with colorization applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(blackColor.get()) == 0 or len(whiteColor.get()) == 0 or len(midColor.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a valid colors")
                return
            if len(blackValue.get()) == 0 or len(midValue.get()) == 0 or len(whiteValue.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a valid int values (0-255)")
                return
            blk = int(blackValue.get())
            wht = int(whiteValue.get())
            mid = int(midValue.get())
            if blk > 255 or blk < 0 or wht > 255 or wht < 0 or mid > 255 or mid < 0:
                messagebox.showinfo("ERROR", "Enter a valid int values (0-255)")
                return

            image1 = Image.open(dir.get() + "\\" + listOfNames[0])
            image2 = ImageOps.colorize(image1, black=blackColor.get(), white=whiteColor.get(), mid=midColor.get(),
                                       blackpoint=int(blackValue.get()), whitepoint=int(whiteValue.get()),
                                       midpoint=int(midValue.get()))
            # equal to image two
            image2.show()  # display image 2

        colorPreviewButton = t.Button(colorWindow, text="Preview", fg=fg, bg=bg)
        colorPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                     relief=buttonRelief,
                                     command=previewPushed)
        colorPreviewButton.grid(column=0, row=15, padx=padx, pady=pady)
        colorButton = t.Button(colorWindow, text="Colorize", fg=fg, bg=bg)
        colorButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                              command=colorPushed)
        colorButton.grid(column=0, row=16, padx=padx, pady=pady)
        colorWindow.mainloop()

    colorWindowButton = t.Button(enhanceWindow, text="Colorize Menu", fg=fg, bg=bg)
    colorWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                command=colorWindowPushed)
    colorWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeSolarizeButton(column, row):
    """
    Makes button to open solarize menu, when its pressed the solarize menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def solarizeWindowPushed():
        """
        Places instructions and other entries and widgest for solarize
        :return:
        """
        solarWindow = t.Toplevel(enhanceWindow)
        solarWindow.geometry("300x300")
        solarWindow.title("Solarize")
        solarWindow.iconbitmap("imagesForGUI\\solarize.ico")
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
            checks for requirements and preforms solarization
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(threshold.get()) == 0 or int(threshold.get()) < 0 or int(threshold.get()) > 256:
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
                image2.save(folder.get() + "\\-solarize-" + i)
            getFiles()
            solarWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(threshold.get()) == 0 or int(threshold.get()) < 0 or int(threshold.get()) > 256:
                messagebox.showinfo("ERROR", "Enter a valid factor")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            image1 = Image.open(dir.get() + "\\" + listOfNames[0])
            image2 = ImageOps.solarize(image1, int(threshold.get()))
            # equal to image two
            image2.show()  # display image 2

        solarPreviewButton = t.Button(solarWindow, text="Preview", fg=fg, bg=bg)
        solarPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                     relief=buttonRelief,
                                     command=previewPushed)
        solarPreviewButton.grid(column=0, row=5, padx=padx, pady=pady)
        solarButton = t.Button(solarWindow, text="Solarize", fg=fg, bg=bg)
        solarButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                              command=solarPushed)
        solarButton.grid(column=0, row=6, padx=padx, pady=pady)
        solarWindow.mainloop()

    solarWindowButton = t.Button(enhanceWindow, text="Solarize Menu", fg=fg, bg=bg)
    solarWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                command=solarizeWindowPushed)
    solarWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeAndCheckThreshFolders(folder, stateOfBinary, stateOfInvBinary, stateOfToZero, stateOfInvZero, stateOfTrunc):
    """
    Once the directory for thresholding os created individual folders for each type selected are mad if not already there
    :param folder: folder to put/ look for folders
    :param stateOfBinary: state of corresponding check box
    :param stateOfInvBinary: state of corresponding check box
    :param stateOfToZero: state of corresponding check box
    :param stateOfInvZero: state of corresponding check box
    :param stateOfTrunc: state of corresponding check box
    :return: state, true if successful, false otherwise
    """
    status = True
    if stateOfBinary.get():
        status = folderCheckCreation(folder + "\\" + "Binary")
        if not status:
            return status
    if stateOfInvBinary.get():
        status = folderCheckCreation(folder + "\\" + "InverseBinary")
        if not status:
            return status
    if stateOfToZero.get():
        status = folderCheckCreation(folder + "\\" + "ToZero")
        if not status:
            return status
    if stateOfInvZero.get():
        status = folderCheckCreation(folder + "\\" + "InverseToZero")
        if not status:
            return status
    if stateOfTrunc.get():
        status = folderCheckCreation(folder + "\\" + "Trunc")
        if not status:
            return status
    return status


def makeAndCheckGradientFolders(folder, stateOfSobelX, stateOfSobelY, stateOfScharrX, stateOfScharrY, stateOfLap):
    """
    Once the directory for thresholding os created individual folders for each type selected are mad if not already there
    :param folder: folder to put/ look for folders
    :param stateOfSobel: state of corresponding check box
    :param stateOfLap: state of corresponding check box
    """
    status = True
    status = folderCheckCreation(folder)
    if not status:
        return status
    if stateOfSobelX:
        status = folderCheckCreation(folder + "\\" + "Sobel-x")
        if not status:
            return status
    if stateOfSobelY:
        status = folderCheckCreation(folder + "\\" + "Sobel-y")
        if not status:
            return status
    if stateOfScharrX:
        status = folderCheckCreation(folder + "\\" + "Scharr-x")
        if not status:
            return status
    if stateOfScharrY:
        status = folderCheckCreation(folder + "\\" + "Scharr-y")
        if not status:
            return status
    if stateOfLap:
        status = folderCheckCreation(folder + "\\" + "Laplacian")
        if not status:
            return status
    return status


def makeThresholdButton(column, row):
    """
    Makes button to open threshold menu, when its pressed the threshold menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def threshWindowPushed():
        """
        Places instructions for threshold, and other entries and widgets required
        :return:
        """
        threshWindow = t.Toplevel(enhanceWindow)
        threshWindow.geometry("300x400")
        threshWindow.title("Threshold")
        threshWindow.iconbitmap("imagesForGUI\\threshold.ico")

        def rightClick(event):
            helpThreshWindow = t.Toplevel(threshWindow)
            helpThreshWindow.geometry("800x600")
            helpThreshWindow.title("Help")
            helpThreshWindow.iconbitmap("imagesForGUI\\helpMenu.ico")
            photo = t.PhotoImage(file="imagesForGUI\\thresholdmethods.GIF")
            lab = t.Label(helpThreshWindow, image=photo)
            lab.pack()
            web = t.Label(helpThreshWindow, text="https://docs.opencv.org/master/d7/d1b/group__imgproc__misc.html"
                                                 "#ggaa9e58d2860d4afa658ef70a9b1115576ac7e89a5e95490116e7d2082b3096b2b8")
            web.pack()
            scrollInstruct.insert(t.INSERT, "")
            helpThreshWindow.mainloop()

        threshWindow.bind("<Button-3>", rightClick)
        scrollInstruct = scrolledtext.ScrolledText(threshWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "In thresholding if the pixel value\nis smaller than the threshold, it\nis set to 0, "
                              "otherwise it is set to\na maximum value. The function\ncv.threshold is used to apply "
                              "the\nthresholding. Threshold is the\nthreshold value which is used to\nclassify the pixel "
                              "values. Max is\nthe maximum value which is assigned\nto pixel values exceeding the\n"
                              "threshold. Choose one or more\nthresholding methods.\nEnter a folder path to place "
                              "the\nresults in.\nRight click for more information.")
        # can select types of thresholding
        stateOfBinary = t.BooleanVar()
        stateOfBinary.set(True)
        stateOfInvBinary = t.BooleanVar()
        stateOfInvBinary.set(False)
        stateOfToZero = t.BooleanVar()
        stateOfToZero.set(False)
        stateOfInvZero = t.BooleanVar()
        stateOfInvZero.set(False)
        stateOfTrunc = t.BooleanVar()
        stateOfTrunc.set(False)
        binary = ttk.Checkbutton(threshWindow, text="Binary", var=stateOfBinary)
        binary.grid(column=0, row=1, padx=padx)
        inverseBinary = ttk.Checkbutton(threshWindow, text="Inverse Binary", var=stateOfInvBinary)
        inverseBinary.grid(column=0, row=2, padx=padx)
        toZero = ttk.Checkbutton(threshWindow, text="To Zero", var=stateOfToZero)
        toZero.grid(column=0, row=3, padx=padx)
        inverseToZero = ttk.Checkbutton(threshWindow, text="Inverse to Zero", var=stateOfInvZero)
        inverseToZero.grid(column=0, row=4, padx=padx)
        trunc = ttk.Checkbutton(threshWindow, text="Trunc", var=stateOfTrunc)
        trunc.grid(column=0, row=5, padx=padx)

        thresholdLabel = t.Label(threshWindow, text="Enter Threshold", fg=fg, bg=titleBg)
        thresholdLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        thresholdLabel.grid(column=0, row=6, padx=padx, pady=pady)
        threshold = t.Entry(threshWindow)
        threshold.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        threshold.grid(column=0, row=7)
        maxLabel = t.Label(threshWindow, text="Enter Max Value", fg=fg, bg=titleBg)
        maxLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        maxLabel.grid(column=0, row=8, padx=padx, pady=pady)
        max = t.Entry(threshWindow)
        max.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        max.grid(column=0, row=9)
        folderLabel = t.Label(threshWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=10, padx=padx, pady=pady)
        folder = t.Entry(threshWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=11)

        def threshPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(threshold.get()) == 0 or len(max.get()) == 0:
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
            status = makeAndCheckThreshFolders(folder.get(), stateOfBinary, stateOfInvBinary, stateOfToZero,
                                               stateOfInvZero, stateOfTrunc)
            if not status:
                messagebox.showinfo("ERROR", "Could not find or make threshold type specific folders")
                return
            for i in listOfNames:
                img1 = cv2.imread(dir.get() + "\\" + i)
                if stateOfBinary.get():
                    retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_BINARY)
                    cv2.imwrite(folder.get() + "\\" + "Binary\\thresh-binary-" + i, threshImg)
                if stateOfInvBinary.get():
                    retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_BINARY_INV)
                    cv2.imwrite(folder.get() + "\\" + "InverseBinary\\thresh-Inversebinary-" + i, threshImg)
                if stateOfToZero.get():
                    retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_TOZERO)
                    cv2.imwrite(folder.get() + "\\" + "ToZero\\thresh-ToZero-" + i, threshImg)
                if stateOfInvZero.get():
                    retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_TOZERO_INV)
                    cv2.imwrite(folder.get() + "\\" + "InverseToZero\\thresh-InverseToZero-" + i, threshImg)
                if stateOfTrunc.get():
                    retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_TRUNC)
                    cv2.imwrite(folder.get() + "\\" + "Trunc\\thresh-Trunc-" + i, threshImg)
            getFiles()
            threshWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if len(threshold.get()) == 0 or len(max.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a valid color")
                return
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            img1 = Image.open(dir.get() + "\\" + listOfNames[0])
            if stateOfBinary.get():
                retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_BINARY)
                cv2.imshow("Binary", threshImg)
            if stateOfInvBinary.get():
                retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_BINARY_INV)
                cv2.imshow("Inverse Binary", threshImg)
            if stateOfToZero.get():
                retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_TOZERO)
                cv2.imshow("To Thresholding", threshImg)
            if stateOfInvZero.get():
                retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_TOZERO_INV)
                cv2.imshow("Inverse to Zero", threshImg)
            if stateOfTrunc.get():
                retval, threshImg = cv2.threshold(img1, int(threshold.get()), int(max.get()), cv2.THRESH_TRUNC)
                cv2.imshow("Trunc", threshImg)

        thresholdPreviewButton = t.Button(threshWindow, text="Preview", fg=fg, bg=bg)
        thresholdPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                         relief=buttonRelief,
                                         command=previewPushed)
        thresholdPreviewButton.grid(column=0, row=12, padx=padx, pady=pady)
        thresholdsButton = t.Button(threshWindow, text="Threshold", fg=fg, bg=bg)
        thresholdsButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=threshPushed)
        thresholdsButton.grid(column=0, row=13, padx=padx, pady=pady)
        threshWindow.mainloop()

    thresholdWindowButton = t.Button(enhanceWindow, text="Threshold Menu", fg=fg, bg=bg)
    thresholdWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                    command=threshWindowPushed)
    thresholdWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeEdgeDetectButton(column, row):
    """
    Makes button to open edge detection menu, when its pressed the edge detection menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def edgeWindowPushed():
        """
        Places instruction, widgets and entries for colorization
        :return:
        """
        edgeWindow = t.Toplevel(enhanceWindow)
        edgeWindow.geometry("300x450")
        edgeWindow.title("Edge Detection")
        edgeWindow.iconbitmap("imagesForGUI\\edgeDetection.ico")

        def rightClick(event):
            helpEdgeWindow = t.Toplevel(edgeWindow)
            helpEdgeWindow.geometry("800x1000")
            helpEdgeWindow.title("Help")
            helpEdgeWindow.iconbitmap("imagesForGUI\\helpMenu.ico")
            photo = t.PhotoImage(file="imagesForGUI\\edgedection.GIF")
            lab = t.Label(helpEdgeWindow, image=photo)
            lab.pack()
            web = t.Label(helpEdgeWindow, text="https://docs.opencv.org/2.4/doc/tutorials/imgproc/imgtrans"
                                               "/canny_detector/canny_detector.html#:~:text=Canny%20does%20use"
                                               "%20two%20thresholds,threshold%2C%20then%20it%20is%20rejected.")
            web.pack()
            helpEdgeWindow.mainloop()

        edgeWindow.bind("<Button-3>", rightClick)
        scrollInstruct = scrolledtext.ScrolledText(edgeWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Edge detection requires a two\nthresholds. It also requires an\naperture_size. "
                              "It is the size of\nSobel kernel used for find image\ngradients. 2gradient specifies "
                              "the\nequation for finding gradient\nmagnitude. If it is selected, it\nuses a more "
                              "accurate equation,\notherwise it uses this function:"
                              "\nEdge_Gradient(G)=|Gx|+|Gy|.\nEnter a folder path to place "
                              "the\nresults in.")
        t1Label = t.Label(edgeWindow, text="Enter minVal", fg=fg, bg=titleBg)
        t1Label.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        t1Label.grid(column=0, row=1, padx=padx, pady=pady)
        threshold1 = t.Entry(edgeWindow)
        threshold1.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        threshold1.grid(column=0, row=2)
        t2Label = t.Label(edgeWindow, text="Enter axVal", fg=fg, bg=titleBg)
        t2Label.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        t2Label.grid(column=0, row=3, padx=padx, pady=pady)
        threshold2 = t.Entry(edgeWindow)
        threshold2.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        threshold2.grid(column=0, row=4)
        aptValueLabel = t.Label(edgeWindow, text="Enter aperture size", fg=fg, bg=titleBg)
        aptValueLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        aptValueLabel.grid(column=0, row=5, padx=padx, pady=pady)
        aptVal = t.Entry(edgeWindow)
        aptVal.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        aptVal.grid(column=0, row=6)
        stateOfChk = t.BooleanVar()
        stateOfChk.set(False)
        chk = ttk.Checkbutton(edgeWindow, text="2gradient", var=stateOfChk)
        chk.grid(column=0, row=7)
        folderLabel = t.Label(edgeWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=8, padx=padx, pady=pady)
        folder = t.Entry(edgeWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=9)

        def edgePushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(threshold1.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a first threshold value alue")
                return
            if len(threshold2.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a axVal value")
                return
            if len(aptVal.get()) != 0:
                aperture = int(aptVal.get())
                if aperture % 2 == 0 and 8 < aperture < 2:
                    messagebox.showinfo("ERROR", "Enter a valid aperture value (3, 5, 7)")
                    return
            else:
                aperture = 3
            t1 = float(threshold1.get())
            t2 = float(threshold2.get())
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = folderCheckCreation(folder.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = cv2.imread(dir.get() + "\\" + i)
                image2 = cv2.Canny(image1, t2, t1, stateOfChk.get(), aperture)
                cv2.imwrite(folder.get() + "\\-edgeDetect-" + i, image2)
            getFiles()
            edgeWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the brightness factor applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(threshold1.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a first threshold value")
                return
            if len(threshold2.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a second threshold value")
                return
            if len(aptVal.get()) != 0:
                aperture = int(aptVal.get())
                if aperture % 2 == 0 and 8 < aperture < 2:
                    messagebox.showinfo("ERROR", "Enter a valid aperture value (3, 5, 7)")
                    return
            else:
                aperture = 3
            t1 = float(threshold1.get())
            t2 = float(threshold2.get())

            image1 = cv2.imread(dir.get() + "\\" + listOfNames[0])
            image2 = cv2.Canny(image1, t2, t1, stateOfChk.get(), aperture)
            cv2.imwrite(folder.get() + "\\-edgeDetect-" + listOfNames[0], image2)
            cv2.imshow("Edge Detection", image2)

        edgePreviewButton = t.Button(edgeWindow, text="Preview", fg=fg, bg=bg)
        edgePreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                    relief=buttonRelief,
                                    command=previewPushed)
        edgePreviewButton.grid(column=0, row=10, padx=padx, pady=pady)
        edgeButton = t.Button(edgeWindow, text="Edge Detection", fg=fg, bg=bg)
        edgeButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                             command=edgePushed)
        edgeButton.grid(column=0, row=11, padx=padx, pady=pady)
        edgeWindow.mainloop()

    edgeWindowButton = t.Button(enhanceWindow, text="Edge Detection Menu", fg=fg, bg=bg)
    edgeWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                               command=edgeWindowPushed)
    edgeWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
    return row + 1


def makeGradientButton(column, row):
    """
    Makes button to open gradient menu, when its pressed the gradient menu is opened
    :param column: column to place button
    :param row: row to place button
    :return: int row updated, increased by 1
    """

    def gradientWindowPushed():
        """
        Makes gradient window with required instructions entries and other widgets
        :return:
        """
        gradientWindow = t.Toplevel(enhanceWindow)
        gradientWindow.geometry("300x400")
        gradientWindow.title("Gradient")
        gradientWindow.iconbitmap("imagesForGUI\\gradients.ico")

        def rightClick(event):
            helpGradientWindow = t.Toplevel(gradientWindow)
            helpGradientWindow.geometry("700x500")
            helpGradientWindow.title("Help")
            helpGradientWindow.iconbitmap("imagesForGUI\\helpMenu.ico")
            photo = t.PhotoImage(file="imagesForGUI\\gradient.GIF")
            lab = t.Label(helpGradientWindow, image=photo)
            lab.pack()
            web = t.Label(helpGradientWindow, text="https://docs.opencv.org/master/d5/d0f/tutorial_py_gradients.html")
            web.pack()
            helpGradientWindow.mainloop()

        gradientWindow.bind("<Button-3>", rightClick)
        scrollInstruct = scrolledtext.ScrolledText(gradientWindow, width=35, height=5)
        scrollInstruct.grid(column=0, row=0)
        scrollInstruct.insert(t.INSERT,
                              "Chooses at least one of the three\ngradient methods. Kernel size is\nthe size of the kernel "
                              "used and is\nonly needed for the sobel method.\nEnter a folder path to place "
                              "the\nresults in.")
        stateOfSobelX = t.BooleanVar()
        stateOfSobelX.set(False)
        stateOfSobelY = t.BooleanVar()
        stateOfSobelY.set(False)
        stateOfScharrX = t.BooleanVar()
        stateOfScharrX.set(False)
        stateOfScharrY = t.BooleanVar()
        stateOfScharrY.set(False)
        stateOfLaplacian = t.BooleanVar()
        stateOfLaplacian.set(False)
        # stateOfScharr = t.BooleanVar()
        # stateOfScharr.set(False)
        sobelBoxX = ttk.Checkbutton(gradientWindow, text="Sobel in x direction", var=stateOfSobelX)
        sobelBoxX.grid(column=0, row=1, padx=padx)
        sobelBoxY = ttk.Checkbutton(gradientWindow, text="Sobel in y direction", var=stateOfSobelY)
        sobelBoxY.grid(column=0, row=2, padx=padx)
        scharrBoxX = ttk.Checkbutton(gradientWindow, text="Scharr in x direction", var=stateOfScharrX)
        scharrBoxX.grid(column=0, row=3, padx=padx)
        scharrBoxY = ttk.Checkbutton(gradientWindow, text="Scharr in y direction", var=stateOfScharrY)
        scharrBoxY.grid(column=0, row=4, padx=padx)
        laplacianBox = ttk.Checkbutton(gradientWindow, text="Laplacian", var=stateOfLaplacian)
        laplacianBox.grid(column=0, row=5, padx=padx)
        kernelLabel = t.Label(gradientWindow, text="Enter kernel size", fg=fg, bg=titleBg)
        kernelLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        kernelLabel.grid(column=0, row=6, padx=padx, pady=pady)
        kernel = t.Entry(gradientWindow)
        kernel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        kernel.grid(column=0, row=7)
        folderLabel = t.Label(gradientWindow, text="Enter folder", fg=fg, bg=titleBg)
        folderLabel.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=titleRelief)
        folderLabel.grid(column=0, row=8, padx=padx, pady=pady)
        folder = t.Entry(gradientWindow)
        folder.configure(font=(font, fontSize), width=width, borderwidth=borderwidth)
        folder.grid(column=0, row=9)

        def gradientPushed():
            """
            Get folder, check that theirs file to PCA
            :return:
            """
            listOfNames = getFilesInDrop()
            if not stateOfLaplacian.get() and not stateOfSobelX.get() and not stateOfSobelY.get() and not stateOfScharrX.get() and not stateOfScharrY.get():
                messagebox.showinfo("ERROR", "Choose at least one gradient method")
                return
            if (stateOfSobelX.get() or stateOfSobelY.get()) and len(kernel.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a kernel size for Sobel methods")
                return
            if len(kernel.get()) > 0:
                ksize = int(kernel.get())
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return
            if len(folder.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a folder")
                return
            status = makeAndCheckGradientFolders(folder.get(), stateOfSobelX.get(), stateOfSobelY.get(),
                                                 stateOfScharrX.get(), stateOfScharrY.get(), stateOfLaplacian.get())
            if not status:
                messagebox.showinfo("ERROR", "Directory not found and could not be created")
                return
            for i in listOfNames:
                image1 = cv2.imread(dir.get() + "\\" + i)
                if stateOfSobelX.get():
                    image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 1, 0, ksize=ksize)
                    cv2.imwrite(folder.get() + "\\Sobel-x\\sobel-x-" + i, image2)
                if stateOfSobelY.get():
                    image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 0, 1, ksize=ksize)
                    cv2.imwrite(folder.get() + "\\Sobel-y\\sobel-y-" + i, image2)
                if stateOfScharrX.get():
                    image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 1, 0, -1)
                    cv2.imwrite(folder.get() + "\\Scharr-x\\scharr-x-" + i, image2)
                if stateOfScharrY.get():
                    image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 0, 1, -1)
                    cv2.imwrite(folder.get() + "\\Scharr-y\\scharr-y-" + i, image2)
                if stateOfLaplacian.get():
                    image2 = cv2.Laplacian(image1, int(-1/cv2.CV_64F))
                    cv2.imwrite(folder.get() + "\\Laplacian\\laplacian-" + i, image2)
            getFiles()
            gradientWindow.destroy()

        def previewPushed():
            """
            Allow user to see the first image in the dir with a the selected gradients applied
            :return:
            """
            listOfNames = getFilesInDrop()
            if not stateOfLaplacian.get() and not stateOfSobelX.get() and not stateOfSobelY.get() and not stateOfScharrX.get() and not stateOfScharrY.get():
                messagebox.showinfo("ERROR", "Choose at least one gradient method")
                return
            if (stateOfSobelX.get() or stateOfSobelY.get()) and len(kernel.get()) == 0:
                messagebox.showinfo("ERROR", "Enter a kernel size for Sobel methods")
                return
            if len(kernel.get()) > 0:
                ksize = int(kernel.get())
            if listOfNames[0] == "No files available" or listOfNames[0] == "No files chosen":
                messagebox.showinfo("ERROR", listOfNames[0])
                return

            image1 = cv2.imread(dir.get() + "\\" + listOfNames[0])
            if stateOfSobelX.get():
                image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 1, 0, ksize)
                cv2.imshow("Sobel in x direction", image2)
            if stateOfSobelY.get():
                image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 0, 1, ksize)
                cv2.imshow("Sobel in y direction", image2)
            if stateOfScharrX.get():
                image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 1, 0, -1)
                cv2.imshow("Scharr in x direction", image2)
            if stateOfScharrY.get():
                image2 = cv2.Sobel(image1, int(-1/cv2.CV_64F), 0, 1, -1)
                cv2.imshow("Scharr in y direction", image2)
            if stateOfLaplacian.get():
                image2 = cv2.Laplacian(image1, int(-1/cv2.CV_64F))
                cv2.imshow("Laplacian", image2)

        gradientPreviewButton = t.Button(gradientWindow, text="Preview", fg=fg, bg=bg)
        gradientPreviewButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth,
                                        relief=buttonRelief,
                                        command=previewPushed)
        gradientPreviewButton.grid(column=0, row=10, padx=padx, pady=pady)
        gradientButton = t.Button(gradientWindow, text="Gradient", fg=fg, bg=bg)
        gradientButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                 command=gradientPushed)
        gradientButton.grid(column=0, row=11, padx=padx, pady=pady)
        gradientWindow.mainloop()

    gradientWindowButton = t.Button(enhanceWindow, text="Gradient Menu", fg=fg, bg=bg)
    gradientWindowButton.configure(font=(font, fontSize), width=width, borderwidth=borderwidth, relief=buttonRelief,
                                   command=gradientWindowPushed)
    gradientWindowButton.grid(column=column, row=row, padx=padx, pady=pady)
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


def makePillowImageButtons(column):
    """
    This column effects individual images rather than combining the whole in some way.
    This include the Pillow methods: Contrast, Brightness, sharpness, equalize, solarize(invert pixels) maybe colorize
    :param column: the column the buttons are going to be placed in
    :return: int of updated column, column + 1
    """
    row = 0
    row = makeBrightnessButton(column, row)
    row = makeContrastButton(column, row)
    row = makeSharpnessButton(column, row)
    row = makeEqualizeButton(column, row)
    row = makeSolarizeButton(column, row)
    row = makeColorizeButton(column, row)
    return column + 1


def makeOpenCVImageButtons(column):
    """
    This column effects individual images rather than combining the whole in some way.
    This includes the OpenCV methods: threshold, edge detection, gradients
    :param column: the column the buttons are going to be placed in
    :return: int of updated column, column + 1
    """
    row = 0
    row = makeThresholdButton(column, row)
    row = makeEdgeDetectButton(column, row)
    row = makeGradientButton(column, row)
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
    column = makePillowImageButtons(column)
    column = makeOpenCVImageButtons(column)


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
