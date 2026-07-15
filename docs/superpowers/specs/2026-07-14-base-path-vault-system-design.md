# Base-Path Vault System — Design

**Date:** 2026-07-14
**Branch:** base-path-vault-system

## Problem

Vaults are currently registered with absolute paths typed by the user. This is
error-prone: typos and malformed paths silently create vaults in the wrong
place. Instead, the user should specify a single **base folder** where all
vaults live, and each vault is just a folder inside it addressed by name
(`base_path/vault-name`).

## Approach

`base_path` is the single source of truth. Each vault's full path is **derived**
at load time as `base_path / name` and held in memory; it is **not** stored in
`config.toml`. This keeps one authoritative location and lets downstream code
(`obsidian.py`) keep reading `vault.path` as the full directory path unchanged.

## Changes

### config.toml / config.example.toml

`[vaults]` gains a required `base_path`. Item entries store only `name` and
`tags` (no `path`):

```toml
[vaults]
base_path = "/Users/me/Obsidian"
default = "norwegian"
[[vaults.items]]
name = "norwegian"
tags = []
```

### fetch_settings.py

- `Settings` gains `base_vault_path: str`, loaded from
  `data["vaults"]["base_path"]`. Missing key → error at load (it is required).
- `load()`: config items no longer carry `path`. For each item, build the
  `Vault` and set its in-memory `.path = str(Path(base_path) / name)`.
- `create_vault(self, name)` — drops the `path` param. Computes
  `vault_path = Path(self.base_vault_path) / name`, `mkdir(parents=True,
  exist_ok=True)`, creates `Vault(name=name, path=str(vault_path))`, runs
  `search_tags`, appends, saves. Fixes the existing broken
  `Path.joinpath(path, name)` call.
- `add_vault(self, name)` — drops the `path` param. Same path derivation but
  **no** mkdir. Registers an existing vault folder under `base_path` so its
  existing notes/tags are picked up.
- `save()` — writes `base_path` under `[vaults]`; `items` entries contain only
  `name` and `tags` (drop `path`).
- `list_vaults()` — unchanged; returns `(name, path)` using the derived
  in-memory path.

### telegram_bot.py

The `create_vault` flow collapses from two steps to one. After the `vault_name`
substep, call `obsidian.settings.create_vault(name)` directly. Remove the
`vault_path` substep and its "give an absolute path" prompt.

## Distinction: create_vault vs add_vault

Both remain and both take only `name`:

- `create_vault(name)` — user is making a **new** vault; the folder is created.
- `add_vault(name)` — user has an **existing** vault (notes already present)
  and wants the bot to use it; the folder is registered, not created.

## Downstream (unchanged)

`obsidian.py` (`search_tags`, `create_note`) reads `vault.path` as the full
vault directory. Because `.path` is still populated in memory, no changes are
needed there.

## Edge cases

- `base_path` missing from config → error at load.
- The current `config.toml` contains a stale blank-name item and per-item
  `path` keys; the new `save()` drops `path` on next write. Clean up the blank
  entry manually.
