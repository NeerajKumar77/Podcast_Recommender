from flask import Flask, jsonify, request, render_template
import json
import pandas as pd
import os

app = Flask(__name__)

def read_json_lines_in_chunks(file_path, chunk_size=10000):
    """
    Reads a JSON Lines file in chunks and returns a generator that yields pandas DataFrames.
    
    Parameters:
    - file_path (str): Path to the JSON Lines file.
    - chunk_size (int): Number of lines per chunk to read.

    Yields:
    - pd.DataFrame: DataFrame of the current chunk.
    """
    with open(file_path, 'r') as file:
        data_chunk = []
        for line_num, line in enumerate(file, 1):
            try:
                # Load each line as a JSON object
                data_chunk.append(json.loads(line))
                
                # When the chunk size is reached, yield the data as a DataFrame
                if line_num % chunk_size == 0:
                    yield pd.DataFrame(data_chunk)
                    data_chunk = []  # Reset the chunk

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_num}: {e}")

        # Yield the last chunk if there is any data left
        if data_chunk:
            yield pd.DataFrame(data_chunk)

# Path to your podcast data file
podcasts_file_path = '/Users/neerajkumar/Downloads/digital_assignments/c1 - dsp/last_da/podcasts.json'

def load_podcasts(file_path):
    podcasts = []
    # Read the file and extend the podcasts list with each chunk
    if os.path.exists(file_path):
        for chunk in read_json_lines_in_chunks(file_path):
            podcasts.extend(chunk.to_dict(orient='records'))  # Convert each chunk to dict and extend the list
    else:
        print(f"File not found: {file_path}")
    return podcasts

# Load podcasts into memory once when the app starts
podcasts_data = load_podcasts(podcasts_file_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    topic = request.args.get('topic', '').lower()
    recommendations = recommend_podcasts_by_topic(topic, podcasts_data, max_recommendations=5)
    return jsonify(recommendations)

def recommend_podcasts_by_topic(topic, podcasts, max_recommendations=5):
    recommendations = []
    for item in podcasts:
        if 'description' in item and item['description'] and topic in item['description'].lower():
            recommendations.append({
                'title': item.get('title', 'No Title'),
                'link': item.get('itunes_url', 'No Link')
            })
            if len(recommendations) >= max_recommendations:
                break
    return recommendations

if __name__ == '__main__':
    app.run(debug=True)
