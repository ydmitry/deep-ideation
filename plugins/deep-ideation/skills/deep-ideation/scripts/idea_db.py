#!/usr/bin/env python3
"""
Idea Database — CSV-based idea tracking for deep-ideation skill.

Every idea is a row. Columns can be added dynamically for evaluation.
Built-in columns: id, name, description, source_agent, source_seed, chain, tag, phase

Usage:
    python idea_db.py init <workspace>                    # Create empty idea DB
    python idea_db.py add <workspace> --name "..." --description "..." --source_agent "..." [--source_seed "..."] [--chain "..."] [--tag SAFE|BOLD|WILD] [--phase seed|transform|build|tension|synthesis]
    python idea_db.py add_batch <workspace> <json_file>   # Add multiple ideas from JSON
    python idea_db.py add_column <workspace> <column_name> [--default ""]  # Add a new evaluation column
    python idea_db.py set <workspace> <id> <column> <value>               # Set a value for an idea
    python idea_db.py set_batch <workspace> <json_file>                   # Set multiple values from JSON
    python idea_db.py sort <workspace> <column> [--desc]                  # Sort by column (prints sorted)
    python idea_db.py filter <workspace> <column> <value>                 # Filter rows where column == value
    python idea_db.py filter_above <workspace> <column> <threshold>       # Filter rows where column > threshold (numeric)
    python idea_db.py top <workspace> <column> [--n 10]                   # Top N by column
    python idea_db.py stats <workspace>                                   # Summary stats
    python idea_db.py show <workspace> [--columns "name,tag,ice_score"]   # Show DB (optional column filter)
    python idea_db.py export_md <workspace> [--columns "..."] [--sort "..."] [--desc]  # Export as markdown table
    python idea_db.py describe <workspace>                   # Show current schema: columns, types, fill rates
    python idea_db.py size <workspace>                      # Row count + breakdown by phase
    python idea_db.py slice <workspace> --ids 1-50          # Get ideas by ID range (for parallel splits)
    python idea_db.py slice <workspace> --offset 0 --limit 50  # Get ideas by offset+limit
    python idea_db.py slice <workspace> --phase build --ids 60-80  # Filter by phase, then slice
    python idea_db.py compute_composite <workspace>                 # composite_score = total_score * stress_multiplier * brilliance_multiplier * favorites_multiplier
    python idea_db.py compute_zscores <workspace> [--source composite_score] [--target z_score]  # Z-scores across cohort
    python idea_db.py validate_evidence_refs <workspace> <json_file>   # Validate evidence_ref fields cite valid IDs (blocks write on failure)
    python idea_db.py scorer_drop_log <workspace> <json_file>          # Write scorer_drop_log.md with excluded ideas + reason codes
    python idea_db.py mark_favorites <workspace> --ids "1,3,7"     # Set user_favorites=true for given IDs (Phase 5.8)
"""

import argparse
import csv
import fcntl
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

DB_FILENAME = "ideas.csv"
LOCK_FILENAME = "ideas.csv.lock"
BUILT_IN_COLUMNS = ["id", "name", "description", "source_agent", "source_seed", "chain", "tag", "phase"]


def get_db_path(workspace):
    return os.path.join(workspace, DB_FILENAME)


def get_lock_path(workspace):
    return os.path.join(workspace, LOCK_FILENAME)


READ_ONLY_COMMANDS = frozenset({
    "describe", "size", "slice", "filter", "filter_above",
    "top", "stats", "show", "export_md", "unscored",
    "validate_evidence_refs",
})


@contextmanager
def locked_db(workspace, *, shared=False):
    """Acquire a file lock before reading/writing the CSV.
    Read-only commands use a shared lock (LOCK_SH) so they don't block each other.
    Write commands use an exclusive lock (LOCK_EX) so parallel agents don't corrupt the CSV."""
    lock_path = get_lock_path(workspace)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def read_db(workspace):
    db_path = get_db_path(workspace)
    if not os.path.exists(db_path):
        print(f"Error: No idea DB found at {db_path}. Run 'init' first.", file=sys.stderr)
        sys.exit(1)
    with open(db_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or BUILT_IN_COLUMNS
    return columns, rows


def write_db(workspace, columns, rows):
    db_path = get_db_path(workspace)
    with open(db_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows):
    if not rows:
        return 1
    return max(int(r.get("id", 0)) for r in rows) + 1


def cmd_init(args):
    db_path = get_db_path(args.workspace)
    os.makedirs(args.workspace, exist_ok=True)
    with open(db_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=BUILT_IN_COLUMNS)
        writer.writeheader()
    print(f"Initialized idea DB at {db_path}")
    print(f"Columns: {', '.join(BUILT_IN_COLUMNS)}")


def cmd_add(args):
    columns, rows = read_db(args.workspace)
    new_id = next_id(rows)
    row = {col: "" for col in columns}
    row["id"] = str(new_id)
    row["name"] = args.name
    row["description"] = args.description
    row["source_agent"] = args.source_agent or ""
    row["source_seed"] = args.source_seed or ""
    row["chain"] = args.chain or ""
    row["tag"] = args.tag or ""
    row["phase"] = args.phase or ""
    rows.append(row)
    write_db(args.workspace, columns, rows)
    print(f"Added idea #{new_id}: {args.name}")
    print(f"ID: {new_id}")


def cmd_add_batch(args):
    columns, rows = read_db(args.workspace)
    with open(args.json_file, "r") as f:
        ideas = json.load(f)

    added = 0
    for idea in ideas:
        new_id = next_id(rows)
        row = {col: "" for col in columns}
        row["id"] = str(new_id)
        for key, value in idea.items():
            if key in columns:
                row[key] = str(value)
        rows.append(row)
        added += 1

    write_db(args.workspace, columns, rows)
    added_ids = [rows[-(added - i)]["id"] for i in range(added)]
    print(f"Added {added} ideas")
    print(f"IDs: {','.join(added_ids)}")


def cmd_add_column(args):
    columns, rows = read_db(args.workspace)
    if args.column_name in columns:
        print(f"Column '{args.column_name}' already exists.")
        return
    columns.append(args.column_name)
    default = args.default or ""
    for row in rows:
        row[args.column_name] = default
    write_db(args.workspace, columns, rows)
    print(f"Added column '{args.column_name}' (default: '{default}')")
    print(f"All columns: {', '.join(columns)}")


def cmd_set(args):
    columns, rows = read_db(args.workspace)
    if args.column not in columns:
        print(f"Error: Column '{args.column}' does not exist. Use 'add_column' first.", file=sys.stderr)
        sys.exit(1)
    found = False
    for row in rows:
        if row["id"] == str(args.id):
            row[args.column] = args.value
            found = True
            break
    if not found:
        print(f"Error: Idea #{args.id} not found.", file=sys.stderr)
        sys.exit(1)
    write_db(args.workspace, columns, rows)
    print(f"Set idea #{args.id} [{args.column}] = {args.value}")


def cmd_set_batch(args):
    columns, rows = read_db(args.workspace)
    with open(args.json_file, "r") as f:
        updates = json.load(f)

    id_map = {row["id"]: row for row in rows}
    updated = 0
    for update in updates:
        idea_id = str(update.get("id"))
        if idea_id not in id_map:
            print(f"Warning: Idea #{idea_id} not found, skipping.", file=sys.stderr)
            continue
        for key, value in update.items():
            if key == "id":
                continue
            if key not in columns:
                print(f"Warning: Column '{key}' does not exist, skipping.", file=sys.stderr)
                continue
            id_map[idea_id][key] = str(value)
        updated += 1

    write_db(args.workspace, columns, rows)
    print(f"Updated {updated} ideas")


def cmd_sort(args):
    columns, rows = read_db(args.workspace)
    if args.column not in columns:
        print(f"Error: Column '{args.column}' does not exist.", file=sys.stderr)
        sys.exit(1)

    def sort_key(row):
        val = row.get(args.column, "")
        try:
            return (0, float(val))
        except (ValueError, TypeError):
            if val == "":
                return (1, 0)  # Empty values sort last
            return (0, val)

    rows.sort(key=sort_key, reverse=args.desc)
    write_db(args.workspace, columns, rows)

    # Print sorted
    print(f"Sorted by '{args.column}' ({'desc' if args.desc else 'asc'}):")
    for row in rows:
        print(f"  #{row['id']} [{row.get(args.column, '')}] {row['name']}")


def cmd_filter(args):
    columns, rows = read_db(args.workspace)
    if args.column not in columns:
        print(f"Error: Column '{args.column}' does not exist.", file=sys.stderr)
        sys.exit(1)
    filtered = [r for r in rows if r.get(args.column, "") == args.value]
    print(f"Found {len(filtered)} ideas where {args.column} == '{args.value}':")
    for row in filtered:
        print(f"  #{row['id']} {row['name']} — {row['description'][:80]}")


def cmd_filter_above(args):
    columns, rows = read_db(args.workspace)
    if args.column not in columns:
        print(f"Error: Column '{args.column}' does not exist.", file=sys.stderr)
        sys.exit(1)
    threshold = float(args.threshold)
    filtered = []
    for r in rows:
        try:
            if float(r.get(args.column, 0)) > threshold:
                filtered.append(r)
        except (ValueError, TypeError):
            pass
    print(f"Found {len(filtered)} ideas where {args.column} > {threshold}:")
    for row in filtered:
        print(f"  #{row['id']} [{row.get(args.column, '')}] {row['name']}")


def cmd_top(args):
    columns, rows = read_db(args.workspace)
    if args.column not in columns:
        print(f"Error: Column '{args.column}' does not exist.", file=sys.stderr)
        sys.exit(1)

    scored = []
    for r in rows:
        try:
            scored.append((float(r.get(args.column, 0)), r))
        except (ValueError, TypeError):
            pass

    scored.sort(key=lambda x: x[0], reverse=True)
    n = args.n or 10
    print(f"Top {min(n, len(scored))} by '{args.column}':")
    for i, (score, row) in enumerate(scored[:n]):
        print(f"  {i+1}. #{row['id']} [{score}] {row['name']} — {row['description'][:60]}")


def cmd_stats(args):
    columns, rows = read_db(args.workspace)
    print(f"Idea Database Stats:")
    print(f"  Total ideas: {len(rows)}")
    print(f"  Columns: {', '.join(columns)}")

    # Count by phase
    phases = {}
    for r in rows:
        p = r.get("phase", "unknown")
        phases[p] = phases.get(p, 0) + 1
    if phases:
        print(f"  By phase: {', '.join(f'{k}={v}' for k, v in sorted(phases.items()))}")

    # Count by tag
    tags = {}
    for r in rows:
        t = r.get("tag", "unknown")
        tags[t] = tags.get(t, 0) + 1
    if tags:
        print(f"  By tag: {', '.join(f'{k}={v}' for k, v in sorted(tags.items()))}")

    # Count by source_agent
    agents = {}
    for r in rows:
        a = r.get("source_agent", "unknown")
        agents[a] = agents.get(a, 0) + 1
    if agents:
        print(f"  By agent: {', '.join(f'{k}={v}' for k, v in sorted(agents.items()))}")

    # Numeric column stats
    for col in columns:
        if col in BUILT_IN_COLUMNS:
            continue
        vals = []
        for r in rows:
            try:
                vals.append(float(r.get(col, "")))
            except (ValueError, TypeError):
                pass
        if vals:
            avg = sum(vals) / len(vals)
            print(f"  {col}: min={min(vals)}, max={max(vals)}, avg={avg:.1f}, scored={len(vals)}/{len(rows)}")


def cmd_show(args):
    columns, rows = read_db(args.workspace)
    if args.columns:
        show_cols = [c.strip() for c in args.columns.split(",")]
        show_cols = [c for c in show_cols if c in columns]
    else:
        show_cols = columns

    # Print header
    header = " | ".join(show_cols)
    print(header)
    print("-" * len(header))
    for row in rows:
        vals = [str(row.get(c, ""))[:40] for c in show_cols]
        print(" | ".join(vals))


def cmd_add_criteria(args):
    """Add multiple evaluation criteria columns at once."""
    columns, rows = read_db(args.workspace)
    criteria = [c.strip() for c in args.criteria.split(",")]
    added = []
    for criterion in criteria:
        if criterion not in columns:
            columns.append(criterion)
            for row in rows:
                row[criterion] = ""
            added.append(criterion)
    # Also add a composite score column if requested
    if args.composite:
        composite_name = args.composite
        if composite_name not in columns:
            columns.append(composite_name)
            for row in rows:
                row[composite_name] = ""
            added.append(composite_name)
    write_db(args.workspace, columns, rows)
    print(f"Added criteria columns: {', '.join(added)}")
    print(f"All columns: {', '.join(columns)}")
    if args.composite:
        print(f"Composite score column: {args.composite}")
        print(f"Use 'compute' command to calculate composite from criteria.")


def cmd_compute(args):
    """Compute a composite score from multiple criteria columns."""
    columns, rows = read_db(args.workspace)
    criteria = [c.strip() for c in args.criteria.split(",")]
    target = args.target

    # Validate
    for c in criteria:
        if c not in columns:
            print(f"Error: Column '{c}' does not exist.", file=sys.stderr)
            sys.exit(1)
    if target not in columns:
        columns.append(target)
        for row in rows:
            row[target] = ""

    # Parse weights if provided
    weights = {}
    if args.weights:
        pairs = args.weights.split(",")
        for pair in pairs:
            col, w = pair.strip().split(":")
            weights[col.strip()] = float(w.strip())
    else:
        weights = {c: 1.0 for c in criteria}

    computed = 0
    for row in rows:
        vals = {}
        skip = False
        for c in criteria:
            try:
                vals[c] = float(row.get(c, ""))
            except (ValueError, TypeError):
                skip = True
                break
        if skip:
            continue

        if args.formula == "weighted_avg":
            total_weight = sum(weights.get(c, 1.0) for c in criteria)
            score = sum(vals[c] * weights.get(c, 1.0) for c in criteria) / total_weight
        elif args.formula == "sum":
            score = sum(vals[c] * weights.get(c, 1.0) for c in criteria)
        elif args.formula == "product":
            score = 1
            for c in criteria:
                score *= vals[c] ** weights.get(c, 1.0)
        elif args.formula == "ice":
            # Expects exactly: impact, confidence, ease
            if len(criteria) == 3:
                i, c_val, e = [vals[c] for c in criteria]
                score = (i * c_val) / (11 - e) if (11 - e) != 0 else 0
            else:
                score = sum(vals[c] for c in criteria) / len(criteria)
        else:
            score = sum(vals[c] for c in criteria) / len(criteria)

        row[target] = f"{score:.1f}"
        computed += 1

    write_db(args.workspace, columns, rows)
    print(f"Computed '{target}' for {computed}/{len(rows)} ideas using {args.formula}")


def cmd_multi_filter(args):
    """Filter ideas matching ALL conditions (column>threshold pairs)."""
    columns, rows = read_db(args.workspace)
    conditions = args.conditions.split(",")
    filtered = list(rows)

    for cond in conditions:
        cond = cond.strip()
        # Parse operator
        for op in [">=", "<=", ">", "<", "="]:
            if op in cond:
                col, val = cond.split(op, 1)
                col = col.strip()
                val = val.strip()
                if col not in columns:
                    print(f"Warning: Column '{col}' not found, skipping.", file=sys.stderr)
                    break
                new_filtered = []
                for row in filtered:
                    row_val = row.get(col, "")
                    try:
                        rv = float(row_val)
                        fv = float(val)
                        if op == ">" and rv > fv: new_filtered.append(row)
                        elif op == ">=" and rv >= fv: new_filtered.append(row)
                        elif op == "<" and rv < fv: new_filtered.append(row)
                        elif op == "<=" and rv <= fv: new_filtered.append(row)
                        elif op == "=" and row_val == val: new_filtered.append(row)
                    except (ValueError, TypeError):
                        if op == "=" and row_val == val:
                            new_filtered.append(row)
                filtered = new_filtered
                break

    print(f"Found {len(filtered)} ideas matching all conditions:")
    for row in filtered:
        scores = " | ".join(f"{c}={row.get(c, '')}" for c in columns if c not in BUILT_IN_COLUMNS and row.get(c, ""))
        print(f"  #{row['id']} {row['name']} [{scores}]")


def cmd_describe(args):
    """Describe the current CSV schema: columns in order, types, fill rates, and which phase added them."""
    columns, rows = read_db(args.workspace)
    total = len(rows)

    print(f"## ideas.csv schema — {total} ideas\n")
    print(f"| # | Column | Type | Filled | Empty | Example |")
    print(f"|---|--------|------|--------|-------|---------|")

    for i, col in enumerate(columns, 1):
        filled = 0
        empty = 0
        example = ""
        is_numeric = True
        for r in rows:
            val = r.get(col, "").strip()
            if val:
                filled += 1
                if not example:
                    example = val[:50]
                try:
                    float(val)
                except (ValueError, TypeError):
                    is_numeric = False
            else:
                empty += 1

        if total == 0:
            col_type = "builtin" if col in BUILT_IN_COLUMNS else "added"
        elif col in BUILT_IN_COLUMNS:
            col_type = "builtin"
        elif is_numeric and filled > 0:
            col_type = "numeric"
        else:
            col_type = "text"

        fill_pct = f"{filled}/{total}" if total > 0 else "0/0"
        example_display = example.replace("|", "\\|") if example else "—"
        print(f"| {i} | {col} | {col_type} | {fill_pct} | {empty} | {example_display} |")

    # Show columns grouped by likely phase origin
    added_cols = [c for c in columns if c not in BUILT_IN_COLUMNS]
    if added_cols:
        print(f"\n## Dynamic columns ({len(added_cols)}):")
        for col in added_cols:
            print(f"  - {col}")


def cmd_size(args):
    """Print the number of rows in the DB. Useful for parallel agents to check state."""
    columns, rows = read_db(args.workspace)
    total = len(rows)
    print(f"SIZE: {total}")
    # Also show breakdown by phase if rows exist
    if rows:
        phases = {}
        for r in rows:
            p = r.get("phase", "")
            if p:
                phases[p] = phases.get(p, 0) + 1
        if phases:
            print(f"BY_PHASE: {','.join(f'{k}={v}' for k, v in sorted(phases.items()))}")


def cmd_slice(args):
    """Return a subset of ideas by ID range or offset+limit. For splitting work across parallel agents.

    Usage:
        idea_db.py slice <workspace> --ids 1-50        # IDs 1 through 50
        idea_db.py slice <workspace> --ids 51-100      # IDs 51 through 100
        idea_db.py slice <workspace> --offset 0 --limit 50   # first 50 rows
        idea_db.py slice <workspace> --offset 50 --limit 50  # next 50 rows
        idea_db.py slice <workspace> --phase seed      # filter by phase, then slice
        idea_db.py slice <workspace> --phase build --ids 60-80
    """
    columns, rows = read_db(args.workspace)

    # Optional phase filter first
    if args.phase:
        rows = [r for r in rows if r.get("phase", "") == args.phase]

    # Slice by ID range or offset+limit
    if args.ids:
        parts = args.ids.split("-")
        id_start = int(parts[0])
        id_end = int(parts[1]) if len(parts) > 1 else id_start
        sliced = [r for r in rows if id_start <= int(r.get("id", 0)) <= id_end]
    else:
        offset = args.offset or 0
        limit = args.limit or len(rows)
        sliced = rows[offset:offset + limit]

    if not sliced and args.ids:
        all_ids = [int(r.get("id", 0)) for r in rows]
        max_id = max(all_ids) if all_ids else 0
        print(f"WARNING: No ideas found in range {args.ids}. "
              f"Available IDs: 1-{max_id} ({len(rows)} ideas after filters).", file=sys.stderr)

    ids = [r["id"] for r in sliced]
    print(f"SLICE: {len(sliced)} ideas")
    print(f"IDS: {','.join(ids)}")
    for row in sliced:
        scores = " | ".join(f"{c}={row.get(c, '')}" for c in columns if c not in BUILT_IN_COLUMNS and row.get(c, ""))
        print(f"  #{row['id']} {row['name']} [{scores}]" if scores else f"  #{row['id']} {row['name']}")


def cmd_unscored(args):
    """Show ideas that haven't been scored on a given column."""
    columns, rows = read_db(args.workspace)
    if args.column not in columns:
        print(f"Error: Column '{args.column}' does not exist.", file=sys.stderr)
        sys.exit(1)
    unscored = [r for r in rows if r.get(args.column, "").strip() == ""]
    print(f"Found {len(unscored)} unscored ideas for '{args.column}':")
    for row in unscored:
        print(f"  #{row['id']} {row['name']} (phase: {row.get('phase', '?')}, agent: {row.get('source_agent', '?')})")


FAVORITES_BOOST = 1.10  # Phase 5.8 Taste Check gives favorites +10% on the composite


def cmd_mark_favorites(args):
    """Mark specific ideas as user favorites (Phase 5.8 Taste Check).

    Ensures user_favorites and favorites_multiplier columns exist, then:
    - sets user_favorites="true" for each idea ID in the provided list
    - sets favorites_multiplier=FAVORITES_BOOST (1.10) for the same rows
      so that Phase 8.5 compute_composite mechanically applies the +10%
      bounded boost via the standard multiplier chain

    Usage:
        idea_db.py mark_favorites <workspace> --ids "1,3,7"
    """
    columns, rows = read_db(args.workspace)

    # Ensure both columns exist (idempotent)
    if "user_favorites" not in columns:
        columns.append("user_favorites")
        for row in rows:
            row["user_favorites"] = ""
    if "favorites_multiplier" not in columns:
        columns.append("favorites_multiplier")
        for row in rows:
            row["favorites_multiplier"] = "1.0"

    ids_to_mark = {s.strip() for s in args.ids.split(",") if s.strip()}
    if not ids_to_mark:
        print("Warning: no IDs provided (--ids was empty).", file=sys.stderr)
        return

    id_map = {row["id"]: row for row in rows}

    marked = []
    missing = []
    for idea_id in ids_to_mark:
        if idea_id in id_map:
            id_map[idea_id]["user_favorites"] = "true"
            id_map[idea_id]["favorites_multiplier"] = f"{FAVORITES_BOOST}"
            marked.append(idea_id)
        else:
            missing.append(idea_id)

    write_db(args.workspace, columns, rows)
    sorted_marked = ', '.join(f'#{i}' for i in sorted(marked, key=int))
    print(f"Marked {len(marked)} ideas as favorites (+{int((FAVORITES_BOOST - 1) * 100)}% composite boost): {sorted_marked}")
    if missing:
        print(f"Warning: IDs not found: {', '.join(missing)}", file=sys.stderr)


def cmd_compute_composite(args):
    """Compute composite_score = total_score * stress_multiplier * brilliance_multiplier * favorites_multiplier.

    Missing multiplier columns default to 1.0. Ensures composite_score column exists.

    The favorites_multiplier is populated by Phase 5.8 (Taste Check) via the
    mark_favorites command; it is 1.10 for user-picked ideas and 1.0 otherwise.
    This gives favorites a bounded +10% boost without letting them override
    strong non-favorites on the underlying criteria.
    """
    columns, rows = read_db(args.workspace)

    if "composite_score" not in columns:
        columns.append("composite_score")
        for row in rows:
            row["composite_score"] = ""

    computed = 0
    for row in rows:
        raw_total = row.get("total_score", "").strip()
        if not raw_total:
            continue
        try:
            total = float(raw_total)
        except (ValueError, TypeError):
            continue

        try:
            stress_mult = float(row.get("stress_multiplier", "").strip() or 1.0)
        except (ValueError, TypeError):
            stress_mult = 1.0

        try:
            brilliance_mult = float(row.get("brilliance_multiplier", "").strip() or 1.0)
        except (ValueError, TypeError):
            brilliance_mult = 1.0

        try:
            favorites_mult = float(row.get("favorites_multiplier", "").strip() or 1.0)
        except (ValueError, TypeError):
            favorites_mult = 1.0

        row["composite_score"] = f"{total * stress_mult * brilliance_mult * favorites_mult:.3f}"
        computed += 1

    write_db(args.workspace, columns, rows)
    print(f"Computed composite_score for {computed}/{len(rows)} ideas")
    print("Formula: total_score * stress_multiplier * brilliance_multiplier * favorites_multiplier")
    print("(missing multipliers default to 1.0)")


def cmd_compute_zscores(args):
    """Compute Z-scores for a given column across the scored cohort.

    Usage:
        idea_db.py compute_zscores <workspace> --source composite_score --target z_score
    """
    import math

    columns, rows = read_db(args.workspace)
    source = args.source
    target = args.target or "z_score"

    if source not in columns:
        print(f"Error: Source column '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if target not in columns:
        columns.append(target)
        for row in rows:
            row[target] = ""

    values = []
    for row in rows:
        try:
            values.append(float(row.get(source, "").strip()))
        except (ValueError, TypeError):
            pass

    if len(values) < 2:
        print(f"Error: Need at least 2 scored ideas to compute Z-scores (found {len(values)}).",
              file=sys.stderr)
        sys.exit(1)

    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)

    if std == 0:
        print("Warning: All values are identical — Z-scores will be 0.000 for all.", file=sys.stderr)

    computed = 0
    for row in rows:
        try:
            val = float(row.get(source, "").strip())
            row[target] = f"{(val - mean) / std:.3f}" if std > 0 else "0.000"
            computed += 1
        except (ValueError, TypeError):
            pass

    write_db(args.workspace, columns, rows)
    print(f"Computed Z-scores for {computed}/{len(rows)} ideas")
    print(f"Source: '{source}', Target: '{target}'")
    print(f"Cohort: mean={mean:.3f}, std={std:.3f}")


def cmd_validate_evidence_refs(args):
    """Validate that evidence_ref fields in a batch JSON cite valid idea IDs.

    Usage:
        idea_db.py validate_evidence_refs <workspace> <json_file>

    Checks that any '#N' patterns in evidence_ref fields reference existing idea IDs.
    Exits non-zero if any refs are missing or invalid — blocks the subsequent write.
    """
    import re

    columns, rows = read_db(args.workspace)
    valid_ids = {row["id"] for row in rows}

    with open(args.json_file, "r") as f:
        batch = json.load(f)

    errors = []
    for entry in batch:
        idea_id = str(entry.get("id", "?"))
        evidence = str(entry.get("evidence_ref", "")).strip()
        if not evidence:
            errors.append(f"  Idea #{idea_id}: evidence_ref is empty or missing")
            continue
        for ref in re.findall(r'#(\d+)', evidence):
            if ref not in valid_ids:
                errors.append(f"  Idea #{idea_id}: evidence_ref cites #'{ref}' which does not exist in DB")

    if errors:
        print(f"EVIDENCE REF VALIDATION FAILED — {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        print("\nFix evidence_ref fields before running set_batch.", file=sys.stderr)
        sys.exit(1)

    filled = sum(1 for e in batch if str(e.get("evidence_ref", "")).strip())
    print(f"Evidence refs OK: {filled}/{len(batch)} ideas have refs, all cited IDs exist.")


def cmd_scorer_drop_log(args):
    """Write scorer_drop_log.md listing cohort ideas excluded from scoring with reason codes.

    Usage:
        idea_db.py scorer_drop_log <workspace> <json_file>

    JSON format:
        [{"id": 1, "reason": "phase_excluded|low_quality|duplicate|no_description|other"}]

    Reason codes:
        phase_excluded  — phase not in scorer cohort
        low_quality     — insufficient description to score reliably
        duplicate       — near-duplicate of another scored idea
        no_description  — description field is empty
        other           — reason noted in optional "note" field
    """
    columns, rows = read_db(args.workspace)
    id_map = {row["id"]: row for row in rows}

    with open(args.json_file, "r") as f:
        drops = json.load(f)

    reason_labels = {
        "phase_excluded": "Phase not in scorer cohort",
        "low_quality": "Insufficient description to score",
        "duplicate": "Near-duplicate of another idea",
        "no_description": "Missing description",
        "other": "Other",
    }

    log_path = os.path.join(args.workspace, "scorer_drop_log.md")
    lines = [
        "# Scorer Drop Log\n",
        "Ideas from the expanded cohort excluded from scoring.\n",
        f"Total excluded: {len(drops)}\n",
        "",
        "| ID | Idea | Phase | Reason | Code |",
        "|-----|------|-------|--------|------|",
    ]

    for drop in drops:
        idea_id = str(drop.get("id", "?"))
        row = id_map.get(idea_id, {})
        name = drop.get("name", row.get("name", "Unknown"))
        phase = row.get("phase", "?")
        code = drop.get("reason", "other")
        note = drop.get("note", "")
        label = reason_labels.get(code, code)
        if note:
            label = f"{label} — {note}"
        lines.append(f"| #{idea_id} | {name} | {phase} | {label} | `{code}` |")

    with open(log_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote scorer_drop_log.md: {len(drops)} excluded ideas → {log_path}")


def cmd_export_md(args):
    columns, rows = read_db(args.workspace)
    if args.columns:
        show_cols = [c.strip() for c in args.columns.split(",")]
        show_cols = [c for c in show_cols if c in columns]
    else:
        show_cols = columns

    if args.sort and args.sort in columns:
        def sort_key(row):
            val = row.get(args.sort, "")
            try:
                return float(val)
            except (ValueError, TypeError):
                return val
        rows = sorted(rows, key=sort_key, reverse=args.desc)

    # Markdown table
    print("| " + " | ".join(show_cols) + " |")
    print("| " + " | ".join(["---"] * len(show_cols)) + " |")
    for row in rows:
        vals = [str(row.get(c, "")).replace("|", "\\|") for c in show_cols]
        print("| " + " | ".join(vals) + " |")


def main():
    parser = argparse.ArgumentParser(description="Idea Database for deep-ideation")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # init
    p = subparsers.add_parser("init")
    p.add_argument("workspace")

    # add
    p = subparsers.add_parser("add")
    p.add_argument("workspace")
    p.add_argument("--name", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--source_agent", default="")
    p.add_argument("--source_seed", default="")
    p.add_argument("--chain", default="")
    p.add_argument("--tag", default="")
    p.add_argument("--phase", default="")

    # add_batch
    p = subparsers.add_parser("add_batch")
    p.add_argument("workspace")
    p.add_argument("json_file")

    # add_column
    p = subparsers.add_parser("add_column")
    p.add_argument("workspace")
    p.add_argument("column_name")
    p.add_argument("--default", default="")

    # set
    p = subparsers.add_parser("set")
    p.add_argument("workspace")
    p.add_argument("id", type=int)
    p.add_argument("column")
    p.add_argument("value")

    # set_batch
    p = subparsers.add_parser("set_batch")
    p.add_argument("workspace")
    p.add_argument("json_file")

    # sort
    p = subparsers.add_parser("sort")
    p.add_argument("workspace")
    p.add_argument("column")
    p.add_argument("--desc", action="store_true")

    # filter
    p = subparsers.add_parser("filter")
    p.add_argument("workspace")
    p.add_argument("column")
    p.add_argument("value")

    # filter_above
    p = subparsers.add_parser("filter_above")
    p.add_argument("workspace")
    p.add_argument("column")
    p.add_argument("threshold")

    # top
    p = subparsers.add_parser("top")
    p.add_argument("workspace")
    p.add_argument("column")
    p.add_argument("--n", type=int, default=10)

    # stats
    p = subparsers.add_parser("stats")
    p.add_argument("workspace")

    # show
    p = subparsers.add_parser("show")
    p.add_argument("workspace")
    p.add_argument("--columns", default="")

    # export_md
    p = subparsers.add_parser("export_md")
    p.add_argument("workspace")
    p.add_argument("--columns", default="")
    p.add_argument("--sort", default="")
    p.add_argument("--desc", action="store_true")

    # add_criteria
    p = subparsers.add_parser("add_criteria")
    p.add_argument("workspace")
    p.add_argument("--criteria", required=True, help="Comma-separated list of criteria columns to add")
    p.add_argument("--composite", default="", help="Name of composite score column to create")

    # compute
    p = subparsers.add_parser("compute")
    p.add_argument("workspace")
    p.add_argument("--criteria", required=True, help="Comma-separated criteria columns to compute from")
    p.add_argument("--target", required=True, help="Target column to write computed score to")
    p.add_argument("--formula", default="weighted_avg", choices=["weighted_avg", "sum", "product", "ice"],
                   help="Formula: weighted_avg, sum, product, ice")
    p.add_argument("--weights", default="", help="Optional weights as col1:w1,col2:w2,...")

    # multi_filter
    p = subparsers.add_parser("multi_filter")
    p.add_argument("workspace")
    p.add_argument("--conditions", required=True, help="Comma-separated conditions: 'col>val,col2<=val2,col3=val3'")

    # size
    p = subparsers.add_parser("size")
    p.add_argument("workspace")

    # slice
    p = subparsers.add_parser("slice")
    p.add_argument("workspace")
    p.add_argument("--ids", default="", help="ID range: '1-50' or '51-100'")
    p.add_argument("--offset", type=int, default=0, help="Row offset (0-based)")
    p.add_argument("--limit", type=int, default=0, help="Max rows to return")
    p.add_argument("--phase", default="", help="Filter by phase before slicing")

    # describe
    p = subparsers.add_parser("describe")
    p.add_argument("workspace")

    # unscored
    p = subparsers.add_parser("unscored")
    p.add_argument("workspace")
    p.add_argument("column")

    # compute_composite
    p = subparsers.add_parser("compute_composite",
        help="Compute composite_score = total_score * stress_multiplier * brilliance_multiplier * favorites_multiplier")
    p.add_argument("workspace")

    # compute_zscores
    p = subparsers.add_parser("compute_zscores",
        help="Compute Z-scores for a column across the scored cohort")
    p.add_argument("workspace")
    p.add_argument("--source", default="composite_score", help="Source column (default: composite_score)")
    p.add_argument("--target", default="z_score", help="Target column (default: z_score)")

    # validate_evidence_refs
    p = subparsers.add_parser("validate_evidence_refs",
        help="Validate that evidence_ref fields in a batch JSON cite valid idea IDs")
    p.add_argument("workspace")
    p.add_argument("json_file")

    # scorer_drop_log
    p = subparsers.add_parser("scorer_drop_log",
        help="Write scorer_drop_log.md listing excluded cohort ideas with reason codes")
    p.add_argument("workspace")
    p.add_argument("json_file")

    # mark_favorites
    p = subparsers.add_parser("mark_favorites",
        help="Mark ideas as user favorites (Phase 5.8 Taste Check)")
    p.add_argument("workspace")
    p.add_argument("--ids", required=True, help="Comma-separated idea IDs to mark as favorites, e.g. '1,3,7'")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init, "add": cmd_add, "add_batch": cmd_add_batch,
        "add_column": cmd_add_column, "set": cmd_set, "set_batch": cmd_set_batch,
        "sort": cmd_sort, "filter": cmd_filter, "filter_above": cmd_filter_above,
        "top": cmd_top, "stats": cmd_stats, "show": cmd_show, "export_md": cmd_export_md,
        "add_criteria": cmd_add_criteria, "compute": cmd_compute,
        "multi_filter": cmd_multi_filter, "size": cmd_size, "slice": cmd_slice,
        "describe": cmd_describe, "unscored": cmd_unscored,
        "compute_composite": cmd_compute_composite,
        "compute_zscores": cmd_compute_zscores,
        "validate_evidence_refs": cmd_validate_evidence_refs,
        "scorer_drop_log": cmd_scorer_drop_log,
        "mark_favorites": cmd_mark_favorites,
    }

    # All commands except init acquire a file lock so parallel agents
    # (e.g. multiple Johns in Phase 5) don't corrupt the CSV.
    # Read-only commands use a shared lock; write commands use exclusive.
    if args.command == "init":
        commands[args.command](args)
    else:
        shared = args.command in READ_ONLY_COMMANDS
        with locked_db(args.workspace, shared=shared):
            commands[args.command](args)


if __name__ == "__main__":
    main()
