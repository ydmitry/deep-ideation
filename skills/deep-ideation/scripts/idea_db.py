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
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

DB_FILENAME = "ideas.csv"
BUILT_IN_COLUMNS = ["id", "name", "description", "source_agent", "source_seed", "chain", "tag", "phase"]


def get_db_path(workspace):
    return os.path.join(workspace, DB_FILENAME)


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
    print(f"Added {added} ideas (IDs {int(rows[-added]['id'])} to {rows[-1]['id']})")


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

    # unscored
    p = subparsers.add_parser("unscored")
    p.add_argument("workspace")
    p.add_argument("column")

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
        "multi_filter": cmd_multi_filter, "unscored": cmd_unscored,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
