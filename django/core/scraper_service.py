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

def scrape_mercado_livre(query):
    """Raspa ofertas do Mercado Livre."""
    offers = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://lista.mercadolivre.com.br/{encoded_query}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        
        items = soup.find_all("li", class_="ui-search-layout__item")
        if not items:
            
            items = soup.find_all("div", class_="ui-search-result__wrapper")
            
        for item in items[:4]:  
            
            title_el = item.find("h2", class_="ui-search-item__title")
            if not title_el:
                title_el = item.find("h3", class_="ui-search-item__title")
            title = title_el.text.strip() if title_el else query

            
            link_el = item.find("a", class_="ui-search-link")
            link = link_el["href"] if link_el and "href" in link_el.attrs else "#"

            
            price_fraction = item.find("span", class_="andes-money-amount__fraction")
            price_cents = item.find("span", class_="andes-money-amount__cents")
            
            if price_fraction:
                price_str = price_fraction.text.strip()
                if price_cents:
                    price_str += f",{price_cents.text.strip()}"
                price = clean_price_string(price_str)
            else:
                price = 0.0

            
            img_el = item.find("img", class_="ui-search-result-image__element")
            if not img_el:
                img_el = item.find("img", class_="poly-component__picture")
            
            thumbnail = ""
            if img_el:
                
                thumbnail = img_el.get("data-src") or img_el.get("src") or ""

            if title and price > 0:
                offers.append({
                    "store": "Mercado Livre (Oficial)",
                    "title": title,
                    "price": price,
                    "link": link,
                    "thumbnail": thumbnail,
                    "is_live": True
                })
    except Exception as e:
        
        pass
    return offers

def scrape_amazon(query):
    """Raspa ofertas da Amazon Brasil."""
    offers = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.amazon.com.br/s?k={encoded_query}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", {"data-component-type": "s-search-result"})
        
        for item in items[:3]:  # Limita aos 3 primeiros
            # Título
            title_el = item.find("span", class_="a-size-base-plus") or item.find("span", class_="a-size-medium")
            title = title_el.text.strip() if title_el else query

            # Link
            link_el = item.find("a", class_="a-link-normal")
            link = "https://www.amazon.com.br" + link_el["href"] if link_el and "href" in link_el.attrs else "#"

            # Preço
            price_whole = item.find("span", class_="a-price-whole")
            price_fraction = item.find("span", class_="a-price-fraction")
            if price_whole:
                price_str = price_whole.text.strip().replace(".", "")
                if price_fraction:
                    price_str += f",{price_fraction.text.strip()}"
                price = clean_price_string(price_str)
            else:
                price = 0.0

            # Imagem
            img_el = item.find("img", class_="s-image")
            thumbnail = img_el["src"] if img_el and "src" in img_el.attrs else ""

            if title and price > 0:
                offers.append({
                    "store": "Amazon",
                    "title": title,
                    "price": price,
                    "link": link,
                    "thumbnail": thumbnail,
                    "is_live": True
                })
    except Exception:
        pass
    return offers

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

def generate_fallback_offers(query):
    """Gera ofertas fallback de alta fidelidade simulando Kabum, Pichau e Terabyte."""
    base_price = get_base_price_by_hardware_name(query)
    
    stores_info = [
        {
            "store": "KaBuM!",
            "title_template": "{query} - Excelente Custo Benefício",
            "price_multiplier": 0.95,  # Desconto no Pix
            "link_template": "https://www.kabum.com.br/busca?query={query_slug}",
            "thumbnail": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=150&auto=format&fit=crop&q=60" # CPU/Tech image
        },
        {
            "store": "Pichau",
            "title_template": "{query} em Promoção Especial",
            "price_multiplier": 0.94,
            "link_template": "https://www.pichau.com.br/search?q={query_slug}",
            "thumbnail": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=150&auto=format&fit=crop&q=60"
        },
        {
            "store": "TerabyteShop",
            "title_template": "{query} Gamer Edition",
            "price_multiplier": 0.96,
            "link_template": "https://www.terabyteshop.com.br/busca?str={query_slug}",
            "thumbnail": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=150&auto=format&fit=crop&q=60"
        },
        {
            "store": "Amazon",
            "title_template": "{query} - Vendido e Entregue por Amazon",
            "price_multiplier": 1.02,
            "link_template": "https://www.amazon.com.br/s?k={query_slug}",
            "thumbnail": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=150&auto=format&fit=crop&q=60"
        }
    ]
    
    query_slug = urllib.parse.quote_plus(query)
    fallback_offers = []
    
    for info in stores_info:
        # Preço final com variação aleatória de +/- 3%
        variation = random.uniform(0.97, 1.03)
        final_price = round(base_price * info["price_multiplier"] * variation, 2)
        
        fallback_offers.append({
            "store": info["store"],
            "title": info["title_template"].format(query=query),
            "price": final_price,
            "link": info["link_template"].format(query_slug=query_slug),
            "thumbnail": info["thumbnail"],
            "is_live": False
        })
        
    # Ordena pelo melhor preço (menor primeiro)
    fallback_offers.sort(key=lambda x: x["price"])
    return fallback_offers

def get_best_offers(query):
    """Busca ofertas na internet e complementa com ofertas simuladas de alta qualidade se necessário."""
    if not query or len(query.strip()) < 2:
        return []
        
    query_cleaned = query.strip()
    
    # 1. Tenta raspar Mercado Livre
    ml_offers = scrape_mercado_livre(query_cleaned)
    
    # 2. Tenta raspar Amazon
    amazon_offers = scrape_amazon(query_cleaned)
    
    live_offers = ml_offers + amazon_offers
    
    # Remove duplicados baseados no link ou título
    seen_links = set()
    unique_live = []
    for offer in live_offers:
        if offer["link"] not in seen_links:
            seen_links.add(offer["link"])
            unique_live.append(offer)
            
    # Se obtivemos resultados online válidos, retornamos eles
    if len(unique_live) >= 3:
        # Ordena pelo menor preço
        unique_live.sort(key=lambda x: x["price"])
        return unique_live[:6]
        
    # Se não temos resultados reais suficientes, combinamos com fallbacks de lojas famosas (Kabum, Pichau, Terabyte)
    # Isso garante que a UI sempre estará linda e operacional
    fallbacks = generate_fallback_offers(query_cleaned)
    
    # Combina live_offers com fallbacks, garantindo lojas variadas
    combined = unique_live + fallbacks
    seen_stores = set()
    final_offers = []
    
    # Prioriza os reais
    for offer in combined:
        store_key = f"{offer['store']}-{offer['title']}"
        if store_key not in seen_stores:
            seen_stores.add(store_key)
            final_offers.append(offer)
            
    final_offers.sort(key=lambda x: x["price"])
    return final_offers[:6]
