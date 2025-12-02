#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成技术演化树数据 evolution_tree.json
结构：Root -> Base Models -> Level 1 Topics -> Specific Models (Leaf Nodes)
"""

import pandas as pd
import json
from collections import defaultdict

def generate_evolution_tree():
    """生成演化树数据"""
    print("正在读取数据...")
    df = pd.read_csv('5_bertopic_results_vocab.csv')
    
    # 解析列表字段
    df['model_names_brief'] = df['model_names_brief'].apply(
        lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else []
    )
    df['base_models_brief'] = df['base_models_brief'].apply(
        lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else []
    )
    
    # 构建树形结构
    tree = {
        "name": "AI创新机制演化树",
        "collapsed": False,
        "children": []
    }
    
    # 按基础模型分组
    base_model_groups = defaultdict(lambda: defaultdict(list))
    
    for idx, row in df.iterrows():
        base_models = row['base_models_brief']
        if not base_models or len(base_models) == 0:
            base_models = ['Other']
        
        level1_topic = row['一级主题']
        model_names = row['model_names_brief']
        
        # 为每个基础模型添加记录
        for base_model in base_models:
            base_model_groups[base_model][level1_topic].append({
                'model_names': model_names,
                'year': int(row['Publication year']) if pd.notna(row['Publication year']) else 2020,
                'type': row['doc_type'],
                'desc': row['relation_summary_zh'],
                'topic': row['二级主题']
            })
    
    # 构建树的子节点
    # 只选择Top 10基础模型，避免树太大
    top_base_models = sorted(
        base_model_groups.items(),
        key=lambda x: sum(len(topics) for topics in x[1].values()),
        reverse=True
    )[:10]
    
    for base_model, level1_topics in top_base_models:
        base_node = {
            "name": base_model,
            "collapsed": True,  # 默认折叠
            "symbolSize": 30,
            "itemStyle": {"color": "#3b82f6"},
            "children": []
        }
        
        # 为每个一级主题创建节点
        for level1_topic, records in level1_topics.items():
            level1_node = {
                "name": level1_topic,
                "collapsed": True,  # 默认折叠
                "symbolSize": 20,
                "itemStyle": {"color": "#8b5cf6"},
                "children": []
            }
            
            # 为每条记录创建叶子节点
            # 限制每个一级主题最多显示前20个模型
            for record in records[:20]:
                model_names = record['model_names']
                if not model_names or len(model_names) == 0:
                    model_name = f"{record['topic']} ({record['year']})"
                else:
                    model_name = model_names[0] if len(model_names) > 0 else "Unknown"
                
                leaf_node = {
                    "name": model_name,
                    "symbolSize": 12,
                    "itemStyle": {"color": "#10b981"},
                    "attributes": {
                        "year": record['year'],
                        "type": record['type'],
                        "desc": record['desc'],
                        "topic": record['topic']
                    }
                }
                
                level1_node['children'].append(leaf_node)
            
            if level1_node['children']:  # 只添加有子节点的节点
                base_node['children'].append(level1_node)
        
        if base_node['children']:  # 只添加有子节点的节点
            tree['children'].append(base_node)
    
    return tree

def main():
    print("正在生成技术演化树数据...")
    tree = generate_evolution_tree()
    
    # 统计信息
    base_model_count = len(tree['children'])
    level1_count = sum(len(base['children']) for base in tree['children'])
    leaf_count = sum(
        len(level1['children']) 
        for base in tree['children'] 
        for level1 in base['children']
    )
    
    print(f"\n树结构统计:")
    print(f"  根节点: 1")
    print(f"  基础模型节点: {base_model_count}")
    print(f"  一级主题节点: {level1_count}")
    print(f"  叶子节点（具体模型）: {leaf_count}")
    print(f"  总节点数: {1 + base_model_count + level1_count + leaf_count}")
    
    # 保存到文件
    output_file = 'dashboard/public/data/evolution_tree.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {output_file}")
    print("完成！")

if __name__ == '__main__':
    main()

