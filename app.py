from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
import json
from girth import *
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('professor'))

@app.route('/professor')
def professor():
    return render_template('professor.html')

# Nova função aluno() modificada
@app.route('/aluno')
def aluno():
    with open('simulated_bd.json', 'r') as file:
        exams = json.load(file)
    exam_names = [exam['Nome do Exame'] for exam in exams]
    return render_template('aluno.html', exam_names=exam_names) 

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400

    if file and file.filename.endswith('.csv'):
        sb = pd.read_csv(file) # aqui você deve importar o csv response
        dT = np.array([i.split(",") for i in sb.split("\n")])
        d = dT.T
        objt = [[ 0 if dT[i][j]=="0" else 1 for i in range(len(d[j])) if i != 0] for j in range(len(d)) if len(set(d[j])) == 3]
        data = np.array(objt)
        gTRI = twopl_jml(data) # salvar em formato json, isto é o compulado de parametros do exame. Deve ser importado do json quando o aluno requisitar a nota
        gTRI['Exame'] = str(json.loads(request.form['Nome do Exame']))
        with open("bd.json") as fp:
          bd = json.load(fp)
        bd.update(gTRI)
        with open("bd.json", 'w') as json_file:
            json.dump(bd, json_file, 
                        indent=4,  
                        separators=(',',': '))
        
        return 'CSV e Gabarito processados com sucesso', 200
    else:
        return 'Formato de arquivo inválido', 400

@app.route('/calculate_score', methods=['POST'])
def calculate_score():
    prova_do_aluno = np.array(request.json['answers'])
    with open("bd.json") as fp:
          bd = json.load(fp)
    gTRI = bd[request.json['Nome do Exame']] ## unico problema
    score = ability_eap(prova_do_aluno, gTRI["Difficulty"], gTRI["Discrimination"])*100+500 # retorna nota do aluno
    return jsonify({'score': score})

if __name__ == '__main__':
    app.run(debug=True)