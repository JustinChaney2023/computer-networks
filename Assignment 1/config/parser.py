# Tiny "yaml-ish" parser for our two yaml files.
# "Why did you not use PyYAML or similar? or Why did I use yaml in general?"
# I wanted to make it so no third-party libraries are needed. and I wanted
# to keep it simple and readable. I also wanted to avoid JSON because
# I have more experience with YAML and it is more readable for this use case.
# 
# Files it expects:
#   airports.yaml   -> lines like: ANC: "127.0.0.1:6001"
#   routes.yaml     -> hubs: ["ANC"]
#                   default_hub:
#                        SEA: "ANC"
#                        FAI: ["ANC", "SEA"]
#
# It ignores blank lines and lines starting with '#'.
# This is NOT a full YAML parser. It just handles my use case.
#
# ChatGPT/CoPilot was used in tandem with myself during this

def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s

def _is_iata(code: str) -> bool:
    code = code.strip()
    return len(code) == 3 and code.isalpha()

def load_airports(path: str) -> dict:
    """
    Read airports.yaml into a dict like {"ANC": "127.0.0.1:6001", ...}.
    Expected line format: IATA: "host:port"
    """
    result = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            # skip comments / blanks
            if not line or line.startswith("#"):
                continue

            # split only at the first colon so "host:port" is intact
            if ":" not in line:
                raise ValueError(f"airports.yaml bad line (no colon): {raw.rstrip()}")
            key, rest = line.split(":", 1)
            key = key.strip().upper()
            if not _is_iata(key):
                raise ValueError(f"airports.yaml bad IATA: {key!r}")

            addr = _strip_quotes(rest).strip()  # e.g. 127.0.0.1:6001
            if ":" not in addr:
                raise ValueError(f"airports.yaml bad address (need host:port): {addr!r}")
            host, port_str = addr.rsplit(":", 1)
            if not host:
                raise ValueError("airports.yaml empty host")
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"airports.yaml port not an int: {port_str!r}")
            if port <= 1024 or port >= 65536:
                raise ValueError(f"airports.yaml port out of range: {port}")

            result[key] = f"{host}:{port}"

    if "ANC" not in result:
        raise ValueError("airports.yaml must include ANC")
    return result

def load_routes(path: str) -> tuple[list[str], dict[str, list[str]]]:
    """
    Read routes.yaml into (hubs_list, default_hub_dict).
    Expects something like
    hubs: ["ANC", "SEA"]
    default_hub:
        ASD: "ANC" 
        WSD: ["ANC", "SEA"]
    Hours worked: "2"
    """
    hubs: list[str] = []
    default_hub: dict[str, list[str]] = {}
    mode = None  # None or "default"

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()

            # skip comments / blanks
            if not stripped or stripped.startswith("#"):
                continue

            # hubs: ["ANC", "XYZ"]
            if stripped.startswith("hubs:"):
                # find the [...] part and split by comma
                if "[" in stripped and "]" in stripped:
                    inside = stripped.split("[", 1)[1].split("]", 1)[0]
                    items = [x.strip() for x in inside.split(",") if x.strip()]
                    hubs = [ _strip_quotes(x).upper() for x in items ]
                else:
                    # keep it simple: we only handle bracket form
                    raise ValueError('routes.yaml expected hubs: ["ANC", ...]')
                mode = None
                continue

            # start of default_hub block
            if stripped.startswith("default_hub:"):
                mode = "default"
                continue

            # inside default_hub: read indented KEY: "VAL" lines
            if mode == "default":
                # require indentation so we know we're still in the block
                if line.startswith(" ") or line.startswith("\t"):
                    if ":" in stripped:
                        k, v = stripped.split(":", 1)
                        k = k.strip().upper()
                        raw_value = v.strip()
                        if not _is_iata(k):
                            raise ValueError(f"routes.yaml bad mapping key: {k!r}")

                        hub_candidates: list[str] = []
                        if raw_value.startswith("[") and raw_value.endswith("]"):
                            inside = raw_value[1:-1]
                            items = [item.strip() for item in inside.split(",") if item.strip()]
                            for item in items:
                                hub_code = _strip_quotes(item).strip().upper()
                                if not _is_iata(hub_code):
                                    raise ValueError(f"routes.yaml bad hub code in list: {hub_code!r}")
                                hub_candidates.append(hub_code)
                        else:
                            hub_code = _strip_quotes(raw_value).strip().upper()
                            if not _is_iata(hub_code):
                                raise ValueError(f"routes.yaml bad hub code: {hub_code!r}")
                            hub_candidates.append(hub_code)

                        if not hub_candidates:
                            raise ValueError(f"routes.yaml empty hub list for {k}")

                        for hub_code in hub_candidates:
                            if hub_code not in hubs:
                                raise ValueError(f"routes.yaml hub {hub_code!r} missing from hubs list")

                        default_hub[k] = hub_candidates
                    continue
                else:
                    mode = None

    if "ANC" not in hubs:
        raise ValueError("routes.yaml hubs must include ANC")
    return hubs, default_hub

# quick test case: print a tiny summary
if __name__ == "__main__":
    a = load_airports("src/airports.yaml")
    h, d = load_routes("src/routes.yaml")
    print("airports:", len(a), "ANC:", a.get("ANC"))
    print("hubs:", h)
    print("default_hub count:", len(d), "SEA->", d.get("SEA"))
