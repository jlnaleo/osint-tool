#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Busca de E-mails e Informações de Contato para Ferramenta OSINT
Este módulo permite coletar e-mails, números de telefone e outras informações de contato.
"""

import os
import re
import json
import time
import logging
import requests
import socket
import whois
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Set, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('osint_contact_info')

class ContactInfoOSINT:
    """Classe principal para busca de e-mails e informações de contato."""
    
    def __init__(self, output_dir: str = "resultados"):
        """
        Inicializa o módulo de busca de e-mails e informações de contato.
        
        Args:
            output_dir: Diretório para salvar os resultados
        """
        self.output_dir = output_dir
        self._setup_directories()
        self.results = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info("Módulo de busca de e-mails e informações de contato inicializado")
    
    def _setup_directories(self):
        """Cria os diretórios necessários para armazenar os resultados."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Diretório de resultados criado: {self.output_dir}")
        
        # Diretórios específicos para cada tipo de busca
        for search_type in ['emails', 'domains', 'phones']:
            type_dir = os.path.join(self.output_dir, search_type)
            if not os.path.exists(type_dir):
                os.makedirs(type_dir)
                logger.info(f"Diretório para {search_type} criado: {type_dir}")
    
    def search_emails_from_domain(self, domain: str, max_pages: int = 5) -> Dict[str, Any]:
        """
        Busca e-mails associados a um domínio específico.
        
        Args:
            domain: Domínio para buscar e-mails (ex: 'example.com')
            max_pages: Número máximo de páginas a serem analisadas
            
        Returns:
            Dicionário com e-mails encontrados e informações relacionadas
        """
        try:
            logger.info(f"Iniciando busca de e-mails para o domínio: {domain}")
            
            # Verificar se o domínio é válido
            if not self._is_valid_domain(domain):
                logger.error(f"Domínio inválido: {domain}")
                return {"error": f"Domínio inválido: {domain}"}
            
            # Coletar e-mails do site do domínio
            site_emails = self._extract_emails_from_website(f"https://{domain}", max_pages)
            
            # Gerar possíveis padrões de e-mail
            email_patterns = self._generate_email_patterns(domain)
            
            # Compilar resultados
            results = {
                'domain': domain,
                'emails_found': list(site_emails),
                'possible_patterns': email_patterns,
                'collection_date': datetime.now().isoformat()
            }
            
            # Adicionar informações do domínio
            try:
                domain_info = self._get_domain_info(domain)
                results['domain_info'] = domain_info
            except Exception as e:
                logger.error(f"Erro ao obter informações do domínio: {str(e)}")
                results['domain_info'] = {"error": str(e)}
            
            # Salvar resultados
            self._save_results('emails', domain, results)
            
            logger.info(f"Busca de e-mails concluída para {domain}. Encontrados {len(site_emails)} e-mails.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar e-mails do domínio: {str(e)}")
            return {"error": str(e)}
    
    def search_emails_for_person(self, name: str, domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Busca possíveis e-mails para uma pessoa com base em seu nome e domínios conhecidos.
        
        Args:
            name: Nome completo da pessoa
            domains: Lista de domínios a serem verificados (opcional)
            
        Returns:
            Dicionário com possíveis e-mails para a pessoa
        """
        try:
            logger.info(f"Iniciando busca de e-mails para a pessoa: {name}")
            
            # Normalizar nome
            name = name.lower().strip()
            parts = name.split()
            
            if len(parts) < 2:
                logger.warning(f"Nome muito curto, pode gerar resultados imprecisos: {name}")
            
            # Gerar variações de nome para e-mails
            name_variations = self._generate_name_variations(parts)
            
            # Se não foram fornecidos domínios, usar alguns comuns
            if not domains:
                domains = ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com']
            
            # Gerar possíveis e-mails
            possible_emails = []
            for variation in name_variations:
                for domain in domains:
                    email = f"{variation}@{domain}"
                    possible_emails.append(email)
            
            # Compilar resultados
            results = {
                'name': name,
                'domains_checked': domains,
                'possible_emails': possible_emails,
                'name_variations': name_variations,
                'collection_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            safe_name = name.replace(' ', '_')
            self._save_results('emails', safe_name, results)
            
            logger.info(f"Busca de e-mails concluída para {name}. Gerados {len(possible_emails)} possíveis e-mails.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar e-mails para a pessoa: {str(e)}")
            return {"error": str(e)}
    
    def search_phone_info(self, phone_number: str) -> Dict[str, Any]:
        """
        Busca informações sobre um número de telefone.
        
        Args:
            phone_number: Número de telefone (com código do país)
            
        Returns:
            Dicionário com informações sobre o número de telefone
        """
        try:
            logger.info(f"Iniciando busca de informações para o telefone: {phone_number}")
            
            # Normalizar número de telefone
            normalized_number = self._normalize_phone_number(phone_number)
            
            if not normalized_number:
                logger.error(f"Número de telefone inválido: {phone_number}")
                return {"error": f"Número de telefone inválido: {phone_number}"}
            
            # Extrair informações básicas
            country_code = self._extract_country_code(normalized_number)
            
            # Simular informações do telefone (em uma implementação real, usaríamos APIs específicas)
            phone_info = self._simulate_phone_info(normalized_number, country_code)
            
            # Compilar resultados
            results = {
                'original_number': phone_number,
                'normalized_number': normalized_number,
                'phone_info': phone_info,
                'collection_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            safe_number = normalized_number.replace('+', '').replace(' ', '')
            self._save_results('phones', safe_number, results)
            
            logger.info(f"Busca de informações de telefone concluída para {phone_number}.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar informações do telefone: {str(e)}")
            return {"error": str(e)}
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """
        Analisa informações detalhadas sobre um domínio.
        
        Args:
            domain: Domínio a ser analisado
            
        Returns:
            Dicionário com informações detalhadas sobre o domínio
        """
        try:
            logger.info(f"Iniciando análise do domínio: {domain}")
            
            # Verificar se o domínio é válido
            if not self._is_valid_domain(domain):
                logger.error(f"Domínio inválido: {domain}")
                return {"error": f"Domínio inválido: {domain}"}
            
            # Obter informações WHOIS
            domain_info = self._get_domain_info(domain)
            
            # Obter endereços IP associados
            try:
                ip_addresses = socket.gethostbyname_ex(domain)[2]
            except Exception as e:
                logger.error(f"Erro ao obter IPs para o domínio: {str(e)}")
                ip_addresses = []
            
            # Verificar disponibilidade do site
            try:
                response = requests.get(f"https://{domain}", headers=self.headers, timeout=10)
                site_available = response.status_code == 200
                status_code = response.status_code
            except Exception as e:
                logger.error(f"Erro ao verificar disponibilidade do site: {str(e)}")
                site_available = False
                status_code = None
            
            # Verificar certificado SSL
            ssl_info = self._check_ssl(domain)
            
            # Compilar resultados
            results = {
                'domain': domain,
                'whois_info': domain_info,
                'ip_addresses': ip_addresses,
                'site_available': site_available,
                'status_code': status_code,
                'ssl_info': ssl_info,
                'collection_date': datetime.now().isoformat()
            }
            
            # Salvar resultados
            self._save_results('domains', domain, results)
            
            logger.info(f"Análise de domínio concluída para {domain}.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao analisar domínio: {str(e)}")
            return {"error": str(e)}
    
    def export_results_to_csv(self, search_type: str, filename: Optional[str] = None) -> str:
        """
        Exporta os resultados para um arquivo CSV.
        
        Args:
            search_type: Tipo de busca ('emails', 'domains', 'phones')
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho para o arquivo CSV gerado
        """
        try:
            if search_type not in self.results or not self.results[search_type]:
                logger.warning(f"Não há resultados para exportar do tipo: {search_type}")
                return ""
            
            if not filename:
                filename = f"{search_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            output_file = os.path.join(self.output_dir, filename)
            
            # Converter resultados para DataFrame
            if search_type == 'emails':
                data = []
                for domain, results in self.results[search_type].items():
                    for email in results.get('emails_found', []):
                        data.append({
                            'domain': domain,
                            'email': email,
                            'collection_date': results.get('collection_date')
                        })
                
                df = pd.DataFrame(data)
            
            elif search_type == 'domains':
                data = []
                for domain, results in self.results[search_type].items():
                    data.append({
                        'domain': domain,
                        'registrar': results.get('whois_info', {}).get('registrar'),
                        'creation_date': results.get('whois_info', {}).get('creation_date'),
                        'expiration_date': results.get('whois_info', {}).get('expiration_date'),
                        'site_available': results.get('site_available'),
                        'ip_addresses': ', '.join(results.get('ip_addresses', [])),
                        'collection_date': results.get('collection_date')
                    })
                
                df = pd.DataFrame(data)
            
            elif search_type == 'phones':
                data = []
                for phone, results in self.results[search_type].items():
                    data.append({
                        'phone_number': results.get('normalized_number'),
                        'country': results.get('phone_info', {}).get('country'),
                        'carrier': results.get('phone_info', {}).get('carrier'),
                        'line_type': results.get('phone_info', {}).get('line_type'),
                        'collection_date': results.get('collection_date')
                    })
                
                df = pd.DataFrame(data)
            
            # Salvar DataFrame como CSV
            df.to_csv(output_file, index=False, encoding='utf-8')
            
            logger.info(f"Resultados exportados para: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Erro ao exportar resultados para CSV: {str(e)}")
            return ""
    
    def _extract_emails_from_website(self, url: str, max_pages: int = 5) -> Set[str]:
        """
        Extrai e-mails de um website.
        
        Args:
            url: URL do website
            max_pages: Número máximo de páginas a serem analisadas
            
        Returns:
            Conjunto de e-mails encontrados
        """
        emails_found = set()
        visited_urls = set()
        urls_to_visit = [url]
        
        # Padrão para encontrar e-mails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Extrair domínio base da URL
        base_domain = self._extract_domain_from_url(url)
        
        page_count = 0
        while urls_to_visit and page_count < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
            
            visited_urls.add(current_url)
            page_count += 1
            
            try:
                logger.info(f"Analisando página: {current_url}")
                response = requests.get(current_url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    logger.warning(f"Falha ao acessar {current_url}: Status {response.status_code}")
                    continue
                
                # Extrair e-mails do conteúdo da página
                content = response.text
                found_emails = re.findall(email_pattern, content)
                emails_found.update(found_emails)
                
                # Extrair links para outras páginas do mesmo domínio
                if page_count < max_pages:
                    soup = BeautifulSoup(content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Normalizar URL
                        if href.startswith('/'):
                            full_url = f"{url.rstrip('/')}{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = f"{url.rstrip('/')}/{href.lstrip('/')}"
                        
                        # Verificar se o link é do mesmo domínio
                        link_domain = self._extract_domain_from_url(full_url)
                        if link_domain == base_domain and full_url not in visited_urls:
                            urls_to_visit.append(full_url)
                
                # Pequena pausa para não sobrecarregar o servidor
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao analisar {current_url}: {str(e)}")
        
        logger.info(f"Análise de website concluída. Encontrados {len(emails_found)} e-mails em {page_count} páginas.")
        return emails_found
    
    def _generate_email_patterns(self, domain: str) -> List[str]:
        """
        Gera padrões comuns de e-mail para um domínio.
        
        Args:
            domain: Domínio para gerar padrões
            
        Returns:
            Lista de padrões de e-mail
        """
        patterns = [
            "nome@{domain}",
            "nome.sobrenome@{domain}",
            "n.sobrenome@{domain}",
            "nomesob@{domain}",
            "nome_sobrenome@{domain}",
            "sobrenome.nome@{domain}",
            "sobrenome@{domain}",
            "nome-sobrenome@{domain}",
            "contato@{domain}",
            "info@{domain}",
            "atendimento@{domain}",
            "suporte@{domain}",
            "vendas@{domain}",
            "comercial@{domain}",
            "admin@{domain}",
            "administracao@{domain}",
            "rh@{domain}",
            "financeiro@{domain}",
            "marketing@{domain}",
            "sac@{domain}"
        ]
        
        return [pattern.format(domain=domain) for pattern in patterns]
    
    def _generate_name_variations(self, name_parts: List[str]) -> List[str]:
        """
        Gera variações de nome para busca de e-mails.
        
        Args:
            name_parts: Partes do nome (primeiro nome, sobrenomes)
            
        Returns:
            Lista de variações de nome para e-mails
        """
        variations = []
        
        if not name_parts:
            return variations
        
        # Nome simples
        first_name = name_parts[0]
        variations.append(first_name)
        
        if len(name_parts) > 1:
            # Último sobrenome
            last_name = name_parts[-1]
            variations.append(last_name)
            
            # Combinações de nome e sobrenome
            variations.append(f"{first_name}{last_name}")
            variations.append(f"{first_name}.{last_name}")
            variations.append(f"{first_name}_{last_name}")
            variations.append(f"{first_name}-{last_name}")
            variations.append(f"{first_name[0]}{last_name}")
            variations.append(f"{first_name[0]}.{last_name}")
            
            # Combinações com sobrenome primeiro
            variations.append(f"{last_name}{first_name}")
            variations.append(f"{last_name}.{first_name}")
            variations.append(f"{last_name}_{first_name}")
            
            # Se houver nome do meio
            if len(name_parts) > 2:
                middle_name = name_parts[1]
                variations.append(f"{first_name}{middle_name[0]}{last_name}")
                variations.append(f"{first_name}.{middle_name[0]}.{last_name}")
                
                # Iniciais
                initials = ''.join([part[0] for part in name_parts])
                variations.append(initials)
        
        # Remover duplicatas e retornar
        return list(set(variations))
    
    def _normalize_phone_number(self, phone_number: str) -> str:
        """
        Normaliza um número de telefone para formato internacional.
        
        Args:
            phone_number: Número de telefone a ser normalizado
            
        Returns:
            Número de telefone normalizado
        """
        # Remover caracteres não numéricos
        digits_only = re.sub(r'\D', '', phone_number)
        
        # Se começar com 0, remover
        if digits_only.startswith('0'):
            digits_only = digits_only[1:]
        
        # Se não tiver código de país e for do Brasil, adicionar +55
        if len(digits_only) <= 11 and not phone_number.startswith('+'):
            digits_only = f"55{digits_only}"
        
        # Formatar com o símbolo +
        if not digits_only.startswith('00') and not phone_number.startswith('+'):
            formatted = f"+{digits_only}"
        else:
            # Se começar com 00 (código de discagem internacional), substituir por +
            if digits_only.startswith('00'):
                formatted = f"+{digits_only[2:]}"
            else:
                formatted = digits_only
        
        return formatted
    
    def _extract_country_code(self, phone_number: str) -> str:
        """
        Extrai o código do país de um número de telefone.
        
        Args:
            phone_number: Número de telefone normalizado
            
        Returns:
            Código do país
        """
        # Remover o símbolo + se presente
        if phone_number.startswith('+'):
            number = phone_number[1:]
        else:
            number = phone_number
        
        # Códigos de país comuns
        country_codes = {
            '1': 'Estados Unidos/Canadá',
            '55': 'Brasil',
            '351': 'Portugal',
            '34': 'Espanha',
            '33': 'França',
            '44': 'Reino Unido',
            '49': 'Alemanha',
            '39': 'Itália',
            '81': 'Japão',
            '86': 'China',
            '7': 'Rússia'
        }
        
        # Verificar códigos de país
        for code, country in country_codes.items():
            if number.startswith(code):
                return code
        
        return "Desconhecido"
    
    def _simulate_phone_info(self, phone_number: str, country_code: str) -> Dict[str, str]:
        """
        Simula informações de um número de telefone para demonstração.
        
        Args:
            phone_number: Número de telefone normalizado
            country_code: Código do país
            
        Returns:
            Informações simuladas do telefone
        """
        # Mapeamento de códigos de país para nomes de países
        country_names = {
            '1': 'Estados Unidos/Canadá',
            '55': 'Brasil',
            '351': 'Portugal',
            '34': 'Espanha',
            '33': 'França',
            '44': 'Reino Unido',
            '49': 'Alemanha',
            '39': 'Itália',
            '81': 'Japão',
            '86': 'China',
            '7': 'Rússia',
            'Desconhecido': 'País desconhecido'
        }
        
        # Operadoras brasileiras comuns
        br_carriers = ['Vivo', 'Claro', 'TIM', 'Oi', 'Nextel']
        
        # Determinar país
        country = country_names.get(country_code, 'País desconhecido')
        
        # Simular operadora com base no país
        if country_code == '55':  # Brasil
            # Usar DDD para determinar região
            if len(phone_number) >= 5:
                ddd = phone_number[3:5] if phone_number.startswith('+') else phone_number[2:4]
                
                # Simular operadora com base no último dígito do número
                if phone_number[-1] in '01234':
                    carrier = br_carriers[0]  # Vivo
                elif phone_number[-1] in '56':
                    carrier = br_carriers[1]  # Claro
                elif phone_number[-1] in '78':
                    carrier = br_carriers[2]  # TIM
                else:
                    carrier = br_carriers[3]  # Oi
                
                # Determinar tipo de linha
                if ddd in ['11', '21', '31', '41', '51', '61']:
                    region = 'Grande centro urbano'
                else:
                    region = 'Interior'
                
                # Determinar se é celular ou fixo
                if len(phone_number) >= 13 and phone_number[5] in '6789':
                    line_type = 'Celular'
                else:
                    line_type = 'Fixo'
            else:
                carrier = 'Desconhecida'
                region = 'Desconhecida'
                line_type = 'Desconhecido'
        else:
            carrier = 'Operadora internacional'
            region = 'Internacional'
            line_type = 'Desconhecido'
        
        return {
            'country': country,
            'carrier': carrier,
            'region': region,
            'line_type': line_type,
            'valid_format': True,
            'simulated': True  # Indicador de que os dados são simulados
        }
    
    def _get_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Obtém informações WHOIS de um domínio.
        
        Args:
            domain: Domínio a ser consultado
            
        Returns:
            Informações WHOIS do domínio
        """
        try:
            w = whois.whois(domain)
            
            # Extrair informações relevantes
            info = {
                'domain_name': w.domain_name,
                'registrar': w.registrar,
                'whois_server': w.whois_server,
                'creation_date': w.creation_date.isoformat() if hasattr(w, 'creation_date') and w.creation_date else None,
                'expiration_date': w.expiration_date.isoformat() if hasattr(w, 'expiration_date') and w.expiration_date else None,
                'updated_date': w.updated_date.isoformat() if hasattr(w, 'updated_date') and w.updated_date else None,
                'name_servers': w.name_servers,
                'status': w.status,
                'emails': w.emails,
                'dnssec': w.dnssec,
                'name': w.name,
                'org': w.org,
                'address': w.address,
                'city': w.city,
                'state': w.state,
                'zipcode': w.zipcode,
                'country': w.country
            }
            
            return info
        except Exception as e:
            logger.error(f"Erro ao obter informações WHOIS: {str(e)}")
            
            # Simular informações básicas para demonstração
            return self._simulate_domain_info(domain)
    
    def _simulate_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Simula informações WHOIS de um domínio para demonstração.
        
        Args:
            domain: Domínio a ser simulado
            
        Returns:
            Informações WHOIS simuladas
        """
        creation_date = datetime(2020, 1, 1).isoformat()
        expiration_date = datetime(2025, 1, 1).isoformat()
        
        return {
            'domain_name': domain,
            'registrar': 'Registrar Simulado Ltda.',
            'whois_server': f'whois.{domain.split(".")[-1]}',
            'creation_date': creation_date,
            'expiration_date': expiration_date,
            'updated_date': datetime.now().isoformat(),
            'name_servers': [f'ns1.{domain}', f'ns2.{domain}'],
            'status': 'active',
            'emails': [f'admin@{domain}', f'tech@{domain}'],
            'dnssec': 'unsigned',
            'name': 'Registrante Simulado',
            'org': 'Organização Simulada',
            'address': 'Endereço Simulado, 123',
            'city': 'Cidade Simulada',
            'state': 'Estado Simulado',
            'zipcode': '12345-678',
            'country': 'BR',
            'simulated': True  # Indicador de que os dados são simulados
        }
    
    def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """
        Verifica informações do certificado SSL de um domínio.
        
        Args:
            domain: Domínio a ser verificado
            
        Returns:
            Informações do certificado SSL
        """
        try:
            import ssl
            import socket
            
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
            
            # Extrair informações relevantes
            subject = dict(x[0] for x in cert['subject'])
            issuer = dict(x[0] for x in cert['issuer'])
            
            return {
                'subject': subject,
                'issuer': issuer,
                'version': cert['version'],
                'serial_number': cert['serialNumber'],
                'not_before': cert['notBefore'],
                'not_after': cert['notAfter'],
                'has_ssl': True
            }
        except Exception as e:
            logger.error(f"Erro ao verificar SSL: {str(e)}")
            return {
                'has_ssl': False,
                'error': str(e)
            }
    
    def _is_valid_domain(self, domain: str) -> bool:
        """
        Verifica se um domínio é válido.
        
        Args:
            domain: Domínio a ser verificado
            
        Returns:
            True se o domínio for válido, False caso contrário
        """
        # Padrão para validar domínios
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def _extract_domain_from_url(self, url: str) -> str:
        """
        Extrai o domínio base de uma URL.
        
        Args:
            url: URL completa
            
        Returns:
            Domínio base
        """
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except Exception as e:
            logger.error(f"Erro ao extrair domínio da URL: {str(e)}")
            return ""
    
    def _save_results(self, search_type: str, identifier: str, data: Dict[str, Any]):
        """
        Salva os resultados em um arquivo JSON.
        
        Args:
            search_type: Tipo de busca ('emails', 'domains', 'phones')
            identifier: Identificador único para os resultados
            data: Dados a serem salvos
        """
        output_file = os.path.join(
            self.output_dir, 
            search_type, 
            f"{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Resultados salvos em: {output_file}")
        
        # Armazenar resultados na memória
        if search_type not in self.results:
            self.results[search_type] = {}
        
        self.results[search_type][identifier] = data


# Função para demonstração do módulo
def demo():
    """Função de demonstração do módulo de busca de e-mails e informações de contato."""
    osint = ContactInfoOSINT(output_dir="resultados_osint")
    
    # Demonstração de busca de e-mails por domínio
    print("Demonstração de busca de e-mails por domínio:")
    domain_results = osint.search_emails_from_domain("exemplo.com.br")
    print(f"Domínio: {domain_results['domain']}")
    print(f"E-mails encontrados: {len(domain_results['emails_found'])}")
    
    # Demonstração de busca de e-mails por nome
    print("\nDemonstração de busca de e-mails por nome:")
    name_results = osint.search_emails_for_person("João Silva")
    print(f"Nome: {name_results['name']}")
    print(f"Possíveis e-mails: {len(name_results['possible_emails'])}")
    
    # Demonstração de análise de domínio
    print("\nDemonstração de análise de domínio:")
    domain_analysis = osint.analyze_domain("exemplo.com.br")
    print(f"Domínio: {domain_analysis['domain']}")
    print(f"Disponível: {domain_analysis['site_available']}")
    
    # Exportar resultados
    csv_file = osint.export_results_to_csv('emails')
    if csv_file:
        print(f"\nResultados exportados para: {csv_file}")
    
    print("\nDemonstração concluída!")


if __name__ == "__main__":
    demo()
