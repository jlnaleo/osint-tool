#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes para a Ferramenta OSINT
Este script realiza testes básicos em todos os módulos da ferramenta OSINT.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Adicionar diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos para teste
try:
    from modules.social_media import SocialMediaOSINT
    from modules.contact_info import ContactInfoOSINT
    from modules.image_recognition import ImageRecognitionOSINT
    from modules.metadata_analysis import MetadataAnalysisOSINT
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)

class TestSocialMediaModule(unittest.TestCase):
    """Testes para o módulo de busca em redes sociais."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.social_media = SocialMediaOSINT(output_dir=self.temp_dir)
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    @patch('modules.social_media.tweepy.API')
    def test_twitter_search(self, mock_api):
        """Testa a busca no Twitter."""
        # Configurar mock
        mock_user = MagicMock()
        mock_user.name = "Usuário Teste"
        mock_user.screen_name = "usuario_teste"
        mock_user.description = "Descrição de teste"
        mock_user.followers_count = 100
        mock_user.friends_count = 50
        mock_user.statuses_count = 200
        mock_user.location = "Brasil"
        mock_user.created_at = "2020-01-01"
        mock_user.profile_image_url = "http://example.com/image.jpg"
        
        mock_tweet = MagicMock()
        mock_tweet.text = "Tweet de teste"
        mock_tweet.created_at = "2023-01-01"
        mock_tweet.retweet_count = 10
        mock_tweet.favorite_count = 20
        
        mock_api.return_value.get_user.return_value = mock_user
        mock_api.return_value.user_timeline.return_value = [mock_tweet]
        
        # Executar função
        result = self.social_media.search_twitter("usuario_teste", 1)
        
        # Verificar resultado
        self.assertIn("profile", result)
        self.assertIn("tweets", result)
        self.assertEqual(result["profile"]["name"], "Usuário Teste")
        self.assertEqual(len(result["tweets"]), 1)
        self.assertEqual(result["tweets"][0]["text"], "Tweet de teste")
    
    @patch('modules.social_media.instaloader.Instaloader')
    @patch('modules.social_media.instaloader.Profile')
    def test_instagram_search(self, mock_profile, mock_instaloader):
        """Testa a busca no Instagram."""
        # Configurar mock
        mock_profile_instance = MagicMock()
        mock_profile_instance.username = "usuario_teste"
        mock_profile_instance.full_name = "Usuário Teste"
        mock_profile_instance.biography = "Bio de teste"
        mock_profile_instance.followers = 100
        mock_profile_instance.followees = 50
        mock_profile_instance.mediacount = 30
        mock_profile_instance.profile_pic_url = "http://example.com/image.jpg"
        mock_profile_instance.is_verified = True
        mock_profile_instance.external_url = "http://example.com"
        
        mock_post = MagicMock()
        mock_post.caption = "Legenda de teste"
        mock_post.date_utc = "2023-01-01"
        mock_post.likes = 50
        mock_post.comments = 10
        mock_post.url = "http://example.com/post"
        
        mock_profile.from_username.return_value = mock_profile_instance
        mock_profile_instance.get_posts.return_value = [mock_post]
        
        # Executar função
        result = self.social_media.search_instagram("usuario_teste", 1)
        
        # Verificar resultado
        self.assertIn("profile", result)
        self.assertIn("posts", result)
        self.assertEqual(result["profile"]["username"], "usuario_teste")
        self.assertEqual(len(result["posts"]), 1)
        self.assertEqual(result["posts"][0]["caption"], "Legenda de teste")
    
    @patch('modules.social_media.facebook_scraper.get_profile')
    @patch('modules.social_media.facebook_scraper.get_posts')
    def test_facebook_search(self, mock_get_posts, mock_get_profile):
        """Testa a busca no Facebook."""
        # Configurar mock
        mock_get_profile.return_value = {
            "Name": "Usuário Teste",
            "Username": "usuario_teste",
            "Followers": 100,
            "Following": 50,
            "Friends": 200,
            "Profile picture": "http://example.com/image.jpg",
            "Location": "Brasil"
        }
        
        mock_get_posts.return_value = [{
            "text": "Post de teste",
            "time": "2023-01-01",
            "likes": 30,
            "comments": 5,
            "shares": 2,
            "post_url": "http://example.com/post"
        }]
        
        # Executar função
        result = self.social_media.search_facebook("usuario_teste", 1)
        
        # Verificar resultado
        self.assertIn("profile", result)
        self.assertIn("posts", result)
        self.assertEqual(result["profile"]["name"], "Usuário Teste")
        self.assertEqual(len(result["posts"]), 1)
        self.assertEqual(result["posts"][0]["text"], "Post de teste")
    
    def test_visualize_social_connections(self):
        """Testa a visualização de conexões sociais."""
        # Dados de teste
        data = {
            "profile": {
                "name": "Usuário Teste",
                "screen_name": "usuario_teste"
            },
            "connections": [
                {"source": "usuario_teste", "target": "amigo1", "type": "friend"},
                {"source": "usuario_teste", "target": "amigo2", "type": "friend"}
            ]
        }
        
        # Executar função
        result = self.social_media.visualize_social_connections(data, "twitter", "usuario_teste")
        
        # Verificar resultado
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))


class TestContactInfoModule(unittest.TestCase):
    """Testes para o módulo de busca de e-mails e informações de contato."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.contact_info = ContactInfoOSINT(output_dir=self.temp_dir)
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    @patch('modules.contact_info.requests.get')
    def test_search_emails_from_domain(self, mock_get):
        """Testa a busca de e-mails por domínio."""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <p>Contato: contato@exemplo.com.br</p>
                <p>Suporte: suporte@exemplo.com.br</p>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Executar função
        result = self.contact_info.search_emails_from_domain("exemplo.com.br", 1)
        
        # Verificar resultado
        self.assertIn("emails_found", result)
        self.assertEqual(len(result["emails_found"]), 2)
        self.assertIn("contato@exemplo.com.br", result["emails_found"])
        self.assertIn("suporte@exemplo.com.br", result["emails_found"])
    
    def test_search_emails_for_person(self):
        """Testa a busca de e-mails por pessoa."""
        # Executar função
        result = self.contact_info.search_emails_for_person("João Silva", ["exemplo.com.br"])
        
        # Verificar resultado
        self.assertIn("name_variations", result)
        self.assertIn("domains_checked", result)
        self.assertIn("possible_emails", result)
        self.assertTrue(len(result["possible_emails"]) > 0)
    
    @patch('modules.contact_info.phonenumbers.parse')
    @patch('modules.contact_info.phonenumbers.is_valid_number')
    @patch('modules.contact_info.phonenumbers.format_number')
    def test_search_phone_info(self, mock_format, mock_is_valid, mock_parse):
        """Testa a busca de informações de telefone."""
        # Configurar mock
        mock_parse.return_value = "parsed_number"
        mock_is_valid.return_value = True
        mock_format.return_value = "+5511999999999"
        
        # Executar função com patch adicional para a função interna
        with patch.object(self.contact_info, '_get_phone_carrier_info') as mock_carrier:
            mock_carrier.return_value = {
                "country": "Brasil",
                "carrier": "Operadora Teste",
                "region": "São Paulo",
                "line_type": "mobile"
            }
            
            result = self.contact_info.search_phone_info("+5511999999999")
        
        # Verificar resultado
        self.assertEqual(result["original_number"], "+5511999999999")
        self.assertEqual(result["normalized_number"], "+5511999999999")
        self.assertEqual(result["phone_info"]["country"], "Brasil")
        self.assertEqual(result["phone_info"]["carrier"], "Operadora Teste")
    
    @patch('modules.contact_info.whois.whois')
    def test_analyze_domain(self, mock_whois):
        """Testa a análise de domínio."""
        # Configurar mock
        mock_whois.return_value = {
            "domain_name": "exemplo.com.br",
            "registrar": "Registrador Teste",
            "creation_date": "2020-01-01",
            "expiration_date": "2025-01-01",
            "name_servers": ["ns1.exemplo.com.br", "ns2.exemplo.com.br"],
            "emails": ["admin@exemplo.com.br"]
        }
        
        # Executar função com patch adicional para a função interna
        with patch.object(self.contact_info, '_check_website_availability') as mock_check:
            mock_check.return_value = (True, 200)
            
            with patch.object(self.contact_info, '_get_ssl_info') as mock_ssl:
                mock_ssl.return_value = {
                    "has_ssl": True,
                    "issuer": {"CN": "Let's Encrypt"},
                    "subject": {"CN": "exemplo.com.br"},
                    "not_before": "2023-01-01",
                    "not_after": "2024-01-01"
                }
                
                result = self.contact_info.analyze_domain("exemplo.com.br")
        
        # Verificar resultado
        self.assertEqual(result["domain"], "exemplo.com.br")
        self.assertEqual(result["whois_info"]["registrar"], "Registrador Teste")
        self.assertTrue(result["site_available"])
        self.assertEqual(result["status_code"], 200)
        self.assertTrue(result["ssl_info"]["has_ssl"])


class TestImageRecognitionModule(unittest.TestCase):
    """Testes para o módulo de reconhecimento de imagens."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.image_recognition = ImageRecognitionOSINT(output_dir=self.temp_dir)
        
        # Criar uma imagem de teste
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        with open(self.test_image_path, "w") as f:
            f.write("dummy image content")
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    @patch('modules.image_recognition.cv2.imread')
    @patch('modules.image_recognition.cv2.CascadeClassifier')
    def test_detect_faces(self, mock_cascade, mock_imread):
        """Testa a detecção de faces."""
        # Configurar mock
        mock_image = MagicMock()
        mock_imread.return_value = mock_image
        
        mock_detector = MagicMock()
        mock_detector.detectMultiScale.return_value = [(10, 20, 100, 100)]
        mock_cascade.return_value = mock_detector
        
        # Executar função com patch adicional
        with patch.object(self.image_recognition, '_analyze_face') as mock_analyze:
            mock_analyze.return_value = {
                "gender": "Masculino",
                "age": 30,
                "emotion": "Neutro"
            }
            
            with patch('modules.image_recognition.cv2.imwrite') as mock_imwrite:
                mock_imwrite.return_value = True
                
                result = self.image_recognition.detect_faces(self.test_image_path)
        
        # Verificar resultado
        self.assertIn("faces_detected", result)
        self.assertEqual(len(result["faces_detected"]), 1)
        self.assertEqual(result["faces_detected"][0]["gender"], "Masculino")
        self.assertEqual(result["faces_detected"][0]["age"], 30)
        self.assertIn("result_image", result)
    
    @patch('modules.image_recognition.cv2.imread')
    @patch('modules.image_recognition.cv2.dnn.readNetFromDarknet')
    @patch('modules.image_recognition.cv2.dnn.blobFromImage')
    def test_detect_objects(self, mock_blob, mock_net, mock_imread):
        """Testa a detecção de objetos."""
        # Configurar mock
        mock_image = MagicMock()
        mock_image.shape = (300, 400, 3)
        mock_imread.return_value = mock_image
        
        mock_model = MagicMock()
        mock_model.getLayerNames.return_value = ["layer1", "layer2", "yolo_82", "yolo_94", "yolo_106"]
        mock_model.getUnconnectedOutLayers.return_value = [82, 94, 106]
        mock_net.return_value = mock_model
        
        # Configurar saída da rede neural
        mock_output = [
            # Formato: [x, y, width, height, confidence, class1_conf, class2_conf, ...]
            [[0.5, 0.5, 0.2, 0.2, 0.9, 0.0, 0.9, 0.0]]  # Objeto "pessoa" com 90% de confiança
        ]
        mock_model.forward.return_value = mock_output
        
        # Executar função com patches adicionais
        with patch.object(self.image_recognition, '_load_classes') as mock_load_classes:
            mock_load_classes.return_value = ["background", "pessoa", "carro"]
            
            with patch('modules.image_recognition.cv2.imwrite') as mock_imwrite:
                mock_imwrite.return_value = True
                
                result = self.image_recognition.detect_objects(self.test_image_path)
        
        # Verificar resultado
        self.assertIn("objects_detected", result)
        self.assertEqual(len(result["objects_detected"]), 1)
        self.assertEqual(result["objects_detected"][0]["name"], "pessoa")
        self.assertGreater(result["objects_detected"][0]["confidence"], 0.8)
        self.assertIn("result_image", result)
    
    @patch('modules.image_recognition.cv2.imread')
    @patch('modules.image_recognition.cv2.cvtColor')
    @patch('modules.image_recognition.cv2.calcHist')
    def test_analyze_image_colors(self, mock_hist, mock_cvtcolor, mock_imread):
        """Testa a análise de cores em imagens."""
        # Configurar mock
        mock_image = MagicMock()
        mock_image.shape = (300, 400, 3)
        mock_imread.return_value = mock_image
        
        mock_cvtcolor.return_value = mock_image
        
        # Configurar histograma
        mock_hist.return_value = [10, 20, 30, 40, 50]
        
        # Executar função com patches adicionais
        with patch.object(self.image_recognition, '_get_dominant_colors') as mock_dominant:
            mock_dominant.return_value = [
                {"hex": "#FF0000", "rgb": [255, 0, 0], "percentage": 60.0},
                {"hex": "#0000FF", "rgb": [0, 0, 255], "percentage": 40.0}
            ]
            
            result = self.image_recognition.analyze_image_colors(self.test_image_path)
        
        # Verificar resultado
        self.assertIn("dominant_colors", result)
        self.assertEqual(len(result["dominant_colors"]), 2)
        self.assertEqual(result["dominant_colors"][0]["hex"], "#FF0000")
        self.assertIn("color_distribution", result)
        self.assertIn("image_stats", result)
    
    @patch('modules.image_recognition.cv2.imread')
    @patch('modules.image_recognition.face_recognition.face_encodings')
    @patch('modules.image_recognition.face_recognition.face_locations')
    @patch('modules.image_recognition.face_recognition.compare_faces')
    @patch('modules.image_recognition.face_recognition.face_distance')
    def test_compare_faces(self, mock_distance, mock_compare, mock_locations, mock_encodings, mock_imread):
        """Testa a comparação de faces."""
        # Configurar mock
        mock_image = MagicMock()
        mock_imread.return_value = mock_image
        
        mock_locations.return_value = [(10, 110, 110, 10)]  # top, right, bottom, left
        mock_encodings.return_value = ["face_encoding"]
        mock_compare.return_value = [True]
        mock_distance.return_value = [0.4]  # Distância menor = mais similar
        
        # Executar função
        result = self.image_recognition.compare_faces(self.test_image_path, self.test_image_path)
        
        # Verificar resultado
        self.assertIn("match", result)
        self.assertTrue(result["match"])
        self.assertIn("similarity", result)
        self.assertGreater(result["similarity"], 0.5)  # Similaridade deve ser alta


class TestMetadataAnalysisModule(unittest.TestCase):
    """Testes para o módulo de análise de metadados."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_analysis = MetadataAnalysisOSINT(output_dir=self.temp_dir)
        
        # Criar arquivos de teste
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        with open(self.test_image_path, "w") as f:
            f.write("dummy image content")
        
        self.test_document_path = os.path.join(self.temp_dir, "test_document.docx")
        with open(self.test_document_path, "w") as f:
            f.write("dummy document content")
        
        self.test_pdf_path = os.path.join(self.temp_dir, "test_document.pdf")
        with open(self.test_pdf_path, "w") as f:
            f.write("dummy pdf content")
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    @patch('modules.metadata_analysis.exifread.process_file')
    @patch('modules.metadata_analysis.Image.open')
    def test_analyze_image(self, mock_pil_open, mock_exifread):
        """Testa a análise de metadados de imagem."""
        # Configurar mock para exifread
        mock_exif_tags = {
            'Image Make': 'Canon',
            'Image Model': 'EOS 5D',
            'EXIF DateTimeOriginal': '2023:01:01 12:00:00'
        }
        mock_exifread.return_value = mock_exif_tags
        
        # Configurar mock para PIL
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_img.mode = 'RGB'
        mock_img.format = 'JPEG'
        mock_img._getexif.return_value = {
            271: 'Canon',  # Make
            272: 'EOS 5D',  # Model
            306: '2023:01:01 12:00:00'  # DateTime
        }
        mock_pil_open.return_value.__enter__.return_value = mock_img
        
        # Executar função com patch adicional
        with patch.object(self.metadata_analysis, '_extract_gps_info') as mock_gps:
            mock_gps.return_value = {
                'latitude': 40.7128,
                'longitude': -74.0060,
                'google_maps_url': 'https://maps.google.com/maps?q=40.7128,-74.0060'
            }
            
            result = self.metadata_analysis.analyze_image(self.test_image_path)
        
        # Verificar resultado
        self.assertEqual(result['file_type'], 'image')
        self.assertEqual(result['dimensions']['width'], 800)
        self.assertEqual(result['dimensions']['height'], 600)
        self.assertEqual(result['color_mode'], 'RGB')
        self.assertEqual(result['format'], 'JPEG')
        self.assertIn('exif_data', result)
        self.assertIn('gps_info', result)
        self.assertEqual(result['gps_info']['latitude'], 40.7128)
    
    @patch('modules.metadata_analysis.Document')
    def test_analyze_document(self, mock_document):
        """Testa a análise de metadados de documento."""
        # Configurar mock
        mock_doc = MagicMock()
        
        # Configurar propriedades do documento
        mock_core_properties = MagicMock()
        mock_core_properties.author = 'Autor Teste'
        mock_core_properties.title = 'Documento Teste'
        mock_core_properties.created = '2023-01-01T12:00:00Z'
        mock_core_properties.modified = '2023-01-02T12:00:00Z'
        mock_core_properties.last_modified_by = 'Modificador Teste'
        mock_doc.core_properties = mock_core_properties
        
        # Configurar parágrafos
        mock_paragraph = MagicMock()
        mock_paragraph.text = 'Texto de teste'
        mock_doc.paragraphs = [mock_paragraph, mock_paragraph]
        
        # Configurar tabelas
        mock_doc.tables = [MagicMock()]
        
        # Configurar estilos
        mock_style = MagicMock()
        mock_style.name = 'Estilo Teste'
        mock_doc.styles = [mock_style]
        
        # Configurar seções
        mock_doc.sections = [MagicMock()]
        
        mock_document.return_value = mock_doc
        
        # Executar função
        result = self.metadata_analysis.analyze_document(self.test_document_path)
        
        # Verificar resultado
        self.assertEqual(result['file_type'], 'document')
        self.assertEqual(result['core_properties']['author'], 'Autor Teste')
        self.assertEqual(result['core_properties']['title'], 'Documento Teste')
        self.assertEqual(result['statistics']['paragraphs_count'], 2)
        self.assertEqual(result['statistics']['tables_count'], 1)
        self.assertEqual(result['statistics']['sections_count'], 1)
    
    @patch('modules.metadata_analysis.PdfReader')
    def test_analyze_pdf(self, mock_pdf_reader):
        """Testa a análise de metadados de PDF."""
        # Configurar mock
        mock_pdf = MagicMock()
        
        # Configurar metadados
        mock_pdf.metadata = {
            '/Author': 'Autor Teste',
            '/Creator': 'Criador Teste',
            '/Producer': 'Produtor Teste',
            '/Title': 'PDF Teste',
            '/CreationDate': 'D:20230101120000',
            '/ModDate': 'D:20230102120000'
        }
        
        # Configurar páginas
        mock_page = MagicMock()
        mock_page.__getitem__.return_value = [0, 0, 595, 842]  # MediaBox
        mock_pdf.pages = [mock_page, mock_page]
        
        # Configurar criptografia
        mock_pdf.is_encrypted = False
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Executar função
        with patch('builtins.open', MagicMock()):
            result = self.metadata_analysis.analyze_pdf(self.test_pdf_path)
        
        # Verificar resultado
        self.assertEqual(result['file_type'], 'pdf')
        self.assertEqual(result['metadata']['Author'], 'Autor Teste')
        self.assertEqual(result['metadata']['Title'], 'PDF Teste')
        self.assertEqual(result['page_count'], 2)
        self.assertFalse(result['is_encrypted'])
    
    def test_analyze_generic_file(self):
        """Testa a análise de metadados de arquivo genérico."""
        # Criar arquivo de texto para teste
        test_text_path = os.path.join(self.temp_dir, "test.txt")
        with open(test_text_path, "w") as f:
            f.write("Conteúdo de teste")
        
        # Executar função
        result = self.metadata_analysis.analyze_generic_file(test_text_path)
        
        # Verificar resultado
        self.assertEqual(result['file_type'], 'generic')
        self.assertIn('file_info', result)
        self.assertEqual(result['file_info']['file_name'], 'test.txt')
        self.assertEqual(result['file_info']['extension'], '.txt')
    
    def test_export_results_to_csv(self):
        """Testa a exportação de resultados para CSV."""
        # Adicionar alguns resultados de teste
        self.metadata_analysis.results['images'] = {
            'test_image.jpg': {
                'file_type': 'image',
                'file_name': 'test_image.jpg',
                'file_size': 1024,
                'file_size_human': '1.0 KB',
                'creation_date': '2023-01-01T12:00:00',
                'modification_date': '2023-01-02T12:00:00',
                'dimensions': {'width': 800, 'height': 600}
            }
        }
        
        # Executar função
        csv_file = self.metadata_analysis.export_results_to_csv('images')
        
        # Verificar resultado
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(csv_file.endswith('.csv'))


if __name__ == '__main__':
    unittest.main()
