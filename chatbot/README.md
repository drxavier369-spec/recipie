# 🚀 NOVA STRIKE

A fast, arcade-style space shooter with boss loot, rarity-tiered gear, and endless escalating stages — built as a single self-contained HTML5 file (no engine, no build step, no dependencies to install).

**▶ Play now:** https://raw.githack.com/drxavier369-spec/recipie/play/index.html

---

## How to run it

It's **one file**. Any of these work:

- **Locally:** double-click `spaceshooter.html` (or `index.html`) — it opens in any browser.
- **Host it:** upload that single file to itch.io, Netlify, GitHub Pages, your own server, or submit to **Poki**.
- **Edit it:** open the `.html` in any text editor — all the code (game logic, art, sound, UI) is inside.

No Node, no npm, no compiler required to play. (`server.js` is only a tiny optional local web server for testing.)

## Controls

| | Desktop | Mobile |
|---|---|---|
| Move | Arrow keys / WASD | Drag anywhere |
| Fire | Spacebar | Auto-fires |
| Pause | `Esc` / `P` | Pause button |

## Features

- **Loadout that matters** — 5 weapons (Twin, Spread, Railgun, Plasma, Homing), equipment (shields, engine, repair, magnet, cosmic core), and companion drones. Power-ups *enhance* your equipped weapon.
- **7 rarities** — Common → Uncommon → Rare → Epic → Legendary → Mythical → **Cosmic** (animated).
- **Boss loot** — bosses drop collectible, rarity-rolled gear with a pickup celebration.
- **Upgrades & currency** — level items 1→5 with credits/cores.
- **Bosses & mini-bosses** — 3 redesigned capital ships (Dreadnought, War Carrier, Void Nexus) with attack patterns + enrage phases, every 5/10 stages.
- **Decimal stage progression** (1.1 → 1.9 → 2.0 …) with designed enemy waves (divers, strafers, V-formations).
- **Meta** — animated home hub, inventory, ship skins, profile, badges, top-100 leaderboard, daily reward + challenge.
- **Polish** — rewarded-ad revive, pause/mute/tutorial, animated space backdrop, cinematic boss deaths, layered synthwave music.
- **Poki-ready** — Poki SDK integrated (loading, gameplay events, ad breaks, rewarded revive).

## Tech

- **Rendering:** HTML5 Canvas 2D (all art drawn procedurally — no image assets)
- **Audio:** Web Audio API (all music + SFX synthesized live — no audio files)
- **Loop:** `requestAnimationFrame` with delta-time
- **Save:** `localStorage` (inventory, currency, leaderboard, settings)
- **Only external script:** Poki SDK (free, ads only, loads on Poki)

## Ownership

NOVA STRIKE is original work — no game engine, no third-party art, no third-party audio, no paid libraries. The author holds full copyright. See `LICENSE`.

## Files

- `spaceshooter.html` / `index.html` — the complete game (identical copies)
- `server.js` — optional local static server for testing (`node server.js` → http://localhost:3777)
- `LICENSE` — copyright

---

🤖 Built with [Claude Code](https://claude.com/claude-code)
