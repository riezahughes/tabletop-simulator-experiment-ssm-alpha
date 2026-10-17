# Builds the SSM TTS table. Run from project root: python -I tts/build.py  (needs pymupdf + Pillow)
import pymupdf, json, math, os, shutil
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = R + "/SOLID STATE MACHINE Alpha/"
IMG = R + "/tts/images/"
DOC = os.path.expanduser("~/Documents/My Games/Tabletop Simulator/").replace("\\", "/")
URL = "file:///" + DOC
os.makedirs(IMG, exist_ok=True)

def render(pdf, page, zoom, out):
    pymupdf.open(SRC + pdf)[page].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(IMG + out)

# --- images
for i in range(5):
    render("ssm_character_boards.pdf", 2*i, 3, f"board{i+1}_front.png")
    render("ssm_character_boards.pdf", 2*i+1, 3, f"board{i+1}_back.png")
render("ssm_map.pdf", 0, 2, "map.png")
render("ssm_game_disc.pdf", 0, 3, "disc.png")
render("ssm_game_disc.pdf", 1, 3, "disc_back.png")
cards = pymupdf.open(SRC + "ssm_memorycards.pdf")
N = len(cards); COLS, ROWS = 7, 5
cw, ch = round(cards[0].rect.width*3), round(cards[0].rect.height*3)
sheet = Image.new("RGB", (cw*COLS, ch*ROWS), "black")
for i, p in enumerate(cards):
    pm = p.get_pixmap(matrix=pymupdf.Matrix(3, 3))
    im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples).resize((cw, ch))
    sheet.paste(im, ((i % COLS)*cw, (i//COLS)*ch))
sheet.save(IMG + "memorycards_sheet.png")
mp = pymupdf.open(R + "/MemoryCore User Manual/User_Manual_Bootleg_V0.2.pdf")[3].get_pixmap(matrix=pymupdf.Matrix(3, 3))
back = Image.frombytes("RGB", (mp.width, mp.height), mp.samples)
h = round(back.width*ch/cw); y0 = (back.height-h)//2
back = back.crop((0, y0, back.width, y0+h)).resize((cw, ch), Image.LANCZOS); d = ImageDraw.Draw(back)
d.rectangle([10, 10, cw-11, ch-11], outline=(20, 20, 20), width=8)
d.rectangle([18, 18, cw-19, ch-19], outline=(246, 235, 70), width=4)
plate = [cw*0.12, ch*0.42, cw*0.88, ch*0.58]
d.rectangle(plate, fill=(20, 20, 20), outline=(0, 255, 160), width=4)
f = ImageFont.truetype("arialbd.ttf", cw//12)
d.text((cw/2, ch/2), "MEMORY CARD", font=f, fill=(246, 235, 70), anchor="mm")
back.save(IMG + "card_back.png")
nd = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); d = ImageDraw.Draw(nd)  # needle points up
d.polygon([(256, 20), (290, 256), (222, 256)], fill=(255, 40, 40, 255), outline=(0, 0, 0, 255))
d.ellipse([226, 226, 286, 286], fill=(230, 230, 230, 255), outline=(0, 0, 0, 255), width=4)
nd.save(IMG + "needle.png")
Image.new("RGB", (64, 64), (58, 38, 26)).save(IMG + "shelf.png")

# item tokens: icon cropped from the character board, background keyed to black
from PIL import ImageChops
TOK = {"ration": (14, 42), "diazepam": (126, 147), "medicine": (235, 255)}
bp = pymupdf.open(SRC + "ssm_character_boards.pdf")[0]
for k, (x0, x1) in TOK.items():
    cx = (x0 + x1)/2
    pm = bp.get_pixmap(matrix=pymupdf.Matrix(16, 16), clip=pymupdf.Rect(cx-14, 296, cx+14, 326))
    im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
    bg = im.getpixel((2, 2)); diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L")
    mask = diff.point(lambda v: 255 if v > 14 else 0)
    ImageDraw.floodfill(mask, (2, 2), 128)       # outer background -> 128
    out = Image.new("RGB", im.size, (0, 0, 0)); out.paste(im, mask=mask.point(lambda v: 0 if v == 128 else 255))
    box = out.getbbox(); w, h = box[2]-box[0], box[3]-box[1]; m = int(max(w, h)*1.2)
    sq = Image.new("RGB", (m, m), (0, 0, 0)); sq.paste(out.crop(box), ((m-w)//2, (m-h)//2))
    out = (sq.rotate(180) if k == "ration" else sq).resize((256, 256), Image.LANCZOS); out.save(IMG + f"token_{k}.png")

# GM plate (manual p.4 art), snap-zone frames and counter labels
SH = (58, 38, 26)
g = back.resize((1, 1)) and Image.frombytes("RGB", (mp.width, mp.height), mp.samples)
side = g.width; g = g.crop((0, 0, side, side)).resize((1020, 1020), Image.LANCZOS); d = ImageDraw.Draw(g)
d.rectangle([20, 20, 999, 999], outline=(20, 20, 20), width=22); d.rectangle([48, 48, 971, 971], outline=(246, 235, 70), width=10)
d.rectangle([110, 400, 910, 620], fill=(20, 20, 20), outline=(0, 255, 160), width=10)
d.text((510, 510), "GAME MASTER", font=ImageFont.truetype("arialbd.ttf", 100), fill=(246, 235, 70), anchor="mm")
g.save(IMG + "gm_plate.png")
MATC = {"White": (235, 235, 235), "Red": (220, 40, 40), "Yellow": (230, 220, 30), "Green": (50, 180, 45),
        "Blue": (30, 135, 255), "Pink": (245, 112, 205)}
for c, col in MATC.items():
    fr = Image.new("RGB", (512, 512), SH); d = ImageDraw.Draw(fr)
    d.rectangle([6, 6, 505, 505], outline=col, width=12)
    d.text((256, 256), "CHARACTER" + chr(10) + "BOARD", font=ImageFont.truetype("arialbd.ttf", 48), fill=tuple(v*2//3 for v in col), anchor="mm", align="center")
    fr.save(IMG + f"snap_{c.lower()}.png")
    for nm in ("LIFE", "FOCUS", "LEVEL"):
        lb = Image.new("RGB", (256, 96), SH); d = ImageDraw.Draw(lb)
        d.text((128, 48), nm, font=ImageFont.truetype("arialbd.ttf", 64), fill=col, anchor="mm")
        lb.save(IMG + f"label_{nm.lower()}_{c.lower()}.png")

# --- copy to TTS
for sub in ("Images", "PDF"): os.makedirs(DOC + "Mods/" + sub, exist_ok=True)
for fn in os.listdir(IMG): shutil.copy(IMG + fn, DOC + "Mods/Images/ssm_" + fn)
pdfs = {"ssm_rulebook": SRC + "ssm_rulebook.pdf", "ssm_secret_files": SRC + "ssm_secret_files.pdf",
        "memorycore_manual": R + "/MemoryCore User Manual/User_Manual_Bootleg_V0.2.pdf"}
for k, v in pdfs.items(): shutil.copy(v, DOC + f"Mods/PDF/{k}.pdf")
img = lambda n: URL + "Mods/Images/ssm_" + n
pdf = lambda n: URL + f"Mods/PDF/{n}.pdf"

# --- objects
cnt = [0]
def base(name, x, y, z, rot=(0, 180, 0), scale=(1, 1, 1), **kw):
    cnt[0] += 1
    o = {"GUID": kw.pop("guid", "%06x" % (0xa00000 + cnt[0])), "Name": name,
         "Transform": {"posX": x, "posY": y, "posZ": z, "rotX": rot[0], "rotY": rot[1], "rotZ": rot[2],
                       "scaleX": scale[0], "scaleY": scale[1], "scaleZ": scale[2]},
         "Nickname": "", "Description": "", "GMNotes": "", "ColorDiffuse": {"r": 1, "g": 1, "b": 1},
         "Locked": False, "Grid": True, "Snap": True, "Autoraise": True, "Sticky": True, "Tooltip": True,
         "Hands": False, "LuaScript": "", "LuaScriptState": "", "XmlUI": ""}
    o.update(kw); return o
def tile(img1, img2, x, y, z, s, typ=0, rot=(0, 180, 0), **kw):
    return base("Custom_Tile", x, y, z, rot=rot, scale=(s[0], 1, s[1]), CustomImage={
        "ImageURL": img1, "ImageSecondaryURL": img2 or img1, "ImageScalar": 1.0, "WidthScale": 0.0,
        "CustomTile": {"Type": typ, "Thickness": 0.1, "Stackable": False, "Stretch": True}}, **kw)

objs = []
SEATS = ["White", "Red", "Yellow", "Green", "Blue", "Pink"]
RGB = {"White": (1, 1, 1), "Red": (.86, .1, .09), "Yellow": (.9, .88, .1), "Green": (.19, .7, .17),
       "Blue": (.12, .53, 1), "Pink": (.96, .44, .81)}
DICE = ["Die_4", "Die_6", "Die_8", "Die_10", "Die_12", "Die_20"]
for i, c in enumerate(SEATS):
    sx = (-20, 0, 20)[i % 3]; sgn = 1 if i < 3 else -1; rot = 180 if i < 3 else 0
    objs.append(base("HandTrigger", sx, 3.3, 21*sgn, rot=(0, rot, 0), scale=(10.3, 6.6, 4.9), FogColor=c))
    for j, dn in enumerate(DICE):
        objs.append(base(dn, sx+(j-2.5)*1.6*sgn, 2, 16*sgn, rot=(0, 0, 0), ColorDiffuse=dict(zip("rgb", RGB[c]))))
snaps = []
for i, c in enumerate(SEATS):  # board snap point + Life/Level counters, just inside each seat's dice row
    sx = (-20, 0, 20)[i % 3]; sgn = 1 if i < 3 else -1
    snaps.append({"Position": {"x": sx, "y": 1.1, "z": 27.5*sgn}, "Rotation": {"x": 0, "y": 0 if sgn > 0 else 180, "z": 0}})
    rt = 0 if sgn > 0 else 180
    objs.append(tile(img(f"snap_{c.lower()}.png"), None, sx, 1.03, 27.5*sgn, (5, 5), rot=(0, rt, 0), Locked=True, Snap=False,
                     Nickname=c + " board zone"))
    for nm, off, val, dz in (("Life", 7, 0, 0), ("Focus", 7, 0, 3.5), ("Level", -7.5, 1, 0)):
        objs.append(tile(img(f"label_{nm.lower()}_{c.lower()}.png"), None, sx+sgn*off, 1.03, (26.9+dz)*sgn, (0.8, 0.3), rot=(0, rt, 0),
                         Locked=True, Snap=False, Nickname=f"{c} {nm} label"))
        objs.append(base("Counter", sx+sgn*off, 1.5, (25.5+dz)*sgn, rot=(0, 180 if sgn > 0 else 0, 0), Value=val, Locked=True,
                         Nickname=f"{c} {nm}", ColorDiffuse=dict(zip("rgb", RGB[c]))))
Y = 1.0
for zs in (-1, 1):  # long side shelves for player gear
    objs.append(tile(img("shelf.png"), None, 0, 1.0, 35*zs, (61.5, 13.5), Locked=True, Snap=False, Nickname="Player Shelf"))
for sx_ in (46.8, -46.8):
    objs.append(tile(img("shelf.png"), None, sx_, 1.0, 0, (13.5, 22.5), Locked=True, Snap=False, Nickname="Side Shelf"))
for i in range(5):  # boards, double-sided
    objs.append(tile(img(f"board{i+1}_front.png"), img(f"board{i+1}_back.png"), 41.3+12*(i % 2), Y+0.2, -10+10*(i//2), (4.7, 4.7),
                     Nickname=f"Character Board {i+1}"))
objs.append(tile(img("gm_plate.png"), None, 53.3, Y+0.2, 10, (4.7, 4.7), Nickname="GM Plate"))
objs.append(tile(img("map.png"), None, -14, Y, 1.5, (7.4, 11.1), Nickname="Map of ARK-9"))
objs.append(tile(img("disc.png"), img("disc_back.png"), 6, Y, 4, (4.5, 4.5), typ=2, guid="d15c01", Locked=True,
                 Nickname="Game Disc (Alert)"))
objs.append(base("Custom_Token", 6, Y+0.2, 4, scale=(1.8, 1, 1.8), guid="ae3d01", Locked=True, Nickname="Alert Spinner",
                 CustomImage={"ImageURL": img("needle.png"), "ImageSecondaryURL": "", "ImageScalar": 1.0, "WidthScale": 0.0,
                              "CustomToken": {"Thickness": 0.05, "MergeDistancePixels": 15.0, "StandUp": False, "Stackable": False}}))
cd = {"1": {"FaceURL": img("memorycards_sheet.png"), "BackURL": img("card_back.png"), "NumWidth": COLS,
            "NumHeight": ROWS, "BackIsHidden": True, "UniqueBack": False, "Type": 0}}
deck = base("DeckCustom", 16, 1.5, 4, rot=(0, 180, 180), scale=(1.5, 1, 1.5), Nickname="MemoryCards", CustomDeck=cd,
            DeckIDs=[100+i for i in range(N)])
deck["ContainedObjects"] = [dict(base("CardCustom", 0, 0, 0, rot=(0, 180, 180)), CardID=100+i, CustomDeck=cd) for i in range(N)]
objs.append(deck)
for n, f, x in [("SSM Rulebook (GM)", "ssm_rulebook", -13), ("Secret Files (GM)", "ssm_secret_files", 0),
                ("MemoryCore Manual", "memorycore_manual", 13)]:
    objs.append(base("Custom_PDF", -46.8, Y+0.2, x, scale=(2.4, 1, 2.4), Nickname=n,
                     CustomPDF={"PDFUrl": pdf(f), "PDFPassword": "", "PDFPage": 0, "PDFPageOffset": 0}))

for k, nm in (("ration", "Ration"), ("diazepam", "Diazepam"), ("medicine", "Medicine")):
    tok = tile(img(f"token_{k}.png"), None, 0, 0, 0, (0.5, 0.5), Nickname=nm)
    bag = base("Infinite_Bag", -3, 1.5, (-3.5, 1.5, 6.5)[list(TOK).index(k)], scale=(0.7, 0.7, 0.7), Nickname=nm + " (infinite)",
               ColorDiffuse={"r": .15, "g": .45, "b": .2}, ContainedObjects=[tok])
    objs.append(bag)

save = {"SaveName": "Solid State Machine", "GameMode": "Solid State Machine (MemoryCore)", "VersionNumber": "v14.2.2",
        "Gravity": 0.5, "PlayArea": 0.5, "Table": "Table_RPG", "Sky": "Sky_Regal", "SkyURL": img("background.png"), "Note": "", "Tags": ["RPG"],
        "PlayerCounts": [1, 6], "Hands": {"Enable": True, "DisableUnused": False, "Hiding": 0},
        "LuaScript": "SNAPS = {" + ", ".join("{position = {%g, %g, %g}, rotation = {0, %g, 0}, rotation_snap = true}" % (q["Position"]["x"], q["Position"]["y"], q["Position"]["z"], q["Rotation"]["y"]) for q in snaps) + "}" + chr(10) + open(R + "/tts/lua/global.lua", encoding="utf8").read(), "LuaScriptState": "", "XmlUI": "",
        "ObjectStates": objs}
for p in (R + "/tts/Solid_State_Machine.json", DOC + "Saves/Solid_State_Machine.json"):
    json.dump(save, open(p, "w", encoding="utf8"), indent=1)
print("ok", N, "cards")
