import glob
import os
import re
from collections import defaultdict, Counter
from itertools import combinations
from sklearn.decomposition import PCA
from adjustText import adjust_text
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt

folder_path = './datasets/csvs/'
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

data = []
for file in csv_files:
    df = pd.read_csv(file)
    if list(df.columns[:3]) == ['파일명', '시스템콜', '해당함수']:
        data.append(df[['시스템콜', '해당함수']])

merged_df = pd.concat(data, ignore_index=True)

def normalize(func_name):
    return re.sub(r'\.part\.\d+|\.isra\.\d+|\.constprop\.\d+', '', func_name)

merged_df['해당함수'] = merged_df['해당함수'].apply(normalize)

syscall_to_funcs_raw = merged_df.groupby('시스템콜')['해당함수'].apply(set).to_dict()

func_counter = defaultdict(int)
for funcs in syscall_to_funcs_raw.values():
    for f in funcs:
        func_counter[f] += 1

total_syscalls = len(syscall_to_funcs_raw)
common_funcs = {f for f, count in func_counter.items() if count / total_syscalls >= 0.7}

syscall_to_funcs = {
    s: funcs - common_funcs for s, funcs in syscall_to_funcs_raw.items()
}

syscalls = list(syscall_to_funcs.keys())

similarity_matrix = pd.DataFrame(index=syscalls, columns=syscalls, dtype=float)

def jaccard_similarity(a, b):
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union != 0 else 0.0

for a, b in combinations(syscalls, 2):
    sim = jaccard_similarity(syscall_to_funcs[a], syscall_to_funcs[b])
    if sim >= 0.3:
        similarity_matrix.at[a, b] = sim
        similarity_matrix.at[b, a] = sim

for s in syscalls:
    similarity_matrix.at[s, s] = 1.0

similarities = similarity_matrix.stack()
filtered = similarities[(similarities < 1.0) & (similarities >= 0.7)]

counter = Counter()
for (a, b), _ in filtered.items():
    counter[a] += 1
    counter[b] += 1

top_syscalls = [s for s, _ in counter.most_common(50)]
top_matrix = similarity_matrix.loc[top_syscalls, top_syscalls].fillna(0.0)

exclude_functions = {
    "syscall", "printf", "do_syscall_64", "x64_sys_call", "smp_irq_work_interrupt", "irq_enter", "irq_exit",
    "rcu_irq_enter", "rcu_irq_exit", "_raw_spin_lock", "_raw_spin_unlock",
    "_raw_spin_lock_irqsave", "_raw_spin_unlock_irqrestore", "__wake_up",
    "__wake_up_common", "__wake_up_common_lock"
}

pca = PCA(n_components=2)
coords = pca.fit_transform(top_matrix.fillna(0.0))

kmeans = KMeans(n_clusters=5, n_init=10, random_state=42)
cluster_labels = kmeans.fit_predict(coords)

plot_df = pd.DataFrame(coords, columns=['PC1', 'PC2'])
plot_df['syscall'] = top_matrix.index
plot_df['cluster'] = cluster_labels

sns.set(style="white", context="notebook")
palette = sns.color_palette("Set2", n_colors=10)

plt.figure(figsize=(12, 9))
texts = []

for i in sorted(set(cluster_labels)):
    mask = plot_df['cluster'] == i
    sns.kdeplot(
        x=plot_df.loc[mask, 'PC1'],
        y=plot_df.loc[mask, 'PC2'],
        fill=True,
        alpha=0.3,
        linewidth=1,
        color=palette[i]
    )

for i in sorted(set(cluster_labels)):
    mask = plot_df['cluster'] == i
    plt.scatter(
        plot_df.loc[mask, 'PC1'],
        plot_df.loc[mask, 'PC2'],
        s=90,
        color=palette[i],
        edgecolor='black',
        label=f"Cluster {i}"
    )
    for _, row in plot_df[mask].iterrows():
        texts.append(plt.text(row['PC1'], row['PC2'], row['syscall'], fontsize=15))

adjust_text(
    texts,
    arrowprops=dict(arrowstyle="-", color='gray', lw=0.5),
    expand_points=(1.2, 1.4),
    expand_text=(1.2, 1.4),
    force_text=1.0,
    force_points=1.0,
)

plt.title("System Call Clustering", fontsize=25)
plt.xlabel("Principal Component 1", fontsize=20)
plt.ylabel("Principal Component 2", fontsize=20)

plt.legend(
    title="Cluster",
    title_fontsize=22,
    fontsize=20,
    loc='upper right',
    frameon=True,
    framealpha=0.9,
    edgecolor='black',
    facecolor='white'
)

plt.tight_layout()
plt.savefig("./claim/fig3.png", dpi=300)

import matplotlib.pyplot as plt
import seaborn as sns
import os

for cid in sorted(plot_df['cluster'].unique()):
    members = plot_df[plot_df['cluster'] == cid]['syscall'].tolist()
    
    cluster_matrix = similarity_matrix.loc[members, members].fillna(0.0)

target_clusters = [3,4]

vmin, vmax = 0.0, 1.0

fig, axes = plt.subplots(1, 2, figsize=(22, 15))
cbar_ax = fig.add_axes([0.92, 0.3, 0.015, 0.4])

for i, cid in enumerate(target_clusters):
    members = plot_df[plot_df['cluster'] == cid]['syscall'].tolist()
    cluster_matrix = similarity_matrix.loc[members, members].fillna(0.0)

    ax = axes[i]
    sns.heatmap(
        cluster_matrix,
        cmap="YlGnBu",
        annot=False,
        fmt=".2f",
        xticklabels=True,
        yticklabels=True,
        square=True,
        vmin=vmin,
        vmax=vmax,
        cbar=(i == len(target_clusters) - 1),
        cbar_ax=cbar_ax if i == len(target_clusters) - 1 else None,
        ax=ax
    )

    ax.set_title(f"Cluster {cid}", fontsize=50)
    ax.tick_params(axis='x', labelsize=40, rotation=90)
    ax.tick_params(axis='y', labelsize=40)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=30, ha='right', va='center', rotation_mode='anchor')

cbar_ax.tick_params(labelsize=40)

plt.tight_layout(rect=[0, 0, 0.9, 0.9])
plt.savefig("./claim/fig4.png", dpi=300, bbox_inches='tight')
