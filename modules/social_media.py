#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Busca em Redes Sociais para Ferramenta OSINT
Este módulo permite coletar informações de perfis e publicações em diferentes redes sociais.
"""

import os
import json
import time
import logging
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('osint_social_media')

class SocialMediaOSINT:
    """Classe principal para busca de informações em redes sociais."""
    
    def __init__(self, output_dir: str = "resultados"):
        """
        Inicializa o módulo de busca em redes sociais.
        
        Args:
            output_dir: Diretório para salvar os resultados
        """
        self.output_dir = output_dir
        self._setup_directories()
        self.results = {}
        logger.info("Módulo de busca em redes sociais inicializado")
    
    def _setup_directories(self):
        """Cria os diretórios necessários para armazenar os resultados."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Diretório de resultados criado: {self.output_dir}")
        
        # Diretórios específicos para cada rede social
        for network in ['twitter', 'instagram', 'facebook']:
            network_dir = os.path.join(self.output_dir, network)
            if not os.path.exists(network_dir):
                os.makedirs(network_dir)
                logger.info(f"Diretório para {network} criado: {network_dir}")
    
    def search_twitter(self, username: str, max_tweets: int = 100) -> Dict[str, Any]:
        """
        Busca informações de um perfil do Twitter e seus tweets recentes.
        
        Args:
            username: Nome de usuário do Twitter (sem @)
            max_tweets: Número máximo de tweets a serem coletados
            
        Returns:
            Dicionário com informações do perfil e tweets
        """
        try:
            import tweepy
            
            logger.info(f"Iniciando busca no Twitter para usuário: {username}")
            
            # Verificar se as credenciais da API estão disponíveis
            # Nota: Em uma implementação real, estas credenciais seriam armazenadas de forma segura
            # e não diretamente no código
            api_key = os.environ.get("TWITTER_API_KEY")
            api_secret = os.environ.get("TWITTER_API_SECRET")
            access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
            access_secret = os.environ.get("TWITTER_ACCESS_SECRET")
            
            if not all([api_key, api_secret, access_token, access_secret]):
                logger.warning("Credenciais da API do Twitter não encontradas. Usando modo simulado.")
                # Modo simulado para demonstração
                profile_data = self._simulate_twitter_profile(username)
                self._save_results('twitter', username, profile_data)
                return profile_data
            
            # Configuração da API do Twitter
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            
            # Obter informações do perfil
            user = api.get_user(screen_name=username)
            
            # Obter tweets recentes
            tweets = []
            for tweet in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended").items(max_tweets):
                tweets.append({
                    'id': tweet.id,
                    'created_at': tweet.created_at.isoformat(),
                    'text': tweet.full_text,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'hashtags': [h['text'] for h in tweet.entities.get('hashtags', [])],
                    'mentions': [m['screen_name'] for m in tweet.entities.get('user_mentions', [])]
                })
            
            # Compilar resultados
            results = {
                'profile': {
                    'id': user.id,
                    'name': user.name,
                    'screen_name': user.screen_name,
                    'description': user.description,
                    'location': user.location,
                    'url': user.url,
                    'followers_count': user.followers_count,
                    'friends_count': user.friends_count,
                    'listed_count': user.listed_count,
                    'created_at': user.created_at.isoformat(),
                    'verified': user.verified,
                    'statuses_count': user.statuses_count,
                    'profile_image_url': user.profile_image_url_https
                },
                'tweets': tweets,
                'collection_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            self._save_results('twitter', username, results)
            
            logger.info(f"Busca no Twitter concluída para {username}. Coletados {len(tweets)} tweets.")
            return results
            
        except ImportError:
            logger.error("Biblioteca Tweepy não está instalada.")
            return {"error": "Biblioteca Tweepy não está instalada."}
        except Exception as e:
            logger.error(f"Erro ao buscar informações do Twitter: {str(e)}")
            return {"error": str(e)}
    
    def search_instagram(self, username: str, max_posts: int = 20) -> Dict[str, Any]:
        """
        Busca informações de um perfil do Instagram e seus posts recentes.
        
        Args:
            username: Nome de usuário do Instagram
            max_posts: Número máximo de posts a serem coletados
            
        Returns:
            Dicionário com informações do perfil e posts
        """
        try:
            import instaloader
            
            logger.info(f"Iniciando busca no Instagram para usuário: {username}")
            
            # Inicializar o Instaloader
            L = instaloader.Instaloader()
            
            # Tentar login se as credenciais estiverem disponíveis
            insta_username = os.environ.get("INSTAGRAM_USERNAME")
            insta_password = os.environ.get("INSTAGRAM_PASSWORD")
            
            if insta_username and insta_password:
                try:
                    L.login(insta_username, insta_password)
                    logger.info("Login no Instagram realizado com sucesso")
                except Exception as e:
                    logger.warning(f"Falha no login do Instagram: {str(e)}. Continuando sem login.")
            else:
                logger.warning("Credenciais do Instagram não encontradas. Continuando sem login.")
            
            # Obter perfil
            profile = instaloader.Profile.from_username(L.context, username)
            
            # Coletar informações do perfil
            profile_data = {
                'username': profile.username,
                'user_id': profile.userid,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers_count': profile.followers,
                'following_count': profile.followees,
                'is_private': profile.is_private,
                'is_verified': profile.is_verified,
                'media_count': profile.mediacount,
                'profile_pic_url': profile.profile_pic_url,
                'external_url': profile.external_url
            }
            
            # Coletar posts recentes
            posts = []
            count = 0
            
            for post in profile.get_posts():
                if count >= max_posts:
                    break
                
                post_data = {
                    'id': post.shortcode,
                    'date': post.date_local.isoformat(),
                    'caption': post.caption if post.caption else "",
                    'likes': post.likes,
                    'comments': post.comments,
                    'url': f"https://www.instagram.com/p/{post.shortcode}/",
                    'is_video': post.is_video,
                    'location': post.location.name if post.location else None,
                    'hashtags': list(post.caption_hashtags),
                    'mentioned_users': list(post.caption_mentions)
                }
                
                posts.append(post_data)
                count += 1
            
            # Compilar resultados
            results = {
                'profile': profile_data,
                'posts': posts,
                'collection_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            self._save_results('instagram', username, results)
            
            logger.info(f"Busca no Instagram concluída para {username}. Coletados {len(posts)} posts.")
            return results
            
        except ImportError:
            logger.error("Biblioteca Instaloader não está instalada.")
            return {"error": "Biblioteca Instaloader não está instalada."}
        except Exception as e:
            logger.error(f"Erro ao buscar informações do Instagram: {str(e)}")
            return {"error": str(e)}
    
    def search_facebook(self, username: str, max_posts: int = 20) -> Dict[str, Any]:
        """
        Busca informações de um perfil do Facebook e seus posts recentes.
        
        Args:
            username: Nome de usuário ou ID do Facebook
            max_posts: Número máximo de posts a serem coletados
            
        Returns:
            Dicionário com informações do perfil e posts
        """
        try:
            from facebook_scraper import get_profile, get_posts
            
            logger.info(f"Iniciando busca no Facebook para usuário: {username}")
            
            # Obter informações do perfil
            try:
                profile_data = get_profile(username)
            except Exception as e:
                logger.error(f"Erro ao obter perfil do Facebook: {str(e)}")
                # Modo simulado para demonstração
                profile_data = self._simulate_facebook_profile(username)
            
            # Obter posts recentes
            posts = []
            try:
                for i, post in enumerate(get_posts(username, pages=max_posts//10 + 1)):
                    if i >= max_posts:
                        break
                    
                    post_data = {
                        'post_id': post.get('post_id'),
                        'text': post.get('text'),
                        'time': post.get('time').isoformat() if post.get('time') else None,
                        'likes': post.get('likes'),
                        'comments': post.get('comments'),
                        'shares': post.get('shares'),
                        'post_url': post.get('post_url'),
                        'is_video': post.get('is_video', False),
                        'image_url': post.get('image'),
                        'video_url': post.get('video'),
                        'video_thumbnail_url': post.get('video_thumbnail')
                    }
                    
                    posts.append(post_data)
            except Exception as e:
                logger.error(f"Erro ao obter posts do Facebook: {str(e)}")
                # Modo simulado para demonstração
                posts = self._simulate_facebook_posts(username, max_posts)
            
            # Compilar resultados
            results = {
                'profile': profile_data,
                'posts': posts,
                'collection_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            self._save_results('facebook', username, results)
            
            logger.info(f"Busca no Facebook concluída para {username}. Coletados {len(posts)} posts.")
            return results
            
        except ImportError:
            logger.error("Biblioteca facebook-scraper não está instalada.")
            return {"error": "Biblioteca facebook-scraper não está instalada."}
        except Exception as e:
            logger.error(f"Erro ao buscar informações do Facebook: {str(e)}")
            return {"error": str(e)}
    
    def visualize_social_connections(self, data: Dict[str, Any], network_type: str, username: str) -> str:
        """
        Cria uma visualização das conexões sociais do usuário.
        
        Args:
            data: Dados coletados da rede social
            network_type: Tipo de rede social ('twitter', 'instagram', 'facebook')
            username: Nome de usuário
            
        Returns:
            Caminho para o arquivo de imagem gerado
        """
        try:
            logger.info(f"Criando visualização de conexões para {username} no {network_type}")
            
            # Criar grafo
            G = nx.Graph()
            
            # Adicionar nó central (usuário)
            G.add_node(username, type='user')
            
            if network_type == 'twitter':
                # Adicionar menções de tweets como conexões
                for tweet in data.get('tweets', []):
                    for mention in tweet.get('mentions', []):
                        G.add_node(mention, type='mention')
                        G.add_edge(username, mention)
                
                # Adicionar hashtags como nós
                for tweet in data.get('tweets', []):
                    for hashtag in tweet.get('hashtags', []):
                        hashtag_node = f"#{hashtag}"
                        G.add_node(hashtag_node, type='hashtag')
                        G.add_edge(username, hashtag_node)
            
            elif network_type == 'instagram':
                # Adicionar menções de posts como conexões
                for post in data.get('posts', []):
                    for mention in post.get('mentioned_users', []):
                        G.add_node(mention, type='mention')
                        G.add_edge(username, mention)
                
                # Adicionar hashtags como nós
                for post in data.get('posts', []):
                    for hashtag in post.get('hashtags', []):
                        hashtag_node = f"#{hashtag}"
                        G.add_node(hashtag_node, type='hashtag')
                        G.add_edge(username, hashtag_node)
            
            elif network_type == 'facebook':
                # Para Facebook, podemos extrair menções do texto dos posts
                for post in data.get('posts', []):
                    text = post.get('text', '')
                    if text:
                        # Extrair menções simples (pode ser melhorado com regex)
                        words = text.split()
                        for word in words:
                            if word.startswith('@'):
                                mention = word[1:]
                                G.add_node(mention, type='mention')
                                G.add_edge(username, mention)
            
            # Verificar se há nós suficientes para visualização
            if len(G.nodes) <= 1:
                logger.warning(f"Não há conexões suficientes para visualizar para {username}")
                return ""
            
            # Definir cores para os nós
            node_colors = []
            for node in G.nodes:
                node_type = G.nodes[node].get('type')
                if node_type == 'user':
                    node_colors.append('red')
                elif node_type == 'mention':
                    node_colors.append('blue')
                else:  # hashtag
                    node_colors.append('green')
            
            # Criar visualização
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, seed=42)
            nx.draw_networkx(
                G, pos, 
                node_color=node_colors,
                node_size=500,
                font_size=10,
                font_weight='bold',
                with_labels=True,
                alpha=0.8
            )
            
            # Adicionar legenda
            plt.text(0.01, 0.01, f"Vermelho: Usuário\nAzul: Menções\nVerde: Hashtags", 
                    transform=plt.gca().transAxes, fontsize=10, 
                    bbox=dict(facecolor='white', alpha=0.8))
            
            plt.title(f"Conexões sociais de {username} no {network_type.capitalize()}")
            plt.axis('off')
            
            # Salvar imagem
            output_file = os.path.join(
                self.output_dir, 
                network_type, 
                f"{username}_connections.png"
            )
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Visualização de conexões salva em: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Erro ao criar visualização: {str(e)}")
            return ""
    
    def _save_results(self, network: str, username: str, data: Dict[str, Any]):
        """
        Salva os resultados em um arquivo JSON.
        
        Args:
            network: Nome da rede social
            username: Nome de usuário
            data: Dados a serem salvos
        """
        output_file = os.path.join(
            self.output_dir, 
            network, 
            f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Resultados salvos em: {output_file}")
        
        # Armazenar resultados na memória
        if network not in self.results:
            self.results[network] = {}
        
        self.results[network][username] = data
    
    def _simulate_twitter_profile(self, username: str) -> Dict[str, Any]:
        """
        Simula dados de perfil do Twitter para demonstração.
        
        Args:
            username: Nome de usuário
            
        Returns:
            Dados simulados do perfil
        """
        logger.info(f"Simulando dados do Twitter para {username}")
        
        # Gerar tweets simulados
        tweets = []
        for i in range(10):
            tweets.append({
                'id': f"tweet_{i}",
                'created_at': (datetime.now().replace(day=datetime.now().day - i)).isoformat(),
                'text': f"Este é um tweet simulado #{i} de {username}. #osint #simulacao",
                'retweet_count': i * 5,
                'favorite_count': i * 10,
                'hashtags': ['osint', 'simulacao'],
                'mentions': [f"usuario{j}" for j in range(i % 3)]
            })
        
        return {
            'profile': {
                'id': f"id_{username}",
                'name': f"Nome de {username}",
                'screen_name': username,
                'description': f"Este é um perfil simulado para demonstração da ferramenta OSINT",
                'location': "Brasil",
                'url': f"https://twitter.com/{username}",
                'followers_count': 1000,
                'friends_count': 500,
                'listed_count': 10,
                'created_at': "2020-01-01T00:00:00",
                'verified': False,
                'statuses_count': 1500,
                'profile_image_url': f"https://example.com/{username}.jpg"
            },
            'tweets': tweets,
            'collection_date': datetime.now().isoformat(),
            'simulated': True
        }
    
    def _simulate_facebook_profile(self, username: str) -> Dict[str, Any]:
        """
        Simula dados de perfil do Facebook para demonstração.
        
        Args:
            username: Nome de usuário
            
        Returns:
            Dados simulados do perfil
        """
        logger.info(f"Simulando dados do Facebook para {username}")
        
        return {
            'id': f"id_{username}",
            'name': f"Nome de {username}",
            'user_name': username,
            'user_id': f"id_{username}",
            'profile_url': f"https://facebook.com/{username}",
            'cover_photo': f"https://example.com/cover_{username}.jpg",
            'profile_picture': f"https://example.com/{username}.jpg",
            'work': [{"employer": "Empresa Simulada"}],
            'education': [{"school": "Universidade Simulada"}],
            'location': "Brasil",
            'hometown': "São Paulo",
            'relationship_status': "Solteiro(a)",
            'following': 500,
            'followers': 1000,
            'likes': 200,
            'friends_count': 500,
            'simulated': True
        }
    
    def _simulate_facebook_posts(self, username: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Simula posts do Facebook para demonstração.
        
        Args:
            username: Nome de usuário
            count: Número de posts a serem simulados
            
        Returns:
            Lista de posts simulados
        """
        logger.info(f"Simulando posts do Facebook para {username}")
        
        posts = []
        for i in range(count):
            posts.append({
                'post_id': f"post_{i}",
                'text': f"Este é um post simulado #{i} de {username}. #osint #simulacao",
                'time': (datetime.now().replace(day=datetime.now().day - i)).isoformat(),
                'likes': i * 10,
                'comments': i * 3,
                'shares': i * 2,
                'post_url': f"https://facebook.com/{username}/posts/{i}",
                'is_video': i % 3 == 0,
                'image_url': None if i % 3 == 0 else f"https://example.com/image_{i}.jpg",
                'video_url': f"https://example.com/video_{i}.mp4" if i % 3 == 0 else None,
                'video_thumbnail_url': f"https://example.com/thumb_{i}.jpg" if i % 3 == 0 else None,
                'simulated': True
            })
        
        return posts


# Função para demonstração do módulo
def demo():
    """Função de demonstração do módulo de busca em redes sociais."""
    osint = SocialMediaOSINT(output_dir="resultados_osint")
    
    # Demonstração com Twitter
    print("Demonstração de busca no Twitter:")
    twitter_results = osint.search_twitter("exemplo_usuario")
    print(f"Perfil: {twitter_results['profile']['name']}")
    print(f"Seguidores: {twitter_results['profile']['followers_count']}")
    print(f"Tweets coletados: {len(twitter_results['tweets'])}")
    
    # Visualização de conexões
    viz_file = osint.visualize_social_connections(twitter_results, 'twitter', "exemplo_usuario")
    if viz_file:
        print(f"Visualização salva em: {viz_file}")
    
    print("\nDemonstração concluída!")


if __name__ == "__main__":
    demo()
