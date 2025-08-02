#!/usr/bin/env python3
"""
Análise dos Resultados do Teste de Stress
"""

import json
import sys
from datetime import datetime
import statistics

def analyze_stress_results(filename):
    """Analisa os resultados do teste de stress"""
    
    print("📊 ANÁLISE DOS RESULTADOS DO TESTE DE STRESS")
    print("=" * 60)
    
    # Carregar resultados
    with open(filename, 'r') as f:
        results = json.load(f)
    
    # Estatísticas gerais
    total_sessions = results['total_sessions']
    successful_sessions = results['successful_sessions']
    failed_sessions = results['failed_sessions']
    
    # Calcular tempos
    start_time = datetime.fromisoformat(results['start_time'])
    end_time = datetime.fromisoformat(results['end_time'])
    total_duration = (end_time - start_time).total_seconds()
    
    # Estatísticas BTC
    btc_sessions = results['btc_sessions']
    btc_times = [s['response_time'] for s in btc_sessions]
    btc_amounts = [s['amount_ars'] for s in btc_sessions]
    btc_crypto_amounts = [s['crypto_amount'] for s in btc_sessions]
    
    # Estatísticas USDT
    usdt_sessions = results['usdt_sessions']
    usdt_times = [s['response_time'] for s in usdt_sessions]
    usdt_amounts = [s['amount_ars'] for s in usdt_sessions]
    usdt_crypto_amounts = [s['crypto_amount'] for s in usdt_sessions]
    
    print(f"📈 ESTATÍSTICAS GERAIS:")
    print(f"   - Total de sessões: {total_sessions}")
    print(f"   - Sessões bem-sucedidas: {successful_sessions}")
    print(f"   - Sessões falharam: {failed_sessions}")
    print(f"   - Taxa de sucesso: {(successful_sessions/total_sessions)*100:.2f}%")
    print(f"   - Duração total: {total_duration:.2f} segundos")
    print(f"   - Sessões por segundo: {total_sessions/total_duration:.2f}")
    
    print(f"\n🪙 ESTATÍSTICAS BITCOIN (BTC):")
    print(f"   - Sessões criadas: {len(btc_sessions)}")
    print(f"   - Tempo médio de resposta: {statistics.mean(btc_times):.2f}ms")
    print(f"   - Tempo mínimo: {min(btc_times):.2f}ms")
    print(f"   - Tempo máximo: {max(btc_times):.2f}ms")
    print(f"   - Desvio padrão: {statistics.stdev(btc_times):.2f}ms")
    print(f"   - Valor médio ARS: ${statistics.mean(btc_amounts):,.2f}")
    print(f"   - Valor médio BTC: {statistics.mean(btc_crypto_amounts):.8f}")
    
    print(f"\n💎 ESTATÍSTICAS USDT (TRC20):")
    print(f"   - Sessões criadas: {len(usdt_sessions)}")
    print(f"   - Tempo médio de resposta: {statistics.mean(usdt_times):.2f}ms")
    print(f"   - Tempo mínimo: {min(usdt_times):.2f}ms")
    print(f"   - Tempo máximo: {max(usdt_times):.2f}ms")
    print(f"   - Desvio padrão: {statistics.stdev(usdt_times):.2f}ms")
    print(f"   - Valor médio ARS: ${statistics.mean(usdt_amounts):,.2f}")
    print(f"   - Valor médio USDT: {statistics.mean(usdt_crypto_amounts):.2f}")
    
    # Comparação de performance
    print(f"\n⚡ COMPARAÇÃO DE PERFORMANCE:")
    btc_avg = statistics.mean(btc_times)
    usdt_avg = statistics.mean(usdt_times)
    difference = usdt_avg - btc_avg
    percentage_diff = (difference / btc_avg) * 100
    
    print(f"   - BTC médio: {btc_avg:.2f}ms")
    print(f"   - USDT médio: {usdt_avg:.2f}ms")
    print(f"   - Diferença: {difference:.2f}ms ({percentage_diff:+.1f}%)")
    
    if percentage_diff > 0:
        print(f"   - USDT é {percentage_diff:.1f}% mais lento que BTC")
    else:
        print(f"   - USDT é {abs(percentage_diff):.1f}% mais rápido que BTC")
    
    # Análise de erros
    if results['errors']:
        print(f"\n❌ ANÁLISE DE ERROS:")
        print(f"   - Total de erros: {len(results['errors'])}")
        
        # Agrupar erros por tipo
        error_types = {}
        for error in results['errors']:
            error_msg = error['error']
            if error_msg not in error_types:
                error_types[error_msg] = 0
            error_types[error_msg] += 1
        
        for error_msg, count in error_types.items():
            print(f"   - {error_msg}: {count} ocorrências")
    else:
        print(f"\n✅ NENHUM ERRO ENCONTRADO!")
    
    # Distribuição de valores
    print(f"\n💰 DISTRIBUIÇÃO DE VALORES:")
    
    # BTC
    btc_ranges = {
        '10k-50k': len([a for a in btc_amounts if 10000 <= a < 50000]),
        '50k-100k': len([a for a in btc_amounts if 50000 <= a < 100000]),
        '100k-150k': len([a for a in btc_amounts if 100000 <= a < 150000]),
        '150k-200k': len([a for a in btc_amounts if 150000 <= a < 200000]),
        '200k-250k': len([a for a in btc_amounts if 200000 <= a <= 250000])
    }
    
    print(f"   BTC por faixa de valor:")
    for range_name, count in btc_ranges.items():
        percentage = (count / len(btc_amounts)) * 100
        print(f"     - {range_name}: {count} sessões ({percentage:.1f}%)")
    
    # USDT
    usdt_ranges = {
        '10k-50k': len([a for a in usdt_amounts if 10000 <= a < 50000]),
        '50k-100k': len([a for a in usdt_amounts if 50000 <= a < 100000]),
        '100k-150k': len([a for a in usdt_amounts if 100000 <= a < 150000]),
        '150k-200k': len([a for a in usdt_amounts if 150000 <= a < 200000]),
        '200k-250k': len([a for a in usdt_amounts if 200000 <= a <= 250000])
    }
    
    print(f"   USDT por faixa de valor:")
    for range_name, count in usdt_ranges.items():
        percentage = (count / len(usdt_amounts)) * 100
        print(f"     - {range_name}: {count} sessões ({percentage:.1f}%)")
    
    # Conclusão
    print(f"\n" + "=" * 60)
    print("🎯 CONCLUSÕES:")
    
    success_rate = (successful_sessions/total_sessions)*100
    if success_rate >= 95:
        print("✅ Sistema muito estável - Pronto para produção")
    elif success_rate >= 80:
        print("⚠️  Sistema estável - Algumas melhorias recomendadas")
    else:
        print("❌ Sistema instável - Correções necessárias")
    
    if btc_avg < 300 and usdt_avg < 400:
        print("✅ Performance excelente")
    elif btc_avg < 500 and usdt_avg < 600:
        print("✅ Performance boa")
    else:
        print("⚠️  Performance pode ser melhorada")
    
    print("=" * 60)

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python analyze_stress_results.py <arquivo_resultados.json>")
        return
    
    filename = sys.argv[1]
    try:
        analyze_stress_results(filename)
    except FileNotFoundError:
        print(f"❌ Arquivo {filename} não encontrado")
    except Exception as e:
        print(f"❌ Erro ao analisar resultados: {e}")

if __name__ == "__main__":
    main() 