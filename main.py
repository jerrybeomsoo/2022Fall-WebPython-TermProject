# import libraries for resampling, fft spectrogram view and etc.
import random
import urllib.request
import copy
import matplotlib.pyplot as pyplot
import scipy.interpolate as interpolate

# Define class: WAV file header translation
class header:
    inputHeader = bytes()

    # Define the default values which should be replaced by 'extractData' method.
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
        self.byte_byteRate = (self.byteRate).to_bytes(4, "little")
        self.byte_blockAlign = (self.blockAlign).to_bytes(2, "little")
        self.byte_bitsPerSample = (self.bitsPerSample).to_bytes(2, "little")
        self.byte_chunkSize_40to43 = (self.chunkSize_40to43).to_bytes(4, "little")

        newHeaderString = "RIFF" + str(self.byte_chunkSize_4to7)[2:-1] + "WAVEfmt " + str(self.byte_chunkSize_16to19)[2:-1] + "\\x01\\x00" + str(self.byte_numberOfChannels)[2:-1] + str(self.byte_sampleRate)[2:-1] + str(self.byte_byteRate)[2:-1] + str(self.byte_blockAlign)[2:-1] + str(self.byte_bitsPerSample)[2:-1] + "data" + str(self.byte_chunkSize_40to43)[2:-1] 
        self.inputHeader = bytes(newHeaderString, "ascii")
        self.inputHeader = self.inputHeader.decode('unicode_escape').encode('raw_unicode_escape')

# Define function: Create new list with integer from list with raw byte data
def rawHexDatatoInt(rawData, intData):
    for counter in range(len(rawData)):
        integerData = int.from_bytes(rawData[counter], "little", signed=True)
        intData.append(integerData)

# Define function: Create new list with raw byte data from list with signed (with +/- signs) little endian 16 bit integers
# All audio samples used in this project are in 2 bytes
def intDatatoHex(intData, rawData):
    for samples in intData:
        if samples < 0:
            byteData = (samples + 2**16).to_bytes(2, "little")
        else:
            byteData = samples.to_bytes(2, "little")
        rawData.append(byteData)

# Fetch random audio file from server: https://dagshub.com/hazalkl/MS-SNSD/src/master/Data/clean_test (MS-SNSD by Microsoft Corporation, MIT License)
# All of the audio files are in Signed PCM 16bit / 16000kHz
randomSample = random.randint(0,1000)
sampleUrl = "https://github.com/microsoft/MS-SNSD/raw/master/clean_test/clnsp{0}.wav".format(randomSample)
urllib.request.urlretrieve(sampleUrl, "dl_wav_file.wav")

# Extract header, raw data from WAV file
# Read the wav file from offset 44, which is the start point of raw PCM data
# 2 bytes = 1 sample (btw, all of the samples are in mono channel) / little endian
original_file_data_raw = []

with open("dl_wav_file.wav", "rb") as original_file_binary:
    byteStep = 2
    original_file_header = header()
    original_file_header.inputHeader = original_file_binary.read(44)
    original_file_header.extractData()

    for i in range(0, int(original_file_header.chunkSize_40to43 / 2)):
        # 44 byte is the starting point of the raw PCM data, but we have already read the file to that point when reading the header of the file.
        original_file_data_raw.append(original_file_binary.read(byteStep))

# Raw data conversion to SIGNED integer
original_file_data_signed_int = []
rawHexDatatoInt(original_file_data_raw, original_file_data_signed_int)

# Resample (Sample truncation) the retreived wav file to 8000Hz (half the samplerate of the original file)
truncated_file_data_raw = []
truncated_file_data_signed_int = []

truncated_file_header = copy.copy(original_file_header)
for samples in range(len(original_file_data_raw)):
    if samples % 2 == 0:
        truncated_file_data_raw.append(original_file_data_raw[samples])
        truncated_file_data_signed_int.append(original_file_data_signed_int[samples])
    else:
        continue
truncated_file_header.chunkSize_4to7 = 44 + (len(truncated_file_data_raw) * 2) - 8
truncated_file_header.chunkSize_40to43 = len(truncated_file_data_raw) * 2
truncated_file_header.sampleRate = 8000
truncated_file_header.byteRate = 2 * truncated_file_header.sampleRate * 1
truncated_file_header.generateData()

# Create new file: resampled data
with open('truncated_wav_file.wav', 'wb') as truncated_wav_file:
    truncated_wav_file.write(truncated_file_header.inputHeader)
    for samples in truncated_file_data_raw:
        truncated_wav_file.write(samples)

# Create new file: One sample deleted original data if original file has even sample number
if len(original_file_data_raw) % 2 == 0:
    with open('mod_original_wav_file.wav', 'wb') as mod_original_wav_file:
        mod_original_wav_file_header = copy.copy(original_file_header)
        mod_original_wav_file_header.chunkSize_4to7 -= 2
        mod_original_wav_file_header.chunkSize_40to43 -= 2
        mod_original_wav_file_header.generateData()
        mod_original_wav_file.write(mod_original_wav_file_header.inputHeader)
        for samples in range(len(original_file_data_raw) - 1):
            mod_original_wav_file.write(original_file_data_raw[samples])
else:
    with open('mod_original_wav_file.wav', 'wb') as mod_original_wav_file:
        mod_original_wav_file_header = copy.copy(original_file_header)
        mod_original_wav_file_header.generateData()
        mod_original_wav_file.write(mod_original_wav_file_header.inputHeader)
        for samples in range(len(original_file_data_raw)):
            mod_original_wav_file.write(original_file_data_raw[samples])
### End of Pre-Processing Section

### Start of Interpolation Section
# We have the data of the resampled (downsampled) audio as truncated_wav_*
# First method of interpolation: linear interpolation
linear_interpolated_data_signed_int = []
linear_interpolated_data_raw = []

for samples in range(len(truncated_file_data_signed_int) - 1):
    median_data = round((truncated_file_data_signed_int[samples] + truncated_file_data_signed_int[samples + 1]) / 2)
    linear_interpolated_data_signed_int.append(truncated_file_data_signed_int[samples])
    linear_interpolated_data_signed_int.append(median_data)

linear_interpolated_data_signed_int.append(truncated_file_data_signed_int[-1]) # The last one should not be interpolated
intDatatoHex(linear_interpolated_data_signed_int, linear_interpolated_data_raw)

# Save the linear interpolated data into "linear_interpolated_wav_file.wav"
# Reuse the header of mod_original_wav_file_header as it has same sample length and audio characteristics
with open('linear_interpolated_wav_file.wav', 'wb') as linear_interpolated_wav_file:
    linear_interpolated_wav_file.write(mod_original_wav_file_header.inputHeader)
    for samples in linear_interpolated_data_raw:
        linear_interpolated_wav_file.write(samples)

# Second method of interpolation: Random-value-between-samples
# Select the random integers between the samples and put them between the original samples
random_interpolated_data_signed_int = []
random_interpolated_data_raw = []

for samples in range(len(truncated_file_data_signed_int) - 1):
    if truncated_file_data_signed_int[samples] > truncated_file_data_signed_int[samples + 1]:
        randomSample = random.randint(truncated_file_data_signed_int[samples + 1], truncated_file_data_signed_int[samples])
    elif truncated_file_data_signed_int[samples] < truncated_file_data_signed_int[samples + 1]:
        randomSample = random.randint(truncated_file_data_signed_int[samples], truncated_file_data_signed_int[samples + 1])
    else: # ==
        randomSample = truncated_file_data_signed_int[samples]
    
    random_interpolated_data_signed_int.append(truncated_file_data_signed_int[samples])
    random_interpolated_data_signed_int.append(randomSample)

random_interpolated_data_signed_int.append(truncated_file_data_signed_int[-1])
intDatatoHex(random_interpolated_data_signed_int, random_interpolated_data_raw)

with open('random_interpolated_wav_file.wav', 'wb') as random_interpolated_wav_file:
    random_interpolated_wav_file.write(mod_original_wav_file_header.inputHeader)
    for samples in random_interpolated_data_raw:
        random_interpolated_wav_file.write(samples)

# Third method of interpolation: Random-value-between-samples v2
# Random upsampling, but with a bit of linear sampling characteristics, by using limiting the range of random samples to Q2-Q4 range.
quarter_random_interpolated_data_signed_int = []
quarter_random_interpolated_data_raw = []

def quarterCalc(first, fourth):
    q1 = first
    q4 = fourth
    median = (first + fourth) / 2
    q2 = (q1 + median) / 2
    q3 = (q4 + median) / 2

    secondFourthList = []
    secondFourthList.append(q2)
    secondFourthList.append(q3)
    return secondFourthList
        
for samples in range(len(truncated_file_data_signed_int) - 1):
    if truncated_file_data_signed_int[samples] > truncated_file_data_signed_int[samples + 1]:
        quarters = quarterCalc(truncated_file_data_signed_int[samples + 1], truncated_file_data_signed_int[samples])
        randomSample = random.randint(round(quarters[0]), round(quarters[1]))
    elif truncated_file_data_signed_int[samples] < truncated_file_data_signed_int[samples + 1]:
        quarters = quarterCalc(truncated_file_data_signed_int[samples], truncated_file_data_signed_int[samples + 1])
        randomSample = random.randint(round(quarters[0]), round(quarters[1]))
    else: # ==
        randomSample = truncated_file_data_signed_int[samples]
    
    quarter_random_interpolated_data_signed_int.append(truncated_file_data_signed_int[samples])
    quarter_random_interpolated_data_signed_int.append(randomSample)

quarter_random_interpolated_data_signed_int.append(truncated_file_data_signed_int[-1])
intDatatoHex(quarter_random_interpolated_data_signed_int, quarter_random_interpolated_data_raw)

with open('quarter_random_interpolated_wav_file.wav', 'wb') as quarter_random_interpolated_wav_file:
    quarter_random_interpolated_wav_file.write(mod_original_wav_file_header.inputHeader)
    for samples in quarter_random_interpolated_data_raw:
        quarter_random_interpolated_wav_file.write(samples)

# Fourth method : Spline interpolation (with scipy)
spline_interpolated_data_raw = []
spline_interpolated_data_signed_int = []
sampleNumber = range(len(truncated_file_data_signed_int))
sampleData = truncated_file_data_signed_int
splineSample = interpolate.splrep(sampleNumber, sampleData)

def spline(inputNumber):
    return interpolate.splev(inputNumber, splineSample)

for samples in range(len(truncated_file_data_signed_int) - 1):
    spline_data = round(float(spline(samples + 0.5)))
    spline_interpolated_data_signed_int.append(truncated_file_data_signed_int[samples])
    spline_interpolated_data_signed_int.append(spline_data)

spline_interpolated_data_signed_int.append(truncated_file_data_signed_int[-1])
intDatatoHex(spline_interpolated_data_signed_int, spline_interpolated_data_raw)

with open('spline_interpolated_wav_file.wav', 'wb') as spline_interpolated_wav_file:
    spline_interpolated_wav_file.write(mod_original_wav_file_header.inputHeader)
    for samples in spline_interpolated_data_raw:
        spline_interpolated_wav_file.write(samples)

# Fifth method: Random-value-between-samples v3
# Random upsampling, but with a bit of linear sampling characteristics, by referring to p/n mean values of linear interpolated data
positive_diff = 0
positive_diff_count = 0
positive_diff_list = []
negative_diff = 0
negative_diff_count = 0
negative_diff_list = []
randv3_interpolated_data_signed_int = []
randv3_interpolated_data_raw = []

for samples in range(len(original_file_data_signed_int) - 1):
    if samples % 2 != 0:
        difference = linear_interpolated_data_signed_int[samples] - original_file_data_signed_int[samples]
        if difference > 0: # Random > Original
            positive_diff += difference
            positive_diff_list.append(difference)
            positive_diff_count += 1
        elif difference < 0: # Original > Random
            negative_diff += difference
            negative_diff_list.append(difference)
            negative_diff_count += 1
    else:
        continue
positive_diff_mean = abs(positive_diff / positive_diff_count)
negative_diff_mean = abs(negative_diff / negative_diff_count)

for samples in range(len(truncated_file_data_signed_int) - 1):
    randv3_interpolated_data_signed_int.append(truncated_file_data_signed_int[samples])
    linearValue = (truncated_file_data_signed_int[samples] + truncated_file_data_signed_int[samples + 1]) / 2
    lowerLimit = round(linearValue - positive_diff_mean)
    upperLimit = round(linearValue + negative_diff_mean)
    randomSample = random.randint(lowerLimit, upperLimit)
    randv3_interpolated_data_signed_int.append(randomSample)

randv3_interpolated_data_signed_int.append(truncated_file_data_signed_int[-1])
intDatatoHex(random_interpolated_data_signed_int, randv3_interpolated_data_raw)

with open('randv3_interpolated_wav_file.wav', 'wb') as randv3_interpolated_wav_file:
    randv3_interpolated_wav_file.write(mod_original_wav_file_header.inputHeader)
    for samples in randv3_interpolated_data_raw:
        randv3_interpolated_wav_file.write(samples)
### End of Interpolation Section

### Start of Post-Processing Section using FFT Spectrogram
class spectrogram:
    def __init__(self, name, sampleDataforClass, sampleRate):
        self.name = name
        self.sampleDataforClass = sampleDataforClass
        self.sampleRate = sampleRate
        pyplot.title(self.name)
        pyplot.specgram(self.sampleDataforClass,Fs=self.sampleRate)

pyplot.subplot(3,2,1)
originalSpec = spectrogram('Original WAVE File', original_file_data_signed_int, original_file_header.sampleRate)
pyplot.subplot(3,2,2)
randomSpec = spectrogram('Random Interpolated WAVE File', random_interpolated_data_signed_int, original_file_header.sampleRate)
pyplot.subplot(3,2,3)
linearSpec = spectrogram('Linear Interpolated WAVE File', linear_interpolated_data_signed_int, original_file_header.sampleRate)
pyplot.subplot(3,2,4)
limitedRandomSpec = spectrogram('Random Interpolated (Limited to Near-median values) WAVE File', quarter_random_interpolated_data_signed_int, original_file_header.sampleRate)
pyplot.subplot(3,2,5)
splineSpec = spectrogram('Spline Interpolated WAVE File', spline_interpolated_data_signed_int, original_file_header.sampleRate)
pyplot.subplot(3,2,6)
randv3Spec = spectrogram('Random Interpolated (Limited to mean values of linear-original difference) WAVE File', randv3_interpolated_data_signed_int, original_file_header.sampleRate)
pyplot.show()
### End of Post-Processing Section