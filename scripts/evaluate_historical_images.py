#!/usr/bin/env python3
"""Build a read-only review of historical sources, old AI art and image edits.

This does not generate images, call an API, or change game assets. Similarity is
only a diagnostic; subject identity and historical accuracy need visual review.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
from urllib.parse import quote

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from style_historical_image import similarity_scores


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = REPO_ROOT / "assets/historical/review"
GAME_ASPECT = (27, 11)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opened(path: Path) -> Image.Image:
    with Image.open(path) as image:
        image.load()
        return ImageOps.exif_transpose(image).convert("RGB")


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def inspect_edit(source: Image.Image, output_path: Path) -> dict:
    output = opened(output_path)
    diagnostic_size = source.copy()
    diagnostic_size.thumbnail((512, 512), Image.Resampling.LANCZOS)
    original = np.asarray(diagnostic_size, dtype=np.float32) / 255.0
    edited = np.asarray(output.resize(diagnostic_size.size, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    pixel, structure = similarity_scores(original, edited)
    ratio_error = abs(output.width / output.height / (source.width / source.height) - 1)
    retained_area = min(output.width / output.height / (27 / 11), (27 / 11) / (output.width / output.height))
    return {
        "output": relative(output_path),
        "output_sha256": digest(output_path),
        "output_size": list(output.size),
        "aspect_ratio_relative_error": round(ratio_error, 5),
        "source_aligned_pixel_ssim": round(pixel, 5),
        "source_aligned_structure_ssim": round(structure, 5),
        "center_crop_27_11_retained_area": round(retained_area, 5),
        "diagnostic_note": "SSIM compares resized images, without registration. Aspect or composition changes can lower it; a high value does not prove historical accuracy.",
    }


def panel(path: Path | None, width: int, height: int, *, crop: bool = False) -> Image.Image:
    canvas = Image.new("RGB", (width, height), "#24272c")
    if path is None or not path.exists():
        ImageDraw.Draw(canvas).text((18, 24), "AI OUTPUT PENDING", fill="#f0c38b")
        return canvas
    image = opened(path)
    if crop:
        image = ImageOps.fit(image, (width, round(width * 11 / 27)), Image.Resampling.LANCZOS)
    image.thumbnail((width - 12, height - 12), Image.Resampling.LANCZOS)
    canvas.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return canvas


def image_html(path: str | None, label: str, *, crop: bool = False, base_dir: Path = REVIEW_DIR) -> str:
    if path is None or not (REPO_ROOT / path).exists():
        return f'<figure><div class="pending">{html.escape(label)}：等待生成</div></figure>'
    url = quote(Path(os.path.relpath(REPO_ROOT / path, base_dir)).as_posix(), safe="/")
    mode = "crop" if crop else "full"
    return f'<figure><a href="{url}" target="_blank"><img class="{mode}" src="{url}" loading="lazy" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>'


def write_review(config: dict, reviews: list[dict], output_dir: Path, *, images_dir: Path = REPO_ROOT / "assets/historical/processed") -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    by_name = {item["name"]: item for item in reviews}
    def asset_html(path: str | None, label: str, *, crop: bool = False) -> str:
        return image_html(path, label, crop=crop, base_dir=output_dir)
    rows = []
    cards = []
    for index, task in enumerate(config["historical_images"]["images"], 1):
        source_path = REPO_ROOT / task["source"]
        source = opened(source_path)
        review = by_name.get(source_path.stem, {})
        generated = images_dir / task["output"]
        row = {
            "index": index, "name": source_path.stem, "source": task["source"],
            "source_size": list(source.size), "source_sha256": digest(source_path),
            "source_review": review, "status": "generated" if generated.exists() else "pending",
            "planned_output": relative(generated),
        }
        if generated.exists():
            row.update(inspect_edit(source, generated))
        rows.append(row)
        existing = review.get("existing_ai")
        current = relative(generated) if generated.exists() else None
        findings = review.get("source_findings", [])
        if isinstance(findings, str):
            findings = [findings]
        notes = "；".join(findings)
        action = review.get("suggested_action", "待人工评估")
        if isinstance(action, list):
            action = "；".join(action)
        suitability = review.get("source_suitability", "待核验")
        label = f'{index:02d} {source_path.stem}'
        metrics = "等待 AI 生成"
        if generated.exists():
            metrics = f'输出 {row["output_size"][0]}×{row["output_size"][1]} · 宽高比偏差 {row["aspect_ratio_relative_error"]:.1%} · 结构 SSIM {row["source_aligned_structure_ssim"]:.3f} · 横幅保留面积 {row["center_crop_27_11_retained_area"]:.0%}'
        cards.append(
            f'<article data-name="{html.escape(source_path.stem)}" data-state="{html.escape(suitability)}">'
            f'<h2>{html.escape(label)} <small>{html.escape(suitability)}</small></h2>'
            '<div class="grid">' + asset_html(task["source"], "参考源图")
            + asset_html(existing, "原有纯 AI") + asset_html(current, "本轮图生图") + '</div>'
            '<div class="grid crop-row"><div class="notes">'
            f'<p>{html.escape(notes)}</p><p>建议：{html.escape(action)}</p></div>'
            + asset_html(existing, "纯 AI · 27:11 居中裁剪示意", crop=True)
            + asset_html(current, "图生图 · 27:11 居中裁剪示意", crop=True) + '</div>'
            f'<p class="metrics">{html.escape(metrics)}</p></article>'
        )

    generated_count = sum(row["status"] == "generated" for row in rows)
    from generate_historical_images import PROMPTS_PATH
    prompt_set = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    summary = {
        "generated": generated_count, "requested": len(rows),
        "execution": "project_cli_images_edits", "model": config["historical_images"]["model"],
        "endpoint": config["historical_images"]["endpoint"],
        "prompt_file": relative(PROMPTS_PATH), "configured_prompts": prompt_set,
        "prompt_note": "Configured prompts describe the next generation. Existing outputs may have been generated with earlier prompts; consult the archived baseline for those.",
        "images_dir": relative(images_dir),
        "game_aspect": list(GAME_ASPECT),
        "evaluation_scope": "Visual comparison and unregistered SSIM diagnostics. No automatic historical accuracy or quality acceptance.",
        "images": rows,
    }
    (output_dir / "evaluation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "generation_prompt.txt").write_text(
        "当前配置的逐图提示词（用于下一次生成，不代表已有图片的生成记录）。\n"
        + json.dumps(prompt_set, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    document = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>伟大工程 · 图生图评估</title><style>
    :root{color-scheme:dark}*{box-sizing:border-box}body{background:#15171a;color:#e9e1d5;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif;margin:0;padding:24px}header{max-width:1600px;margin:auto}h1{font-size:28px;margin:0}h2{font-size:22px}small{font-size:14px;color:#dfb989}article{max-width:1600px;margin:28px auto;padding:20px;background:#202329;border:1px solid #393a3d;border-radius:10px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}figure{margin:0;background:#111315;text-align:center}img.full{width:100%;height:340px;object-fit:contain}img.crop{width:100%;aspect-ratio:27/11;object-fit:cover;object-position:center}figcaption{color:#cbbd9f;padding:6px;font-size:14px}.crop-row{margin-top:16px}.notes{font-size:14px;padding:8px}.metrics{font-size:13px;color:#a7b5c1}.pending{padding:60px 12px;color:#f0c38b}.controls{position:sticky;top:0;background:#15171aee;padding:10px 0;z-index:1}input,select{font:inherit;padding:8px;background:#252930;color:inherit;border:1px solid #777}button{font:inherit;padding:8px;cursor:pointer}article[hidden]{display:none}@media(max-width:900px){.grid{grid-template-columns:1fr}img.full{height:auto;max-height:450px}body{padding:12px}}
    </style><header><h1>伟大工程 · 源图 / 纯 AI / 图生图</h1>'''
    document += f'<p>本轮已生成 {generated_count}/{len(rows)}。点击图片查看原尺寸；横幅为 27:11 居中裁剪压力测试，正式游戏裁剪使用单独的人工配置。</p>'
    document += '<p>重点检查主体是否正确、建筑特征是否保留、现代元素是否仍在、绘画质感和缩略图可读性。结构相似度仅作诊断，不证明考据正确。源图的作者、拍摄年代和出处尚未核验。</p><div class="controls"><input id="search" placeholder="搜索工程名称"> <select id="state"><option value="">全部源图</option><option>适合风格化</option><option>需清理</option><option>需换源</option><option>待核验</option></select></div></header>'
    document += "\n".join(cards)
    document += '''<script>function filter(){let s=document.querySelector('#search').value.toLowerCase(),t=document.querySelector('#state').value;document.querySelectorAll('article').forEach(a=>a.hidden=!a.dataset.name.toLowerCase().includes(s)||(t&&a.dataset.state!==t));}document.querySelector('#search').addEventListener('input',filter);document.querySelector('#state').addEventListener('change',filter);</script></html>'''
    (output_dir / "index.html").write_text(document, encoding="utf-8")

    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    for start in range(0, len(rows), 5):
        group = rows[start:start + 5]
        width, height = 400, 320
        sheet = Image.new("RGB", (width * 4, 55 + height * len(group)), "#17191c")
        draw = ImageDraw.Draw(sheet)
        for col, title in enumerate(("参考源图", "原有纯 AI", "本轮图生图", "图生图 · 27:11")):
            draw.text((col * width + 12, 12), title, fill="#dabc88", font=font)
        for offset, row in enumerate(group):
            existing = row["source_review"].get("existing_ai")
            paths = [REPO_ROOT / row["source"], REPO_ROOT / existing if existing else None,
                     REPO_ROOT / row["planned_output"], REPO_ROOT / row["planned_output"]]
            y = 55 + offset * height
            for col, path in enumerate(paths):
                sheet.paste(panel(path, width - 10, height - 40, crop=col == 3), (col * width + 5, y))
            draw.text((12, y + height - 34), f'{row["index"]:02d} {row["name"]}', fill="#eee2d0", font=font)
        sheet.save(output_dir / f"comparison_{start // 5 + 1:02d}.jpg", quality=93)
    return {"generated": generated_count, "requested": len(rows), "review": relative(output_dir / "index.html")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REVIEW_DIR)
    parser.add_argument("--images-dir", type=Path, default=REPO_ROOT / "assets/historical/processed", help="Image batch to review, including a variant directory")
    args = parser.parse_args()
    config = json.loads((REPO_ROOT / "generate_dds_icon_config.json").read_text(encoding="utf-8"))
    review_path = REVIEW_DIR / "source_review.json"
    reviews = json.loads(review_path.read_text(encoding="utf-8"))
    if isinstance(reviews, dict):
        reviews = reviews["images"]
    print(json.dumps(write_review(config, reviews, args.output_dir.resolve(), images_dir=args.images_dir.resolve()), ensure_ascii=True))


if __name__ == "__main__":
    main()
