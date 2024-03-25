from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Arquivo inválido!", 400

    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo foi selecionado!", 400

    if file:
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(file.read()), encoding='utf-8')
        else:
            return "Arquivo inválido, é aceito apenas XLSX ou CSV.", 400

        df['data início'] = pd.to_datetime(df['data início'], format='%m/%d/%y %H:%M')
        df['valor'] = df['valor'].apply(lambda x: float(str(x).replace(',', '.')))

        # Cálculo de MRR - Este será o cálculo principal
        mrr_data = df.groupby(df['data início'].dt.to_period('M'))['valor'].sum().to_dict()

        # Cálculo de Churn Rate - Este será o cálculo secundário
        churn_data = df[df['status'] == 'Cancelada'].groupby(df['data início'].dt.to_period('M')).size().to_dict()

        # Cálculo de Trial Cancelados - Este cálculo se baseia em todos os usuários com status "Trial cancelado"
        # É uma boa métrica para avaliar se as opções do trial são realmente atrativas e cativantes
        trial_cancelled_data = df[df['status'] == 'Trial cancelado'].groupby(df['data início'].dt.to_period('M')).size().to_dict()

        # Cálculo de Active Subscribers
        # Esta também é uma métrica interessante, pois expõe a satisfação dos usuários da plataforma
        active_subs_data = df[df['status'] == 'Ativa'].groupby(df['data início'].dt.to_period('M')).size().to_dict()

        # Conversão de Period para string
        mrr_data_str = {str(key): value for key, value in mrr_data.items()}
        churn_data_str = {str(key): value for key, value in churn_data.items()}
        trial_cancelled_data_str = {str(key): value for key, value in trial_cancelled_data.items()}
        active_subs_data_str = {str(key): value for key, value in active_subs_data.items()}

        return jsonify({
            "MRR": mrr_data_str,
            "Churn Rate": churn_data_str,
            "Trial Cancelled": trial_cancelled_data_str,
            "Active Subscribers": active_subs_data_str
        })

    return "Houve um erro sistêmico, tente novamente!", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)