# Arrivo_GameOver.py
"""
Lecchi — Gestione di:
  - Step 4: Riepilogo fine settimana (TODO Giorno 1)
  - Arrivo nel Nuovo Mondo e interazione con indigeni
  - Baratto delle merci
  - Evento tradimento
  - Epilogo: profitti, asta nave, finali
  - Game over e condizioni di sconfitta
"""

from termcolor import colored, cprint
import random
import time
import json
import os

# ==========================================
# GAME OVER
# ==========================================

def game_over(messaggio, stato, capitano):
    """Termina la partita con sconfitta."""
    import nuovo_mondo
    
    dati = nuovo_mondo.carica_dati()
    dati["stats"]["morti"] += 1
    nuovo_mondo.salva_dati(dati)
    print()
    cprint("="*60, "red", attrs=["bold"])
    import nuovo_mondo
    nuovo_mondo.stampa_lenta(messaggio, "red")
    cprint("\n💀 === GAME OVER === 💀\n", "red", attrs=["bold", "blink"])
    cprint("="*60, "red", attrs=["bold"])
    nuovo_mondo.archivia_partita(capitano, stato, "Morto in mare")
    return False

# ==========================================
# ARRIVO NEL NUOVO MONDO
# ==========================================

def arrivo_nuovo_mondo(stato, capitano):
    """TODO-36/37: indigeni armati, scelta far fuoco / contrattare / furto."""
    import nuovo_mondo
    import Stati_Ingaggio
    
    nuovo_mondo.pulisci_schermo()
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])
    nuovo_mondo.stampa_lenta(" TERRA IN VISTA! Il Nuovo Mondo emerge tra la nebbia mattutina.", "green", ["bold"])
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])

    nuovo_mondo.stampa_lenta("La barca tocca la spiaggia. Silenzio assordante.", "yellow")
    nuovo_mondo.stampa_lenta("Poi... centinaia di guerrieri emergono dalla foresta, dipinti di ocra rossa.", "red", attrs=["bold"])

    albatro_ucciso = stato.get('albatro_ucciso', False)
    if albatro_ucciso:
        nuovo_mondo.stampa_lenta("⚠️  Gli sciamani agitano le lance — come se sapessero della vostra colpa verso l'albatro!", "red", attrs=["bold"])
        aggressivita_bonus = 3
    else:
        aggressivita_bonus = 0

    nuovo_mondo.stampa_lenta("Dietro di loro, enormi ceste di perle, manufatti e spezie. Ricchezza immensa.", "yellow", ["bold"])

    # ARRIVO-1: Controllo armi prima di mostrare opzione F
    opzioni_disponibili = ['C', 'N']
    if stato['merci'].get('armi', 0) > 0:
        opzioni_disponibili.insert(0, 'F')
        prompt = colored("\n👉 I tamburi battono. [F] FAI FUOCO | [C] Contratta | [N] Furto notturno: ", "magenta", attrs=["bold"])
    else:
        prompt = colored("\n👉 I tamburi battono. [C] Contratta | [N] Furto notturno: ", "magenta", attrs=["bold"])
        nuovo_mondo.stampa_lenta("⚠️  (Senza armi, non puoi aprire il fuoco)", "yellow")
    
    scelta = nuovo_mondo.chiedi_scelta(prompt, opzioni_disponibili)

    if scelta == 'F':
        nuovo_mondo.stampa_lenta("💥 'FUOCO A VOLONTÀ!'", "red", attrs=["bold", "blink"])
        nuovo_mondo.stampa_lenta("Un attimo di silenzio... poi migliaia di frecce avvelenate oscurano il sole.", "red")
        nuovo_mondo.stampa_lenta("Siete sopraffatti in secondi. Nessun sopravvissuto.", "red", attrs=["bold"])
        return game_over("Avete provocato un massacro. Il Nuovo Mondo vi uccide tutti.", stato, capitano)

    elif scelta == 'C':
        nuovo_mondo.stampa_lenta("🤝 Avanzate lentamente, mani aperte. Offrite i doni.", "cyan")
        tiro = random.randint(1, 10) + stato['equipaggio'].get('navigatori', 0) - aggressivita_bonus
        if tiro >= 5:
            nuovo_mondo.stampa_lenta("✨ Il capo tribù accetta! Inizia il baratto.", "green", attrs=["bold"])
            return fase_baratto(stato, capitano)
        else:
            nuovo_mondo.stampa_lenta("🩸 Un malinteso! Un guerriero scaglia la lancia. Fuggite!", "red", attrs=["bold"])
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            vittime = 2 + aggressivita_bonus
            for _ in range(vittime):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    Stati_Ingaggio.rimuovi_membro(stato, ruolo)
                    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            import Morale_Eventi
            Morale_Eventi.varia_morale_tutti(stato, -20, "contrattazione fallita")
            nuovo_mondo.stampa_lenta("⚠️  Non avete ottenuto nulla. Dovete ripartire senza merci.", "red")
            return True

    elif scelta == 'N':
        nuovo_mondo.stampa_lenta("🌙 Attendete la notte profonda...", "cyan")
        n_marinai = stato['equipaggio'].get('marinai', 0)
        n_nav = stato['equipaggio'].get('navigatori', 0)
        tiro = random.randint(1, 10) + n_marinai + n_nav - aggressivita_bonus
        if tiro >= 8:
            nuovo_mondo.stampa_lenta("🥷 Come ombre nella notte, vi infiltrate nel villaggio. Un successo perfetto!", "green", attrs=["bold"])
            perle_rubate = random.randint(5, 15)
            stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + perle_rubate
            nuovo_mondo.variazione_stat(f"📈 +{perle_rubate} 🔮 Perle rubate", "green")
            return True
        else:
            nuovo_mondo.stampa_lenta("🚨 Una trappola! Torce ovunque. Fuggite nel sangue!", "red", attrs=["bold"])
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            vittime = 3 + aggressivita_bonus
            for _ in range(vittime):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    Stati_Ingaggio.rimuovi_membro(stato, ruolo)
                    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            import Morale_Eventi
            Morale_Eventi.varia_morale_tutti(stato, -30, "furto fallito")
            Morale_Eventi.aggiungi_punti_ammutinamento(stato, 20, "raid fallito")
            return True

# ==========================================
# BARATTO
# ==========================================

def fase_baratto(stato, capitano):
    """TODO-38/39/40: BARATTO-2 con tassi esatti, BARATTO-3 con profitto stimato."""
    import nuovo_mondo
    
    nuovo_mondo.pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🤝 --- GRANDE BARATTO NEL NUOVO MONDO ---", "green", attrs=["bold"])
    nuovo_mondo.stampa_lenta("Il capo tribù siede sul trono di conchiglie. È tempo di trattare.", "cyan")
    print()

    # TODO-BARATTO-2: Tassi esatti dalle specifiche (invertiti)
    tabelle_baratto = {
        "sale": [
            ("perle",     1/0.5, "🔮", 2),      # qty/0.5 perle, valore 2 per perla
            ("manufatti", 1/0.5, "🗿", 2),      # qty/0.5 manufatti, valore 2 per manufatto
            ("spezie",    1/1, "🌶️", 1),         # qty/1 spezie, valore 1 per spezia
        ],
        "stoffa": [
            ("perle",     1/5, "🔮", 2),
            ("manufatti", 1/7, "🗿", 2),
            ("spezie",    1/3, "🌶️", 1),
        ],
        "coltelli": [
            ("perle",     1/1, "🔮", 2),
            ("manufatti", 1/3, "🗿", 2),
            ("spezie",    1/6, "🌶️", 1),
        ],
        "diamanti": [
            ("perle",     1/2, "🔮", 2),
            ("manufatti", 1/4, "🗿", 2),
            ("spezie",    1/4, "🌶️", 1),
        ],
    }

    merci_barattabili = {k: v for k, v in stato['merci'].items() if k in tabelle_baratto and v > 0}

    if not merci_barattabili:
        nuovo_mondo.stampa_lenta("❌ Non hai merci barattabili! Il capo tribù ti congeda deluso.", "red", attrs=["bold"])
        return True

    stato.setdefault('barattato', {"sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0})

    for merce, quantita in merci_barattabili.items():
        if quantita <= 0:
            continue
        nuovo_mondo.pulisci_schermo()
        cprint(f"🔄 Baratto: {merce.upper()} (hai {quantita} unità)", "yellow", attrs=["bold"])
        print()

        offerte = tabelle_baratto[merce]
        for i, (cosa, tasso, simbolo, valore_base) in enumerate(offerte, 1):
            guadagno_stimato_merci = quantita * tasso
            guadagno_stimato_monete = guadagno_stimato_merci * valore_base
            print(f"  {i}. {simbolo} {cosa.capitalize():<12} → {tasso:.1f} {cosa.split('[')[0]}/unità → ~{guadagno_stimato_monete:.0f}🪙 di valore")
        print(f"  0. Salta (non barattare {merce})")
        print()

        scelta_offerta = nuovo_mondo.chiedi_scelta(
            colored(f"👉 Quale offerta scegli? (0-{len(offerte)}): ", "magenta", attrs=["bold"]),
            ['0'] + [str(i) for i in range(1, len(offerte)+1)]
        )

        if scelta_offerta == '0':
            continue

        idx = int(scelta_offerta) - 1
        cosa, tasso, simbolo, valore_base = offerte[idx]

        while True:
            try:
                qty_str = nuovo_mondo.leggi_input(colored(f"  Quante unità di {merce} vuoi barattare? (max {quantita}): ", "yellow"))
                qty = int(qty_str) if qty_str.strip() else 0
                if qty < 0 or qty > quantita:
                    cprint(f"  ❌ Quantità non valida (0-{int(quantita)})", "red")
                    continue
                break
            except ValueError:
                cprint("  ❌ Numero non valido.", "red")

        if qty > 0:
            guadagno = qty * tasso
            guadagno_monete = guadagno * valore_base
            stato['merci'][merce] -= qty
            stato['barattato'][merce] = stato['barattato'].get(merce, 0) + qty
            stato['risorse_baratto'][cosa] = stato['risorse_baratto'].get(cosa, 0) + guadagno
            cprint(f"  ✅ Barattato {qty}x {merce} → +{guadagno:.1f} {simbolo} {cosa} (~{guadagno_monete:.0f}🪙)", "green", attrs=["bold"])
            time.sleep(0.8)

    evento_tradimento(stato)

    print()
    cprint("📊 RIEPILOGO BARATTO:", "cyan", attrs=["bold"])
    for risorsa, qty in stato['risorse_baratto'].items():
        if qty > 0:
            simboli_r = {"perle": "🔮", "manufatti": "🗿", "spezie": "🌶️"}
            print(f"  {simboli_r.get(risorsa,'')} {risorsa.capitalize()}: {qty:.1f}")

    time.sleep(2)
    return True

# ==========================================
# TRADIMENTO
# ==========================================

def evento_tradimento(stato):
    """TODO-41/42: TRADIMENTO-2/3 con logica albatro esatta."""
    import nuovo_mondo
    
    if stato['merci'].get('armi', 0) <= 0:
        return

    nuovo_mondo.stampa_lenta("\n🌑 Un guerriero si avvicina di notte, con uno sguardo losco.", "yellow")
    nuovo_mondo.stampa_lenta("Sussurra: 'Il rivale del capo... offre 30 perle per ogni arma. In segreto.'", "red")

    scelta = nuovo_mondo.chiedi_scelta(
        colored("👉 [A] Accetta il tradimento | [R] Rifiuta: ", "magenta", attrs=["bold"]),
        ['A', 'R']
    )

    if scelta == 'A':
        # TODO-TRADIMENTO-2: logica albatro esatta
        albatro_ucciso = stato.get('albatro_ucciso', False)
        avvistamenti = stato.get('avvistamenti_albatro', 0)
        
        if avvistamenti > 0 and albatro_ucciso:
            # Caso 3: albatro ucciso → sempre scoperto
            nuovo_mondo.stampa_lenta("☠️  La maledizione dell'albatro vi tradisce!", "red", attrs=["bold"])
            # TODO-GAMEOVER-7: questo NON è game over nel codice, ma dovrebbe essere
            # Per ora implementiamo come nel codice originale, ma segnaliamo il TODO
            armi_confiscate = stato['merci']['armi']
            stato['merci']['armi'] = 0
            import Stati_Ingaggio
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            for _ in range(min(3, Stati_Ingaggio.conta_equipaggio(stato))):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    Stati_Ingaggio.rimuovi_membro(stato, ruolo)
                    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            import Morale_Eventi
            Morale_Eventi.varia_morale_tutti(stato, -30, "tradimento scoperto")
            Morale_Eventi.aggiungi_punti_ammutinamento(stato, 40, "disonore del tradimento")
            nuovo_mondo.variazione_stat(f"📉 -{armi_confiscate} armi confiscate", "red")
            # TODO-GAMEOVER-7: dovrebbe essere game_over() qui
        elif avvistamenti > 0 and not albatro_ucciso:
            # Caso 1: albatro vivo → sempre franca
            nuovo_mondo.stampa_lenta("🕊️ L'albatro vi protegge! Il tradimento riesce.", "green", attrs=["bold"])
            armi_vendute = min(stato['merci']['armi'], 3)
            stato['merci']['armi'] -= armi_vendute
            guadagno = armi_vendute * 30
            stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + guadagno
            nuovo_mondo.stampa_lenta(f"💰 Il tradimento riesce! +{guadagno} 🔮 perle (vendute {armi_vendute} armi).", "green", attrs=["bold"])
        else:
            # Caso 2: nessun avvistamento → 50% scoperto
            if random.random() < 0.5:
                nuovo_mondo.stampa_lenta("🚨 SIETE SCOPERTI! Il capo tribù urla vendetta!", "red", attrs=["bold"])
                armi_confiscate = stato['merci']['armi']
                stato['merci']['armi'] = 0
                import Stati_Ingaggio
                ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
                for _ in range(min(3, Stati_Ingaggio.conta_equipaggio(stato))):
                    if ruoli_vivi:
                        ruolo = random.choice(ruoli_vivi)
                        Stati_Ingaggio.rimuovi_membro(stato, ruolo)
                        ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
                import Morale_Eventi
                Morale_Eventi.varia_morale_tutti(stato, -30, "tradimento scoperto")
                Morale_Eventi.aggiungi_punti_ammutinamento(stato, 40, "disonore del tradimento")
                nuovo_mondo.variazione_stat(f"📉 -{armi_confiscate} armi confiscate", "red")
            else:
                armi_vendute = min(stato['merci']['armi'], 3)
                stato['merci']['armi'] -= armi_vendute
                guadagno = armi_vendute * 30
                stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + guadagno
                nuovo_mondo.stampa_lenta(f"💰 Il tradimento riesce! +{guadagno} 🔮 perle (vendute {armi_vendute} armi).", "green", attrs=["bold"])
    else:
        # TODO-TRADIMENTO-3: bonus perle capo tribù se rifiuta
        if stato.get('albatro_ucciso', False):
            bonus = random.randint(5, 20)
            nuovo_mondo.stampa_lenta(f"🌙 La maledizione rende il capo tribù pietoso. Offre {bonus} perle di ringraziamento.", "yellow")
        else:
            bonus = random.randint(30, 50)
            nuovo_mondo.stampa_lenta(f"🤝 Il capo tribù, grato per la lealtà, offre {bonus} perle di ringraziamento.", "cyan", attrs=["bold"])
        
        stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + bonus
        nuovo_mondo.variazione_stat(f"📈 +{bonus} 🔮 Perle (ringraziamento)", "green")

# ==========================================
# EPILOGO E FINALE
# ==========================================

def asta_nave(stato):
    """TODO-45/EPILOGO-7: asta della nave con offerte e ripetizione."""
    import nuovo_mondo
    
    nuovo_mondo.pulisci_schermo()
    cprint("⚓ --- ASTA DELLA NAVE ---", "yellow", attrs=["bold"])
    nuovo_mondo.stampa_lenta("Il galeone è consumato dai viaggi. Vuoi venderlo all'asta?", "cyan")
    print()

    offerte_lista = [50, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 1200]
    integrita = stato.get('integrita', 100)
    cprint(f"🛡️  Integrità nave: {integrita}%", "cyan")

    # Filtra offerte per integrità
    if integrita >= 80:
        max_idx = 13
    elif integrita >= 60:
        max_idx = 11
    elif integrita >= 40:
        max_idx = 8
    elif integrita >= 20:
        max_idx = 5
    else:
        max_idx = 1

    offerte_disponibili = offerte_lista[:max_idx+1]
    random.shuffle(offerte_disponibili)
    
    gia_proposte = set()
    ripetibili_sempre = {50, 300, 400, 450}

    ricavo_totale = 0
    for offerta in offerte_disponibili:
        if offerta in gia_proposte and offerta not in ripetibili_sempre:
            continue
        
        gia_proposte.add(offerta)
        scelta = nuovo_mondo.chiedi_scelta(
            colored(f"👉 {offerta}🪙 da un offerente — [A] Accetta | [P] Passa: ", "magenta", attrs=["bold"]),
            ['A', 'P']
        )
        
        if scelta == 'A':
            nuovo_mondo.stampa_lenta(f"✅ Venduta per {offerta}🪙!", "green", attrs=["bold"])
            ricavo_totale = offerta
            break

    if ricavo_totale == 0:
        nuovo_mondo.stampa_lenta("🚢 Tieni la nave. Potrebbe servire per il prossimo viaggio.", "cyan")
    
    return ricavo_totale

def conclusione(capitano, stato):
    """TODO-43/44/46/EPILOGO-2/3/4/5/8: calcolo profitti e finali."""
    import nuovo_mondo
    import Stati_Ingaggio
    
    nuovo_mondo.pulisci_schermo()
    dati = nuovo_mondo.carica_dati()

    cprint("🔔" + "="*58 + "🔔", "yellow", attrs=["bold"])
    nuovo_mondo.stampa_lenta(f" LE CAMPANE DI SIVIGLIA! Capitano {capitano}, avete ingannato la Mietitrice.", "yellow", ["bold"])
    cprint("🔔" + "="*58 + "🔔", "yellow", attrs=["bold"])

    nuovo_mondo.stampa_lenta("\nLa folla ammutolisce nel vedere il galeone annerito scivolare nel porto.", "cyan")

    # TODO-EPILOGO-3: Fattore unico, valori base corretti
    valori_risorse = {"perle": 2, "manufatti": 2, "spezie": 1}  # ← VALORI CORRETTI
    fattore = random.choice([0.5, 1.0, 2.0])

    profitto_baratto = 0
    print()
    cprint("📦 --- VALUTAZIONE MERCI ---", "cyan", attrs=["bold"])
    for risorsa, qty in stato.get('risorse_baratto', {}).items():
        if qty > 0 and risorsa in valori_risorse:
            valore = qty * valori_risorse[risorsa] * fattore
            profitto_baratto += valore
            segno_f = colored(f"×{fattore}", "green" if fattore >= 1 else "red", attrs=["bold"])
            nuovo_mondo.stampa_lenta(f"  {risorsa.capitalize()}: {qty:.1f} × {valori_risorse[risorsa]}🪙 {segno_f} = {valore:.0f}🪙", "green")
            time.sleep(0.4)

    stato['budget'] += profitto_baratto

    # TODO-EPILOGO-5: Calcolo paghe corrette per singolo membro
    print()
    cprint("💰 --- PAGAMENTO EQUIPAGGIO (settimane effettive) ---", "yellow", attrs=["bold"])
    settimane_reali = stato.get('settimane_percorse', 16)
    cprint(f"  Settimane totali percorse: {settimane_reali}", "cyan")

    costo_totale_equipaggio = 0
    costo_sett_ruolo = stato.get('costo_sett_ruolo', {})

    for ruolo, n_persone in stato['equipaggio'].items():
        costo_per_sett = costo_sett_ruolo.get(ruolo, 0)
        if costo_per_sett > 0:
            # Numero di MEMBRI INGAGGIATI di questo ruolo (non naufraghi)
            costo_ruolo = costo_per_sett * settimane_reali
            costo_totale_equipaggio += costo_ruolo
            nuovo_mondo.stampa_lenta(f"  {Stati_Ingaggio.NOMI_RUOLO.get(ruolo, ruolo)}: {costo_per_sett}🪙/sett × {settimane_reali} sett = {costo_ruolo:.0f}🪙", "yellow")
            time.sleep(0.3)

    stato['budget'] -= costo_totale_equipaggio
    if stato['budget'] < 0:
        nuovo_mondo.stampa_lenta(f"⚠️  Non hai abbastanza per pagare la ciurma! Debito: {abs(stato['budget']):.0f}🪙", "red", attrs=["bold"])

    # Asta nave
    print()
    ricavo_nave = asta_nave(stato)
    stato['budget'] += ricavo_nave

    # TODO-EPILOGO-6: Bonus albatro benevolo
    if stato.get('albatro_benevolo', False):
        bonus = 500
        stato['budget'] += bonus
        nuovo_mondo.stampa_lenta(f"✨ Benedizione dell'albatro! Bonus fortuna divina: +{bonus}🪙", "yellow", attrs=["bold"])

    budget_finale = stato['budget']
    
    # TODO-EPILOGO-4: Mostra residuo budget iniziale
    spese_init = stato.get('spese_iniziali', 0)
    budget_residuo_init = 2000 - spese_init

    print()
    cprint("─"*60, "cyan")
    cprint(f"📊 BILANCIO FINALE: {budget_finale:.0f}🪙", "cyan", attrs=["bold"])
    print(f"  Budget iniziale:      2000🪙")
    print(f"  Spese iniziali:       -{spese_init:.0f}🪙")
    print(f"  Residuo dopo acquisti: {budget_residuo_init:.0f}🪙")
    print(f"  Profitto baratto:     +{profitto_baratto:.0f}🪙")
    print(f"  Costo equipaggio:     -{costo_totale_equipaggio:.0f}🪙")
    print(f"  Ricavo nave:          +{ricavo_nave}🪙")
    if stato.get('albatro_benevolo'):
        print(f"  Benedizione albatro:  +500🪙")
    cprint("─"*60, "cyan")

    # TODO-EPILOGO-8: Soglie finali corrette
    esito = ""
    print()
    if budget_finale > 0:
        dati["stats"]["vittorie_pirro"] += 1
        esito = "Vittoria di Pirro"
        cprint("\n⚖️  ═══════════════════════════════════", "cyan", attrs=["bold"])
        cprint("   VITTORIA DI PIRRO - SOPRAVVISSUTO!", "cyan", attrs=["bold"])
        cprint("═══════════════════════════════════", "cyan", attrs=["bold"])
        nuovo_mondo.stampa_lenta("Sei vivo. I debiti sono saldati. Ma i sogni di gloria restano sogni.", "yellow")
        nuovo_mondo.stampa_lenta("La taverna ti accoglie come sempre. Forse un altro viaggio?", "cyan")
    elif budget_finale == 0:
        dati["stats"]["vittorie_pirro"] += 1
        esito = "Vittoria Nulla"
        cprint("\n🤝 ═══════════════════════════════════", "dark_grey", attrs=["bold"])
        cprint("   PAREGGIO - NULLA GUADAGNATO NÉ PERSO!", "dark_grey", attrs=["bold"])
        cprint("═══════════════════════════════════", "dark_grey", attrs=["bold"])
        nuovo_mondo.stampa_lenta("Siete tornati come siete partiti: senza fortuna, ma vivi.", "dark_grey")
    else:
        dati["stats"]["rovine"] += 1
        esito = "Rovina Totale"
        cprint("\n💀 ═══════════════════════════════════", "red", attrs=["bold"])
        cprint("   ROVINA TOTALE - DISONORATO!", "red", attrs=["bold"])
        cprint("═══════════════════════════════════", "red", attrs=["bold"])
        nuovo_mondo.stampa_lenta("Le Guardie Reali vi incatenano sul molo davanti alla folla.", "red", ["bold"])
        nuovo_mondo.stampa_lenta("Prigione per debiti. La cella è umida. Le catene sono pesanti.", "red")
        nuovo_mondo.stampa_lenta("Il Nuovo Mondo vi ha sconfitto.", "dark_grey")

    nuovo_mondo.salva_dati(dati)
    nuovo_mondo.archivia_partita(capitano, stato, esito)
    input(colored("\n📖 [Premi Invio per tornare al Menù Principale] ", "dark_grey"))