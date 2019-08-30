# pylint: disable=E0401
# pylint: disable=C0412
import os
import numpy as np
import pandas as pd
import easygui
from natsort import natsorted
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# This code is for cleaning up the naming system for the QC files. It takes in
# the file names and automatically adjusts the names to include the depth limits.
# This way, the user will rarely have to manually rename the files. The next
# step is to automatically create the desired folder structure to save time.

def list_files(directory, extension1, extension2):
    return (f for f in os.listdir(directory) if f.endswith('.' + extension1) or
            f.endswith('.' + extension1.lower()) or
            f.endswith('.' + extension2) or
            f.endswith('.' + extension2.lower()))

def substring(whole, sub1, sub2):
    return whole[whole.index(sub1) : whole.index(sub2)]


DIRECTORY = easygui.diropenbox()                          
FILESLIST = list_files(DIRECTORY, 'JPG', 'PNG')
FILESLIST = natsorted(FILESLIST)
NUM_FILES = len(FILESLIST)

# identifies the name of the folder we are in
folderName = os.path.basename(DIRECTORY + str("\new")[:1] + FILESLIST[0])

fileDiction = {}

for i in range(0, NUM_FILES):
    FILESLIST[i] = FILESLIST[i].replace(' Box', ' Box ')
    FILESLIST[i] = FILESLIST[i].replace(' Box  ', ' Box ')
    FILESLIST[i] = FILESLIST[i].replace(',', '.')
    #taking care of cases that m is at the end of the photo name
    FILESLIST[i] = FILESLIST[i].replace('m)', ')')
    FILESLIST[i] = FILESLIST[i].replace('M)', ')')
    FILESLIST[i] = FILESLIST[i].replace('M)', ')')
    FILESLIST[i] = FILESLIST[i].replace('DRILL_ ','DRILL_')

    # identifies the numbering system to use as the key in the hash
    try:
        index1 = FILESLIST[i].index(" Box ") + len(" Box ")
    except:
        print("RIP 1",FILESLIST[i])
    try:
        index2 = FILESLIST[i][index1:].index(" ")
    except:
        print("RIP 2",FILESLIST[i])
        
    newString = FILESLIST[i][index1: index1+index2]

    # adds the element into the array if the key exists, otherwise initializes 
    elem = fileDiction.get(newString)
    if elem is None:
        fileDiction[newString] = [i]
    else:
        fileDiction[newString].append(i)

# creates a copy of file names for renaming later
OLDFILESLIST = FILESLIST

# rename all the files that are repated to include the bracketed terms
for key in fileDiction:
    if len(fileDiction[key]) >= 2:
        bracketString = ""
        # determine the string that is inside the brackets
        for i in range(len(fileDiction[key])):
            num = fileDiction[key][i]
            string = FILESLIST[num]
            indexBeg = string.find("(")
            indexEnd = string.find(")")
            if indexBeg != -1 and indexEnd != -1:
                indices = [indexBeg, indexEnd]
                bracketString = string[indexBeg+1:indexEnd]

        # insert the string found inside the brackets to the strings that have no brackets
        for i in range(len(fileDiction[key])):
            num = fileDiction[key][i]
            string = FILESLIST[num]
            indexBeg = string.find("(")
            indexEnd = string.find(")")
            if indexBeg == -1 and indexEnd == -1:
                FILESLIST[num] = string[:indices[0]] + "(" + bracketString + ") " + string[indices[0]:]


FILESLIST = natsorted(FILESLIST)
        
COLUMN_NAMES = ['BHID', 'BOX #', 'FROM', 'TO']
DATAFRAME = pd.DataFrame(columns=COLUMN_NAMES)
for i in range(0, NUM_FILES):
    print(FILESLIST[i])
    #Taking care of the cases there is no space after to
    FILESLIST[i] = FILESLIST[i].replace(' to', ' to ')

    n = int(np.floor(len((substring(FILESLIST[i], 'Box', '(')).split()[1]) - 1) / 2)
    #taking care of the cases we have just one box# in the name
    if n== 0 or n== 1:
        n = (len((substring(FILESLIST[i], 'Box', '(')).split()[1]))

    DATAFRAME = DATAFRAME.append({'BHID': FILESLIST[i].split()[0],
                                  'BOX #': (substring(FILESLIST[i], 'Box', '(')).split()[1][0:n],
                                  'FROM': (FILESLIST[i].split('(', 1)[1].split(')')[0]).split()[0], #find the first value in ()
                                  'TO': (FILESLIST[i].split('(', 1)[1].split(')')[0]).split()[2]}, #find the last value in ()
                                 ignore_index=True)


print(DATAFRAME)
NAME = DATAFRAME['BHID'][0]
DATAFRAME.to_csv(NAME + '.csv', index=False)

basePath = r"Desktop" + str(r"\New")[:1]
mainPath = basePath+folderName
#print(basePath, folderName, mainPath)

#sort dataframe
DATAFRAME['FROM'] = [float(x) for x in DATAFRAME['FROM']]
DATAFRAME['TO'] = [float(x) for x in DATAFRAME['TO']]

print('------------------------')
peaks_from, _ = find_peaks(DATAFRAME['FROM'],prominence=1)
print(DATAFRAME['BOX #'][peaks_from])
print('------------------------')
peaks_to, _ = find_peaks(DATAFRAME['TO'],prominence=1)
print(DATAFRAME['BOX #'][peaks_to])
print('------------------------')
ax1 = plt.subplot(131)
plt.plot(DATAFRAME['BOX #'], DATAFRAME['FROM'])
plt.plot(peaks_from, DATAFRAME['FROM'][peaks_from], "xr")
plt.title('From')
start, end = ax1.get_xlim()
plt.xticks(np.arange(0, end, 5),rotation=90)
ax1 = plt.subplot(132)
plt.plot(DATAFRAME['BOX #'], DATAFRAME['TO'])
plt.plot(peaks_to, DATAFRAME['TO'][peaks_to], "xr")
plt.title('To')
plt.xticks(np.arange(0, end, 5),rotation=90)
ax1 = plt.subplot(133)
plt.plot(DATAFRAME['BOX #'],'*')
plt.yticks(np.arange(0, end, 5))
plt.title('Box Number')
plt.show()
