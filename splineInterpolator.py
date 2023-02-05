import scipy.interpolate as interpolate
import copy

class header:
    inputHeader = bytes()

    chunkSize_4to7 = 0
    chunkSize_16to19 = 16
    numberOfChannels = 1
    sampleRate = 0
    byteRate = 0
    blockAlign = 0
    bitsPerSample = 16
    chunkSize_40to43 = 0

    byte_chunkSize_4to7 = None
    byte_chunkSize_16to19 = None
    byte_numberOfChannels = None
    byte_sampleRate = None
    byte_byteRate = None
    byte_blockAlign = None
    byte_bitsPerSample = None
    byte_chunkSize_40to43 = None

    def extractData(self):
        self.chunkSize_4to7 = int.from_bytes(self.inputHeader[4:8], "little", signed=True)
        self.chunkSize_16to19 = int.from_bytes(self.inputHeader[16:20], "little", signed=True)
        self.numberOfChannels = int.from_bytes(self.inputHeader[22:24], "little", signed=True)
        self.sampleRate = int.from_bytes(self.inputHeader[24:28], "little", signed=True)
        self.byteRate = int.from_bytes(self.inputHeader[28:32], "little", signed=True)
        self.blockAlign = int.from_bytes(self.inputHeader[32:34], "little", signed=True)
        self.bitsPerSample = int.from_bytes(self.inputHeader[34:36], "little", signed=True)
        self.chunkSize_40to43 = int.from_bytes(self.inputHeader[40:44], "little", signed=True)

    def generateData(self):
        self.byte_chunkSize_4to7 = (self.chunkSize_4to7).to_bytes(4, "little")
        self.byte_chunkSize_16to19 = (self.chunkSize_16to19).to_bytes(4, "little")
        self.byte_numberOfChannels = (self.numberOfChannels).to_bytes(2, "little")
        self.byte_sampleRate = (self.sampleRate).to_bytes(4, "little")
        self.byte_byteRate = (int(self.byteRate)).to_bytes(4, "little")
        self.byte_blockAlign = (self.blockAlign).to_bytes(2, "little")
        self.byte_bitsPerSample = (self.bitsPerSample).to_bytes(2, "little")
        self.byte_chunkSize_40to43 = (self.chunkSize_40to43).to_bytes(4, "little")

        newHeaderString = "RIFF" + str(self.byte_chunkSize_4to7)[2:-1] + "WAVEfmt " + str(self.byte_chunkSize_16to19)[2:-1] + "\\x01\\x00" + str(self.byte_numberOfChannels)[2:-1] + str(self.byte_sampleRate)[2:-1] + str(self.byte_byteRate)[2:-1] + str(self.byte_blockAlign)[2:-1] + str(self.byte_bitsPerSample)[2:-1] + "data" + str(self.byte_chunkSize_40to43)[2:-1] 
        self.inputHeader = bytes(newHeaderString, "ascii")
        self.inputHeader = self.inputHeader.decode('unicode_escape').encode('raw_unicode_escape')

# Create new list with integer from list with raw byte data
def rawHexDatatoInt(rawData, intData):
    for counter in range(len(rawData)):
        integerData = int.from_bytes(rawData[counter], "little", signed=True)
        intData.append(integerData)

def intDatatoHex(intData, rawData):
    for samples in intData:
        if samples < 0:
            byteData = (samples + 2**original_file_header.bitsPerSample).to_bytes(int(original_file_header.bitsPerSample/8), "little")
        else:
            byteData = samples.to_bytes(int(original_file_header.bitsPerSample/8), "little")
        rawData.append(byteData)

# Extract header, raw data from WAV file
# Read the wav file from offset 44, which is the start point of raw PCM data
inputFile = "fortest.wav"
multiplier = 0
while True:
    multiplier = int(input("Please enter the multiplcation ratio (2 or 4): "))
    if multiplier == 2 or 4:
        print("Multiplier set as {}".format(multiplier))
        break
    else:
        print("Invalid input. Please enter 2 or 4.")
        continue

original_file_data1_raw = []
original_file_data2_raw = []
original_file_data1_signed_int = []
original_file_data2_signed_int = []

new_file_data1_raw = []
new_file_data2_raw = []
new_file_data1_signed_int = []
new_file_data2_signed_int = []

with open(inputFile, "rb") as original_file_binary:
    byteStep = 2
    original_file_header = header()
    original_file_header.inputHeader = original_file_binary.read(44)
    original_file_header.extractData()

    if int(original_file_header.numberOfChannels) == 1:
        for i in range(0, int(original_file_header.chunkSize_40to43 / original_file_header.blockAlign)):
            original_file_data1_raw.append(original_file_binary.read(int(original_file_header.bitsPerSample/8)))
        rawHexDatatoInt(original_file_data1_raw, original_file_data1_signed_int)
        sampleNumber = range(len(original_file_data1_signed_int))
        splineSample1 = interpolate.splrep(sampleNumber, original_file_data1_signed_int)
    else: # ==2
        for i in range(0, int(original_file_header.chunkSize_40to43 / original_file_header.blockAlign)):
            original_file_data1_raw.append(original_file_binary.read(int(original_file_header.bitsPerSample/8)))
            original_file_data2_raw.append(original_file_binary.read(int(original_file_header.bitsPerSample/8)))
        rawHexDatatoInt(original_file_data1_raw, original_file_data1_signed_int)
        rawHexDatatoInt(original_file_data2_raw, original_file_data2_signed_int)
        sampleNumber = range(len(original_file_data1_signed_int))
        splineSample1 = interpolate.splrep(sampleNumber, original_file_data1_signed_int)
        splineSample2 = interpolate.splrep(sampleNumber, original_file_data2_signed_int)

spline_interpolated_data_raw = []
spline_interpolated_data_signed_int = []

def spline(inputNumber, selectSplineSample):
    if selectSplineSample == 1:
        return interpolate.splev(inputNumber, splineSample1)
    else: # ==2
        return interpolate.splev(inputNumber, splineSample2)

def splineInterpolate(thingtointerpolate, selectSplineSample):
    spline_interpolated_data_raw = []
    spline_interpolated_data_signed_int = []

    if multiplier == 2:
        for samples in range(0, len(thingtointerpolate) - 1):
            spline_data = round(float(spline(samples + 0.5, selectSplineSample)))
            spline_interpolated_data_signed_int.append(thingtointerpolate[samples])
            spline_interpolated_data_signed_int.append(spline_data)
            print("Processing Sample {} out of {}".format(samples, len(thingtointerpolate)-1))
    else: #==4
        for samples in range(0, len(thingtointerpolate) - 1):
            spline_interpolated_data_signed_int.append(thingtointerpolate[samples])
            spline_interpolated_data_signed_int.append(round(float(spline(samples + 0.25, selectSplineSample))))
            spline_interpolated_data_signed_int.append(round(float(spline(samples + 0.5, selectSplineSample))))
            spline_interpolated_data_signed_int.append(round(float(spline(samples + 0.75, selectSplineSample))))
            print("Processing Sample {} out of {}".format(samples, len(thingtointerpolate)-1))

    spline_interpolated_data_signed_int.append(thingtointerpolate[-1])
    intDatatoHex(spline_interpolated_data_signed_int, spline_interpolated_data_raw)
    return spline_interpolated_data_raw

if original_file_header.numberOfChannels == 1:
    finalRawData = splineInterpolate(original_file_data1_signed_int, 1)

    newHeader = copy.copy(original_file_header)
    newHeader.chunkSize_4to7 = 44 + (len(finalRawData) * int(newHeader.bitsPerSample/8)) - 8
    newHeader.chunkSize_40to43 = len(finalRawData) * int(newHeader.bitsPerSample/8)
    newHeader.sampleRate = original_file_header.sampleRate * multiplier
    newHeader.byteRate = newHeader.bitsPerSample * newHeader.sampleRate * newHeader.numberOfChannels / 8
    newHeader.generateData()

    with open('spline_interpolated_wav_file.wav', 'wb') as spline_interpolated_wav_file:
        spline_interpolated_wav_file.write(newHeader.inputHeader)
        for samples in range(len(finalRawData)):
            spline_interpolated_wav_file.write(finalRawData[samples])

else: # ==2
    finalRawData1 = splineInterpolate(original_file_data1_signed_int, 1)
    finalRawData2 = splineInterpolate(original_file_data2_signed_int, 2)

    newHeader = copy.copy(original_file_header)
    newHeader.chunkSize_4to7 = 44 + ((len(finalRawData1)) * int(newHeader.bitsPerSample/8) * 2) - 8
    newHeader.chunkSize_40to43 = ((len(finalRawData1)) * int(newHeader.bitsPerSample/8) * 2)
    newHeader.sampleRate = int(original_file_header.sampleRate * multiplier)
    newHeader.byteRate = int(newHeader.bitsPerSample * newHeader.sampleRate * newHeader.numberOfChannels / 8)
    newHeader.generateData()

    with open('spline_interpolated_wav_file.wav', 'wb') as spline_interpolated_wav_file:
        spline_interpolated_wav_file.write(newHeader.inputHeader)
        for samples in range(len(finalRawData1)):
            spline_interpolated_wav_file.write(finalRawData1[samples])
            spline_interpolated_wav_file.write(finalRawData2[samples])