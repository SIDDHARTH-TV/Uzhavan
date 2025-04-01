import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# ✅ Step 1: Define the model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(3, activation='softmax')  # Assuming 3 classes (vegetables)
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# ✅ Step 2: Load Dataset
dataset_path = "vegetable_dataset"  # Change this to your dataset folder
if not os.path.exists(dataset_path):
    print(f"Dataset folder '{dataset_path}' not found! Please provide a valid path.")
    exit()

datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_data = datagen.flow_from_directory(
    dataset_path, target_size=(224, 224), batch_size=32, class_mode="categorical", subset="training")

val_data = datagen.flow_from_directory(
    dataset_path, target_size=(224, 224), batch_size=32, class_mode="categorical", subset="validation")

# ✅ Step 3: Train the model
model.fit(train_data, validation_data=val_data, epochs=10)

# ✅ Step 4: Save the trained model
model.save("vegetable_model.h5")
print("Model saved successfully as 'vegetable_model.h5'!")
