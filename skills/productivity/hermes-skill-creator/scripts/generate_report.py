#!/usr/bin/env python3
"""
Generate a static HTML review report from benchmark results.

This is a Hermes-adapted version of the original eval-viewer/generate_review.py.
Instead of starting an HTTP server, it generates a standalone static HTML file.

Usage:
    python generate_report.py <workspace/iteration-N>
    
Options:
    --static <output_path>   Generate static HTML file at specified path
    --skill-name <name>      Skill name for the report header
    --benchmark <path>       Path to benchmark.json (default: <dir>/benchmark.json)
    
Example:
    python generate_report.py ./workspace/iteration-1 --static ./review.html --skill-name "my-skill"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DASH = "\u2014"  # em dash character for HTML output


def load_benchmark(benchmark_dir: Path) -> dict:
    """Load benchmark.json from directory."""
    benchmark_path = benchmark_dir / "benchmark.json"
    if not benchmark_path.exists():
        print(f"benchmark.json not found at {benchmark_path}")
        return {}
    return json.loads(benchmark_path.read_text())


def load_run_results(benchmark_dir: Path) -> list[dict]:
    """Load individual run results from eval directories."""
    results = []
    for eval_dir in sorted(benchmark_dir.glob("eval-*")):
        eval_name = eval_dir.name
        
        metadata = {}
        meta_path = eval_dir / "eval_metadata.json"
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text())
        
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            config = config_dir.name
            if config in ("inputs",):
                continue
            
            for run_dir in sorted(config_dir.glob("run-*")):
                grading_path = run_dir / "grading.json"
                timing_path = run_dir / "timing.json"
                
                grading = {}
                timing = {}
                
                if grading_path.exists():
                    grading = json.loads(grading_path.read_text())
                if timing_path.exists():
                    timing = json.loads(timing_path.read_text())
                
                outputs_dir = run_dir / "outputs"
                output_files = []
                if outputs_dir.exists():
                    output_files = [str(f.relative_to(outputs_dir)) for f in sorted(outputs_dir.iterdir()) if f.is_file()]
                
                results.append({
                    "eval_name": eval_name,
                    "eval_id": metadata.get("eval_id", eval_name),
                    "prompt": metadata.get("prompt", ""),
                    "config": config,
                    "run_number": run_dir.name,
                    "grading": grading,
                    "timing": timing,
                    "output_files": output_files,
                    "outputs_dir": str(outputs_dir) if outputs_dir.exists() else ""
                })
    
    return results


def generate_html(benchmark: dict, run_results: list[dict], skill_name: str = "") -> str:
    """Generate static HTML report."""
    meta = benchmark.get("metadata", {})
    run_summary = benchmark.get("run_summary", {})
    notes = benchmark.get("notes", [])
    
    name = skill_name or meta.get("skill_name", "Unknown Skill")
    timestamp = meta.get("timestamp", datetime.now().isoformat())
    
    configs = [k for k in run_summary if k != "delta"]
    delta = run_summary.get("delta", {})
    
    # Build summary table rows
    summary_rows = ""
    
    # Pass Rate row
    if configs:
        summary_rows += "<tr><td>Pass Rate</td>"
        for c in configs:
            s = run_summary.get(c, {}).get("pass_rate", {})
            summary_rows += f"<td>{s.get('mean', 0)*100:.0f}% &plusmn; {s.get('stddev', 0)*100:.0f}%</td>"
        summary_rows += f"<td>{delta.get('pass_rate', DASH)}</td></tr>"
    
    # Time row
    if configs:
        summary_rows += "<tr><td>Time</td>"
        for c in configs:
            s = run_summary.get(c, {}).get("time_seconds", {})
            summary_rows += f"<td>{s.get('mean', 0):.1f}s &plusmn; {s.get('stddev', 0):.1f}s</td>"
        summary_rows += f"<td>{delta.get('time_seconds', DASH)}s</td></tr>"
    
    # Tokens row
    if configs:
        summary_rows += "<tr><td>Tokens</td>"
        for c in configs:
            s = run_summary.get(c, {}).get("tokens", {})
            summary_rows += f"<td>{s.get('mean', 0):.0f} &plusmn; {s.get('stddev', 0):.0f}</td>"
        summary_rows += f"<td>{delta.get('tokens', DASH)}</td></tr>"
    
    # Build per-eval results
    eval_html = ""
    for eval_name, data in sorted(run_results.items()):
        eval_html += f"<h3>Eval: {eval_name}</h3>"
        if data.get("prompt"):
            eval_html += f"<p><em>Prompt:</em> {data['prompt']}</p>"
        eval_html += "<table><tr><th>Config</th><th>Run</th><th>Pass Rate</th><th>Time</th><th>Errors</th><th>Output Files</th></tr>"
        for r in data.get("runs", []):
            pr = r.get("grading", {}).get("summary", {}).get("pass_rate", 0)
            pr_class = "pass" if pr >= 0.5 else "fail"
            time_val = r.get("timing", {}).get("total_duration_seconds", 0)
            errors = r.get("grading", {}).get("execution_metrics", {}).get("errors_encountered", 0)
            files = ", ".join(r.get("output_files", [])) if r.get("output_files") else DASH
            eval_html += f"<tr><td>{r['config'].replace('_', ' ').title()}</td><td>{r['run_number']}</td><td class='{pr_class}'>{pr*100:.0f}%</td><td>{time_val:.1f}s</td><td>{errors}</td><td>{files}</td></tr>"
        eval_html += "</table>"
        
        # Expectations detail
        for r in data.get("runs", []):
            expectations = r.get("grading", {}).get("expectations", [])
            if expectations:
                eval_html += f"<h4>{r['config'].replace('_', ' ').title()} - {r['run_number']} Expectations:</h4>"
                eval_html += "<table><tr><th>Expectation</th><th>Result</th><th>Evidence</th></tr>"
                for e in expectations:
                    cls = "pass" if e.get("passed") else "fail"
                    label = "PASS" if e.get("passed") else "FAIL"
                    eval_html += f"<tr><td>{e.get('text', '')}</td><td class='{cls}'>{label}</td><td><small>{e.get('evidence', '')}</small></td></tr>"
                eval_html += "</table>"
    
    # Build notes
    notes_html = ""
    if notes:
        for note in notes:
            notes_html += f"<div class='note'>{note}</div>"
    else:
        notes_html = "<p>No notes recorded.</p>"
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Skill Review: {name}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #e0e0e0; }}
h1, h2, h3 {{ color: #e94560; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #333; }}
th {{ background: #16213e; color: #e94560; }}
tr:hover {{ background: #0f3460; }}
.pass {{ color: #4ecca3; font-weight: bold; }}
.fail {{ color: #e94560; font-weight: bold; }}
.section {{ background: #16213e; border-radius: 8px; padding: 16px; margin: 16px 0; }}
.note {{ background: #2d2d44; border-left: 4px solid #e94560; padding: 8px 12px; margin: 8px 0; }}
pre {{ background: #0d0d1a; padding: 12px; border-radius: 4px; overflow-x: auto; }}
</style>
</head>
<body>
<h1>Skill Review: {name}</h1>
<p><small>Generated: {timestamp}</small></p>

<div class="section">
<h2>Performance Summary</h2>
<table>
<tr><th>Metric</th><th>{'</th><th>'.join(c.replace('_', ' ').title() for c in configs)}</th><th>Delta</th></tr>
{summary_rows}
</table>
</div>

<div class="section">
<h2>Eval Results</h2>
{eval_html}
</div>

<div class="section">
<h2>Notes</h2>
{notes_html}
</div>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate static HTML review report from benchmark results"
    )
    parser.add_argument(
        "benchmark_dir",
        type=Path,
        help="Path to the benchmark/iteration directory"
    )
    parser.add_argument(
        "--static",
        type=Path,
        default=None,
        help="Output path for static HTML file"
    )
    parser.add_argument(
        "--skill-name",
        default="",
        help="Skill name for the report header"
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=None,
        help="Path to benchmark.json (default: <benchmark_dir>/benchmark.json)"
    )

    args = parser.parse_args()

    if not args.benchmark_dir.exists():
        print(f"Directory not found: {args.benchmark_dir}")
        sys.exit(1)

    # Load benchmark.json
    benchmark_path = args.benchmark or (args.benchmark_dir / "benchmark.json")
    benchmark = {}
    if benchmark_path.exists():
        benchmark = json.loads(benchmark_path.read_text())
    else:
        print(f"Warning: benchmark.json not found at {benchmark_path}")

    # Load run results organized by eval
    raw_results = load_run_results(args.benchmark_dir)
    run_results = {}
    for r in raw_results:
        key = r["eval_name"]
        if key not in run_results:
            run_results[key] = {"prompt": r["prompt"], "runs": []}
        run_results[key]["runs"].append(r)

    # Generate report
    html = generate_html(benchmark, run_results, args.skill_name)

    # Write output
    output_path = args.static or (args.benchmark_dir / "review.html")
    output_path.write_text(html)
    print(f"Generated review report: {output_path}")


if __name__ == "__main__":
    main()
