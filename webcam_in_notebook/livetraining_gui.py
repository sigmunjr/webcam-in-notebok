import random
import ipywidgets as widgets
from google.colab.patches import cv2_imshow
from IPython.display import display
from IPython.display import HTML
from IPython.display import clear_output
import cv2
import tensorflow as tf

class LiveDataset:
    def __init__(self):
        self.train_set = {}
        self.label_map = {}
        self.name_map = {}

    def add_image(self, image, label):
        train_image = self.convert_to_tf_image(image)
        self.add_label(label)
        self.train_set[label] += [train_image]

    def add_label(self, label):
        if label in self.train_set:
            return
        n_labels = len(self.label_map)
        self.train_set[label] = []
        self.label_map[label] = n_labels
        self.name_map[n_labels] = label

    def get_batch(self, batch_size=16):
        labels = []
        images = []
        for i in range(batch_size):
            labels += [np.random.choice(list(self.name_map.keys()))]
            examples = self.train_set[self.name_map[labels[-1]]]
            images += random.sample(examples, 1)
        return np.stack(images), np.stack(labels)

    @staticmethod
    def convert_to_tf_image(image):
        train_image = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), (224, 224))
        train_image = tf.cast(train_image, tf.float32)
        train_image = preprocess_input(train_image)
        return train_image

class DatasetGUI:
  def __init__(self, dataset, webcam):
    self.dataset = dataset
    self.webcam = webcam
    self.build_widgets()
    self.js_textfield = LiveJavascriptTextField()

  def build_widgets(self):
    self.select = widgets.Select(
        options=list(self.dataset.label_map.keys()),
        description='Selected:',
        disabled=False
    )
    self.button = widgets.Button(
        description='Add image',
        disabled = len(self.dataset.label_map) == 0,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Add image',
        icon='check' # (FontAwesome names without the `fa-` prefix)
    )
    self.text_field = widgets.Text(
        placeholder='Object label',
        description='New object:',
        disabled=False
    )
    self.select.observe(self.onSelect, 'value')
    self.text_field.on_submit(self.addObject)
    self.button.on_click(self.addImage)

  def addImage(self, _):
    img = self.webcam.next()
    self.dataset.add_image(img, self.select.value)
    self.js_textfield.updateText('label : count')
    for key, value in self.dataset.train_set.items():
      self.js_textfield.addText(key + ':' + str(len(value)))

  def onSelect(self, selected):
    self.button.description = 'Add image to ' + selected['new']

  def addObject(self, label):
    if label.value in self.dataset.label_map:
        return
    self.dataset.add_label(label.value)
    label.value = ''
    self.select.options = list(self.dataset.label_map.keys())
    self.button.disabled = False
    self.select.disabled = False

  def display(self):
    display(self.text_field, self.select, self.button)

from IPython.display import display, Javascript
from google.colab.output import eval_js

class LiveJavascriptTextField:
  def __init__(self, style=''):
    self.initText(style)

  def initText(self, style):
    js = Javascript('''
      that = this;
      async function initText(style)
      {
        const video = document.querySelector("#output-area");
        const div = document.createElement('div');
        div.innerHTML = '';
        that.text_area = div;
        div.style = style;
        video.appendChild(
          div
          );
      }
      async function updateText(text)
      {
        that.text_area.innerHTML = text;
      }
      async function addText(text)
      {
        that.text_area.innerHTML += '<p>' + text + '</p>';
      }
    ''')
    display(js);
    eval_js('initText("{}")'.format(style));

  def addText(self, text):
    eval_js('addText("{}")'.format(text))

  def updateText(self, text):
    eval_js('updateText("{}")'.format(text))
