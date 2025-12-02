import pandas as pd
import ast
import json
import numpy as np

df = pd.read_csv('5_bertopic_results_vocab.csv')

# --- Preprocessing ---
df['model_names_brief'] = df['model_names_brief'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
df['base_models_brief'] = df['base_models_brief'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# Filter data for meaningful years (e.g., 2012-2024) to avoid long flat tails
df_recent = df[df['Publication year'] >= 2012].copy()

# --- 1. Level 1 Topic Evolution (Stacked Area) ---
# Format: { "years": [2012, ...], "series": [ { "name": "Topic A", "data": [1, 5, ...] } ] }
trend_l1 = df_recent.groupby(['Publication year', '一级主题']).size().unstack(fill_value=0)
years = trend_l1.index.tolist()

l1_series = []
for column in trend_l1.columns:
    l1_series.append({
        "name": column,
        "type": "line",
        "stack": "Total",
        "areaStyle": {},
        "data": trend_l1[column].tolist()
    })

chart1_data = {
    "title": "Level 1 Innovation Evolution",
    "categories": years,
    "series": l1_series
}

# --- 2. Innovation Nature (Doc Type) Evolution (Line/Area) ---
trend_doc = df_recent.groupby(['Publication year', 'doc_type']).size().unstack(fill_value=0)

doc_series = []
for column in trend_doc.columns:
    doc_series.append({
        "name": column,
        "type": "line",  # Can be changed to stack if preferred
        "smooth": True,
        "data": trend_doc[column].tolist()
    })

chart2_data = {
    "title": "Innovation Nature Evolution",
    "categories": years,
    "series": doc_series
}

# --- 3. Technical Model Influence (Top Base Models Bar Chart) ---
# Users often want to see "Who is the king?"
df_exploded = df.explode('base_models_brief')
top_bases = df_exploded['base_models_brief'].value_counts().head(15)

# 删除LLM模型
top_bases = top_bases[top_bases.index != 'LLM']

chart3_data = {
    "title": "Top Base Model Influence",
    "categories": top_bases.index.tolist(),
    "values": top_bases.values.tolist()
}

# --- 4. Sankey Diagram (Base Model -> Level 1 Topic) ---
# Filter for top 10 base models to keep Sankey clean
top_10_bases = top_bases.head(10).index.tolist()
df_sankey = df_exploded[df_exploded['base_models_brief'].isin(top_10_bases)]

# Group by (Base, L1)
sankey_counts = df_sankey.groupby(['base_models_brief', '一级主题']).size().reset_index(name='value')

# Generate Nodes and Links
# Nodes must be unique list of all Bases + all Topics
bases_in_sankey = sankey_counts['base_models_brief'].unique().tolist()
topics_in_sankey = sankey_counts['一级主题'].unique().tolist()
all_nodes = list(set(bases_in_sankey + topics_in_sankey))

nodes_data = [{"name": n} for n in all_nodes]

links_data = []
for _, row in sankey_counts.iterrows():
    links_data.append({
        "source": row['base_models_brief'],
        "target": row['一级主题'],
        "value": int(row['value'])
    })

chart4_data = {
    "title": "Base Model to Innovation Mapping",
    "nodes": nodes_data,
    "links": links_data
}

# --- Combine all into one JSON structure ---
dashboard_data = {
    "evolution_l1": chart1_data,
    "evolution_nature": chart2_data,
    "model_influence": chart3_data,
    "sankey_flow": chart4_data
}

# Save to file
with open('dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

print("dashboard_data.json generated.")
print(f"\n数据统计:")
print(f"  - 一级主题演化: {len(chart1_data['series'])} 个系列, {len(chart1_data['categories'])} 个年份")
print(f"  - 创新性质演化: {len(chart2_data['series'])} 个系列, {len(chart2_data['categories'])} 个年份")
print(f"  - 模型影响力: {len(chart3_data['categories'])} 个模型")
print(f"  - 桑基图: {len(chart4_data['nodes'])} 个节点, {len(chart4_data['links'])} 条链接")

