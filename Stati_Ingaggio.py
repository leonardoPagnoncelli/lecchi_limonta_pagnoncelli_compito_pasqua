#STATO, INGAGGIO, PROVVISTE, MERCI (LEO)
# Stati_Ingaggio.py
"""
Leo — Gestione di:
  - Struttura dati dello stato (crea_stato_iniziale → in nuovo_mondo.py)
  - Fase 1: Arruolamento della flotta
  - Fase 2: Acquisto provviste
  - Fase 3: Acquisto merci
  - Utility: stampa_risorse, conta_equipaggio, aggiungi_membro, etc.
"""

from termcolor import colored, cprint
import random
import time

# ==========================================
# COSTANTI
# ==========================================

COSTI_RUOLO = {
    "cuochi": 15,
    "marinai": 10,
    "meccanici": 15,
    "medici": 25,
    "navigatori": 20
}

NOMI_RUOLO = {
    "cuochi": "Cuoco",
    "marinai": "Marinaio",
    "meccanici": "Meccanico",
    "medici": "Medico",
    "navigatori": "Navigatore"
}

COSTI_SCORTE = {
    "verdura": 0.5,
    "frutta": 1.0,
    "carne": 2.0,
    "acqua": 0.5
}

CONSUMI_SETTIMANALI_PER_MEMBRO = {
    "verdura": 0.5,
    "frutta": 1.0,
    "carne": 1.0,
    "acqua": 0.5
}

# MERCI-1: CORREZIONE prezzi (TODO Giorno 1)
COSTI_MERCI = {
    "bottiglie_medicinale": 1,     # ← CORRETTO
    "armi": 5,                       # ← CORRETTO
    "sale": 0.5,                     # ← CORRETTO
    "stoffa": 2,                     # ← CORRETTO
    "coltelli": 0.5,                # ← CORRETTO
    "diamanti": 1                    # ← CORRETTO
}

# ==========================================
# UTILITY DI STAMPA
# ==========================================

def stampa_risorse(stato):
    """Mostra risorse correnti del giocatore."""
    ciurma_totale = sum(stato['equipaggio'].values())
    cprint(f"👥 Ciurma: {ciurma_totale} | 🪙 Budget: {stato['budget']:.0f} | 🥬 Verdura: {stato['scorte']['verdura']:.1f}kg | 🍊 Frutta: {stato['scorte']['frutta']:.1f}kg | 🥩 Carne: {stato['scorte']['carne']:.1f}kg | 💧 Acqua: {stato['scorte']['acqua']:.1f}brl", "cyan", attrs=["bold"])
    cprint(f"🛡️ Integrità: {stato.get('integrita', 100)}% | ⚠️ Punti Ammutinamento: {stato.get('punti_ammutinamento', 0)}", "magenta", attrs=["bold"])
    
    # Morale medio
    morali = list(stato.get('morale_individuale', {}).values())
    if morali:
        media_morale = sum(morali) / len(morali)
        colore_morale = "green" if media_morale > 60 else ("yellow" if media_morale > 30 else "red")
        cprint(f"❤️  Morale medio equipaggio: {media_morale:.0f}/100", colore_morale, attrs=["bold"])
    
    sett_percorse = stato.get('settimane_percorse', 0)
    if sett_percorse > 0:
        cprint(f"🗓️  Settimane percorse: {sett_percorse}", "dark_grey")

# ==========================================
# UTILITY EQUIPAGGIO
# ==========================================

def conta_equipaggio(stato):
    """Conta il totale di membri equipaggio."""
    return sum(stato['equipaggio'].values())

def aggiungi_membro(stato, ruolo, nome=None):
    """Aggiunge un membro con morale individuale."""
    stato['equipaggio'][ruolo] = stato['equipaggio'].get(ruolo, 0) + 1
    if nome is None:
        idx = sum(stato['equipaggio'].values())
        nome = f"{NOMI_RUOLO.get(ruolo, ruolo)}_{idx}"
    stato['morale_individuale'][nome] = 100
    return nome

def rimuovi_membro(stato, ruolo):
    """Rimuove il membro con morale più bassa del ruolo dato."""
    if stato['equipaggio'].get(ruolo, 0) > 0:
        stato['equipaggio'][ruolo] -= 1
        chiavi_ruolo = [k for k in stato['morale_individuale'] if k.startswith(NOMI_RUOLO.get(ruolo, ruolo))]
        if chiavi_ruolo:
            vittima = min(chiavi_ruolo, key=lambda k: stato['morale_individuale'][k])
            del stato['morale_individuale'][vittima]
            return vittima
    return None

# ==========================================
# GESTIONE SCORTE E CONSUMI
# ==========================================

def incrementa_settimane(stato, n=1):
    """Incrementa le settimane realmente percorse."""
    stato['settimane_percorse'] = stato.get('settimane_percorse', 0) + n

def consuma_scorte_dettagliate(stato, moltiplicatore=1.0):
    """TODO-05: consumi settimanali specifici per categoria."""
    # IMPORTA QUI PER EVITARE CICLI: Morale_Eventi
    import Morale_Eventi
    
    n = conta_equipaggio(stato)
    esaurite = []
    
    for cat, consumo_per_membro in CONSUMI_SETTIMANALI_PER_MEMBRO.items():
        # TODO-STATO-7: applica moltiplicatore da razioni_moltiplicatore
        fattore_razione = stato.get('razioni_moltiplicatore', {}).get(cat, 1.0)
        consumo = consumo_per_membro * n * moltiplicatore * fattore_razione
        stato['scorte'][cat] -= consumo
        if stato['scorte'][cat] < 0:
            esaurite.append(cat)
            stato['scorte'][cat] = 0

    if esaurite:
        for cat in esaurite:
            Morale_Eventi.varia_morale_tutti(stato, -10, f"scorte {cat} esaurite")
            Morale_Eventi.aggiungi_punti_ammutinamento(stato, 15, f"scorte {cat} esaurite")

    if stato.get('punti_ammutinamento', 0) >= 100:
        return "ammutinamento"

    if stato.get('integrita', 100) <= 0:
        return "affondato"

    if esaurite:
        return "scorte_esaurite"

    return "ok"

# ==========================================
# FASE 1: ARRUOLAMENTO
# ==========================================

def fase_arruolamento(stato, capitano):
    """TODO-01/02/03/05: esattamente 1 per ruolo obbligatorio, costi differenziati."""
    # IMPORTA QUI: nuovo_mondo per utility UI
    import nuovo_mondo
    
    ruoli_info = {
        "cuochi": ("🍲 Cuoco", 15),
        "marinai": ("🪢 Marinaio", 10),
        "meccanici": ("⚙️  Meccanico", 15),
        "medici": ("🩸 Medico", 25),
        "navigatori": ("🧭 Navigatore", 20),
    }
    RUOLI_OBBLIGATORI = list(ruoli_info.keys())

    while True:
        nuovo_mondo.pulisci_schermo()
        print()
        cprint("="*60, "green", attrs=["bold"])
        cprint("🍻 TAVERNA DEL PORTO - ARRUOLAMENTO (paga a fine viaggio)", "green", attrs=["bold"])
        nuovo_mondo.stampa_lenta("Devi ingaggiare ESATTAMENTE 1 persona per ogni ruolo prima di salpare.", "yellow")
        print()

        for i, (ruolo, (etichetta, costo)) in enumerate(ruoli_info.items(), 1):
            ingaggiato = stato['equipaggio'].get(ruolo, 0) > 0
            stato_str = colored("✅ INGAGGIATO", "green", attrs=["bold"]) if ingaggiato else colored(f"❌ {costo}🪙/sett (fine viaggio)", "red")
            print(f"  {i}. {etichetta:<22} {stato_str}")

        print()
        cprint(f"🪙 Budget attuale: {stato['budget']:.0f}", "cyan")
        # INGAGGIO-1: Aggiungi controllo limite 16 persone
        ciurma_tot = conta_equipaggio(stato)
        cprint(f"👥 Equipaggio attuale: {ciurma_tot}/16", "cyan")

        print()

        tutti_obbligatori = all(stato['equipaggio'].get(r, 0) >= 1 for r in RUOLI_OBBLIGATORI)
        mancanti = [r for r in RUOLI_OBBLIGATORI if stato['equipaggio'].get(r, 0) == 0]

        if tutti_obbligatori:
            cprint("✅ Tutti i ruoli coperti! Puoi salpare.", "green", attrs=["bold"])
            print(colored("\n  0.", "red", attrs=["bold"]) + " 🚢 SALPA! (Termina Arruolamento)")
        else:
            cprint(f"⚠️   Mancano ancora: {', '.join(NOMI_RUOLO[r] for r in mancanti)}", "yellow", attrs=["bold"])
            print(colored("\n  0.", "dark_grey") + " 🚢 Salpa (NON disponibile - ingaggia prima tutti i ruoli)")

        if ciurma_tot < 16:  # INGAGGIO-1: permetti solo se sotto il limite
            print(colored("  6.", "magenta") + " 🪢 Ingaggia Marinaio Extra (supporto in combattimento)")
        else:
            print(colored("  6.", "dark_grey") + " 🪢 Limite equipaggio raggiunto (16/16)")

        scelta = nuovo_mondo.chiedi_scelta(colored("\n👉 Scegli (0-6): ", "magenta", attrs=["bold"]), ['0','1','2','3','4','5','6'])

        if scelta == "0":
            if not tutti_obbligatori:
                cprint(f"\n🚫 IMPOSSIBILE SALPARE! Mancano: {', '.join(NOMI_RUOLO[r] for r in mancanti)}", "red", attrs=["bold"])
                nuovo_mondo.stampa_lenta("Devi ingaggiare almeno un membro per ogni ruolo.", "red")
                time.sleep(2)
                continue
            break

        ruoli_lista = list(ruoli_info.keys())
        if scelta in ['1','2','3','4','5']:
            idx = int(scelta) - 1
            ruolo_scelto = ruoli_lista[idx]
            etichetta, costo_sett = ruoli_info[ruolo_scelto]

            if stato['equipaggio'].get(ruolo_scelto, 0) > 0:
                cprint(f"\n❌ Hai già un {NOMI_RUOLO[ruolo_scelto]}! Ogni ruolo richiede esattamente 1 membro.", "red")
                time.sleep(1.5)
                continue

            nome = aggiungi_membro(stato, ruolo_scelto)
            stato['debito_equipaggio'] = stato.get('debito_equipaggio', 0) + costo_sett
            stato['costo_sett_ruolo'] = stato.get('costo_sett_ruolo', {})
            stato['costo_sett_ruolo'][ruolo_scelto] = stato['costo_sett_ruolo'].get(ruolo_scelto, 0) + costo_sett
            nuovo_mondo.stampa_lenta(f"  ✍️  {etichetta} ingaggiato! ({costo_sett}🪙/sett — paghi a fine viaggio).", "green")
            time.sleep(0.8)

        elif scelta == '6':
            # INGAGGIO-1: controlla il limite
            if conta_equipaggio(stato) >= 16:
                cprint(f"\n❌ Limite equipaggio raggiunto (16/16)! Non puoi aggiungere altri marinai.", "red")
                time.sleep(1.5)
                continue
            
            costo_sett = ruoli_info['marinai'][1]
            aggiungi_membro(stato, 'marinai')
            stato['debito_equipaggio'] = stato.get('debito_equipaggio', 0) + costo_sett
            stato['costo_sett_ruolo'] = stato.get('costo_sett_ruolo', {})
            stato['costo_sett_ruolo']['marinai'] = stato['costo_sett_ruolo'].get('marinai', 0) + costo_sett
            nuovo_mondo.stampa_lenta(f"  ✍️  Marinaio extra ingaggiato! ({costo_sett}🪙/sett — paghi a fine viaggio).", "green")
            time.sleep(0.8)

    if conta_equipaggio(stato) == 0:
        import Arrivo_GameOver
        return Arrivo_GameOver.game_over("Senza ciurma, i creditori ti raggiungono sul molo. Fine.", stato, capitano)
    return True

# ==========================================
# FASE 2: ACQUISTO PROVVISTE
# ==========================================

def fase_acquisto_provviste(stato, capitano):
    """TODO-04/05/06: 4 categorie, consumi specifici, dimezzamento/raddoppio razioni."""
    import nuovo_mondo
    
    nuovo_mondo.pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🏪 --- MERCATO DEL PORTO (PROVVISTE) ---", "green", attrs=["bold"])
    nuovo_mondo.stampa_lenta("Scegli bene le scorte. Ogni membro consuma ogni settimana:", "cyan")
    print()
    print(f"  🥬 Verdura:  {CONSUMI_SETTIMANALI_PER_MEMBRO['verdura']} kg/membro/sett  → {COSTI_SCORTE['verdura']}🪙/kg")
    print(f"  🍊 Frutta:   {CONSUMI_SETTIMANALI_PER_MEMBRO['frutta']} kg/membro/sett  → {COSTI_SCORTE['frutta']}🪙/kg")
    print(f"  🥩 Carne:    {CONSUMI_SETTIMANALI_PER_MEMBRO['carne']} kg/membro/sett  → {COSTI_SCORTE['carne']}🪙/kg")
    print(f"  💧 Acqua:    {CONSUMI_SETTIMANALI_PER_MEMBRO['acqua']} brl/membro/sett → {COSTI_SCORTE['acqua']}🪙/brl")
    print()
    n_eq = conta_equipaggio(stato)
    cprint(f"👥 Equipaggio: {n_eq} | 🪙 Budget: {stato['budget']:.0f}", "cyan", attrs=["bold"])
    print()

    simboli = {"verdura": "🥬", "frutta": "🍊", "carne": "🥩", "acqua": "💧"}
    unita = {"verdura": "kg", "frutta": "kg", "carne": "kg", "acqua": "barili"}

    costo_totale = 0
    for cat in ["verdura", "frutta", "carne", "acqua"]:
        n_suggerito = CONSUMI_SETTIMANALI_PER_MEMBRO[cat] * n_eq * 10
        costo_suggerito = n_suggerito * COSTI_SCORTE[cat]
        while True:
            try:
                prompt = colored(
                    f"{simboli[cat]} {cat.capitalize()} ({COSTI_SCORTE[cat]}🪙/{unita[cat]}) "
                    f"[suggerito: {n_suggerito:.1f} = {costo_suggerito:.0f}🪙 | budget rimasto: {stato['budget'] - costo_totale:.0f}🪙]: ",
                    "yellow", attrs=["bold"]
                )
                qty_str = nuovo_mondo.leggi_input(prompt)
                qty = float(qty_str) if qty_str.strip() else n_suggerito
                if qty < 0:
                    raise ValueError("quantità negativa")
                costo = qty * COSTI_SCORTE[cat]
                if costo_totale + costo > stato['budget']:
                    cprint(f"❌ Non hai abbastanza budget! Budget rimasto: {stato['budget'] - costo_totale:.0f}🪙", "red")
                    continue
                stato['scorte'][cat] = qty
                costo_totale += costo
                break
            except ValueError:
                cprint("❌ Inserisci un numero valido.", "red")

    stato['budget'] -= costo_totale
    cprint(f"\n✅ Scorte caricate! Spesi {costo_totale:.0f}🪙 | Budget rimasto: {stato['budget']:.0f}🪙", "green", attrs=["bold"])

    # TODO-06: Step 2 — gestione razioni
    print()
    cprint("─"*60, "yellow")
    cprint("📋 FASE 2 - GESTIONE RAZIONI INIZIALI", "yellow", attrs=["bold"])
    nuovo_mondo.stampa_lenta("Puoi regolare le razioni per categoria (influenza morale e ammutinamento).", "cyan")
    print(f"  Dimezzare:   -5 morale, +30 punti ammutinamento")
    print(f"  Raddoppiare: +5 morale (richiede budget extra)")
    print()

    # IMPORTA QUI per evitare cicli
    import Morale_Eventi

    for cat in ["verdura", "frutta", "carne", "acqua"]:
        scelta_razione = nuovo_mondo.chiedi_scelta(
            colored(f"{simboli[cat]} {cat.capitalize()} ({stato['scorte'][cat]:.1f} {unita[cat]}): [N] Normale | [D] Dimezza | [R] Raddoppia: ", "magenta"),
            ['N', 'D', 'R']
        )
        if scelta_razione == 'D':
            # TODO-STATO-7: aggiorna moltiplicatore invece di scorte dirette
            stato['razioni_moltiplicatore'][cat] *= 0.5
            Morale_Eventi.varia_morale_tutti(stato, -5, f"razioni {cat} dimezzate")
            Morale_Eventi.aggiungi_punti_ammutinamento(stato, 30, "razioni ridotte")
        elif scelta_razione == 'R':
            costo_extra = stato['scorte'][cat] * COSTI_SCORTE[cat]
            if stato['budget'] >= costo_extra:
                stato['razioni_moltiplicatore'][cat] *= 2.0
                stato['budget'] -= costo_extra
                Morale_Eventi.varia_morale_tutti(stato, +5, f"razioni {cat} raddoppiate")
                cprint(f"  💰 Spesi {costo_extra:.0f}🪙 per raddoppiare {cat} | Budget: {stato['budget']:.0f}🪙", "yellow")
            else:
                cprint(f"  ❌ Budget insufficiente ({costo_extra:.0f}🪙 necessari, hai {stato['budget']:.0f}🪙). Razioni rimaste normali.", "red")

    # TODO: Lecchi EPILOGO-4 traccia spese
    stato['spese_iniziali'] = stato['spese_iniziali'] + costo_totale

    time.sleep(1.5)
    return True

# ==========================================
# FASE 3: ACQUISTO MERCI
# ==========================================

def fase_merci_arsenale(stato, capitano):
    """TODO-07/08: MERCI-1 corretti, 6 tipi, niente legno/carpentiere."""
    import nuovo_mondo
    
    nuovo_mondo.pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("⚔️  --- L'ARSENALE E IL MERCATO DELLE MERCI ---", "green", attrs=["bold"])
    nuovo_mondo.stampa_lenta("Equipaggia la nave con armi e merci da barattare nel Nuovo Mondo.", "cyan")
    nuovo_mondo.stampa_lenta("Le bottiglie di medicinale curano le epidemie. Le armi difendono dai pirati.", "yellow")
    print()

    catalogo_merci = {
        "bottiglie_medicinale": ("💊 Bottiglie Medicinale", COSTI_MERCI["bottiglie_medicinale"]),
        "armi":                 ("⚔️  Armi", COSTI_MERCI["armi"]),
        "sale":                 ("🧂 Sale", COSTI_MERCI["sale"]),
        "stoffa":               ("🧵 Stoffa", COSTI_MERCI["stoffa"]),
        "coltelli":             ("🔪 Coltelli", COSTI_MERCI["coltelli"]),
        "diamanti":             ("💎 Diamanti", COSTI_MERCI["diamanti"]),
    }

    cprint(f"🪙 Budget disponibile: {stato['budget']:.0f}", "cyan", attrs=["bold"])
    print()

    for codice, (nome, costo) in catalogo_merci.items():
        if stato['budget'] < costo:
            cprint(f"  ❌ {nome} ({costo}🪙) - Budget insufficiente", "dark_grey")
            continue
        while True:
            try:
                qty_str = nuovo_mondo.leggi_input(colored(f"  {nome} ({costo}🪙/unità) [Budget: {stato['budget']:.0f}🪙] Quante? [0=nessuna]: ", "yellow"))
                qty = int(qty_str) if qty_str.strip() else 0
                if qty < 0:
                    raise ValueError
                costo_tot = qty * costo
                if costo_tot > stato['budget']:
                    cprint(f"  ❌ Non hai abbastanza budget! ({stato['budget']:.0f}🪙 rimasti)", "red")
                    continue
                stato['merci'][codice] = stato['merci'].get(codice, 0) + qty
                if qty > 0:
                    stato['budget'] -= costo_tot
                    cprint(f"  ✅ Acquistato {qty}x {nome} per {costo_tot}🪙 | Rimasto: {stato['budget']:.0f}🪙", "green")
                break
            except ValueError:
                cprint("  ❌ Numero non valido.", "red")

    if stato['merci'].get('armi', 0) == 0:
        nuovo_mondo.stampa_lenta("\n⚠️  Nessuna arma! Sarete vulnerabili agli attacchi dei pirati.", "yellow", attrs=["bold"])

    # TODO: Lecchi EPILOGO-4 traccia spese
    costo_merci_tot = sum(stato['merci'].get(m, 0) * COSTI_MERCI.get(m, 0) for m in catalogo_merci.keys())
    stato['spese_iniziali'] = stato['spese_iniziali'] + costo_merci_tot

    cprint(f"\n🪙 Budget rimasto: {stato['budget']:.0f}", "cyan", attrs=["bold"])
    time.sleep(1.5)
    return True