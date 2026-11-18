"""Build feed.xml and index.html for the players' podcast.
Run from the feed folder: python3 build_feed.py  (episodes/ holds the MP3s; only those present are listed)."""
import json, os, subprocess, html, datetime
BASE = "https://alevensailor.github.io/orzelbirg-podcast/"
TITLE = "The Barons of Orzelbirg"
SUB = "The players' podcast for the Irregulars: the barony's rules, lore and people, some of it read by the court itself."
eps = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "episodes.json")))
start = datetime.datetime(2026, 11, 17, 12, 0, tzinfo=datetime.timezone.utc)
items, rows = [], []
for e in eps:
    p = os.path.join("episodes", e["file"])
    if not os.path.exists(p):
        continue
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())
    size = os.path.getsize(p)
    # episode n is published n minutes after the start, so apps keep series order
    pub = (start + datetime.timedelta(minutes=e["n"])).strftime("%a, %d %b %Y %H:%M:%S +0000")
    url = BASE + "episodes/" + e["file"]
    t = f'{e["n"]}. {e["title"]}'
    d = f'{e["by"]}. {e["desc"]}'
    items.append(f"""  <item>
    <title>{html.escape(t)}</title>
    <description>{html.escape(d)}</description>
    <itunes:summary>{html.escape(d)}</itunes:summary>
    <enclosure url="{url}" length="{size}" type="audio/mpeg"/>
    <guid isPermaLink="false">orzelbirg-podcast-{e["n"]:02d}</guid>
    <pubDate>{pub}</pubDate>
    <itunes:duration>{int(round(dur))}</itunes:duration>
    <itunes:episode>{e["n"]}</itunes:episode>
    <itunes:episodeType>full</itunes:episodeType>
    <itunes:explicit>false</itunes:explicit>
  </item>""")
    rows.append(f"""<section id="ep{e["n"]}"><h2>{html.escape(t)}</h2><p class="by">{html.escape(e["by"])} · {int(dur//60)} min</p><p>{html.escape(e["desc"])}</p><audio controls preload="none" src="episodes/{e["file"]}"></audio></section>""")
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{TITLE}</title>
  <link>{BASE}</link>
  <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>
  <language>en</language>
  <description>{html.escape(SUB)}</description>
  <itunes:summary>{html.escape(SUB)}</itunes:summary>
  <itunes:author>The Irregulars</itunes:author>
  <itunes:type>serial</itunes:type>
  <itunes:explicit>false</itunes:explicit>
  <itunes:image href="{BASE}cover.jpg"/>
  <image><url>{BASE}cover.jpg</url><title>{TITLE}</title><link>{BASE}</link></image>
  <itunes:category text="Leisure"><itunes:category text="Games"/></itunes:category>
{chr(10).join(items)}
</channel>
</rss>
"""
open("feed.xml", "w").write(feed)
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>{TITLE}</title><link rel="alternate" type="application/rss+xml" href="feed.xml">
<style>body{{font:17px/1.55 Georgia,serif;max-width:680px;margin:2rem auto;padding:0 1rem;background:#16120e;color:#e9e1d3}}
h1{{font-size:2rem;margin:.2rem 0}}h2{{font-size:1.2rem;margin:0}}img{{width:160px;border-radius:6px;float:right;margin:0 0 1rem 1rem}}
section{{border-top:1px solid #3a3128;padding:1rem 0}}.by{{color:#b9a98f;font-style:italic;margin:.2rem 0}}audio{{width:100%}}
code{{background:#2a231c;padding:.15rem .4rem;border-radius:4px;word-break:break-all}}a{{color:#e2b866}}</style></head><body>
<img src="cover.jpg" alt=""><h1>{TITLE}</h1><p>{html.escape(SUB)}</p>
<p><b>Subscribe:</b> in your podcast app, choose "add by URL" (Pocket Casts, Overcast, Apple Podcasts: Library → Follow a Show by URL) and paste <code>{BASE}feed.xml</code></p>
{chr(10).join(rows)}
</body></html>
"""
open("index.html", "w").write(page)
print(len(items), "episodes")
