import pandas as pd
from itertools import combinations
from collections import defaultdict, Counter
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

csv_path = "./datasets/cve_results_5.4.0.csv"
df = pd.read_csv(csv_path)

syscall_to_funcs = defaultdict(set)
for _, row in df.iterrows():
    func = row['해당함수'].strip()
    syscall_list = [s.strip() for s in str(row['시스템콜 목록']).split(',')]
    for sc in syscall_list:
        syscall_to_funcs[sc].add(func)

syscalls = list(syscall_to_funcs.keys())

jaccard_df = pd.DataFrame(index=syscalls, columns=syscalls, dtype=float)
for sc1, sc2 in combinations(syscalls, 2):
    funcs1, funcs2 = syscall_to_funcs[sc1], syscall_to_funcs[sc2]
    inter = funcs1 & funcs2
    union = funcs1 | funcs2
    jac = len(inter) / len(union) if union else 0.0
    if len(inter) <= 2:
        jac = 0.0
    jaccard_df.at[sc1, sc2] = jac
    jaccard_df.at[sc2, sc1] = jac
for sc in syscalls:
    jaccard_df.at[sc, sc] = 1.0

similarities = jaccard_df.stack()
filtered = similarities[(similarities < 1.0) & (similarities >= 0.5)]
counter = Counter()
for (a, b), _ in filtered.items():
    counter[a] += 1
    counter[b] += 1

filtered_syscalls = list(counter.keys())
top_syscalls = [s for s, _ in counter.most_common(50)]
filtered_matrix = jaccard_df.loc[top_syscalls, top_syscalls].fillna(0.0)
filtered_syscalls = filtered_matrix.index.tolist()

coords = PCA(n_components=2).fit_transform(filtered_matrix)
plot_df = pd.DataFrame(coords, columns=['PC1', 'PC2'])
plot_df['syscall'] = filtered_syscalls

kmeans = KMeans(n_clusters=4, random_state=42)
plot_df['cluster'] = kmeans.fit_predict(coords)

cluster_to_syscalls = plot_df.groupby('cluster')['syscall'].apply(list).to_dict()

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(24, 22))
axes = axes.flatten()

vmin, vmax = 0.0, 1.0
heatmap_mappable = None

for idx, (cid, syscall_list) in enumerate(sorted(cluster_to_syscalls.items())):
    if idx >= len(axes):
        break

    cluster_matrix = jaccard_df.loc[syscall_list, syscall_list].fillna(0.0)
    if cluster_matrix.shape[0] < 2:
        continue

    ax = axes[idx]
    hm = sns.heatmap(
        cluster_matrix, ax=ax, cmap="YlGnBu",
        vmin=vmin, vmax=vmax, cbar=False,
        square=True, xticklabels=True, yticklabels=True
    )

    ax.set_title(f"Cluster {cid}", fontsize=50)
    ax.tick_params(axis='x', labelsize=35, rotation=90)
    ax.tick_params(axis='y', labelsize=35)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=30, ha='right', va='center', rotation_mode='anchor')

    if heatmap_mappable is None:
        heatmap_mappable = hm.get_children()[0]

for j in range(idx + 1, len(axes)):
    fig.delaxes(axes[j])

cbar_ax = fig.add_axes([0.88, 0.15, 0.015, 0.7])
fig.colorbar(heatmap_mappable, cax=cbar_ax)
cbar_ax.tick_params(labelsize=30)

plt.subplots_adjust(left=0.05, right=0.92, top=0.92, bottom=0.08, wspace=0.02, hspace=0.55)
plt.savefig("./claim/fig5.png", dpi=300, bbox_inches='tight')
plt.close()
