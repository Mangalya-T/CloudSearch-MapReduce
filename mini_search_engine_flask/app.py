from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)
FOLDER = "documents"

# Map Phase: tokenize and map words to filenames
def map_phase(folder):
    mapped = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as file:
                content = file.read().lower()
                words = re.findall(r'\b\w+\b', content)
                for word in words:
                    mapped.append((word, filename))
    return mapped

# Reduce Phase: create inverted index from mapped data
def reduce_phase(mapped):
    inverted_index = {}
    for word, filename in mapped:
        if word not in inverted_index:
            inverted_index[word] = set()
        inverted_index[word].add(filename)
    return inverted_index

# Build the inverted index at startup
mapped = map_phase(FOLDER)
inverted_index = reduce_phase(mapped)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    result_docs = inverted_index.get(query, [])

    highlighted_results = []
    for doc in result_docs:
        with open(os.path.join(FOLDER, doc), "r", encoding="utf-8") as file:
            content = file.read()
            # Highlight the searched word in red bold text
            highlighted = re.sub(f"(?i)({re.escape(query)})", r"<span style='color: red; font-weight: bold;'>\1</span>", content)
            highlighted_results.append((doc, highlighted))

    return render_template('result.html', results=highlighted_results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
