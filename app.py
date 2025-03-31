from flask import Flask, request, jsonify
import os
import zipfile
import openai

# OpenAI API Key (Set this securely in an environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_csv_from_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        for file in os.listdir(extract_to):
            if file.endswith(".csv"):
                return os.path.join(extract_to, file)
    return None

def generate_answer(question):
    if not OPENAI_API_KEY:
        return "LLM API key missing. Set the OPENAI_API_KEY environment variable."
    
    prompt = f"Answer the following question based on the graded assignments: {question}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert in IIT Madras Data Science assignments. Always provide precise answers."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

app = Flask(__name__)

@app.route('/api/', methods=['POST'])
def tds_solver():
    question = request.form.get("question")
    file = request.files.get("file")
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    answer = generate_answer(question)
    
    if file:
        zip_path = os.path.join("uploads", file.filename)
        file.save(zip_path)
        extract_to = "extracted"
        csv_file = extract_csv_from_zip(zip_path, extract_to)
        if csv_file:
            answer = f"Processed CSV file: {csv_file} - {generate_answer(f'Process data from {csv_file}')}"
    
    return jsonify({"answer": answer})

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("extracted", exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
