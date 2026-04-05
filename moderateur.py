import os
import time
import re
from supabase import create_client

# ── CONFIG ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
DUREE        = 55   # secondes avant arrêt propre
INTERVALLE   = 2    # scan toutes les 2 secondes

# ── LISTE D'INSULTES ────────────────────────────────────
INSULTES = [
    # français
    "connard", "connasse", "salope", "pute", "putain", "enculé", "enculer",
    "merde", "fils de pute", "fdp", "batard", "bâtard", "nique", "niquer",
    "trou du cul", "trouduc", "branler", "branleur", "con", "conne",
    "pd", "pédé", "tapette", "gouine", "raciste", "nazi", "suicide",
    "crève", "crever", "tuer", "tues", "viol", "violer",
    "grosse vache", "gros con", "idiot", "imbécile", "débile",
    # anglais
    "fuck", "shit", "bitch", "asshole", "bastard", "whore", "slut",
    "dick", "cock", "pussy", "cunt", "nigger", "faggot", "retard",
]

# Pré-compilation des patterns regex
PATTERNS = [
    re.compile(r'\b' + re.escape(mot) + r'\b', re.IGNORECASE | re.UNICODE)
    for mot in INSULTES
]

# ── CLIENT SUPABASE ──────────────────────────────────────
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── FONCTIONS ────────────────────────────────────────────
def contient_insulte(texte):
    if not texte:
        return False
    for pattern in PATTERNS:
        if pattern.search(texte):
            return True
    return False

def scanner_et_supprimer():
    res = db.table("crushes").select(
        "id, message, crush_prenom, sender_prenom, sender_nom, sender_classe"
    ).execute()
    rows = res.data or []

    ids_a_supprimer = [
        row["id"] for row in rows
        if any(
            contient_insulte(row.get(champ) or "")
            for champ in ["message", "crush_prenom", "sender_prenom", "sender_nom", "sender_classe"]
        )
    ]

    if ids_a_supprimer:
        db.table("crushes").delete().in_("id", ids_a_supprimer).execute()
        print(f"❌ {len(ids_a_supprimer)} message(s) supprimé(s)")
    else:
        print("✅ RAS")

    return len(ids_a_supprimer)

# ── BOUCLE PRINCIPALE ────────────────────────────────────
debut = time.time()
total = 0
print("🛡️  Modérateur démarré")

while time.time() - debut < DUREE:
    total += scanner_et_supprimer()
    time.sleep(INTERVALLE)

print(f"⏹️  Arrêt propre — {total} message(s) supprimé(s) cette session")
