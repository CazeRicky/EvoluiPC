"""
Exemplo de integração da classificação de dispositivo com a API Django
Mostra como usar o cpu_classifier e armazenar no Neo4j
"""

def exemplo_integracao_na_api():
    """
    Exemplo de como integrar a classificação no endpoint de upload do Django
    """
    
    # Este código seria adicionado ao views.py no endpoint de upload
    
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    from django.views.decorators.csrf import csrf_exempt
    import json
    
    # Importar os novos módulos
    # from core import neo4j_identity, neo4j_store
    # from evoluipc_engine.cpu_classifier import classificar_dispositivo
    
    @require_http_methods(["POST"])
    @csrf_exempt
    def machine_upload_com_classificacao(request):
        """
        Endpoint exemplo que recebe dados de hardware e classifica o dispositivo
        """
        try:
            data = json.loads(request.body)
            username = data.get('username')
            hardware = data.get('hardware', {})
            
            # Autenticar usuário
            # user = neo4j_identity.get_user_by_token(token)
            # if not user:
            #     return JsonResponse({'detail': 'Não autenticado'}, status=401)
            
            nome_cpu = hardware.get('cpu', '')
            
            # Classificar o dispositivo
            classificacao = classificar_dispositivo(nome_cpu)
            
            # Simular objeto de usuário para armazenar
            mock_user = type('User', (), {
                'id': '12345-uuid',
                'username': username,
                'email': f'{username}@example.com'
            })()
            
            # Armazenar classificação no Neo4j
            # neo4j_store.upsert_device_classification(
            #     user=mock_user,
            #     cpu_classification=classificacao,
            #     source="device-scanner"
            # )
            
            # Armazenar dados do PC
            # neo4j_store.upsert_user_pc_parts(
            #     user=mock_user,
            #     machine=hardware,
            #     diagnostics=[],
            #     source="device-scanner"
            # )
            
            response = {
                'status': 'success',
                'message': 'Hardware recebido e classificado',
                'device_classification': classificacao,
                'hardware_received': {
                    'cpu': nome_cpu,
                    'gpu': hardware.get('gpu'),
                    'ram': hardware.get('ram'),
                    'motherboard': hardware.get('motherboard')
                }
            }
            
            return JsonResponse(response, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'detail': f'Erro: {str(e)}'}, status=500)


# Exemplo de resposta esperada:
EXEMPLO_RESPOSTA = {
    "status": "success",
    "message": "Hardware recebido e classificado",
    "device_classification": {
        "cpu_suffix": "HX",
        "device_type": "Laptop",
        "description": "Desempenho mais alto, todas as UNs desbloqueadas",
        "confidence": 100
    },
    "hardware_received": {
        "cpu": "Intel Core i9-13900HX",
        "gpu": "NVIDIA RTX 4090",
        "ram": "32GB",
        "motherboard": "ASUS ROG Strix G614JI"
    }
}


def exemplo_query_neo4j_para_device_info():
    """
    Exemplo de query Cypher para recuperar informações de classificação do dispositivo
    """
    
    query_get_user_with_device = """
    MATCH (u:AppUser {username: $username})
    OPTIONAL MATCH (u)-[:HAS_DEVICE_INFO]->(d:DeviceClassification)
    OPTIONAL MATCH (u)-[:HAS_PC_PARTS]->(p:UserPcParts)
    RETURN {
        username: u.username,
        email: u.email,
        device_type: d.device_type,
        cpu_suffix: d.cpu_suffix,
        confidence: d.confidence,
        detected_at: d.detected_at,
        pc_cpu: p.machine_json  // Vai ter que fazer JSON parse
    } AS user_info
    """
    
    query_stats_by_device_type = """
    MATCH (u:AppUser)-[:HAS_DEVICE_INFO]->(d:DeviceClassification)
    RETURN 
        d.device_type AS device_type,
        count(u) AS count,
        collect(u.username) AS users
    """
    
    query_popular_cpu_suffixes = """
    MATCH (u:AppUser)-[:HAS_DEVICE_INFO]->(d:DeviceClassification)
    WHERE d.cpu_suffix IS NOT NULL
    RETURN 
        d.cpu_suffix AS suffix,
        count(u) AS count,
        d.description AS description
    ORDER BY count DESC
    """
    
    return {
        'get_user_with_device': query_get_user_with_device,
        'stats_by_device_type': query_stats_by_device_type,
        'popular_cpu_suffixes': query_popular_cpu_suffixes
    }


if __name__ == "__main__":
    print("📚 EXEMPLOS DE INTEGRAÇÃO - EvoluiPC Device Classification\n")
    
    print("=" * 70)
    print("1. EXEMPLO DE RESPOSTA DA API")
    print("=" * 70)
    import json
    print(json.dumps(EXEMPLO_RESPOSTA, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)
    print("2. QUERIES NEO4J DISPONÍVEIS")
    print("=" * 70)
    queries = exemplo_query_neo4j_para_device_info()
    for nome, query in queries.items():
        print(f"\n{nome}:")
        print(query)
    
    print("\n" + "=" * 70)
    print("3. FLUXO COMPLETO")
    print("=" * 70)
    print("""
    1. Scanner.py coleta hardware local (CPU, GPU, RAM, Motherboard)
    2. cpu_classifier.py analisa o nome do CPU e extrai o sufixo
    3. Classifica como Desktop ou Laptop baseado no sufixo
    4. Envia tudo para a API Django junto com a classificação
    5. Django armazena no Neo4j:
       - AppUser (usuário)
       - UserPcParts (peças do PC e hardware)
       - DeviceClassification (tipo de dispositivo + sufixo)
    6. Frontend pode usar device_type para mostrar recomendações específicas
    """)
