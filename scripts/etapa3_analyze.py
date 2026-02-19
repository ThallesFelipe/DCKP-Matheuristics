#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise dedicada da Etapa 3 (ILS vs VNS) e comparação entre melhores etapas.

Gera métricas, testes estatísticos e gráficos prontos para apresentação.
Não altera scripts existentes (ex.: analyze_results.py).
"""

from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


@dataclass
class Config:
    alpha: float = 0.05
    bootstrap_n: int = 4000
    random_seed: int = 42
    dpi: int = 300


CONFIG = Config()

PALETTE = {
    "ILS": "#0072B2",
    "VNS": "#D55E00",
    "Etapa3": "#009E73",
    "Etapa2": "#E69F00",
    "Etapa1": "#56B4E9",
}


def setup_style() -> None:
    sns.set_style("whitegrid")
    sns.set_context("talk", font_scale=0.9)
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": CONFIG.dpi,
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "legend.frameon": True,
            "legend.framealpha": 0.95,
            "axes.titleweight": "bold",
        }
    )


def load_stage(stage_dir: Path) -> pd.DataFrame:
    csv_files = sorted(stage_dir.glob("results_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {stage_dir}")

    data = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        needed = {"Instance", "Method", "Profit", "Time"}
        missing = needed - set(df.columns)
        if missing:
            raise ValueError(f"Colunas ausentes em {csv_file.name}: {sorted(missing)}")
        data.append(df)

    result = pd.concat(data, ignore_index=True)
    result = result.copy()
    result["Instance"] = result["Instance"].astype(str)
    result["InstanceKey"] = result["Instance"].str.replace(".txt", "", regex=False)
    if "Feasible" in result.columns:
        result = result[result["Feasible"].astype(str).str.lower().isin(["yes", "true", "1"])]
    return result


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) == 0 or len(y) == 0:
        return np.nan
    greater = 0
    lower = 0
    for xi in x:
        greater += np.sum(xi > y)
        lower += np.sum(xi < y)
    return (greater - lower) / (len(x) * len(y))


def effect_label(delta_abs: float) -> str:
    if np.isnan(delta_abs):
        return "NA"
    if delta_abs < 0.147:
        return "negligível"
    if delta_abs < 0.33:
        return "pequeno"
    if delta_abs < 0.474:
        return "médio"
    return "grande"


def bootstrap_ci_mean(diff: np.ndarray, n_boot: int, seed: int) -> Tuple[float, float]:
    if len(diff) == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot, dtype=float)
    n = len(diff)
    for i in range(n_boot):
        sample = rng.choice(diff, size=n, replace=True)
        means[i] = np.mean(sample)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def paired_stats(a: pd.Series, b: pd.Series, higher_is_better: bool, label_a: str, label_b: str) -> Dict[str, float | str]:
    common = pd.concat([a, b], axis=1, join="inner").dropna()
    if common.empty:
        return {
            "n": 0,
            "mean_a": np.nan,
            "mean_b": np.nan,
            "median_diff": np.nan,
            "mean_diff": np.nan,
            "pvalue": np.nan,
            "cliffs_delta": np.nan,
            "effect": "NA",
            "ci_low": np.nan,
            "ci_high": np.nan,
        }

    vec_a = common.iloc[:, 0].to_numpy(dtype=float)
    vec_b = common.iloc[:, 1].to_numpy(dtype=float)

    diff = vec_b - vec_a
    if not higher_is_better:
        diff = -diff

    if np.allclose(diff, 0.0):
        pvalue = 1.0
    else:
        try:
            pvalue = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided").pvalue
        except ValueError:
            pvalue = np.nan

    delta = cliffs_delta(vec_b, vec_a)
    delta_signed = delta if higher_is_better else -delta
    ci_low, ci_high = bootstrap_ci_mean(diff, CONFIG.bootstrap_n, CONFIG.random_seed)

    return {
        "n": int(len(common)),
        "mean_a": float(np.mean(vec_a)),
        "mean_b": float(np.mean(vec_b)),
        "median_diff": float(np.median(diff)),
        "mean_diff": float(np.mean(diff)),
        "pvalue": float(pvalue) if not np.isnan(pvalue) else np.nan,
        "cliffs_delta": float(delta_signed),
        "effect": effect_label(abs(delta_signed)),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "label_a": label_a,
        "label_b": label_b,
    }


def save_fig(fig: plt.Figure, output_dir: Path, name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{name}.png", bbox_inches="tight")
    fig.savefig(output_dir / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def best_per_instance(stage_df: pd.DataFrame, stage_name: str) -> pd.DataFrame:
    df = stage_df.copy()
    df = df.sort_values(["InstanceKey", "Profit", "Time"], ascending=[True, False, True])
    best = df.groupby("InstanceKey", as_index=False).first()
    best = best[["Instance", "InstanceKey", "Method", "Profit", "Time"]].copy()
    best = best.rename(
        columns={
            "Method": f"Method_{stage_name}",
            "Profit": f"Profit_{stage_name}",
            "Time": f"Time_{stage_name}",
        }
    )
    return best


def compare_ils_vns(etapa3: pd.DataFrame, output_dir: Path) -> Dict[str, Dict[str, float | str]]:
    subset = etapa3[etapa3["Method"].isin(["ILS", "VNS"])].copy()
    pivot_profit = subset.pivot_table(index="InstanceKey", columns="Method", values="Profit", aggfunc="max")
    pivot_time = subset.pivot_table(index="InstanceKey", columns="Method", values="Time", aggfunc="min")

    comp = pd.concat([pivot_profit.add_prefix("Profit_"), pivot_time.add_prefix("Time_")], axis=1).dropna()
    if comp.empty:
        raise ValueError("Sem instâncias comuns para comparação ILS vs VNS na etapa 3.")

    comp["BestProfit"] = comp[["Profit_ILS", "Profit_VNS"]].max(axis=1)
    comp["Gap_ILS_%"] = (comp["BestProfit"] - comp["Profit_ILS"]) / comp["BestProfit"] * 100.0
    comp["Gap_VNS_%"] = (comp["BestProfit"] - comp["Profit_VNS"]) / comp["BestProfit"] * 100.0
    comp["Profit_Diff_VNS_minus_ILS"] = comp["Profit_VNS"] - comp["Profit_ILS"]
    comp["Time_Ratio_VNS_over_ILS"] = comp["Time_VNS"] / comp["Time_ILS"]
    comp.reset_index().to_csv(output_dir / "ils_vs_vns_instancewise.csv", index=False)

    wins_profit = {
        "ILS": int((comp["Profit_ILS"] > comp["Profit_VNS"]).sum()),
        "VNS": int((comp["Profit_VNS"] > comp["Profit_ILS"]).sum()),
        "Tie": int((comp["Profit_ILS"] == comp["Profit_VNS"]).sum()),
    }
    wins_time = {
        "ILS": int((comp["Time_ILS"] < comp["Time_VNS"]).sum()),
        "VNS": int((comp["Time_VNS"] < comp["Time_ILS"]).sum()),
        "Tie": int((comp["Time_ILS"] == comp["Time_VNS"]).sum()),
    }

    stats_profit = paired_stats(comp["Profit_ILS"], comp["Profit_VNS"], True, "ILS", "VNS")
    stats_time = paired_stats(comp["Time_ILS"], comp["Time_VNS"], False, "ILS", "VNS")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))

    ax = axes[0]
    ax.scatter(comp["Profit_ILS"], comp["Profit_VNS"], s=35, alpha=0.8, color=PALETTE["VNS"])
    lim0 = [min(comp["Profit_ILS"].min(), comp["Profit_VNS"].min()), max(comp["Profit_ILS"].max(), comp["Profit_VNS"].max())]
    ax.plot(lim0, lim0, "--", color="#444444", linewidth=1)
    ax.set_title("Qualidade: ILS vs VNS")
    ax.set_xlabel("Profit ILS")
    ax.set_ylabel("Profit VNS")

    ax = axes[1]
    ax.scatter(comp["Time_ILS"], comp["Time_VNS"], s=35, alpha=0.8, color=PALETTE["ILS"])
    lim1 = [min(comp["Time_ILS"].min(), comp["Time_VNS"].min()), max(comp["Time_ILS"].max(), comp["Time_VNS"].max())]
    ax.plot(lim1, lim1, "--", color="#444444", linewidth=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Tempo: ILS vs VNS (escala log)")
    ax.set_xlabel("Tempo ILS (s)")
    ax.set_ylabel("Tempo VNS (s)")

    fig.suptitle("Etapa 3: Comparação Pareada ILS vs VNS", fontsize=14, fontweight="bold")
    save_fig(fig, output_dir, "fig01_ils_vs_vns_scatter")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    box_df = pd.DataFrame(
        {
            "Método": ["ILS"] * len(comp) + ["VNS"] * len(comp),
            "Gap (%)": pd.concat([comp["Gap_ILS_%"], comp["Gap_VNS_%"]], ignore_index=True),
        }
    )
    sns.boxplot(data=box_df, x="Método", y="Gap (%)", palette=[PALETTE["ILS"], PALETTE["VNS"]], ax=axes[0])
    axes[0].set_title("Gap para o melhor da dupla (menor é melhor)")

    win_df = pd.DataFrame(
        {
            "Categoria": ["Qualidade"] * 3 + ["Tempo"] * 3,
            "Resultado": ["ILS", "VNS", "Tie", "ILS", "VNS", "Tie"],
            "Contagem": [wins_profit["ILS"], wins_profit["VNS"], wins_profit["Tie"], wins_time["ILS"], wins_time["VNS"], wins_time["Tie"]],
        }
    )
    sns.barplot(data=win_df, x="Categoria", y="Contagem", hue="Resultado", palette=[PALETTE["ILS"], PALETTE["VNS"], "#999999"], ax=axes[1])
    axes[1].set_title("Vitórias, derrotas e empates")
    axes[1].legend(title="")

    fig.suptitle("Etapa 3: Distribuição de Qualidade e Dominância", fontsize=14, fontweight="bold")
    save_fig(fig, output_dir, "fig02_ils_vs_vns_gap_wins")

    return {
        "profit": stats_profit,
        "time": stats_time,
        "wins_profit": wins_profit,
        "wins_time": wins_time,
    }


def compare_stage_best(
    best1: pd.DataFrame,
    best2: pd.DataFrame,
    best3: pd.DataFrame,
    output_dir: Path,
) -> Dict[str, Dict[str, float | str]]:
    merge32 = best3.merge(best2, on="InstanceKey", how="inner")
    merge31 = best3.merge(best1, on="InstanceKey", how="inner")

    cmp_rows = []

    for name, merged, other_tag in [
        ("Etapa3_vs_Etapa2", merge32, "etapa2"),
        ("Etapa3_vs_Etapa1", merge31, "etapa1"),
    ]:
        if merged.empty:
            continue

        merged = merged.copy()
        merged["ProfitGain_%"] = (
            (merged["Profit_etapa3"] - merged[f"Profit_{other_tag}"]) / merged[f"Profit_{other_tag}"]
        ) * 100.0
        merged["TimeRatio"] = merged["Time_etapa3"] / merged[f"Time_{other_tag}"]

        merged[[
            "InstanceKey",
            "Method_etapa3",
            f"Method_{other_tag}",
            "Profit_etapa3",
            f"Profit_{other_tag}",
            "Time_etapa3",
            f"Time_{other_tag}",
            "ProfitGain_%",
            "TimeRatio",
        ]].to_csv(output_dir / f"{name.lower()}_instancewise.csv", index=False)

        s_profit = paired_stats(
            merged[f"Profit_{other_tag}"],
            merged["Profit_etapa3"],
            True,
            f"Melhor {other_tag}",
            "Melhor etapa3",
        )
        s_time = paired_stats(
            merged[f"Time_{other_tag}"],
            merged["Time_etapa3"],
            False,
            f"Melhor {other_tag}",
            "Melhor etapa3",
        )

        cmp_rows.append(
            {
                "comparison": name,
                "n_instances": int(len(merged)),
                "mean_profit_gain_pct": float(merged["ProfitGain_%"].mean()),
                "median_profit_gain_pct": float(merged["ProfitGain_%"].median()),
                "mean_time_ratio_stage3_over_other": float(merged["TimeRatio"].mean()),
                "median_time_ratio_stage3_over_other": float(merged["TimeRatio"].median()),
                "profit_pvalue": s_profit["pvalue"],
                "time_pvalue": s_time["pvalue"],
                "profit_cliffs_delta": s_profit["cliffs_delta"],
                "time_cliffs_delta": s_time["cliffs_delta"],
                "profit_effect": s_profit["effect"],
                "time_effect": s_time["effect"],
            }
        )

    if not cmp_rows:
        raise ValueError("Não foi possível comparar melhores etapas: sem instâncias em comum.")

    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_csv(output_dir / "stage_best_comparison_summary.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    if not merge32.empty:
        axes[0, 0].scatter(merge32["Profit_etapa2"], merge32["Profit_etapa3"], color=PALETTE["Etapa2"], alpha=0.8)
        lim = [
            min(merge32["Profit_etapa2"].min(), merge32["Profit_etapa3"].min()),
            max(merge32["Profit_etapa2"].max(), merge32["Profit_etapa3"].max()),
        ]
        axes[0, 0].plot(lim, lim, "--", color="#444444", linewidth=1)
        axes[0, 0].set_title("Melhor Etapa 3 vs Melhor Etapa 2 (Profit)")
        axes[0, 0].set_xlabel("Etapa 2")
        axes[0, 0].set_ylabel("Etapa 3")

        axes[1, 0].scatter(merge32["Time_etapa2"], merge32["Time_etapa3"], color=PALETTE["Etapa2"], alpha=0.8)
        lim = [
            min(merge32["Time_etapa2"].min(), merge32["Time_etapa3"].min()),
            max(merge32["Time_etapa2"].max(), merge32["Time_etapa3"].max()),
        ]
        axes[1, 0].plot(lim, lim, "--", color="#444444", linewidth=1)
        axes[1, 0].set_xscale("log")
        axes[1, 0].set_yscale("log")
        axes[1, 0].set_title("Melhor Etapa 3 vs Melhor Etapa 2 (Tempo)")
        axes[1, 0].set_xlabel("Etapa 2 (s)")
        axes[1, 0].set_ylabel("Etapa 3 (s)")

    if not merge31.empty:
        axes[0, 1].scatter(merge31["Profit_etapa1"], merge31["Profit_etapa3"], color=PALETTE["Etapa1"], alpha=0.8)
        lim = [
            min(merge31["Profit_etapa1"].min(), merge31["Profit_etapa3"].min()),
            max(merge31["Profit_etapa1"].max(), merge31["Profit_etapa3"].max()),
        ]
        axes[0, 1].plot(lim, lim, "--", color="#444444", linewidth=1)
        axes[0, 1].set_title("Melhor Etapa 3 vs Melhor Etapa 1 (Profit)")
        axes[0, 1].set_xlabel("Etapa 1")
        axes[0, 1].set_ylabel("Etapa 3")

        axes[1, 1].scatter(merge31["Time_etapa1"], merge31["Time_etapa3"], color=PALETTE["Etapa1"], alpha=0.8)
        lim = [
            min(merge31["Time_etapa1"].min(), merge31["Time_etapa3"].min()),
            max(merge31["Time_etapa1"].max(), merge31["Time_etapa3"].max()),
        ]
        axes[1, 1].plot(lim, lim, "--", color="#444444", linewidth=1)
        axes[1, 1].set_xscale("log")
        axes[1, 1].set_yscale("log")
        axes[1, 1].set_title("Melhor Etapa 3 vs Melhor Etapa 1 (Tempo)")
        axes[1, 1].set_xlabel("Etapa 1 (s)")
        axes[1, 1].set_ylabel("Etapa 3 (s)")

    fig.suptitle("Comparação entre Melhores Soluções por Etapa", fontsize=15, fontweight="bold")
    save_fig(fig, output_dir, "fig03_stage_best_scatter")

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    bar = cmp_df.copy()
    bar["comparison"] = bar["comparison"].str.replace("_", " ")
    sns.barplot(data=bar, x="comparison", y="mean_profit_gain_pct", palette=[PALETTE["Etapa2"], PALETTE["Etapa1"]], ax=ax)
    ax.axhline(0.0, color="#444444", linewidth=1)
    ax.set_title("Ganho médio de profit do melhor da Etapa 3")
    ax.set_ylabel("Ganho médio (%)")
    ax.set_xlabel("")
    save_fig(fig, output_dir, "fig04_stage3_profit_gain")

    result = {}
    for _, row in cmp_df.iterrows():
        result[row["comparison"]] = row.to_dict()
    return result


def write_report(
    output_dir: Path,
    ils_vns_stats: Dict[str, Dict[str, float | str]],
    stage_stats: Dict[str, Dict[str, float | str]],
) -> None:
    p = ils_vns_stats["profit"]
    t = ils_vns_stats["time"]
    wp = ils_vns_stats["wins_profit"]
    wt = ils_vns_stats["wins_time"]

    lines = []
    lines.append("# Relatório Acadêmico - Etapa 3 (ILS vs VNS) e Comparação entre Etapas")
    lines.append("")
    lines.append("## 1. Comparação direta na Etapa 3: ILS vs VNS")
    lines.append("")
    lines.append(f"- Instâncias comparadas: **{p['n']}**")
    lines.append(f"- Vitórias em qualidade (Profit): ILS={wp['ILS']}, VNS={wp['VNS']}, Empates={wp['Tie']}")
    lines.append(f"- Vitórias em tempo: ILS={wt['ILS']}, VNS={wt['VNS']}, Empates={wt['Tie']}")
    lines.append(f"- Diferença média pareada em qualidade (favorável ao VNS quando > 0): **{p['mean_diff']:.4f}**")
    lines.append(f"- IC95% bootstrap (qualidade): [{p['ci_low']:.4f}, {p['ci_high']:.4f}]")
    lines.append(f"- Wilcoxon qualidade p-valor: **{p['pvalue']:.4g}**")
    lines.append(f"- Cliff's delta qualidade: **{p['cliffs_delta']:.4f}** ({p['effect']})")
    lines.append(f"- Diferença média pareada em tempo (favorável ao VNS quando > 0): **{t['mean_diff']:.4f}**")
    lines.append(f"- IC95% bootstrap (tempo): [{t['ci_low']:.4f}, {t['ci_high']:.4f}]")
    lines.append(f"- Wilcoxon tempo p-valor: **{t['pvalue']:.4g}**")
    lines.append(f"- Cliff's delta tempo: **{t['cliffs_delta']:.4f}** ({t['effect']})")
    lines.append("")
    lines.append("## 2. Melhor da Etapa 3 vs melhor da Etapa 2 e Etapa 1")
    lines.append("")
    for name, vals in stage_stats.items():
        lines.append(f"### {name.replace('_', ' ')}")
        lines.append(f"- Instâncias comparadas: **{int(vals['n_instances'])}**")
        lines.append(f"- Ganho médio de profit da Etapa 3 (%): **{vals['mean_profit_gain_pct']:.3f}**")
        lines.append(f"- Ganho mediano de profit da Etapa 3 (%): **{vals['median_profit_gain_pct']:.3f}**")
        lines.append(f"- Razão média de tempo (Etapa3/outra): **{vals['mean_time_ratio_stage3_over_other']:.3f}**")
        lines.append(f"- Razão mediana de tempo (Etapa3/outra): **{vals['median_time_ratio_stage3_over_other']:.3f}**")
        lines.append(f"- Wilcoxon profit p-valor: **{vals['profit_pvalue']:.4g}**")
        lines.append(f"- Wilcoxon tempo p-valor: **{vals['time_pvalue']:.4g}**")
        lines.append(f"- Cliff's delta profit: **{vals['profit_cliffs_delta']:.4f}** ({vals['profit_effect']})")
        lines.append(f"- Cliff's delta tempo: **{vals['time_cliffs_delta']:.4f}** ({vals['time_effect']})")
        lines.append("")

    lines.append("## 3. Arquivos gerados")
    lines.append("")
    lines.append("- `ils_vs_vns_instancewise.csv`")
    lines.append("- `etapa3_vs_etapa2_instancewise.csv`")
    lines.append("- `etapa3_vs_etapa1_instancewise.csv`")
    lines.append("- `stage_best_comparison_summary.csv`")
    lines.append("- `fig01_ils_vs_vns_scatter.(png|pdf)`")
    lines.append("- `fig02_ils_vs_vns_gap_wins.(png|pdf)`")
    lines.append("- `fig03_stage_best_scatter.(png|pdf)`")
    lines.append("- `fig04_stage3_profit_gain.(png|pdf)`")

    (output_dir / "report_etapa3.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Análise da etapa 3 (ILS vs VNS) e comparação com melhores etapas 1 e 2"
    )
    parser.add_argument("--results-dir", default="results", help="Diretório raiz de resultados")
    parser.add_argument("--output", default="results/analysis/etapa3", help="Diretório de saída")
    args = parser.parse_args()

    setup_style()

    results_dir = Path(args.results_dir)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    etapa1 = load_stage(results_dir / "etapa1")
    etapa2 = load_stage(results_dir / "etapa2")
    etapa3 = load_stage(results_dir / "etapa3")

    best1 = best_per_instance(etapa1, "etapa1")
    best2 = best_per_instance(etapa2, "etapa2")
    best3 = best_per_instance(etapa3, "etapa3")

    ils_vns = compare_ils_vns(etapa3, out)
    stages = compare_stage_best(best1, best2, best3, out)

    with (out / "stats_etapa3.json").open("w", encoding="utf-8") as f:
        json.dump({"ils_vs_vns": ils_vns, "stage_best": stages}, f, ensure_ascii=False, indent=2)

    write_report(out, ils_vns, stages)

    print("=" * 72)
    print("Análise da etapa 3 concluída com sucesso.")
    print(f"Saída: {out.resolve()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
