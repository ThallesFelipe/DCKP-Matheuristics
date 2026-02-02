#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DCKP Matheuristics - Suite de Análise para Publicação v2.0
================================================================================

Script de análise avançada para o Problema da Mochila com Restrições de Conflitos.
Produz visualizações prontas para publicação e análise estatística abrangente.

Funcionalidades:
- Análise de fronteira de Pareto (trade-off tempo-qualidade)
- Gráfico radar para comparação multi-métrica
- Diagramas de diferença crítica (teste de Nemenyi)
- Perfis de desempenho (Dolan-Moré)
- Classificação de dificuldade de instâncias
- Métricas de dominância e robustez
- Análise comparativa Etapa 1 vs Etapa 2
- Geração de tabelas LaTeX
- Gráficos de crista e comparações CDF
- Análise de tamanho de efeito (Delta de Cliff)

Autor: Projeto DCKP Metaheurísticas
Versão: 2.0
================================================================================
"""

import warnings
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass
from itertools import combinations
import re
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import seaborn as sns
from scipy import stats
from scipy.stats import rankdata

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AnalysisConfig:
    """Configuration for the analysis pipeline."""
    # Dominance threshold (win rate to consider domination)
    dominance_threshold: float = 0.80
    # Alpha for time-quality score (0=time only, 1=quality only)
    alpha_time_quality: float = 0.7
    # Statistical significance level
    alpha_stat: float = 0.05
    # Performance profile tau max
    tau_max: float = 5.0
    # Bootstrap iterations
    bootstrap_n: int = 1000
    # Figure DPI
    dpi: int = 300


CONFIG = AnalysisConfig()

# Colorblind-friendly professional palette (Wong palette)
PALETTE = [
    "#0072B2",  # Blue
    "#E69F00",  # Orange
    "#009E73",  # Green
    "#CC79A7",  # Pink
    "#D55E00",  # Vermillion
    "#56B4E9",  # Sky Blue
    "#F0E442",  # Yellow
    "#000000",  # Black
]

# Markers for methods
MARKERS = ['o', 's', '^', 'D', 'v', '<', '>', 'p', 'h', '*']

# Method-specific colors (assigned dynamically)
METHOD_COLORS: Dict[str, str] = {}
METHOD_MARKERS: Dict[str, str] = {}


def assign_method_styles(methods: List[str]) -> None:
    """Assign consistent colors and markers to methods."""
    global METHOD_COLORS, METHOD_MARKERS
    sorted_methods = sorted(methods)
    METHOD_COLORS = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(sorted_methods)}
    METHOD_MARKERS = {m: MARKERS[i % len(MARKERS)] for i, m in enumerate(sorted_methods)}


def setup_publication_style():
    """Configure matplotlib/seaborn for publication-quality figures."""
    sns.set_palette("colorblind")
    sns.set_context("paper", font_scale=1.1)
    sns.set_style("whitegrid")
    
    plt.rcParams.update({
        # Figure
        'figure.figsize': (8, 5),
        'figure.dpi': 150,
        'figure.facecolor': 'white',
        'figure.edgecolor': 'white',
        'figure.constrained_layout.use': True,
        
        # Saving
        'savefig.dpi': CONFIG.dpi,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        'savefig.facecolor': 'white',
        
        # Fonts (Serif for LaTeX compatibility)
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif'],
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'axes.titleweight': 'bold',
        'legend.fontsize': 9,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        
        # Axes
        'axes.linewidth': 0.8,
        'axes.edgecolor': '#333333',
        'axes.labelcolor': '#333333',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'axes.axisbelow': True,
        
        # Grid (subtle)
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,
        'grid.color': '#cccccc',
        
        # Ticks
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.color': '#333333',
        'ytick.color': '#333333',
        
        # Legend
        'legend.frameon': True,
        'legend.framealpha': 0.95,
        'legend.edgecolor': '#cccccc',
        'legend.fancybox': True,
        
        # Text
        'text.color': '#333333',
        
        # Math text
        'mathtext.fontset': 'dejavuserif',
    })


def save_figure(fig: plt.Figure, output_dir: Path, name: str, 
                formats: List[str] = ['png', 'pdf']):
    """Save figure in multiple formats."""
    for fmt in formats:
        filepath = output_dir / f"{name}.{fmt}"
        fig.savefig(filepath, format=fmt, dpi=CONFIG.dpi if fmt == 'png' else None)
    plt.close(fig)
    print(f"    ✓ {name}.{'/'.join(formats)}")


# =============================================================================
# DATA LOADING AND PREPROCESSING
# =============================================================================

def load_results(csv_file: Path) -> Optional[pd.DataFrame]:
    """Load results from a CSV file with validation."""
    if not csv_file.exists():
        return None
    
    try:
        df = pd.read_csv(csv_file)
        required_cols = {'Instance', 'Method', 'Profit', 'Time'}
        if not required_cols.issubset(df.columns):
            return None
        return df
    except Exception as e:
        print(f"    [ERRO] Falha ao carregar {csv_file}: {e}")
        return None


def load_all_results(results_dir: Path) -> Optional[pd.DataFrame]:
    """Load and concatenate all CSV result files."""
    csv_files = sorted([f for f in results_dir.glob("*.csv") 
                        if not f.name.startswith(("single_", "analysis", "gap_", "perf"))])
    
    if not csv_files:
        return None
    
    all_data = []
    for csv_file in csv_files:
        df = load_results(csv_file)
        if df is not None:
            all_data.append(df)
    
    if not all_data:
        return None
    
    return pd.concat(all_data, ignore_index=True)


def load_multi_stage_results() -> Dict[str, pd.DataFrame]:
    """Load results from multiple stages (etapa1, etapa2)."""
    results = {}
    
    for stage in ['etapa1', 'etapa2']:
        stage_dir = Path(f"results/{stage}")
        if stage_dir.exists():
            df = load_all_results(stage_dir)
            if df is not None and not df.empty:
                results[stage] = df
    
    return results


def compute_gap_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Compute gap (%) relative to Best Known Solution (BKS) per instance."""
    gaps = []
    
    for instance in df['Instance'].unique():
        inst_df = df[df['Instance'] == instance]
        bks = inst_df['Profit'].max()
        
        for _, row in inst_df.iterrows():
            gap = ((bks - row['Profit']) / bks * 100) if bks > 0 else 0.0
            gaps.append({
                'Instance': instance,
                'Method': row['Method'],
                'Profit': row['Profit'],
                'BKS': bks,
                'Gap': gap,
                'Time': row['Time']
            })
    
    return pd.DataFrame(gaps)


def parse_instance_info(instance_name: str) -> Dict[str, Any]:
    """
    Parse instance name to extract class, size, and other metadata.
    
    Returns dict with keys: 'class', 'size', 'density', 'set'
    """
    name = str(instance_name)
    info = {'class': 'Unknown', 'size': None, 'density': None, 'set': 'Unknown'}
    
    # Pattern for Set I instances: e.g., "10I5", "1I1", "11I1.txt"
    match_set1 = re.match(r'^(\d+)I(\d+)', name.replace('.txt', ''))
    if match_set1:
        info['size'] = int(match_set1.group(1))
        info['class'] = f"I{match_set1.group(1)}"
        info['set'] = 'I'
        return info
    
    # Pattern for Set II instances: e.g., "BPPC_1_0_1.txt_0.5"
    if 'BPPC' in name:
        # Extract density from suffix
        match_density = re.search(r'_(\d+\.\d+)$', name)
        if match_density:
            info['density'] = float(match_density.group(1))
        info['class'] = 'BPPC'
        info['set'] = 'II'
        return info
    
    # Sparse instances
    if 'sparse' in name.lower():
        if 'corr' in name.lower():
            info['class'] = 'sparse_corr'
        elif 'rand' in name.lower():
            info['class'] = 'sparse_rand'
        info['set'] = 'II'
        return info
    
    return info


# =============================================================================
# ADVANCED METRICS COMPUTATION
# =============================================================================

def compute_dominance_matrix(gap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pairwise dominance matrix.
    D[A][B] = proportion of instances where A beats B.
    """
    methods = sorted(gap_df['Method'].unique())
    instances = gap_df['Instance'].unique()
    n_instances = len(instances)
    
    # Pivot to get gaps per instance
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    
    dominance = pd.DataFrame(index=methods, columns=methods, dtype=float)
    
    for m1 in methods:
        for m2 in methods:
            if m1 == m2:
                dominance.loc[m1, m2] = 0.5
            else:
                if m1 in pivot.columns and m2 in pivot.columns:
                    wins = (pivot[m1] < pivot[m2]).sum()
                    dominance.loc[m1, m2] = wins / n_instances
                else:
                    dominance.loc[m1, m2] = np.nan
    
    return dominance


def compute_dominance_score(dominance_matrix: pd.DataFrame) -> pd.Series:
    """
    Compute dominance score for each method.
    Score = sum of (1 if dominates other methods at threshold)
    """
    methods = dominance_matrix.index
    scores = {}
    
    for method in methods:
        # Count how many methods this one dominates (>= threshold)
        dominated = (dominance_matrix.loc[method] >= CONFIG.dominance_threshold).sum()
        # Subtract self-comparison
        dominated -= 1 if dominance_matrix.loc[method, method] >= CONFIG.dominance_threshold else 0
        scores[method] = dominated
    
    return pd.Series(scores).sort_values(ascending=False)


def compute_consistency_index(gap_df: pd.DataFrame) -> pd.Series:
    """
    Compute consistency index: CI = 1 / (1 + CV)
    Higher CI = more consistent performance.
    """
    stats_df = gap_df.groupby('Method')['Gap'].agg(['mean', 'std'])
    cv = stats_df['std'] / (stats_df['mean'] + 1e-10)  # Avoid division by zero
    ci = 1 / (1 + cv)
    return ci.sort_values(ascending=False)


def compute_robustness_score(gap_df: pd.DataFrame) -> pd.Series:
    """
    Compute robustness score: R = (Median - Min) / (Max - Min)
    Lower R = more robust (less affected by outliers).
    """
    stats_df = gap_df.groupby('Method')['Gap'].agg(['min', 'median', 'max'])
    range_val = stats_df['max'] - stats_df['min']
    range_val = range_val.replace(0, 1e-10)  # Avoid division by zero
    robustness = (stats_df['median'] - stats_df['min']) / range_val
    return robustness.sort_values()


def compute_efficiency_ratio(gap_df: pd.DataFrame) -> pd.Series:
    """
    Compute efficiency ratio: ER = (1 - normalized_gap) / normalized_time
    Higher ER = better quality per unit of time.
    """
    stats_df = gap_df.groupby('Method').agg({
        'Gap': 'mean',
        'Time': 'mean'
    })
    
    # Normalize to [0, 1]
    gap_norm = (stats_df['Gap'] - stats_df['Gap'].min()) / (stats_df['Gap'].max() - stats_df['Gap'].min() + 1e-10)
    time_norm = (stats_df['Time'] - stats_df['Time'].min()) / (stats_df['Time'].max() - stats_df['Time'].min() + 1e-10)
    
    er = (1 - gap_norm) / (time_norm + 0.1)  # Add small constant to avoid infinity
    return er.sort_values(ascending=False)


def compute_time_quality_score(gap_df: pd.DataFrame, alpha: float = None) -> pd.Series:
    """
    Compute Time-Quality Score (Pareto score):
    TQ = alpha * (1 - normalized_gap) + (1 - alpha) * (1 - normalized_time)
    """
    if alpha is None:
        alpha = CONFIG.alpha_time_quality
    
    stats_df = gap_df.groupby('Method').agg({
        'Gap': 'mean',
        'Time': 'mean'
    })
    
    # Normalize to [0, 1]
    gap_norm = (stats_df['Gap'] - stats_df['Gap'].min()) / (stats_df['Gap'].max() - stats_df['Gap'].min() + 1e-10)
    time_norm = (stats_df['Time'] - stats_df['Time'].min()) / (stats_df['Time'].max() - stats_df['Time'].min() + 1e-10)
    
    tq = alpha * (1 - gap_norm) + (1 - alpha) * (1 - time_norm)
    return tq.sort_values(ascending=False)


def compute_win_rates(gap_df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute win rate (percentage of instances where method achieves best).
    """
    methods = gap_df['Method'].unique()
    instances = gap_df['Instance'].unique()
    n_instances = len(instances)
    
    wins = {m: 0 for m in methods}
    
    for instance in instances:
        inst_df = gap_df[gap_df['Instance'] == instance]
        best_gap = inst_df['Gap'].min()
        winners = inst_df[inst_df['Gap'] == best_gap]['Method'].tolist()
        for w in winners:
            wins[w] += 1 / len(winners)  # Split ties
    
    return {m: wins[m] / n_instances * 100 for m in methods}


def compute_podium_rates(gap_df: pd.DataFrame, top_n: int = 3) -> Dict[str, float]:
    """
    Compute podium rate (percentage of instances where method is in top N).
    """
    methods = gap_df['Method'].unique()
    instances = gap_df['Instance'].unique()
    n_instances = len(instances)
    
    podiums = {m: 0 for m in methods}
    
    for instance in instances:
        inst_df = gap_df[gap_df['Instance'] == instance].sort_values('Gap')
        top_methods = inst_df.head(top_n)['Method'].tolist()
        for m in top_methods:
            podiums[m] += 1
    
    return {m: podiums[m] / n_instances * 100 for m in methods}


def compute_instance_difficulty(gap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute instance difficulty metrics:
    - Hardness: mean gap across all methods
    - Discriminatory Power: std(gaps) / mean(gaps)
    """
    instance_stats = gap_df.groupby('Instance')['Gap'].agg(['mean', 'std', 'min', 'max'])
    instance_stats.columns = ['Hardness', 'StdGap', 'MinGap', 'MaxGap']
    
    instance_stats['DiscriminatoryPower'] = (
        instance_stats['StdGap'] / (instance_stats['Hardness'] + 1e-10)
    )
    
    # Classificar dificuldade
    def classify_difficulty(hardness):
        if hardness < 1:
            return 'Fácil'
        elif hardness < 5:
            return 'Médio'
        elif hardness < 10:
            return 'Difícil'
        else:
            return 'Muito Difícil'
    
    instance_stats['DifficultyClass'] = instance_stats['Hardness'].apply(classify_difficulty)
    
    return instance_stats


def compute_scalability_index(gap_df: pd.DataFrame) -> pd.Series:
    """
    Compute scalability index via log-log regression of time vs instance size.
    Lower SI = better scalability.
    """
    # Parse instance info
    gap_df = gap_df.copy()
    parsed = gap_df['Instance'].apply(parse_instance_info)
    gap_df['Size'] = parsed.apply(lambda x: x['size'])
    
    # Filter to instances with known sizes
    sized_df = gap_df[gap_df['Size'].notna()].copy()
    
    if sized_df.empty or len(sized_df['Size'].unique()) < 3:
        return pd.Series(dtype=float)
    
    methods = sized_df['Method'].unique()
    scalability = {}
    
    for method in methods:
        method_df = sized_df[sized_df['Method'] == method]
        if len(method_df) < 3:
            continue
        
        x = np.log(method_df['Size'].values + 1)
        y = np.log(method_df['Time'].values + 1e-10)
        
        try:
            slope, _, _, _, _ = stats.linregress(x, y)
            scalability[method] = slope
        except Exception:
            pass
    
    return pd.Series(scalability).sort_values()


# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def friedman_test(gap_df: pd.DataFrame) -> Dict[str, Any]:
    """Perform Friedman test for comparing multiple methods."""
    methods = sorted(gap_df['Method'].unique())
    
    if len(methods) < 2:
        return {'statistic': None, 'p_value': None, 'significant': False}
    
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    pivot = pivot.dropna()
    
    if len(pivot) < 3:
        return {'statistic': None, 'p_value': None, 'significant': False}
    
    try:
        method_gaps = [pivot[m].values for m in methods if m in pivot.columns]
        if len(method_gaps) >= 2:
            stat, p_value = stats.friedmanchisquare(*method_gaps)
            return {
                'statistic': stat,
                'p_value': p_value,
                'significant': p_value < CONFIG.alpha_stat
            }
    except Exception:
        pass
    
    return {'statistic': None, 'p_value': None, 'significant': False}


def nemenyi_critical_difference(n_methods: int, n_instances: int, alpha: float = 0.05) -> float:
    """
    Compute Nemenyi critical difference.
    """
    # Q-alpha values for Nemenyi test (approximation)
    q_alpha_values = {
        2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 
        7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164
    }
    
    q_alpha = q_alpha_values.get(n_methods, 2.569 + 0.1 * (n_methods - 4))
    
    cd = q_alpha * np.sqrt(n_methods * (n_methods + 1) / (6 * n_instances))
    return cd


def compute_average_ranks(gap_df: pd.DataFrame) -> pd.Series:
    """Compute average ranks for each method."""
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    pivot = pivot.dropna()
    
    if pivot.empty:
        return pd.Series(dtype=float)
    
    ranks = pivot.rank(axis=1)
    avg_ranks = ranks.mean().sort_values()
    
    return avg_ranks


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> Tuple[float, str]:
    """
    Compute Cliff's Delta effect size.
    Returns (delta, interpretation).
    """
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return 0.0, 'negligible'
    
    greater = sum(xi > yi for xi in x for yi in y)
    less = sum(xi < yi for xi in x for yi in y)
    
    delta = (greater - less) / (n1 * n2)
    
    # Interpretation
    abs_delta = abs(delta)
    if abs_delta < 0.147:
        interpretation = 'negligible'
    elif abs_delta < 0.33:
        interpretation = 'small'
    elif abs_delta < 0.474:
        interpretation = 'medium'
    else:
        interpretation = 'large'
    
    return delta, interpretation


def compute_effect_sizes(gap_df: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise Cliff's Delta effect sizes."""
    methods = sorted(gap_df['Method'].unique())
    
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    
    effect_sizes = pd.DataFrame(index=methods, columns=methods, dtype=object)
    
    for m1, m2 in combinations(methods, 2):
        if m1 in pivot.columns and m2 in pivot.columns:
            delta, interp = cliffs_delta(pivot[m1].dropna().values, 
                                         pivot[m2].dropna().values)
            effect_sizes.loc[m1, m2] = f"{delta:.3f} ({interp})"
            effect_sizes.loc[m2, m1] = f"{-delta:.3f} ({interp})"
    
    for m in methods:
        effect_sizes.loc[m, m] = "0.000 (negligible)"
    
    return effect_sizes


def bootstrap_confidence_interval(data: np.ndarray, n_bootstrap: int = None,
                                   confidence: float = 0.95) -> Tuple[float, float]:
    """Compute bootstrap confidence interval for the mean."""
    if n_bootstrap is None:
        n_bootstrap = CONFIG.bootstrap_n
    
    if len(data) == 0:
        return (np.nan, np.nan)
    
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))
    
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, alpha / 2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)
    
    return (lower, upper)


def compute_performance_profile(gap_df: pd.DataFrame, tau_max: float = None,
                                 n_points: int = 100) -> pd.DataFrame:
    """Compute Dolan-Moré performance profiles."""
    if tau_max is None:
        tau_max = CONFIG.tau_max
    
    methods = sorted(gap_df['Method'].unique())
    instances = gap_df['Instance'].unique()
    n_instances = len(instances)
    
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    
    # Find best gap per instance
    best_per_instance = pivot.min(axis=1)
    
    # Compute performance ratios
    eps = 1e-10
    ratios = pivot.div(best_per_instance + eps, axis=0)
    
    # Fix optimal solutions
    for col in ratios.columns:
        ratios.loc[pivot[col] == best_per_instance, col] = 1.0
    
    ratios = ratios.replace([np.inf, -np.inf], tau_max + 1)
    ratios = ratios.fillna(tau_max + 1)
    
    tau_values = np.linspace(1.0, tau_max, n_points)
    
    profile_data = {'tau': tau_values}
    
    for method in methods:
        if method not in ratios.columns:
            continue
        
        method_ratios = ratios[method].values
        probs = [np.sum(method_ratios <= tau) / n_instances for tau in tau_values]
        profile_data[method] = probs
    
    return pd.DataFrame(profile_data)


# =============================================================================
# PARETO ANALYSIS
# =============================================================================

def identify_pareto_optimal(gap_df: pd.DataFrame) -> List[str]:
    """Identify Pareto-optimal methods (non-dominated in time-quality space)."""
    stats_df = gap_df.groupby('Method').agg({
        'Gap': 'mean',
        'Time': 'mean'
    }).reset_index()
    
    pareto_optimal = []
    
    for i, row_i in stats_df.iterrows():
        is_dominated = False
        for j, row_j in stats_df.iterrows():
            if i == j:
                continue
            # row_j dominates row_i if better in both dimensions
            if row_j['Gap'] <= row_i['Gap'] and row_j['Time'] <= row_i['Time']:
                if row_j['Gap'] < row_i['Gap'] or row_j['Time'] < row_i['Time']:
                    is_dominated = True
                    break
        
        if not is_dominated:
            pareto_optimal.append(row_i['Method'])
    
    return pareto_optimal


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_pareto_frontier(gap_df: pd.DataFrame, output_dir: Path):
    """
    Plot Pareto frontier: Time vs Gap with dominated region shading.
    """
    if gap_df.empty:
        return
    
    stats_df = gap_df.groupby('Method').agg({
        'Gap': 'mean',
        'Time': 'mean'
    }).reset_index()
    
    pareto_methods = identify_pareto_optimal(gap_df)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot all methods
    for _, row in stats_df.iterrows():
        method = row['Method']
        color = METHOD_COLORS.get(method, '#808080')
        marker = METHOD_MARKERS.get(method, 'o')
        is_pareto = method in pareto_methods
        
        ax.scatter(row['Time'], row['Gap'],
                   s=200 if is_pareto else 120,
                   c=color,
                   marker=marker,
                   edgecolor='gold' if is_pareto else '#333333',
                   linewidth=3 if is_pareto else 1,
                   zorder=10 if is_pareto else 5,
                   label=f"{method}{'★' if is_pareto else ''}")
    
    # Draw Pareto frontier line
    pareto_stats = stats_df[stats_df['Method'].isin(pareto_methods)].sort_values('Time')
    if len(pareto_stats) > 1:
        ax.plot(pareto_stats['Time'], pareto_stats['Gap'],
                'k--', linewidth=1.5, alpha=0.7, zorder=1)
    
    # Shade dominated region (simplified)
    if len(pareto_stats) >= 1:
        x_max = stats_df['Time'].max() * 1.1
        y_max = stats_df['Gap'].max() * 1.1
        
        # Find the "ideal" corner (lowest time, lowest gap on frontier)
        for idx, prow in pareto_stats.iterrows():
            rect_x = prow['Time']
            rect_y = prow['Gap']
            ax.fill([rect_x, x_max, x_max, rect_x], 
                    [rect_y, rect_y, y_max, y_max],
                    alpha=0.05, color='red')
    
    ax.set_xlabel('Tempo Médio (s)')
    ax.set_ylabel('Gap Médio para BKS (%)')
    ax.set_title('Fronteira de Pareto: Trade-off Tempo-Qualidade')
    
    # Usar escala log se tempo varia significativamente
    if stats_df['Time'].max() / (stats_df['Time'].min() + 1e-10) > 100:
        ax.set_xscale('log')
    
    ax.legend(loc='upper right', framealpha=0.95, fontsize=8)
    
    # Adicionar anotação para ponto ideal
    ax.annotate('← Ideal\n(rápido e preciso)', 
                xy=(stats_df['Time'].min(), stats_df['Gap'].min()),
                xytext=(15, 15), textcoords='offset points',
                fontsize=8, alpha=0.6,
                arrowprops=dict(arrowstyle='->', alpha=0.4))
    
    save_figure(fig, output_dir, '01_pareto_frontier')


def plot_radar_chart(gap_df: pd.DataFrame, output_dir: Path):
    """
    Plot radar chart comparing methods across multiple metrics.
    """
    if gap_df.empty:
        return
    
    methods = sorted(gap_df['Method'].unique())
    n_methods = len(methods)
    
    if n_methods < 2:
        return
    
    # Compute metrics
    gap_means = gap_df.groupby('Method')['Gap'].mean()
    time_means = gap_df.groupby('Method')['Time'].mean()
    consistency = compute_consistency_index(gap_df)
    win_rates = compute_win_rates(gap_df)
    podium_rates = compute_podium_rates(gap_df)
    
    # Normalize metrics to [0, 1] where 1 is best
    def normalize(series, higher_is_better=True):
        if series.max() == series.min():
            return pd.Series(0.5, index=series.index)
        norm = (series - series.min()) / (series.max() - series.min())
        return norm if higher_is_better else 1 - norm
    
    metrics = {
        'Qualidade\n(1-Gap)': normalize(gap_means, higher_is_better=False),
        'Velocidade\n(1/Tempo)': normalize(time_means, higher_is_better=False),
        'Consistência': normalize(consistency),
        'Taxa Vitória': normalize(pd.Series(win_rates)),
        'Taxa Pódio': normalize(pd.Series(podium_rates)),
    }
    
    # Tentar adicionar escalabilidade
    scalability = compute_scalability_index(gap_df)
    if not scalability.empty and len(scalability) >= n_methods // 2:
        metrics['Escalabilidade'] = normalize(scalability, higher_is_better=False)
    
    metric_names = list(metrics.keys())
    n_metrics = len(metric_names)
    
    # Compute angles
    angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for method in methods:
        values = [metrics[m].get(method, 0) for m in metric_names]
        values += values[:1]  # Close the polygon
        
        color = METHOD_COLORS.get(method, '#808080')
        ax.plot(angles, values, 'o-', linewidth=2, label=method, color=color, markersize=4)
        ax.fill(angles, values, alpha=0.1, color=color)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_names, size=10)
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], size=8, alpha=0.7)
    ax.set_title('Comparação Multi-Métrica dos Métodos', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
    
    save_figure(fig, output_dir, '02_radar_comparison')


def plot_gap_violin(gap_df: pd.DataFrame, output_dir: Path):
    """
    Enhanced violin plot with strip overlay and statistical annotations.
    """
    if gap_df.empty:
        return
    
    methods = gap_df.groupby('Method')['Gap'].median().sort_values().index.tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create violin plot
    parts = ax.violinplot(
        [gap_df[gap_df['Method'] == m]['Gap'].values for m in methods],
        positions=range(len(methods)),
        showmeans=False,
        showmedians=False,
        widths=0.8
    )
    
    # Color the violins
    for i, (pc, method) in enumerate(zip(parts['bodies'], methods)):
        color = METHOD_COLORS.get(method, '#808080')
        pc.set_facecolor(color)
        pc.set_alpha(0.4)
        pc.set_edgecolor(color)
        pc.set_linewidth(1.5)
    
    for partname in ['cbars', 'cmins', 'cmaxes']:
        if partname in parts:
            parts[partname].set_visible(False)
    
    # Add boxplot inside
    bp = ax.boxplot(
        [gap_df[gap_df['Method'] == m]['Gap'].values for m in methods],
        positions=range(len(methods)),
        widths=0.15,
        patch_artist=True,
        showfliers=False,
        medianprops={'color': 'black', 'linewidth': 2},
        boxprops={'facecolor': 'white', 'alpha': 0.8},
        whiskerprops={'color': '#333333'},
        capprops={'color': '#333333'}
    )
    
    # Add strip plot (jittered points)
    for i, method in enumerate(methods):
        data = gap_df[gap_df['Method'] == method]['Gap'].values
        x = np.random.normal(i, 0.04, len(data))
        color = METHOD_COLORS.get(method, '#808080')
        ax.scatter(x, data, alpha=0.3, s=15, color=color, edgecolor='none')
    
    # Add mean markers
    for i, method in enumerate(methods):
        mean_val = gap_df[gap_df['Method'] == method]['Gap'].mean()
        ax.scatter(i, mean_val, marker='D', s=50, color='white', 
                   edgecolor='black', zorder=10, linewidth=1.5)
    
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, rotation=30, ha='right')
    ax.set_ylabel('Gap para BKS (%)')
    ax.set_xlabel('Método')
    ax.set_title('Distribuição de Gap por Método (ordenado por mediana)')
    
    # Linha de referência em 0
    ax.axhline(y=0, color='#55A868', linestyle='--', linewidth=1.5, alpha=0.8)
    
    # Adicionar anotação de n
    n_instances = gap_df['Instance'].nunique()
    ax.annotate(f'n = {n_instances} instâncias', 
                xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=9, alpha=0.7, va='top')
    
    save_figure(fig, output_dir, '03_gap_distribution')


def plot_performance_profile(profile_df: pd.DataFrame, output_dir: Path):
    """Enhanced Dolan-Moré performance profile."""
    if profile_df.empty or len(profile_df.columns) < 2:
        return
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    methods = [col for col in profile_df.columns if col != 'tau']
    
    for method in methods:
        color = METHOD_COLORS.get(method, '#808080')
        marker = METHOD_MARKERS.get(method, 'o')
        ax.plot(profile_df['tau'], profile_df[method],
                label=method, linewidth=2, color=color,
                marker=marker, markevery=10, markersize=6)
    
    ax.set_xlabel(r'Razão de desempenho $\tau$')
    ax.set_ylabel(r'$P(r_{i,m} \leq \tau)$ — Probabilidade de estar dentro de $\tau$ do melhor')
    ax.set_title('Perfil de Desempenho (Dolan-Moré)')
    ax.set_xlim(1, profile_df['tau'].max())
    ax.set_ylim(0, 1.05)
    
    ax.legend(loc='lower right', framealpha=0.95)
    
    # Adicionar linha vertical em tau=1 (ótimo)
    ax.axvline(x=1, color='#cccccc', linestyle=':', linewidth=1)
    ax.annotate('τ=1\n(ótimo)', xy=(1.05, 0.1), fontsize=8, alpha=0.7)
    
    save_figure(fig, output_dir, '04_performance_profile')


def plot_critical_difference(gap_df: pd.DataFrame, output_dir: Path):
    """
    Plot critical difference diagram (Nemenyi test visualization).
    """
    if gap_df.empty:
        return
    
    methods = sorted(gap_df['Method'].unique())
    n_methods = len(methods)
    
    if n_methods < 2:
        return
    
    # Compute average ranks
    avg_ranks = compute_average_ranks(gap_df)
    
    if avg_ranks.empty:
        return
    
    n_instances = gap_df['Instance'].nunique()
    
    if n_instances < 3:
        return
    
    # Compute critical difference
    cd = nemenyi_critical_difference(n_methods, n_instances)
    
    fig, ax = plt.subplots(figsize=(10, max(3, n_methods * 0.5)))
    
    # Draw axis
    min_rank, max_rank = 1, n_methods
    ax.set_xlim(min_rank - 0.5, max_rank + 0.5)
    ax.set_ylim(-1, len(avg_ranks) + 0.5)
    
    # Draw horizontal axis
    ax.axhline(y=0, xmin=0, xmax=1, color='black', linewidth=1.5)
    
    # Draw tick marks
    for i in range(1, n_methods + 1):
        ax.plot([i, i], [-0.1, 0.1], 'k-', linewidth=1)
        ax.text(i, -0.4, str(i), ha='center', va='top', fontsize=10)
    
    # Draw methods
    y_positions = {}
    for i, (method, rank) in enumerate(avg_ranks.items()):
        y = i + 1
        y_positions[method] = y
        color = METHOD_COLORS.get(method, '#808080')
        
        # Draw line from axis to method position
        ax.plot([rank, rank], [0, y * 0.4], color=color, linewidth=2, alpha=0.8)
        ax.scatter(rank, y * 0.4, s=100, color=color, zorder=10, edgecolor='black')
        
        # Method label
        if rank < (min_rank + max_rank) / 2:
            ax.text(rank + 0.15, y * 0.4, f' {method} ({rank:.2f})', 
                   va='center', fontsize=9, color=color)
        else:
            ax.text(rank - 0.15, y * 0.4, f'{method} ({rank:.2f}) ', 
                   va='center', ha='right', fontsize=9, color=color)
    
    # Draw CD bar at top
    cd_y = -0.7
    ax.plot([1, 1 + cd], [cd_y, cd_y], 'k-', linewidth=2)
    ax.plot([1, 1], [cd_y - 0.1, cd_y + 0.1], 'k-', linewidth=2)
    ax.plot([1 + cd, 1 + cd], [cd_y - 0.1, cd_y + 0.1], 'k-', linewidth=2)
    ax.text(1 + cd / 2, cd_y - 0.25, f'CD = {cd:.2f}', ha='center', fontsize=9)
    
    # Draw connections between non-significantly different methods
    sorted_methods = avg_ranks.index.tolist()
    connection_y = len(avg_ranks) * 0.4 + 0.3
    for i, m1 in enumerate(sorted_methods):
        for m2 in sorted_methods[i+1:]:
            if abs(avg_ranks[m1] - avg_ranks[m2]) < cd:
                # Draw thick bar connecting these methods
                x1, x2 = avg_ranks[m1], avg_ranks[m2]
                ax.plot([x1, x2], [connection_y, connection_y], 
                       color='gray', linewidth=6, alpha=0.4, solid_capstyle='round')
        connection_y += 0.15
    
    ax.set_title(f'Diagrama de Diferença Crítica (n={n_instances}, α=0.05)')
    ax.text((min_rank + max_rank) / 2, -0.9, 'Ranking Médio (menor é melhor)', 
            ha='center', fontsize=10)
    
    ax.axis('off')
    
    save_figure(fig, output_dir, '05_critical_difference')


def plot_instance_difficulty(gap_df: pd.DataFrame, output_dir: Path):
    """
    Scatter plot classifying instance difficulty.
    """
    if gap_df.empty:
        return
    
    instance_stats = compute_instance_difficulty(gap_df)
    
    if instance_stats.empty:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Cor por classe de dificuldade
    colors = {'Fácil': '#55A868', 'Médio': '#F0E442', 'Difícil': '#E69F00', 'Muito Difícil': '#CC79A7'}
    
    for diff_class in ['Fácil', 'Médio', 'Difícil', 'Muito Difícil']:
        subset = instance_stats[instance_stats['DifficultyClass'] == diff_class]
        if not subset.empty:
            ax.scatter(subset['Hardness'], subset['DiscriminatoryPower'],
                       s=80, c=colors[diff_class], label=diff_class,
                       alpha=0.7, edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Dificuldade da Instância (Gap Médio entre métodos, %)')
    ax.set_ylabel('Poder Discriminatório (CV dos Gaps)')
    ax.set_title('Classificação de Dificuldade das Instâncias')
    
    ax.legend(title='Dificuldade', loc='upper right')
    
    # Adicionar linhas verticais para limiares de dificuldade
    for thresh, label in [(1, 'Fácil/Médio'), (5, 'Médio/Difícil'), (10, 'Difícil/M.Difícil')]:
        if thresh < instance_stats['Hardness'].max():
            ax.axvline(x=thresh, color='gray', linestyle=':', alpha=0.5)
    
    save_figure(fig, output_dir, '06_instance_difficulty')


def plot_method_affinity_heatmap(gap_df: pd.DataFrame, output_dir: Path):
    """
    Heatmap showing method-instance class affinity.
    """
    if gap_df.empty:
        return
    
    # Parse instance classes
    gap_df = gap_df.copy()
    parsed = gap_df['Instance'].apply(parse_instance_info)
    gap_df['Size'] = parsed.apply(lambda x: x['size'])
    
    # Group by size if available
    gap_df = gap_df[gap_df['Size'].notna()]
    if gap_df.empty:
        return
    
    # Create size groups
    gap_df['SizeGroup'] = pd.cut(gap_df['Size'], 
                                  bins=[0, 3, 6, 10, 15, 20, 100],
                                  labels=['1-3', '4-6', '7-10', '11-15', '16-20', '20+'])
    
    # Compute average gap per method per size group
    pivot = gap_df.pivot_table(values='Gap', index='Method', 
                                columns='SizeGroup', aggfunc='mean')
    
    if pivot.empty or pivot.shape[1] < 2:
        return
    
    # Normalize per column (class)
    pivot_norm = (pivot - pivot.min()) / (pivot.max() - pivot.min() + 1e-10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    im = ax.imshow(pivot_norm.values, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(np.arange(len(pivot_norm.columns)))
    ax.set_yticks(np.arange(len(pivot_norm.index)))
    ax.set_xticklabels(pivot_norm.columns)
    ax.set_yticklabels(pivot_norm.index)
    
    # Add value annotations
    for i in range(len(pivot_norm.index)):
        for j in range(len(pivot_norm.columns)):
            val = pivot.iloc[i, j]
            if not np.isnan(val):
                text_color = 'white' if pivot_norm.iloc[i, j] > 0.5 else 'black'
                ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                        color=text_color, fontsize=9)
    
    ax.set_xlabel('Grupo de Tamanho da Instância')
    ax.set_ylabel('Método')
    ax.set_title('Afinidade Método-Instância (Gap %)')
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Gap Normalizado (0=melhor, 1=pior)', fontsize=9)
    
    save_figure(fig, output_dir, '07_method_affinity_heatmap')


def plot_dominance_matrix(gap_df: pd.DataFrame, output_dir: Path):
    """
    Heatmap of pairwise dominance scores.
    """
    if gap_df.empty:
        return
    
    dominance = compute_dominance_matrix(gap_df)
    
    if dominance.empty:
        return
    
    fig, ax = plt.subplots(figsize=(8, 7))
    
    im = ax.imshow(dominance.values.astype(float), cmap='RdYlGn', 
                   aspect='equal', vmin=0, vmax=1)
    
    ax.set_xticks(np.arange(len(dominance.columns)))
    ax.set_yticks(np.arange(len(dominance.index)))
    ax.set_xticklabels(dominance.columns, rotation=45, ha='right')
    ax.set_yticklabels(dominance.index)
    
    # Add value annotations
    for i in range(len(dominance.index)):
        for j in range(len(dominance.columns)):
            if i != j:
                val = dominance.iloc[i, j]
                text_color = 'white' if val > 0.6 else 'black'
                weight = 'bold' if val >= CONFIG.dominance_threshold else 'normal'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                        color=text_color, fontsize=9, fontweight=weight)
    
    ax.set_xlabel('Método B')
    ax.set_ylabel('Método A')
    ax.set_title(f'Matriz de Dominância (A→B: Taxa de Vitória de A sobre B)\nLimiar: {CONFIG.dominance_threshold:.0%}')
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Taxa de Vitória', fontsize=9)
    
    save_figure(fig, output_dir, '08_dominance_matrix')


def plot_time_distribution(df: pd.DataFrame, output_dir: Path):
    """
    Enhanced time distribution with log scale and annotations.
    """
    if df.empty:
        return
    
    methods = df.groupby('Method')['Time'].median().sort_values().index.tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Violin plot for time
    parts = ax.violinplot(
        [df[df['Method'] == m]['Time'].values for m in methods],
        positions=range(len(methods)),
        showmeans=True,
        showmedians=True,
        widths=0.7
    )
    
    for i, (pc, method) in enumerate(zip(parts['bodies'], methods)):
        color = METHOD_COLORS.get(method, '#808080')
        pc.set_facecolor(color)
        pc.set_alpha(0.5)
        pc.set_edgecolor(color)
    
    for partname in ['cbars', 'cmins', 'cmaxes', 'cmeans', 'cmedians']:
        if partname in parts:
            parts[partname].set_edgecolor('#333333')
    
    ax.set_yscale('log')
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, rotation=30, ha='right')
    ax.set_ylabel('Tempo de Execução (s) [escala log]')
    ax.set_xlabel('Método')
    ax.set_title('Distribuição do Tempo de Execução')
    
    # Add median annotations
    for i, method in enumerate(methods):
        median_time = df[df['Method'] == method]['Time'].median()
        ax.annotate(f'{median_time:.3f}s', xy=(i, median_time * 1.5),
                    ha='center', fontsize=8, alpha=0.8)
    
    save_figure(fig, output_dir, '10_time_distribution')


def plot_executive_dashboard(gap_df: pd.DataFrame, df: pd.DataFrame, output_dir: Path):
    """
    Multi-panel executive summary dashboard.
    """
    if gap_df.empty:
        return
    
    methods = sorted(gap_df['Method'].unique())
    
    fig = plt.figure(figsize=(14, 10))
    
    # Layout: 2x3 grid
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    
    # Panel A: Ranking bar chart (horizontal)
    ax1 = fig.add_subplot(gs[0, 0])
    avg_gap = gap_df.groupby('Method')['Gap'].mean().sort_values()
    colors = [METHOD_COLORS.get(m, '#808080') for m in avg_gap.index]
    bars = ax1.barh(range(len(avg_gap)), avg_gap.values, color=colors, alpha=0.8)
    ax1.set_yticks(range(len(avg_gap)))
    ax1.set_yticklabels(avg_gap.index, fontsize=8)
    ax1.set_xlabel('Gap Médio (%)')
    ax1.set_title('A) Ranking dos Métodos', fontsize=10, fontweight='bold')
    ax1.invert_yaxis()
    
    # Add value labels
    for i, (method, gap) in enumerate(avg_gap.items()):
        ax1.text(gap + 0.1, i, f'{gap:.2f}%', va='center', fontsize=7)
    
    # Panel B: Win rate pie/donut chart
    ax2 = fig.add_subplot(gs[0, 1])
    win_rates = compute_win_rates(gap_df)
    win_values = [win_rates[m] for m in methods]
    colors = [METHOD_COLORS.get(m, '#808080') for m in methods]
    
    wedges, texts, autotexts = ax2.pie(win_values, autopct='%1.0f%%',
                                        colors=colors, pctdistance=0.75,
                                        wedgeprops=dict(width=0.5, edgecolor='white'))
    for autotext in autotexts:
        autotext.set_fontsize(7)
    ax2.set_title('B) Distribuição Taxa de Vitória', fontsize=10, fontweight='bold')
    ax2.legend(methods, loc='center left', bbox_to_anchor=(0.9, 0.5), fontsize=7)
    
    # Panel C: Time-Quality scatter
    ax3 = fig.add_subplot(gs[0, 2])
    stats_agg = gap_df.groupby('Method').agg({'Gap': 'mean', 'Time': 'mean'})
    pareto = identify_pareto_optimal(gap_df)
    
    for method in methods:
        if method not in stats_agg.index:
            continue
        color = METHOD_COLORS.get(method, '#808080')
        is_pareto = method in pareto
        ax3.scatter(stats_agg.loc[method, 'Time'], stats_agg.loc[method, 'Gap'],
                    s=120 if is_pareto else 80, c=color,
                    edgecolor='gold' if is_pareto else 'black',
                    linewidth=2 if is_pareto else 1, label=method)
    
    ax3.set_xlabel('Tempo Médio (s)', fontsize=9)
    ax3.set_ylabel('Gap Médio (%)', fontsize=9)
    ax3.set_title('C) Trade-off Tempo-Qualidade', fontsize=10, fontweight='bold')
    if stats_agg['Time'].max() / (stats_agg['Time'].min() + 1e-10) > 10:
        ax3.set_xscale('log')
    
    # Panel D: Performance profile
    ax4 = fig.add_subplot(gs[1, 0])
    profile_df = compute_performance_profile(gap_df)
    for method in [c for c in profile_df.columns if c != 'tau']:
        color = METHOD_COLORS.get(method, '#808080')
        ax4.plot(profile_df['tau'], profile_df[method], label=method,
                 linewidth=1.5, color=color)
    ax4.set_xlabel('τ', fontsize=9)
    ax4.set_ylabel('P(razão ≤ τ)', fontsize=9)
    ax4.set_title('D) Perfil de Desempenho', fontsize=10, fontweight='bold')
    ax4.set_xlim(1, CONFIG.tau_max)
    ax4.set_ylim(0, 1.05)
    ax4.legend(fontsize=6, loc='lower right')
    
    # Panel E: Time comparison bar
    ax5 = fig.add_subplot(gs[1, 1])
    avg_time = df.groupby('Method')['Time'].mean().sort_values()
    colors = [METHOD_COLORS.get(m, '#808080') for m in avg_time.index]
    ax5.bar(range(len(avg_time)), avg_time.values, color=colors, alpha=0.8)
    ax5.set_xticks(range(len(avg_time)))
    ax5.set_xticklabels(avg_time.index, rotation=45, ha='right', fontsize=7)
    ax5.set_ylabel('Tempo Médio (s)', fontsize=9)
    ax5.set_title('E) Tempo Médio de Execução', fontsize=10, fontweight='bold')
    if avg_time.max() / (avg_time.min() + 1e-10) > 10:
        ax5.set_yscale('log')
    
    # Painel F: Tabela resumo de métricas
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    
    # Criar tabela resumo
    table_data = []
    consistency = compute_consistency_index(gap_df)
    
    for method in sorted(methods):
        row = [
            method[:12],
            f"{avg_gap.get(method, 0):.2f}%",
            f"{win_rates.get(method, 0):.0f}%",
            f"{consistency.get(method, 0):.2f}",
            '★' if method in pareto else ''
        ]
        table_data.append(row)
    
    table = ax6.table(cellText=table_data,
                      colLabels=['Método', 'Gap', 'Vit.', 'Consist.', 'P'],
                      loc='center',
                      cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.4)
    ax6.set_title('F) Resumo das Métricas', fontsize=10, fontweight='bold', pad=10)
    
    fig.suptitle('Heurísticas DCKP - Sumário Executivo', fontsize=14, fontweight='bold')
    
    save_figure(fig, output_dir, '09_executive_dashboard')


def plot_etapa_comparison(results: Dict[str, pd.DataFrame], output_dir: Path):
    """
    Comparar desempenho Etapa 1 vs Etapa 2.
    """
    if 'etapa1' not in results or 'etapa2' not in results:
        print("    [PULAR] Necessário etapa1 e etapa2 para comparação")
        return
    
    df1 = results['etapa1']
    df2 = results['etapa2']
    
    # Encontrar instâncias em comum
    common_instances = set(df1['Instance'].unique()) & set(df2['Instance'].unique())
    
    if not common_instances:
        print("    [PULAR] Nenhuma instância em comum entre as etapas")
        return
    
    # Obter melhor lucro por instância para cada etapa
    best1 = df1[df1['Instance'].isin(common_instances)].groupby('Instance')['Profit'].max()
    best2 = df2[df2['Instance'].isin(common_instances)].groupby('Instance')['Profit'].max()
    
    # Calcular melhoria
    improvement = ((best2 - best1) / best1 * 100).dropna()
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Esquerda: Distribuição de melhorias
    ax1 = axes[0]
    ax1.hist(improvement.values, bins=20, color='#0072B2', alpha=0.7, edgecolor='black')
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='Sem alteração')
    ax1.axvline(x=improvement.median(), color='green', linestyle='-', linewidth=2,
                label=f'Mediana: {improvement.median():.1f}%')
    ax1.set_xlabel('Melhoria (%)')
    ax1.set_ylabel('Número de Instâncias')
    ax1.set_title('A) Etapa 2 vs Etapa 1: Distribuição de Melhoria')
    ax1.legend()
    
    # Anotação de estatísticas
    pos_imp = (improvement > 0).sum()
    neg_imp = (improvement < 0).sum()
    ax1.annotate(f'Melhorou: {pos_imp} ({pos_imp/len(improvement)*100:.1f}%)\n'
                 f'Piorou: {neg_imp} ({neg_imp/len(improvement)*100:.1f}%)',
                 xy=(0.95, 0.95), xycoords='axes fraction',
                 ha='right', va='top', fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Direita: Gráfico de dispersão
    ax2 = axes[1]
    ax2.scatter(best1.values, best2.values, alpha=0.6, edgecolor='black', linewidth=0.5)
    
    # Linha diagonal (sem mudança)
    lims = [min(best1.min(), best2.min()), max(best1.max(), best2.max())]
    ax2.plot(lims, lims, 'k--', alpha=0.5, label='Sem alteração')
    ax2.set_xlabel('Melhor Lucro Etapa 1')
    ax2.set_ylabel('Melhor Lucro Etapa 2')
    ax2.set_title('B) Comparação de Melhor Lucro')
    ax2.legend()
    
    plt.suptitle('Comparação de Etapas: Melhorias da Busca Local', fontsize=12, fontweight='bold')
    
    save_figure(fig, output_dir, '11_etapa1_vs_etapa2')


def plot_improvement_analysis(gap_df: pd.DataFrame, output_dir: Path):
    """
    Analyze improvement from initial solution to local search.
    Specific to Etapa 2 methods.
    """
    if gap_df.empty:
        return
    
    methods = gap_df['Method'].unique()
    
    # Check if we have the expected Etapa 2 methods
    if 'GRASP_Inicial' not in methods:
        return
    
    instances = gap_df['Instance'].unique()
    
    improvements = []
    for instance in instances:
        inst_df = gap_df[gap_df['Instance'] == instance]
        
        initial = inst_df[inst_df['Method'] == 'GRASP_Inicial']['Profit'].values
        if len(initial) == 0:
            continue
        initial = initial[0]
        
        for method in ['HillClimbing', 'VND']:
            if method in inst_df['Method'].values:
                final = inst_df[inst_df['Method'] == method]['Profit'].values[0]
                imp = (final - initial) / initial * 100 if initial > 0 else 0
                improvements.append({
                    'Instance': instance,
                    'Method': method,
                    'Initial': initial,
                    'Final': final,
                    'Improvement': imp
                })
    
    if not improvements:
        return
    
    imp_df = pd.DataFrame(improvements)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Improvement distribution by method
    ax1 = axes[0]
    for method in ['HillClimbing', 'VND']:
        data = imp_df[imp_df['Method'] == method]['Improvement'].values
        if len(data) > 0:
            color = METHOD_COLORS.get(method, '#808080')
            ax1.hist(data, bins=20, alpha=0.6, label=method, color=color, edgecolor='black')
    
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=1.5)
    ax1.set_xlabel('Melhoria sobre GRASP Inicial (%)')
    ax1.set_ylabel('Número de Instâncias')
    ax1.set_title('A) Distribuição de Melhoria da Busca Local')
    ax1.legend()
    
    # Direita: Boxplot comparativo
    ax2 = axes[1]
    methods_present = [m for m in ['HillClimbing', 'VND'] if m in imp_df['Method'].values]
    colors = [METHOD_COLORS.get(m, '#808080') for m in methods_present]
    
    bp = ax2.boxplot([imp_df[imp_df['Method'] == m]['Improvement'].values for m in methods_present],
                      labels=methods_present, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1.5)
    ax2.set_ylabel('Melhoria (%)')
    ax2.set_title('B) Comparação de Melhoria')
    
    # Adicionar anotações de média
    for i, method in enumerate(methods_present):
        mean_imp = imp_df[imp_df['Method'] == method]['Improvement'].mean()
        ax2.annotate(f'μ={mean_imp:.1f}%', xy=(i + 1, mean_imp), fontsize=9)
    
    plt.suptitle('Análise de Melhoria da Busca Local', fontsize=12, fontweight='bold')
    
    save_figure(fig, output_dir, '12_improvement_analysis')


def plot_correlation_matrix(gap_df: pd.DataFrame, df: pd.DataFrame, output_dir: Path):
    """
    Plot correlation matrix between metrics.
    """
    if gap_df.empty:
        return
    
    # Prepare data at instance level
    instance_data = []
    
    for instance in gap_df['Instance'].unique():
        inst_gap = gap_df[gap_df['Instance'] == instance]
        inst_df = df[df['Instance'] == instance]
        
        info = parse_instance_info(instance)
        
        row = {
            'Instance': instance,
            'Size': info['size'] if info['size'] else np.nan,
            'AvgGap': inst_gap['Gap'].mean(),
            'MinGap': inst_gap['Gap'].min(),
            'MaxGap': inst_gap['Gap'].max(),
            'StdGap': inst_gap['Gap'].std(),
            'AvgTime': inst_df['Time'].mean(),
            'BKS': inst_gap['BKS'].iloc[0] if 'BKS' in inst_gap.columns else np.nan
        }
        instance_data.append(row)
    
    instance_df = pd.DataFrame(instance_data)
    
    # Select numeric columns
    numeric_cols = ['Size', 'AvgGap', 'MinGap', 'MaxGap', 'StdGap', 'AvgTime', 'BKS']
    numeric_df = instance_df[numeric_cols].dropna(axis=1, how='all')
    
    if numeric_df.shape[1] < 2:
        return
    
    # Compute correlation
    corr = numeric_df.corr()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    im = ax.imshow(corr.values, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    
    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr.index)
    
    # Add annotations
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            val = corr.iloc[i, j]
            color = 'white' if abs(val) > 0.5 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=9)
    
    ax.set_title('Matriz de Correlação')
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Correlação', fontsize=9)
    
    save_figure(fig, output_dir, '13_correlation_matrix')


def plot_cdf_comparison(gap_df: pd.DataFrame, output_dir: Path):
    """
    Plot cumulative distribution functions of gaps.
    """
    if gap_df.empty:
        return
    
    methods = sorted(gap_df['Method'].unique())
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for method in methods:
        data = gap_df[gap_df['Method'] == method]['Gap'].values
        sorted_data = np.sort(data)
        cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
        
        color = METHOD_COLORS.get(method, '#808080')
        ax.plot(sorted_data, cdf, label=method, linewidth=2, color=color)
    
    ax.set_xlabel('Gap para BKS (%)')
    ax.set_ylabel('Probabilidade Acumulada')
    ax.set_title('CDF da Distribuição de Gap')
    ax.legend(loc='lower right')
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.05)
    
    # Adicionar linhas de referência
    for thresh in [1, 5, 10]:
        if thresh < gap_df['Gap'].max():
            ax.axvline(x=thresh, color='gray', linestyle=':', alpha=0.5)
            ax.annotate(f'{thresh}%', xy=(thresh, 0.02), fontsize=8, alpha=0.7)
    
    save_figure(fig, output_dir, '14_cdf_comparison')


# =============================================================================
# FUNÇÕES DE EXPORTAÇÃO LaTeX
# =============================================================================

def export_latex_table(df: pd.DataFrame, output_file: Path, caption: str, label: str,
                       float_format: str = "%.2f"):
    """Exportar DataFrame como tabela LaTeX com estilo booktabs."""
    
    # Converter para LaTeX
    latex_str = df.to_latex(
        float_format=float_format,
        escape=False,
        column_format='l' + 'r' * len(df.columns),
    )
    
    # Adicionar comandos do pacote booktabs
    lines = latex_str.split('\n')
    new_lines = []
    for line in lines:
        if '\\toprule' in line or '\\midrule' in line or '\\bottomrule' in line:
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    latex_str = '\n'.join(new_lines)
    
    # Envolver em ambiente de tabela
    full_latex = f"""% Tabela LaTeX gerada automaticamente
% Requer: \\usepackage{{booktabs}}

\\begin{{table}}[htbp]
\\centering
\\caption{{{caption}}}
\\label{{{label}}}
{latex_str}
\\end{{table}}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_latex)
    
    print(f"    ✓ {output_file.name}")


def generate_latex_tables(gap_df: pd.DataFrame, df: pd.DataFrame, output_dir: Path):
    """Gerar todas as tabelas LaTeX."""
    latex_dir = output_dir / "latex"
    latex_dir.mkdir(exist_ok=True)
    
    methods = sorted(gap_df['Method'].unique())
    
    # Tabela de estatísticas resumidas
    summary_data = []
    win_rates = compute_win_rates(gap_df)
    consistency = compute_consistency_index(gap_df)
    
    for method in methods:
        method_gaps = gap_df[gap_df['Method'] == method]['Gap']
        method_times = df[df['Method'] == method]['Time']
        
        row = {
            'Método': method,
            'Gap Méd. (\\%)': f"{method_gaps.mean():.2f}",
            'Desvio Gap': f"{method_gaps.std():.2f}",
            'Mediana Gap': f"{method_gaps.median():.2f}",
            'Tempo Méd. (s)': f"{method_times.mean():.4f}",
            'Taxa Vit. (\\%)': f"{win_rates.get(method, 0):.1f}",
            'Consistência': f"{consistency.get(method, 0):.2f}"
        }
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data).set_index('Método')
    
    export_latex_table(
        summary_df,
        latex_dir / "table_summary.tex",
        caption="Estatísticas resumidas dos métodos heurísticos nas instâncias DCKP.",
        label="tab:summary"
    )
    
    # Matriz de dominância
    dominance = compute_dominance_matrix(gap_df)
    export_latex_table(
        dominance.round(2),
        latex_dir / "table_dominance.tex",
        caption="Matriz de dominância par-a-par (proporção de instâncias onde o método da linha supera o da coluna).",
        label="tab:dominance"
    )
    
    # Resultados de testes estatísticos
    friedman = friedman_test(gap_df)
    if friedman['statistic'] is not None:
        test_data = [{
            'Teste': 'Friedman',
            'Estatística': f"{friedman['statistic']:.2f}",
            'p-valor': f"{friedman['p_value']:.4e}",
            'Significativo': 'Sim' if friedman['significant'] else 'Não'
        }]
        test_df = pd.DataFrame(test_data).set_index('Teste')
        
        export_latex_table(
            test_df,
            latex_dir / "table_statistical_tests.tex",
            caption="Testes de significância estatística para comparação de métodos.",
            label="tab:tests"
        )


# =============================================================================
# PIPELINE PRINCIPAL DE ANÁLISE
# =============================================================================

def analyze_stage(stage: str, output_dir: Path) -> Optional[pd.DataFrame]:
    """Analisar uma única etapa."""
    results_dir = Path(f"results/{stage}")
    
    if not results_dir.exists():
        print(f"    [PULAR] {results_dir} não encontrado")
        return None
    
    df = load_all_results(results_dir)
    
    if df is None or df.empty:
        print(f"    [PULAR] Sem resultados em {results_dir}")
        return None
    
    print(f"\n  Analisando {stage}...")
    print(f"    Carregados {len(df)} resultados de {df['Instance'].nunique()} instâncias")
    print(f"    Métodos: {', '.join(sorted(df['Method'].unique()))}")
    
    # Assign colors
    assign_method_styles(df['Method'].unique().tolist())
    
    # Create output directory
    stage_output = output_dir / stage
    stage_output.mkdir(parents=True, exist_ok=True)
    
    # Compute gap dataframe
    gap_df = compute_gap_dataframe(df)
    
    # Gerar todas as visualizações
    print(f"\n    Gerando visualizações...")
    
    plot_pareto_frontier(gap_df, stage_output)
    plot_radar_chart(gap_df, stage_output)
    plot_gap_violin(gap_df, stage_output)
    
    profile_df = compute_performance_profile(gap_df)
    plot_performance_profile(profile_df, stage_output)
    
    plot_critical_difference(gap_df, stage_output)
    plot_instance_difficulty(gap_df, stage_output)
    plot_method_affinity_heatmap(gap_df, stage_output)
    plot_dominance_matrix(gap_df, stage_output)
    plot_executive_dashboard(gap_df, df, stage_output)
    plot_time_distribution(df, stage_output)
    plot_correlation_matrix(gap_df, df, stage_output)
    plot_cdf_comparison(gap_df, stage_output)
    
    # Gráficos específicos da etapa
    if stage == 'etapa2':
        plot_improvement_analysis(gap_df, stage_output)
    
    # Análise estatística
    print(f"\n    Executando testes estatísticos...")
    friedman = friedman_test(gap_df)
    if friedman['statistic'] is not None:
        sig = "***" if friedman['p_value'] < 0.001 else ("**" if friedman['p_value'] < 0.01 else ("*" if friedman['p_value'] < 0.05 else ""))
        print(f"      Friedman: χ²={friedman['statistic']:.2f}, p={friedman['p_value']:.4e} {sig}")
    
    # Calcular e salvar métricas
    print(f"\n    Calculando métricas...")
    
    dominance = compute_dominance_score(compute_dominance_matrix(gap_df))
    print(f"      Scores de dominância: {dict(dominance)}")
    
    win_rates = compute_win_rates(gap_df)
    print(f"      Taxas de vitória: {', '.join([f'{m}:{v:.1f}%' for m, v in sorted(win_rates.items(), key=lambda x: -x[1])])}")
    
    pareto = identify_pareto_optimal(gap_df)
    print(f"      Pareto-ótimos: {pareto}")
    
    # Gerar tabelas LaTeX
    print(f"\n    Gerando tabelas LaTeX...")
    generate_latex_tables(gap_df, df, stage_output)
    
    # Export data
    gap_df.to_csv(stage_output / "gap_analysis.csv", index=False)
    profile_df.to_csv(stage_output / "performance_profile.csv", index=False)
    
    # Save comprehensive metrics
    metrics = {
        'avg_gap': gap_df.groupby('Method')['Gap'].mean().to_dict(),
        'win_rates': win_rates,
        'consistency': compute_consistency_index(gap_df).to_dict(),
        'robustness': compute_robustness_score(gap_df).to_dict(),
        'pareto_optimal': pareto,
        'friedman_pvalue': friedman['p_value'] if friedman['p_value'] else None
    }
    
    pd.DataFrame([metrics]).to_json(stage_output / "metrics.json", indent=2)
    
    return gap_df


def main():
    """Pipeline principal de análise."""
    parser = argparse.ArgumentParser(description='Suite de Análise DCKP v2.0')
    parser.add_argument('--stage', '-s', choices=['etapa1', 'etapa2', 'all'], 
                        default='all', help='Qual etapa analisar')
    parser.add_argument('--output', '-o', default='results/analysis',
                        help='Diretório de saída')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print(" DCKP MATHEURISTICS - SUITE DE ANÁLISE PARA PUBLICAÇÃO v2.0")
    print("=" * 70)
    
    # Configurar estilo
    setup_publication_style()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Analisar etapas solicitadas
    if args.stage in ['etapa1', 'all']:
        gap1 = analyze_stage('etapa1', output_dir)
        if gap1 is not None:
            results['etapa1'] = load_all_results(Path("results/etapa1"))
    
    if args.stage in ['etapa2', 'all']:
        gap2 = analyze_stage('etapa2', output_dir)
        if gap2 is not None:
            results['etapa2'] = load_all_results(Path("results/etapa2"))
    
    # Análise cruzada entre etapas
    if len(results) == 2:
        print("\n  Gerando comparação entre etapas...")
        assign_method_styles(
            list(results['etapa1']['Method'].unique()) + 
            list(results['etapa2']['Method'].unique())
        )
        plot_etapa_comparison(results, output_dir)
    
    print("\n" + "=" * 70)
    print(" ANÁLISE CONCLUÍDA!")
    print(f" Resultados salvos em: {output_dir.absolute()}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
