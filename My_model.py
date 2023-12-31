pip install --upgrade tensorflow
pip install pyyaml h5py
pip install --upgrade keras

import tensorflow as tf
import cv2
import os
from PIL import Image
import numpy as np
from numpy import asarray
from sklearn.model_selection import train_test_split
from tensorflow import keras
from keras.utils import normalize
from keras.models import Sequential
from keras.layers import Conv2D,MaxPooling2D,Activation,Dropout,Flatten,Dense
from sklearn.utils import shuffle
from tensorflow.keras import models
from keras.utils import to_categorical
import matplotlib.pyplot as plt
from keras.callbacks import History

image_directory = '/content/Lungcancer Detection/CT-Scan Images' #choose the correct path for the directory
tumour_images = os.listdir('/content/Lungcancer Detection/CT-Scan Images/Cancerous raw images-jpg') #choose the correct path for the directory
no_tumour_images = os.listdir('/content/Lungcancer Detection/CT-Scan Images/Non-Cancerous raw images - jpg') #choose the correct path for the directory
dataset=[]
label=[]
INPUT_SIZE = 64
print(tumour_images)

print(no_tumour_images)

#Iterating through all the images in the cancerous raw images and non-cancerous raw images folders

for i, image_name in enumerate(tumour_images):
   if(image_name.split('.')[1]=='jpg'):
       image=cv2.imread('/content/Lungcancer Detection/CT-Scan Images/Cancerous raw images-jpg/' #choose the correct path for the directory
       +image_name)
       image=Image.fromarray(image, 'RGB')#converting the image to an array
       image=image.resize((INPUT_SIZE,INPUT_SIZE)) # Resizing the image
       dataset.append(np.array(image))#appending the dataset in numpy array format
       label.append(1) #Has lung cancer

for i, image_name in enumerate(no_tumour_images):
   if(image_name.split('.')[1]=='jpg'):
       image=cv2.imread('/content/Lungcancer Detection/CT-Scan Images/Non-Cancerous raw images - jpg/' #choose the correct path for the directory
                        +image_name)
       image=Image.fromarray(image,'RGB') #converting the image to an array
       image=image.resize((INPUT_SIZE,INPUT_SIZE)) # Resizing the image
       dataset.append(np.array(image))#appending the dataset in numpy array format
       label.append(0) #Has no lung cancer

print(dataset)
print(label)
print(len(dataset))
print(len(label))

#image is converted to array
dataset = np.array(dataset)
label = np.array(label)

#Splitting data into test and train

x_train,x_test,y_train,y_test = train_test_split(dataset,label,test_size=0.3,random_state=0)
print(x_train.shape)
print(y_train.shape)
print(x_test.shape)
print(y_test.shape)

x_train = normalize(x_train,axis=1)
x_test = normalize(x_test,axis=1)

model = Sequential()

#Adding the first layer

model.add(Conv2D(32,(3,3),input_shape=(INPUT_SIZE,INPUT_SIZE,3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))


model.add(Conv2D(32,(3,3),kernel_initializer='he_uniform'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Conv2D(64,(3,3),kernel_initializer='he_uniform'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
history = History()
model.fit(x_train,y_train,batch_size=16,verbose=1,epochs=10,validation_data=(x_test,y_test),shuffle=False,callbacks=[history])

#model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, callbacks=[history])

# Plot training & validation accuracy values
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.savefig('/content/Lungcancer Detection/static/accuracy_plot.png')  # Save plot as image
plt.show()
plt.close()  # Close the figure

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.savefig('/content/Lungcancer Detection/static/loss_plot.png')  # Save plot as image
plt.show()
plt.close()  # Close the figure

model.save('/content/Lungcancer Detection/My_model')

#TESTING THE MODEL

from keras.models import load_model

model = load_model('/content/Lungcancer Detection/My_model') #Save your model in a location 

images = cv2.imread('/content/Lungcancer Detection/Prediction/pred57.jpg') #choose the correct path 
img = Image.fromarray(images)
img = img.resize((64,64))
img = np.array(img)
input_img = np.expand_dims(img,axis=0)
results= (model.predict(input_img) > 0.5).astype("int32")

print(results)

score = model.evaluate(x_test, y_test, verbose = 0 )
print("Test Score: ", score[0])
print("Test accuracy: ", score[1])

!pip install flask
!pip install flask-ngrok

!wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
!unzip ngrok-stable-linux-amd64.zip

!mv ngrok /usr/bin/

#Add ngrok token from https://dashboard.ngrok.com/get-started/your-authtoken
!ngrok authtoken 2TD7cUCl0yxooVQjaeQTtuy0XCK_7uXy6rPUaC6bsGEhkam21

from flask import Flask, request, jsonify, render_template, Response
from flask_ngrok import run_with_ngrok
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img
import numpy as np
from io import BytesIO

   app = Flask(__name__,template_folder='/content/Lungcancer Detection/templates') #choose the correct path for templates
run_with_ngrok(app)  # Start ngrok when the app is run
model = load_model('/content/Lungcancer Detection/My_model') #Choose the path of your saved model

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file = BytesIO(file.read())
        img = load_img(file, target_size=(64, 64))
        img = np.array(img)
        img = img.reshape((1, 64, 64, 3))  # Reshape the image to match the model input shape
        prediction = model.predict(img)
        # return render_template('result.html', prediction=prediction[0][0])
        return render_template('result.html', prediction=float(prediction[0][0]))
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
