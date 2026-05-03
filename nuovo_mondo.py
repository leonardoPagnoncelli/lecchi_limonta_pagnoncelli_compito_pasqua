#MAIN + FUNZIONI CONDIVISE
# nuovo_mondo.py
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

# Importa i moduli funzionali (NO import circolare a questo livello)
import Stati_Ingaggio
import Morale_Eventi
import Arrivo_GameOver

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
# FUNZIONI DI INPUT E STAMPA (SHARED)
# ==========================================

def leggi_input(prompt_testo):
    """Legge input da tastiera con supporto Windows/Unix."""
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
    """Chiede una scelta tra opzioni valide."""
    while True:
        scelta = leggi_input(prompt_testo).upper().strip()
        if scelta in opzioni_valide:
            return scelta
        cprint("\n❌ Scelta non valida. Scegli una delle opzioni tra parentesi.", "red")

def stampa_lenta(testo, colore=None, attrs=None, ritardo=0.03):
    """Stampa testo con animazione carattere per carattere."""
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

def variazione_stat(messaggio, colore):
    """Mostra una variazione di stato (es. morale, ammutinamento)."""
    cprint(f"  {messaggio}", colore, attrs=["bold"])

# ==========================================
# CICLO DI VIAGGIO (ORCHESTRAZIONE)
# ==========================================

def _ciclo_viaggio(stato, capitano, fase_nome, settimane_base):
    """
    Motore comune per andata e ritorno.
    Orchestra: Step 1 (eventi), Step 2 (scorte), Step 3 (morale),
    Step 4 (riepilogo), Step 5 (ammutinamento), Step 6 (settimane).
    
    Restituisce True se sopravvivono, False in caso di game over.
    """
    settimana = 1
    while True:
        settimane_totali = settimane_base + stato.get('settimane_extra', 0) - stato.get('settimane_risparmiate', 0)
        settimane_totali = max(settimane_totali, settimana)

        cprint(f"\n📅 --- SETTIMANA {settimana} DI {fase_nome.upper()} (di ~{settimane_totali}) ---", "yellow", attrs=["bold"])
        
        # Stampa risorse correnti
        Stati_Ingaggio.stampa_risorse(stato)

        # Step 6: Se morale basso rallenta il viaggio
        if Morale_Eventi.equipaggio_basso_morale(stato, 30):
            stampa_lenta("⚠️   Il morale è a pezzi! La navigazione rallenta terribilmente.", "red", attrs=["bold"])
            stato['settimane_extra'] = stato.get('settimane_extra', 0) + 1
            settimane_totali += 1
            cprint(f"📅 Il viaggio si allunga! Ora mancano ancora {settimane_totali - settimana} settimane.", "red")

        # Step 1: Evento ogni 2 settimane
        if settimana % 2 == 0:
            Morale_Eventi.gestisci_evento_casuale(stato)

        leggi_input(colored("\n📖 [Premi Invio per avanzare...] ", "dark_grey"))
        pulisci_schermo()

        # Step 2: Controllo scorte interattivo (attendere implementazione Sara)
        # step2_controllo_scorte(stato, settimane_totali - settimana)

        # Consuma scorte della settimana
        esito = Stati_Ingaggio.consuma_scorte_dettagliate(stato)
        Stati_Ingaggio.incrementa_settimane(stato)

        if esito == "ammutinamento":
            return Arrivo_GameOver.game_over(
                "I punti ammutinamento hanno raggiunto il massimo. La ciurma si ribella.\n"
                "Ti sgozzano sul ponte mentre l'alba tinge di rosso l'oceano.",
                stato, capitano
            )
        elif esito == "affondato":
            return Arrivo_GameOver.game_over("La nave non regge più. L'acqua invade la stiva. Naufragate.", stato, capitano)

        # Step 3: Aggiorna morale (già in consuma_scorte_dettagliate)
        
        # Step 4: Riepilogo settimana (attendere implementazione Lecchi)
        # step4_riepilogo_settimana(stato)

        # Step 5: Calcola ammutinamento (attendere implementazione Sara)
        # calcola_ammutinamento(stato)

        if stato.get('punti_ammutinamento', 0) >= 100:
            return Arrivo_GameOver.game_over(
                "L'ammutinamento esplode! Anni di torti si riversano in una notte di fuoco e sangue.\n"
                "Il tuo corpo viene gettato in pasto agli squali.",
                stato, capitano
            )

        if Stati_Ingaggio.conta_equipaggio(stato) == 0:
            return Arrivo_GameOver.game_over("L'ultimo uomo è morto. La nave vaga senza vita verso l'abisso.", stato, capitano)

        if settimana >= settimane_totali:
            break
        settimana += 1

    return True

# ==========================================
# FASI DI GIOCO (ORCHESTRAZIONE)
# ==========================================

def introduzione():
    """Introduzione e scelta nome capitano."""
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

def viaggio_andata(stato, capitano):
    """Andata verso il Nuovo Mondo — 8 settimane base."""
    pulisci_schermo()
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(" SALPATE! L'ancora viene strappata dal fondo del porto.", "cyan", ["bold"])
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    # TODO: nessun cuoco a bordo = +30 punti ammutinamento
    if stato['equipaggio'].get('cuochi', 0) == 0:
        Morale_Eventi.aggiungi_punti_ammutinamento(stato, 30, "nessun cuoco a bordo")

    return _ciclo_viaggio(stato, capitano, "ANDATA", settimane_base=8)

def viaggio_ritorno(stato, capitano):
    """Ritorno verso Siviglia."""
    pulisci_schermo()

    # Rifornimento dal capo tribù per 3 settimane
    stampa_lenta("🎁 Il capo tribù, grato per il commercio, rifornisce la nave per 3 settimane di viaggio.", "green", attrs=["bold"])
    n = Stati_Ingaggio.conta_equipaggio(stato)
    for cat, consumo in Stati_Ingaggio.CONSUMI_SETTIMANALI_PER_MEMBRO.items():
        aggiunte = consumo * n * 3
        stato['scorte'][cat] += aggiunte
    variazione_stat("📈 Scorte per 3 settimane caricate gratuitamente!", "green")

    # Calcolo durata ritorno
    settimane_base_ritorno = 8
    if stato['equipaggio'].get('navigatori', 0) > 0:
        settimane_base_ritorno -= 1
        stampa_lenta("🧭 Il navigatore traccia la rotta di ritorno più efficiente. -1 settimana!", "green")
    if stato.get('albatro_ucciso', False):
        settimane_base_ritorno += 1
        stampa_lenta("☠️  La maledizione dell'albatro prolunga il ritorno di 1 settimana.", "red")

    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(f" IL RITORNO. ~{settimane_base_ritorno} settimane di oceano ancora.", "cyan", ["bold"])
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    return _ciclo_viaggio(stato, capitano, "RITORNO", settimane_base=settimane_base_ritorno)

# ==========================================
# CREAZIONE E NORMALIZZAZIONE STATO
# ==========================================

def crea_stato_iniziale():
    """TODO-50: stato completo con tutti i campi necessari."""
    return {
        "fase": "inizio",
        "budget": 2000,
        "spese_iniziali": 0,  # TODO: Lecchi traccia spese per EPILOGO-4
        "scorte": {"verdura": 0.0, "frutta": 0.0, "carne": 0.0, "acqua": 0.0},
        "razioni_moltiplicatore": {"verdura": 1.0, "frutta": 1.0, "carne": 1.0, "acqua": 1.0},  # TODO-STATO-7
        "merci": {
            "bottiglie_medicinale": 0,
            "armi": 0,
            "sale": 0,
            "stoffa": 0,
            "coltelli": 0,
            "diamanti": 0,
        },
        "risorse_baratto": {"perle": 0.0, "manufatti": 0.0, "spezie": 0.0},
        "barattato": {"sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0},
        "morale_individuale": {},
        "punti_ammutinamento": 0,
        "integrita": 100,
        "equipaggio": {
            "marinai": 0,
            "cuochi": 0,
            "meccanici": 0,
            "medici": 0,
            "navigatori": 0,
        },
        "debito_equipaggio": 0,
        "costo_sett_ruolo": {},
        "albatro_ucciso": False,
        "albatro_benevolo": False,
        "avvistamenti_albatro": 0,
        "eventi_accaduti": [],
        "settimane_risparmiate": 0,
        "settimane_extra": 0,
        "settimane_percorse": 0,
        "naufraghi_tot": 0,
        "esito": "In corso",
    }

def normalizza_stato(stato):
    """TODO-50: compatibilità con vecchi salvataggi."""
    default = crea_stato_iniziale()
    for chiave, valore_default in default.items():
        if chiave not in stato:
            stato[chiave] = valore_default
    for cat in ["verdura", "frutta", "carne", "acqua"]:
        stato['scorte'].setdefault(cat, 0.0)
        stato['razioni_moltiplicatore'].setdefault(cat, 1.0)
    for m in ["bottiglie_medicinale", "armi", "sale", "stoffa", "coltelli", "diamanti"]:
        stato['merci'].setdefault(m, 0)
    for r in ["perle", "manufatti", "spezie"]:
        stato['risorse_baratto'].setdefault(r, 0.0)
    return stato

def esegui_partita(nuova=True, dati_salvati=None):
    """Esegue una partita completa: fasi sequenziali."""
    capitano = "Sconosciuto"
    stato_partita = {}

    try:
        if nuova:
            capitano, budget_iniziale = introduzione()
            stato_partita = crea_stato_iniziale()
            stato_partita["budget"] = budget_iniziale
        else:
            pulisci_schermo()
            stato_partita = normalizza_stato(dati_salvati["stato"])
            capitano = dati_salvati["capitano"]
            cprint(f"\n⚓ Bentornato a bordo, Capitano {capitano}!", "green", attrs=["bold"])
            cprint(f"   Fase corrente: {stato_partita['fase']} | Budget: {stato_partita['budget']:.0f}🪙", "cyan")
            time.sleep(1.5)

        # Fasi sequenziali
        if stato_partita["fase"] == "inizio":
            stato_partita["fase"] = "arruolamento"

        if stato_partita["fase"] == "arruolamento":
            if not Stati_Ingaggio.fase_arruolamento(stato_partita, capitano):
                return
            stato_partita["fase"] = "provviste"

        if stato_partita["fase"] == "provviste":
            if not Stati_Ingaggio.fase_acquisto_provviste(stato_partita, capitano):
                return
            stato_partita["fase"] = "merci"

        if stato_partita["fase"] == "merci":
            if not Stati_Ingaggio.fase_merci_arsenale(stato_partita, capitano):
                return
            stato_partita["fase"] = "andata"

        if stato_partita["fase"] == "andata":
            if not viaggio_andata(stato_partita, capitano):
                return
            stato_partita["fase"] = "nuovo_mondo"

        if stato_partita["fase"] == "nuovo_mondo":
            risultato = Arrivo_GameOver.arrivo_nuovo_mondo(stato_partita, capitano)
            if risultato is False:
                return
            stato_partita["fase"] = "ritorno"

        if stato_partita["fase"] == "ritorno":
            if not viaggio_ritorno(stato_partita, capitano):
                return
            Arrivo_GameOver.conclusione(capitano, stato_partita)

    except InterruptedError:
        cprint("\n\n⏸️   GIOCO IN PAUSA (Tasto ESC intercettato)", "yellow", attrs=["bold"])
        nome = input(colored("👉 Inserisci il nome del salvataggio (Invio per automatico): ", "cyan")).strip()
        if not nome:
            nome = f"Salvataggio_{capitano}_{random.randint(100,999)}"
        dati = carica_dati()
        stato_partita["esito"] = "In corso"
        dati["salvataggi"][nome] = {"capitano": capitano, "stato": stato_partita}
        salva_dati(dati)
        cprint(f"\n✅ Partita salvata come '{nome}'!", "green", attrs=["bold"])
        time.sleep(2)

# ==========================================
# MENU PRINCIPALE
# ==========================================

def menu_principale():
    """Menu principale del gioco."""
    while True:
        pulisci_schermo()
        dati = carica_dati()

        cprint("="*60, "cyan", attrs=["bold"])
        cprint("  ☠️    LA MALEDIZIONE D'ORO - MENU PRINCIPALE   ☠️  ", "yellow", "on_grey", attrs=["bold"])
        cprint("="*60, "cyan", attrs=["bold"])

        print(colored("  1.", "magenta", attrs=["bold"]) + " 🏴‍☠️  Nuova Partita")

        salvataggi_in_corso = {k: v for k, v in dati["salvataggi"].items()
                               if v["stato"].get("esito") == "In corso"}

        if salvataggi_in_corso:
            print(colored("  2.", "magenta", attrs=["bold"]) + f" ⚓ Continua Partita ({len(salvataggi_in_corso)} salvatagg{'io' if len(salvataggi_in_corso)==1 else 'i'})")
        else:
            print(colored("  2.", "dark_grey") + " ⚓ Continua Partita (Nessun salvataggio)")

        print(colored("  3.", "magenta", attrs=["bold"]) + " 📊 Statistiche Globali")
        print(colored("  4.", "magenta", attrs=["bold"]) + " 🔍 Esplora Archivi Partita")
        print(colored("  0.", "magenta", attrs=["bold"]) + " 🚪 Esci dal Gioco")

        scelta = input(colored("\n👉 Scegli un'opzione: ", "magenta", attrs=["bold"])).strip()

        if scelta == "1":
            esegui_partita(nuova=True)

        elif scelta == "2":
            if not salvataggi_in_corso:
                cprint("\n❌ Inizia prima una nuova avventura!", "red")
                time.sleep(1.5)
            else:
                pulisci_schermo()
                print("\n⚓ Salvataggi disponibili:\n")
                nomi = list(salvataggi_in_corso.keys())
                for i, n in enumerate(nomi, 1):
                    sv = salvataggi_in_corso[n]
                    fase = sv['stato'].get('fase', '?')
                    budget = sv['stato'].get('budget', 0)
                    print(f"  {i}. {n}")
                    print(f"     Capitano: {sv['capitano']} | Fase: {fase} | Budget: {budget:.0f}🪙")
                    print()
                scelta_s = input(colored("👉 Numero o nome del salvataggio: ", "cyan")).strip()
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
            print("\n🔍 --- ARCHIVI PARTITA ---\n")
            if not dati["salvataggi"]:
                cprint("❌ Nessuna partita negli archivi.", "red")
                time.sleep(1.5)
                continue
            nomi_archivi = list(dati["salvataggi"].keys())
            for i, n in enumerate(nomi_archivi, 1):
                esito = dati["salvataggi"][n]["stato"].get("esito", "Sconosciuto")
                capitano_arch = dati["salvataggi"][n]["capitano"]
                print(f"  {i}. {n}  [{esito}]  — Cap. {capitano_arch}")
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
                print(f"🏴‍☠️  Capitano: {s['capitano']} | 📌 Esito: {sp.get('esito','?')} | 🗺️  Fase: {sp.get('fase','?')}")
                print()
                cprint("💰 RISORSE:", "green")
                print(f"  🪙 Budget: {sp.get('budget', 0):.0f}")
                for cat, qty in sp.get('scorte', {}).items():
                    print(f"  {cat.capitalize()}: {qty:.1f}")
                print(f"  🛡️  Integrità: {sp.get('integrita',100)}%")
                print(f"  ⚠️  Punti Ammutinamento: {sp.get('punti_ammutinamento',0)}")
                print(f"  🗓️  Settimane percorse: {sp.get('settimane_percorse', 0)}")
                print()
                cprint("👥 EQUIPAGGIO:", "cyan")
                for ruolo, n_p in sp.get('equipaggio', {}).items():
                    if n_p > 0:
                        print(f"  {Stati_Ingaggio.NOMI_RUOLO.get(ruolo, ruolo)}: {n_p}")
                print()
                cprint("📦 MERCI:", "magenta")
                for merce, qty in sp.get('merci', {}).items():
                    if qty > 0:
                        print(f"  {merce}: {qty}")
                cprint("🔮 RISORSE BARATTO:", "yellow")
                for r, qty in sp.get('risorse_baratto', {}).items():
                    if qty > 0:
                        print(f"  {r.capitalize()}: {qty:.1f}")
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