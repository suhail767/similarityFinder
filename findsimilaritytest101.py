# -*- coding: utf-8 -*-
"""fIndSimilarityTest101.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vi7LPmjv6SRX4xsR_CkNdhSZPguvrbaB
"""

import pandas as pd
import numpy as np

import requests
import json
import os

from tqdm import tqdm
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt

def get_all_products(url):
    all_products = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}")
        if response.ok:
            products = json.loads(response.content)["products"]
            if not products:
                break
            all_products.extend(products)
            page += 1
        else:
            break

    print(f"Retrieved {len(all_products)} products from {url}.")
    return all_products

# Set the base URL for the website
base_url = 'https://www.woolsboutiqueuomo.com//'
data_url = "https://www.woolsboutiqueuomo.com/collections/all/products.json"

# Enter the id of the product which you want to find similar products of
product_identifier = '8392243675465'

all_products = get_all_products(data_url)

# Save the combined dataset as a JSON file
with open("productInfo.json", "w") as f:
    json.dump(all_products, f)

# Load data from JSON file
with open('productInfo.json', 'r') as f:
    data = json.load(f)

# Create a list of dictionaries for each product with required features
products = []
for p in data:
    product_dict = {'product_id':str(p['id']),'title': p['title'], 'vendor': p['vendor'], 'product_type': p['product_type'], 'tags': p['tags'], 'handle': p['handle'], 'images': p['images']}
    products.append(product_dict)


# Print the list of product dictionaries
print(f"Loaded data for {len(products)} products")
print(products[:3])

print(data[0].keys())

import os
from multiprocessing.pool import ThreadPool
import requests
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
import logging

def extract_image_urls(products):
    image_urls = []
    for product in products:
        for image in product['images']:
            image_urls.append(image['src'])
    return image_urls




def download_image(url, product_id, image_index):
    response = requests.get(url, stream=True)
    directory = './images/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{product_id}_image_{image_index}.jpg"
    try:
        response.raise_for_status()
        with open(os.path.join(directory, filename), 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except requests.exceptions.HTTPError as e:
        logging.error(f"Failed to download image at {url} for product {product_id}: {e}")
    except Exception as e:
        logging.error(f"Failed to download image at {url} for product {product_id}: {e}")



def download_images(products, num_threads=8):
    with ThreadPool(num_threads) as pool:
        results = []
        for product in products:
            product_id = product['product_id']
            for i, image in enumerate(product['images']):
                url = image['src']
                results.append(pool.apply_async(download_image, (url, product_id, i)))
        for r in tqdm(results, total=len(results), desc="Downloading images"):
            r.wait()


# Extract image URLs from data
image_urls = extract_image_urls(products)

# Plot a histogram of the number of images per product
num_images_per_product = [len(p['images']) for p in products]
plt.hist(num_images_per_product, bins=range(max(num_images_per_product)+2))
plt.title("Distribution of Number of Images per Product")
plt.xlabel("Number of Images")
plt.ylabel("Frequency")
plt.show()

# Download images
download_images(products, num_threads=16)


# Plot a bar chart of the number of images downloaded per product
num_images_downloaded_per_product = [len(p['images']) for p in products if len(p['images']) > 0]
num_images_downloaded = sum(num_images_downloaded_per_product)
num_products_with_images = len(num_images_downloaded_per_product)
num_products_without_images = len(products) - num_products_with_images
plt.bar(['With Images', 'Without Images'], [num_products_with_images, num_products_without_images])
plt.title("Number of Products with and without Images")
plt.xlabel("Product Status")
plt.ylabel("Count")
plt.show()

print(f"Downloaded {num_images_downloaded} images for {num_products_with_images} products")

import random
from PIL import Image

# define the path to your image directory
image_dir = "./images/"

# get a list of all image files in the directory
image_files = os.listdir(image_dir)

# choose a random selection of products from the list
num_products = 5
product_indices = random.sample(range(len(products)), num_products)
selected_products = [products[i] for i in product_indices]

# loop over the selected products and display 3 images from each product
for product in selected_products:
    product_id = product['product_id']
    product_title = product['title']
    product_images = [img for img in image_files if img.startswith(product_id)]
    if len(product_images) >= 3:
        print(f"Product ID: {product_id}, Product Title: {product_title}")
        selected_images = random.sample(product_images, 3)
        for img_file in selected_images:
            img_path = os.path.join(image_dir, img_file)
            with Image.open(img_path) as img:
                # resize the image to a maximum size of 200 x 200 pixels
                img.thumbnail((200, 200))
                img.show()
    else:
        print(f"Product ID: {product_id}, Product Title: {product_title} does not have enough images.")

import cv2
import numpy as np
import os

# Define the path to the image directory
image_dir = "./images/"

# Get a list of all image files in the directory
image_files = os.listdir(image_dir)

# Set the dimensions for resizing the 0
height = 200
width = 200

# Create an empty list to store the resized images
resized_images = []

# Loop through each image file
for img_file in image_files:
    # Load the image
    img_path = os.path.join(image_dir, img_file)
    img = cv2.imread(img_path)

    # Check if the image is loaded successfully
    if img is None:
        print("Error loading image:", img_file)
    else:
        # Resize the image to the specified dimensions
        img_resized = cv2.resize(img, (height, width))
        # Add the resized image to the list
        resized_images.append(img_resized)

# Convert the list of resized images to a numpy array
resized_images = np.array(resized_images)

# Print the shape of the array to verify that all images are of the same size
print(resized_images.shape)

import numpy as np
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

# Load the pre-trained ResNet50 model
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# Define a function to extract features from an image
def extract_features(img_path):
    # Load the image and resize it to (224, 224)
    img = image.load_img(img_path, target_size=(224, 224))
    # Convert the image to a numpy array
    img_array = image.img_to_array(img)
    # Add an extra dimension to the array to represent the batch size (1)
    img_array = np.expand_dims(img_array, axis=0)
    # Preprocess the input by subtracting the mean pixel value
    img_array = preprocess_input(img_array)
    # Use the ResNet50 model to extract features
    features = model.predict(img_array)
    # Return the features as a numpy array
    return features

# Define a function to compute the cosine similarity between two feature vectors
def cosine_similarity(features1, features2):
    dot_product = np.dot(features1, features2)
    norm1 = np.linalg.norm(features1)
    norm2 = np.linalg.norm(features2)
    cosine_similarity = dot_product / (norm1 * norm2)
    return cosine_similarity

import os
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

# Set the path to your image directory
image_dir = './images/'

# Get a list of all image files in the directory
image_files = os.listdir(image_dir)

# Define a function to load and preprocess images
def load_and_preprocess_image(image_path, target_size=(224, 224)):
    # Get the product ID from the image filename
    product_id = image_path.split("/")[-1].split("_")[0]
    # Load the image using OpenCV
    img = cv2.imread(image_path)
    # Resize the image to the target size
    img = cv2.resize(img, target_size)
    # Convert the image to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Flatten the image into a 1D array
    img = img.flatten()
    # Normalize the pixel values to be between 0 and 1
    img = img.astype('float32') / 255.0
    return product_id, img

# Load and preprocess all the images
images = []
products = []
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    product_id, image = load_and_preprocess_image(image_path)
    images.append(image)
    product_dict = {'product_id': product_id, 'image': image, 'filename': image_file}
    products.append(product_dict)

# Calculate the pairwise cosine similarity between all images
similarity_matrix = cosine_similarity(images)

# Visualize the similarity matrix as a heatmap
sns.set()
fig, ax = plt.subplots(figsize=(10,10))
sns.heatmap(similarity_matrix, ax=ax, cmap="YlGnBu")
plt.show()

# Find the most similar images for each image
for i, product in enumerate(products):
    # Sort the similarity matrix row for this image in descending order
    sorted_indices = np.argsort(similarity_matrix[i])[::-1]
    # Get the top 5 similar images
    top_indices = sorted_indices[1:6] # exclude self-similarity
    # Display the product and its top 5 similar products
    fig, axs = plt.subplots(1, 6, figsize=(15, 10))
    axs[0].imshow(cv2.imread(os.path.join(image_dir, product['filename'])))
    axs[0].axis('off')
    axs[0].set_title(f"{product['product_id']}: {product['filename']}")
    for j, index in enumerate(top_indices):
        similar_product = products[index]
        axs[j+1].imshow(cv2.imread(os.path.join(image_dir, similar_product['filename'])))
        axs[j+1].axis('off')
        axs[j+1].set_title(f"{similar_product['product_id']}: {similar_product['filename']} ({similarity_matrix[i][index]:.2f})")
    plt.show()

import os
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import random

# Set the path to your image directory
image_dir = './images/'

# Get a list of all image files in the directory
image_files = os.listdir(image_dir)

# Define a function to load and preprocess images
def load_and_preprocess_image(image_path, target_size=(224, 224)):
    # Get the product ID from the image filename
    product_id = image_path.split("/")[-1].split("_")[0]
    # Load the image using OpenCV
    img = cv2.imread(image_path)
    # Resize the image to the target size
    img = cv2.resize(img, target_size)
    # Convert the image to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Flatten the image into a 1D array
    img = img.flatten()
    # Normalize the pixel values to be between 0 and 1
    img = img.astype('float32') / 255.0
    return product_id, img

# Load and preprocess all the images
images = []
products = []
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    product_id, image = load_and_preprocess_image(image_path)
    images.append(image)
    product_dict = {'product_id': product_id, 'image': image, 'filename': image_file}
    products.append(product_dict)

# Calculate the pairwise cosine similarity between all images
similarity_matrix = cosine_similarity(images)

# Select a random product and find its similar products
product_index = random.randint(0, len(products)-1)
product = products[product_index]
product_id = product['product_id']
print(f"Selected product: {product_id}")

# Sort the similarity matrix row for the selected product in descending order
sorted_indices = np.argsort(similarity_matrix[product_index])[::-1]
# Get the top 5 similar products
top_indices = sorted_indices[1:6] # exclude self-similarity

# Display the selected product and its details
fig, axs = plt.subplots(1, 2, figsize=(10, 5))
axs[0].imshow(cv2.imread(os.path.join(image_dir, product['filename'])))
axs[0].axis('off')
axs[0].set_title(f"{product['product_id']}: {product['filename']}")
axs[1].set_axis_off()
axs[1].text(0, 0.5, 'Top 5 Similar Products:', fontsize=14)
for j, index in enumerate(top_indices):
    similar_product = products[index]
    fig = plt.figure(figsize=(5, 5))
    plt.imshow(cv2.imread(os.path.join(image_dir, similar_product['filename'])))
    plt.axis('off')
    plt.title(f"{similar_product['product_id']}: {similar_product['filename']} ({similarity_matrix[product_index][index]:.2f})", fontsize=12)
    plt.show()

import os
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import random

# Set the path to your image directory
image_dir = './images/'

# Get a list of all image files in the directory
image_files = os.listdir(image_dir)

# Define a function to load and preprocess images
def load_and_preprocess_image(image_path, target_size=(224, 224)):
    # Get the product ID from the image filename
    product_id = image_path.split("/")[-1].split("_")[0]
    # Load the image using OpenCV
    img = cv2.imread(image_path)
    # Resize the image to the target size
    img = cv2.resize(img, target_size)
    # Convert the image to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Flatten the image into a 1D array
    img = img.flatten()
    # Normalize the pixel values to be between 0 and 1
    img = img.astype('float32') / 255.0
    return product_id, img

# Load and preprocess all the images
images = []
products = []
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    product_id, image = load_and_preprocess_image(image_path)
    images.append(image)
    product_dict = {'product_id': product_id, 'image': image, 'filename': image_file}
    products.append(product_dict)

# Calculate the pairwise cosine similarity between all images
similarity_matrix = cosine_similarity(images)

# Select a random product and find its similar products
product_index = random.randint(0, len(products)-1)
product = products[product_index]
product_id = product['product_id']
print(f"Selected product: {product_id}")

# Sort the similarity matrix row for the selected product in descending order
sorted_indices = np.argsort(similarity_matrix[product_index])[::-1]
# Get the top 5 similar products
top_indices = sorted_indices[1:6] # exclude self-similarity

# Display the selected product and its top 5 similar products
fig, axs = plt.subplots(1, 6, figsize=(15, 10))
axs[0].imshow(cv2.imread(os.path.join(image_dir, product['filename'])))
axs[0].axis('off')
axs[0].set_title(f"{product['product_id']}: {product['filename']}")
for j, index in enumerate(top_indices):
    similar_product = products[index]
    axs[j+1].imshow(cv2.imread(os.path.join(image_dir, similar_product['filename'])))
    axs[j+1].axis('off')
    axs[j+1].set_title(f"{similar_product['product_id']}: {similar_product['filename']} ({similarity_matrix[product_index][index]:.2f})")
plt.show()

import os
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

# Set the path to your image directory
image_dir = './images/'

# Get a list of all image files in the directory
image_files = os.listdir(image_dir)

# Define a function to load and preprocess images
def load_and_preprocess_image(image_path, target_size=(224, 224)):
    # Get the product ID from the image filename
    product_id = image_path.split("/")[-1].split("_")[0]
    # Load the image using OpenCV
    img = cv2.imread(image_path)
    # Resize the image to the target size
    img = cv2.resize(img, target_size)
    # Convert the image to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Flatten the image into a 1D array
    img = img.flatten()
    # Normalize the pixel values to be between 0 and 1
    img = img.astype('float32') / 255.0
    return product_id, img

# Load and preprocess all the images
images = []
products = []
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    product_id, image = load_and_preprocess_image(image_path)
    images.append(image)
    product_dict = {'product_id': product_id, 'image': image, 'filename': image_file}
    products.append(product_dict)

# Calculate the pairwise cosine similarity between all images
similarity_matrix = cosine_similarity(images)

# Get user input for the product ID to find similar products
product_id = input("Enter product ID to find similar products: ")

# Find the product in the products list
product_index = None
for i, product in enumerate(products):
    if product['product_id'] == product_id:
        product_index = i
        break

if product_index is None:
    print("Product not found.")
else:
    # Sort the similarity matrix row for this product in descending order
    sorted_indices = np.argsort(similarity_matrix[product_index])[::-1]
    # Get the top 5 similar products
    top_indices = sorted_indices[1:6] # exclude self-similarity
    # Display the product and its top 5 similar products
    fig, axs = plt.subplots(1, 6, figsize=(15, 10))
    axs[0].imshow(cv2.imread(os.path.join(image_dir, products[product_index]['filename'])))
    axs[0].axis('off')
    axs[0].set_title(f"{products[product_index]['product_id']}: {products[product_index]['filename']}")
    for j, index in enumerate(top_indices):
        similar_product = products[index]
        axs[j+1].imshow(cv2.imread(os.path.join(image_dir, similar_product['filename'])))
        axs[j+1].axis('off')
        axs[j+1].set_title(f"{similar_product['product_id']}: {similar_product['filename']} ({similarity_matrix[product_index][index]:.2f})")
    plt.show()

