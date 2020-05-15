from IPython.display import display, Javascript
from google.colab.output import eval_js
from base64 import b64decode
import numpy as np
import cv2

class WebCamera:
  def __init__(self, quality=0.8, size=None):
    self.quality = quality
    self.build_website(size)

  def __iter__(self):
    return self

  def __next__(self):
    return self.next()

  def next(self):
    data = eval_js('getImage({})'.format(self.quality))
    return cv2.imdecode(
      np.frombuffer(
        b64decode(data.split(',')[1]),
        dtype=np.uint8
      ), -1)

  @staticmethod
  def build_website(size):
    js = Javascript('''
      that = this;
      async function initWebsite(size) {
        const video = document.createElement('video');
        video.style.display = 'block';
        const stream = await navigator.mediaDevices.getUserMedia({video: true});

        document.body.appendChild(video);
        video.srcObject = stream;
        that.video = video;
        await video.play();

        google.colab.output.setIframeHeight(
          2*document.documentElement.scrollHeight, true);

        const canvas = document.createElement('canvas');
        if(!!size) {
            canvas.width = size;
            canvas.height = size;
        } else {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        }
        that.canvas = canvas;
      }

      async function getImage(quality)
      {
        that.canvas.getContext('2d').drawImage(that.video, 0, 0);
        return that.canvas.toDataURL('image/jpeg', quality);
      }
      ''')
    display(js)
    if size is None:
        eval_js('initWebsite(undefined)')
    else:
        eval_js('initWebsite({})'.format(size))

