import Tkinter as tk

class Excellon(file):

    def __init__(self, file):
        self.header = []
        self.drills = {}
        row_index = 0
        while row_index < len(file):
            if file[row_index].startswith('M48'):
                row_index += 1
                while not file[row_index].startswith('%'):
                    self.header.append(file[row_index].replace('\n', ''))
                    row_index += 1

            if file[row_index].startswith('T'):
                toolNumber = file[row_index].replace('\n', '').replace('\r', '')
                self.drills[toolNumber] = []
                row_index += 1
                while row_index < len(file) and not file[row_index].startswith('T') and not file[row_index].startswith('M30'):
                    self.drills[toolNumber].append(file[row_index].replace('\n', '').replace('\r', ''))
                    row_index += 1

            else:
                row_index += 1


class GcodeISO:

    def __init__(self, excellonFile, parameters):
        self.units, self.zSafe, self.zDepth, self.inCutFeed = parameters
        self.header = ['G17 G40 G54 G64  G90 ']
        if self.units.get() == 'mm':
            self.header.append('G21\n')
        elif self.units.get() == 'inch':
            self.header.append('G20\n')
        else:
            self.header.append('\n')
        self.body = []
        for tool in excellonFile.drills:
            self.body.append(tool + ' M6\n')
            self.body.append('G0 Z' + str(self.zSafe) + '\n')
            for hole in excellonFile.drills[tool]:
                self.body.append('G98 G81 ' + hole.replace('Y', ' Y') + ' Z-' + str(self.zDepth) + ' R' + str(self.zSafe) + ' F' + str(self.inCutFeed) + '\n')

            self.body.append('G80\n')

        self.body.append('M30\n')

    def toText(self):
        return self.header + self.body


def excellonToGcode(file, parameters):
    with open(file, 'r') as f:
        file = f.readlines()
        excellonFile = Excellon(file)
        gcodeFile = GcodeISO(excellonFile, parameters)
        return gcodeFile.toText()
