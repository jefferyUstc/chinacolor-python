from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from .dataset import load_palette_list, load_chinacolor
from .colorparse import to_hex


PaletteIdent = Union[int, str]


def list_palettes() -> List[Dict[str, Any]]:
    """Return palette metadata as a list of dicts.

    Fields: index (1-based), element_name, palette_name (CN), palette_name_e (EN),
    type, color_count.
    """
    pl_map, order = load_palette_list()
    out: List[Dict[str, Any]] = []
    for idx, key in enumerate(order, start=1):
        p = pl_map[key]
        out.append(
            {
                "index": idx,
                "element_name": key,
                "palette_name": p.get("palette_name"),
                "palette_name_e": p.get("palette_name_e"),
                "type": p.get("type"),
                "color_count": p.get("color_count"),
            }
        )
    return out


def _normalize_identifier(x: PaletteIdent) -> Tuple[str, Dict[str, Any]]:
    pl_map, order = load_palette_list()
    # numeric index
    if isinstance(x, (int,)):
        if x < 1 or x > len(order):
            raise IndexError(f"Index {x} out of range (1..{len(order)})")
        key = order[x - 1]
        return key, pl_map[key]

    if isinstance(x, str):
        # try exact element key
        if x in pl_map:
            return x, pl_map[x]

        # case-insensitive match on palette_name or palette_name_e
        low = x.lower()
        for k in order:
            p = pl_map[k]
            if str(p.get("palette_name", "")).lower() == low or str(p.get("palette_name_e", "")).lower() == low:
                return k, p

    raise KeyError(f"Palette '{x}' not found. Use list_palettes() to inspect available options.")


def find_palette(identifier: PaletteIdent) -> Dict[str, Any]:
    """Return the palette dict for an identifier (index, element name, CN/EN name)."""
    _, p = _normalize_identifier(identifier)
    return p


def _interpolate_colors(base: List[str], n: int) -> List[str]:
    # Use matplotlib to interpolate colors uniformly in RGB space
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    n = int(n)
    cmap = LinearSegmentedColormap.from_list("_tmp", base, N=max(n, 256))
    # sample n colors evenly
    colors = [
        tuple((c * 255).astype(int))
        for c in (cmap(np.linspace(0, 1, n))[:, :3])
    ]
    # back to hex
    return ["#" + "".join(f"{v:02X}" for v in rgb) for rgb in colors]


def _diverging_center_out(base: List[str], n: int) -> List[str]:
    m = len(base)
    if n >= m:
        return base[:n]
    mid = (m - 1) // 2  # 0-based center
    if n == 1:
        return [base[mid]]
    left = []
    right = []
    # expand from center
    li = mid - 1
    ri = mid + 1
    out = [base[mid]]
    while len(out) < n:
        if li >= 0:
            out.append(base[li])
            if len(out) >= n:
                break
            li -= 1
        if ri < m:
            out.append(base[ri])
            ri += 1
        if li < 0 and ri >= m:
            break
    # keep original left-to-right order as in base (not symmetrical around center),
    # but since we appended center, then left, then right, we should re-order by their index
    idxs = [base.index(c) for c in out]
    sorted_pairs = sorted(zip(idxs, out))
    return [c for _, c in sorted_pairs][:n]


def create_color_pick(
    *,
    color_id: Optional[Iterable[int]] = None,
    groups: Optional[Iterable[int]] = None,
    subgroups: Optional[Iterable[Iterable[int]]] = None,
    order_rule: int = 1,
) -> Dict[str, Any]:
    """Construct a color_pick dict similar to the R API.

    - color_id: explicit color ids
    - groups: list of group numbers (aka group_id)
    - subgroups: list-of-lists per group; each contains values in 1..4 or a single -1 (meaning 4:1)
    - order_rule: 1 preserve input order; 0 ascending by color_id; -1 descending by color_id
    """
    if order_rule not in (1, 0, -1):
        raise ValueError("order_rule must be 1, 0 or -1")
    pick: Dict[str, Any] = {"order": order_rule}
    if color_id is not None:
        pick["color_id"] = list(color_id)
    if groups is not None:
        groups = list(groups)
        if subgroups is None:
            subgroups = [list(range(1, 5)) for _ in groups]
        else:
            subgroups = [list(sg) if not isinstance(sg, int) else [sg] for sg in subgroups]
            if len(subgroups) != len(groups) and len(subgroups) != 1:
                raise ValueError("subgroups must be length 1 or match length of groups")
            if len(subgroups) == 1 and len(groups) > 1:
                subgroups = subgroups * len(groups)
        pick["group_info"] = {"group": groups, "subgroup": subgroups}
    return pick


def get_palette(
    identifier: PaletteIdent,
    n: Optional[int] = None,
    direction: int = 1,
) -> List[str]:
    """Return a list of hex colors from a built-in palette.

    - Sequential/Diverging: when n > base_count, interpolate; when n < base_count,
      take first n (diverging uses center-out selection).
    - Qualitative: when n > base_count, cycle; else take first n.
    - direction: 1 normal, -1 reversed.
    """
    key, p = _normalize_identifier(identifier)
    base = list(p.get("hex", []))
    base_count = int(p.get("color_count", len(base)))
    ptype = p.get("type", "qualitative")

    if n is None:
        colors = base
    else:
        n = int(n)
        if n > base_count:
            if ptype in ("sequential", "diverging"):
                colors = _interpolate_colors(base, n)
            else:
                # qualitative cycles
                colors = (base * (n // len(base) + 1))[:n]
        else:
            if ptype in ("sequential", "qualitative"):
                colors = base[:n]
            elif ptype == "diverging":
                colors = _diverging_center_out(base, n)
            else:
                colors = base[:n]

    if direction not in (1, -1):
        direction = 1
    if direction == -1:
        colors = list(reversed(colors))
    return colors


def custom_palette(
    color_ids: Optional[Iterable[int]] = None,
    names: Optional[Iterable[str]] = None,
    hexes: Optional[Iterable[str]] = None,
    groups: Optional[Iterable[int]] = None,
    subgroups: Optional[Iterable[Iterable[int]]] = None,
    order: int = 1,
    n: Optional[int] = None,
    direction: int = 1,
) -> List[str]:
    """Build a custom palette.

    Supports:
    - color_ids: 1-based indices into the 384-color list
    - names: match by color Chinese name (exact match)
    - hexes: direct hex values
    - order: 1 preserve input order; 0 sort by color_id asc; -1 sort by color_id desc
    - n: if provided and larger than result, cycle to length n; if smaller, truncate
    - direction: 1 or -1 to reverse

    Note: Group/subgroup selection is only possible if such fields are present in the
    JSON dataset. This function focuses on ID/name/hex selection to be dataset-agnostic.
    """
    base_colors = load_chinacolor()
    id_to_hex = {c.get("color_id"): c["hex"] for c in base_colors if c.get("hex")}
    name_to_hex = {c.get("name"): c["hex"] for c in base_colors if c.get("hex")}

    chosen: List[Tuple[int, str]] = []  # (id, hex)

    if color_ids:
        for cid in color_ids:
            cid = int(cid)
            if cid in id_to_hex:
                chosen.append((cid, id_to_hex[cid]))

    if names:
        for nm in names:
            if nm in name_to_hex:
                # find id too, if possible
                # linear search acceptable for 384 items
                cid = next((c["color_id"] for c in base_colors if c["name"] == nm), None)
                chosen.append((cid if cid is not None else 10**9, name_to_hex[nm]))

    if hexes:
        for hx in hexes:
            try:
                hx_norm = to_hex(str(hx))
                chosen.append((10**9 + len(chosen), hx_norm))
            except Exception:
                # ignore invalid string
                continue

    # Group/subgroup selection if provided
    if groups is not None:
        groups = list(groups)
        # normalize subgroups
        if subgroups is None:
            subgroups = [list(range(1, 5)) for _ in groups]
        else:
            # ensure list-of-lists
            subgroups = [list(sg) if not isinstance(sg, int) else [sg] for sg in subgroups]
            if len(subgroups) < len(groups):
                # recycle
                last = subgroups[-1]
                subgroups = subgroups + [last] * (len(groups) - len(subgroups))

        # Iterate groups in order; for each subgroup order, select color_ids
        for gi, g in enumerate(groups):
            s_list = subgroups[gi]
            # handle -1 meaning 4:1
            if len(s_list) == 1 and s_list[0] == -1:
                s_list = [4, 3, 2, 1]
            for s in s_list:
                # pick colors where group or group_id matches and subgroup/subgroup_id matches
                for c in base_colors:
                    gval = c.get("group") if c.get("group") is not None else c.get("group_id")
                    sval = c.get("subgroup") if c.get("subgroup") is not None else c.get("subgroup_id")
                    if gval == g and sval == s:
                        cid = c.get("color_id")
                        hx = c.get("hex")
                        if cid is not None and hx:
                            chosen.append((cid, hx))

    # deduplicate by hex while preserving order
    seen = set()
    dedup: List[Tuple[int, str]] = []
    for cid, hx in chosen:
        if hx not in seen:
            seen.add(hx)
            dedup.append((cid, hx))

    if not dedup:
        raise ValueError("No colors selected. Provide color_ids, names or hexes.")

    if order == 0:
        dedup.sort(key=lambda t: (t[0] if t[0] is not None else 10**9, t[1]))
    elif order == -1:
        dedup.sort(key=lambda t: (t[0] if t[0] is not None else 10**9, t[1]), reverse=True)

    colors = [hx for _, hx in dedup]

    if n is not None:
        n = int(n)
        if n > len(colors):
            colors = (colors * (n // len(colors) + 1))[:n]
        else:
            colors = colors[:n]

    if direction == -1:
        colors = list(reversed(colors))
    return colors


def custom_palette_pick(color_pick: Dict[str, Any], *, n: Optional[int] = None, direction: int = 1) -> List[str]:
    """Build a custom palette from a color_pick dict.

    Supports the same fields as R: color_id, group_info{group, subgroup}, order.
    """
    order = int(color_pick.get("order", 1))
    groups = None
    subgroups = None
    gi = color_pick.get("group_info")
    if gi:
        groups = gi.get("group")
        subgroups = gi.get("subgroup")
    return custom_palette(
        color_ids=color_pick.get("color_id"),
        groups=groups,
        subgroups=subgroups,
        order=order,
        n=n,
        direction=direction,
    )
