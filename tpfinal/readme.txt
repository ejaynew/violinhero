Violin Hero is an application built by Emma Wenger for the 15-112 term project assignment. It is focused on helping violinists sight read by providing them feedback on their tune.

In "game mode", the app utilizes computer vision to turn an image of sheet music into guitar hero style notes, which the violinist can then play and receive feedback on how many notes he or she hit.

In "tune mode", the app will simply display the sheet music onscreen and provide feedback on the performance.

The file "songs.txt" contains a few pre-loaded music samples, accessed by pressing "Select from library", which can be used for quick demos.

Run the program from "basicGUI2.py".

If you press "r", the program will reset so that you don't have to close it between demos.

The libraries you will need to pip in are as follows:
	opencv_python, matplotlib, numpy, aubio, tkthread