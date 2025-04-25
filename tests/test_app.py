#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes de integração para a aplicação Flask da Ferramenta OSINT
Este script realiza testes na aplicação web para garantir que todas as rotas e APIs estejam funcionando corretamente.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Adicionar diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar a aplicação Flask
try:
    from app import app
except ImportError as e:
    print(f"Erro ao importar a aplicação Flask: {e}")
    sys.exit(1)

class TestFlaskApp(unittest.TestCase):
    """Testes para a aplicação Flask."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Configurar cliente de teste
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Criar diretório temporário para uploads
        self.temp_dir = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = self.temp_dir
        app.config['RESULTS_FOLDER'] = self.temp_dir
        
        # Criar arquivo de teste para upload
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        with open(self.test_image_path, "wb") as f:
            f.write(b"dummy image content")
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    def test_index_route(self):
        """Testa a rota principal."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ferramenta OSINT', response.data)
    
    def test_social_media_route(self):
        """Testa a rota de redes sociais."""
        response = self.client.get('/social_media')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Redes Sociais', response.data)
    
    def test_contact_info_route(self):
        """Testa a rota de e-mails e contatos."""
        response = self.client.get('/contact_info')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'E-mails e Contatos', response.data)
    
    def test_image_recognition_route(self):
        """Testa a rota de reconhecimento de imagens."""
        response = self.client.get('/image_recognition')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reconhecimento de Imagens', response.data)
    
    def test_metadata_analysis_route(self):
        """Testa a rota de análise de metadados."""
        response = self.client.get('/metadata_analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Análise de Metadados', response.data)
    
    def test_about_route(self):
        """Testa a rota sobre."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sobre a Ferramenta OSINT', response.data)
    
    @patch('modules.social_media.SocialMediaOSINT')
    def test_twitter_search_api(self, mock_social_media):
        """Testa a API de busca no Twitter."""
        # Configurar mock
        mock_instance = MagicMock()
        mock_instance.search_twitter.return_value = {
            "profile": {
                "name": "Usuário Teste",
                "screen_name": "usuario_teste",
                "followers_count": 100
            },
            "tweets": [
                {
                    "text": "Tweet de teste",
                    "created_at": "2023-01-01",
                    "retweet_count": 10
                }
            ]
        }
        mock_social_media.return_value = mock_instance
        
        # Executar requisição
        response = self.client.post('/api/social_media/twitter', json={
            "username": "usuario_teste",
            "tweet_count": 1
        })
        
        # Verificar resultado
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("profile", data)
        self.assertIn("tweets", data)
        self.assertEqual(data["profile"]["name"], "Usuário Teste")
    
    @patch('modules.contact_info.ContactInfoOSINT')
    def test_email_search_api(self, mock_contact_info):
        """Testa a API de busca de e-mails."""
        # Configurar mock
        mock_instance = MagicMock()
        mock_instance.search_emails_from_domain.return_value = {
            "domain": "exemplo.com.br",
            "emails_found": ["contato@exemplo.com.br", "suporte@exemplo.com.br"],
            "pages_scanned": 1
        }
        mock_contact_info.return_value = mock_instance
        
        # Executar requisição
        response = self.client.post('/api/contact_info/emails', json={
            "domain": "exemplo.com.br",
            "pages": 1
        })
        
        # Verificar resultado
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("domain", data)
        self.assertIn("emails_found", data)
        self.assertEqual(data["domain"], "exemplo.com.br")
        self.assertEqual(len(data["emails_found"]), 2)
    
    @patch('modules.image_recognition.ImageRecognitionOSINT')
    def test_face_detection_api(self, mock_image_recognition):
        """Testa a API de detecção de faces."""
        # Configurar mock
        mock_instance = MagicMock()
        mock_instance.detect_faces.return_value = {
            "faces_detected": [
                {
                    "location": {"x": 10, "y": 20, "width": 100, "height": 100},
                    "gender": "Masculino",
                    "age": 30,
                    "emotion": "Neutro"
                }
            ],
            "result_image": "result_image.jpg"
        }
        mock_image_recognition.return_value = mock_instance
        
        # Criar arquivo de imagem para upload
        with open(self.test_image_path, "rb") as img:
            # Executar requisição
            response = self.client.post(
                '/api/image_recognition/detect_faces',
                data={"image": (img, "test_image.jpg")},
                content_type="multipart/form-data"
            )
        
        # Verificar resultado
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("faces_detected", data)
        self.assertEqual(len(data["faces_detected"]), 1)
        self.assertEqual(data["faces_detected"][0]["gender"], "Masculino")
    
    @patch('modules.metadata_analysis.MetadataAnalysisOSINT')
    def test_metadata_analysis_api(self, mock_metadata_analysis):
        """Testa a API de análise de metadados."""
        # Configurar mock
        mock_instance = MagicMock()
        mock_instance.analyze_file.return_value = {
            "file_type": "image",
            "file_name": "test_image.jpg",
            "file_size": 1024,
            "file_size_human": "1.0 KB",
            "creation_date": "2023-01-01T12:00:00",
            "modification_date": "2023-01-02T12:00:00",
            "dimensions": {"width": 800, "height": 600},
            "exif_data": {
                "Make": "Canon",
                "Model": "EOS 5D"
            }
        }
        mock_metadata_analysis.return_value = mock_instance
        
        # Criar arquivo para upload
        with open(self.test_image_path, "rb") as img:
            # Executar requisição
            response = self.client.post(
                '/api/metadata_analysis/analyze_file',
                data={"file": (img, "test_image.jpg")},
                content_type="multipart/form-data"
            )
        
        # Verificar resultado
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["file_type"], "image")
        self.assertEqual(data["file_name"], "test_image.jpg")
        self.assertIn("exif_data", data)
        self.assertEqual(data["exif_data"]["Make"], "Canon")


if __name__ == '__main__':
    unittest.main()
