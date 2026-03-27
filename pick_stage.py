import os, random

SELECT_DEF = r"data\select.def"
OUT_FILE = "current_stage.txt"
DEBUG_FILE = "stage_debug.txt"

def normalize_stage_path(s: str) -> str:
    s = s.strip().strip('"').strip("'").replace("\\", "/")
    if not s:
        return ""
    if s.startswith("./"):
        s = s[2:]
    # collapse any number of leading "stages/"
    while s.lower().startswith("stages/"):
        s = s[7:]
    return "stages/" + s

def main():
    stages = []
    in_stages = False

    with open(SELECT_DEF, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()

            # section start
            if line.lower() in ("[extrastages]", "[extra stages]", "[extra_stages]"):
                in_stages = True
                continue

            # section end
            if in_stages and line.startswith("[") and line.endswith("]"):
                break

            if not in_stages:
                continue

            # strip comments
            if ";" in line:
                line = line.split(";", 1)[0].strip()

            if not line:
                continue

            # IMPORTANT: only take stage path before first comma
            stage_part = line.split(",", 1)[0].strip()

            stage_path = normalize_stage_path(stage_part)

            if os.path.exists(stage_path):
                stages.append(stage_path)

    with open(DEBUG_FILE, "w", encoding="utf-8") as d:
        d.write(f"Stages found: {len(stages)}\n")
        for s in stages[:50]:
            d.write(s + "\n")
        if len(stages) > 50:
            d.write("...\n")

    if not stages:
        raise SystemExit("No valid stages found under [ExtraStages]. Check data/select.def paths.")

    choice = random.choice(stages)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(choice)

if __name__ == "__main__":
    main()