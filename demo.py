import pyaudio
import wave
import numpy as np
import math
import mingus.extra.lilypond as LilyPond
from mingus.containers.bar import Bar
import pydub
from wand.image import Image
from flask import Flask, request, jsonify
import cloudinary
import cloudinary.uploader
import cloudinary.api
from pytube import *

cloudinary.config(
  cloud_name = "dkyd8xu73",
  api_key = "322425711941656",
  api_secret = "o-e73GxmgdmSJX73hXckygs_pus"
)

app = Flask(__name__)



@app.route('/', methods=['POST'])
def index():
    link = request.form['link']
    chunk = 2048
    b = Bar()
    ar = []
    mp3.export("file.wav", format="wav") 
    # open up a wave
    wf = wave.open('file.wav', 'rb')
    swidth = wf.getsampwidth()
    RATE = wf.getframerate()
    # use a Blackman window
    window = np.blackman(chunk)
    # open stream
    p = pyaudio.PyAudio()
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = RATE,
                    output = True)

    # read some data
    data = wf.readframes(chunk)
    from math import log, pow

    A4 = 440
    C0 = A4*pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # play stream and find the frequency of each chunk
    def pitch(freq):
        h = round(12*(log(freq/C0))/log(2))
        octave = (int) (h // 12)
        n = (int) (h % 12)
        # return name[n] + str(octave)
        return name[n]

    count = 0
    while data != '':
        # write data out to the audio stream
        count += 1
        stream.write(data)

        # unpack the data and times by the hamming window
        indata = np.array(wave.struct.unpack_from("%dh"%(len(data)/swidth), data))
        # Take the fft and square each value
        fftData=abs(np.fft.rfft(indata))**2
        # find the maximum
        which = fftData[1:].argmax() + 1
        # use quadratic interpolation around the max
        if which != len(fftData)-1:
            y0,y1,y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            thefreq = (which+x1)*RATE/chunk
        else:
            thefreq = which*RATE/chunk
        if not math.isnan(thefreq):
            print pitch(thefreq)
            b + pitch(thefreq)
        # read some more data
        data = wf.readframes(chunk)

        if count%4 == 0:
            bar = LilyPond.from_Bar(b)
            LilyPond.to_pdf(bar, "temp")
            toPng()
            data = cloudinary.uploader.upload("temp.png")['url']
            print data
            ar.append(data)
            b = Bar()

    if data:
        stream.write(data)
        
    stream.close()
    p.terminate()

    return jsonify(ar)

def toPng():
    with Image(filename="temp.pdf") as img:

        with img.convert('png') as c:
            c.crop(50,0,200,100)
            c.save(filename='temp.png')
        # all_pages = Image(blob=img)
        # single_image = all_pages.sequence[0]
        # with Image(single_image) as i:
        #     i.format = 'png'
        #     i.background_color = Color('white')
        #     i.alpha_channel = 'remove'  

if __name__ == "__main__":
    app.run(host='0.0.0.0')
