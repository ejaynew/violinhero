##### START MY CODE
# note: sheet music samples from https://github.com/cal-pratt/SheetVision
from detectPitches2 import recordPitchFromInput
from main import jpg2pitches
import time
import os
import tkinter.filedialog
from tkinter import *
from tkinter import messagebox
from gameOOP import GoalNote
from PIL import ImageTk,Image
import threading

def beats2duration(beats, tempo):
    return beats * 60 / tempo
    
def pitchIsClose(recorded, target):
    tolerance = 13
    return abs(float(recorded) - float(target)) <= tolerance
    
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)
        
def launchLibrary(preData):
    # adapted from https://stackoverflow.com/questions/43636683/how-to-code-for-a-new-window
    # make library window pop up
    popup = Toplevel()
    popup.grab_set()
    popup.title('Violin Hero Library')
    popup.geometry('500x500')
    data = preData
    preData.heart = 5
    # create the root and the canvas
    canvas = Canvas(popup, width=500, height=1000)
    canvas.configure(bd=0, highlightthickness=0)
    # create right scrollbar and connect to canvas Y
    # scrollbar code adapted from http://effbot.org/zone/tkinter-scrollbar-patterns.htm
    scrollbar = Scrollbar(popup)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set, scrollregion=(0, 0, 1000, 1000))
    scrollbar.config(command=canvas.yview)
    
    # draw library
    canvas.create_rectangle(0, 0, 500, 1000, fill="#0b4f6c")
    # canvas.create_text(250, 40, text="Library", fill="white", font="Arial 40")
    canvas.create_image(250, 40, image=data.library)
    loadImages(data)
    cols = 2 if len(data.libImg) >= 2 else len(data.libImg)
    rows = (len(data.libImg) // 2) + 1 if len(data.libImg) > 2 else 1
    xmargin = 60
    ymargin = 80
    dx = 225
    dy = 225
    p = 0
    for j in range(rows):
        for i in range(cols):
            canvas.create_image(i*dx + xmargin, j*dy + ymargin, anchor=NW, image=data.libImg[p])
            p += 1
            if p >= len(data.libImg):
                break
        if p >= len(data.libImg):
            break
    canvas.pack()
    
    def getRowCol(event, canvas, data):
        if xmargin <= event.x <= 500 - xmargin and ymargin <= event.y <= 1000 - ymargin:
            scrolled = 1
            if scrollbar.get()[0] > 0:
                scrolled = -1
            data = preData
            row = int((event.y + scrollbar.get()[1]*500 - scrolled*ymargin) // 400) + 1
            col = (event.x // (250)) + 1
            print(event.x, event.y)
            print("s", scrolled)
            print(event.y + scrollbar.get()[1]*500 - scrolled*ymargin)
            print(row, col)
            preData.selection = (row, col)
            preData.selected = True
            popup.destroy()
            selection_defs = {
            (1, 1) : 0,
            (1, 2) : 1,
            (2, 1) : 2,
            (2, 2) : 3,
            (3, 1) : 4,
            (3, 2) : 5,
            (4, 1) : 6,
            (4, 2) : 7,
            (5, 1) : 8,
            (5, 2) : 9,
            (6, 1) : 10,
            (6, 2) : 11
            }
            ind = selection_defs[preData.selection]
            tmpPath = preData.currSongs.split("Song: ")[ind + 1]
            path = tmpPath[:tmpPath.find("[") - 1]
            data.file = path
            loadImages(data)
            print(path)
            loadUpSong(path, preData)
        
    popup.bind("<Button-1>", lambda event: getRowCol(event, canvas, data))
    
    def loadUpSong(filePath, data):
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, 'songs.txt')
        currSongs = readFile(filename)
        for song in currSongs.split("Song: "):
            thisSong = song[:song.find("[")]
            if thisSong.strip() == filePath:
                if song.find(" b") != -1:
                    data.flat = True
                elif song.find(" #") != -1:
                    data.sharp = True
                data.loadingProgress = 0.5
                pitches = song[song.find("[")+1:song.find("]")]
                for pitch in pitches.split("(")[1:]:
                    data.goalPitches.append((pitch[1:pitch.find(",")-1], float(pitch[pitch.find(" ")+1:pitch.find(")")])))
                data.durs = []
                for pitch in data.goalPitches:
                    data.durs.append(pitch[1])
                data.goalNotes = []
                for pitch in data.goalPitches:
                    data.goalNotes.append(GoalNote(pitch[1], int(pitch[0]), data))
                    data.currPitch += 1
                data.loadingProgress = 1
                data.doneLoading = True
                print("Finished finding pitches.")
                print(data.goalPitches)
    
def startImages(data):
    # next two images from https://ui-ex.com/explore/violin-transparent-cartoon/
    here = os.path.dirname(os.path.abspath(__file__))
    filename2 = os.path.join(here, 'img/violin.png')
    data.violin = Image.open(filename2)
    data.violin = data.violin.resize((100, 100), Image.ANTIALIAS)
    data.violin = ImageTk.PhotoImage(data.violin)
    filename3 = os.path.join(here, 'img/violin2.png')
    data.violin2 = Image.open(filename3)
    data.violin2 = data.violin2.resize((100, 100), Image.ANTIALIAS)
    data.violin2 = ImageTk.PhotoImage(data.violin2)
    # next image from https://ui-ex.com/explore/music-transparent-folk/
    filename4 = os.path.join(here, 'img/music.png')
    data.music = Image.open(filename4)
    data.music = data.music.resize((500, 150), Image.ANTIALIAS)
    data.music = ImageTk.PhotoImage(data.music)
    # font from https://fontmeme.com/guitar-hero-font/
    filename5 = os.path.join(here, 'img/title.png')
    data.title = Image.open(filename5)
    data.title = data.title.resize((400, 170), Image.ANTIALIAS)
    data.title = ImageTk.PhotoImage(data.title)
    filename6 = os.path.join(here, 'img/gameMode.png')
    data.gameTitle = Image.open(filename6)
    data.bigGame = data.gameTitle.resize((400, 170), Image.ANTIALIAS)
    data.bigGame = ImageTk.PhotoImage(data.bigGame)
    data.gameTitle = data.gameTitle.resize((100, 50), Image.ANTIALIAS)
    data.gameTitle = ImageTk.PhotoImage(data.gameTitle)
    filename7 = os.path.join(here, 'img/tuneMode.png')
    data.tuneTitle = Image.open(filename7)
    data.bigTune = data.tuneTitle.resize((400, 170), Image.ANTIALIAS)
    data.bigTune = ImageTk.PhotoImage(data.bigTune)
    data.tuneTitle = data.tuneTitle.resize((100, 50), Image.ANTIALIAS)
    data.tuneTitle = ImageTk.PhotoImage(data.tuneTitle)
    filename8 = os.path.join(here, 'img/browse.png')
    data.browse = Image.open(filename8)
    data.browse = data.browse.resize((100, 50), Image.ANTIALIAS)
    data.browse = ImageTk.PhotoImage(data.browse)
    filename9 = os.path.join(here, 'img/library.png')
    data.library = Image.open(filename9)
    data.library = data.library.resize((100, 50), Image.ANTIALIAS)
    data.library = ImageTk.PhotoImage(data.library)
    
def init(data):
    data.buttonWidth = data.width//8
    data.buttonHeight = data.width//16
    data.note_defs = {
     -4 : ("g5", 79, 0),
     -3 : ("f5", 77, 3),
     -2 : ("e5", 76, 2),
     -1 : ("d5", 74, 1),
      0 : ("c5", 72, 0),
      1 : ("b4", 71, 3),
      2 : ("a4", 69, 2),
      3 : ("g4", 67, 1),
      4 : ("f4", 65, 0),
      5 : ("e4", 64, 3),
      6 : ("d4", 62, 2),
      7 : ("c4", 60, 1),
      8 : ("b3", 59, 0),
      9 : ("a3", 57, 3),
     10 : ("g3", 55, 2),
     11 : ("f3", 53, 1),
     12 : ("e3", 52, 0),
     13 : ("d3", 50, 3),
     14 : ("c3", 48, 2),
     15 : ("b2", 47, 1),
     16 : ("a2", 45, 0),
     17 : ("f2", 43, 3),
    }
    data.finger_defs = {
    79 : 0, 77: 3, 76: 2, 74: 1, 72: 0, 71: 3, 69 : 2, 67 : 1, 65 : 0, 64 : 3, 
    62 : 2, 60 : 1, 59 : 0, 57 : 3, 55 : 2, 53 : 1, 52 : 0, 50 : 3, 48 : 2, 
    47 : 1, 45 : 0, 43 : 3
    }
    data.tempo = 180
    data.currPitch = 0
    data.mode = "startPage"
    data.currPlayPitch = 0
    data.goalPitches = []
    data.durs = []
    for pitch in data.goalPitches:
        data.durs.append(pitch[1])
    data.goalNotes = []
    for pitch in data.goalPitches:
        data.goalNotes.append(GoalNote(pitch[1], int(pitch[0]), data))
        data.currPitch += 1
    data.tuneText = "This is tune mode.\nClick play to begin."
    data.gameText = "This is game mode.\nClick play to begin."
    data.backWidth = data.width//8
    data.backHeight = data.height//16
    data.featureSize = data.width//20
    data.widthMargin = data.width//20
    data.tunePause = True
    data.gamePause = True
    data.tuneTimer = 0
    data.doneLoading = False
    data.stringWidth = data.width//4
    # colors
    data.RED = "#b80c09"
    data.LRED = "#e8472e"
    data.BLUE = "#0b4f6c"
    data.CYAN = "#01baef"
    data.WHITE = "#fbfbff"
    data.BLACK = "#040f16"
    data.GRAY = "#d3d3d3"
    data.DGRAY = "#afaeae"
    data.LGRAY = "#eaeaea"
    data.YELLOW = "#fff493"
    data.GREEN = "#54e55e"
    data.DBLUE = "#545ee5"
    data.DRED = "#db4632"
    data.ORANGE = "#f2a713"
    data.tuneHit = 0
    data.gameHit = 0
    data.nextMode = None
    data.currInPitch = 0
    data.loadBrowsing = False
    data.loadingText = "Loading"
    data.loadingTimer = 0
    data.gradeSize = data.width//20
    data.gradeHeight = data.height//7
    data.loadingProgress = -1
    data.barWidth = data.width//4
    data.barHeight = data.height//25
    data.finalHit = 1
    data.finalCurrPitch = 1
    data.file = ""
    data.tuneTimer = 0
    data.gameTimer = 0
    data.readyText = ""
    data.fingerColor = data.WHITE
    data.currFinger = -1
    data.helpSize = data.width//15
    data.performanceLog = []
    data.finalLog = []
    data.graphxMargin = data.width//6
    data.graphyMargin = data.height//4
    data.pointSize = data.width//200
    data.sharp = False
    data.flat = False
    # next two lines from https://stackoverflow.com/questions/21957131/python-not-finding-file-in-the-same-directory
    here = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(here, 'songs.txt')
    data.currSongs = readFile(filename)
    data.libImg = []
    data.selected = False
    data.beat = beats2duration(4.0, data.tempo)
    data.currBeat = 0
    data.metronomeSize = data.width//60
    data.tuneTimerLast = 0
    data.meter = True
    data.nextMeter = False
    startImages(data)
    data.tuneMiss = 0
    
def loadImages(data):
    if len(data.file) > 0:
        # next 3 lines adapted from https://stackoverflow.com/questions/47442051/reading-an-image-from-a-url-resizing-it-and-applying-antialiasing
        data.image = Image.open(data.file)
        data.image = data.image.resize((500, 500), Image.ANTIALIAS)
        data.image = ImageTk.PhotoImage(data.image)
    for song in data.currSongs.split("Song: ")[1:]:
        thisSong = song[:song.find("[")].strip()
        print(thisSong)
        tmpImg = Image.open(thisSong)
        tmpImg = tmpImg.resize((150, 200), Image.ANTIALIAS)
        tmpImg = ImageTk.PhotoImage(tmpImg)
        data.libImg.append(tmpImg)
    
def getGrade(stat, data):
    if stat < 60:
        return ("F", "Try taking it slow!", data.CYAN)
    elif stat < 70:
        return ("D", "Practice makes perfect!", data.RED)
    elif stat < 80:
        return ("C", "Keep working on it!", data.ORANGE)
    elif stat < 90:
        return ("B", "You're doing great!", data.YELLOW)
    else:
        return ("A", "Fantastic job!", data.GREEN)
    
def mousePressed(event, data, canvas):
    if data.mode == "startPage":
        startMousePressed(event, data)
    elif data.mode == "loadingMode":
        loadingMousePressed(event, data, canvas)
    elif data.mode == "tuneMode":
        tuneMousePressed(event, data)
    elif data.mode == "gameMode":
        gameMousePressed(event, data, canvas)
    elif data.mode == "statMode":
        statMousePressed(event, data)
    elif data.mode == "helpMode":
        helpMousePressed(event, data)

def keyPressed(event, data):
    if event.keysym == "r":
        print("resetting...")
        init(data)

def timerFired(data):
    if data.mode == "startPage":
        startTimerFired(data)
    elif data.mode == "loadingMode":
        loadingTimerFired(data)
    elif data.mode == "tuneMode":
        tuneTimerFired(data)
    elif data.mode == "gameMode":
        gameTimerFired(data)
    elif data.mode == "statMode":
        statTimerFired(data)
    elif data.mode == "helpMode":
        helpTimerFired(data)
    elif data.mode == "gameStart":
        gameStartTimerFired(data)

def redrawAll(canvas, data):
    if data.mode == "startPage":
        startRedrawAll(canvas, data)
    elif data.mode == "loadingMode":
        loadingRedrawAll(canvas, data)
    elif data.mode == "tuneMode":
        tuneRedrawAll(canvas, data)
    elif data.mode == "gameMode":
        gameRedrawAll(canvas, data)
    elif data.mode == "statMode":
        statRedrawAll(canvas, data)
    elif data.mode == "helpMode":
        helpRedrawAll(canvas, data)
    elif data.mode == "gameStart":
        gameStartRedrawAll(canvas, data)
     
##### START SCREEN MODE #####
def startRedrawAll(canvas, data):
    # background
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.CYAN)
    # violin image
    canvas.create_image(3.5*data.width//4, 0.9*data.height//4, anchor=CENTER, image=data.violin)
    canvas.create_image(0.5*data.width//4, 0.9*data.height//4, anchor=CENTER, image=data.violin2)
    canvas.create_image(data.width//2, 3*data.height//4, anchor=CENTER, image=data.music)
    # title
    canvas.create_image(data.width//2, 0.8*data.height//4, anchor=CENTER, image=data.title)
    # canvas.create_text(data.width//2, data.height//6, text="Violin Hero", font="Arial 70", fill=data.WHITE)
    # tune mode
    canvas.create_rectangle(data.width//4 - data.buttonWidth, 
        data.height//2 - data.buttonHeight, data.width//4 + data.buttonWidth, 
        data.height//2 + data.buttonHeight, fill=data.BLUE)
    # canvas.create_text(data.width//4, data.height//2, text="Tune Mode", font="Arial 20", fill=data.WHITE)
    canvas.create_image(data.width//4, data.height//2, image=data.tuneTitle)
    # game mode
    canvas.create_rectangle(3*data.width//4 - data.buttonWidth,
    data.height//2 - data.buttonHeight, 3*data.width//4 + data.buttonWidth,
    data.height//2 + data.buttonHeight, fill=data.RED)
    canvas.create_image(3*data.width//4, data.height//2, image=data.gameTitle)
    # canvas.create_text(3*data.width//4, data.height//2, text="Game Mode", font="Arial 20", fill=data.WHITE)
    # help button
    canvas.create_oval(3.5*data.width//4, 3.5*data.height//4, 3.5*data.width//4 + data.helpSize, 3.5*data.height//4 + data.helpSize, fill=data.DGRAY)
    canvas.create_text(3.5*data.width//4 + data.helpSize//2, 3.5*data.height//4 + data.helpSize//2, text="?", font="Arial 14", fill=data.WHITE)
    
def startMousePressed(event, data):
    # tune mode
    if data.width//4 - data.buttonWidth <= event.x <= data.width//4 + data.buttonWidth \
    and data.height//2 - data.buttonHeight <= event.y <= data.height//2 + data.buttonHeight:
        data.mode = "loadingMode"
        data.nextMode = "tuneMode"
    # game mode
    elif 3*data.width//4 - data.buttonWidth <= event.x <= 3*data.width//4 + data.buttonWidth \
    and data.height//2 - data.buttonHeight <= event.y <= data.height//2 + data.buttonHeight:
        data.mode = "loadingMode"
        data.nextMode = "gameMode"
    # help mode
    elif 3.5*data.width//4 <= event.x <= 3.5*data.width//4 + data.helpSize and 3.5*data.height//4 <= event.y <= 3.5*data.height//4 + data.helpSize:
        data.mode = "helpMode"
        
def startTimerFired(data):
    pass
    
##### HELP MODE #####
def helpRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.BLACK)
    # back button
    canvas.create_rectangle(0, 0, data.backWidth, data.backHeight, fill=data.RED)
    canvas.create_text(data.backWidth//2, data.backHeight//2, text="Back", font="Arial 16", fill=data.WHITE)
    # help text
    canvas.create_text(data.width//2, data.height//11, text="Overview", font="Arial 50", fill=data.WHITE)
    canvas.create_text(data.width//2, data.height//5, text="Welcome to Violin Hero:", font="Arial 27", fill=data.WHITE)
    canvas.create_text(data.width//2, 1.3*data.height//5, text="making your sight reading fun since 2019!", font="Arial 18", fill=data.WHITE)
    canvas.create_text(data.width//2, 1.1*data.height//3, text="This app is used in two ways:", font="Arial 16", fill=data.WHITE)
    canvas.create_rectangle(data.width//4 - data.buttonWidth, data.height//2 - data.buttonHeight, data.width//4 + data.buttonWidth, data.height//2 + data.buttonHeight, fill=data.BLUE)
    canvas.create_image(data.width//4, data.height//2, image=data.tuneTitle)
    # canvas.create_text(data.width//4, data.height//2, text="Tune Mode", font="Arial 20", fill=data.WHITE)
    canvas.create_rectangle(3*data.width//4 - data.buttonWidth, data.height//2 - data.buttonHeight, 3*data.width//4 + data.buttonWidth, data.height//2 + data.buttonHeight, fill=data.RED)
    canvas.create_image(3*data.width//4, data.height//2, image=data.gameTitle)
    # canvas.create_text(3*data.width//4, data.height//2, text="Game Mode", font="Arial 20", fill=data.WHITE)
    canvas.create_text(data.widthMargin, 1.25*data.height//2, text="Tune mode will display your sheet music and allow you to play normally while providing\nreal time feedback on your performance.\n\nGame mode will display your music as color-coded graphic notes and allow you to play\nguitar hero style.\n\nBoth modes will then provide statistics and give you tips for improvement.\n\nClick on one of the buttons above to read more about how to use each mode.\n\nHappy practicing!", font="Arial 16", fill=data.WHITE, anchor=NW)
    
def helpMousePressed(event, data):
    if 0 <= event.x <= data.backWidth and 0 <= event.y <= data.backHeight:
        # back button was pressed
        data.mode = "startPage"
    
def helpTimerFired(data):
    pass
    
##### GAME MODE HELP #####
def gameHelpRedrawAll(canvas, data):
    pass
    
def gameHelpMousePressed(event, data):
    pass
    
def gameHelpTimerFired(data):
    pass

##### TUNE MODE HELP #####
def tuneHelpRedrawAll(canvas, data):
    pass
    
def tuneHelpMousePressed(event, data):
    pass
    
def tuneHelpTimerFired(data):
    pass

##### LOADING SCREEN MODE #####
def loadingRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.CYAN)
    # back button
    canvas.create_rectangle(0, 0, data.backWidth, data.backHeight, fill=data.RED)
    canvas.create_text(data.backWidth//2, data.backHeight//2, text="Back", font="Arial 16", fill=data.WHITE)
    if data.nextMode == "gameMode":
        # currText = "Game Mode"
        currImg = data.bigGame
    else:
        # currText = "Tune Mode"
        currImg = data.bigTune
    # canvas.create_text(data.width//2, data.height//4, text=currText, font="Arial 50", fill=data.WHITE)
    canvas.create_image(data.width//2, data.height//4, image=currImg)
    if not data.loadBrowsing:
        # haven't selected a file yet, have button
        canvas.create_rectangle(data.width//4 - data.buttonWidth, data.height//2 - data.buttonHeight, data.width//4 + data.buttonWidth, data.height//2 + data.buttonHeight, fill=data.BLUE)
        # canvas.create_text(data.width//4, data.height//2, text="Browse for a file", font="Arial 18", fill=data.WHITE)
        canvas.create_image(data.width//4, data.height//2, image=data.browse)
        # select from library
        canvas.create_rectangle(3*data.width//4 - data.buttonWidth, data.height//2 - data.buttonHeight, 3*data.width//4 + data.buttonWidth, data.height//2 + data.buttonHeight, fill=data.BLUE)
        # canvas.create_text(3*data.width//4, data.height//2, text="Select from library", font="Arial 18", fill=data.WHITE)
        canvas.create_image(3*data.width//4, data.height//2, image=data.library)
    else:
        # have selected a file, converting to pitches
        # loading...
        canvas.create_text(data.width//2, 2.5*data.height//4, text=data.loadingText, font="Arial 24", fill=data.WHITE)
        # progress bar
        canvas.create_rectangle(data.width//2 - data.barWidth, data.height//2 - data.barHeight, data.width//2 + data.barWidth, data.height//2 + data.barHeight, fill=data.WHITE)
        canvas.create_rectangle(data.width//2 - data.barWidth, data.height//2 - data.barHeight, (data.width//2 + data.loadingProgress * data.barWidth), data.height//2 + data.barHeight, fill=data.GREEN)
    canvas.create_image(data.width//2, 3*data.height//4, image=data.music)
    
def loadingMousePressed(event, data, canvas):
    if 0 <= event.x <= data.backWidth and 0 <= event.y <= data.backHeight:
        # back button was pressed
        data.mode = "startPage"
    elif not data.loadBrowsing:
        if data.width//4 - data.buttonWidth <= event.x <= data.width//4 + data.buttonWidth \
        and data.height//2 - data.buttonHeight <= event.y <= data.height//2 + data.buttonHeight:
            if len(data.goalPitches) < 2:
                try:
                    # this line from https://stackoverflow.com/questions/16798937/creating-a-browse-button-with-tkinter
                    data.file =  filedialog.askopenfilename(initialdir = "/",title = "Select file")
                    data.loadBrowsing = True
                    loadImages(data)
                    a = threading.Thread(target=jpg2pitches, args=(data.file, data), daemon=True)
                    a.start()
                except:
                    print("Wrong file type.")
            else:
                data.mode = data.nextMode
        elif 3*data.width//4 - data.buttonWidth <= event.x <= 3*data.width//4 + data.buttonWidth \
        and data.height//2 - data.buttonHeight <= event.y <= data.height//2 + data.buttonHeight:
            if len(data.goalPitches) < 2:
                try:
                    h = threading.Thread(target=launchLibrary, args=(data,))
                    h.start()
                    data.loadBrowsing = True
                except:
                    print("Took too long")
            else:
                data.mode = data.nextMode
        
def loadingTimerFired(data):
    data.loadingTimer += 1
    if data.doneLoading:
        data.mode = data.nextMode
    elif data.loadingTimer % 40 == 0:
        data.loadingText = "Loading"
    elif data.loadingTimer % 10 == 0:
        data.loadingText += "."
        
##### TUNE MODE #####
def tuneRedrawAll(canvas, data):
    # canvas.create_rectangle(0, 0, data.width, data.height, fill=data.BLACK)
    canvas.create_image(0, data.backHeight, anchor=NW, image=data.image)
    # back button
    canvas.create_rectangle(0, 0, data.backWidth, data.backHeight, fill=data.RED)
    canvas.create_text(data.backWidth//2, data.backHeight//2, text="Back", font="Arial 16", fill=data.WHITE)
    # features bar
    canvas.create_rectangle(0, 8.5*data.height//10, data.width, data.height, fill=data.GRAY)
    # pause/play button
    if data.tunePause:
        # play button
        canvas.create_oval(data.width//2 - data.featureSize, 9.25*data.height//10 - data.featureSize, data.width//2 + data.featureSize, 9.25*data.height//10 + data.featureSize, fill=data.LGRAY)
        canvas.create_polygon(data.width//2 - data.featureSize//2.5, 9.25*data.height//10 - data.featureSize//2, data.width//2 - data.featureSize//2.5, 9.25*data.height//10 + data.featureSize//2, data.width//2 + data.featureSize//1.5, 9.25*data.height//10, fill=data.BLACK)
    else:
        # pause button
        canvas.create_oval(data.width//2 - data.featureSize, 9.25*data.height//10 - data.featureSize, data.width//2 + data.featureSize, 9.25*data.height//10 + data.featureSize, fill=data.LGRAY)
        canvas.create_rectangle(data.width//2 - data.featureSize//2, 9.25*data.height//10 - data.featureSize//2, data.width//2 - data.featureSize//6, 9.25*data.height//10 + data.featureSize//2, fill=data.BLACK)
        canvas.create_rectangle(data.width//2 + data.featureSize//2, 9.25*data.height//10 - data.featureSize//2, data.width//2 + data.featureSize//6, 9.25*data.height//10 + data.featureSize//2, fill=data.BLACK)
    # stat bar
    canvas.create_rectangle(3*data.width//4, 0, data.width, data.height//5, fill=data.WHITE)
    canvas.create_text(3.5*data.width//4, data.height//30, text="Feedback:", font="Arial 14")
    canvas.create_text(3.5*data.width//4, data.height//10, text=data.tuneText, font="Arial 14")
    currStat = str(data.tuneHit) + "/" + str(data.currPlayPitch + 1)
    canvas.create_text(3.5*data.width//4, data.height//6, text=currStat, font="Arial 14")
    canvas.create_rectangle(3*data.width//4, data.height//5, data.width, data.height//5 + data.backHeight, fill=data.LGRAY)
    canvas.create_text(3.5*data.width//4, data.height//5 + data.backHeight//2, text="Go to stats", font="Arial 14") 
    # metronome
    # if not data.tunePause and data.tuneTimer % data.beat*4 <= 0.1:
    #     canvas.create_rectangle(3*data.width//4 - data.metronomeSize, 9.25*data.height//10 - data.metronomeSize, 3*data.width//4 + data.metronomeSize, 9.25*data.height//10 + data.metronomeSize, fill=data.RED)
    
    if data.meter:
        canvas.create_rectangle(3*data.width//4 - data.metronomeSize, 9.25*data.height//10 - data.metronomeSize, 3*data.width//4 + data.metronomeSize, 9.25*data.height//10 + data.metronomeSize, fill=data.RED)
        
def tuneMousePressed(event, data):
    if 0 <= event.x <= data.backWidth and 0 <= event.y <= data.backHeight:
        # back button was pressed
        data.mode = "startPage"
    elif data.width//2 - data.featureSize <= event.x <= data.width//2 + data.featureSize \
    and 9.25*data.height//10 - data.featureSize <= event.y <= 9.25*data.height//10 + data.featureSize:
        data.tunePause = not data.tunePause
        if not data.tunePause:
            d = threading.Thread(target=playTune, args=(data,))
            d.start()
    elif 3*data.width//4 <= event.x <= data.width and data.height//5 <= event.y <= data.height//5 + data.backHeight:
        data.tunePause = True
        data.finalHit = data.tuneHit
        data.finalCurrPitch = data.tuneHit + data.tuneMiss
        data.finalLog = data.performanceLog
        data.mode = "statMode"
        
def playTune(data):
    for pitch in data.goalPitches:
        if not data.tunePause:
            data.currPlayPitch += 1
            dur = pitch[1]
            e = threading.Thread(recordPitchFromInput(dur, data))
            e.start()
            if pitchIsClose(data.currInPitch, pitch[0]):
                data.tuneText = "Nailed it!"
                data.tuneHit += 1
            else:
                data.tuneMiss += 1
                data.tuneText = "Oof, pretty off there."
            currStat = ((data.tuneHit)/(data.tuneHit + data.tuneMiss))*100
            data.performanceLog.append(currStat)
    data.tunePause = True
    data.finalHit = data.tuneHit
    data.finalCurrPitch = data.tuneHit + data.tuneMiss
    data.finalLog = data.performanceLog
    data.mode = "statMode"
    
def tuneTimerFired(data):
    if not data.tunePause:
        data.tuneTimer += 1
        if data.tuneTimer % (data.beat*10) <= 3:
            data.meter = True
        else:
            data.meter = False
        
##### GAME MODE #####
def gameRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.BLUE)
    # keys
    for i in range(4):
        canvas.create_rectangle(data.widthMargin + data.stringWidth*i, 7.5*data.height//10, data.stringWidth*(i+1) - data.widthMargin, 8*data.height//10, outline=data.fingerColor, width=data.width//100)
    # notes
    for goalNote in data.goalNotes:
        data.currPitch += 1
        goalNote.draw(canvas, data)
    data.currPitch = 0
    # back button
    canvas.create_rectangle(0, 0, data.backWidth, data.backHeight, fill=data.RED)
    canvas.create_text(data.backWidth//2, data.backHeight//2, text="Back", font="Arial 16", fill=data.WHITE)
    # features bar
    canvas.create_rectangle(0, 8.5*data.height//10, data.width, data.height, fill=data.GRAY)
    # pause/play button
    if data.gamePause:
        # play button
        canvas.create_oval(data.width//2 - data.featureSize, 9.25*data.height//10 - data.featureSize, data.width//2 + data.featureSize, 9.25*data.height//10 + data.featureSize, fill=data.LGRAY)
        canvas.create_polygon(data.width//2 - data.featureSize//2.5, 9.25*data.height//10 - data.featureSize//2, data.width//2 - data.featureSize//2.5, 9.25*data.height//10 + data.featureSize//2, data.width//2 + data.featureSize//1.5, 9.25*data.height//10, fill=data.BLACK)
    else:
        # pause button
        canvas.create_oval(data.width//2 - data.featureSize, 9.25*data.height//10 - data.featureSize, data.width//2 + data.featureSize, 9.25*data.height//10 + data.featureSize, fill=data.LGRAY)
        canvas.create_rectangle(data.width//2 - data.featureSize//2, 9.25*data.height//10 - data.featureSize//2, data.width//2 - data.featureSize//6, 9.25*data.height//10 + data.featureSize//2, fill=data.BLACK)
        canvas.create_rectangle(data.width//2 + data.featureSize//2, 9.25*data.height//10 - data.featureSize//2, data.width//2 + data.featureSize//6, 9.25*data.height//10 + data.featureSize//2, fill=data.BLACK)
    # stat bar
    canvas.create_rectangle(3*data.width//4, 0, data.width, data.height//5, fill=data.WHITE)
    canvas.create_text(3.5*data.width//4, data.height//30, text="Feedback:", font="Arial 14")
    canvas.create_text(3.5*data.width//4, data.height//10, text=data.gameText, font="Arial 14")
    currStat = str(data.gameHit) + "/" + str(data.currPlayPitch + 1)
    canvas.create_text(3.5*data.width//4, data.height//6, text=currStat, font="Arial 14")
    canvas.create_rectangle(3*data.width//4, data.height//5, data.width, data.height//5 + data.backHeight, fill=data.LGRAY)
    canvas.create_text(3.5*data.width//4, data.height//5 + data.backHeight//2, text="Go to stats", font="Arial 14")
    
def gameMousePressed(event, data, canvas):
    if 0 <= event.x <= data.backWidth and 0 <= event.y <= data.backHeight:
        # back button was pressed
        data.mode = "startPage"
    elif data.width//2 - data.featureSize <= event.x <= data.width//2 + data.featureSize \
    and 9.25*data.height//10 - data.featureSize <= event.y <= 9.25*data.height//10 + data.featureSize:
        if data.gamePause:
            # launch countdown
            data.mode = "gameStart"
        data.gamePause = not data.gamePause
    elif 3*data.width//4 <= event.x <= data.width and data.height//5 <= event.y <= data.height//5 + data.backHeight:
        # pressed go to stats
        data.gamePause = True
        data.finalHit = data.gameHit
        data.finalCurrPitch = data.currPlayPitch
        data.finalLog = data.performanceLog
        data.mode = "statMode"
        
def playGame(data):
    for note in data.goalNotes:
        if not data.gamePause:
            dur = note.dur
            c = threading.Thread(recordPitchFromInput(dur, data))
            c.start()
            if pitchIsClose(data.currInPitch, note.pitch):
                data.gameText = "Nailed it!"
                data.gameHit += 1
                data.fingerColor = data.WHITE
            else:
                data.gameText = "Oof, pretty off there."
                data.fingerColor = data.LRED
            currStat = ((data.gameHit)/(data.currPlayPitch + 1))*100
            data.performanceLog.append(currStat)
    data.gamePause = True
    data.finalHit = data.gameHit
    data.finalCurrPitch = data.currPlayPitch
    data.finalLog = data.performanceLog
    data.mode = "statMode"
        
def gameTimerFired(data):
    if not data.gamePause:
        for goalNote in data.goalNotes:
            data.currPitch += 1
            goalNote.move(data)
        data.currPitch = 0
        
def gameStartRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.BLUE)
    # keys
    for i in range(4):
        canvas.create_rectangle(data.widthMargin + data.stringWidth*i, 7.5*data.height//10, data.stringWidth*(i+1) - data.widthMargin, 8*data.height//10, outline=data.fingerColor, width=data.width//100)
    # notes
    for goalNote in data.goalNotes:
        data.currPitch += 1
        goalNote.draw(canvas, data)
    data.currPitch = 0
    # back button
    canvas.create_rectangle(0, 0, data.backWidth, data.backHeight, fill=data.RED)
    canvas.create_text(data.backWidth//2, data.backHeight//2, text="Back", font="Arial 16", fill=data.WHITE)
    # features bar
    canvas.create_rectangle(0, 8.5*data.height//10, data.width, data.height, fill=data.GRAY)
    # pause/play button
    if data.gamePause:
        # play button
        canvas.create_oval(data.width//2 - data.featureSize, 9.25*data.height//10 - data.featureSize, data.width//2 + data.featureSize, 9.25*data.height//10 + data.featureSize, fill=data.LGRAY)
        canvas.create_polygon(data.width//2 - data.featureSize//2.5, 9.25*data.height//10 - data.featureSize//2, data.width//2 - data.featureSize//2.5, 9.25*data.height//10 + data.featureSize//2, data.width//2 + data.featureSize//1.5, 9.25*data.height//10, fill=data.BLACK)
    else:
        # pause button
        canvas.create_oval(data.width//2 - data.featureSize, 9.25*data.height//10 - data.featureSize, data.width//2 + data.featureSize, 9.25*data.height//10 + data.featureSize, fill=data.LGRAY)
        canvas.create_rectangle(data.width//2 - data.featureSize//2, 9.25*data.height//10 - data.featureSize//2, data.width//2 - data.featureSize//6, 9.25*data.height//10 + data.featureSize//2, fill=data.BLACK)
        canvas.create_rectangle(data.width//2 + data.featureSize//2, 9.25*data.height//10 - data.featureSize//2, data.width//2 + data.featureSize//6, 9.25*data.height//10 + data.featureSize//2, fill=data.BLACK)
    # stat bar
    canvas.create_rectangle(3*data.width//4, 0, data.width, data.height//5, fill=data.WHITE)
    canvas.create_text(3.5*data.width//4, data.height//30, text="Feedback:", font="Arial 14")
    canvas.create_text(3.5*data.width//4, data.height//10, text=data.gameText, font="Arial 14")
    currStat = str(data.gameHit) + "/" + str(data.currPlayPitch + 1)
    canvas.create_text(3.5*data.width//4, data.height//6, text=currStat, font="Arial 14")
    canvas.create_rectangle(3*data.width//4, data.height//5, data.width, data.height//5 + data.backHeight, fill=data.LGRAY)
    canvas.create_text(3.5*data.width//4, data.height//5 + data.backHeight//2, text="Go to stats", font="Arial 14")
    # ready message
    canvas.create_text(data.width//2, data.height//2, text=data.readyText, fill=data.WHITE, font="Arial 70")
    
def gameStartTimerFired(data):
    data.gameTimer += 1
    if data.gameTimer % 40 == 0:
        data.readyText = ""
        data.mode = "gameMode"
        b = threading.Thread(target=playGame, args=(data,))
        b.start()
    elif data.gameTimer % 30 == 0:
        data.readyText = "1"
    elif data.gameTimer % 20 == 0:
        data.readyText = "2"
    elif data.gameTimer % 10 == 0:
        data.readyText = "3"
    
##### STAT MODE #####
def statRedrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.BLUE)
    # back button
    canvas.create_rectangle(0, 0, data.backWidth, data.backHeight, fill=data.RED)
    canvas.create_text(data.backWidth//2, data.backHeight//2, text="Back", font="Arial 16", fill=data.WHITE)
    # stats
    currStat = int(data.finalHit*100/(data.finalCurrPitch+1))
    outStats = getGrade(currStat, data)
    statText = "You hit " + str(currStat) + "% of notes!"
    # percentage
    canvas.create_text(0.9*data.width//2, data.height//10, text=statText, font="Arial 40", fill=data.WHITE)
    # grade
    canvas.create_oval(7*data.width//8 - data.gradeSize, data.height//10 - data.gradeSize, 7*data.width//8 + data.gradeSize, data.height//10 + data.gradeSize, fill=outStats[2])
    canvas.create_text(7*data.width//8, data.height//10, text=outStats[0], font="Arial 30", fill=data.WHITE)
    canvas.create_text(data.width//2, 8*data.height//9, text=outStats[1], font="Arial 25", fill=data.WHITE)
    # performance graph
    canvas.create_rectangle(data.graphxMargin - data.width//20, data.graphyMargin - data.height//20, data.width - data.graphxMargin + data.width//20, data.height - data.graphyMargin + data.height//20, fill=data.WHITE)
    # grid
    gridx = (data.width - 2*data.graphxMargin)/(len(data.finalLog) - 1)
    gridy = (data.height - 2*data.graphyMargin)/10
    for i in range(len(data.finalLog) - 1):
        for j in range(10):
            canvas.create_rectangle(i*gridx + data.graphxMargin, j*gridy + data.graphyMargin, (i+1)*gridx + data.graphxMargin, (j+1)*gridy + data.graphyMargin)
    canvas.create_text(data.width//2, data.graphyMargin - data.height//20, text="Performance", font="Arial 20", anchor=N)
    # graph statistics
    dx = (data.width - 2*data.graphxMargin)/(len(data.finalLog) - 1)
    dy = (data.height - 2*data.graphyMargin)/100
    for i in range(len(data.finalLog) - 1):
        # line
        thisPoint = data.finalLog[i] if data.finalLog[i] <= 100 else 100
        nextPoint = data.finalLog[i+1] if data.finalLog[i+1] <= 100 else 100
        canvas.create_line(dx*i + data.graphxMargin, (100 - thisPoint)*dy + data.graphyMargin, dx*(i+1) + data.graphxMargin, (100 - nextPoint)*dy + data.graphyMargin, fill=data.RED, width=data.width//200)
        # points
        canvas.create_oval(dx*i + data.graphxMargin - data.pointSize, (100 - data.finalLog[i])*dy + data.graphyMargin - data.pointSize, dx*i + data.graphxMargin + data.pointSize, (100 - data.finalLog[i])*dy + data.graphyMargin + data.pointSize, fill=data.BLUE, width=data.width//200)
        canvas.create_oval(dx*(i+1) + data.graphxMargin - data.pointSize, (100 - data.finalLog[i+1])*dy + data.graphyMargin - data.pointSize, dx*(i+1) + data.graphxMargin + data.pointSize, (100 - data.finalLog[i+1])*dy + data.graphyMargin + data.pointSize, fill=data.BLUE, width=data.width//200)
    
def statMousePressed(event, data):
    if 0 <= event.x <= data.backWidth and 0 <= event.y <= data.backHeight:
        # back button was pressed
        data.mode = "startPage"
        init(data)
    
def statTimerFired(data):
    pass
    
##### RUN FUNCTION #####
def run(width=300, height=300):
    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
        
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()
        
    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data, canvas)
        redrawAllWrapper(canvas, data)
    
    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)


    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    init(data)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.title("Violin Hero")
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(650, 650)
##### END MY CODE