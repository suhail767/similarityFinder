# -*- coding: utf-8 -*-
"""findSimilarProduct767

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15WkBKWCmIbspnL3VaC2frEbQfPPm37kM

## **Import Libraries**
"""

!pip install -r 'https://raw.githubusercontent.com/suhail767/similarityFinder/main/requirements.txt'

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
from PIL import Image
import requests
from io import BytesIO

"""# Extract Data from website Json file"""

# Use this when you have a list of websites and want to extract data from all 
# and combine it to one big dataset
"""

urls = [

    "https://www.boysnextdoor-apparel.co/collections/all/products.json"
]

all_products = []

for url in urls:
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

print(f"Retrieved {len(all_products)} products from {len(urls)} websites.")

# Save the combined dataset as a JSON file
with open("productInfo.json", "w") as f:
    json.dump(all_products, f)

"""

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

"""# Provide the inputs for the program here"""

# Set the base URL for the website
base_url = 'https://www.woolsboutiqueuomo.com//'
data_url = "https://www.woolsboutiqueuomo.com/collections/all/products.json"

# Enter the id of the product which you want to find similar products of
product_identifier = '8392243675465'

all_products = get_all_products(data_url)

# Save the combined dataset as a JSON file
with open("productInfo.json", "w") as f:
    json.dump(all_products, f)

"""# Set the base URL for the website
base_url = 'https://www.boysnextdoor-apparel.co//'
data_url = "https://www.boysnextdoor-apparel.co/collections/all/products.json"

all_products = get_all_products(url)

# Save the combined dataset as a JSON file
with open("productInfo.json", "w") as f:
    json.dump(all_products, f)

# Load Dataset
"""

# Load data from JSON file
with open('productInfo.json', 'r') as f:
    data = json.load(f)

# Create a list of dictionaries for each product with required features
# Create a list of dictionaries for each product with required features
products = []
for p in data:
    product_dict = {'product_id':str(p['id']),'title': p['title'], 'vendor': p['vendor'], 'product_type': p['product_type'], 'tags': p['tags'], 'handle': p['handle'], 'images': p['images']}
    products.append(product_dict)

# Print the list of product dictionaries
print(len(products))
print(products[:3])

"""# Dataframe creation and preprocessing"""

# Create a pandas dataframe from products list
df = pd.DataFrame(products)

# drop duplicates based on product_id
df.drop_duplicates(subset='product_id', keep='first', inplace=True)
# remove any NaN values
df = df.dropna()
# convert 'tags' column to string type
df['tags'] = df['tags'].astype(str)
df.shape

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

# Define stop words and lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Function to clean text data
def clean_text(text):
    # Remove special characters
    text = re.sub(r'\W+', ' ', text)

    # Convert to lowercase
    text = text.lower()

    # Remove stop words
    text = ' '.join(word for word in text.split() if word not in stop_words)

    # Lemmatize words
    text = ' '.join(lemmatizer.lemmatize(word) for word in text.split())

    return text

# Apply text cleaning to the title and tags columns
df['title'] = df['title'].apply(clean_text)
df['tags'] = df['tags'].apply(clean_text)

# Add URL to product and URL to image columns to the DataFrame
df['product_url'] = df.apply(lambda row: f"{base_url}product/{row['handle']}", axis=1)
df['image_url'] = df.apply(lambda row: row['images'][0]['src'] if row['images'] else None, axis=1)

# Add URL to product and URL to image columns to the DataFrame
df['product_url'] = df['handle'].apply(lambda x: f"https://www.boysnextdoor-apparel.co/products/{x}")
df['image_url'] = df['images'].apply(lambda x: x[0]['src'] if len(x)>0 else None)

"""# Generate Word embeddings"""

!wget http://nlp.stanford.edu/data/glove.6B.zip
!unzip glove.6B.zip

from gensim.scripts.glove2word2vec import glove2word2vec
glove_file = 'glove.6B.100d.txt'
word2vec_output_file = 'glove.6B.100d.word2vec.txt'
glove2word2vec(glove_file, word2vec_output_file)

from gensim.models import KeyedVectors
word_vectors = KeyedVectors.load_word2vec_format(word2vec_output_file, binary=False)

# Function to generate word embeddings for a text string
def get_word_embeddings(text):
    # Split text into individual words
    words = text.split()

    # Initialize an empty array for storing the embeddings
    embeddings = []

    # Iterate over each word in the text
    for word in words:
        # Check if the word is in the vocabulary
        if word in word_vectors.key_to_index:
            # If the word is in the vocabulary, add its embedding to the list
            embeddings.append(word_vectors[word])

    # If no valid embeddings were found, return None
    if len(embeddings) == 0:
        return None

    # Otherwise, calculate the mean of the embeddings and return the result
    return np.mean(embeddings, axis=0)

# Generate word embeddings for each product
df['title_vec'] = df['title'].apply(get_word_embeddings)
df['tag_vec'] = df['tags'].apply(get_word_embeddings)

"""# Get similarity score by calculating Cosine Similarity"""

def get_similar_products(product_id, num_similar=5):
    # Get the embedding vector for the specified product
    embedding = df.loc[df['product_id'] == product_id, 'title_vec'].values[0]
    
    # Calculate the cosine similarity between the specified product and all other products
    similarities = cosine_similarity(df['title_vec'].tolist(), [embedding])
    
    # Get the indices of the most similar products
    similar_indices = np.argsort(similarities.ravel())[::-1][:num_similar+1]
    
    # Exclude the specified product from the list of similar products
    similar_indices = similar_indices[similar_indices != df.index[df['product_id'] == product_id][0]]
    
    # Get the details of the specified product
    product = df.loc[df['product_id'] == product_id].iloc[0]
    
    # Print the details of the specified product
    print(f"Product ID: {product['product_id']}")
    print(f"Title: {product['title']}")
    print(f"Product Type: {product['product_type']}")
    print(f"Vendor: {product['vendor']}")
    print(f"Tags: {product['tags']}")
    print(f"Product URL: {product['product_url']}")
    print(f"Image URL: {product['image_url']}")
    
    # Open the image and resize it
    response = requests.get(product['image_url'])
    img = Image.open(BytesIO(response.content))
    img = img.resize((300, 300))  # Change the dimensions as per your requirement
    img.show()
    
    # Print the details of the similar products
    print("\n******************************\n")
    print("\nSimilar products:\n")
    for i in similar_indices:
        product = df.iloc[i]
        print(f"Product ID: {product['product_id']}")
        print(f"Title: {product['title']}")
        print(f"Product Type: {product['product_type']}")
        print(f"Vendor: {product['vendor']}")
        print(f"Tags: {product['tags']}")
        print(f"Product URL: {product['product_url']}")
        print(f"Image URL: {product['image_url']}")
        
        # Open the image and resize it
        response = requests.get(product['image_url'])
        img = Image.open(BytesIO(response.content))
        img = img.resize((300, 300))  # Change the dimensions as per your requirement
        img.show()
        
        print(f"Similarity score: {similarities[i][0]:.4f}")
        print()

"""# Find similar products for a Product ID based on the Similarity score"""

if product_identifier not in df['product_id'].unique():
    print(f"The product ID {product_identifier} does not exist in the DataFrame.")
else:
    get_similar_products(product_identifier)

