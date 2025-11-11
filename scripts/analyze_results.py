"""
Script para análise dos resultados da Etapa 1
Gera estatísticas e visualizações dos experimentos
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from pathlib import Path

# Configuração de estilo 
sns.set_context("paper", font_scale=1.5)
sns.set_style("whitegrid", {
    'grid.linestyle': '--',
    'grid.alpha': 0.3,
    'axes.edgecolor': '.15',
    'axes.linewidth': 1.25
})

# Configurações matplotlib
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': '0.8',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'lines.linewidth': 1.5,
    'lines.markersize': 6
})

# Paleta de cores
COLORS = {
    'Greedy_MaxProfit': '#2E86AB',  # Azul
    'Greedy_MinWeight': '#A23B72',  # Magenta
    'Greedy_MaxProfitWeight': '#F18F01',  # Laranja
    'Greedy_MinConflicts': '#06A77D',  # Verde
    'GRASP_MultiStart_100_alpha0.300000': '#C73E1D'  # Vermelho
}

def load_results(csv_file):
    """Carrega resultados de um arquivo CSV"""
    if not os.path.exists(csv_file):
        print(f"Arquivo não encontrado: {csv_file}")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"\nCarregados {len(df)} resultados de {csv_file}")
    return df

def analyze_methods(df):
    """Analisa desempenho dos métodos com estatísticas detalhadas"""
    print("\n" + "="*70)
    print("ANÁLISE POR MÉTODO")
    print("="*70)
    
    # Estatísticas por método
    stats = df.groupby('Method').agg({
        'Profit': ['mean', 'std', 'min', 'max', 'median'],
        'Time': ['mean', 'std', 'min', 'max'],
        'NumItems': ['mean', 'std']
    }).round(2)
    
    print("\nEstatísticas por Método:")
    print(stats)
    
    # Melhor método por instância
    best_per_instance = df.loc[df.groupby('Instance')['Profit'].idxmax()]
    method_wins = best_per_instance['Method'].value_counts()
    
    print("\nNúmero de vezes que cada método obteve o melhor resultado:")
    print(method_wins)
    
    # Análise de gap em relação ao melhor
    print("\n" + "-"*70)
    print("GAP EM RELAÇÃO AO MELHOR MÉTODO POR INSTÂNCIA")
    print("-"*70)
    
    gaps = []
    for instance in df['Instance'].unique():
        instance_df = df[df['Instance'] == instance]
        best_profit = instance_df['Profit'].max()
        for _, row in instance_df.iterrows():
            if best_profit > 0:
                gap = ((best_profit - row['Profit']) / best_profit) * 100
                gaps.append({
                    'Instance': instance,
                    'Method': row['Method'],
                    'Gap': gap
                })
    
    gap_df = pd.DataFrame(gaps)
    avg_gaps = gap_df.groupby('Method')['Gap'].agg(['mean', 'std', 'min', 'max']).round(2)
    print("\nGap médio (%) em relação ao melhor:")
    print(avg_gaps)
    
    return stats, method_wins, gap_df

def plot_method_comparison(df, output_dir):
    """Gera gráficos comparando métodos"""
    
    methods = sorted(df['Method'].unique())
    colors_list = [COLORS.get(m, '#808080') for m in methods]
    
    # 1. Boxplot de valores com estatísticas
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Subplot 1: Distribuição de Profit
    ax1 = axes[0]
    bp1 = ax1.boxplot([df[df['Method'] == m]['Profit'].values for m in methods],
                       labels=methods,
                       patch_artist=True,
                       notch=True,
                       showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red', 
                                    markeredgecolor='red', markersize=6))
    
    # Colorir boxplots
    for patch, color in zip(bp1['boxes'], colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax1.set_ylabel('Valor da Solução (Profit)', fontweight='bold')
    ax1.set_xlabel('Método', fontweight='bold')
    ax1.set_title('(a) Distribuição de Valores por Método', fontweight='bold', loc='left')
    ax1.tick_params(axis='x', rotation=15)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Subplot 2: Distribuição de Tempo
    ax2 = axes[1]
    bp2 = ax2.boxplot([df[df['Method'] == m]['Time'].values for m in methods],
                       labels=methods,
                       patch_artist=True,
                       notch=True,
                       showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red', 
                                    markeredgecolor='red', markersize=6))
    
    # Colorir boxplots
    for patch, color in zip(bp2['boxes'], colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax2.set_ylabel('Tempo de Execução (segundos)', fontweight='bold')
    ax2.set_xlabel('Método', fontweight='bold')
    ax2.set_title('(b) Tempo de Execução por Método', fontweight='bold', loc='left')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/method_comparison.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/method_comparison.pdf", bbox_inches='tight')
    print(f"\nGráfico salvo: {output_dir}/method_comparison.png (e .pdf)")
    plt.close()
    
    # 2. Gráfico de barras com médias e desvio padrão
    fig, ax = plt.subplots(figsize=(12, 6))
    
    method_stats = df.groupby('Method')['Profit'].agg(['mean', 'std']).loc[methods]
    x_pos = np.arange(len(methods))
    
    bars = ax.bar(x_pos, method_stats['mean'], yerr=method_stats['std'],
                  color=colors_list, alpha=0.7, capsize=5, 
                  edgecolor='black', linewidth=1.2, error_kw={'linewidth': 2})
    
    ax.set_ylabel('Valor Médio da Solução', fontweight='bold')
    ax.set_xlabel('Método', fontweight='bold')
    ax.set_title('Comparação de Desempenho Médio dos Métodos', fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(methods, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores no topo das barras
    for i, (bar, val) in enumerate(zip(bars, method_stats['mean'])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + method_stats['std'].iloc[i],
                f'{val:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/method_performance.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/method_performance.pdf", bbox_inches='tight')
    print(f"Gráfico salvo: {output_dir}/method_performance.png (e .pdf)")
    plt.close()

def plot_instance_comparison(df, output_dir):
    """Compara métodos para cada instância com heatmap"""
    
    # Pivot table para heatmap
    pivot = df.pivot_table(values='Profit', index='Instance', 
                           columns='Method', aggfunc='mean')
    
    # Reordenar colunas para melhor visualização
    method_order = sorted(pivot.columns, 
                         key=lambda x: pivot[x].mean(), 
                         reverse=True)
    pivot = pivot[method_order]
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(14, max(10, len(pivot) * 0.25)))
    
    # Heatmap com anotações
    im = ax.imshow(pivot.values, cmap='YlGnBu', aspect='auto')
    
    # Configurar ticks
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=25, ha='right')
    ax.set_yticklabels(pivot.index)
    
    # Adicionar anotações
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if not np.isnan(value):
                # Destacar melhor valor por instância
                is_best = value == pivot.iloc[i, :].max()
                text = ax.text(j, i, f'{value:.0f}',
                             ha="center", va="center",
                             color="white" if value > pivot.values.mean() else "black",
                             fontweight='bold' if is_best else 'normal',
                             fontsize=8)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Valor da Solução', rotation=270, labelpad=20, fontweight='bold')
    
    ax.set_xlabel('Método', fontweight='bold')
    ax.set_ylabel('Instância', fontweight='bold')
    ax.set_title('Valor das Soluções por Instância e Método', 
                fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/instance_heatmap.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/instance_heatmap.pdf", bbox_inches='tight')
    print(f"Gráfico salvo: {output_dir}/instance_heatmap.png (e .pdf)")
    plt.close()

def plot_pareto_front(df, output_dir):
    """Plota fronteira de Pareto: Valor vs Tempo"""
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    methods = sorted(df['Method'].unique())
    
    for method in methods:
        method_df = df[df['Method'] == method]
        color = COLORS.get(method, '#808080')
        
        # Plotar pontos com transparência
        ax.scatter(method_df['Time'], method_df['Profit'], 
                  label=method, alpha=0.5, s=80, color=color,
                  edgecolors='black', linewidth=0.5)
        
        # Adicionar média com marcador especial
        mean_time = method_df['Time'].mean()
        mean_profit = method_df['Profit'].mean()
        ax.scatter(mean_time, mean_profit, s=300, color=color,
                  marker='*', edgecolors='black', linewidth=2,
                  zorder=5)
    
    ax.set_xlabel('Tempo de Execução (segundos)', fontweight='bold')
    ax.set_ylabel('Valor da Solução', fontweight='bold')
    ax.set_title('Trade-off entre Qualidade e Tempo de Execução', 
                fontweight='bold', pad=15)
    
    # Legenda fora do gráfico
    legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
                      frameon=True, fancybox=True, shadow=True,
                      title='Método', title_fontsize=11)
    legend.get_title().set_fontweight('bold')
    
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Adicionar anotação explicativa
    ax.text(0.02, 0.98, '★ = Média do método',
           transform=ax.transAxes, fontsize=10,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pareto_front.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/pareto_front.pdf", bbox_inches='tight')
    print(f"Gráfico salvo: {output_dir}/pareto_front.png (e .pdf)")
    plt.close()


def plot_gap_analysis(gap_df, output_dir):
    """Visualiza o gap de qualidade em relação ao melhor método"""
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    methods = sorted(gap_df['Method'].unique())
    colors_list = [COLORS.get(m, '#808080') for m in methods]
    
    # Subplot 1: Boxplot de gaps
    ax1 = axes[0]
    bp = ax1.boxplot([gap_df[gap_df['Method'] == m]['Gap'].values for m in methods],
                      labels=methods,
                      patch_artist=True,
                      notch=True,
                      showmeans=True,
                      meanprops=dict(marker='D', markerfacecolor='red', 
                                   markeredgecolor='red', markersize=6))
    
    for patch, color in zip(bp['boxes'], colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax1.set_ylabel('Gap (%) em relação ao melhor', fontweight='bold')
    ax1.set_xlabel('Método', fontweight='bold')
    ax1.set_title('(a) Distribuição do Gap de Qualidade', fontweight='bold', loc='left')
    ax1.tick_params(axis='x', rotation=15)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=0, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Ótimo')
    ax1.legend()
    
    # Subplot 2: Barras com gap médio
    ax2 = axes[1]
    gap_stats = gap_df.groupby('Method')['Gap'].agg(['mean', 'std']).loc[methods]
    x_pos = np.arange(len(methods))
    
    bars = ax2.bar(x_pos, gap_stats['mean'], yerr=gap_stats['std'],
                   color=colors_list, alpha=0.7, capsize=5,
                   edgecolor='black', linewidth=1.2, error_kw={'linewidth': 2})
    
    ax2.set_ylabel('Gap Médio (%)', fontweight='bold')
    ax2.set_xlabel('Método', fontweight='bold')
    ax2.set_title('(b) Gap Médio em Relação ao Melhor', fontweight='bold', loc='left')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(methods, rotation=15, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=0, color='green', linestyle='--', linewidth=2, alpha=0.7)
    
    # Adicionar valores
    for bar, val in zip(bars, gap_stats['mean']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/gap_analysis.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/gap_analysis.pdf", bbox_inches='tight')
    print(f"Gráfico salvo: {output_dir}/gap_analysis.png (e .pdf)")
    plt.close()


def plot_performance_profile(df, output_dir):
    """Performance Profile - mostra robustez dos métodos"""
    
    # Calcular performance ratio para cada método
    instances = df['Instance'].unique()
    methods = sorted(df['Method'].unique())
    
    performance_ratios = {method: [] for method in methods}
    
    for instance in instances:
        instance_df = df[df['Instance'] == instance]
        best_profit = instance_df['Profit'].max()
        
        for method in methods:
            method_profit = instance_df[instance_df['Method'] == method]['Profit'].values
            if len(method_profit) > 0 and best_profit > 0:
                ratio = method_profit[0] / best_profit
                performance_ratios[method].append(ratio)
    
    # Criar performance profile
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tau_values = np.linspace(0, 1, 100)
    
    for method in methods:
        ratios = np.array(performance_ratios[method])
        n_instances = len(ratios)
        
        rho = []
        for tau in tau_values:
            count = np.sum(ratios >= tau)
            rho.append(count / n_instances)
        
        color = COLORS.get(method, '#808080')
        ax.plot(tau_values, rho, label=method, linewidth=2.5, 
               color=color, marker='o', markersize=4, markevery=10)
    
    ax.set_xlabel('τ (razão de desempenho)', fontweight='bold')
    ax.set_ylabel('ρ(τ) (fração de instâncias)', fontweight='bold')
    ax.set_title('Performance Profile dos Métodos', fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    
    # Adicionar linhas de referência
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=1, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/performance_profile.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/performance_profile.pdf", bbox_inches='tight')
    print(f"Gráfico salvo: {output_dir}/performance_profile.png (e .pdf)")
    plt.close()


def plot_convergence_analysis(df, output_dir):
    """Análise de convergência - relação entre itens e valor"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    methods = sorted(df['Method'].unique())
    
    for method in methods:
        method_df = df[df['Method'] == method]
        color = COLORS.get(method, '#808080')
        
        ax.scatter(method_df['NumItems'], method_df['Profit'],
                  label=method, alpha=0.5, s=60, color=color,
                  edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Número de Itens Selecionados', fontweight='bold')
    ax.set_ylabel('Valor da Solução', fontweight='bold')
    ax.set_title('Relação entre Número de Itens e Valor da Solução', 
                fontweight='bold', pad=15)
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/items_vs_profit.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/items_vs_profit.pdf", bbox_inches='tight')
    print(f"Gráfico salvo: {output_dir}/items_vs_profit.png (e .pdf)")
    plt.close()

def generate_summary_report(df, gap_df, output_file):
    """Gera relatório resumido em texto"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RELATÓRIO DE RESULTADOS - ETAPA 1\n")
        f.write("Heurísticas Construtivas para o DCKP\n")
        f.write("="*70 + "\n\n")
        
        # Informações gerais
        f.write(f"Total de experimentos: {len(df)}\n")
        f.write(f"Número de instâncias: {df['Instance'].nunique()}\n")
        f.write(f"Número de métodos: {df['Method'].nunique()}\n")
        f.write(f"Métodos testados: {', '.join(sorted(df['Method'].unique()))}\n\n")
        
        # Estatísticas globais
        f.write("-"*70 + "\n")
        f.write("ESTATÍSTICAS GLOBAIS\n")
        f.write("-"*70 + "\n")
        f.write(f"Melhor valor encontrado: {df['Profit'].max()}\n")
        f.write(f"  Método: {df.loc[df['Profit'].idxmax(), 'Method']}\n")
        f.write(f"  Instância: {df.loc[df['Profit'].idxmax(), 'Instance']}\n\n")
        
        f.write(f"Valor médio geral: {df['Profit'].mean():.2f}\n")
        f.write(f"Desvio padrão geral: {df['Profit'].std():.2f}\n\n")
        
        f.write(f"Tempo médio de execução: {df['Time'].mean():.4f}s\n")
        f.write(f"Tempo mínimo: {df['Time'].min():.4f}s\n")
        f.write(f"Tempo máximo: {df['Time'].max():.4f}s\n\n")
        
        # Estatísticas por método
        f.write("-"*70 + "\n")
        f.write("DESEMPENHO POR MÉTODO\n")
        f.write("-"*70 + "\n\n")
        
        for method in sorted(df['Method'].unique()):
            method_df = df[df['Method'] == method]
            f.write(f"Método: {method}\n")
            f.write(f"  Valor médio: {method_df['Profit'].mean():.2f}\n")
            f.write(f"  Valor mediano: {method_df['Profit'].median():.2f}\n")
            f.write(f"  Desvio padrão: {method_df['Profit'].std():.2f}\n")
            f.write(f"  Coef. variação: {(method_df['Profit'].std() / method_df['Profit'].mean() * 100):.2f}%\n")
            f.write(f"  Melhor valor: {method_df['Profit'].max()}\n")
            f.write(f"  Pior valor: {method_df['Profit'].min()}\n")
            f.write(f"  Tempo médio: {method_df['Time'].mean():.4f}s\n")
            f.write(f"  Tempo desvio padrão: {method_df['Time'].std():.4f}s\n")
            f.write(f"  Itens médios: {method_df['NumItems'].mean():.1f}\n")
            f.write(f"  Itens desvio padrão: {method_df['NumItems'].std():.2f}\n\n")
        
        # Ranking de métodos
        f.write("-"*70 + "\n")
        f.write("RANKING DE MÉTODOS (por valor médio)\n")
        f.write("-"*70 + "\n")
        
        ranking = df.groupby('Method')['Profit'].mean().sort_values(ascending=False)
        for i, (method, avg_profit) in enumerate(ranking.items(), 1):
            f.write(f"{i}. {method}: {avg_profit:.2f}\n")
        
        # Análise de dominância
        f.write("\n" + "-"*70 + "\n")
        f.write("ANÁLISE DE DOMINÂNCIA\n")
        f.write("-"*70 + "\n")
        
        best_per_instance = df.loc[df.groupby('Instance')['Profit'].idxmax()]
        method_wins = best_per_instance['Method'].value_counts()
        
        f.write("Número de vezes que cada método obteve o melhor resultado:\n")
        for method, wins in method_wins.items():
            percentage = (wins / len(df['Instance'].unique())) * 100
            f.write(f"  {method}: {wins} ({percentage:.1f}%)\n")
        
        # Gap Analysis
        f.write("\n" + "-"*70 + "\n")
        f.write("ANÁLISE DE GAP EM RELAÇÃO AO MELHOR\n")
        f.write("-"*70 + "\n")
        
        gap_stats = gap_df.groupby('Method')['Gap'].agg(['mean', 'std', 'min', 'max'])
        f.write("\nGap médio (%) por método:\n")
        for method in sorted(gap_stats.index):
            stats_row = gap_stats.loc[method]
            f.write(f"  {method}:\n")
            f.write(f"    Média: {stats_row['mean']:.2f}%\n")
            f.write(f"    Desvio padrão: {stats_row['std']:.2f}%\n")
            f.write(f"    Mínimo: {stats_row['min']:.2f}%\n")
            f.write(f"    Máximo: {stats_row['max']:.2f}%\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("OBSERVAÇÕES E CONCLUSÕES\n")
        f.write("="*70 + "\n\n")
        
        # Identificar melhor método
        best_method = ranking.index[0]
        f.write(f"1. MELHOR MÉTODO GERAL: {best_method}\n")
        f.write(f"   - Maior valor médio: {ranking.iloc[0]:.2f}\n")
        best_wins = method_wins.get(best_method, 0) if best_method in method_wins else 0
        f.write(f"   - Venceu em {best_wins} de {len(df['Instance'].unique())} instâncias\n\n")
        
        # Identificar método mais rápido
        fastest = df.groupby('Method')['Time'].mean().idxmin()
        fastest_time = df.groupby('Method')['Time'].mean().min()
        f.write(f"2. MÉTODO MAIS RÁPIDO: {fastest}\n")
        f.write(f"   - Tempo médio: {fastest_time:.4f}s\n\n")
        
        # Análise de trade-off
        f.write("3. ANÁLISE DE TRADE-OFF:\n")
        for method in sorted(df['Method'].unique()):
            method_df = df[df['Method'] == method]
            avg_profit = method_df['Profit'].mean()
            avg_time = method_df['Time'].mean()
            efficiency = avg_profit / (avg_time + 0.0001)  # Evitar divisão por zero
            f.write(f"   {method}:\n")
            f.write(f"     - Eficiência (Valor/Tempo): {efficiency:.2f}\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"\nRelatório salvo: {output_file}")

def main():
    """Função principal"""
    
    print("="*60)
    print("ANÁLISE DE RESULTADOS - ETAPA 1")
    print("="*60)
    
    # Diretórios
    results_dir = Path("results/etapa1")
    output_dir = results_dir / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Procura arquivos CSV (ignora single_*.csv)
    csv_files = [f for f in results_dir.glob("*.csv") if not f.name.startswith("single_")]
    
    if not csv_files:
        print("\nNenhum arquivo de resultados encontrado!")
        print("Execute primeiro os experimentos com: .\\scripts\\run_experiments.ps1")
        return
    
    # Carrega e combina todos os resultados
    all_data = []
    for csv_file in csv_files:
        df = load_results(csv_file)
        if df is not None:
            all_data.append(df)
    
    if not all_data:
        print("\nErro ao carregar resultados!")
        return
    
    # Combina todos os dataframes
    df_combined = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal de resultados combinados: {len(df_combined)}")
    
    # Análises
    print("\nGerando análises...")
    stats, method_wins, gap_df = analyze_methods(df_combined)
    
    print("\nGerando visualizações...")
    plot_method_comparison(df_combined, output_dir)
    plot_instance_comparison(df_combined, output_dir)
    plot_pareto_front(df_combined, output_dir)
    plot_gap_analysis(gap_df, output_dir)
    plot_performance_profile(df_combined, output_dir)
    plot_convergence_analysis(df_combined, output_dir)
    
    print("\nGerando relatório...")
    generate_summary_report(df_combined, gap_df, output_dir / "summary_report.txt")
    
    # Salva estatísticas em CSV
    stats.to_csv(output_dir / "method_statistics.csv")
    method_wins.to_csv(output_dir / "method_wins.csv", header=['Wins'])
    gap_df.to_csv(output_dir / "gap_analysis.csv", index=False)
    
    print("\n" + "="*70)
    print("ANÁLISE CONCLUÍDA!")
    print("="*70)
    print(f"\nResultados salvos em: {output_dir}")
    print("\nArquivos gerados:")
    print("  Visualizações:")
    print("    - method_comparison.png/pdf")
    print("    - method_performance.png/pdf")
    print("    - instance_heatmap.png/pdf")
    print("    - pareto_front.png/pdf")
    print("    - gap_analysis.png/pdf")
    print("    - performance_profile.png/pdf")
    print("    - items_vs_profit.png/pdf")
    print("  Relatórios:")
    print("    - summary_report.txt")
    print("  Dados:")
    print("    - method_statistics.csv")
    print("    - method_wins.csv")
    print("    - gap_analysis.csv")

if __name__ == "__main__":
    main()
