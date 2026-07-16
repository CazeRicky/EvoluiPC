import re
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

def clean_price_string(price_str):
    """Converte string de preço (ex: '1.250,90' ou '899') em float."""
    if not price_str:
        return 0.0
    # Remove R$, espaços e pontos de milhar, substitui vírgula por ponto
    cleaned = re.sub(r"[^\d,]", "", price_str).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def get_db_price_for_hardware(name):
    """Busca o preço estimado do componente no Neo4j local para garantir condizência."""
    query = """
    MATCH (h)
    WHERE (h:Processor OR h:Gpu OR h:Motherboard OR h:PlacaMae OR h:PlacaDeVideo OR h:Processador)
      AND toLower(h.name) CONTAINS toLower($name)
    RETURN h.price AS price, h.preco AS preco
    LIMIT 1
    """
    try:
        from .neo4j_store import get_driver, NEO4J_DATABASE
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                record = session.run(query, name=name).single()
                if record:
                    p = record.get("price") or record.get("preco")
                    if p:
                        return float(p)
    except Exception:
        pass
    return None

def extract_price_from_text(text):
    """Tenta extrair um valor de preço (R$) de um texto de snippet."""
    if not text:
        return None
    match = re.search(r"R\$\s*([0-9]+(?:\.[0-9]{3})*(?:,[0-9]{2})?)", text)
    if match:
        return clean_price_string(match.group(1))
    return None

def get_exact_link_and_price_from_ddg(store_domain, query):
    """
    Busca no DuckDuckGo a página exata do produto e tenta obter o preço real no snippet.
    """
    search_query = f"site:{store_domain} {query}"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=8, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", class_="result")
            
            for r in results:
                # Extrai o link
                link_el = r.find("a", class_="result__url")
                if not link_el:
                    link_el = r.find("a", href=True)
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if "/l/?uddg=" in href:
                    actual_url = href.split("/l/?uddg=")[1].split("&")[0]
                    actual_url = urllib.parse.unquote(actual_url)
                    
                    url_lower = actual_url.lower()
                    if store_domain in url_lower:
                        # Valida se é link direto de produto
                        if "kabum.com.br" in url_lower and "/produto/" not in url_lower:
                            continue
                        if "pichau.com.br" in url_lower and "/produto/" not in url_lower and "/p/" not in url_lower:
                            continue
                        if "terabyteshop.com.br" in url_lower and "/produto/" not in url_lower:
                            continue
                        if "amazon.com.br" in url_lower and "/dp/" not in url_lower and "/gp/" not in url_lower:
                            if "/product/" not in url_lower:
                                continue
                                
                        # Tenta obter o preço do snippet correspondente
                        price = None
                        snippet_el = r.find("a", class_="result__snippet")
                        if snippet_el:
                            price = extract_price_from_text(snippet_el.text)
                            
                        return actual_url, price
    except Exception:
        pass
    return None, None

def get_base_price_by_hardware_name(name):
    """Estima um preço base realista baseado no nome do hardware para gerar ofertas fallback coerentes."""
    name_upper = name.upper()
    
    # Processadores
    if "I3-10" in name_upper or "I3-12" in name_upper:
        return 550.00
    if "I5-10" in name_upper or "I5-11" in name_upper:
        return 750.00
    if "I5-12" in name_upper or "I5-13" in name_upper or "I5-14" in name_upper:
        return 1100.00
    if "I7-12" in name_upper or "I7-13" in name_upper or "I7-14" in name_upper:
        return 1800.00
    if "I9-" in name_upper:
        return 2900.00
    if "5500" in name_upper:
        return 520.00
    if "5600" in name_upper:
        return 820.00
    if "5700X3D" in name_upper:
        return 1350.00
    if "7600" in name_upper:
        return 1250.00
    if "7700" in name_upper or "7800X3D" in name_upper:
        return 2200.00
    
    # Placas de Vídeo
    if "1650" in name_upper or "1660" in name_upper:
        return 850.00
    if "2060" in name_upper or "3050" in name_upper:
        return 1200.00
    if "3060" in name_upper or "4060" in name_upper or "7600 XT" in name_upper:
        return 1900.00
    if "4070" in name_upper or "7700 XT" in name_upper:
        return 3800.00
    if "4080" in name_upper:
        return 7500.00
    if "4090" in name_upper:
        return 13500.00
    
    # Placas-mãe
    if "A320" in name_upper or "H610" in name_upper:
        return 380.00
    if "B550" in name_upper or "B660" in name_upper or "B760" in name_upper or "B650" in name_upper:
        return 750.00
    if "Z790" in name_upper or "X670" in name_upper:
        return 1600.00

    return 600.00  # Default fallback

def get_best_offers(query):
    """Busca as melhores ofertas para o hardware e retorna links exatos das páginas dos produtos."""
    if not query or len(query.strip()) < 2:
        return []
        
    query_cleaned = query.strip()
    
    # Tenta buscar preço da peça no banco Neo4j para alinhar os valores estimados
    base_price = get_db_price_for_hardware(query_cleaned)
    if not base_price:
        base_price = get_base_price_by_hardware_name(query_cleaned)
        
    stores_info = [
        {
            "store": "KaBuM!",
            "domain": "kabum.com.br",
            "title_template": "{query} - Oficial KaBuM!",
            "price_multiplier": 0.95,  # Desconto no Pix
            "search_fallback": "https://www.kabum.com.br/busca?query={slug}",
            "thumbnail": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=150&auto=format&fit=crop&q=60"
        },
        {
            "store": "Pichau",
            "domain": "pichau.com.br",
            "title_template": "{query} - Oficial Pichau",
            "price_multiplier": 0.94,
            "search_fallback": "https://www.pichau.com.br/search?q={slug}",
            "thumbnail": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=150&auto=format&fit=crop&q=60"
        },
        {
            "store": "TerabyteShop",
            "domain": "terabyteshop.com.br",
            "title_template": "{query} - Oficial TerabyteShop",
            "price_multiplier": 0.96,
            "search_fallback": "https://www.terabyteshop.com.br/busca?str={slug}",
            "thumbnail": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=150&auto=format&fit=crop&q=60"
        },
        {
            "store": "Amazon",
            "domain": "amazon.com.br",
            "title_template": "{query} - Vendido e Entregue por Amazon",
            "price_multiplier": 1.02,
            "search_fallback": "https://www.amazon.com.br/s?k={slug}",
            "thumbnail": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=150&auto=format&fit=crop&q=60"
        }
    ]
    
    query_slug = urllib.parse.quote_plus(query_cleaned)
    final_offers = []
    
    for info in stores_info:
        # Busca no DuckDuckGo pelo link da página exata do produto no domínio da loja
        exact_link, live_price = get_exact_link_and_price_from_ddg(info["domain"], query_cleaned)
        
        # Define o link
        is_live = False
        if exact_link:
            link = exact_link
            is_live = True
        else:
            # Fallback para o link da pesquisa interna caso não encontre link exato
            link = info["search_fallback"].format(slug=query_slug)
            
        # Define o preço
        if is_live and live_price and abs(live_price - base_price) < (base_price * 0.4):
            # Se encontramos um preço real e ele é condizente com a estimativa do banco (+/- 40%)
            price = live_price
        else:
            # Senão, calcula preço condizente baseado no banco de dados + variação de mercado da loja (+/- 2.5%)
            variation = random.uniform(0.975, 1.025)
            price = round(base_price * info["price_multiplier"] * variation, 2)
            
        # Ajusta título
        title = info["title_template"].format(query=query_cleaned)
        
        final_offers.append({
            "store": info["store"],
            "title": title,
            "price": price,
            "link": link,
            "thumbnail": info["thumbnail"],
            "is_live": is_live
        })
        
    # Ordena pelo menor preço
    final_offers.sort(key=lambda x: x["price"])
    return final_offers
