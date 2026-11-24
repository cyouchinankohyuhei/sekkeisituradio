# ステップ3：骨組みDXFの作成（壁・室名・階段・押入・寸法）
# 座標は2Fの左端を0とする（1F = 2F座標 - 910）。y=0 が手書き図の上端。単位 mm
import sys
import ezdxf

G = 455  # すべての寸法は455の倍数

# (室名, x0, x1, y0, y1, 種別)  種別: room=壁で囲む部屋 / overlay=部屋の中に重ねる記号
FLOORS = {
    "2F": [
        ("撮影スペース", 0, 4550, 0, 4550, "room"),
        ("和室8帖", 4550, 8190, 0, 3640, "room"), ("押入", 4550, 8190, 3640, 4550, "oshi"),
        ("洋室", 8190, 10920, 0, 4550, "room"),
        ("押入", 10920, 11830, 0, 3640, "oshi"), ("?", 10920, 11830, 3640, 4550, "room"),
        ("和室8帖", 11830, 15470, 0, 3640, "room"), ("押入", 11830, 14560, 3640, 4550, "oshi"),
        ("階段", 14560, 15470, 3640, 4550, "stair"),
        ("和室8帖", 15470, 19110, 0, 3640, "room"), ("押入", 15470, 19110, -455, 0, "oshi"),
        ("押入", 15470, 19110, 3640, 4550, "oshi"),
        ("縁側", 19110, 19565, 0, 4550, "room"),
        # 部屋の中に重ねる階段（壁にはしない）
        ("階段", 910, 2730, 3640, 4550, "stair-ov"),
        ("階段", 10010, 11375, 3640, 4550, "stair-ov"),
    ],
    "1F": [
        ("ホール", 910, 2730, 0, 3640, "room"), ("階段", 910, 2730, 3640, 4550, "stair"),
        ("店舗", 2730, 10010, 0, 4550, "room"),
        ("土間", 10010, 11375, 0, 910, "room"), ("WC", 10010, 11375, 910, 2275, "room"),
        ("WC", 10010, 11375, 2275, 3640, "room"), ("階段", 10010, 11375, 3640, 4550, "stair"),
        ("廊下", 11375, 12740, 0, 4550, "room"),
        ("和室6帖", 12740, 15470, 0, 3640, "room"), ("階段", 12740, 15470, 3640, 4550, "stair"),
        ("床の間", 15470, 15925, 0, 1365, "room"), ("洗面脱衣", 15925, 17290, 0, 1365, "room"),
        ("フロ", 17290, 19110, 0, 910, "room"), ("", 17290, 18200, 910, 1365, "room"),
        ("台所", 15470, 19110, 1365, 4550, "room"), ("", 18200, 19110, 910, 1365, "room"),
    ],
}
# フロ内部の仕切り線（17290-18200 の y=910）は風呂の一部なので壁から除く
REMOVE = {"1F": [((17290, 910), (18200, 910))]}
DIMS = {"2F": [0, 910, 4550, 8190, 10920, 11830, 15470, 19110, 19565],
        "1F": [910, 2730, 10010, 11375, 12740, 15470, 19110]}
FLOOR_Y = {"2F": 0, "1F": 8000}  # 図面上で2Fを上、1Fを下に配置


def wall_segments(rooms, remove):
    """部屋の辺を455単位に分解→重複除去→一直線に連結"""
    units = set()
    for _, x0, x1, y0, y1, k in rooms:
        if k.endswith("-ov"):
            continue
        for (a, b) in [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))]:
            if a[1] == b[1]:
                for x in range(a[0], b[0], G):
                    units.add(("h", a[1], x))
            else:
                for y in range(a[1], b[1], G):
                    units.add(("v", a[0], y))
    for (a, b) in remove:
        for x in range(a[0], b[0], G):
            units.discard(("h", a[1], x))
    segs = []
    for d in ("h", "v"):
        lines = {}
        for (dd, c, s) in units:
            if dd == d:
                lines.setdefault(c, []).append(s)
        for c, ss in lines.items():
            ss.sort()
            start = prev = ss[0]
            for s in ss[1:] + [None]:
                if s is not None and s == prev + G:
                    prev = s
                    continue
                segs.append((d, c, start, prev + G))
                if s is not None:
                    start = prev = s
    return segs


def build(path, version, encoding=None):
    doc = ezdxf.new(version)
    if encoding:
        doc.header["$DWGCODEPAGE"] = "ANSI_932"
    for name, color in [("壁芯", 7), ("室名", 3), ("階段", 5), ("押入", 8), ("寸法", 4), ("注記", 1)]:
        doc.layers.add(name, color=color)
    if version != "R12":
        doc.styles.add("JP", font="msgothic.ttc")
    style = {} if version == "R12" else {"style": "JP"}
    msp = doc.modelspace()

    for fl, rooms in FLOORS.items():
        oy = FLOOR_Y[fl]
        P = lambda x, y: (x, -(y + oy))  # DXFはyが上向きなので反転
        for d, c, s, e in wall_segments(rooms, REMOVE.get(fl, [])):
            a, b = ((s, c), (e, c)) if d == "h" else ((c, s), (c, e))
            msp.add_line(P(*a), P(*b), dxfattribs={"layer": "壁芯"})
        for name, x0, x1, y0, y1, k in rooms:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if k.startswith("stair"):
                if k == "stair-ov":
                    msp.add_polyline2d([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)], close=True,
                                       dxfattribs={"layer": "階段"})
                n = round((x1 - x0) / 227.5)
                for i in range(1, n):
                    x = x0 + (x1 - x0) * i / n
                    msp.add_line(P(x, y0), P(x, y1), dxfattribs={"layer": "階段"})
                msp.add_line(P(x0, cy), P(x1, cy), dxfattribs={"layer": "階段"})
            if k == "oshi":
                msp.add_line(P(x0, y0), P(x1, y1), dxfattribs={"layer": "押入"})
            if name and not k.startswith("stair") or k == "stair":
                h = 150 if min(x1 - x0, y1 - y0) < 1000 else 250
                if name:
                    msp.add_text(name, height=h, dxfattribs={"layer": "室名", **style}).set_placement(
                        P(cx, cy), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        # 寸法（簡易：線と文字）
        xs = DIMS[fl]
        dy = 4550 + 600
        msp.add_line(P(xs[0], dy), P(xs[-1], dy), dxfattribs={"layer": "寸法"})
        for x in xs:
            msp.add_line(P(x, dy - 150), P(x, dy + 150), dxfattribs={"layer": "寸法"})
        for a, b in zip(xs, xs[1:]):
            msp.add_text(f"{b - a:,}", height=180, dxfattribs={"layer": "寸法", **style}).set_placement(
                P((a + b) / 2, dy - 120), align=ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)
        msp.add_text(f"{xs[-1] - xs[0]:,}", height=200, dxfattribs={"layer": "寸法", **style}).set_placement(
            P((xs[0] + xs[-1]) / 2, dy + 500), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text(fl, height=500, dxfattribs={"layer": "注記", **style}).set_placement(
            P(-1500, 0), align=ezdxf.enums.TextEntityAlignment.TOP_LEFT)
    msp.add_text("2F 洋室下の?：1F階段の真上。押入との取り合い要確認", height=180,
                 dxfattribs={"layer": "注記", **style}).set_placement(P(8190, -1200))
    if encoding:
        doc.saveas(path, encoding=encoding)
    else:
        doc.saveas(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    build(f"{out}/madori-honekumi.dxf", "R2010")
    build(f"{out}/madori-honekumi_jwcad.dxf", "R12", encoding="cp932")
