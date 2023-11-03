from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
import json
from pyirt import irt

app = Flask(__name__)

# Dados globais para armazenar o gabarito e as respostas dos alunos
answer_key = {}
item_params = {}

@app.route('/')
def index():
    return redirect(url_for('professor'))

@app.route('/professor')
def professor():
    return render_template('professor.html')

@app.route('/aluno')
def aluno():
    return render_template('aluno.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400

    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        global answer_key
        answer_key = json.loads(request.form['answers'])
        global item_params
        item_params = perform_calibration(df, answer_key)
        
        return 'CSV e Gabarito processados com sucesso', 200
    else:
        return 'Formato de arquivo inválido', 400

@app.route('/calculate_score', methods=['POST'])
def calculate_score():
    student_answers = request.json['answers']
    score = calculate_student_score(student_answers, item_params, answer_key)
    return jsonify({'score': score})

def perform_calibration(df, answer_key):
    src_data = []
    for idx, row in df.iterrows():
        user_id = str(row['user_id'])  # Ou o identificador de cada aluno
        for q in range(1, 26):  # Supondo 25 questões
            item_id = str(q)
            is_correct = 1 if row[f'Q{q}'] == answer_key[f'answer{q}'] else 0
            src_data.append((user_id, item_id, is_correct))
    
    _, item_param_dict, _ = irt(src_data, est_theta=False)
    return item_param_dict

def calculate_student_score(answers, item_params, answer_key):
    student_data = []
    for q in range(1, 26):  # Supondo 25 questões
        item_id = str(q)
        is_correct = 1 if answers[f'question{q}'] == answer_key[f'answer{q}'] else 0
        student_data.append((None, item_id, is_correct))
    
    _, _, person_param_dict = irt(student_data, est_item=False, item_param=item_params)
    theta = next(iter(person_param_dict.values()))[0]
    return theta

if __name__ == '__main__':
    app.run(debug=True)