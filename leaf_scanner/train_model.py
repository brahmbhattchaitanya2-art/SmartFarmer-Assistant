import os
import argparse
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def train_mobilenet_model(dataset_path, model_save_path, classes_save_path, epochs=5, batch_size=32):
    print(f"Loading dataset from: {dataset_path}")
    
    # Load training and validation datasets with 224x224 size
    train_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size
    )
    
    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"Detected {num_classes} classes: {class_names}")
    
    # Save only the class names to class_names.json
    with open(classes_save_path, 'w') as f:
        json.dump(class_names, f)
    print(f"Saved class names to {classes_save_path}")
    
    # Autotune performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    # Build transfer learning model using MobileNetV2
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False # Freeze base convolutional weights
    
    model = keras.Sequential([
        # MobileNetV2 expects input pixel values scaled to [-1, 1]
        layers.Rescaling(1./127.5, offset=-1, input_shape=(224, 224, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    model.summary()
    
    print(f"Starting training for {epochs} epochs...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )
    
    print(f"Saving trained model to {model_save_path}")
    model.save(model_save_path)
    print("MobileNetV2 model training and saving completed successfully!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train a MobileNetV2 classifier on leaf images")
    parser.add_argument('--dataset', type=str, default=r'C:\TesT_Example\Leaf_Disease_Dataset', help='Path to dataset')
    parser.add_argument('--epochs', type=int, default=5, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    args = parser.parse_args()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'leaf_disease_model.h5')
    classes_path = os.path.join(current_dir, 'class_names.json')
    
    train_mobilenet_model(args.dataset, model_path, classes_path, epochs=args.epochs, batch_size=args.batch_size)
