#!/usr/bin/env python3
"""
Idea Database — CSV-based idea tracking for deep-ideation skill.

Every idea is a row. Columns can be added dynamically for evaluation.
Built-in columns: id, name, description, source_agent, source_seed, chain, tag, phase, created_at

Usage:
    python idea_db.py init <workspace>                    # Create empty idea DB
    python idea_db.py add <workspace> --name "..." --description "..." --source_agent "..." [--source_seed "..."] [--chain "..."] [--tag SAFE|BOLD|WILD] [--phase seed|transform|build|tension|synthesis]  # created_at auto-set to UTC now
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
    python idea_db.py comment_add <workspace> <idea_id> --author "name" --author-type human|agent --text "..." [--parent <comment_id>]
    python idea_db.py comment_list <workspace> [--idea-id <id>] [--author-type human|agent]
    python idea_db.py comment_show <workspace> <idea_id>           # Full comment thread for one idea
"""

import argparse
import csv
import json
import os
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl

    def _acquire_lock(lock_fd, shared):
        fcntl.flock(lock_fd, fcntl.LOCK_SH if shared else fcntl.LOCK_EX)

    def _release_lock(lock_fd):
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
except ImportError:
    import msvcrt

    def _acquire_lock(lock_fd, shared):
        lock_fd.seek(0)
        while True:
            try:
                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                time.sleep(0.05)

    def _release_lock(lock_fd):
        try:
            lock_fd.seek(0)
            msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass

DB_FILENAME = "ideas.csv"
LOCK_FILENAME = "ideas.csv.lock"
BUILT_IN_COLUMNS = ["id", "name", "description", "source_agent", "source_seed", "chain", "tag", "phase", "created_at"]

COMMENTS_FILENAME = "comments.csv"
COMMENTS_LOCK_FILENAME = "comments.csv.lock"
COMMENTS_COLUMNS = ["id", "idea_id", "author", "author_type", "ts", "text", "parent_comment_id"]


def get_db_path(workspace):
    return os.path.join(workspace, DB_FILENAME)


def get_lock_path(workspace):
    return os.path.join(workspace, LOCK_FILENAME)


def get_comments_path(workspace):
    return os.path.join(workspace, COMMENTS_FILENAME)


def get_comments_lock_path(workspace):
    return os.path.join(workspace, COMMENTS_LOCK_FILENAME)


READ_ONLY_COMMANDS = frozenset({
    "describe", "size", "slice", "filter", "filter_above",
    "top", "stats", "show", "export_md", "export_html", "unscored",
    "validate_evidence_refs",
    "comment_list", "comment_show",
})

COMMENT_COMMANDS = frozenset({"comment_add", "comment_list", "comment_show"})


@contextmanager
def locked_db(workspace, *, shared=False):
    """Acquire a file lock before reading/writing the CSV.
    Read-only commands use a shared lock (LOCK_SH) so they don't block each other.
    Write commands use an exclusive lock (LOCK_EX) so parallel agents don't corrupt the CSV."""
    lock_path = get_lock_path(workspace)
    if not os.path.exists(lock_path):
        try:
            with open(lock_path, "x") as f:
                f.write("\0")
        except FileExistsError:
            pass
    lock_fd = open(lock_path, "r+")
    try:
        _acquire_lock(lock_fd, shared)
        yield
    finally:
        _release_lock(lock_fd)
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


@contextmanager
def locked_comments(workspace, *, shared=False):
    lock_path = get_comments_lock_path(workspace)
    if not os.path.exists(lock_path):
        try:
            with open(lock_path, "x") as f:
                f.write("\0")
        except FileExistsError:
            pass
    lock_fd = open(lock_path, "r+")
    try:
        _acquire_lock(lock_fd, shared)
        yield
    finally:
        _release_lock(lock_fd)
        lock_fd.close()


def read_comments(workspace):
    comments_path = get_comments_path(workspace)
    if not os.path.exists(comments_path):
        return []
    with open(comments_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_comments(workspace, comments):
    comments_path = get_comments_path(workspace)
    with open(comments_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMMENTS_COLUMNS)
        writer.writeheader()
        writer.writerows(comments)


def _build_comment_tree(comments):
    """Return (top_level, replies) for a flat list of comments.
    top_level: comments with no parent, in original order.
    replies: {parent_id: [child_comments]} for threading."""
    top_level = [c for c in comments if not c.get("parent_comment_id")]
    replies = {}
    for c in comments:
        pid = c.get("parent_comment_id")
        if pid:
            replies.setdefault(pid, []).append(c)
    return top_level, replies


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
    row["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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
        if not row.get("created_at"):
            row["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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

    comment_counts = {}
    if os.path.exists(get_comments_path(args.workspace)):
        for c in read_comments(args.workspace):
            comment_counts[c["idea_id"]] = comment_counts.get(c["idea_id"], 0) + 1

    if args.columns:
        show_cols = [c.strip() for c in args.columns.split(",")]
        show_cols = [c for c in show_cols if c in columns or c == "comment_count"]
    else:
        show_cols = list(columns)
        if comment_counts:
            show_cols.append("comment_count")

    for row in rows:
        if comment_counts:
            row["comment_count"] = str(comment_counts.get(row.get("id", ""), 0))

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


def cmd_comment_add(args):
    _, rows = read_db(args.workspace)
    idea_ids = {r["id"] for r in rows}
    if str(args.idea_id) not in idea_ids:
        print(f"Error: idea #{args.idea_id} does not exist.", file=sys.stderr)
        sys.exit(1)
    if args.parent:
        comments = read_comments(args.workspace)
        if not any(c["id"] == args.parent for c in comments):
            print(f"Error: parent comment '{args.parent}' does not exist.", file=sys.stderr)
            sys.exit(1)
    comment_id = uuid.uuid4().hex[:12]
    new_comment = {
        "id": comment_id,
        "idea_id": str(args.idea_id),
        "author": args.author,
        "author_type": args.author_type,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "text": args.text,
        "parent_comment_id": args.parent or "",
    }
    comments_path = get_comments_path(args.workspace)
    if not os.path.exists(comments_path):
        with open(comments_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=COMMENTS_COLUMNS)
            writer.writeheader()
    with open(comments_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMMENTS_COLUMNS)
        writer.writerow(new_comment)
    print(f"Comment {comment_id} added to idea #{args.idea_id}")


def cmd_comment_list(args):
    comments = read_comments(args.workspace)
    if not comments:
        print("No comments found.")
        return
    if args.idea_id:
        comments = [c for c in comments if c["idea_id"] == str(args.idea_id)]
    if args.author_type:
        comments = [c for c in comments if c["author_type"] == args.author_type]
    if not comments:
        print("No comments match the filter.")
        return
    for c in comments:
        parent = f" (reply to {c['parent_comment_id']})" if c["parent_comment_id"] else ""
        print(f"[{c['id']}] idea #{c['idea_id']} | {c['author']} ({c['author_type']}) | {c['ts']}{parent}")
        print(f"  {c['text']}")


def cmd_comment_show(args):
    comments = read_comments(args.workspace)
    thread = [c for c in comments if c["idea_id"] == str(args.idea_id)]
    if not thread:
        print(f"No comments for idea #{args.idea_id}.")
        return
    _, rows = read_db(args.workspace)
    idea = next((r for r in rows if r["id"] == str(args.idea_id)), None)
    if idea:
        print(f"Idea #{args.idea_id}: {idea.get('name', '')}")
        print()
    top_level, replies = _build_comment_tree(thread)

    def _print_thread(comment, indent=0):
        prefix = "  " * indent
        badge = "human" if comment["author_type"] == "human" else "agent"
        print(f"{prefix}[{badge}] {comment['author']} — {comment['ts']}")
        print(f"{prefix}  {comment['text']}")
        for reply in replies.get(comment["id"], []):
            _print_thread(reply, indent + 1)

    for c in top_level:
        _print_thread(c)
        print()


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

    all_comments = read_comments(args.workspace)
    comments_by_idea = {}
    for c in all_comments:
        comments_by_idea.setdefault(c["idea_id"], []).append(c)

    # Markdown table
    print("| " + " | ".join(show_cols) + " |")
    print("| " + " | ".join(["---"] * len(show_cols)) + " |")
    for row in rows:
        vals = [str(row.get(c, "")).replace("|", "\\|") for c in show_cols]
        print("| " + " | ".join(vals) + " |")
        idea_comments = comments_by_idea.get(row.get("id", ""), [])
        if idea_comments:
            top_level, replies = _build_comment_tree(idea_comments)

            def _render_comment(comment, depth=0):
                indent = "  " * depth + "> "
                badge = "human" if comment["author_type"] == "human" else "agent"
                print(f"{indent}**[{badge}] {comment['author']}** ({comment['ts']}): {comment['text']}")
                for reply in replies.get(comment["id"], []):
                    _render_comment(reply, depth + 1)

            print()
            for c in top_level:
                _render_comment(c)
            print()


def _build_html(payload: str, top_score_cols: list) -> str:
    score_headers = "".join(
        f'<div class="col score sortable" data-col="scores.{c}" data-label="{c}">{c}</div>'
        for c in top_score_cols
    )
    template = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Idea Canvas</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f0f2f5;color:#1a1a1a;font-size:14px}
#app{max-width:1240px;margin:0 auto;padding:16px}
h1{font-size:18px;font-weight:600;margin-bottom:12px;color:#333}
#controls{background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;margin-bottom:10px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
#search{flex:1;min-width:200px;padding:7px 12px;border:1px solid #ccc;border-radius:6px;font-size:14px;outline:none}
#search:focus{border-color:#4a90d9;box-shadow:0 0 0 2px rgba(74,144,217,.15)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{padding:4px 10px;border-radius:20px;border:1.5px solid #ccc;background:#fff;cursor:pointer;font-size:12px;font-weight:500;transition:all .15s;user-select:none}
.chip:hover{border-color:#888}
.chip.active.SAFE{background:#28a745;border-color:#28a745;color:#fff}
.chip.active.BOLD{background:#fd7e14;border-color:#fd7e14;color:#fff}
.chip.active.WILD{background:#dc3545;border-color:#dc3545;color:#fff}
.chip.active.phase{background:#4a90d9;border-color:#4a90d9;color:#fff}
#count{font-size:12px;color:#888;white-space:nowrap;margin-left:auto}
#table{background:#fff;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden}
.thead{display:flex;align-items:center;padding:8px 12px;border-bottom:2px solid #e0e0e0;background:#f8f9fa;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:#555}
.col{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:0 6px}
.col.sortable{cursor:pointer;user-select:none}
.col.sortable:hover{color:#4a90d9}
.col.sorted{color:#4a90d9}
.col.id{width:44px;flex-shrink:0;text-align:right}
.col.name{flex:2;min-width:140px}
.col.tag{width:76px;flex-shrink:0;text-align:center}
.col.phase{width:96px;flex-shrink:0}
.col.score{width:84px;flex-shrink:0;text-align:right}
.col.comments{width:44px;flex-shrink:0;text-align:center}
details.row{border-bottom:1px solid #f0f0f0}
details.row:last-child{border-bottom:none}
details.row>summary{display:flex;align-items:center;padding:9px 12px;cursor:pointer;list-style:none;transition:background .1s}
details.row>summary::-webkit-details-marker{display:none}
details.row>summary:hover{background:#f8f9fa}
details.row[open]>summary{background:#f0f6ff;border-bottom:1px solid #dce8f7}
.tag-pill{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;text-transform:uppercase}
.tag-pill.SAFE{background:#d4edda;color:#155724}
.tag-pill.BOLD{background:#ffe8cc;color:#7d3c00}
.tag-pill.WILD{background:#f8d7da;color:#721c24}
.tag-pill.empty{color:#bbb}
.score-val{font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:1px 6px;border-radius:10px;font-size:11px;font-weight:500}
.badge.human{background:#dbeafe;color:#1d4ed8}
.badge.agent{background:#f3f4f6;color:#666}
.cc{display:inline-block;min-width:20px;text-align:center;padding:1px 5px;border-radius:10px;font-size:11px;background:#f3f4f6;color:#888}
.cc.has{background:#dbeafe;color:#1d4ed8}
.detail{padding:14px 16px 16px 58px;background:#fafcff}
.description{margin-bottom:12px}
.dl{font-size:11px;text-transform:uppercase;color:#999;letter-spacing:.4px;margin-bottom:3px}
.dv{font-size:13px;line-height:1.55;white-space:pre-wrap;word-break:break-word;color:#1a1a1a}
.scores-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.score-chip{background:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:3px 9px;font-size:12px}
.score-chip .sn{color:#888}
.score-chip .sv{font-weight:600;color:#333;margin-left:4px}
.prov{font-size:11px;color:#aaa;margin-bottom:10px}
.comments-title{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:#999;margin-bottom:8px}
.comment{padding:8px 10px;border-radius:6px;border:1px solid #e9ecef;background:#fff;margin-bottom:6px}
.comment.reply{border-left:3px solid #c3d9f7}
.cmeta{font-size:11px;color:#999;margin-bottom:3px}
.ctext{font-size:13px;line-height:1.4;white-space:pre-wrap;word-break:break-word}
#empty{padding:48px;text-align:center;color:#bbb;font-size:14px}
</style>
</head>
<body>
<div id="app">
<h1>Idea Canvas</h1>
<div id="controls">
  <input id="search" type="text" placeholder="Search name and description…" autocomplete="off">
  <div class="chips" id="tag-chips"></div>
  <div class="chips" id="phase-chips"></div>
  <span id="count"></span>
</div>
<div id="table">
  <div class="thead">
    <div class="col id sortable" data-col="id" data-label="#">#</div>
    <div class="col name sortable" data-col="name" data-label="Name">Name</div>
    <div class="col tag">Tag</div>
    <div class="col phase sortable" data-col="phase" data-label="Phase">Phase</div>
    __SCORE_HEADERS__
    <div class="col comments sortable" data-col="comment_count" data-label="💬">💬</div>
  </div>
  <div id="rows"></div>
</div>
</div>
<script>
const DATA=__PAYLOAD__;
let state={sortCol:null,sortDir:-1,search:'',tags:new Set(),phases:new Set()};

function esc(s){
  if(s==null)return'';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function getNumVal(idea,col){
  if(col==='id'||col==='comment_count')return parseFloat(idea[col])||0;
  if(col.startsWith('scores.'))return parseFloat((idea.scores||{})[col.slice(7)])||0;
  return 0;
}

function renderComments(comments){
  if(!comments||!comments.length)return'';
  function rc(c,depth){
    const badge=c.author_type==='human'
      ?'<span class="badge human">human</span>'
      :'<span class="badge agent">agent</span>';
    const children=comments.filter(x=>x.parent_comment_id===c.id);
    return`<div class="comment${depth>0?' reply':''}" style="margin-left:${depth*20}px">
      <div class="cmeta">${badge} <strong>${esc(c.author)}</strong> · ${esc(c.ts)}</div>
      <div class="ctext">${esc(c.text)}</div>
      ${children.map(x=>rc(x,depth+1)).join('')}
    </div>`;
  }
  const roots=comments.filter(c=>!c.parent_comment_id);
  return`<div class="comments-title">Comments</div>${roots.map(c=>rc(c,0)).join('')}`;
}

function renderRow(idea){
  const topCols=DATA.topScoreCols;
  const allCols=DATA.allScoreCols;
  const tagCls=idea.tag?` ${idea.tag}`:'';
  const tagHtml=idea.tag
    ?`<span class="tag-pill${tagCls}">${esc(idea.tag)}</span>`
    :`<span class="tag-pill empty">—</span>`;
  const scoreHtml=topCols.map(c=>{
    const v=(idea.scores||{})[c];
    return`<div class="col score"><span class="score-val">${v!=null&&v!==''?parseFloat(v).toFixed(1):'—'}</span></div>`;
  }).join('');
  const ccHtml=`<div class="col comments"><span class="cc${idea.comment_count>0?' has':''}">${idea.comment_count}</span></div>`;

  const scoresExpanded=allCols.length&&idea.scores
    ?`<div class="scores-row">${allCols.map(c=>{
        const v=(idea.scores||{})[c];
        return v!=null&&v!==''?`<div class="score-chip"><span class="sn">${esc(c)}</span><span class="sv">${esc(v)}</span></div>`:'';
      }).join('')}</div>`:'';

  const prov=[];
  if(idea.source_agent)prov.push(`agent: ${esc(idea.source_agent)}`);
  if(idea.source_seed)prov.push(`seed: #${esc(idea.source_seed)}`);
  const provHtml=prov.length?`<div class="prov">[${prov.join(' · ')}]</div>`:'';

  return`<details class="row" data-id="${idea.id}">
  <summary>
    <div class="col id">${esc(idea.id)}</div>
    <div class="col name">${esc(idea.name)}</div>
    <div class="col tag">${tagHtml}</div>
    <div class="col phase">${esc(idea.phase||'—')}</div>
    ${scoreHtml}${ccHtml}
  </summary>
  <div class="detail">
    <div class="description"><div class="dl">Description</div><div class="dv">${esc(idea.description)}</div></div>
    ${scoresExpanded}${provHtml}${renderComments(idea.comments)}
  </div>
</details>`;
}

function updateHeader(){
  document.querySelectorAll('.thead .sortable').forEach(th=>{
    const col=th.dataset.col;
    const label=th.dataset.label;
    const arrow=col===state.sortCol?(state.sortDir===1?' ▲':' ▼'):'';
    th.textContent=label+arrow;
    th.classList.toggle('sorted',col===state.sortCol);
  });
}

function render(){
  const openIds=new Set();
  document.querySelectorAll('details[open]').forEach(d=>openIds.add(d.dataset.id));

  let ideas=DATA.ideas;
  if(state.tags.size>0)ideas=ideas.filter(i=>state.tags.has(i.tag||''));
  if(state.phases.size>0)ideas=ideas.filter(i=>state.phases.has(i.phase||''));
  if(state.search){
    const q=state.search.toLowerCase();
    ideas=ideas.filter(i=>(i.name||'').toLowerCase().includes(q)||(i.description||'').toLowerCase().includes(q));
  }
  if(state.sortCol){
    const col=state.sortCol,dir=state.sortDir;
    const isNum=col==='id'||col==='comment_count'||col.startsWith('scores.');
    ideas=[...ideas].sort((a,b)=>{
      if(isNum)return dir*(getNumVal(a,col)-getNumVal(b,col));
      const av=(a[col]||'').toLowerCase(),bv=(b[col]||'').toLowerCase();
      return dir*(av<bv?-1:av>bv?1:0);
    });
  }

  document.getElementById('count').textContent=`${ideas.length} / ${DATA.ideas.length} ideas`;
  const container=document.getElementById('rows');
  if(!ideas.length){container.innerHTML='<div id="empty">No ideas match your filters.</div>';updateHeader();return;}
  container.innerHTML=ideas.map(renderRow).join('');
  container.querySelectorAll('details').forEach(d=>{if(openIds.has(d.dataset.id))d.open=true;});
  updateHeader();
}

function buildChips(){
  const tagBar=document.getElementById('tag-chips');
  DATA.tags.forEach(tag=>{
    const chip=document.createElement('div');
    chip.className=`chip ${tag}`;chip.textContent=tag;
    chip.onclick=()=>{state.tags.has(tag)?state.tags.delete(tag):state.tags.add(tag);chip.classList.toggle('active',state.tags.has(tag));render();};
    tagBar.appendChild(chip);
  });
  const phaseBar=document.getElementById('phase-chips');
  DATA.phases.forEach(phase=>{
    const chip=document.createElement('div');
    chip.className='chip phase';chip.textContent=phase;
    chip.onclick=()=>{state.phases.has(phase)?state.phases.delete(phase):state.phases.add(phase);chip.classList.toggle('active',state.phases.has(phase));render();};
    phaseBar.appendChild(chip);
  });
}

document.querySelectorAll('.thead .sortable').forEach(th=>{
  th.onclick=()=>{
    state.sortCol===th.dataset.col?state.sortDir*=-1:(state.sortCol=th.dataset.col,state.sortDir=-1);
    render();
  };
});

let raf=null;
document.getElementById('search').addEventListener('input',e=>{
  if(raf)cancelAnimationFrame(raf);
  raf=requestAnimationFrame(()=>{state.search=e.target.value;render();});
});

buildChips();
render();
</script>
</body>
</html>"""
    return template.replace("__PAYLOAD__", payload).replace("__SCORE_HEADERS__", score_headers)


def cmd_export_html(args):
    columns, rows = read_db(args.workspace)
    all_comments = read_comments(args.workspace)

    comments_by_idea = {}
    for c in all_comments:
        comments_by_idea.setdefault(c["idea_id"], []).append(c)

    # Detect numeric score columns ordered by fill rate
    score_cols = []
    for col in columns:
        if col in BUILT_IN_COLUMNS:
            continue
        filled_numeric = 0
        filled_total = 0
        for r in rows:
            v = r.get(col, "").strip()
            if v:
                filled_total += 1
                try:
                    float(v)
                    filled_numeric += 1
                except ValueError:
                    pass
        if filled_total > 0 and filled_numeric >= filled_total * 0.5:
            score_cols.append((col, filled_total))
    score_cols.sort(key=lambda x: -x[1])
    top_score_cols = [c for c, _ in score_cols[:3]]
    all_score_cols = [c for c, _ in score_cols]

    # Build compact idea objects (strip empty fields)
    ideas = []
    for row in rows:
        idea_id = row.get("id", "")
        clist = comments_by_idea.get(idea_id, [])
        obj = {
            "id": idea_id,
            "name": row.get("name", ""),
            "description": row.get("description", ""),
            "comment_count": len(clist),
        }
        for k in ("tag", "phase", "source_agent", "source_seed"):
            v = row.get(k, "")
            if v:
                obj[k] = v
        scores = {c: row[c] for c in all_score_cols if row.get(c, "").strip()}
        if scores:
            obj["scores"] = scores
        if clist:
            obj["comments"] = [
                {k: c[k] for k in ("id", "author", "author_type", "ts", "text", "parent_comment_id") if c.get(k)}
                for c in clist
            ]
        ideas.append(obj)

    tags = sorted({r.get("tag", "") for r in rows if r.get("tag", "")})
    phases = sorted({r.get("phase", "") for r in rows if r.get("phase", "")})

    payload = json.dumps({
        "ideas": ideas,
        "topScoreCols": top_score_cols,
        "allScoreCols": all_score_cols,
        "tags": tags,
        "phases": phases,
    }, ensure_ascii=False, separators=(",", ":"))

    html = _build_html(payload, top_score_cols)

    output_path = args.output if args.output else os.path.join(args.workspace, "ideas.html")
    if output_path == "-":
        print(html)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = len(html.encode("utf-8")) // 1024
        print(f"Exported {len(ideas)} ideas → {output_path} ({size_kb} KB)")


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

    # export_html
    p = subparsers.add_parser("export_html",
        help="Export ideas and comments as a self-contained offline HTML file")
    p.add_argument("workspace")
    p.add_argument("--output", default="", help="Output path (default: <workspace>/ideas.html). Use - for stdout.")

    # comment add
    p = subparsers.add_parser("comment_add",
        help="Add a comment to an idea")
    p.add_argument("workspace")
    p.add_argument("idea_id", type=int)
    p.add_argument("--author", required=True)
    p.add_argument("--author-type", required=True, choices=["human", "agent"], dest="author_type")
    p.add_argument("--text", required=True)
    p.add_argument("--parent", default="", help="Parent comment ID for threading")

    # comment list
    p = subparsers.add_parser("comment_list",
        help="List comments, optionally filtered by idea or author type")
    p.add_argument("workspace")
    p.add_argument("--idea-id", type=int, default=None, dest="idea_id")
    p.add_argument("--author-type", default=None, choices=["human", "agent"], dest="author_type")

    # comment show
    p = subparsers.add_parser("comment_show",
        help="Show full comment thread for one idea")
    p.add_argument("workspace")
    p.add_argument("idea_id", type=int)

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
        "comment_add": cmd_comment_add,
        "comment_list": cmd_comment_list,
        "comment_show": cmd_comment_show,
        "export_html": cmd_export_html,
    }

    if args.command == "init":
        commands[args.command](args)
    elif args.command in COMMENT_COMMANDS:
        shared = args.command in READ_ONLY_COMMANDS
        with locked_comments(args.workspace, shared=shared):
            commands[args.command](args)
    else:
        shared = args.command in READ_ONLY_COMMANDS
        with locked_db(args.workspace, shared=shared):
            commands[args.command](args)


if __name__ == "__main__":
    main()
