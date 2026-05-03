#MORALE, EVENTI, VIAGGIO (SARA)
# Morale_Eventi.py
"""
Sara — Gestione di:
  - Sistema del morale (varia_morale_tutti, controlla_morti_morale_zero)
  - Viaggio: Step 1 (Evento casuale), Step 5 (Ammutinamento), Step 6 (Rallentamento)
  - 15 Eventi casualmente triggerati (Uomo in mare, Pesca, Tempesta, etc.)
  - Albatro con max 3 apparizioni e logica completa
  - TODO: Step 2 (controllo scorte interattivo) e Step 5 (calcolo ammutinamento preciso)
"""

from termcolor import colored, cprint
import random
import time

# ==========================================
# UTILITY MORALE
# ==========================================

def varia_morale_tutti(stato, delta, motivo=""):
    """Varia morale di tutti i membri."""
    # IMPORTA QUI per evitare cicli
    import Stati_Ingaggio
    
    for k in stato['morale_individuale']:
        stato['morale_individuale'][k] = max(0, min(100, stato['morale_individuale'][k] + delta))
    if motivo:
        import nuovo_mondo
        segno = "📈" if delta > 0 else "📉"
        nuovo_mondo.variazione_stat(f"{segno} Morale {'+' if delta>0 else ''}{delta} ({motivo})", "green" if delta > 0 else "red")
    controlla_morti_morale_zero(stato)

def controlla_morti_morale_zero(stato):
    """TODO-11: morte automatica membri con morale = 0."""
    import Stati_Ingaggio
    
    morti = [k for k, v in list(stato['morale_individuale'].items()) if v <= 0]
    for morto in morti:
        del stato['morale_individuale'][morto]
        for ruolo, nome_singolo in Stati_Ingaggio.NOMI_RUOLO.items():
            if morto.startswith(nome_singolo):
                stato['equipaggio'][ruolo] = max(0, stato['equipaggio'].get(ruolo, 0) - 1)
                cprint(f"  💀 {morto} è morto per morale a zero!", "red", attrs=["bold"])
                break

def equipaggio_basso_morale(stato, soglia=30):
    """TODO-12: controlla se più della metà ha morale ≤ soglia."""
    morali = list(stato['morale_individuale'].values())
    if not morali:
        return False
    bassi = sum(1 for m in morali if m <= soglia)
    return bassi > len(morali) / 2

# ==========================================
# AMMUTINAMENTO (TODO: riscrivere Sara Giorno 4)
# ==========================================

def aggiungi_punti_ammutinamento(stato, punti, motivo=""):
    """TODO-13: aggiunge punti ammutinamento con log."""
    import nuovo_mondo
    stato['punti_ammutinamento'] = stato.get('punti_ammutinamento', 0) + punti
    if motivo:
        nuovo_mondo.variazione_stat(f"⚠️  +{punti} punti ammutinamento ({motivo})", "red")

# ==========================================
# EVENTI UNICI E RIPETIBILI
# ==========================================

def evento_uomo_in_mare(stato):
    """TODO-16."""
    import nuovo_mondo
    import Stati_Ingaggio
    
    nuovo_mondo.stampa_lenta("🌊 UOMO IN MARE! Un'onda gigantesca spazza il ponte senza preavviso.", "red", attrs=["bold"])
    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
    if ruoli_vivi:
        ruolo = random.choice(ruoli_vivi)
        vittima = Stati_Ingaggio.rimuovi_membro(stato, ruolo)
        varia_morale_tutti(stato, -15, "collega caduto in mare")
        nuovo_mondo.variazione_stat(f"💀 Hai perso {vittima or '1 membro'}!", "red")
        aggiungi_punti_ammutinamento(stato, 10, "morte in mare")
    else:
        nuovo_mondo.stampa_lenta("Miracolosamente, nessuno cade.", "green")

def evento_perdita_scorte(stato):
    """TODO-17: Verdura/Frutta/Carne/Acqua in mare (DA SEPARARE in 4 eventi - Sara Giorno 2)."""
    import nuovo_mondo
    
    categorie = ["verdura", "frutta", "carne", "acqua"]
    cat = random.choice(categorie)
    simboli = {"verdura": "🥬", "frutta": "🍊", "carne": "🥩", "acqua": "💧"}
    quantita = random.uniform(5, 15)
    stato['scorte'][cat] = max(0, stato['scorte'][cat] - quantita)
    nuovo_mondo.stampa_lenta(f"🌊 Un'onda scellerata trascina in mare {quantita:.1f} unità di {cat}!", "red")
    nuovo_mondo.variazione_stat(f"📉 -{quantita:.1f} {simboli[cat]} {cat.capitalize()}", "red")
    varia_morale_tutti(stato, -5, f"perdita {cat}")

def evento_pesca_miracolosa(stato):
    """TODO-18."""
    import nuovo_mondo
    
    nuovo_mondo.stampa_lenta("🎣 Un banco di pesci enormi circonda la nave. Pesca miracolosa!", "green", attrs=["bold"])
    carne_guadagnata = random.uniform(8, 20)
    stato['scorte']['carne'] += carne_guadagnata
    nuovo_mondo.variazione_stat(f"📈 +{carne_guadagnata:.1f} 🥩 Carne (pesca)", "green")
    varia_morale_tutti(stato, +5, "pesca miracolosa")

def evento_tempesta_miracolosa(stato):
    """TODO-19: guarisce malati, riempie cisterne."""
    import nuovo_mondo
    
    nuovo_mondo.stampa_lenta("⛈️ Una tempesta provvidenziale! La pioggia riempie ogni contenitore e lava i malati.", "cyan", attrs=["bold"])
    acqua_guadagnata = random.uniform(10, 25)
    stato['scorte']['acqua'] += acqua_guadagnata
    varia_morale_tutti(stato, +15, "tempesta miracolosa")
    nuovo_mondo.variazione_stat(f"📈 +{acqua_guadagnata:.1f} 💧 Acqua", "green")

def evento_venti_favorevoli(stato):
    """TODO-20: accorcia viaggio di 1 sett, +morale casuale (TODO-MORALE-2: random.randint(5,15) Giorno 1)."""
    import nuovo_mondo
    
    nuovo_mondo.stampa_lenta("💨 VENTI FAVOREVOLI! Le vele si gonfiano al massimo. Avanzate di settimane in giorni!", "green", attrs=["bold"])
    stato['settimane_risparmiate'] = stato.get('settimane_risparmiate', 0) + 1
    # TODO-MORALE-2: correggere range di random
    bonus = random.randint(5, 15)  # ← CORRETTO (da random.choice)
    varia_morale_tutti(stato, bonus, f"venti favorevoli (+{bonus})")
    nuovo_mondo.variazione_stat("📈 Viaggio accorciato di 1 settimana!", "green")

# ← TODO Sara: aggiungere EVT-I, EVT-J, EVT-K corretti
# ← TODO Sara: aggiungere ALBATRO-1/2/3 con logica completa
# ← TODO Sara: aggiungere SCIALUPPA-2/3 corretti
# ← TODO Sara: aggiungere EPIDEMIA-1/2/3 riscritta
# ← TODO Sara: aggiungere PIRATA-1/2/3/4 riscritta
# ← TODO Sara: aggiungere TIMONE-1/2 corretti
# ← TODO Sara: aggiungere VENTO-1/2 corretti
# ← TODO Sara: aggiungere ISOLA-1/2/3/4 riscritta

EVENTI_UNICI = {
    "uomo_in_mare": evento_uomo_in_mare,
    "perdita_scorte": evento_perdita_scorte,
    # TODO: aggiungere altri 6 eventi unici
}

EVENTI_RIPETIBILI = {
    "pesca_miracolosa": evento_pesca_miracolosa,
    "tempesta_miracolosa": evento_tempesta_miracolosa,
    "venti_favorevoli": evento_venti_favorevoli,
    # TODO: aggiungere altri 5 eventi ripetibili
}

def gestisci_evento_casuale(stato):
    """Orchestra selezione e trigger eventi."""
    import nuovo_mondo
    
    cprint("\n" + "~"*60, "blue", attrs=["bold"])
    cprint("⚠️   EVENTO IN MARE!", "yellow", attrs=["bold", "blink"])

    eventi_accaduti = stato.get('eventi_accaduti', [])

    # Filtra albatro se già 3 volte
    if stato.get('avvistamenti_albatro', 0) >= 3:
        eventi_ripetibili_filtrati = {k: v for k, v in EVENTI_RIPETIBILI.items() if k != 'albatro'}
    else:
        eventi_ripetibili_filtrati = EVENTI_RIPETIBILI

    # Filtra eventi unici già accaduti
    eventi_unici_disponibili = {k: v for k, v in EVENTI_UNICI.items() if k not in eventi_accaduti}

    pool_ripetibili = list(eventi_ripetibili_filtrati.values())
    pool_unici = list(eventi_unici_disponibili.items())

    # 50% chance evento unico se disponibili
    if pool_unici and random.random() < 0.5:
        nome_ev, funzione_ev = random.choice(pool_unici)
        eventi_accaduti.append(nome_ev)
        stato['eventi_accaduti'] = eventi_accaduti
        funzione_ev(stato)
    elif pool_ripetibili:
        random.choice(pool_ripetibili)(stato)
    else:
        nuovo_mondo.stampa_lenta("🌅 Il mare è calmo. Nessun imprevisto questa settimana.", "cyan")

    cprint("~"*60, "blue", attrs=["bold"])