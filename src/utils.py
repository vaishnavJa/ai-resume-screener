import json
import requests

def get_available_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        print("Error fetching Ollama models:", e)
        return []

def read_file(filename):

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        print(f"Cannot open file {filename}, {e}")

    return data

def write_json_output(filename,data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data,f,indent=2)
