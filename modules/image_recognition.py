#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Reconhecimento de Imagens para Ferramenta OSINT
Este módulo permite analisar imagens para reconhecimento facial e extração de informações visuais.
"""

import os
import cv2
import json
import logging
import numpy as np
from PIL import Image
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('osint_image_recognition')

class ImageRecognitionOSINT:
    """Classe principal para reconhecimento de imagens."""
    
    def __init__(self, output_dir: str = "resultados"):
        """
        Inicializa o módulo de reconhecimento de imagens.
        
        Args:
            output_dir: Diretório para salvar os resultados
        """
        self.output_dir = output_dir
        self._setup_directories()
        self.results = {}
        
        # Carregar classificadores do OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        logger.info("Módulo de reconhecimento de imagens inicializado")
    
    def _setup_directories(self):
        """Cria os diretórios necessários para armazenar os resultados."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Diretório de resultados criado: {self.output_dir}")
        
        # Diretórios específicos para cada tipo de análise
        for analysis_type in ['faces', 'objects', 'scenes', 'processed']:
            type_dir = os.path.join(self.output_dir, analysis_type)
            if not os.path.exists(type_dir):
                os.makedirs(type_dir)
                logger.info(f"Diretório para {analysis_type} criado: {type_dir}")
    
    def detect_faces(self, image_path: str, save_result: bool = True) -> Dict[str, Any]:
        """
        Detecta faces em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            save_result: Se True, salva a imagem com as faces marcadas
            
        Returns:
            Dicionário com informações sobre as faces detectadas
        """
        try:
            logger.info(f"Detectando faces na imagem: {image_path}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(image_path):
                logger.error(f"Arquivo não encontrado: {image_path}")
                return {"error": f"Arquivo não encontrado: {image_path}"}
            
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Não foi possível carregar a imagem: {image_path}")
                return {"error": f"Não foi possível carregar a imagem: {image_path}"}
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detectar faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Processar faces detectadas
            face_data = []
            for i, (x, y, w, h) in enumerate(faces):
                face_info = {
                    'id': i,
                    'position': {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h)
                    },
                    'confidence': 1.0  # OpenCV Haar Cascade não fornece confiança
                }
                
                # Extrair região da face
                face_roi = gray[y:y+h, x:x+w]
                
                # Detectar olhos
                eyes = self.eye_cascade.detectMultiScale(face_roi)
                face_info['eyes'] = len(eyes)
                
                # Detectar sorriso
                smile = self.smile_cascade.detectMultiScale(
                    face_roi,
                    scaleFactor=1.7,
                    minNeighbors=22,
                    minSize=(25, 25)
                )
                face_info['smiling'] = len(smile) > 0
                
                face_data.append(face_info)
                
                # Desenhar retângulo na imagem
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(image, f"Face {i}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            
            # Salvar imagem com faces marcadas
            result_image_path = ""
            if save_result and len(faces) > 0:
                base_name = os.path.basename(image_path)
                name, ext = os.path.splitext(base_name)
                result_image_path = os.path.join(
                    self.output_dir,
                    'processed',
                    f"{name}_faces{ext}"
                )
                cv2.imwrite(result_image_path, image)
                logger.info(f"Imagem com faces marcadas salva em: {result_image_path}")
            
            # Compilar resultados
            results = {
                'image_path': image_path,
                'faces_detected': len(faces),
                'faces': face_data,
                'result_image': result_image_path,
                'analysis_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            if save_result:
                self._save_results('faces', os.path.basename(image_path), results)
            
            logger.info(f"Detecção de faces concluída. Encontradas {len(faces)} faces.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao detectar faces: {str(e)}")
            return {"error": str(e)}
    
    def detect_objects(self, image_path: str, save_result: bool = True) -> Dict[str, Any]:
        """
        Detecta objetos em uma imagem usando OpenCV DNN.
        
        Args:
            image_path: Caminho para a imagem
            save_result: Se True, salva a imagem com os objetos marcados
            
        Returns:
            Dicionário com informações sobre os objetos detectados
        """
        try:
            logger.info(f"Detectando objetos na imagem: {image_path}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(image_path):
                logger.error(f"Arquivo não encontrado: {image_path}")
                return {"error": f"Arquivo não encontrado: {image_path}"}
            
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Não foi possível carregar a imagem: {image_path}")
                return {"error": f"Não foi possível carregar a imagem: {image_path}"}
            
            # Como não temos modelos pré-treinados disponíveis, vamos simular a detecção de objetos
            # Em uma implementação real, usaríamos modelos como YOLO, SSD ou Faster R-CNN
            
            # Simular detecção de objetos
            object_data = self._simulate_object_detection(image)
            
            # Desenhar objetos na imagem
            for obj in object_data:
                x, y, w, h = obj['position']['x'], obj['position']['y'], obj['position']['width'], obj['position']['height']
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                label = f"{obj['class']} ({obj['confidence']:.2f})"
                cv2.putText(image, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Salvar imagem com objetos marcados
            result_image_path = ""
            if save_result and len(object_data) > 0:
                base_name = os.path.basename(image_path)
                name, ext = os.path.splitext(base_name)
                result_image_path = os.path.join(
                    self.output_dir,
                    'processed',
                    f"{name}_objects{ext}"
                )
                cv2.imwrite(result_image_path, image)
                logger.info(f"Imagem com objetos marcados salva em: {result_image_path}")
            
            # Compilar resultados
            results = {
                'image_path': image_path,
                'objects_detected': len(object_data),
                'objects': object_data,
                'result_image': result_image_path,
                'analysis_date': datetime.now().isoformat(),
                'simulated': True  # Indicador de que os dados são simulados
            }
            
            # Salvar resultados
            if save_result:
                self._save_results('objects', os.path.basename(image_path), results)
            
            logger.info(f"Detecção de objetos concluída. Encontrados {len(object_data)} objetos.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao detectar objetos: {str(e)}")
            return {"error": str(e)}
    
    def analyze_image_colors(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa as cores predominantes em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dicionário com informações sobre as cores da imagem
        """
        try:
            logger.info(f"Analisando cores da imagem: {image_path}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(image_path):
                logger.error(f"Arquivo não encontrado: {image_path}")
                return {"error": f"Arquivo não encontrado: {image_path}"}
            
            # Carregar imagem com PIL para melhor manipulação de cores
            pil_image = Image.open(image_path)
            
            # Converter para RGB se for outro modo
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Redimensionar para acelerar o processamento
            pil_image.thumbnail((200, 200))
            
            # Converter para array numpy
            np_image = np.array(pil_image)
            
            # Calcular histograma de cores
            hist_r = np.histogram(np_image[:,:,0], bins=8, range=(0, 256))[0]
            hist_g = np.histogram(np_image[:,:,1], bins=8, range=(0, 256))[0]
            hist_b = np.histogram(np_image[:,:,2], bins=8, range=(0, 256))[0]
            
            # Normalizar histogramas
            total_pixels = np_image.shape[0] * np_image.shape[1]
            hist_r = hist_r / total_pixels
            hist_g = hist_g / total_pixels
            hist_b = hist_b / total_pixels
            
            # Calcular cor média
            avg_color = np_image.mean(axis=0).mean(axis=0)
            
            # Calcular brilho médio
            brightness = np.mean(np.mean(np_image, axis=0), axis=0).mean()
            
            # Determinar se a imagem é clara ou escura
            is_dark = brightness < 128
            
            # Compilar resultados
            results = {
                'image_path': image_path,
                'average_color': {
                    'r': int(avg_color[0]),
                    'g': int(avg_color[1]),
                    'b': int(avg_color[2]),
                    'hex': f"#{int(avg_color[0]):02x}{int(avg_color[1]):02x}{int(avg_color[2]):02x}"
                },
                'brightness': float(brightness),
                'is_dark': bool(is_dark),
                'color_distribution': {
                    'r': hist_r.tolist(),
                    'g': hist_g.tolist(),
                    'b': hist_b.tolist()
                },
                'analysis_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            self._save_results('scenes', os.path.basename(image_path), results)
            
            logger.info(f"Análise de cores concluída para: {image_path}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao analisar cores: {str(e)}")
            return {"error": str(e)}
    
    def compare_faces(self, image_path1: str, image_path2: str, save_result: bool = True) -> Dict[str, Any]:
        """
        Compara faces em duas imagens.
        
        Args:
            image_path1: Caminho para a primeira imagem
            image_path2: Caminho para a segunda imagem
            save_result: Se True, salva a imagem com as correspondências marcadas
            
        Returns:
            Dicionário com informações sobre a comparação de faces
        """
        try:
            logger.info(f"Comparando faces entre: {image_path1} e {image_path2}")
            
            # Verificar se os arquivos existem
            if not os.path.exists(image_path1):
                logger.error(f"Arquivo não encontrado: {image_path1}")
                return {"error": f"Arquivo não encontrado: {image_path1}"}
            
            if not os.path.exists(image_path2):
                logger.error(f"Arquivo não encontrado: {image_path2}")
                return {"error": f"Arquivo não encontrado: {image_path2}"}
            
            # Detectar faces nas duas imagens
            faces1 = self.detect_faces(image_path1, save_result=False)
            faces2 = self.detect_faces(image_path2, save_result=False)
            
            if 'error' in faces1:
                return faces1
            
            if 'error' in faces2:
                return faces2
            
            # Como não temos face_recognition disponível, vamos simular a comparação
            # Em uma implementação real, usaríamos face_recognition ou DeepFace
            
            # Simular comparação de faces
            comparison_results = self._simulate_face_comparison(faces1, faces2)
            
            # Compilar resultados
            results = {
                'image_path1': image_path1,
                'image_path2': image_path2,
                'faces_in_image1': faces1['faces_detected'],
                'faces_in_image2': faces2['faces_detected'],
                'matches': comparison_results['matches'],
                'match_details': comparison_results['match_details'],
                'analysis_date': datetime.now().isoformat(),
                'simulated': True  # Indicador de que os dados são simulados
            }
            
            # Salvar resultados
            if save_result:
                result_name = f"{os.path.basename(image_path1)}_vs_{os.path.basename(image_path2)}"
                self._save_results('faces', result_name, results)
            
            logger.info(f"Comparação de faces concluída. Encontradas {results['matches']} correspondências.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao comparar faces: {str(e)}")
            return {"error": str(e)}
    
    def extract_scene_info(self, image_path: str) -> Dict[str, Any]:
        """
        Extrai informações sobre a cena em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dicionário com informações sobre a cena
        """
        try:
            logger.info(f"Extraindo informações de cena da imagem: {image_path}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(image_path):
                logger.error(f"Arquivo não encontrado: {image_path}")
                return {"error": f"Arquivo não encontrado: {image_path}"}
            
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Não foi possível carregar a imagem: {image_path}")
                return {"error": f"Não foi possível carregar a imagem: {image_path}"}
            
            # Obter dimensões da imagem
            height, width, channels = image.shape
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calcular histograma de gradientes
            gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
            gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
            mag, ang = cv2.cartToPolar(gx, gy)
            
            # Calcular estatísticas de gradiente
            gradient_mean = np.mean(mag)
            gradient_std = np.std(mag)
            
            # Determinar se a imagem é interna ou externa (simulação)
            # Em uma implementação real, usaríamos um modelo de classificação
            is_indoor = gradient_mean < 20  # Valor arbitrário para simulação
            
            # Determinar se é dia ou noite (simulação)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            brightness = np.mean(hsv[:,:,2])
            is_night = brightness < 100  # Valor arbitrário para simulação
            
            # Simular detecção de cena
            scene_info = self._simulate_scene_detection(image)
            
            # Compilar resultados
            results = {
                'image_path': image_path,
                'dimensions': {
                    'width': width,
                    'height': height,
                    'channels': channels
                },
                'scene_type': scene_info['scene_type'],
                'scene_attributes': scene_info['attributes'],
                'is_indoor': bool(is_indoor),
                'is_night': bool(is_night),
                'gradient_statistics': {
                    'mean': float(gradient_mean),
                    'std': float(gradient_std)
                },
                'analysis_date': datetime.now().isoformat(),
                'simulated': True  # Indicador de que os dados são simulados
            }
            
            # Salvar resultados
            self._save_results('scenes', os.path.basename(image_path), results)
            
            logger.info(f"Extração de informações de cena concluída para: {image_path}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações de cena: {str(e)}")
            return {"error": str(e)}
    
    def _simulate_object_detection(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Simula a detecção de objetos em uma imagem.
        
        Args:
            image: Imagem em formato numpy array
            
        Returns:
            Lista de objetos detectados
        """
        height, width, _ = image.shape
        
        # Classes comuns em detecção de objetos
        classes = ['pessoa', 'carro', 'cadeira', 'mesa', 'computador', 'telefone', 'livro', 'garrafa']
        
        # Gerar detecções aleatórias
        num_objects = np.random.randint(1, 5)
        objects = []
        
        for i in range(num_objects):
            # Gerar posição aleatória
            obj_width = np.random.randint(width // 10, width // 3)
            obj_height = np.random.randint(height // 10, height // 3)
            obj_x = np.random.randint(0, width - obj_width)
            obj_y = np.random.randint(0, height - obj_height)
            
            # Selecionar classe aleatória
            obj_class = np.random.choice(classes)
            
            # Gerar confiança aleatória
            confidence = np.random.uniform(0.6, 0.95)
            
            objects.append({
                'id': i,
                'class': obj_class,
                'confidence': float(confidence),
                'position': {
                    'x': int(obj_x),
                    'y': int(obj_y),
                    'width': int(obj_width),
                    'height': int(obj_height)
                }
            })
        
        return objects
    
    def _simulate_face_comparison(self, faces1: Dict[str, Any], faces2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula a comparação de faces entre duas imagens.
        
        Args:
            faces1: Resultados da detecção de faces na primeira imagem
            faces2: Resultados da detecção de faces na segunda imagem
            
        Returns:
            Dicionário com resultados da comparação
        """
        # Determinar número de correspondências (simulação)
        max_possible_matches = min(faces1['faces_detected'], faces2['faces_detected'])
        num_matches = np.random.randint(0, max_possible_matches + 1)
        
        # Gerar detalhes das correspondências
        match_details = []
        
        for i in range(num_matches):
            # Selecionar faces aleatórias das duas imagens
            face1_idx = np.random.randint(0, faces1['faces_detected'])
            face2_idx = np.random.randint(0, faces2['faces_detected'])
            
            # Gerar distância aleatória (menor é melhor)
            distance = np.random.uniform(0.1, 0.6)
            
            # Determinar se é uma correspondência
            is_match = distance < 0.5  # Valor arbitrário para simulação
            
            match_details.append({
                'face1_id': face1_idx,
                'face2_id': face2_idx,
                'distance': float(distance),
                'is_match': bool(is_match),
                'confidence': float(1.0 - distance)
            })
        
        return {
            'matches': num_matches,
            'match_details': match_details
        }
    
    def _simulate_scene_detection(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Simula a detecção de cena em uma imagem.
        
        Args:
            image: Imagem em formato numpy array
            
        Returns:
            Dicionário com informações da cena
        """
        # Tipos de cena comuns
        scene_types = [
            'praia', 'montanha', 'floresta', 'cidade', 'escritório',
            'sala de estar', 'cozinha', 'quarto', 'rua', 'parque'
        ]
        
        # Atributos de cena comuns
        scene_attributes = [
            'ensolarado', 'nublado', 'chuvoso', 'noturno', 'diurno',
            'interno', 'externo', 'natural', 'urbano', 'rural',
            'movimentado', 'tranquilo', 'colorido', 'monocromático'
        ]
        
        # Selecionar tipo de cena aleatório
        scene_type = np.random.choice(scene_types)
        
        # Selecionar atributos aleatórios
        num_attributes = np.random.randint(2, 5)
        attributes = np.random.choice(scene_attributes, size=num_attributes, replace=False).tolist()
        
        return {
            'scene_type': scene_type,
            'attributes': attributes
        }
    
    def _save_results(self, analysis_type: str, identifier: str, data: Dict[str, Any]):
        """
        Salva os resultados em um arquivo JSON.
        
        Args:
            analysis_type: Tipo de análise ('faces', 'objects', 'scenes')
            identifier: Identificador único para os resultados
            data: Dados a serem salvos
        """
        output_file = os.path.join(
            self.output_dir, 
            analysis_type, 
            f"{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Resultados salvos em: {output_file}")
        
        # Armazenar resultados na memória
        if analysis_type not in self.results:
            self.results[analysis_type] = {}
        
        self.results[analysis_type][identifier] = data


# Função para demonstração do módulo
def demo():
    """Função de demonstração do módulo de reconhecimento de imagens."""
    osint = ImageRecognitionOSINT(output_dir="resultados_osint")
    
    # Criar uma imagem de teste
    test_image_path = os.path.join(osint.output_dir, "test_image.jpg")
    
    # Criar uma imagem simples com um retângulo (simulando um rosto)
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img.fill(200)  # Fundo cinza claro
    cv2.rectangle(img, (100, 100), (200, 200), (0, 0, 255), -1)  # Retângulo vermelho
    cv2.imwrite(test_image_path, img)
    
    # Demonstração de detecção de faces
    print("Demonstração de detecção de faces:")
    face_results = osint.detect_faces(test_image_path)
    print(f"Faces detectadas: {face_results['faces_detected']}")
    
    # Demonstração de detecção de objetos
    print("\nDemonstração de detecção de objetos:")
    object_results = osint.detect_objects(test_image_path)
    print(f"Objetos detectados: {object_results['objects_detected']}")
    
    # Demonstração de análise de cores
    print("\nDemonstração de análise de cores:")
    color_results = osint.analyze_image_colors(test_image_path)
    print(f"Cor média: {color_results['average_color']['hex']}")
    print(f"Brilho: {color_results['brightness']}")
    
    # Demonstração de extração de informações de cena
    print("\nDemonstração de extração de informações de cena:")
    scene_results = osint.extract_scene_info(test_image_path)
    print(f"Tipo de cena: {scene_results['scene_type']}")
    print(f"Atributos: {', '.join(scene_results['scene_attributes'])}")
    
    print("\nDemonstração concluída!")


if __name__ == "__main__":
    demo()
