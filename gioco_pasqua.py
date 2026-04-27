import random
import sys
import time
import json
import os
from termcolor import colored, cprint

try:
    import msvcrt
    is_windows = True
except ImportError:
    import select
    is_windows = False

# ==========================================
# GESTIONE DATI E SALVATAGGI
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_SALVATAGGIO = os.path.join(BASE_DIR, "galeone_save.json")

def pulisci_schermo():
    os.system('cls' if os.name == 'nt' else 'clear')

def carica_dati():
    dati_base = {
        "stats": {
            "morti": 0,
            "vittorie_epiche": 0,
            "vittorie_pirro": 0,
            "rovine": 0
        },
        "salvataggi": {}
    }
    if os.path.exists(FILE_SALVATAGGIO):
        try:
            with open(FILE_SALVATAGGIO, "r", encoding="utf-8") as f:
                dati_letti = json.load(f)
                if "stats" in dati_letti:
                    dati_base["stats"].update(dati_letti["stats"])
                if "salvataggi" in dati_letti:
                    dati_base["salvataggi"].update(dati_letti["salvataggi"])
        except json.JSONDecodeError:
            cprint("\n⚠️  ATTENZIONE: Il file di salvataggio è corrotto!", "red", attrs=["bold"])
        except Exception as e:
            cprint(f"\n⚠️  Errore imprevisto nel caricamento: {e}", "red")
    return dati_base

def salva_dati(dati):
    try:
        with open(FILE_SALVATAGGIO, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4, ensure_ascii=False)
    except Exception as e:
        cprint(f"❌ Errore durante il salvataggio: {e}", "red")

def archivia_partita(capitano, stato, esito):
    print()
    nome = input(colored("👉 Inserisci un nome per registrare questa partita (Invio per casuale): ", "cyan")).strip()
    if not nome:
        nome = f"Cronaca_di_{capitano}_{random.randint(1000,9999)}"
    dati = carica_dati()
    stato["esito"] = esito
    dati["salvataggi"][nome] = {"capitano": capitano, "stato": stato}
    salva_dati(dati)
    cprint(f"✅ Partita '{nome}' registrata negli archivi.", "green")

def mostra_statistiche_globali(dati):
    pulisci_schermo()
    cprint("\n" + "="*60, "cyan", attrs=["bold"])
    cprint(" 📊 --- REGISTRO DEL CAPITANO (STATISTICHE GLOBALI) --- 📊 ", "yellow", attrs=["bold"])
    cprint("="*60, "cyan", attrs=["bold"])
    stats = dati["stats"]
    print(f"💀 Morti in mare:        {colored(stats['morti'], 'red', attrs=['bold'])}")
    print(f"👑 Vittorie Epiche:      {colored(stats['vittorie_epiche'], 'yellow', attrs=['bold'])}")
    print(f"⚖️  Vittorie di Pirro:   {colored(stats['vittorie_pirro'], 'cyan', attrs=['bold'])}")
    print(f"⛓️  Rovina Totale:       {colored(stats['rovine'], 'dark_grey', attrs=['bold'])}")
    input(colored("\n📖 [Premi Invio per tornare al Menù] ", "dark_grey"))

# ==========================================
# FUNZIONI DI INPUT E STAMPA
# ==========================================

def leggi_input(prompt_testo):
    sys.stdout.write(prompt_testo)
    sys.stdout.flush()
    risposta = ""
    while True:
        if is_windows:
            c = msvcrt.getch()
            if c == b'\x1b':
                print()
                raise InterruptedError("ESC")
            elif c in (b'\r', b'\n'):
                print()
                return risposta
            elif c == b'\x08':
                if len(risposta) > 0:
                    risposta = risposta[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                try:
                    char = c.decode('utf-8')
                    risposta += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
                except: pass
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                c = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            if c == '\x1b':
                print()
                raise InterruptedError("ESC")
            elif c in ('\r', '\n'):
                print()
                return risposta
            elif c in ('\x7f', '\x08'):
                if len(risposta) > 0:
                    risposta = risposta[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif c == '\x03':
                raise KeyboardInterrupt
            else:
                risposta += c
                sys.stdout.write(c)
                sys.stdout.flush()

def chiedi_scelta(prompt_testo, opzioni_valide):
    while True:
        scelta = leggi_input(prompt_testo).upper().strip()
        if scelta in opzioni_valide:
            return scelta
        cprint("\n❌ Scelta non valida. Scegli una delle opzioni tra parentesi.", "red")

def stampa_lenta(testo, colore=None, attrs=None, ritardo=0.03):
    salta_animazione = False
    if is_windows:
        while msvcrt.kbhit():
            msvcrt.getch()
    for carattere in testo:
        if not salta_animazione:
            if is_windows:
                if msvcrt.kbhit():
                    tasto = msvcrt.getch()
                    if tasto in (b'\r', b'\n'):
                        salta_animazione = True
            else:
                i, o, e = select.select([sys.stdin], [], [], 0)
                if i:
                    sys.stdin.readline()
                    salta_animazione = True
        char_da_stampare = colored(carattere, colore, attrs=attrs) if colore else carattere
        sys.stdout.write(char_da_stampare)
        sys.stdout.flush()
        if not salta_animazione:
            time.sleep(ritardo)
    print()

def game_over(messaggio, stato, capitano):
    dati = carica_dati()
    dati["stats"]["morti"] += 1
    salva_dati(dati)
    print()
    cprint("="*60, "red", attrs=["bold"])
    stampa_lenta(messaggio, "red")
    cprint("\n💀 === GAME OVER === 💀\n", "red", attrs=["bold", "blink"])
    cprint("="*60, "red", attrs=["bold"])
    archivia_partita(capitano, stato, "Morto in mare")
    return False

def variazione_stat(messaggio, colore):
    cprint(f"  {messaggio}", colore, attrs=["bold"])

# ==========================================
# STATO EQUIPAGGIO E MORALE INDIVIDUALE
# ==========================================

COSTI_RUOLO = {
    "cuochi": 15,
    "marinai": 10,
    "meccanici": 15,
    "medici": 25,
    "navigatori": 20
}

# Nomi ruolo singolari per la stampa
NOMI_RUOLO = {
    "cuochi": "Cuoco",
    "marinai": "Marinaio",
    "meccanici": "Meccanico",
    "medici": "Medico",
    "navigatori": "Navigatore"
}

def stampa_risorse(stato):
    ciurma_totale = sum(stato['equipaggio'].values())
    cprint(f"👥 Ciurma: {ciurma_totale} | 🪙 Budget: {stato['budget']} | 🥬 Verdura: {stato['scorte']['verdura']:.1f}kg | 🍊 Frutta: {stato['scorte']['frutta']:.1f}kg | 🥩 Carne: {stato['scorte']['carne']:.1f}kg | 💧 Acqua: {stato['scorte']['acqua']:.1f}brl", "cyan", attrs=["bold"])
    cprint(f"🛡️ Integrità: {stato.get('integrita', 100)}% | 🪝 Punti Ammutinamento: {stato.get('punti_ammutinamento', 0)}", "magenta", attrs=["bold"])
    # Stampa morale medio
    morali = list(stato.get('morale_individuale', {}).values())
    if morali:
        media_morale = sum(morali) / len(morali)
        cprint(f"❤️ Morale medio equipaggio: {media_morale:.0f}/100", "yellow", attrs=["bold"])

def aggiungi_membro(stato, ruolo, nome=None):
    """Aggiunge un membro con morale individuale."""
    stato['equipaggio'][ruolo] = stato['equipaggio'].get(ruolo, 0) + 1
    if nome is None:
        idx = sum(stato['equipaggio'].values())
        nome = f"{NOMI_RUOLO.get(ruolo, ruolo)}_{idx}"
    stato['morale_individuale'][nome] = 100
    return nome

def rimuovi_membro(stato, ruolo):
    """Rimuove un membro casuale del ruolo dato (TODO-11: morte a morale 0)."""
    if stato['equipaggio'].get(ruolo, 0) > 0:
        stato['equipaggio'][ruolo] -= 1
        # Rimuovi il membro con morale più bassa del ruolo
        chiavi_ruolo = [k for k in stato['morale_individuale'] if k.startswith(NOMI_RUOLO.get(ruolo, ruolo))]
        if chiavi_ruolo:
            vittima = min(chiavi_ruolo, key=lambda k: stato['morale_individuale'][k])
            del stato['morale_individuale'][vittima]

def controlla_morti_morale_zero(stato):
    """TODO-11: morte automatica membri con morale = 0."""
    morti = [k for k, v in list(stato['morale_individuale'].items()) if v <= 0]
    for morto in morti:
        del stato['morale_individuale'][morto]
        # Rimuovi dal conteggio equipaggio
        for ruolo, nome_singolo in NOMI_RUOLO.items():
            if morto.startswith(nome_singolo):
                stato['equipaggio'][ruolo] = max(0, stato['equipaggio'].get(ruolo, 0) - 1)
                cprint(f"  💀 {morto} è morto per morale a zero!", "red", attrs=["bold"])
                break

def varia_morale_tutti(stato, delta, motivo=""):
    """Varia morale di tutti i membri."""
    for k in stato['morale_individuale']:
        stato['morale_individuale'][k] = max(0, min(100, stato['morale_individuale'][k] + delta))
    if motivo:
        segno = "📈" if delta > 0 else "📉"
        variazione_stat(f"{segno} Morale {'+' if delta>0 else ''}{delta} ({motivo})", "green" if delta > 0 else "red")
    controlla_morti_morale_zero(stato)

def conta_equipaggio(stato):
    return sum(stato['equipaggio'].values())

def equipaggio_basso_morale(stato, soglia=30):
    """TODO-12: controlla se più della metà ha morale ≤ soglia."""
    morali = list(stato['morale_individuale'].values())
    if not morali:
        return False
    bassi = sum(1 for m in morali if m <= soglia)
    return bassi > len(morali) / 2

def aggiungi_punti_ammutinamento(stato, punti, motivo=""):
    stato['punti_ammutinamento'] = stato.get('punti_ammutinamento', 0) + punti
    if motivo:
        variazione_stat(f"⚠️ +{punti} punti ammutinamento ({motivo})", "red")

# ==========================================
# SISTEMA SCORTE E CONSUMI
# ==========================================

COSTI_SCORTE = {
    "verdura": 0.5,   # per kg
    "frutta": 1.0,    # per kg
    "carne": 2.0,     # per kg
    "acqua": 0.5      # per barile
}

CONSUMI_SETTIMANALI_PER_MEMBRO = {
    "verdura": 0.5,   # kg
    "frutta": 1.0,    # kg
    "carne": 1.0,     # kg
    "acqua": 0.5      # barili
}

def consuma_scorte_dettagliate(stato, moltiplicatore=1.0):
    """TODO-05: consumi settimanali specifici per categoria."""
    n = conta_equipaggio(stato)
    esaurite = []
    for cat, consumo_per_membro in CONSUMI_SETTIMANALI_PER_MEMBRO.items():
        consumo = consumo_per_membro * n * moltiplicatore
        stato['scorte'][cat] -= consumo
        if stato['scorte'][cat] < 0:
            esaurite.append(cat)
            stato['scorte'][cat] = 0

    if esaurite:
        for cat in esaurite:
            # TODO-10: -10 morale per esaurimento scorte
            varia_morale_tutti(stato, -10, f"scorte {cat} esaurite")
            aggiungi_punti_ammutinamento(stato, 15, f"scorte {cat} esaurite")
        return "scorte_esaurite"

    if stato.get('punti_ammutinamento', 0) >= 100:
        return "ammutinamento"

    if stato.get('integrita', 100) <= 0:
        return "affondato"

    return "ok"

# ==========================================
# EVENTI CASUALI (TODO-15 a TODO-31)
# ==========================================

def evento_uomo_in_mare(stato):
    """TODO-16."""
    stampa_lenta("🌊 UOMO IN MARE! Un'onda gigantesca spazza il ponte senza preavviso.", "red", attrs=["bold"])
    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
    if ruoli_vivi:
        ruolo = random.choice(ruoli_vivi)
        rimuovi_membro(stato, ruolo)
        varia_morale_tutti(stato, -15, "collega caduto in mare")
        variazione_stat(f"💀 Hai perso 1 {NOMI_RUOLO.get(ruolo, ruolo)}!", "red")
    else:
        stampa_lenta("Miracolosamente, nessuno cade.", "green")

def evento_perdita_scorte(stato):
    """TODO-17: Verdura/Frutta/Carne/Acqua in mare."""
    categorie = ["verdura", "frutta", "carne", "acqua"]
    cat = random.choice(categorie)
    simboli = {"verdura": "🥬", "frutta": "🍊", "carne": "🥩", "acqua": "💧"}
    quantita = random.uniform(5, 15)
    stato['scorte'][cat] = max(0, stato['scorte'][cat] - quantita)
    stampa_lenta(f"🌊 Un'onda scellerata trascina in mare {quantita:.1f} unità di {cat}!", "red")
    variazione_stat(f"📉 -{quantita:.1f} {simboli[cat]} {cat.capitalize()}", "red")
    varia_morale_tutti(stato, -5, f"perdita {cat}")

def evento_pesca_miracolosa(stato):
    """TODO-18."""
    stampa_lenta("🎣 Un banco di pesci enormi circonda la nave. Pesca miracolosa!", "green", attrs=["bold"])
    carne_guadagnata = random.uniform(8, 20)
    stato['scorte']['carne'] += carne_guadagnata
    variazione_stat(f"📈 +{carne_guadagnata:.1f} 🥩 Carne (pesca)", "green")
    varia_morale_tutti(stato, +5, "pesca miracolosa")

def evento_tempesta_miracolosa(stato):
    """TODO-19: guarisce malati, riempie cisterne."""
    stampa_lenta("⛈️ Una tempesta provvidenziale! La pioggia riempie ogni contenitore e lava i malati.", "cyan", attrs=["bold"])
    acqua_guadagnata = random.uniform(10, 25)
    stato['scorte']['acqua'] += acqua_guadagnata
    # Guarisce: aumenta morale di tutti
    varia_morale_tutti(stato, +15, "tempesta miracolosa")
    variazione_stat(f"📈 +{acqua_guadagnata:.1f} 💧 Acqua", "green")

def evento_venti_favorevoli(stato):
    """TODO-20: accorcia viaggio di 1 sett, +morale."""
    stampa_lenta("💨 VENTI FAVOREVOLI! Le vele si gonfiano al massimo. Avanzate di settimane in giorni!", "green", attrs=["bold"])
    stato['settimane_risparmiate'] = stato.get('settimane_risparmiate', 0) + 1
    bonus = random.choice([5, 15])
    varia_morale_tutti(stato, bonus, "venti favorevoli")
    variazione_stat(f"📈 Viaggio accorciato di 1 settimana!", "green")

def evento_cattivo_tempo(stato):
    """TODO-21: consuma doppio viveri."""
    stampa_lenta("🌧️ CATTIVO TEMPO! Tre giorni di tempesta consumano le scorte al doppio.", "yellow")
    n = conta_equipaggio(stato)
    for cat, consumo in CONSUMI_SETTIMANALI_PER_MEMBRO.items():
        stato['scorte'][cat] = max(0, stato['scorte'][cat] - consumo * n)
    varia_morale_tutti(stato, -5, "cattivo tempo")
    variazione_stat("📉 Consumi doppi questa settimana!", "red")

def evento_ondata(stato):
    """TODO-22: danni nave, perde scorte."""
    stampa_lenta("🌊 UN'ONDATA GIGANTESCA colpisce la fiancata! Tutto vola.", "red", attrs=["bold"])
    stato['integrita'] = max(0, stato.get('integrita', 100) - random.randint(15, 30))
    cat = random.choice(["verdura", "frutta", "carne"])
    perso = random.uniform(3, 10)
    stato['scorte'][cat] = max(0, stato['scorte'][cat] - perso)
    variazione_stat(f"📉 Integrità -{30}% | -{perso:.1f} {cat}", "red")
    varia_morale_tutti(stato, -8, "ondata devastante")

def evento_infestazione_ratti(stato):
    """TODO-23: perdita scorte carne."""
    stampa_lenta("🐀 INFESTAZIONE DI RATTI! I roditori divorano le riserve di carne nella stiva.", "yellow")
    perso = random.uniform(5, 18)
    stato['scorte']['carne'] = max(0, stato['scorte']['carne'] - perso)
    variazione_stat(f"📉 -{perso:.1f} 🥩 Carne divorata dai ratti", "red")
    varia_morale_tutti(stato, -5, "infestazione ratti")

def evento_albatro(stato):
    """TODO-24/32/33/34/35: logica completa albatro."""
    stato['avvistamenti_albatro'] = stato.get('avvistamenti_albatro', 0) + 1
    n_avvistamento = stato['avvistamenti_albatro']

    stampa_lenta(f"🦅 Un albatro enorme sorvola la nave! ({n_avvistamento}/3 avvistamenti)", "cyan", attrs=["bold"])
    stampa_lenta("I marinai sussurrano: 'Porta fortuna... o porta sventura se ucciso!'", "yellow")

    scelta = chiedi_scelta(colored("👉 [S] Spara all'albatro | [L] Lascialo volare: ", "magenta", attrs=["bold"]), ['S', 'L'])

    if scelta == 'S':
        stampa_lenta("💥 BANG! L'albatro cade in mare tra grida di orrore dell'equipaggio!", "red", attrs=["bold"])
        stato['albatro_ucciso'] = True
        aggiungi_punti_ammutinamento(stato, 30, "albatro ucciso - presagio di sventura")
        varia_morale_tutti(stato, -20, "albatro ucciso - maledizione")
        variazione_stat("☠️ La maledizione dell'albatro si abbatte sulla nave!", "red")
    else:
        stampa_lenta("🕊️ L'albatro continua il suo volo. L'equipaggio tira un sospiro di sollievo.", "green")
        if n_avvistamento == 3:
            # TODO-35: effetto benigno finale
            stampa_lenta("✨ L'albatro vi ha scortati per tutto il viaggio! La fortuna è con voi!", "yellow", attrs=["bold"])
            stato['albatro_benevolo'] = True
            varia_morale_tutti(stato, +10, "albatro benevolo - protezione divina")

def evento_scialuppa(stato):
    """TODO-25: cassa con 4 nuovi membri non pagati."""
    stampa_lenta("🚤 Una scialuppa alla deriva! A bordo ci sono 4 naufraghi che implorano soccorso.", "cyan")
    scelta = chiedi_scelta(colored("👉 [R] Raccogli i naufraghi | [I] Ignora e prosegui: ", "magenta", attrs=["bold"]), ['R', 'I'])

    if scelta == 'R':
        stampa_lenta("🤝 I naufraghi salgono a bordo, pronti a lavorare senza paga pur di sopravvivere.", "green")
        # 4 marinai non pagati
        for i in range(4):
            nome = f"Naufrago_{i+1}"
            stato['equipaggio']['marinai'] = stato['equipaggio'].get('marinai', 0) + 1
            stato['morale_individuale'][nome] = 70
        variazione_stat("📈 +4 Marinai naufraghi (senza costo)", "green")
        # Ma consumano scorte
        varia_morale_tutti(stato, -3, "bocche in più da sfamare")
    else:
        stampa_lenta("😔 Li lasciate al loro destino. L'equipaggio mormora.", "yellow")
        varia_morale_tutti(stato, -8, "naufraghi abbandonati")

def evento_epidemia(stato):
    """TODO-26: logica medico/bottiglie medicinale."""
    stampa_lenta("🦠 EPIDEMIA! Una malattia misteriosa colpisce l'equipaggio con febbre alta.", "red", attrs=["bold"])

    ha_medico = stato['equipaggio'].get('medici', 0) > 0
    ha_medicine = stato['merci'].get('bottiglie_medicinale', 0) > 0

    if ha_medico and ha_medicine:
        stampa_lenta("💊 Il medico distribuisce le bottiglie di medicinale. L'epidemia viene debellata!", "green")
        stato['merci']['bottiglie_medicinale'] = max(0, stato['merci']['bottiglie_medicinale'] - 2)
        varia_morale_tutti(stato, +5, "epidemia curata")
        variazione_stat("📉 -2 💊 Bottiglie medicinale usate", "yellow")
    elif ha_medico:
        stampa_lenta("🩺 Il medico fa del suo meglio senza medicine. Alcune vittime.", "yellow")
        ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
        if ruoli_vivi:
            rimuovi_membro(stato, random.choice(ruoli_vivi))
        varia_morale_tutti(stato, -10, "epidemia parzialmente curata")
    else:
        stampa_lenta("💀 Senza medico né medicine, l'epidemia fa strage!", "red", attrs=["bold"])
        ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
        for _ in range(min(3, conta_equipaggio(stato))):
            if ruoli_vivi:
                rimuovi_membro(stato, random.choice(ruoli_vivi))
        aggiungi_punti_ammutinamento(stato, 20, "epidemia senza cure")
        varia_morale_tutti(stato, -25, "epidemia devastante")

def evento_attacco_pirata(stato):
    """TODO-27: formula perdita uomini basata su armi."""
    stampa_lenta("🏴‍☠️ PIRATI! Velieri neri emergono dalla nebbia sparando cannonate!", "red", attrs=["bold"])
    scelta = chiedi_scelta(colored("👉 [C] Combatti | [F] Fuggi | [P] Paga il riscatto (200🪙): ", "magenta", attrs=["bold"]), ['C', 'F', 'P'])

    n_armi = stato['merci'].get('armi', 0)
    n_marinai = stato['equipaggio'].get('marinai', 0)

    if scelta == 'C':
        forza = n_marinai * 2 + n_armi * 3
        if forza >= 10:
            stampa_lenta("⚔️ Resistenza eroica! I pirati si ritirano con le pive nel sacco!", "green", attrs=["bold"])
            varia_morale_tutti(stato, +10, "vittoria contro i pirati")
        else:
            vittime = max(1, (10 - forza) // 2)
            stampa_lenta(f"🩸 Combattimento impari. Perdete {vittime} uomini prima di respingerli.", "red")
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            for _ in range(vittime):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    rimuovi_membro(stato, ruolo)
            varia_morale_tutti(stato, -20, "sconfitta contro i pirati")
            stato['integrita'] = max(0, stato.get('integrita', 100) - 20)
    elif scelta == 'F':
        if stato['equipaggio'].get('navigatori', 0) > 0:
            stampa_lenta("🧭 Il navigatore trova una rotta di fuga tra gli scogli. Siete salvi!", "green")
        else:
            stampa_lenta("💥 Senza navigatore non riuscite a fuggire! Vi speronano.", "red")
            stato['integrita'] = max(0, stato.get('integrita', 100) - 30)
            varia_morale_tutti(stato, -15, "fuga fallita dai pirati")
    else:
        if stato['budget'] >= 200:
            stampa_lenta("💰 Gettate il riscatto. I pirati prendono l'oro e se ne vanno.", "yellow")
            stato['budget'] -= 200
        else:
            stampa_lenta("💀 Non avete abbastanza oro! I pirati saccheggiano le stive.", "red")
            for cat in stato['scorte']:
                stato['scorte'][cat] = stato['scorte'][cat] * 0.5
            aggiungi_punti_ammutinamento(stato, 20, "saccheggio pirata")

def evento_danni_timone(stato):
    """TODO-28: se no navigatore danno grave."""
    stampa_lenta("⚙️ DANNI AL TIMONE! La barra sbanda pericolosamente!", "red", attrs=["bold"])

    if stato['equipaggio'].get('navigatori', 0) > 0 and stato['equipaggio'].get('meccanici', 0) > 0:
        stampa_lenta("🔧 Il meccanico e il navigatore riparano il timone in tempo!", "green")
        stato['integrita'] = max(0, stato.get('integrita', 100) - 5)
    elif stato['equipaggio'].get('meccanici', 0) > 0:
        stampa_lenta("🔧 Il meccanico fa una riparazione di fortuna. Si va avanti storto.", "yellow")
        stato['integrita'] = max(0, stato.get('integrita', 100) - 15)
        stato['settimane_extra'] = stato.get('settimane_extra', 0) + 1
    else:
        stampa_lenta("💥 DANNO GRAVE! Senza navigatore né meccanico, la nave gira in cerchio per giorni!", "red", attrs=["bold"])
        stato['integrita'] = max(0, stato.get('integrita', 100) - 35)
        stato['settimane_extra'] = stato.get('settimane_extra', 0) + 2
        varia_morale_tutti(stato, -20, "danni al timone irrecuperabili")
        aggiungi_punti_ammutinamento(stato, 25, "nave ingovernabile")

def evento_raffiche_vento(stato):
    """TODO-29: danno nave, perdita scorte."""
    stampa_lenta("💨 RAFFICHE DI VENTO VIOLENTE! Le vele si strappano, oggetti volano ovunque!", "red")
    stato['integrita'] = max(0, stato.get('integrita', 100) - random.randint(10, 25))
    cat_persa = random.choice(["verdura", "frutta", "carne", "acqua"])
    perso = random.uniform(5, 12)
    stato['scorte'][cat_persa] = max(0, stato['scorte'][cat_persa] - perso)
    variazione_stat(f"📉 -{perso:.1f} {cat_persa} | -Integrità nave", "red")
    varia_morale_tutti(stato, -5, "raffiche di vento")

def evento_avvistamento_isola(stato):
    """TODO-30: casualità strana."""
    stampa_lenta("🏝️ TERRA! Un'isola sconosciuta si profila all'orizzonte...", "cyan", attrs=["bold"])
    risultato = random.randint(1, 4)
    if risultato == 1:
        stampa_lenta("🌿 L'isola è disabitata! Trovate frutta fresca e acqua dolce in abbondanza.", "green")
        stato['scorte']['frutta'] += random.uniform(10, 20)
        stato['scorte']['acqua'] += random.uniform(10, 20)
        varia_morale_tutti(stato, +10, "isola provvidenziale")
    elif risultato == 2:
        stampa_lenta("🐊 L'isola pullula di coccodrilli enormi. Fuggite a nuoto con le bende ai morsi.", "red")
        ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
        if ruoli_vivi:
            rimuovi_membro(stato, random.choice(ruoli_vivi))
        varia_morale_tutti(stato, -15, "isola maledetta")
    elif risultato == 3:
        stampa_lenta("🗺️ L'isola non è sulle carte. Il navigatore aggiorna la rotta: risparmio di tempo!", "green")
        stato['settimane_risparmiate'] = stato.get('settimane_risparmiate', 0) + 1
    else:
        stampa_lenta("🌫️ L'isola scompare come un miraggio. Un'allucinazione collettiva per la sete.", "yellow")
        varia_morale_tutti(stato, -10, "miraggio deludente")

# Registro eventi già accaduti (TODO-15)
EVENTI_UNICI = {
    "uomo_in_mare": evento_uomo_in_mare,
    "perdita_scorte": evento_perdita_scorte,
    "epidemia": evento_epidemia,
    "danni_timone": evento_danni_timone,
    "raffiche_vento": evento_raffiche_vento,
    "avvistamento_isola": evento_avvistamento_isola,
    "attacco_pirata": evento_attacco_pirata,
    "scialuppa": evento_scialuppa,
}

EVENTI_RIPETIBILI = {
    "pesca_miracolosa": evento_pesca_miracolosa,
    "tempesta_miracolosa": evento_tempesta_miracolosa,
    "venti_favorevoli": evento_venti_favorevoli,
    "cattivo_tempo": evento_cattivo_tempo,
    "ondata": evento_ondata,
    "infestazione_ratti": evento_infestazione_ratti,
    "albatro": evento_albatro,
}

def gestisci_evento_casuale(stato):
    cprint("\n" + "~"*60, "blue", attrs=["bold"])
    cprint("⚠️  EVENTO IN MARE!", "yellow", attrs=["bold", "blink"])

    eventi_accaduti = stato.get('eventi_accaduti', [])

    # TODO-32: albatro max 3 apparizioni
    if stato.get('avvistamenti_albatro', 0) >= 3:
        eventi_disponibili_ripetibili = {k: v for k, v in EVENTI_RIPETIBILI.items() if k != 'albatro'}
    else:
        eventi_disponibili_ripetibili = EVENTI_RIPETIBILI

    eventi_unici_disponibili = {k: v for k, v in EVENTI_UNICI.items() if k not in eventi_accaduti}

    pool = list(eventi_disponibili_ripetibili.values())
    pool_unici = [(k, v) for k, v in eventi_unici_disponibili.items()]

    # 50% chance evento unico se disponibili
    if pool_unici and random.random() < 0.5:
        nome_ev, funzione_ev = random.choice(pool_unici)
        eventi_accaduti.append(nome_ev)
        stato['eventi_accaduti'] = eventi_accaduti
        funzione_ev(stato)
    elif pool:
        random.choice(pool)(stato)
    else:
        stampa_lenta("🌅 Il mare è calmo. Nessun imprevisto questa settimana.", "cyan")

    cprint("~"*60, "blue", attrs=["bold"])

# ==========================================
# FASI DI GIOCO
# ==========================================

def introduzione():
    pulisci_schermo()
    cprint("="*60, "yellow", attrs=["bold"])
    cprint(" ⚓  VERSO IL NUOVO MONDO: SANGUE, SALE E SPEZIE  ⚓ ", "red", "on_grey", attrs=["bold"])
    cprint("="*60, "yellow", attrs=["bold"])
    stampa_lenta("\nSiviglia, 1519. L'aria del porto è un miasma denso di pesce marcio, catrame bollente e disperazione.", "cyan")
    stampa_lenta("I creditori bussano alla tua porta. La prigione per debiti ti aspetta, a meno che tu non compia un miracolo.", "cyan")
    stampa_lenta("Di fronte a te riposa il possente galeone 'La Maledizione d'Oro'.", "cyan")
    stampa_lenta("Il tuo obiettivo: raggiungere il Nuovo Mondo, barattare merci preziose e tornare vivo.", "cyan", ["bold"])
    capitano = leggi_input(colored("\n🏴‍☠️  Capitano, qual è il tuo nome? ", "yellow", attrs=["bold"])).strip().capitalize()
    if not capitano:
        capitano = "Senza Nome"
    stampa_lenta(f"\nChe Dio abbia pietà della tua anima, Capitano {capitano}.", "red", ["bold"])
    time.sleep(1)
    return capitano, 2000

def fase_arruolamento(stato, capitano):
    """TODO-01/02/03: esattamente 1 per ruolo, costi differenziati, pagamento differito."""
    pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🍻 --- LA TAVERNA DEL PORTO (ARRUOLAMENTO) ---", "green", attrs=["bold"])
    stampa_lenta("Entri in una bettola fumosa. Ogni ruolo richiede un esperto. Il pagamento avverrà a fine viaggio.", "cyan")
    stampa_lenta("⚠️  Devi ingaggiare ESATTAMENTE 1 persona per ruolo prima di salpare.", "yellow", attrs=["bold"])

    ruoli_info = {
        "cuochi": ("🍲 Cuoco", 15),
        "marinai": ("🪢 Marinaio", 10),
        "meccanici": ("⚙️ Meccanico", 15),
        "medici": ("🩸 Medico", 25),
        "navigatori": ("🧭 Navigatore", 20),
    }

    while True:
        pulisci_schermo()
        print()
        cprint("="*60, "green", attrs=["bold"])
        cprint("🍻 TAVERNA DEL PORTO - ARRUOLAMENTO (paga a fine viaggio)", "green", attrs=["bold"])
        print()
        
        for i, (ruolo, (etichetta, costo)) in enumerate(ruoli_info.items(), 1):
            ingaggiato = stato['equipaggio'].get(ruolo, 0) > 0
            stato_str = colored("✅ INGAGGIATO", "green", attrs=["bold"]) if ingaggiato else colored(f"❌ {costo}🪙/sett (fine viaggio)", "red")
            print(f"{i}. {etichetta:<20} {stato_str}")

        print()
        cprint(f"🪙 Budget attuale: {stato['budget']}", "cyan")
        
        tutti_ingaggiati = all(stato['equipaggio'].get(r, 0) >= 1 for r in ruoli_info)
        if tutti_ingaggiati:
            cprint("✅ Tutti i ruoli coperti! Puoi salpare.", "green", attrs=["bold"])
            print(colored("0.", "red", attrs=["bold"]) + " 🚪 SALPA! (Termina Arruolamento)")
        else:
            mancanti = [r for r in ruoli_info if stato['equipaggio'].get(r, 0) == 0]
            cprint(f"⚠️  Mancano ancora: {', '.join(NOMI_RUOLO[r] for r in mancanti)}", "yellow")
            print(colored("0.", "red", attrs=["bold"]) + " 🚪 Esci senza ingaggiare tutti (sconsigliato)")

        # Opzione aggiuntiva marinai extra
        print(colored("6.", "magenta") + " 🪢 Ingaggia Marinaio Extra (supporto in combattimento)")

        scelta = chiedi_scelta(colored("\n👉 Scegli (0-6): ", "magenta", attrs=["bold"]), ['0','1','2','3','4','5','6'])

        if scelta == "0":
            if not tutti_ingaggiati:
                stampa_lenta("⚠️  Parti senza equipaggio completo. Rischi altissimi!", "red", attrs=["bold"])
            break

        ruoli_lista = list(ruoli_info.keys())
        if scelta in ['1','2','3','4','5']:
            idx = int(scelta) - 1
            ruolo_scelto = ruoli_lista[idx]
            etichetta, costo_sett = ruoli_info[ruolo_scelto]
            
            if stato['equipaggio'].get(ruolo_scelto, 0) > 0 and scelta != '6':
                cprint(f"❌ Hai già un {NOMI_RUOLO[ruolo_scelto]}! Ruolo coperto.", "red")
                time.sleep(1)
                continue
            
            nome = aggiungi_membro(stato, ruolo_scelto)
            # TODO-03: non sottrarre subito - registra il debito
            settimane_stimate = 16
            costo_totale_stimato = costo_sett * settimane_stimate
            stato['debito_equipaggio'] = stato.get('debito_equipaggio', 0) + costo_sett
            stampa_lenta(f"✍️ {etichetta} ingaggiato! Paga: {costo_sett}🪙/sett (da corrispondere a fine viaggio).", "green")
            time.sleep(0.8)

        elif scelta == '6':
            # Marinaio extra
            nome = aggiungi_membro(stato, 'marinai')
            stato['debito_equipaggio'] = stato.get('debito_equipaggio', 0) + ruoli_info['marinai'][1]
            stampa_lenta(f"✍️ Marinaio extra ingaggiato! Paga: {ruoli_info['marinai'][1]}🪙/sett.", "green")
            time.sleep(0.8)

    if conta_equipaggio(stato) == 0:
        return game_over("Senza ciurma, i creditori ti raggiungono sul molo. Fine.", stato, capitano)
    return True

def fase_acquisto_provviste(stato, capitano):
    """TODO-04/05/06: 4 categorie, consumi specifici, dimezzamento/raddoppio."""
    pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🏪 --- MERCATO DEL PORTO (PROVVISTE) ---", "green", attrs=["bold"])
    stampa_lenta("Scegli bene le scorte. Ogni membro consuma ogni settimana:", "cyan")
    print()
    print(f"  🥬 Verdura:  {CONSUMI_SETTIMANALI_PER_MEMBRO['verdura']} kg/membro/sett  → {COSTI_SCORTE['verdura']}🪙/kg")
    print(f"  🍊 Frutta:   {CONSUMI_SETTIMANALI_PER_MEMBRO['frutta']} kg/membro/sett  → {COSTI_SCORTE['frutta']}🪙/kg")
    print(f"  🥩 Carne:    {CONSUMI_SETTIMANALI_PER_MEMBRO['carne']} kg/membro/sett  → {COSTI_SCORTE['carne']}🪙/kg")
    print(f"  💧 Acqua:    {CONSUMI_SETTIMANALI_PER_MEMBRO['acqua']} brl/membro/sett → {COSTI_SCORTE['acqua']}🪙/brl")
    print()
    cprint(f"👥 Equipaggio: {conta_equipaggio(stato)} | 🪙 Budget: {stato['budget']}", "cyan", attrs=["bold"])
    print()

    acquisti = {}
    simboli = {"verdura": "🥬", "frutta": "🍊", "carne": "🥩", "acqua": "💧"}
    unita = {"verdura": "kg", "frutta": "kg", "carne": "kg", "acqua": "barili"}

    costo_totale = 0
    for cat in ["verdura", "frutta", "carne", "acqua"]:
        n_suggerito = CONSUMI_SETTIMANALI_PER_MEMBRO[cat] * conta_equipaggio(stato) * 10  # 10 settimane
        while True:
            try:
                qty_str = leggi_input(colored(f"{simboli[cat]} {cat.capitalize()} ({COSTI_SCORTE[cat]}🪙/{unita[cat]}) [suggerito: {n_suggerito:.1f}]: ", "yellow", attrs=["bold"]))
                qty = float(qty_str) if qty_str.strip() else n_suggerito
                if qty < 0:
                    raise ValueError
                costo = qty * COSTI_SCORTE[cat]
                if costo_totale + costo > stato['budget']:
                    cprint(f"❌ Non hai abbastanza budget! Budget rimasto: {stato['budget'] - costo_totale:.1f}🪙", "red")
                    continue
                acquisti[cat] = qty
                costo_totale += costo
                break
            except (ValueError, Exception):
                cprint("❌ Inserisci un numero valido.", "red")

    for cat, qty in acquisti.items():
        stato['scorte'][cat] = qty

    stato['budget'] -= costo_totale
    cprint(f"\n✅ Scorte caricate! Spesi {costo_totale:.1f}🪙 | Budget rimasto: {stato['budget']:.1f}🪙", "green", attrs=["bold"])

    # TODO-06: Step 2 - Controllo e aggiustamento razioni
    print()
    cprint("📋 FASE 2 - GESTIONE RAZIONI", "yellow", attrs=["bold"])
    stampa_lenta("Puoi dimezzare o raddoppiare le razioni per categoria.", "cyan")
    stampa_lenta("⚠️ Dimezzare: -5 morale | Raddoppiare: +5 morale (TODO-10)", "yellow")
    print()

    for cat in ["verdura", "frutta", "carne", "acqua"]:
        scelta_razione = chiedi_scelta(
            colored(f"{simboli[cat]} {cat.capitalize()} ({stato['scorte'][cat]:.1f}): [N] Normale | [D] Dimezza | [R] Raddoppia: ", "magenta"),
            ['N', 'D', 'R']
        )
        if scelta_razione == 'D':
            stato['scorte'][cat] *= 0.5
            varia_morale_tutti(stato, -5, f"razioni {cat} dimezzate")
            aggiungi_punti_ammutinamento(stato, 30, "razioni ridotte")
        elif scelta_razione == 'R':
            stato['scorte'][cat] *= 2.0
            # Raddoppio costa dal budget? Solo se avanzato
            costo_extra = stato['scorte'][cat] * 0.5 * COSTI_SCORTE[cat]
            if stato['budget'] >= costo_extra:
                stato['budget'] -= costo_extra
                varia_morale_tutti(stato, +5, f"razioni {cat} raddoppiate")
                cprint(f"  💰 Spesi {costo_extra:.1f}🪙 per raddoppiare {cat}", "yellow")
            else:
                stato['scorte'][cat] *= 0.5  # annulla
                cprint(f"  ❌ Budget insufficiente per raddoppiare {cat}. Rimaste normali.", "red")

    time.sleep(1.5)
    return True

def fase_merci_arsenale(stato, capitano):
    """TODO-07/08: 6 tipi di merci barattabili, rimuovere legno/carpentiere."""
    pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("⚔️ --- L'ARSENALE E IL MERCATO DELLE MERCI ---", "green", attrs=["bold"])
    stampa_lenta("Equipaggia la nave con armi e merci da barattare nel Nuovo Mondo.", "cyan")
    print()

    # Merci barattabili (TODO-07)
    catalogo_merci = {
        "bottiglie_medicinale": ("💊 Bottiglie Medicinale", 30),
        "armi": ("⚔️ Armi", 50),
        "sale": ("🧂 Sale", 20),
        "stoffa": ("🧵 Stoffa", 25),
        "coltelli": ("🔪 Coltelli", 15),
        "diamanti": ("💎 Diamanti", 200),
    }

    cprint(f"🪙 Budget disponibile: {stato['budget']}", "cyan", attrs=["bold"])
    print()

    for codice, (nome, costo) in catalogo_merci.items():
        if stato['budget'] < costo:
            cprint(f"  ❌ {nome} ({costo}🪙) - Budget insufficiente", "dark_grey")
            continue
        while True:
            try:
                qty_str = leggi_input(colored(f"  {nome} ({costo}🪙/unità) - Quante ne vuoi? [0=nessuna]: ", "yellow"))
                qty = int(qty_str) if qty_str.strip() else 0
                costo_tot = qty * costo
                if costo_tot > stato['budget']:
                    cprint(f"  ❌ Non hai abbastanza budget! ({stato['budget']}🪙 rimasti)", "red")
                    continue
                stato['merci'][codice] = stato['merci'].get(codice, 0) + qty
                if qty > 0:
                    stato['budget'] -= costo_tot
                    cprint(f"  ✅ Acquistato {qty}x {nome} per {costo_tot}🪙", "green")
                break
            except ValueError:
                cprint("  ❌ Numero non valido.", "red")

    # Armi hanno effetto su ammutinamento/pirateria
    if stato['merci'].get('armi', 0) == 0:
        stampa_lenta("⚠️ Nessuna arma! Vulnerabili agli attacchi.", "yellow", attrs=["bold"])

    cprint(f"\n🪙 Budget rimasto: {stato['budget']}", "cyan", attrs=["bold"])
    time.sleep(1.5)
    return True

def viaggio_andata(stato, capitano):
    """TODO-12/13/14/15+: viaggio con tutti i nuovi sistemi."""
    pulisci_schermo()
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(" SALPATE! L'ancora viene strappata dal fondo del porto.", "cyan", ["bold"])
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    # Gestione cuoco mancante (TODO-13: +30 punti ammutinamento)
    if stato['equipaggio'].get('cuochi', 0) == 0:
        aggiungi_punti_ammutinamento(stato, 30, "nessun cuoco a bordo")

    settimane_viaggio = 8
    settimana = 1

    while settimana <= settimane_viaggio + stato.get('settimane_extra', 0):
        cprint(f"\n📅 --- SETTIMANA {settimana} DI ANDATA ---", "yellow", attrs=["bold"])
        stampa_risorse(stato)

        # TODO-12: se più della metà ha morale ≤ 30, +1 settimana
        if equipaggio_basso_morale(stato, 30):
            stampa_lenta("⚠️ Il morale è a pezzi! La navigazione rallenta terribilmente.", "red", attrs=["bold"])
            settimane_viaggio += 1
            cprint(f"📅 Il viaggio si allunga! Ora mancano ancora {settimane_viaggio + stato.get('settimane_extra',0) - settimana} settimane.", "red")

        # Evento ogni 2 settimane circa
        if settimana % 2 == 0:
            gestisci_evento_casuale(stato)

        leggi_input(colored("\n📖 [Premi Invio per avanzare...] ", "dark_grey"))
        pulisci_schermo()

        esito = consuma_scorte_dettagliate(stato)
        if esito == "ammutinamento":
            return game_over(
                "I punti ammutinamento hanno raggiunto il massimo. La ciurma si ribella. "
                "Ti sgozzano sul ponte mentre l'alba tinge di rosso l'oceano.",
                stato, capitano
            )
        elif esito == "affondato":
            return game_over("La nave non regge più. L'acqua invade la stiva. Naufragate.", stato, capitano)
        elif esito == "scorte_esaurite":
            stampa_lenta("☠️ Le scorte di qualche categoria sono esaurite! L'equipaggio soffre.", "red", attrs=["bold"])

        # TODO-14: ammutinamento a soglia punti (non solo morale)
        if stato.get('punti_ammutinamento', 0) >= 100:
            return game_over(
                "L'ammutinamento esplode! Anni di torti si riversano in una notte di fuoco e sangue. "
                "Il tuo corpo viene gettato in pasto agli squali.",
                stato, capitano
            )

        if conta_equipaggio(stato) == 0:
            return game_over("L'ultimo uomo è morto. La nave vaga senza vita verso l'abisso.", stato, capitano)

        settimana += 1

    return True

def arrivo_nuovo_mondo(stato, capitano):
    """TODO-36/37: indigeni armati, scelta far fuoco/contrattare/furto."""
    pulisci_schermo()
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])
    stampa_lenta(" TERRA IN VISTA! Il Nuovo Mondo emerge tra la nebbia mattutina.", "green", ["bold"])
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])

    stampa_lenta("La barca tocca la spiaggia. Silenzio assordante.", "yellow")
    stampa_lenta("Poi... centinaia di guerrieri emergono dalla foresta, dipinti di ocra rossa.", "red", attrs=["bold"])
    
    # TODO-34: se albatro ucciso, gli indigeni sono più aggressivi
    if stato.get('albatro_ucciso', False):
        stampa_lenta("⚠️ Gli sciamani agitano le lance — come se sapessero della vostra colpa verso l'albatro!", "red", attrs=["bold"])
        aggressivita_bonus = 5
    else:
        aggressivita_bonus = 0

    stampa_lenta("Dietro di loro, enormi ceste di perle, manufatti e spezie. Ricchezza immensa.", "yellow", ["bold"])

    scelta = chiedi_scelta(
        colored("\n👉 I tamburi battono. [F] FAI FUOCO | [C] Contratta | [N] Furto notturno: ", "magenta", attrs=["bold"]),
        ['F', 'C', 'N']
    )

    if scelta == 'F':
        # TODO-37: far fuoco = game over immediato
        stampa_lenta("💥 'FUOCO A VOLONTÀ!'", "red", attrs=["bold", "blink"])
        stampa_lenta("Un attimo di silenzio... poi migliaia di frecce avvelenate oscurano il sole.", "red")
        stampa_lenta("Siete sopraffatti in secondi. Nessun sopravvissuto.", "red", attrs=["bold"])
        return game_over("Avete provocato un massacro. Il Nuovo Mondo vi uccide tutti.", stato, capitano)

    elif scelta == 'C':
        stampa_lenta("🤝 Avanzate lentamente, mani aperte. Offrite i doni.", "cyan")
        successo = random.randint(1, 10) + stato['equipaggio'].get('navigatori', 0) - aggressivita_bonus
        if successo >= 5:
            stampa_lenta("✨ Il capo tribù accetta! Inizia il baratto.", "green", attrs=["bold"])
            stato['fase_baratto'] = True
            return fase_baratto(stato, capitano)
        else:
            stampa_lenta("🩸 Un malinteso! Un guerriero scaglia la lancia. Fuggite!", "red", attrs=["bold"])
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            for _ in range(2 + aggressivita_bonus // 2):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    rimuovi_membro(stato, ruolo)
            varia_morale_tutti(stato, -20, "contrattazione fallita")
            stampa_lenta("⚠️ Non avete ottenuto nulla. Dovete ripartire.", "red")
            return True

    elif scelta == 'N':
        stampa_lenta("🌙 Attendete la notte profonda...", "cyan")
        n_marinai = stato['equipaggio'].get('marinai', 0)
        n_navigatori = stato['equipaggio'].get('navigatori', 0)
        successo = random.randint(1, 10) + n_marinai + n_navigatori - aggressivita_bonus
        if successo >= 8:
            stampa_lenta("🥷 Come ombre nella notte, vi infiltrate nel villaggio. Un successo perfetto!", "green", attrs=["bold"])
            stato['scorte_ritorno'] = True
            # Rubate qualcosa ma non tanto quanto il baratto
            stato['perle_rubate'] = random.randint(5, 15)
            variazione_stat(f"📈 +{stato['perle_rubate']} 🔮 Perle rubate", "green")
            return True
        else:
            stampa_lenta("🚨 Una trappola! Torce ovunque. Fuggite nel sangue!", "red", attrs=["bold"])
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            for _ in range(3 + aggressivita_bonus):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    rimuovi_membro(stato, ruolo)
            varia_morale_tutti(stato, -30, "furto fallito")
            aggiungi_punti_ammutinamento(stato, 20, "raid fallito")
            return True

def fase_baratto(stato, capitano):
    """TODO-38/39/40: baratto con 4 tipologie, 3 offerte ciascuna."""
    pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🤝 --- GRANDE BARATTO NEL NUOVO MONDO ---", "green", attrs=["bold"])
    stampa_lenta("Il capo tribù siede sul trono di conchiglie. È tempo di trattare.", "cyan")

    # Tabelle di baratto: merce → lista di (oggetto_offerto, quantità_ricevuta_per_unità)
    tabelle_baratto = {
        "sale": [
            ("perle", 3.0, "🔮"),
            ("manufatti", 2.0, "🗿"),
            ("spezie", 1.5, "🌶️"),
        ],
        "stoffa": [
            ("perle", 5.0, "🔮"),
            ("manufatti", 4.0, "🗿"),
            ("spezie", 3.0, "🌶️"),
        ],
        "coltelli": [
            ("perle", 4.0, "🔮"),
            ("manufatti", 3.0, "🗿"),
            ("spezie", 2.0, "🌶️"),
        ],
        "diamanti": [
            ("perle", 20.0, "🔮"),
            ("manufatti", 15.0, "🗿"),
            ("spezie", 10.0, "🌶️"),
        ],
    }

    merci_disponibili = {k: v for k, v in stato['merci'].items()
                        if k in tabelle_baratto and v > 0}

    if not merci_disponibili:
        stampa_lenta("❌ Non hai merci barattabili! Il capo tribù ti congeda.", "red", attrs=["bold"])
        return True

    # TODO-40: salva quantità barattate
    stato.setdefault('barattato', {"sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0})

    for merce, quantita in merci_disponibili.items():
        if quantita <= 0:
            continue
        pulisci_schermo()
        cprint(f"🔄 Baratto: {merce.upper()} (hai {quantita} unità)", "yellow", attrs=["bold"])
        print()

        offerte = tabelle_baratto[merce]
        for i, (cosa, tasso, simbolo) in enumerate(offerte, 1):
            print(f"  {i}. {simbolo} {cosa.capitalize()} → {tasso} {simbolo}/unità di {merce}")
        print(f"  0. Salta (non barattare {merce})")
        print()

        scelta_offerta = chiedi_scelta(
            colored(f"👉 Quale offerta scegli? (0-{len(offerte)}): ", "magenta", attrs=["bold"]),
            ['0'] + [str(i) for i in range(1, len(offerte)+1)]
        )

        if scelta_offerta == '0':
            continue

        idx_offerta = int(scelta_offerta) - 1
        cosa, tasso, simbolo = offerte[idx_offerta]

        while True:
            try:
                qty_str = leggi_input(colored(f"  Quante unità di {merce} vuoi barattare? (max {quantita}): ", "yellow"))
                qty = int(qty_str) if qty_str.strip() else 0
                if qty < 0 or qty > quantita:
                    cprint(f"  ❌ Quantità non valida (0-{quantita})", "red")
                    continue
                break
            except ValueError:
                cprint("  ❌ Numero non valido.", "red")

        if qty > 0:
            guadagno = qty * tasso
            stato['merci'][merce] -= qty
            stato['barattato'][merce] = stato['barattato'].get(merce, 0) + qty
            stato['risorse_baratto'][cosa] = stato['risorse_baratto'].get(cosa, 0) + guadagno
            cprint(f"  ✅ Barattato {qty}x {merce} → +{guadagno:.1f} {simbolo} {cosa}", "green", attrs=["bold"])
            time.sleep(0.8)

    # TODO-41/42: Tradimento
    evento_tradimento(stato)

    cprint(f"\n📊 RIEPILOGO BARATTO:", "cyan", attrs=["bold"])
    for risorsa, qty in stato['risorse_baratto'].items():
        if qty > 0:
            print(f"  {risorsa.capitalize()}: {qty:.1f}")

    time.sleep(2)
    return True

def evento_tradimento(stato):
    """TODO-41/42: rivale capo tribù offre 30 perle per arma, 50% scoperta."""
    if stato['merci'].get('armi', 0) <= 0:
        return

    stampa_lenta("\n🌑 Un guerriero si avvicina di notte, con uno sguardo losco.", "yellow")
    stampa_lenta("Sussurra: 'Il rivale del capo... offre 30 perle per ogni arma. In segreto.'", "red")

    scelta = chiedi_scelta(
        colored("👉 [A] Accetta il tradimento | [R] Rifiuta: ", "magenta", attrs=["bold"]),
        ['A', 'R']
    )

    if scelta == 'A':
        # TODO-42: 50% probabilità essere scoperti, peggiorata se albatro ucciso
        prob_scoperto = 0.5
        if stato.get('albatro_ucciso', False):
            prob_scoperto = 0.75  # peggiore con maledizione albatro
            stampa_lenta("☠️ La maledizione dell'albatro porta sfortuna...", "red")

        if random.random() < prob_scoperto:
            stampa_lenta("🚨 SIETE SCOPERTI! Il capo tribù urla vendetta!", "red", attrs=["bold"])
            # Perde armi e viene attaccato
            armi_confiscate = stato['merci']['armi']
            stato['merci']['armi'] = 0
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            for _ in range(min(3, conta_equipaggio(stato))):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    rimuovi_membro(stato, ruolo)
            varia_morale_tutti(stato, -30, "tradimento scoperto")
            aggiungi_punti_ammutinamento(stato, 40, "disonore del tradimento")
        else:
            armi_vendute = min(stato['merci']['armi'], 3)
            stato['merci']['armi'] -= armi_vendute
            guadagno = armi_vendute * 30
            stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + guadagno
            stampa_lenta(f"💰 Il tradimento riesce! +{guadagno} perle (vendute {armi_vendute} armi).", "green", attrs=["bold"])
    else:
        stampa_lenta("🤝 Rifiuti. Il guerriero scompare nell'oscurità.", "cyan")
        varia_morale_tutti(stato, +5, "onestà premiata")

def viaggio_ritorno(stato, capitano):
    """TODO-47/48: durata ritorno variabile, scorte dal capo tribù."""
    pulisci_schermo()

    # TODO-48: capo tribù rifornisce per 3 settimane
    stampa_lenta("🎁 Il capo tribù, grato per il commercio, rifornisce la nave per 3 settimane di viaggio.", "green", attrs=["bold"])
    n = conta_equipaggio(stato)
    for cat, consumo in CONSUMI_SETTIMANALI_PER_MEMBRO.items():
        stato['scorte'][cat] += consumo * n * 3
    variazione_stat("📈 Scorte per 3 settimane caricate dal capo tribù!", "green")

    # TODO-47: durata ritorno
    settimane_ritorno = 1 if stato['equipaggio'].get('navigatori', 0) > 0 else 2
    if stato.get('albatro_ucciso', False):
        settimane_ritorno += 1
        stampa_lenta("☠️ La maledizione dell'albatro prolunga il ritorno di 1 settimana.", "red")

    # Ma il ritorno è in media 8 settimane base, modificato dai fattori sopra
    settimane_base_ritorno = 8
    settimane_ritorno_totali = settimane_base_ritorno + (0 if stato['equipaggio'].get('navigatori', 0) > 0 else 1)
    if stato.get('albatro_ucciso', False):
        settimane_ritorno_totali += 1

    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(f" IL RITORNO. {settimane_ritorno_totali} settimane di oceano ancora.", "cyan", ["bold"])
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    for settimana in range(1, settimane_ritorno_totali + 1):
        cprint(f"\n📅 --- SETTIMANA {settimana} DI RITORNO ---", "yellow", attrs=["bold"])
        stampa_risorse(stato)

        # TODO-12
        if equipaggio_basso_morale(stato, 30):
            stampa_lenta("⚠️ Il morale è a pezzi. Il viaggio rallenta.", "red")
            settimane_ritorno_totali += 1

        if settimana % 2 == 0:
            gestisci_evento_casuale(stato)

        leggi_input(colored("\n📖 [Premi Invio, stringendo i denti...] ", "dark_grey"))
        pulisci_schermo()

        esito = consuma_scorte_dettagliate(stato)
        if esito == "ammutinamento":
            return game_over("L'ammutinamento sul ritorno. Così vicini alla gloria...", stato, capitano)
        elif esito == "affondato":
            return game_over("La nave non regge. Naufraghi a pochi giorni da Siviglia.", stato, capitano)

        if stato.get('punti_ammutinamento', 0) >= 100:
            return game_over("La ciurma si ribella durante il ritorno. Fine ingloriosa.", stato, capitano)

        if conta_equipaggio(stato) == 0:
            return game_over("L'ultimo uomo è morto. La nave vaga vuota verso l'abisso.", stato, capitano)

    return True

def asta_nave(stato):
    """TODO-45: asta della nave con offerte specifiche."""
    pulisci_schermo()
    cprint("⚓ --- ASTA DELLA NAVE ---", "yellow", attrs=["bold"])
    stampa_lenta("Il galeone è consumato dai viaggi. Vuoi venderlo all'asta?", "cyan")

    offerte_asta = {
        1: ("Un pescatore curioso", 50),
        2: ("Un mercante in bancarotta", 300),
        3: ("Un armatore minore", 350),
        4: ("La Compagnia delle Indie", 600),
        5: ("Un nobile spagnolo", 850),
        6: ("Il Re di Portogallo", 1200),
    }

    integrita = stato.get('integrita', 100)
    # Offerte disponibili in base all'integrità
    if integrita >= 80:
        offerte_disponibili = offerte_asta
    elif integrita >= 50:
        offerte_disponibili = {k: v for k, v in offerte_asta.items() if k <= 5}
    elif integrita >= 25:
        offerte_disponibili = {k: v for k, v in offerte_asta.items() if k <= 3}
    else:
        offerte_disponibili = {1: offerte_asta[1]}

    print()
    cprint(f"🛡️ Integrità nave: {integrita}% → offerte disponibili:", "cyan")
    for k, (nome, prezzo) in offerte_disponibili.items():
        print(f"  {k}. {nome}: {prezzo}🪙")
    print(f"  0. Non vendere la nave")

    scelta = chiedi_scelta(
        colored(f"👉 Scegli l'offerente (0-{max(offerte_disponibili.keys())}): ", "magenta", attrs=["bold"]),
        ['0'] + [str(k) for k in offerte_disponibili.keys()]
    )

    if scelta == '0':
        stampa_lenta("🚢 Tieni la nave. Potrebbe servire per il prossimo viaggio.", "cyan")
        return 0
    else:
        _, (nome_offerente, prezzo) = list(offerte_disponibili.items())[int(scelta)-1]
        stampa_lenta(f"✅ Venduta a {nome_offerente} per {prezzo}🪙!", "green", attrs=["bold"])
        return prezzo

def conclusione(capitano, stato):
    """TODO-43/44/46: calcolo profitti, costo equipaggio, 3 finali."""
    pulisci_schermo()
    dati = carica_dati()

    cprint("🔔" + "="*58 + "🔔", "yellow", attrs=["bold"])
    stampa_lenta(f" LE CAMPANE DI SIVIGLIA! Capitano {capitano}, avete ingannato la Mietitrice.", "yellow", ["bold"])
    cprint("🔔" + "="*58 + "🔔", "yellow", attrs=["bold"])

    stampa_lenta("\nLa folla ammutolisce nel vedere il relitto annerito scivolare nel porto.", "cyan")

    # TODO-43: Profitto = perle × valore + manufatti × valore + spezie × valore × fattore casuale
    valori_risorse = {"perle": 10, "manufatti": 15, "spezie": 20}
    fattori = [0.5, 1.0, 2.0]

    profitto_baratto = 0
    print()
    cprint("📦 --- VALUTAZIONE MERCI ---", "cyan", attrs=["bold"])
    for risorsa, qty in stato.get('risorse_baratto', {}).items():
        if qty > 0 and risorsa in valori_risorse:
            fattore = random.choice(fattori)
            valore = qty * valori_risorse[risorsa] * fattore
            profitto_baratto += valore
            stampa_lenta(f"  {risorsa.capitalize()}: {qty:.1f} × {valori_risorse[risorsa]}🪙 × {fattore} = {valore:.0f}🪙", "green")
            time.sleep(0.5)

    # Perle rubate (furto di notte)
    if stato.get('perle_rubate', 0) > 0:
        valore_rubato = stato['perle_rubate'] * valori_risorse['perle']
        profitto_baratto += valore_rubato
        stampa_lenta(f"  🔮 Perle rubate: {stato['perle_rubate']} × {valori_risorse['perle']}🪙 = {valore_rubato}🪙", "yellow")

    stato['budget'] += profitto_baratto

    # TODO-44: costo equipaggio a fine viaggio
    print()
    cprint("💰 --- PAGAMENTO EQUIPAGGIO ---", "yellow", attrs=["bold"])
    settimane_totali = 16  # stima (andata 8 + ritorno 8)
    costo_totale_equipaggio = 0
    for ruolo, n_persone in stato['equipaggio'].items():
        if n_persone > 0 and ruolo in COSTI_RUOLO:
            costo_ruolo = COSTI_RUOLO[ruolo] * n_persone * settimane_totali
            costo_totale_equipaggio += costo_ruolo
            stampa_lenta(f"  {NOMI_RUOLO[ruolo]}: {n_persone}x {COSTI_RUOLO[ruolo]}🪙/sett × {settimane_totali} sett = {costo_ruolo}🪙", "yellow")
            time.sleep(0.3)

    stato['budget'] -= costo_totale_equipaggio
    if stato['budget'] < 0:
        stampa_lenta(f"⚠️ Non hai abbastanza per pagare tutta la ciurma! Debito: {abs(stato['budget'])}🪙", "red", attrs=["bold"])

    # Asta nave (TODO-45)
    print()
    ricavo_nave = asta_nave(stato)
    stato['budget'] += ricavo_nave

    # TODO-35: bonus albatro benevolo
    if stato.get('albatro_benevolo', False):
        bonus = 500
        stato['budget'] += bonus
        stampa_lenta(f"✨ Benedizione dell'albatro! Bonus fortuna: +{bonus}🪙", "yellow", attrs=["bold"])

    cprint(f"\n📊 BILANCIO FINALE: {stato['budget']:.0f}🪙", "cyan", attrs=["bold"])
    print(f"  Profitto baratto: {profitto_baratto:.0f}🪙")
    print(f"  Costo equipaggio: -{costo_totale_equipaggio}🪙")
    print(f"  Ricavo nave: +{ricavo_nave}🪙")

    # TODO-46: 3 finali distinti
    esito = ""
    print()
    if stato['budget'] > 2500:
        dati["stats"]["vittorie_epiche"] += 1
        esito = "Vittoria Epica"
        cprint("\n👑 ═══════════════════════════════════", "yellow", attrs=["bold"])
        cprint("   VITTORIA EPICA - EROE DELL'OCEANO!", "yellow", attrs=["bold"])
        cprint("═══════════════════════════════════", "yellow", attrs=["bold"])
        stampa_lenta("Le campane suonano per tre giorni! Il Re in persona ti riceve.", "green", ["bold"])
        stampa_lenta("Compri terre, un titolo nobiliare e un'intera flotta mercantile.", "green")
        stampa_lenta("Il tuo nome sarà scritto nei libri di storia per sempre.", "yellow", ["bold"])
    elif stato['budget'] > 0:
        dati["stats"]["vittorie_pirro"] += 1
        esito = "Vittoria di Pirro"
        cprint("\n⚖️ ═══════════════════════════════════", "cyan", attrs=["bold"])
        cprint("   VITTORIA DI PIRRO - SOPRAVVISSUTO!", "cyan", attrs=["bold"])
        cprint("═══════════════════════════════════", "cyan", attrs=["bold"])
        stampa_lenta("Sei vivo. I debiti sono saldati. Ma i sogni di gloria restano sogni.", "yellow")
        stampa_lenta("La taverna ti accoglie come sempre. Forse un altro viaggio?", "cyan")
    else:
        dati["stats"]["rovine"] += 1
        esito = "Rovina Totale"
        cprint("\n💀 ═══════════════════════════════════", "red", attrs=["bold"])
        cprint("   ROVINA TOTALE - DISONORATO!", "red", attrs=["bold"])
        cprint("═══════════════════════════════════", "red", attrs=["bold"])
        stampa_lenta("Le Guardie Reali ti incatenano sul molo davanti alla folla.", "red", ["bold"])
        stampa_lenta("Prigione per debiti. La cella è umida. Le catene sono pesanti.", "red")
        stampa_lenta("Il Nuovo Mondo ti ha sconfitto.", "dark_grey")

    salva_dati(dati)
    archivia_partita(capitano, stato, esito)
    input(colored("\n📖 [Premi Invio per tornare al Menù Principale] ", "dark_grey"))

# ==========================================
# MOTORE DI GIOCO E MENU
# ==========================================

def esegui_partita(nuova=True, dati_salvati=None):
    capitano = "Sconosciuto"
    stato_partita = {}

    try:
        if nuova:
            capitano, budget_iniziale = introduzione()
            stato_partita = {
                "fase": "inizio",
                "budget": budget_iniziale,
                "scorte": {"verdura": 0.0, "frutta": 0.0, "carne": 0.0, "acqua": 0.0},
                "merci": {
                    "bottiglie_medicinale": 0,
                    "armi": 0,
                    "sale": 0,
                    "stoffa": 0,
                    "coltelli": 0,
                    "diamanti": 0
                },
                "risorse_baratto": {"perle": 0, "manufatti": 0, "spezie": 0},
                "barattato": {"sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0},
                "morale_individuale": {},
                "punti_ammutinamento": 0,
                "integrita": 100,
                "equipaggio": {
                    "marinai": 0,
                    "cuochi": 0,
                    "meccanici": 0,
                    "medici": 0,
                    "navigatori": 0
                },
                "debito_equipaggio": 0,
                "albatro_ucciso": False,
                "albatro_benevolo": False,
                "avvistamenti_albatro": 0,
                "eventi_accaduti": [],
                "settimane_risparmiate": 0,
                "settimane_extra": 0,
            }
        else:
            pulisci_schermo()
            stato_partita = dati_salvati["stato"]
            capitano = dati_salvati["capitano"]
            # Compatibilità con vecchi salvataggi
            stato_partita.setdefault("scorte", {"verdura": 0.0, "frutta": 0.0, "carne": 0.0, "acqua": 0.0})
            stato_partita.setdefault("merci", {"bottiglie_medicinale": 0, "armi": 0, "sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0})
            stato_partita.setdefault("risorse_baratto", {"perle": 0, "manufatti": 0, "spezie": 0})
            stato_partita.setdefault("barattato", {"sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0})
            stato_partita.setdefault("morale_individuale", {})
            stato_partita.setdefault("punti_ammutinamento", 0)
            stato_partita.setdefault("eventi_accaduti", [])
            stato_partita.setdefault("settimane_risparmiate", 0)
            stato_partita.setdefault("settimane_extra", 0)
            stato_partita.setdefault("albatro_ucciso", False)
            stato_partita.setdefault("albatro_benevolo", False)
            stato_partita.setdefault("avvistamenti_albatro", 0)
            cprint(f"\n⚓ Bentornato a bordo, Capitano {capitano}!", "green", attrs=["bold"])
            time.sleep(1)

        # Avanzamento fasi
        if stato_partita["fase"] == "inizio":
            stato_partita["fase"] = "arruolamento"

        if stato_partita["fase"] == "arruolamento":
            if not fase_arruolamento(stato_partita, capitano): return
            stato_partita["fase"] = "provviste"

        if stato_partita["fase"] == "provviste":
            if not fase_acquisto_provviste(stato_partita, capitano): return
            stato_partita["fase"] = "merci"

        if stato_partita["fase"] == "merci":
            if not fase_merci_arsenale(stato_partita, capitano): return
            stato_partita["fase"] = "andata"

        if stato_partita["fase"] == "andata":
            if not viaggio_andata(stato_partita, capitano): return
            stato_partita["fase"] = "nuovo_mondo"

        if stato_partita["fase"] == "nuovo_mondo":
            risultato = arrivo_nuovo_mondo(stato_partita, capitano)
            if risultato is False: return
            stato_partita["fase"] = "ritorno"

        if stato_partita["fase"] == "ritorno":
            if not viaggio_ritorno(stato_partita, capitano): return
            conclusione(capitano, stato_partita)

    except InterruptedError:
        cprint("\n\n⏸️  GIOCO IN PAUSA (Tasto ESC intercettato)", "yellow", attrs=["bold"])
        nome = input(colored("👉 Inserisci il nome del salvataggio: ", "cyan")).strip()
        if not nome:
            nome = f"Salvataggio_di_{capitano}_{random.randint(100,999)}"
        dati = carica_dati()
        stato_partita["esito"] = "In corso"
        dati["salvataggi"][nome] = {"capitano": capitano, "stato": stato_partita}
        salva_dati(dati)
        cprint(f"\n✅ Partita salvata come '{nome}'!", "green", attrs=["bold"])
        time.sleep(2)
        return

def menu_principale():
    while True:
        pulisci_schermo()
        dati = carica_dati()

        cprint("="*60, "cyan", attrs=["bold"])
        cprint("  ☠️   LA MALEDIZIONE D'ORO - MENU PRINCIPALE   ☠️  ", "yellow", "on_grey", attrs=["bold"])
        cprint("="*60, "cyan", attrs=["bold"])

        print(colored("1.", "magenta", attrs=["bold"]) + " 🏴‍☠️ Nuova Partita")

        salvataggi_in_corso = {k: v for k, v in dati["salvataggi"].items()
                               if v["stato"].get("esito") == "In corso"}

        if salvataggi_in_corso:
            print(colored("2.", "magenta", attrs=["bold"]) + " ⚓ Continua Partita")
        else:
            print(colored("2.", "dark_grey") + " ⚓ Continua Partita (Nessun salvataggio disponibile)")

        print(colored("3.", "magenta", attrs=["bold"]) + " 📊 Statistiche Globali")
        print(colored("4.", "magenta", attrs=["bold"]) + " 🔍 Esplora Archivi Partita")
        print(colored("0.", "magenta", attrs=["bold"]) + " 🚪 Esci dal Gioco")

        scelta = input(colored("\n👉 Scegli un'opzione: ", "magenta", attrs=["bold"])).strip()

        if scelta == "1":
            esegui_partita(nuova=True)

        elif scelta == "2":
            if not salvataggi_in_corso:
                cprint("\n❌ Inizia prima una nuova avventura!", "red")
                time.sleep(1.5)
            else:
                print("\n⚓ Salvataggi disponibili:")
                nomi = list(salvataggi_in_corso.keys())
                for i, n in enumerate(nomi, 1):
                    print(f"   {i}. {n} (Capitano: {salvataggi_in_corso[n]['capitano']}, Fase: {salvataggi_in_corso[n]['stato']['fase']})")
                scelta_s = input("\n👉 Numero o nome del salvataggio: ").strip()
                da_caricare = None
                if scelta_s.isdigit() and 1 <= int(scelta_s) <= len(nomi):
                    da_caricare = nomi[int(scelta_s) - 1]
                elif scelta_s in salvataggi_in_corso:
                    da_caricare = scelta_s
                if da_caricare:
                    esegui_partita(nuova=False, dati_salvati=salvataggi_in_corso[da_caricare])
                else:
                    cprint("❌ Salvataggio non trovato.", "red")
                    time.sleep(1.5)

        elif scelta == "3":
            mostra_statistiche_globali(dati)

        elif scelta == "4":
            pulisci_schermo()
            print("\n🔍 --- CERCA ARCHIVIO PARTITA ---")
            if not dati["salvataggi"]:
                cprint("❌ Nessuna partita negli archivi.", "red")
                time.sleep(1.5)
                continue
            nomi_archivi = list(dati["salvataggi"].keys())
            for i, n in enumerate(nomi_archivi, 1):
                esito = dati["salvataggi"][n]["stato"].get("esito", "Sconosciuto")
                print(f"   {i}. {n} [{esito}]")
            ricerca = input(colored("\n👉 Nome o numero: ", "cyan")).strip()
            da_cercare = None
            if ricerca.isdigit() and 1 <= int(ricerca) <= len(nomi_archivi):
                da_cercare = nomi_archivi[int(ricerca) - 1]
            elif ricerca in dati["salvataggi"]:
                da_cercare = ricerca
            if da_cercare:
                pulisci_schermo()
                s = dati["salvataggi"][da_cercare]
                sp = s['stato']
                cprint(f"\n📜 DETTAGLI: {da_cercare}", "yellow", attrs=["bold"])
                print(f"🏴‍☠️ Capitano: {s['capitano']} | 📌 Stato: {sp.get('esito','?')} | 🗺️ Fase: {sp.get('fase','?')}")
                cprint("\n💰 RISORSE:", "green")
                print(f"  🪙 Budget: {sp.get('budget', 0):.0f}")
                for cat, qty in sp.get('scorte', {}).items():
                    print(f"  {cat.capitalize()}: {qty:.1f}")
                print(f"  🛡️ Integrità: {sp.get('integrita',100)}%")
                print(f"  ⚠️ Punti Ammutinamento: {sp.get('punti_ammutinamento',0)}")
                cprint("\n👥 EQUIPAGGIO:", "cyan")
                for ruolo, n_p in sp.get('equipaggio', {}).items():
                    print(f"  {NOMI_RUOLO.get(ruolo, ruolo)}: {n_p}")
                cprint("\n📦 MERCI:", "magenta")
                for merce, qty in sp.get('merci', {}).items():
                    if qty > 0:
                        print(f"  {merce}: {qty}")
                input(colored("\n📖 [Premi Invio per tornare] ", "dark_grey"))
            else:
                cprint("\n❌ Partita non trovata.", "red")
                time.sleep(1.5)

        elif scelta == "0":
            cprint("\n🌊 Possa l'oceano esserti lieve. Addio, Capitano.", "cyan")
            sys.exit()
        else:
            cprint("\n❌ Scelta non valida.", "red")
            time.sleep(1)

if __name__ == "__main__":
    menu_principale()