#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publication-Quality Analysis of DCKP Heuristic Experiments

This script produces professional, minimalist visualizations suitable for
academic papers (LaTeX). It performs deep statistical analysis including:
- Overview statistics with rich summary tables
- Gap analysis with performance profiles (Dolan-Moré)
- Time analysis with log-scale distributions
- Instance-specific heatmaps
- Statistical significance tests (Wilcoxon, Friedman)

Author: Thalles e Luiz
"""

import warnings
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from scipy import stats

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# =============================================================================
# PUBLICATION-QUALITY STYLE CONFIGURATION
# =============================================================================

# Colorblind-friendly professional palette
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3"]

# Method-specific colors (will be assigned dynamically)
METHOD_COLORS: Dict[str, str] = {}

def setup_publication_style():
    """Configure matplotlib/seaborn for publication-quality figures."""
    # Use seaborn's colorblind palette as fallback
    sns.set_palette("colorblind")
    sns.set_context("paper", font_scale=1.1)
    sns.set_style("ticks")
    
    plt.rcParams.update({
        # Figure
        'figure.figsize': (8, 5),
        'figure.dpi': 150,
        'figure.facecolor': 'white',
        'figure.edgecolor': 'white',
        
        # Saving
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'savefig.facecolor': 'white',
        'savefig.edgecolor': 'white',
        
        # Fonts (Serif for LaTeX compatibility)
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif'],
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'legend.fontsize': 9,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        
        # Axes
        'axes.linewidth': 0.8,
        'axes.edgecolor': '#333333',
        'axes.labelcolor': '#333333',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': False,
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
        'legend.framealpha': 0.9,
        'legend.edgecolor': '#cccccc',
        
        # Text
        'text.color': '#333333',
        
        # Math text
        'mathtext.fontset': 'dejavuserif',
    })


def assign_method_colors(methods: List[str]) -> Dict[str, str]:
    """Assign consistent colors to methods."""
    global METHOD_COLORS
    sorted_methods = sorted(methods)
    METHOD_COLORS = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(sorted_methods)}
    return METHOD_COLORS


def save_figure(fig: plt.Figure, output_dir: Path, name: str):
    """Save figure in both PNG and PDF formats."""
    fig.savefig(output_dir / f"{name}.png", format='png')
    fig.savefig(output_dir / f"{name}.pdf", format='pdf')
    plt.close(fig)
    print(f"  [OK] {name}.png / .pdf")


# =============================================================================
# DATA LOADING AND PREPROCESSING
# =============================================================================

def load_results(csv_file: Path) -> Optional[pd.DataFrame]:
    """Load results from a CSV file with validation."""
    if not csv_file.exists():
        print(f"  [WARN] File not found: {csv_file}")
        return None
    
    try:
        df = pd.read_csv(csv_file)
        required_cols = {'Instance', 'Method', 'Profit', 'Time'}
        if not required_cols.issubset(df.columns):
            print(f"  [WARN] Missing columns in {csv_file}")
            return None
        return df
    except Exception as e:
        print(f"  [ERROR] Failed to load {csv_file}: {e}")
        return None


def load_all_results(results_dir: Path) -> Optional[pd.DataFrame]:
    """Load and concatenate all CSV result files."""
    csv_files = [f for f in results_dir.glob("*.csv") if not f.name.startswith("single_")]
    
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


def parse_instance_class(instance_name: str) -> Tuple[str, Optional[int]]:
    """
    Parse instance name to extract class and size/density information.
    
    Examples:
        '10I5' -> ('I', 10)
        'BPPC_1_0_1.txt_0.5' -> ('C1', None)
        '11I1.txt' -> ('I', 11)
    """
    name = str(instance_name)
    
    # Pattern for Set I instances: e.g., "10I5", "1I1", "11I1.txt"
    match_set1 = re.match(r'^(\d+)I\d+', name)
    if match_set1:
        size = int(match_set1.group(1))
        return ('I', size)
    
    # Pattern for Set II instances: e.g., folder-based (C1, C3, R1, etc.)
    # These are typically named like "BPPC_1_0_1.txt_0.5"
    if 'BPPC' in name or name.startswith('sparse'):
        return ('II', None)
    
    # Default fallback
    return ('Unknown', None)


# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

def compute_overview_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute rich summary statistics per method.
    Returns: Mean, Median, Std, Min, Max, CV% for Profit and Time.
    """
    def cv_percent(x):
        """Coefficient of Variation (%)."""
        return (x.std() / x.mean() * 100) if x.mean() != 0 else 0
    
    profit_stats = df.groupby('Method')['Profit'].agg([
        ('Mean', 'mean'),
        ('Median', 'median'),
        ('Std', 'std'),
        ('Min', 'min'),
        ('Max', 'max'),
        ('CV%', cv_percent)
    ]).round(2)
    
    time_stats = df.groupby('Method')['Time'].agg([
        ('Mean', 'mean'),
        ('Median', 'median'),
        ('Std', 'std'),
        ('Min', 'min'),
        ('Max', 'max'),
        ('CV%', cv_percent)
    ]).round(6)
    
    # Combine with MultiIndex columns
    profit_stats.columns = pd.MultiIndex.from_product([['Profit'], profit_stats.columns])
    time_stats.columns = pd.MultiIndex.from_product([['Time'], time_stats.columns])
    
    return pd.concat([profit_stats, time_stats], axis=1)


def compute_method_wins(df: pd.DataFrame) -> pd.Series:
    """Count wins (best profit) per method across instances."""
    best_per_instance = df.loc[df.groupby('Instance')['Profit'].idxmax()]
    return best_per_instance['Method'].value_counts()


def perform_statistical_tests(gap_df: pd.DataFrame) -> Dict:
    """
    Perform statistical significance tests:
    - Friedman test for overall comparison
    - Wilcoxon signed-rank tests (pairwise) against best method
    """
    results = {'friedman': None, 'wilcoxon': {}}
    
    methods = sorted(gap_df['Method'].unique())
    instances = gap_df['Instance'].unique()
    
    if len(methods) < 2:
        return results
    
    # Pivot to get gaps per instance per method
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    pivot = pivot.dropna()
    
    if len(pivot) < 3:
        return results
    
    # Friedman test
    try:
        method_gaps = [pivot[m].values for m in methods if m in pivot.columns]
        if len(method_gaps) >= 2:
            stat, p_value = stats.friedmanchisquare(*method_gaps)
            results['friedman'] = {'statistic': stat, 'p_value': p_value}
    except Exception:
        pass
    
    # Find best method (lowest average gap)
    avg_gaps = gap_df.groupby('Method')['Gap'].mean()
    best_method = avg_gaps.idxmin()
    
    # Pairwise Wilcoxon tests against best method
    if best_method in pivot.columns:
        best_gaps = pivot[best_method].values
        
        for method in methods:
            if method == best_method or method not in pivot.columns:
                continue
            
            try:
                other_gaps = pivot[method].values
                # Only test if there are differences
                if not np.allclose(best_gaps, other_gaps):
                    stat, p_value = stats.wilcoxon(best_gaps, other_gaps, alternative='less')
                    results['wilcoxon'][method] = {
                        'statistic': stat,
                        'p_value': p_value,
                        'significant_0.05': p_value < 0.05,
                        'significant_0.01': p_value < 0.01
                    }
            except Exception:
                pass
    
    results['best_method'] = best_method
    return results


def compute_performance_profile(gap_df: pd.DataFrame, tau_max: float = 10.0, 
                                 n_points: int = 100) -> pd.DataFrame:
    """
    Compute Dolan-Moré performance profiles.
    
    For each method, compute the probability that the method is within
    a factor tau of the best method for that instance.
    
    Args:
        gap_df: DataFrame with Gap per instance per method
        tau_max: Maximum tau value to consider
        n_points: Number of points in the profile
    
    Returns:
        DataFrame with tau values and cumulative probabilities per method
    """
    methods = sorted(gap_df['Method'].unique())
    instances = gap_df['Instance'].unique()
    n_instances = len(instances)
    
    # Pivot to get gaps
    pivot = gap_df.pivot_table(values='Gap', index='Instance', columns='Method', aggfunc='mean')
    
    # For each instance, find the best (minimum) gap
    best_per_instance = pivot.min(axis=1)
    
    # Compute performance ratios: r_{i,m} = gap_{i,m} / best_gap_i
    # We add a small epsilon to avoid division by zero
    eps = 1e-10
    ratios = pivot.div(best_per_instance + eps, axis=0)
    
    # For methods that achieved the best, ratio should be 1
    for col in ratios.columns:
        ratios.loc[pivot[col] == best_per_instance, col] = 1.0
    
    # Handle cases where best gap is 0 (perfect solution)
    ratios = ratios.replace([np.inf, -np.inf], tau_max + 1)
    ratios = ratios.fillna(tau_max + 1)
    
    # Generate tau values
    tau_values = np.linspace(1.0, tau_max, n_points)
    
    # Compute cumulative probability for each method
    profile_data = {'tau': tau_values}
    
    for method in methods:
        if method not in ratios.columns:
            continue
        
        method_ratios = ratios[method].values
        probs = []
        
        for tau in tau_values:
            # Probability that ratio <= tau
            prob = np.sum(method_ratios <= tau) / n_instances
            probs.append(prob)
        
        profile_data[method] = probs
    
    return pd.DataFrame(profile_data)


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_gap_boxplot(gap_df: pd.DataFrame, output_dir: Path):
    """Plot gap distribution as violin/box plot, sorted by median gap."""
    if gap_df.empty:
        return
    
    methods = gap_df.groupby('Method')['Gap'].median().sort_values().index.tolist()
    colors = [METHOD_COLORS.get(m, '#808080') for m in methods]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Create violin plot with embedded boxplot
    parts = ax.violinplot(
        [gap_df[gap_df['Method'] == m]['Gap'].values for m in methods],
        positions=range(len(methods)),
        showmeans=True,
        showmedians=True,
        widths=0.7
    )
    
    # Color the violins
    for i, (pc, color) in enumerate(zip(parts['bodies'], colors)):
        pc.set_facecolor(color)
        pc.set_alpha(0.6)
        pc.set_edgecolor('#333333')
        pc.set_linewidth(0.8)
    
    # Style the lines
    for partname in ['cbars', 'cmins', 'cmaxes', 'cmeans', 'cmedians']:
        if partname in parts:
            parts[partname].set_edgecolor('#333333')
            parts[partname].set_linewidth(1)
    
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, rotation=25, ha='right')
    ax.set_ylabel('Gap to BKS (%)')
    ax.set_xlabel('Method')
    ax.axhline(y=0, color='#55A868', linestyle='--', linewidth=1, alpha=0.8, label='Optimal')
    
    # Add subtle grid
    ax.yaxis.grid(True, alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'gap_boxplot')


def plot_performance_profile(profile_df: pd.DataFrame, output_dir: Path):
    """Plot Dolan-Moré performance profiles."""
    if profile_df.empty or len(profile_df.columns) < 2:
        return
    
    fig, ax = plt.subplots(figsize=(7, 5))
    
    methods = [col for col in profile_df.columns if col != 'tau']
    
    for method in methods:
        color = METHOD_COLORS.get(method, '#808080')
        ax.plot(profile_df['tau'], profile_df[method], 
                label=method, linewidth=1.8, color=color)
    
    ax.set_xlabel(r'Performance ratio $\tau$')
    ax.set_ylabel(r'$P(r_{i,m} \leq \tau)$')
    ax.set_xlim(1, profile_df['tau'].max())
    ax.set_ylim(0, 1.05)
    
    ax.legend(loc='lower right', framealpha=0.9)
    ax.yaxis.grid(True, alpha=0.3, linewidth=0.5)
    ax.xaxis.grid(True, alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'performance_profile')


def plot_time_boxplot(df: pd.DataFrame, output_dir: Path):
    """Plot execution time distributions on log scale."""
    if df.empty:
        return
    
    methods = df.groupby('Method')['Time'].median().sort_values().index.tolist()
    colors = [METHOD_COLORS.get(m, '#808080') for m in methods]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    bp = ax.boxplot(
        [df[df['Method'] == m]['Time'].values for m in methods],
        labels=methods,
        patch_artist=True,
        showmeans=True,
        meanprops={'marker': 'D', 'markerfacecolor': 'white', 
                   'markeredgecolor': '#333333', 'markersize': 5},
        medianprops={'color': '#333333', 'linewidth': 1.5},
        whiskerprops={'color': '#333333', 'linewidth': 1},
        capprops={'color': '#333333', 'linewidth': 1},
        flierprops={'marker': 'o', 'markerfacecolor': '#cccccc', 
                    'markeredgecolor': '#666666', 'markersize': 4, 'alpha': 0.6}
    )
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
        patch.set_edgecolor('#333333')
        patch.set_linewidth(1)
    
    ax.set_yscale('log')
    ax.set_ylabel('Execution Time (s)')
    ax.set_xlabel('Method')
    ax.tick_params(axis='x', rotation=25)
    
    # Format y-axis with proper scientific notation
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, p: f'{x:.0e}' if x < 0.001 else f'{x:.4f}'
    ))
    
    ax.yaxis.grid(True, alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'time_boxplot')


def plot_time_vs_quality(gap_df: pd.DataFrame, output_dir: Path):
    """Scatter plot: Time (log) vs Average Gap (quality-time trade-off)."""
    if gap_df.empty:
        return
    
    # Aggregate by method
    summary = gap_df.groupby('Method').agg({
        'Gap': 'mean',
        'Time': 'mean'
    }).reset_index()
    
    fig, ax = plt.subplots(figsize=(7, 5))
    
    for _, row in summary.iterrows():
        color = METHOD_COLORS.get(row['Method'], '#808080')
        ax.scatter(row['Time'], row['Gap'], 
                   s=150, color=color, edgecolor='#333333', 
                   linewidth=1, zorder=5, alpha=0.85)
        ax.annotate(row['Method'], 
                    (row['Time'], row['Gap']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.9)
    
    ax.set_xscale('log')
    ax.set_xlabel('Average Time (s) [log scale]')
    ax.set_ylabel('Average Gap to BKS (%)')
    
    ax.xaxis.grid(True, alpha=0.3, linewidth=0.5)
    ax.yaxis.grid(True, alpha=0.3, linewidth=0.5)
    
    # Add quadrant guides
    ax.axhline(y=summary['Gap'].median(), color='#cccccc', 
               linestyle=':', linewidth=1, alpha=0.8)
    ax.axvline(x=summary['Time'].median(), color='#cccccc', 
               linestyle=':', linewidth=1, alpha=0.8)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'time_vs_quality')


def plot_gap_heatmap(gap_df: pd.DataFrame, output_dir: Path):
    """Heatmap of Gap % per instance and method."""
    if gap_df.empty:
        return
    
    # Pivot: instances as rows, methods as columns
    pivot = gap_df.pivot_table(values='Gap', index='Instance', 
                                columns='Method', aggfunc='mean')
    
    # Sort methods by average gap
    method_order = pivot.mean().sort_values().index.tolist()
    pivot = pivot[method_order]
    
    # Sort instances by their "difficulty" (max gap across methods)
    instance_order = pivot.max(axis=1).sort_values().index.tolist()
    pivot = pivot.loc[instance_order]
    
    # Limit to reasonable size for visualization
    max_instances = 50
    if len(pivot) > max_instances:
        # Sample evenly
        step = len(pivot) // max_instances
        pivot = pivot.iloc[::step]
    
    fig, ax = plt.subplots(figsize=(8, max(4, len(pivot) * 0.15)))
    
    # Use a diverging colormap centered at 0
    cmap = sns.color_palette("RdYlGn_r", as_cmap=True)
    
    im = ax.imshow(pivot.values, cmap=cmap, aspect='auto', 
                   vmin=0, vmax=min(pivot.values.max(), 50))
    
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha='right', fontsize=8)
    ax.set_yticklabels(pivot.index, fontsize=7)
    
    ax.set_xlabel('Method')
    ax.set_ylabel('Instance')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Gap (%)', fontsize=9)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'gap_heatmap')


def plot_instance_class_analysis(gap_df: pd.DataFrame, output_dir: Path):
    """Bar plot: Average Gap by Instance Class/Size."""
    if gap_df.empty:
        return
    
    # Parse instance classes
    gap_df = gap_df.copy()
    parsed = gap_df['Instance'].apply(parse_instance_class)
    gap_df['Class'] = parsed.apply(lambda x: x[0])
    gap_df['Size'] = parsed.apply(lambda x: x[1])
    
    # Filter to Set I instances with known sizes
    set1_df = gap_df[(gap_df['Class'] == 'I') & (gap_df['Size'].notna())]
    
    if set1_df.empty:
        # Fallback: just use class
        summary = gap_df.groupby(['Class', 'Method'])['Gap'].mean().reset_index()
        x_col = 'Class'
    else:
        summary = set1_df.groupby(['Size', 'Method'])['Gap'].mean().reset_index()
        summary['Size'] = summary['Size'].astype(int)
        summary = summary.sort_values('Size')
        x_col = 'Size'
    
    if summary.empty:
        return
    
    methods = sorted(summary['Method'].unique())
    x_values = sorted(summary[x_col].unique())
    n_methods = len(methods)
    bar_width = 0.8 / n_methods
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    for i, method in enumerate(methods):
        method_data = summary[summary['Method'] == method]
        x_pos = np.arange(len(x_values)) + i * bar_width - (n_methods - 1) * bar_width / 2
        
        heights = []
        for x in x_values:
            val = method_data[method_data[x_col] == x]['Gap'].values
            heights.append(val[0] if len(val) > 0 else 0)
        
        color = METHOD_COLORS.get(method, '#808080')
        ax.bar(x_pos, heights, bar_width * 0.9, label=method, 
               color=color, alpha=0.8, edgecolor='#333333', linewidth=0.5)
    
    ax.set_xticks(np.arange(len(x_values)))
    ax.set_xticklabels([str(x) for x in x_values])
    ax.set_xlabel('Instance Size' if x_col == 'Size' else 'Instance Class')
    ax.set_ylabel('Average Gap (%)')
    ax.legend(loc='upper left', framealpha=0.9, fontsize=8)
    ax.yaxis.grid(True, alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'instance_class_analysis')


def plot_profit_distribution(df: pd.DataFrame, output_dir: Path):
    """KDE plot of profit distributions per method."""
    if df.empty:
        return
    
    methods = sorted(df['Method'].unique())
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    for method in methods:
        color = METHOD_COLORS.get(method, '#808080')
        data = df[df['Method'] == method]['Profit'].values
        
        if len(data) > 1:
            sns.kdeplot(data, ax=ax, label=method, color=color, 
                       linewidth=1.8, fill=True, alpha=0.15)
    
    ax.set_xlabel('Profit')
    ax.set_ylabel('Density')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.yaxis.grid(True, alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    save_figure(fig, output_dir, 'profit_distribution')


# =============================================================================
# REPORT GENERATION
# =============================================================================

def export_statistics_markdown(stats_df: pd.DataFrame, output_file: Path):
    """Export statistics table in Markdown format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# DCKP Heuristics - Statistical Summary\n\n")
        f.write("## Method Performance Statistics\n\n")
        f.write(stats_df.to_markdown())
        f.write("\n")
    print(f"  [OK] {output_file.name}")


def export_statistics_latex(stats_df: pd.DataFrame, output_file: Path):
    """Export statistics table in LaTeX format."""
    latex_str = stats_df.to_latex(
        float_format="%.4f",
        multicolumn=True,
        multicolumn_format='c',
        caption="Summary statistics of heuristic methods.",
        label="tab:method_stats"
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_str)
    print(f"  [OK] {output_file.name}")


def export_statistical_tests(test_results: Dict, output_file: Path):
    """Export statistical test results to text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("STATISTICAL SIGNIFICANCE TESTS\n")
        f.write("=" * 70 + "\n\n")
        
        if test_results.get('best_method'):
            f.write(f"Best Method (lowest avg gap): {test_results['best_method']}\n\n")
        
        # Friedman test
        f.write("-" * 70 + "\n")
        f.write("FRIEDMAN TEST (Overall comparison)\n")
        f.write("-" * 70 + "\n")
        
        if test_results.get('friedman'):
            fr = test_results['friedman']
            f.write(f"  Chi-square statistic: {fr['statistic']:.4f}\n")
            f.write(f"  p-value: {fr['p_value']:.6f}\n")
            
            if fr['p_value'] < 0.001:
                f.write("  Conclusion: Highly significant (p < 0.001) ***\n")
            elif fr['p_value'] < 0.01:
                f.write("  Conclusion: Significant (p < 0.01) **\n")
            elif fr['p_value'] < 0.05:
                f.write("  Conclusion: Significant (p < 0.05) *\n")
            else:
                f.write("  Conclusion: Not significant (p >= 0.05)\n")
        else:
            f.write("  Not enough data to perform test.\n")
        
        f.write("\n")
        
        # Wilcoxon tests
        f.write("-" * 70 + "\n")
        f.write("WILCOXON SIGNED-RANK TESTS (vs. Best Method)\n")
        f.write("-" * 70 + "\n\n")
        
        if test_results.get('wilcoxon'):
            f.write(f"{'Method':<30} {'Statistic':>12} {'p-value':>12} {'Sig.(0.05)':>12}\n")
            f.write("-" * 70 + "\n")
            
            for method, result in test_results['wilcoxon'].items():
                sig = "Yes ***" if result['significant_0.01'] else \
                      ("Yes *" if result['significant_0.05'] else "No")
                f.write(f"{method:<30} {result['statistic']:>12.4f} "
                       f"{result['p_value']:>12.6f} {sig:>12}\n")
        else:
            f.write("  Not enough data to perform pairwise tests.\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    print(f"  [OK] {output_file.name}")


def generate_summary_report(df: pd.DataFrame, gap_df: pd.DataFrame, 
                            test_results: Dict, output_file: Path):
    """Generate comprehensive text summary report."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("DCKP HEURISTICS - COMPREHENSIVE ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        # Overview
        f.write("1. EXPERIMENT OVERVIEW\n")
        f.write("-" * 70 + "\n")
        f.write(f"   Total experiments: {len(df)}\n")
        f.write(f"   Unique instances:  {df['Instance'].nunique()}\n")
        f.write(f"   Methods tested:    {df['Method'].nunique()}\n")
        f.write(f"   Methods: {', '.join(sorted(df['Method'].unique()))}\n\n")
        
        # Best method identification
        f.write("2. BEST METHOD IDENTIFICATION\n")
        f.write("-" * 70 + "\n")
        
        avg_gap = gap_df.groupby('Method')['Gap'].mean().sort_values()
        f.write("   Ranking by Average Gap (lower is better):\n")
        for i, (method, gap) in enumerate(avg_gap.items(), 1):
            f.write(f"      {i}. {method}: {gap:.4f}%\n")
        f.write("\n")
        
        # Wins count
        wins = compute_method_wins(df)
        f.write("   Wins (best on instance):\n")
        for method, count in wins.items():
            pct = count / df['Instance'].nunique() * 100
            f.write(f"      {method}: {count} ({pct:.1f}%)\n")
        f.write("\n")
        
        # Time analysis
        f.write("3. TIME ANALYSIS\n")
        f.write("-" * 70 + "\n")
        time_stats = df.groupby('Method')['Time'].agg(['mean', 'std', 'min', 'max'])
        f.write(f"   {'Method':<30} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}\n")
        f.write("   " + "-" * 66 + "\n")
        for method in time_stats.index:
            row = time_stats.loc[method]
            f.write(f"   {method:<30} {row['mean']:>10.6f} {row['std']:>10.6f} "
                   f"{row['min']:>10.6f} {row['max']:>10.6f}\n")
        f.write("\n")
        
        # Statistical significance
        f.write("4. STATISTICAL SIGNIFICANCE\n")
        f.write("-" * 70 + "\n")
        if test_results.get('friedman'):
            fr = test_results['friedman']
            f.write(f"   Friedman test p-value: {fr['p_value']:.6f}")
            if fr['p_value'] < 0.05:
                f.write(" (SIGNIFICANT)\n")
            else:
                f.write(" (not significant)\n")
        
        if test_results.get('best_method'):
            f.write(f"   Best method: {test_results['best_method']}\n")
        f.write("\n")
        
        f.write("=" * 70 + "\n")
        f.write("Report generated successfully.\n")
        f.write("=" * 70 + "\n")
    
    print(f"  [OK] {output_file.name}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main analysis pipeline."""
    print("\n" + "=" * 70)
    print(" DCKP HEURISTICS - PUBLICATION-QUALITY ANALYSIS")
    print("=" * 70)
    
    # Setup style
    setup_publication_style()
    
    # Paths
    results_dir = Path("results/etapa1")
    output_dir = results_dir / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n[1/6] Loading results...")
    df = load_all_results(results_dir)
    
    if df is None or df.empty:
        print("  [ERROR] No results found!")
        print("  Run experiments first: ./scripts/run_experiments.ps1")
        return
    
    print(f"  Loaded {len(df)} results from {df['Instance'].nunique()} instances")
    print(f"  Methods: {', '.join(sorted(df['Method'].unique()))}")
    
    # Assign colors to methods
    assign_method_colors(df['Method'].unique().tolist())
    
    # Compute gap dataframe
    print("\n[2/6] Computing gap analysis...")
    gap_df = compute_gap_dataframe(df)
    
    # Compute statistics
    print("\n[3/6] Computing statistics...")
    overview_stats = compute_overview_statistics(df)
    print(overview_stats.to_string())
    
    # Statistical tests
    print("\n[4/6] Performing statistical tests...")
    test_results = perform_statistical_tests(gap_df)
    
    if test_results.get('friedman'):
        fr = test_results['friedman']
        print(f"  Friedman test: chi2={fr['statistic']:.4f}, p={fr['p_value']:.6f}")
    
    if test_results.get('best_method'):
        print(f"  Best method: {test_results['best_method']}")
    
    # Generate visualizations
    print("\n[5/6] Generating visualizations...")
    
    # Gap analysis
    plot_gap_boxplot(gap_df, output_dir)
    
    # Performance profile
    profile_df = compute_performance_profile(gap_df, tau_max=5.0)
    plot_performance_profile(profile_df, output_dir)
    
    # Time analysis
    plot_time_boxplot(df, output_dir)
    plot_time_vs_quality(gap_df, output_dir)
    
    # Instance analysis
    plot_gap_heatmap(gap_df, output_dir)
    plot_instance_class_analysis(gap_df, output_dir)
    
    # Profit distribution
    plot_profit_distribution(df, output_dir)
    
    # Export reports
    print("\n[6/6] Exporting reports...")
    export_statistics_markdown(overview_stats, output_dir / "statistics.md")
    export_statistics_latex(overview_stats, output_dir / "statistics.tex")
    export_statistical_tests(test_results, output_dir / "statistical_tests.txt")
    generate_summary_report(df, gap_df, test_results, output_dir / "summary_report.txt")
    
    # Export raw data
    gap_df.to_csv(output_dir / "gap_analysis.csv", index=False)
    profile_df.to_csv(output_dir / "performance_profile.csv", index=False)
    
    print("\n" + "=" * 70)
    print(" ANALYSIS COMPLETE!")
    print(f" Results saved to: {output_dir.absolute()}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
