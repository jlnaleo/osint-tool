#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Usuário para Ferramenta OSINT
Este módulo integra todos os módulos desenvolvidos em uma interface web.
"""

import os
import sys
import json
import logging
import tempfile
import datetime
from typing import Dict, List, Any, Optional, Union
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash

# Importar módulos OSINT
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.social_media import SocialMediaOSINT
from modules.contact_info import ContactInfoOSINT
from modules.image_recognition import ImageRecognitionOSINT
from modules.metadata_analysis import MetadataAnalysisOSINT

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('osint_interface')

# Inicializar aplicação Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Inicializar módulos OSINT
social_media_osint = SocialMediaOSINT(output_dir=os.path.join(app.config['RESULTS_FOLDER'], 'social_media'))
contact_info_osint = ContactInfoOSINT(output_dir=os.path.join(app.config['RESULTS_FOLDER'], 'contact_info'))
image_recognition_osint = ImageRecognitionOSINT(output_dir=os.path.join(app.config['RESULTS_FOLDER'], 'image_recognition'))
metadata_analysis_osint = MetadataAnalysisOSINT(output_dir=os.path.join(app.config['RESULTS_FOLDER'], 'metadata_analysis'))

@app.route('/')
def index():
    """Página inicial da ferramenta OSINT."""
    return render_template('index.html')

@app.route('/social_media')
def social_media():
    """Página do módulo de busca em redes sociais."""
    return render_template('social_media.html')

@app.route('/contact_info')
def contact_info():
    """Página do módulo de busca de e-mails e informações de contato."""
    return render_template('contact_info.html')

@app.route('/image_recognition')
def image_recognition():
    """Página do módulo de reconhecimento de imagens."""
    return render_template('image_recognition.html')

@app.route('/metadata_analysis')
def metadata_analysis():
    """Página do módulo de análise de metadados."""
    return render_template('metadata_analysis.html')

@app.route('/about')
def about():
    """Página sobre a ferramenta."""
    return render_template('about.html')

@app.route('/api/social_media/twitter', methods=['POST'])
def api_social_media_twitter():
    """API para busca no Twitter."""
    username = request.form.get('username')
    max_tweets = int(request.form.get('max_tweets', 100))
    
    if not username:
        return jsonify({'error': 'Nome de usuário não fornecido'}), 400
    
    try:
        results = social_media_osint.search_twitter(username, max_tweets)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na busca do Twitter: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social_media/instagram', methods=['POST'])
def api_social_media_instagram():
    """API para busca no Instagram."""
    username = request.form.get('username')
    max_posts = int(request.form.get('max_posts', 20))
    
    if not username:
        return jsonify({'error': 'Nome de usuário não fornecido'}), 400
    
    try:
        results = social_media_osint.search_instagram(username, max_posts)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na busca do Instagram: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social_media/facebook', methods=['POST'])
def api_social_media_facebook():
    """API para busca no Facebook."""
    username = request.form.get('username')
    max_posts = int(request.form.get('max_posts', 20))
    
    if not username:
        return jsonify({'error': 'Nome de usuário não fornecido'}), 400
    
    try:
        results = social_media_osint.search_facebook(username, max_posts)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na busca do Facebook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social_media/visualize', methods=['POST'])
def api_social_media_visualize():
    """API para visualização de conexões sociais."""
    username = request.form.get('username')
    network_type = request.form.get('network_type')
    data_json = request.form.get('data')
    
    if not username or not network_type or not data_json:
        return jsonify({'error': 'Parâmetros incompletos'}), 400
    
    try:
        data = json.loads(data_json)
        result_image = social_media_osint.visualize_social_connections(data, network_type, username)
        
        if not result_image or not os.path.exists(result_image):
            return jsonify({'error': 'Falha ao gerar visualização'}), 500
        
        return jsonify({'image_path': result_image})
    except Exception as e:
        logger.error(f"Erro na visualização de conexões: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact_info/domain', methods=['POST'])
def api_contact_info_domain():
    """API para busca de e-mails por domínio."""
    domain = request.form.get('domain')
    max_pages = int(request.form.get('max_pages', 5))
    
    if not domain:
        return jsonify({'error': 'Domínio não fornecido'}), 400
    
    try:
        results = contact_info_osint.search_emails_from_domain(domain, max_pages)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na busca de e-mails por domínio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact_info/person', methods=['POST'])
def api_contact_info_person():
    """API para busca de e-mails por pessoa."""
    name = request.form.get('name')
    domains = request.form.get('domains', '').split(',')
    
    if not name:
        return jsonify({'error': 'Nome não fornecido'}), 400
    
    # Filtrar domínios vazios
    domains = [d.strip() for d in domains if d.strip()]
    
    try:
        results = contact_info_osint.search_emails_for_person(name, domains if domains else None)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na busca de e-mails por pessoa: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact_info/phone', methods=['POST'])
def api_contact_info_phone():
    """API para busca de informações de telefone."""
    phone = request.form.get('phone')
    
    if not phone:
        return jsonify({'error': 'Telefone não fornecido'}), 400
    
    try:
        results = contact_info_osint.search_phone_info(phone)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na busca de informações de telefone: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact_info/domain_analysis', methods=['POST'])
def api_contact_info_domain_analysis():
    """API para análise de domínio."""
    domain = request.form.get('domain')
    
    if not domain:
        return jsonify({'error': 'Domínio não fornecido'}), 400
    
    try:
        results = contact_info_osint.analyze_domain(domain)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na análise de domínio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image_recognition/detect_faces', methods=['POST'])
def api_image_recognition_detect_faces():
    """API para detecção de faces em imagens."""
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Salvar imagem temporariamente
        temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
        image_path = os.path.join(temp_dir, image_file.filename)
        image_file.save(image_path)
        
        # Detectar faces
        results = image_recognition_osint.detect_faces(image_path)
        
        # Adicionar caminho da imagem para exibição
        if 'result_image' in results and results['result_image']:
            results['display_image'] = results['result_image']
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na detecção de faces: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image_recognition/detect_objects', methods=['POST'])
def api_image_recognition_detect_objects():
    """API para detecção de objetos em imagens."""
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Salvar imagem temporariamente
        temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
        image_path = os.path.join(temp_dir, image_file.filename)
        image_file.save(image_path)
        
        # Detectar objetos
        results = image_recognition_osint.detect_objects(image_path)
        
        # Adicionar caminho da imagem para exibição
        if 'result_image' in results and results['result_image']:
            results['display_image'] = results['result_image']
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na detecção de objetos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image_recognition/analyze_colors', methods=['POST'])
def api_image_recognition_analyze_colors():
    """API para análise de cores em imagens."""
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Salvar imagem temporariamente
        temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
        image_path = os.path.join(temp_dir, image_file.filename)
        image_file.save(image_path)
        
        # Analisar cores
        results = image_recognition_osint.analyze_image_colors(image_path)
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na análise de cores: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image_recognition/compare_faces', methods=['POST'])
def api_image_recognition_compare_faces():
    """API para comparação de faces em imagens."""
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Duas imagens são necessárias'}), 400
    
    image1_file = request.files['image1']
    image2_file = request.files['image2']
    
    if image1_file.filename == '' or image2_file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Salvar imagens temporariamente
        temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
        image1_path = os.path.join(temp_dir, image1_file.filename)
        image2_path = os.path.join(temp_dir, image2_file.filename)
        image1_file.save(image1_path)
        image2_file.save(image2_path)
        
        # Comparar faces
        results = image_recognition_osint.compare_faces(image1_path, image2_path)
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na comparação de faces: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metadata_analysis/analyze_file', methods=['POST'])
def api_metadata_analysis_analyze_file():
    """API para análise de metadados de arquivos."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Salvar arquivo temporariamente
        temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # Analisar metadados
        results = metadata_analysis_osint.analyze_file(file_path)
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Erro na análise de metadados: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metadata_analysis/export_csv', methods=['POST'])
def api_metadata_analysis_export_csv():
    """API para exportação de resultados para CSV."""
    file_type = request.form.get('file_type')
    
    if not file_type:
        return jsonify({'error': 'Tipo de arquivo não fornecido'}), 400
    
    try:
        # Exportar para CSV
        csv_file = metadata_analysis_osint.export_results_to_csv(file_type)
        
        if not csv_file or not os.path.exists(csv_file):
            return jsonify({'error': 'Falha ao exportar resultados'}), 500
        
        return jsonify({'csv_file': csv_file})
    except Exception as e:
        logger.error(f"Erro na exportação para CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Rota para download de arquivos."""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(filename):
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('index'))
        
        # Enviar arquivo para download
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Erro no download do arquivo: {str(e)}")
        flash(f'Erro ao baixar arquivo: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/view_image/<path:filename>')
def view_image(filename):
    """Rota para visualização de imagens."""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(filename):
            flash('Imagem não encontrada', 'error')
            return redirect(url_for('index'))
        
        # Enviar imagem para visualização
        return send_file(filename)
    except Exception as e:
        logger.error(f"Erro na visualização da imagem: {str(e)}")
        flash(f'Erro ao visualizar imagem: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Manipulador para páginas não encontradas."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Manipulador para erros internos do servidor."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Iniciar servidor Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
