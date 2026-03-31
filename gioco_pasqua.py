import random
import sys
import time
from termcolor import colored, cprint

try:
    import msvcrt
    is_windows = True
except ImportError:
    import select
    is_windows = False

# ==========================================
# FUNZIONI DI UTILI E STAMPA
# ==========================================

def stampa_lenta(testo, colore=None, attributi=None, ritardo=0.03):
    """Stampa il testo un carattere alla volta, supportando i colori di termcolor."""
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
        
        # Applica il colore al singolo carattere se specificato
        char_da_stampare = colored(carattere, colore, attrs=attributi) if colore else carattere
        sys.stdout.write(char_da_stampare)
        sys.stdout.flush()
        
        if not salta_animazione:
            time.sleep(ritardo)
            
    print()

def game_over(messaggio):
    """Gestisce la fine prematura del gioco."""
    print()
    cprint("="*60, "red", attrs=["bold"])
    stampa_lenta(messaggio, "red")
    cprint("\n💀 === GAME OVER === 💀\n", "red", attrs=["bold", "blink"])
    cprint("="*60, "red", attrs=["bold"])
    sys.exit()

def stampa_risorse(stato):
    cprint(f"👥 Ciurma: {sum(stato['equipaggio'].values())}/16 | 🪙 Budget: {stato['budget']} | 🥩 Cibo: {stato['cibo']} | 💧 Acqua: {stato['acqua']}", "cyan", attrs=["bold"])

def variazione_stat(messaggio, colore):
    cprint(f"  {messaggio}", colore, attrs=["bold"])

# ==========================================
# EVENTI CASUALI
# ==========================================

def evento_1_calma_piatta(stato):
    stampa_lenta("☀️ Il vento muore con un ultimo, debole sospiro. L'oceano diventa uno specchio d'olio nero.", "yellow")
    stampa_lenta("Siete prigionieri della 'Calma Piatta'. Il sole a picco trasforma il ponte in una piastra rovente.", "yellow")
    
    scelta = input(colored("👉 [N] Affidati al Navigatore | [R] Fai remare i marinai | [A] Attendi pregando: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'N':
        if stato['equipaggio']['navigatori'] > 0 and stato['attrezzature']['strumenti_navigazione']:
            stampa_lenta("🧭 Il navigatore calcola l'incalcolabile. Intercetta una microscopica corrente sottomarina che vi salva!", "green")
            stato['acqua'] -= 1
            variazione_stat("📉 -1 💧 Acqua", "red")
        else:
            stampa_lenta("❌ Non hai un navigatore o gli strumenti! Girate in tondo come folli. Sete atroce.", "red")
            stato['acqua'] -= 5
            variazione_stat("📉 -5 💧 Acqua", "red")
    elif scelta == 'R':
        if stato['equipaggio']['marinai'] >= 2:
            stampa_lenta("🛶 I marinai trainano il galeone a forza di braccia sotto un sole assassino. Una fatica immane, ma ne uscite.", "green")
            stato['cibo'] -= 3
            stato['acqua'] -= 1
            variazione_stat("📉 -3 🥩 Cibo | -1 💧 Acqua", "red")
        else:
            stampa_lenta("💀 I pochi uomini che hai crollano svenuti sui remi per i colpi di calore.", "red")
            stato['acqua'] -= 4
            variazione_stat("📉 -4 💧 Acqua", "red")
    else:
        stampa_lenta("⏳ L'inerzia vi condanna. Bevete l'acqua putrida dal fondo dei barili, piena di vermi.", "red")
        stato['acqua'] -= 4
        variazione_stat("📉 -4 💧 Acqua", "red")

def evento_2_relitto(stato):
    stampa_lenta("🏚️ La nebbia si alza. A un miglio dondola la sagoma spettrale di una caravella. Odora di morte e spezie.", "cyan")
    
    scelta = input(colored("👉 [E] Esplora con cautela | [S] Saccheggia in fretta | [I] Ignora il relitto: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'E':
        if stato['equipaggio']['marinai'] > 0 and stato['attrezzature']['armi']:
            stampa_lenta("⚔️ I tuoi uomini sbarcano armati. Uccidono i sopravvissuti impazziti e prendono scorte intatte!", "green")
            stato['cibo'] += 5
            stato['acqua'] += 5
            variazione_stat("📈 +5 🥩 Cibo | +5 💧 Acqua", "green")
        else:
            stampa_lenta("🩸 Mandi uomini indifesi. I cannibali tendono un'imboscata nel buio della stiva!", "red")
            stato['equipaggio']['marinai'] = max(0, stato['equipaggio']['marinai'] - 1)
            variazione_stat("💀 Hai perso 1 Marinaio", "red")
    elif scelta == 'S':
        if random.random() > 0.5:
            stampa_lenta("🏃 Veloci come topi, arraffate qualche barile dal ponte superiore prima che affondi.", "green")
            stato['cibo'] += 2
            stato['acqua'] += 2
            variazione_stat("📈 +2 🥩 Cibo | +2 💧 Acqua", "green")
        else:
            stampa_lenta("🌊 L'avidità è fatale! Il fasciame marcio cede e un uomo annega trascinato dal peso.", "red")
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            if ruoli_vivi:
                sfortunato = random.choice(ruoli_vivi)
                stato['equipaggio'][sfortunato] -= 1
                variazione_stat(f"💀 Hai perso 1 {sfortunato[:-1].capitalize()}o/a", "red")
    else:
        stampa_lenta("🌫️ Ordini di tirare dritto. Lasciate i morti ai morti.", "cyan")

def evento_3_sirene(stato):
    stampa_lenta("🧜‍♀️ Un banco di nebbia luminescente vi avvolge. Si alza un canto etereo che spezza la mente.", "cyan")
    stampa_lenta("I marinai iniziano a camminare in bilico sulle ringhiere, attirati dall'acqua nera.", "yellow")
    
    scelta = input(colored("👉 [C] Grog del Cuoco | [F] Spara in aria (Armi) | [L] Legali agli alberi: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'C':
        if stato['equipaggio']['cuochi'] > 0:
            stampa_lenta("🍲 Il cuoco vi fa bere un intruglio bruciante di peperoncino e grasso. L'incantesimo si spezza!", "green")
        else:
            stampa_lenta("🦈 Senza un cuoco, non riesci a svegliarli. Senti i tonfi in acqua. Gli squali pasteggiano.", "red")
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            if ruoli_vivi: 
                sfortunato = random.choice(ruoli_vivi)
                stato['equipaggio'][sfortunato] -= 1
                variazione_stat(f"💀 Hai perso 1 {sfortunato[:-1].capitalize()}o/a", "red")
    elif scelta == 'F':
        if stato['attrezzature']['armi']:
            stampa_lenta("💥 Sguaini le pistole e spari! Il frastuono del piombo sovrasta il canto mortale.", "green")
        else:
            stampa_lenta("🩸 Non hai armi. Le urla sono inutili. Alcuni si gettano in pasto agli squali.", "red")
            ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
            if ruoli_vivi: 
                sfortunato = random.choice(ruoli_vivi)
                stato['equipaggio'][sfortunato] -= 1
                variazione_stat(f"💀 Hai perso 1 {sfortunato[:-1].capitalize()}o/a", "red")
    else:
        stampa_lenta("🪢 Lotti per legarli. Si dimenano come demoni, spaccando barili d'acqua nella loro furia.", "yellow")
        stato['acqua'] -= 3
        variazione_stat("📉 -3 💧 Acqua", "red")

def evento_4_topi(stato):
    stampa_lenta("🐀 Migliaia di squittii frenetici provengono dalla stiva. Un'orda di ratti neri attacca le gallette!", "yellow")
    
    scelta = input(colored("👉 [M] Marinai all'attacco | [V] Veleno del Medico | [S] Sigilla le paratie: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'M':
        if stato['equipaggio']['marinai'] >= 2:
            stampa_lenta("🏏 I marinai scendono armati di randelli chiodati. È un massacro nel buio, ma salvate quasi tutto.", "green")
            stato['cibo'] -= 1
            variazione_stat("📉 -1 🥩 Cibo", "red")
        else:
            stampa_lenta("🩸 L'orda è inarrestabile. I pochi che scendono vengono morsi fino all'osso.", "red")
            stato['cibo'] -= 5
            variazione_stat("📉 -5 🥩 Cibo", "red")
    elif scelta == 'V':
        if stato['equipaggio']['medici'] > 0 and stato['attrezzature']['kit_medico']:
            stampa_lenta("🧪 Il medico getta esche avvelenate. I ratti muoiono, ma parte del cibo è contaminato.", "yellow")
            stato['cibo'] -= 3
            variazione_stat("📉 -3 🥩 Cibo", "red")
        else:
            stampa_lenta("❌ Senza cure chimiche, guardate impotenti i ratti divorare il vostro futuro.", "red")
            stato['cibo'] -= 5
            variazione_stat("📉 -5 🥩 Cibo", "red")
    else:
        stampa_lenta("🚪 Sbarri la botola dall'esterno. Ascolti i mostri rosicchiare le vostre speranze.", "red")
        stato['cibo'] -= 6
        variazione_stat("📉 -6 🥩 Cibo", "red")

def evento_5_vento_perfetto(stato):
    stampa_lenta("🌪️ Il cielo si tinge di viola livido. Il 'Vento del Diavolo' sta per investire le vele.", "cyan")
    
    scelta = input(colored("👉 [C] Cavalca la tempesta (Rischio) | [A] Ammaina le vele e frena: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'C':
        if random.random() > 0.4:
            stampa_lenta("⛵ Azzardo miracoloso! In pochi giorni coprite la distanza di settimane, risparmiando razioni!", "green")
            stato['cibo'] += 4
            stato['acqua'] += 4
            variazione_stat("📈 +4 🥩 Cibo | +4 💧 Acqua", "green")
        else:
            stampa_lenta("🌊 Un'onda anomala spazza il ponte frantumando i barili d'acqua!", "red")
            stato['acqua'] -= 2
            variazione_stat("📉 -2 💧 Acqua", "red")
    else:
        stampa_lenta("⚓ Scelta prudente. Consumate razioni extra per il freddo, ma non perdete vite.", "yellow")
        stato['cibo'] -= 1
        variazione_stat("📉 -1 🥩 Cibo", "red")

def evento_6_scoglio_nascosto(stato):
    stampa_lenta("💥 BOOM! Avete urtato le 'Fauci di Pietra'. L'acqua entra a fiotti nella stiva!", "red", attrs=["bold"])
    
    scelta = input(colored("👉 [C] Carpentieri | [G] Getta il carico | [T] Tappa alla buona: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'C':
        if stato['equipaggio']['carpentieri'] > 0 and stato['attrezzature']['attrezzi_carpentiere']:
            stampa_lenta("🔨 I carpentieri si tuffano nell'acqua gelida. Il blocco di legno e pece tiene. Nave salvata.", "green")
        else:
            stampa_lenta("🌊 L'acqua salata inonda brutalmente le scorte prima che possiate fermare il disastro a mani nude.", "red")
            stato['cibo'] -= 5
            stato['acqua'] -= 4
            variazione_stat("📉 -5 🥩 Cibo | -4 💧 Acqua", "red")
    elif scelta == 'G':
        stampa_lenta("🪙 Urli di buttare in mare i forzieri dell'oro. Il galeone si disincaglia, ma siete più poveri.", "yellow")
        stato['budget'] = max(0, stato['budget'] - 150)
        variazione_stat("📉 -150 🪙 Budget", "red")
    else:
        stampa_lenta("🕳️ Ci buttate sopra vecchie vele. La pressione è schiacciante e le stive si allagano parzialmente.", "yellow")
        stato['cibo'] -= 3
        stato['acqua'] -= 2
        variazione_stat("📉 -3 🥩 Cibo | -2 💧 Acqua", "red")

def evento_7_tentacoli(stato):
    stampa_lenta("🦑 L'oceano ribolle. Due tentacoli colossali si avvolgono attorno all'albero maestro. Il Kraken!", "red", attrs=["bold"])
    
    scelta = input(colored("👉 [F] Fuoco a Volontà (Armi) | [E] Getta l'esca (Cibo): ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'F':
        if stato['attrezzature']['armi'] and stato['equipaggio']['marinai'] > 0:
            stampa_lenta("💥 I moschetti sputano piombo bollente. Il mostro sibila e si inabissa spaventato.", "green")
        else:
            stampa_lenta("🩸 Siete disarmati! Un enorme tentacolo stritola l'albero e frantuma i barili vitali.", "red")
            stato['acqua'] -= 5
            stato['cibo'] -= 3
            variazione_stat("📉 -3 🥩 Cibo | -5 💧 Acqua", "red")
    else:
        stampa_lenta("🥩 Sacrificate enormi quarti di carne salata. Il mostro la divora e vi lascia in pace.", "yellow")
        stato['cibo'] -= 5
        variazione_stat("📉 -5 🥩 Cibo", "red")

def evento_8_febbre(stato):
    stampa_lenta("🤒 La 'Morte Sudata'. Una febbre letale cuoce le persone dall'interno. Il panico dilaga.", "yellow")
    
    scelta = input(colored("👉 [Q] Quarantena (Medici) | [M] Getta i malati in mare | [P] Prega e aspetta: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'Q':
        if stato['equipaggio']['medici'] > 0 and stato['attrezzature']['kit_medico']:
            stampa_lenta("🩸 Il chirurgo estrae salassi letali e brucia incensi. Epidemia domata.", "green")
        else:
            stampa_lenta("🔥 Non avete cure. Bruciate le vesti e il cibo toccato dai malati per sopravvivere.", "red")
            stato['cibo'] -= 5
            variazione_stat("📉 -5 🥩 Cibo", "red")
    elif scelta == 'M':
        stampa_lenta("⚔️ Decisione crudele. I malati vengono spinti in acqua a fil di spada, ancora urlanti.", "red")
        ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
        for _ in range(2):
            if ruoli_vivi:
                sfortunato = random.choice(ruoli_vivi)
                if stato['equipaggio'][sfortunato] > 0:
                    stato['equipaggio'][sfortunato] -= 1
        variazione_stat("💀 Hai perso 2 membri dell'equipaggio", "red")
    else:
        stampa_lenta("🦠 Mentre preghi, il contagio si diffonde contaminando uomini sani e scorte.", "red")
        stato['cibo'] -= 4
        ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
        if ruoli_vivi: 
            sfortunato = random.choice(ruoli_vivi)
            stato['equipaggio'][sfortunato] -= 1
            variazione_stat(f"📉 -4 🥩 Cibo | 💀 Hai perso 1 {sfortunato[:-1].capitalize()}o/a", "red")

def evento_9_mercante_smarrito(stato):
    stampa_lenta("👻 Appare un fluyt olandese. Uno scheletro vi offre scorte squisite in cambio di 150 denari.", "cyan")
    
    scelta = input(colored("👉 [C] Compra (150🪙) | [A] Abborda per rubarle | [I] Ignora il fantasma: ", "magenta", attrs=["bold"])).upper().strip()
    
    if scelta == 'C':
        if stato['budget'] >= 150:
            stampa_lenta("🍞 Getti le monete. Vi lanciano barili di cibo prima che la nave svanisca nel nulla.", "green")
            stato['budget'] -= 150
            stato['cibo'] += 7
            stato['acqua'] += 7
            variazione_stat("📉 -150 🪙 Budget | 📈 +7 🥩 Cibo | +7 💧 Acqua", "green")
        else:
            stampa_lenta("❌ 'L'oceano non fa credito', sussurra lo scheletro. La nave svanisce deridendovi.", "red")
    elif scelta == 'A':
        if stato['equipaggio']['marinai'] >= 2 and stato['attrezzature']['armi']:
            stampa_lenta("⚔️ Abbordo sanguinoso! Erano contrabbandieri travestiti. Prendete il loro cibo e l'oro!", "green")
            stato['cibo'] += 5
            stato['budget'] += 50
            variazione_stat("📈 +50 🪙 Budget | +5 🥩 Cibo", "green")
        else:
            stampa_lenta("💥 Pensi siano deboli, ma ti scagliano contro cannonate! Erano pirati armati.", "red")
            stato['cibo'] -= 4
            stato['acqua'] -= 4
            variazione_stat("📉 -4 🥩 Cibo | -4 💧 Acqua", "red")
    else:
        stampa_lenta("🌫️ La superstizione ti salva la vita. Li guardi scomparire nel grigio dell'oceano.", "cyan")

def gestisci_evento_casuale(stato):
    """Sceglie e avvia un evento casuale e stampa un separatore."""
    cprint("\n" + "~"*60, "blue", attrs=["bold"])
    cprint("⚠️  EVENTO IN MARE!", "yellow", attrs=["bold", "blink"])
    eventi_disponibili = [
        evento_1_calma_piatta, evento_2_relitto, evento_3_sirene,
        evento_4_topi, evento_5_vento_perfetto, evento_6_scoglio_nascosto,
        evento_7_tentacoli, evento_8_febbre, evento_9_mercante_smarrito
    ]
    evento_scelto = random.choice(eventi_disponibili)
    evento_scelto(stato)
    cprint("~"*60, "blue", attrs=["bold"])

# ==========================================
# FASI DI GIOCO
# ==========================================

def introduzione():
    cprint("="*60, "yellow", attrs=["bold"])
    cprint(" ⚓  VERSO IL NUOVO MONDO: SANGUE, SALE E SPEZIE  ⚓ ", "red", "on_grey", attrs=["bold"])
    cprint("="*60, "yellow", attrs=["bold"])
    
    stampa_lenta("\nSiviglia, 1519. L'aria del porto è un miasma denso di pesce marcio, catrame bollente e disperazione.", "cyan")
    stampa_lenta("I creditori bussano alla tua porta. La prigione per debiti ti aspetta, a meno che tu non compia un miracolo.", "cyan")
    stampa_lenta("Di fronte a te riposa il possente galeone 'La Maledizione d'Oro'.", "cyan")
    stampa_lenta("Il tuo obiettivo: trovare l'Isola del Sole, strappare le spezie ai selvaggi e tornare vivo.", "cyan", ["bold"])
    
    capitano = input(colored("\n🏴‍☠️  Capitano, qual è il tuo nome? ", "yellow", attrs=["bold"])).strip().capitalize()
    stampa_lenta(f"Che Dio abbia pietà della tua anima, Capitano {capitano}.", "red", ["bold"])
    return capitano

def fase_arruolamento(stato):
    costo_membro = 50
    stampa_lenta("\nEntri in una bettola fumosa. Facce sfregiate ti fissano. È ora di formare la ciurma.", "cyan")
    
    while sum(stato['equipaggio'].values()) < 16 and stato['budget'] >= costo_membro:
        print()
        stampa_risorse(stato)
        
        # Menu stampato esattamente con lo stile richiesto
        print(colored("\n🍻 -- LA TAVERNA DEL PORTO (ARRUOLAMENTO) --\n", "green", attrs=["bold"]))
        print(f"1. 🪢 Marinaio      (A bordo: {stato['equipaggio']['marinai']})")
        print(f"2. 🔨 Carpentiere   (A bordo: {stato['equipaggio']['carpentieri']})")
        print(f"3. 🍲 Cuoco         (A bordo: {stato['equipaggio']['cuochi']})")
        print(f"4. 🩸 Medico        (A bordo: {stato['equipaggio']['medici']})")
        print(f"5. 🧭 Navigatore    (A bordo: {stato['equipaggio']['navigatori']})")
        print(colored("0. 🚪 Torna al molo (Termina Arruolamento)", "red", attrs=["bold"]))
        
        scelta = input(colored(f"\n👉 Scegli chi assoldare (0-5) [-{costo_membro}🪙]: ", "magenta", attrs=["bold"])).strip()
        
        if scelta == "0":
            stampa_lenta("Smetti di versare rum e ti prepari a lasciare la taverna.", "cyan")
            break
        elif scelta == "1":
            stato['equipaggio']['marinai'] += 1
            stato['budget'] -= costo_membro
            stampa_lenta("✍️ Un Marinaio firma il contratto col sangue.", "green")
        elif scelta == "2":
            stato['equipaggio']['carpentieri'] += 1
            stato['budget'] -= costo_membro
            stampa_lenta("✍️ Un Carpentiere firma il contratto col sangue.", "green")
        elif scelta == "3":
            stato['equipaggio']['cuochi'] += 1
            stato['budget'] -= costo_membro
            stampa_lenta("✍️ Un Cuoco firma il contratto col sangue.", "green")
        elif scelta == "4":
            stato['equipaggio']['medici'] += 1
            stato['budget'] -= costo_membro
            stampa_lenta("✍️ Un Medico firma il contratto col sangue.", "green")
        elif scelta == "5":
            stato['equipaggio']['navigatori'] += 1
            stato['budget'] -= costo_membro
            stampa_lenta("✍️ Un Navigatore firma il contratto col sangue.", "green")
        else:
            cprint("❌ Scelta non valida. I tagliagole al tavolo ridono di te. Scegli un numero dal menù.", "red")
            
    if sum(stato['equipaggio'].values()) == 0:
        game_over("Senza una ciurma, i tuoi creditori ti raggiungono sul molo. La tua gola viene tagliata per un pugno di debiti.")

def fase_arsenale(stato):
    costo_attrezzatura = 150
    cprint("\n⚔️ --- L'ARSENALE DELLA GILDA ---", "green", attrs=["bold"])
    stampa_lenta("Un medico senza bisturi è un prete, un soldato senza spada è un cadavere.", "cyan")
    
    icone_equip = {"armi": "⚔️", "attrezzi_carpentiere": "🔨", "kit_medico": "🩸", "strumenti_navigazione": "🧭"}
    
    for equip in stato['attrezzature'].keys():
        if stato['budget'] >= costo_attrezzatura:
            print()
            stampa_risorse(stato)
            icona = icone_equip.get(equip, "📦")
            scelta_eq = input(colored(f"👉 Vuoi comprare {icona} '{equip.replace('_', ' ').title()}' per {costo_attrezzatura}🪙? (S/N): ", "magenta", attrs=["bold"])).upper().strip()
            if scelta_eq == 'S':
                stato['attrezzature'][equip] = True
                stato['budget'] -= costo_attrezzatura
                cprint(f"✅ Acquistato: {equip.replace('_', ' ').upper()}!", "green", attrs=["bold"])
        else:
            cprint("\n❌ L'armaiolo ti caccia dal negozio. Non hai più denari.", "red")
            break

def fase_mercato_nero(stato):
    costo_cibo = 2  
    costo_acqua = 1 
    
    cprint("\n🐀 --- IL MERCATO NERO (SCORTE) ---", "green", attrs=["bold"])
    stampa_lenta("Il viaggio non perdona. Scegli bene le scorte, o vi mangerete a vicenda.", "cyan")
    print()
    stampa_risorse(stato)
    
    try:
        cibo_acquistato = int(input(colored(f"🥩 Unità di cibo ({costo_cibo}🪙/u): ", "yellow", attrs=["bold"])))
        acqua_acquistata = int(input(colored(f"💧 Unità di acqua ({costo_acqua}🪙/u): ", "cyan", attrs=["bold"])))
    except ValueError:
        cprint("❌ Il mercante ti inganna. Ottieni scorte minime.", "red")
        cibo_acquistato, acqua_acquistata = 10, 10

    costo_totale = (cibo_acquistato * costo_cibo) + (acqua_acquistata * costo_acqua)
    
    if costo_totale > stato['budget']:
        stampa_lenta("🔪 I mercanti sfoderano i coltelli. Non hai l'oro! Caricano solo ciò che puoi permetterti.", "red", ["bold"])
        stato['cibo'] = stato['budget'] // 3
        stato['acqua'] = stato['budget'] // 3
        stato['budget'] = 0
    else:
        stato['cibo'] = cibo_acquistato
        stato['acqua'] = acqua_acquistata
        stato['budget'] -= costo_totale
        
    cprint(f"\n✅ Stive chiuse. Parti con {stato['cibo']}🥩, {stato['acqua']}💧 e {stato['budget']}🪙 restanti.", "green", attrs=["bold"])

def consuma_scorte(stato):
    consumo_cibo = sum(stato['equipaggio'].values()) * 1  
    consumo_acqua = sum(stato['equipaggio'].values()) * 2 
    
    stato['cibo'] -= consumo_cibo
    stato['acqua'] -= consumo_acqua
    
    if stato['cibo'] < 0 or stato['acqua'] < 0:
        return False
    return True

def viaggio_andata(stato):
    print("\n")
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(" IL MARE APERTO! L'ancora viene strappata dal fango.", "cyan", ["bold"])
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    settimane_con_eventi = [2, 4, 6]

    for settimana in range(1, 9):
        cprint(f"\n📅 --- SETTIMANA {settimana} DI ANDATA ---", "yellow", attrs=["bold"])
        stampa_risorse(stato)
        
        if settimana in settimane_con_eventi:
            gestisci_evento_casuale(stato)
        else:
            stampa_lenta("🌅 L'orizzonte è una linea infinita. La navigazione procede senza intoppi mortali.", "cyan")
            
        input(colored("\n📖 [Premi Invio per chiudere il diario di bordo...] ", "dark_grey"))
        
        if not consuma_scorte(stato):
            game_over("Le botti rimbombano vuote. La porta viene sfondata. L'Ammutinamento è compiuto. Ti sgozzano.")

def esplorazione_isola(stato):
    print("\n")
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])
    stampa_lenta(" TERRA IN VISTA! Emerge l'Isola del Sole.", "green", ["bold"])
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])
    
    stampa_lenta("Sbarcate sulla sabbia. Centinaia di guerrieri emergono, dipinti come scheletri.", "yellow")
    stampa_lenta("Dietro di loro, immense ceste di spezie traboccano. La ricchezza assoluta.", "yellow", ["bold"])
    
    while True:
        scelta = input(colored("\n👉 I tamburi battono. [A] Assalta | [C] Contrattare | [F] Furto notturno: ", "magenta", attrs=["bold"])).upper().strip()
        
        if scelta == 'A':
            stampa_lenta("⚔️ 'UCCIDETELI TUTTI!'", "red", ["bold"])
            forza = random.randint(1, 10) + (stato['equipaggio']["marinai"] * 2)
            if stato['attrezzature']["armi"]: forza += 6
            
            if forza > 9: 
                stampa_lenta("💥 I moschetti frantumano le linee. Caricate il sangue e le spezie sulle scialuppe!", "green", ["bold"])
                stato['spezie'] = True
                stato['budget'] += 400 
            else:
                stampa_lenta("💀 Un massacro inimmaginabile. Vi accerchiano e vi frantumano. Fuggite strisciando.", "red", ["bold"])
                for ruolo in stato['equipaggio']:
                    stato['equipaggio'][ruolo] //= 2
            break
            
        elif scelta == 'C':
            stampa_lenta("🤝 Avanzi sudando freddo, offrendo doni.", "cyan")
            diplomazia = random.randint(1, 10) + (stato['equipaggio']["navigatori"] * 2)
            
            if diplomazia > 5: 
                costo_spezie = 200
                if stato['budget'] >= costo_spezie:
                    stampa_lenta(f"✨ Il capo accetta i doni per {costo_spezie}🪙! Le stive si riempiono di oro vegetale.", "green", ["bold"])
                    stato['budget'] -= costo_spezie
                    stato['spezie'] = True
                else:
                    stampa_lenta("❌ Il capo rovescia i forzieri vuoti. Siete cacciati sotto una pioggia di dardi.", "red")
            else:
                stampa_lenta("🩸 Un malinteso scatena l'inferno. Vi lanciate in acqua fuggendo disperati, senza tesoro.", "red")
            break
            
        elif scelta == 'F':
            stampa_lenta("🌙 Attendete la notte profonda.", "cyan")
            if stato['equipaggio']['navigatori'] > 0 and stato['equipaggio']['marinai'] >= 2:
                stampa_lenta("🥷 Scivolate come ombre. Sgozzate le sentinelle e rubate le spezie prima dell'alba!", "green", ["bold"])
                stato['spezie'] = True
                stato['budget'] += 100
            else:
                stampa_lenta("🚨 Calpestate trappole sonore! Il villaggio si sveglia ruggendo. Fuga nel sangue.", "red", ["bold"])
                ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
                for _ in range(3):
                    if ruoli_vivi:
                        sfortunato = random.choice(ruoli_vivi)
                        if stato['equipaggio'][sfortunato] > 0:
                            stato['equipaggio'][sfortunato] -= 1
            break
        else:
            cprint("❌ Il tempo scorre! Inserisci un'opzione valida.", "red")

def viaggio_ritorno(stato):
    print("\n")
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(" IL RITORNO. L'Oceano ha ancora fame.", "cyan", ["bold"])
    cprint("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    
    settimane_con_eventi = [3, 7]

    for settimana in range(1, 9):
        cprint(f"\n📅 --- SETTIMANA {settimana} DI RITORNO ---", "yellow", attrs=["bold"])
        stampa_risorse(stato)
        
        if settimana == 5 and stato['spezie']:
            stampa_lenta("\n🏴‍☠️ Un boato! Vele nere e cannoni d'ottone. I Pirati della Fratellanza Oscura vi braccano!", "red", ["bold", "blink"])
            
            scelta_pirati = input(colored("👉 [C] Combatti | [M] Manovre Evasive | [P] Paga: ", "magenta", attrs=["bold"])).upper().strip()
            
            if scelta_pirati == 'C':
                if stato['equipaggio']["marinai"] > 0 and stato['attrezzature']["armi"]:
                    stampa_lenta("⚔️ Il piombo vola denso. Massacrate gli invasori respingendoli nell'abisso!", "green", ["bold"])
                else:
                    stampa_lenta("🩸 Senza mezzi, è una carneficina. Stuprano le stive e vi portano via tutto.", "red", ["bold"])
                    stato['cibo'] //= 2
                    stato['acqua'] //= 2
                    stato['spezie'] = False
            elif scelta_pirati == 'M':
                if stato['equipaggio']["navigatori"] > 0:
                    stampa_lenta("🧭 Virate verso un banco di scogli! Sfiorate la distruzione, ma i pirati si schiantano!", "green", ["bold"])
                else:
                    stampa_lenta("💥 Vi speronano a tutta velocità. Razziano le vostre risorse vitali.", "red", ["bold"])
                    stato['cibo'] -= 5
                    stato['acqua'] -= 5
            else:
                stampa_lenta("🏳️ Alzi bandiera bianca. Pretendono l'oro e le spezie. L'umiliazione brucia.", "yellow")
                stato['budget'] = 0
                
        elif settimana in settimane_con_eventi:
            gestisci_evento_casuale(stato)
        else:
            stampa_lenta("🌅 Le assi marce gemono. Si va avanti per inerzia, col cuore in gola.", "cyan")
            
        input(colored("\n📖 [Premi Invio, stringendo i denti...] ", "dark_grey"))
        
        if not consuma_scorte(stato):
            game_over("L'ultimo rivolo d'acqua scende nel fango. La disidratazione trasforma tutti in bestie.")

def conclusione(capitano, stato):
    print("\n")
    cprint("🔔" + "="*58 + "🔔", "yellow", attrs=["bold"])
    stampa_lenta(f" LE CAMPANE DI SIVIGLIA! Capitano {capitano}, avete ingannato la Mietitrice.", "yellow", ["bold"])
    cprint("🔔" + "="*58 + "🔔", "yellow", attrs=["bold"])
    
    stampa_lenta("\nLa folla ammutolisce nel vedere il relitto annerito scivolare nel porto.", "cyan")
    
    if stato['spezie']:
        guadagno = 2500 
        stato['budget'] += guadagno
        stampa_lenta(f"📦 Dogana schioda le stive... l'aroma travolge il molo. Guadagni {guadagno}🪙!", "green", ["bold"])
        
    cprint(f"\n📊 BILANCIO FINALE: {stato['budget']}🪙", "cyan", attrs=["bold"])
    
    if stato['spezie'] and stato['budget'] > 2000:
        cprint("\n👑 VITTORIA EPICA (3/3) 👑", "yellow", attrs=["bold", "blink"])
        stampa_lenta("Compri terre aspre, un titolo nobiliare e un'intera flotta mercantile. Sei l'Eroe dell'Oceano.", "green")
    elif stato['spezie']:
        cprint("\n⚖️ VITTORIA DI PIRRO (2/3) ⚖️", "cyan", attrs=["bold"])
        stampa_lenta("Le vendite placano i debitori. Sei libero dalle catene, ma i tuoi forzieri sono vuoti.", "yellow")
    else:
        cprint("\n💀 ROVINA TOTALE (1/3) 💀", "red", attrs=["bold"])
        stampa_lenta("Il viaggio è stato un collasso. Le Guardie Reali ti incatenano. La prigione si chiude per sempre.", "red")
    print()

# ==========================================
# GIOCO PRINCIPALE (MAIN)
# ==========================================

def inizia_gioco():
    stato_partita = {
        "budget": 2000,
        "cibo": 0,
        "acqua": 0,
        "spezie": False,
        "equipaggio": {"marinai": 0, "carpentieri": 0, "cuochi": 0, "medici": 0, "navigatori": 0},
        "attrezzature": {"armi": False, "attrezzi_carpentiere": False, "kit_medico": False, "strumenti_navigazione": False}
    }
    
    capitano = introduzione()
    fase_arruolamento(stato_partita)
    fase_arsenale(stato_partita)
    fase_mercato_nero(stato_partita)
    
    viaggio_andata(stato_partita)
    esplorazione_isola(stato_partita)
    viaggio_ritorno(stato_partita)
    
    conclusione(capitano, stato_partita)

if __name__ == "__main__":
    inizia_gioco()