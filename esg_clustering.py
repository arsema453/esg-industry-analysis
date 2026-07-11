"""
ESG Industry Clustering Analysis
--------------------------------
Groups industries by the *shape* of their Environment/Social/Governance
profile (not just their total score) using k-means clustering.

Input: esg_clean.csv (produced by the SQL cleaning pipeline — see esg_cleaning.sql)
Output: esg_clusters.csv, cluster_scatter.png, elbow_plot.png

Why clustering, and why here:
Ranking industries by Total ESG Score (see Tableau dashboard) answers
"who's on top." It doesn't answer "are there natural groupings of
industries with similar ESG *profiles*, even if their totals differ?"
K-means on the three standardized sub-scores answers that question.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

RANDOM_STATE = 42
FEATURES = ["environment_score", "social_score", "governance_score"]


def load_data(path: str = "esg_clean.csv") -> pd.DataFrame:
    """Load the cleaned, deduplicated industry-level ESG table."""
    df = pd.read_csv(path)
    expected_cols = {"industry", *FEATURES, "total_esg_score"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Input file is missing expected columns: {missing}")
    return df


def choose_k(X_scaled: np.ndarray, k_range=range(2, 9)) -> pd.DataFrame:
    """
    Score candidate values of k by silhouette score (how well-separated
    and internally coherent the resulting clusters are). Returns a table
    so the choice of k is auditable, not just asserted.
    """
    rows = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
        labels = km.fit_predict(X_scaled)
        rows.append({
            "k": k,
            "silhouette_score": round(silhouette_score(X_scaled, labels), 3),
            "inertia": round(km.inertia_, 1),
        })
    return pd.DataFrame(rows)


def fit_clusters(df: pd.DataFrame, k: int) -> tuple[pd.DataFrame, StandardScaler, KMeans]:
    """
    Standardize the three ESG sub-scores (so no single dimension dominates
    purely because of scale — Environment scores run larger in absolute
    terms than Social/Governance) and fit k-means.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURES])

    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
    df = df.copy()
    df["cluster"] = km.fit_predict(X_scaled)
    return df, scaler, km


def summarize_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """Per-cluster averages, sorted by overall ESG performance."""
    summary = (
        df.groupby("cluster")
        .agg(
            n_industries=("industry", "count"),
            avg_environment=("environment_score", "mean"),
            avg_social=("social_score", "mean"),
            avg_governance=("governance_score", "mean"),
            avg_total=("total_esg_score", "mean"),
        )
        .round(1)
        .sort_values("avg_total", ascending=False)
    )
    return summary


def plot_elbow(k_scores: pd.DataFrame, out_path: str = "elbow_plot.png") -> None:
    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.plot(k_scores["k"], k_scores["silhouette_score"], marker="o", color="#2f5d4f")
    ax1.set_xlabel("Number of clusters (k)")
    ax1.set_ylabel("Silhouette score", color="#2f5d4f")
    ax1.set_title("Cluster quality by k (silhouette score)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_clusters_2d(df: pd.DataFrame, scaler: StandardScaler, out_path: str = "cluster_scatter.png") -> None:
    """
    Reduce the 3 standardized ESG dimensions to 2D via PCA purely for
    visualization — clustering itself was done in the full 3D space.
    """
    X_scaled = scaler.transform(df[FEATURES])
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X_scaled)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ["#2f5d4f", "#a3562c", "#3b4a6b", "#8a2e5c"]
    for c in sorted(df["cluster"].unique()):
        mask = df["cluster"] == c
        ax.scatter(coords[mask, 0], coords[mask, 1], label=f"Cluster {c}",
                   color=colors[c % len(colors)], s=60, alpha=0.85, edgecolor="white")
    for i, industry in enumerate(df["industry"]):
        ax.annotate(industry, (coords[i, 0], coords[i, 1]), fontsize=6.5,
                    alpha=0.7, xytext=(3, 3), textcoords="offset points")

    var_explained = pca.explained_variance_ratio_
    ax.set_xlabel(f"PC1 ({var_explained[0]:.0%} of variance)")
    ax.set_ylabel(f"PC2 ({var_explained[1]:.0%} of variance)")
    ax.set_title("Industries clustered by ESG profile shape (PCA projection)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    df = load_data("esg_clean.csv")

    scaler_probe = StandardScaler()
    X_scaled_probe = scaler_probe.fit_transform(df[FEATURES])

    k_scores = choose_k(X_scaled_probe)
    print("Silhouette score by k:")
    print(k_scores.to_string(index=False))
    plot_elbow(k_scores)

    best_k = 3  # chosen from k_scores: strong silhouette + interpretable, non-trivial group sizes
    df_clustered, scaler, km = fit_clusters(df, best_k)

    summary = summarize_clusters(df_clustered)
    print(f"\nCluster summary (k={best_k}):")
    print(summary.to_string())

    print("\nIndustries per cluster:")
    for c in sorted(df_clustered["cluster"].unique()):
        members = df_clustered.loc[df_clustered["cluster"] == c, "industry"].tolist()
        print(f"  Cluster {c}: {', '.join(members)}")

    plot_clusters_2d(df_clustered, scaler)

    df_clustered.sort_values(["cluster", "total_esg_score"], ascending=[True, False]) \
        .to_csv("esg_clusters.csv", index=False)
    print("\nSaved: esg_clusters.csv, elbow_plot.png, cluster_scatter.png")


if __name__ == "__main__":
    main()
