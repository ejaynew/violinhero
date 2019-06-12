##### START MY CODE
class GoalNote(object):
    def __init__(self, dur, pitch, data):
        self.dur = dur
        self.speed = 7
        self.length = dur * self.speed * 8.7
        self.pitch = pitch
        self.string = None
        self.data = data
        self.y = 7.5*self.data.height//10 - self.length
        self.pitchValue = 0
        for durat in data.durs[:data.currPitch]:
            self.pitchValue += 1
            self.y -= durat * self.speed * 8.7
        self.finger = data.finger_defs.get(self.pitch, -1) # default to offscreen
        self.flat = False
        self.sharp = False
        if self.finger == -1 and not self.pitch == 0:
            if data.flat:
                # key signature is flats
                self.finger = data.finger_defs.get(self.pitch+1, -1)
                self.flat = True
            else:
                # key signature is sharps
                self.finger = data.finger_defs.get(self.pitch-1, -1)
                self.sharp = True
        self.beats = int(self.dur // data.beat)
        self.meters = []
        if self.beats >= 1:
            for i in range(self.beats):
                self.meters.append(self.y + i*(self.length/self.beats))
        # for eighth notes, create a metronome line for every other note
        elif data.nextMeter:
            self.meters.append(self.y)
            data.nextMeter = False
        elif self.dur // data.beat <= 0.6:
            data.nextMeter = not data.nextMeter
            
    def getColor(self):
        if self.pitch <= 50:
            # G -- below 50
            return self.data.DBLUE
        elif 50 < self.pitch <= 57:
            # D -- 50 and up
            return self.data.GREEN
        elif 57 < self.pitch <= 64:
            # A -- 69 and up
            return self.data.DRED
        else:
            # E -- 76 and up
            return self.data.YELLOW
    def draw(self, canvas, data):
        if not self.length <= 0:
            # draw metronome lines
            for meter in self.meters:
                canvas.create_line(0, meter, data.width, meter, fill=data.YELLOW)
            # draw notes
            canvas.create_rectangle(data.widthMargin + data.stringWidth*self.finger,  self.y, data.stringWidth*(self.finger+1) - data.widthMargin, self.y + self.length, fill=self.getColor(), width=data.width//200, outline=data.BLACK)
            if self.flat:
                canvas.create_text(data.stringWidth*(self.finger+0.5), self.y + self.length/2, text="b", fill=data.BLACK, font="Arial 30")
            elif self.sharp:
                canvas.create_text(data.stringWidth*(self.finger+0.5), self.y + self.length/2, text="#", fill=data.BLACK, font="Arial 30")
    def move(self, data):
        self.y += self.speed
        if self.y + self.length >= 7.7*self.data.height//10:
            data.currPlayPitch = self.pitchValue
            self.length -= self.speed
        for i in range(len(self.meters)):
            self.meters[i] = self.meters[i] + self.speed
        
##### END MY CODE