#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust version of DeepSeek pipeline with better error handling and monitoring
- Enhanced output flushing and progress reporting
- Better timeout and retry logic
- Reduced concurrency to avoid rate limits
- Real-time progress monitoring
"""

import argparse, json, os, re, asyncio, random, unicodedata, time, sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# -------------------- prompt loading --------------------
def _read_text(path: Path, name: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing {name}: {path}")
    return path.read_text(encoding="utf-8")

try:
    HERE = Path(__file__).resolve().parent
except NameError:
    HERE = Path.cwd()

SYSTEM     = _read_text(HERE / "system_prompt.txt",       "system_prompt.txt")
SCHEMA     = _read_text(HERE / "schema.json",  "schema.json")
USER_TMPL  = _read_text(HERE / "user_template.txt","user_template.txt")

SYSTEM += """
[Addendum for core_brief STRICT OUTPUT]
- In core_brief, include: relation_summary_en (English, 1–2 sentences) in addition to relation_summary_zh.
- Keep innovation_quotes strictly from Abstract (verbatim). If more than 4, keep the most central 4. If fewer than 2, return whatever found (the pipeline will supplement).
"""

CORE_TYPES  = {"Model","Variant","AdapterModel"}

# -------------------- utils --------------------
def log_with_flush(msg):
    """Print with immediate flush and timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)
    sys.stdout.flush()

def _nz(x):
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return "" if x is None else str(x)

def fmt_user(title:str, abstract:str, year=None, venue:str="", url:str="") -> str:
    p = USER_TMPL
    return (p.replace("{title}", _nz(title))
             .replace("{abstract}", _nz(abstract))
             .replace("{year}", _nz(year))
             .replace("{venue}", _nz(venue))
             .replace("{url}", _nz(url)))

def _parse_json_strict_or_fallback(txt: str):
    try:
        return json.loads(txt)
    except Exception:
        m = re.search(r"\{.*\}", txt, flags=re.S)
        if m:
            return json.loads(m.group(0))
        raise ValueError("模型未返回合法 JSON。片段: " + txt[:400])

def _norm_text(s: str) -> str:
    if s is None: s = ""
    if not isinstance(s, str): s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("'","'").replace("'","'").replace(""",'"').replace(""",'"').replace("—","-").replace("–","-")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def _split_sentences(text: str):
    t = _norm_text(text)
    parts = re.split(r"(?<=[\.!?。！？])\s+|\n+", t)
    return [p.strip() for p in parts if p.strip()]

def _select_innovation_from_abs(abstract: str, need: int):
    sents = _split_sentences(abstract)
    if not sents:
        return []
    cues = [
        r"\bpropos", r"\bintroduc", r"\bnovel", r"\bmethod", r"\bapproach",
        r"\bmodel", r"\bframework", r"\bimprov", r"\bcontribut", r"\bwe ",
        "提出", "新方法", "新模型", "我们", "改进", "创新", "框架"
    ]
    def score(s):
        ls = s.lower()
        sc = 0
        for c in cues:
            if re.search(c, ls): sc += 1
        if 50 <= len(s) <= 300: sc += 1
        return sc
    ranked = sorted(sents, key=score, reverse=True)
    picked = []
    for sent in ranked:
        if all(sent not in x and x not in sent for x in picked):
            picked.append(sent)
        if len(picked) >= need:
            break
    return picked[:need]

def _english_fallback_summary(abstract: str):
    sents = _split_sentences(abstract)
    en = [s for s in sents if re.search(r"[A-Za-z]", s)]
    if not en:
        return sents[0] if sents else ""
    en = sorted(en, key=lambda s: abs(len(s)-120))
    return en[0][:400]

def _clamp_to_1_2_sentences(text: str):
    sents = _split_sentences(text)
    if not sents:
        return ""
    return " ".join(sents[:2])

def _ensure_2_to_4_quotes(quotes, abstract: str):
    abs_norm = _norm_text(abstract).lower()
    kept = []
    for q in (quotes or []):
        qn = _norm_text(str(q)).strip()
        if not qn: 
            continue
        if qn.lower() in abs_norm:
            kept.append(qn)
    if len(kept) > 4:
        kept = kept[:4]
    if len(kept) < 2:
        need = 2 - len(kept)
        supplements = _select_innovation_from_abs(abstract, need)
        for s in supplements:
            if s not in kept:
                kept.append(s)
            if len(kept) >= 2:
                break
    return kept[:4]

# -------------------- async OpenAI call with better error handling --------------------
async def call_llm_async(model:str, system_prompt:str, user_prompt:str,
                         api_key:str|None, base_url:str|None,
                         timeout_s:float=120.0, max_retries:int=6, backoff_base:float=1.0):
    from openai import AsyncOpenAI
    from openai import AuthenticationError, RateLimitError, APIError, APITimeoutError

    key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("No API key. Set DEEPSEEK_API_KEY / OPENAI_API_KEY or pass --api-key.")
    base_url = base_url or os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com"

    client = AsyncOpenAI(api_key=key, base_url=base_url, timeout=timeout_s)
    last_err = None
    
    for attempt in range(max_retries):
        try:
            log_with_flush(f"API调用尝试 {attempt+1}/{max_retries}")
            resp = await client.chat.completions.create(
                model=model,
                temperature=0.1,
                messages=[
                    {"role":"system","content":system_prompt + "\n\nJSON Schema (for reference):\n" + SCHEMA},
                    {"role":"user","content":user_prompt}
                ],
                response_format={"type":"json_object"}
            )
            txt = resp.choices[0].message.content
            result = _parse_json_strict_or_fallback(txt)
            log_with_flush(f"API调用成功")
            return result
            
        except AuthenticationError as e:
            log_with_flush(f"认证失败: {e}")
            raise RuntimeError("认证失败（API Key 错误或项目不匹配）。") from e
            
        except RateLimitError as e:
            wait_time = backoff_base * (2 ** attempt) + random.random() * 2
            log_with_flush(f"速率限制，等待 {wait_time:.1f}秒...")
            last_err = e
            await asyncio.sleep(wait_time)
            
        except (APITimeoutError, APIError) as e:
            wait_time = backoff_base * (2 ** attempt) + random.random() * 1
            log_with_flush(f"API错误 ({type(e).__name__})，等待 {wait_time:.1f}秒...")
            last_err = e
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            wait_time = backoff_base * (2 ** attempt) + random.random() * 1
            log_with_flush(f"未知错误 ({type(e).__name__}: {e})，等待 {wait_time:.1f}秒...")
            last_err = e
            await asyncio.sleep(wait_time)
    
    log_with_flush(f"所有重试失败，抛出最后错误")
    raise last_err

# -------------------- dataframe helpers --------------------
def _normalize_cols(df: pd.DataFrame) -> dict[str,str]:
    df.columns = [str(c).strip() for c in df.columns]
    return {c.lower(): c for c in df.columns}

def _resolve_required(colmap: dict[str,str], desired: str, synonyms: list[str], available: list[str]) -> str:
    for cand in [desired] + synonyms:
        key = str(cand).strip().lower()
        if key in colmap:
            return colmap[key]
    raise ValueError(f"Missing required column: {desired}. Available: {available}")

def _resolve_optional(colmap: dict[str,str], desired: str, synonyms: list[str]) -> str|None:
    for cand in [desired] + synonyms:
        key = str(cand).strip().lower()
        if key in colmap:
            return colmap[key]
    return None

# -------------------- per-row processing --------------------
def _orig_dict(row):
    return {k: row.get(k, None) for k in row.index}

def _build_core_brief(js:dict, orig:dict):
    if js.get("doc_type") not in CORE_TYPES:
        return None
    cb = js.get("core_brief") or {}
    mn = cb.get("model_names_brief") or []
    bm = cb.get("base_models_brief") or []
    iq = cb.get("innovation_quotes") or []
    zh = cb.get("relation_summary_zh","").strip()
    en = cb.get("relation_summary_en","").strip() or js.get("relation_summary_en","").strip()

    abs_text = _nz(orig.get("Abstract"))
    iq_fixed = _ensure_2_to_4_quotes(iq, abs_text)
    zh_fixed = _clamp_to_1_2_sentences(zh) if zh else ""
    if not en:
        en = _english_fallback_summary(abs_text)
    en_fixed = _clamp_to_1_2_sentences(en)

    return {
        **orig,
        "doc_type": js.get("doc_type"),
        "model_names_brief": json.dumps(mn, ensure_ascii=False),
        "base_models_brief": json.dumps(bm, ensure_ascii=False),
        "innovation_quotes": json.dumps(iq_fixed, ensure_ascii=False),
        "relation_summary_zh": zh_fixed,
        "relation_summary_en": en_fixed,
    }

def _build_non_core(js:dict, orig:dict):
    if js.get("doc_type") in CORE_TYPES:
        return None
    return {**orig, "doc_type": js.get("doc_type")}

async def _process_row(idx:int, row, cols, model, semaphore, api_key, base_url):
    title    = row.get(cols["title"])
    abstract = row.get(cols["abstract"])
    year     = row.get(cols["year"]) if cols["year"] else None
    venue    = row.get(cols["venue"]) if cols["venue"] else ""
    url      = row.get(cols["url"]) if cols["url"] else ""

    user_prompt = fmt_user(title, abstract, year, venue, url)

    async with semaphore:
        try:
            js = await call_llm_async(model, SYSTEM, user_prompt, api_key=api_key, base_url=base_url)
        except Exception as e:
            log_with_flush(f"处理第{idx}行失败: {e}")
            raise

    orig = _orig_dict(row)
    return (
        idx,
        _build_core_brief(js, orig),
        _build_non_core(js, orig),
        str(title)[:80]
    )

# -------------------- batch processing with better monitoring --------------------
async def process_batch_robust(df_batch, batch_num, total_batches, cols, model, concurrency, api_key, base_url):
    """Process a single batch with enhanced monitoring"""
    batch_size = len(df_batch)
    log_with_flush(f"{'='*60}")
    log_with_flush(f"开始处理批次 {batch_num}/{total_batches} ({batch_size} 条记录)")
    log_with_flush(f"并发数: {concurrency}")
    log_with_flush(f"{'='*60}")
    
    # 使用指定的并发数，但保持合理上限
    sem = asyncio.Semaphore(max(1, min(concurrency, 30)))  # 最大并发限制为30
    tasks = []
    
    for idx, (_, row) in enumerate(df_batch.iterrows()):
        tasks.append(_process_row(idx, row, cols, model, sem, api_key, base_url))

    core_brief_rows, non_core_rows = [], []
    processed = 0
    start_time = time.time()
    
    for coro in asyncio.as_completed(tasks):
        try:
            idx, core_row, non_core_row, title_preview = await coro
            processed += 1
            
            # 更频繁的进度报告
            if processed % 5 == 0 or processed <= 10:
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0
                eta = (batch_size - processed) / rate if rate > 0 else 0
                log_with_flush(f"[{processed}/{batch_size}] {title_preview} ... (速度: {rate:.1f}/min, 预计剩余: {eta/60:.1f}min)")
            
            if core_row: 
                core_brief_rows.append(core_row)
            if non_core_row: 
                non_core_rows.append(non_core_row)
                
        except Exception as e:
            log_with_flush(f"处理任务失败: {e}")
            # 继续处理其他任务，不中断整个批次
    
    elapsed = time.time() - start_time
    log_with_flush(f"批次 {batch_num} 完成: {processed}/{batch_size} 条, 用时 {elapsed/60:.1f}分钟")
    return core_brief_rows, non_core_rows

def save_batch_results(core_rows, non_core_rows, batch_num, output_dir):
    """Save batch results to separate files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    batch_file = output_dir / f"batch_{batch_num:03d}.xlsx"
    
    engine = None
    try:
        import xlsxwriter
        engine = "xlsxwriter"
    except Exception:
        try:
            import openpyxl
            engine = "openpyxl"
        except Exception:
            raise RuntimeError("需要安装 xlsxwriter 或 openpyxl 才能写入 .xlsx")

    with pd.ExcelWriter(batch_file, engine=engine) as w:
        pd.DataFrame(core_rows).to_excel(w, index=False, sheet_name="core_brief")
        pd.DataFrame(non_core_rows).to_excel(w, index=False, sheet_name="non_core")
    
    log_with_flush(f"✓ 批次 {batch_num} 已保存: {batch_file} (core: {len(core_rows)}, non_core: {len(non_core_rows)})")
    return batch_file

# -------------------- main robust processing --------------------
async def run_robust_async(in_file: Path, output_dir: str, final_output: str, model: str,
                          title_col="title", abstract_col="abstract",
                          year_col="year", venue_col="venue", url_col="url",
                          sheet=None, batch_size=2000, concurrency=20,  # 默认并发数20
                          api_key=None, base_url=None, start_batch=1):
    
    # Read input file
    if sheet is None:
        if str(in_file).endswith('.parquet'):
            df = pd.read_parquet(in_file)
        else:
            df = pd.read_excel(in_file)
    else:
        df = pd.read_excel(in_file, sheet_name=sheet)
    
    # Normalize columns
    colmap = _normalize_cols(df)
    title_col = _resolve_required(colmap, title_col, ["Title"], list(df.columns))
    abstract_col = _resolve_required(colmap, abstract_col, ["Abstract"], list(df.columns))
    year_col_opt = _resolve_optional(colmap, year_col, ["Year", "Publication year"])
    venue_col_opt = _resolve_optional(colmap, venue_col, ["source","journal","conference","venue"])
    url_col_opt = _resolve_optional(colmap, url_col, ["URL","Url","link","Link","paper url"])
    
    cols = {"title": title_col, "abstract": abstract_col,
            "year": year_col_opt, "venue": venue_col_opt, "url": url_col_opt}
    
    total_rows = len(df)
    total_batches = (total_rows + batch_size - 1) // batch_size
    
    log_with_flush(f"=" * 80)
    log_with_flush(f"稳健批量处理配置")
    log_with_flush(f"=" * 80)
    log_with_flush(f"输入文件: {in_file}")
    log_with_flush(f"总记录数: {total_rows:,}")
    log_with_flush(f"批次大小: {batch_size}")
    log_with_flush(f"总批次数: {total_batches}")
    log_with_flush(f"并发数: {concurrency} (保守设置)")
    log_with_flush(f"开始批次: {start_batch}")
    log_with_flush(f"输出目录: {output_dir}")
    
    # Process batches
    for batch_num in range(start_batch, total_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_rows)
        df_batch = df.iloc[start_idx:end_idx]
        
        try:
            core_rows, non_core_rows = await process_batch_robust(
                df_batch, batch_num, total_batches, cols, model, concurrency, api_key, base_url
            )
            
            save_batch_results(core_rows, non_core_rows, batch_num, output_dir)
            
            # 批次间休息，避免速率限制
            if batch_num < total_batches:
                log_with_flush(f"批次间休息30秒...")
                await asyncio.sleep(30)
            
        except Exception as e:
            log_with_flush(f"✗ 批次 {batch_num} 处理失败: {e}")
            log_with_flush(f"可以使用 --start-batch {batch_num} 重新开始")
            break

# -------------------- CLI --------------------
def main():
    ap = argparse.ArgumentParser(description="稳健的批量信息抽取处理")
    ap.add_argument("--in", dest="infile", required=True, help="输入文件 (.xlsx 或 .parquet)")
    ap.add_argument("--output-dir", default="batch_results", help="批次结果输出目录")
    ap.add_argument("--final-output", default="final_results.xlsx", help="最终合并结果文件")
    ap.add_argument("--model", default="deepseek-chat", help="模型名称")
    ap.add_argument("--title-col", default="title", help="标题列名")
    ap.add_argument("--abstract-col", default="abstract", help="摘要列名")
    ap.add_argument("--year-col", default="year", help="年份列名")
    ap.add_argument("--venue-col", default="venue", help="会议/期刊列名")
    ap.add_argument("--url-col", default="url", help="URL列名")
    ap.add_argument("--sheet", default=None, help="Excel工作表名称或索引")
    ap.add_argument("--batch-size", type=int, default=1000, help="每批次处理的记录数(默认1000)")
    ap.add_argument("--concurrency", type=int, default=20, help="并发请求数(默认20)")
    ap.add_argument("--start-batch", type=int, default=1, help="开始处理的批次号（用于恢复）")
    ap.add_argument("--api-key", default=None, help="API密钥")
    ap.add_argument("--base-url", default="https://api.deepseek.com", help="API基础URL")
    
    args = ap.parse_args()
    
    asyncio.run(run_robust_async(
        Path(args.infile), args.output_dir, args.final_output, args.model,
        title_col=args.title_col, abstract_col=args.abstract_col,
        year_col=args.year_col, venue_col=args.venue_col, url_col=args.url_col,
        sheet=args.sheet, batch_size=args.batch_size, concurrency=args.concurrency,
        api_key=args.api_key, base_url=args.base_url, start_batch=args.start_batch
    ))

if __name__ == "__main__":
    main()
