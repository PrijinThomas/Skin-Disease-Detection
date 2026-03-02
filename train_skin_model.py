import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import cv2

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10  # Increased for better results
DATASET_DIR = r"c:\Users\User\Desktop\skin_diseases"
CSV_PATH = os.path.join(DATASET_DIR, "HAM10000_metadata.csv")
MODEL_SAVE_PATH = os.path.join(DATASET_DIR, "skin_cancer_model.h5")

def load_data():
    print("Loading dataset and mapping image paths...")
    df = pd.read_csv(CSV_PATH)
    
    # Map image IDs to their actual paths
    imageid_path_dict = {}
    for folder in ['HAM10000_images_part_1', 'HAM10000_images_part_2']:
        folder_path = os.path.join(DATASET_DIR, folder)
        if os.path.exists(folder_path):
            for img_name in os.listdir(folder_path):
                image_id = os.path.splitext(img_name)[0]
                imageid_path_dict[image_id] = os.path.join(folder_path, img_name)
    
    df['path'] = df['image_id'].map(imageid_path_dict)
    
    # Mapping classes (dx) to numeric values
    class_mapping = {
        'akiec': 'Actinic Keratoses',
        'bcc': 'Basal Cell Carcinoma',
        'bkl': 'Benign Keratosis-like Lesions',
        'df': 'Dermatofibroma',
        'mel': 'Melanoma',
        'nv': 'Melanocytic Nevi',
        'vasc': 'Vascular Lesions'
    }
    df['label_name'] = df['dx'].map(class_mapping)
    
    # Drop rows without image paths
    df = df.dropna(subset=['path'])
    print(f"Total valid images found: {len(df)}")
    return df

def build_transfer_model(num_classes):
    print("Building MobileNetV2 Transfer Learning model...")
    # Load pre-trained MobileNetV2 without the top layer
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    
    # Freeze the base model to preserve learned features
    base_model.trainable = False
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer='adam', 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    return model

def train():
    df = load_data()
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df['dx'])
    
    # Initialize Data Generators with Augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_dataframe(
        train_df,
        x_col='path',
        y_col='label_name',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    test_generator = test_datagen.flow_from_dataframe(
        test_df,
        x_col='path',
        y_col='label_name',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    # Calculate Class Weights to handle imbalance
    class_indices = train_generator.class_indices
    y_train = train_df['dx'].map({k: i for i, k in enumerate(sorted(df['dx'].unique()))})
    weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weights_dict = {i: weights[i] for i in range(len(weights))}

    model = build_transfer_model(num_classes=len(class_indices))
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_accuracy', save_best_only=True, mode='max', verbose=1),
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=0.00001, verbose=1)
    ]
    
    print("Starting training...")
    model.fit(
        train_generator,
        steps_per_epoch=len(train_df) // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=test_generator,
        validation_steps=len(test_df) // BATCH_SIZE,
        class_weight=class_weights_dict,
        callbacks=callbacks
    )
    
    print(f"Final model saved/updated at {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    # Check if GPU is available
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    train()
