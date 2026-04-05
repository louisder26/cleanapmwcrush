import time
import re
from supabase import create_client

# ── CONFIG ──────────────────────────────────────────────
SUPABASE_URL = "https://wcnssxmdfmmekcolragv.supabase.co"
SUPABASE_KEY = "sb_publishable_B9bjLjlywOjkHxbwXtAyWw_u-k3FTJt"  # remplace par ta service_role key !
INTERVALLE   = 1  # secondes entre chaque scan

# ── LISTE D'INSULTES ─────────────────────────────────────
# Ajoute / retire des mots selon tes besoins
INSULTES = [
    # français
    "connard", "connasse", "salope", "pute", "putain", "enculé", "enculer",
    "merde", "fils de pute", "fdp", "batard", "bâtard", "nique", "niquer",
    "trou du cul", "trouduc", "branler", "branleur", "con", "conne",
    "pd", "pédé", "tapette", "gouine", "raciste", "nazi", "suicide",
    "crève", "crever", "mort", "tuer", "tues", "viol", "violer",
    "grosse vache", "gros con", "idiot", "imbécile", "débile",
    # anglais basique
    "fuck", "shit", "bitch", "asshole", "bastard", "whore", "slut",
    "dick", "cock", "pussy", "cunt", "nigger", "faggot", "retard",
]

# Pré-compilation : mot entier, insensible à la casse, ignore accents via unicode
PATTERNS = [
    re.compile(r'\b' + re.escape(mot) + r'\b', re.IGNORECASE | re.UNICODE)
    for mot in INSULTES
]

# ── CLIENT SUPABASE ──────────────────────────────────────
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── LOGIQUE ──────────────────────────────────────────────
def contient_insulte(texte: str) -> bool:
    if not texte:
        return False
    for pattern in PATTERNS:
        if pattern.search(texte):
            return True
    return False

def champs_a_verifier(row: dict) -> list[str]:
    """Retourne les noms des champs qui contiennent une insulte."""
    champs = ["message", "crush_prenom", "sender_prenom", "sender_nom", "sender_classe"]
    return [c for c in champs if contient_insulte(row.get(c, "") or "")]

def scanner_et_supprimer():
    res = db.table("crushes").select("id, message, crush_prenom, sender_prenom, sender_nom, sender_classe").execute()
    rows = res.data or []

    a_supprimer = [row["id"] for row in rows if champs_a_verifier(row)]

    if not a_supprimer:
        return 0

    db.table("crushes").delete().in_("id", a_supprimer).execute()
    return len(a_supprimer)

# ── BOUCLE PRINCIPALE ────────────────────────────────────
print("🛡️  Modérateur démarré — scan toutes les secondes")
print(f"   {len(INSULTES)} mots surveillés\n")

total = 0
try:
    while True:
        supprimes = scanner_et_supprimer()
        if supprimes:
            total += supprimes
            print(f"[{time.strftime('%H:%M:%S')}] ❌ {supprimes} message(s) supprimé(s)  |  total : {total}")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ✅ RAS", end="\r")
        time.sleep(INTERVALLE)
except KeyboardInterrupt:
    print(f"\n\nArrêt. {total} message(s) supprimé(s) au total.")
