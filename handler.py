#!/usr/bin/env python3
"""OpenClaw Search - 从 GitHub 仓库查询 OpenClaw 相关信息"""

import json
import subprocess
import sys
import re

CONFIG_PATH = "/mnt/e/OpenClow_Output/agents/main/skills/openclaw-search/config.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def parse_intent(query: str, config: dict) -> str:
    """解析用户意图，返回要搜索的仓库键名"""
    query_lower = query.lower()
    keywords = config.get("keywords", {})
    
    for keyword, repo_key in keywords.items():
        if keyword.lower() in query_lower:
            return repo_key
    
    return None  # 不确定，搜索所有

def search_repo_by_name(repo_full_name: str) -> list:
    """根据仓库名搜索仓库"""
    url = f"https://api.github.com/search/repositories?q=repo:{repo_full_name}&per_page=1"
    
    try:
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        data = json.loads(result.stdout)
        
        if "items" in data and data["items"]:
            item = data["items"][0]
            return [{
                "name": item.get("name", ""),
                "full_name": item.get("full_name", ""),
                "description": item.get("description", ""),
                "url": item.get("html_url", ""),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0)
            }]
    except Exception:
        pass
    
    return []

def search_code(query: str, repo_full_name: str) -> list:
    """搜索仓库内的代码（用仓库内容匹配）"""
    url = f"https://api.github.com/repos/{repo_full_name}/contents?per_page=50"
    
    results = []
    
    try:
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        data = json.loads(result.stdout)
        
        if isinstance(data, list):
            query_lower = query.lower()
            for item in data:
                name = item.get("name", "").lower()
                if query_lower in name:
                    results.append({
                        "name": item.get("name", ""),
                        "path": item.get("name", ""),
                        "full_name": repo_full_name,
                        "url": item.get("html_url", ""),
                        "type": item.get("type", "")
                    })
                
                # 也检查 description 如果是 README
                if item.get("type") == "file" and "readme" in name.lower():
                    results.append({
                        "name": "📖 README",
                        "path": item.get("name", ""),
                        "full_name": repo_full_name,
                        "url": item.get("html_url", ""),
                        "type": "readme"
                    })
    except Exception:
        pass
    
    return results

def main():
    args = sys.argv[1:]
    if not args:
        print("用法: openclaw-search <查询内容>")
        sys.exit(1)
    
    query = " ".join(args)
    
    # 移除 trigger 关键词
    query = re.sub(r'^openclaw\s*', '', query, flags=re.IGNORECASE).strip()
    
    if not query:
        print("请输入查询内容")
        sys.exit(1)
    
    config = load_config()
    repos = config.get("repos", {})
    
    # 解析意图
    intent_repo = parse_intent(query, config)
    
    all_results = []
    
    if intent_repo:
        # 精确匹配 - 搜索对应仓库
        repo_key = repos.get(intent_repo)
        if repo_key:
            # 先获取仓库信息
            repo_info = search_repo_by_name(repo_key)
            all_results.extend(repo_info)
            
            # 再搜索代码
            code_results = search_code(query, repo_key)
            all_results.extend(code_results)
    else:
        # 模糊搜索 - 搜索所有仓库
        for repo_key in repos.values():
            repo_info = search_repo_by_name(repo_key)
            all_results.extend(repo_info)
    
    if not all_results:
        print(f"未找到与「{query}」相关的 OpenClaw 信息")
        print("\n💡 试试：openclaw skill / openclaw 用例 / openclaw 文档")
        return
    
    # 去重
    seen = set()
    unique_results = []
    for r in all_results:
        key = r.get("url", r.get("full_name", ""))
        if key and key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    unique_results = unique_results[:8]
    
    # 输出
    print(f"🔍 查询: {query}\n")
    
    # 先输出仓库
    repo_results = [r for r in unique_results if "stars" in r]
    file_results = [r for r in unique_results if "stars" not in r]
    
    if repo_results:
        print("📦 仓库:")
        for i, item in enumerate(repo_results, 1):
            print(f"  {i}. {item['full_name']}")
            desc = item.get("description", "")
            if desc:
                print(f"     {desc[:70]}")
            print(f"     ⭐ {item.get('stars', 0)} | 🍴 {item.get('forks', 0)}")
            print(f"     🔗 {item['url']}")
            print()
    
    if file_results:
        print("📄 文件:")
        for i, item in enumerate(file_results, 1):
            print(f"  {i}. {item['name']}")
            print(f"     🔗 {item['url']}")
            print()

if __name__ == "__main__":
    main()
