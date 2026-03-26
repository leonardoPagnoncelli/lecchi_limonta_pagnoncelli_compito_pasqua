import random
import sys
import time

try:
    import msvcrt  # Funziona su Windows
    is_windows = True
except ImportError:
    import select  # Funziona su Mac e Linux
    is_windows = False

def stampa_lenta(testo, ritardo=0.03):
    """Stampa il testo un carattere alla volta. Premi Invio per skippare."""
    salta_animazione = False
    
    # Svuotiamo il buffer di Windows prima di iniziare la riga per evitare skip involontari
    if is_windows:
        while msvcrt.kbhit():
            msvcrt.getch()

    for carattere in testo:
        # Se non abbiamo ancora skippato, controlliamo se l'utente preme Invio
        if not salta_animazione:
            if is_windows:
                if msvcrt.kbhit():
                    tasto = msvcrt.getch()
                    # b'\r' è il tasto Invio su Windows
                    if tasto in (b'\r', b'\n'):
                        salta_animazione = True
            else:
                # Su Mac/Linux 'select' vede se c'è qualcosa in coda su stdin
                i, o, e = select.select([sys.stdin], [], [], 0)
                if i:
                    sys.stdin.readline() # Consuma l'Invio per non farlo apparire nell'input successivo
                    salta_animazione = True
                    
        sys.stdout.write(carattere)
        sys.stdout.flush()
        
        # Aspettiamo solo se l'utente non ha deciso di saltare
        if not salta_animazione:
            time.sleep(ritardo)
            
    print()

def inizia_gioco():
    budget = 2000
    equipaggio = {"marinai": 0, "carpentieri": 0, "cuochi": 0, "medici": 0, "navigatori": 0}
    attrezzature = {"armi": False, "attrezzi_carpentiere": False, "kit_medico": False, "strumenti_navigazione": False}
    
    costo_membro = 50
    costo_attrezzatura = 150
    
    print("="*60)
    print("      VERSO IL NUOVO MONDO: SANGUE, SALE E SPEZIE")
    print("="*60)
    
    stampa_lenta("Siviglia, 1519. L'aria del porto è un miasma denso di pesce marcio, catrame bollente e disperazione.")
    stampa_lenta("I creditori bussano alla tua porta. La prigione per debiti ti aspetta, a meno che tu non compia un miracolo.")
    stampa_lenta("Di fronte a te, cullato da acque scure, riposa il possente galeone 'La Maledizione d'Oro'.")
    stampa_lenta("La spietata Gilda dei Mercanti ti ha finanziato un'ultima, suicida spedizione verso l'ignoto.")
    stampa_lenta("Il tuo obiettivo: trovare l'Isola del Sole, strappare le spezie ai selvaggi e tornare vivo.")
    
    capitano = input("Capitano, qual è il tuo nome? ").strip().capitalize()
    
    stampa_lenta(f"Che Dio abbia pietà della tua anima, Capitano {capitano}.")
    
    # --- 1. RECLUTAMENTO EQUIPAGGIO ---
    print("--- LA TAVERNA DEL PORTO (ARRUOLAMENTO) ---")
    stampa_lenta("Entri in una bettola fumosa. Facce sfregiate e ubriachi ti fissano. È ora di formare la ciurma.")
    print(f"Budget: {budget} denari. Massimo 16 membri. Costo contratto: {costo_membro} denari.")
    print("Ruoli: marinai, carpentieri, cuochi, medici, navigatori.")
    
    while sum(equipaggio.values()) < 16 and budget >= costo_membro:
        print(f"Ciurma: {sum(equipaggio.values())}/16 | Monete: {budget}")
        scelta = input("Chi assoldi? (scrivi il ruolo, o 'fine' per uscire): ").lower().strip()
        
        if scelta == 'fine':
            break
        elif scelta in equipaggio:
            equipaggio[scelta] += 1
            budget -= costo_membro
            print(f"Un {scelta[:-1]}o/a firma il contratto col sangue.")
        else:
            print("Non ci sono uomini con quel mestiere qui. Riprova.")
            
    if sum(equipaggio.values()) == 0:
        stampa_lenta("Senza una ciurma, i tuoi creditori ti raggiungono sul molo. Finisci i tuoi giorni a marcire in galera.")
        print("=== GAME OVER ===")
        sys.exit()

    # --- 2. L'ARSENALE (ACQUISTO ATTREZZATURE) ---
    print("--- L'ARSENALE DELLA GILDA ---")
    stampa_lenta("Avere uomini non basta. Un medico senza bisturi è solo un prete, un soldato senza spada è un cadavere.")
    print(f"Monete rimaste: {budget}")
    print(f"Ogni cassa di equipaggiamento costa {costo_attrezzatura} denari.")
    
    for equip in attrezzature.keys():
        if budget >= costo_attrezzatura:
            scelta_eq = input(f"Vuoi comprare '{equip.replace('_', ' ').title()}'? (s/n): ").lower().strip()
            if scelta_eq == 's':
                attrezzature[equip] = True
                budget -= costo_attrezzatura
                print(f"Acquistato: {equip.replace('_', ' ').upper()}!")
        else:
            print("Non hai più denari sufficienti per le attrezzature rimanenti.")
            break

    # --- 3. LA CAMBUSA (CIBO E ACQUA) ---
    costo_cibo = 2  
    costo_acqua = 1 
    
    print("--- IL MERCATO NERO (SCORTE) ---")
    stampa_lenta("Il viaggio di andata è un inferno di 8 settimane. L'Oceano non fa sconti. Scegli bene, o mangerete i topi.")
    print(f"Ciurma: {sum(equipaggio.values())} anime affamate. Budget rimasto: {budget} denari.")
    
    try:
        cibo_acquistato = int(input(f"Unità di cibo (carne salata, gallette) ({costo_cibo} monete/u): "))
        acqua_acquistata = int(input(f"Unità di acqua (barili sigillati) ({costo_acqua} monete/u): "))
    except ValueError:
        print("Il mercante ti inganna. Ottieni scorte minime.")
        cibo_acquistato, acqua_acquistata = 10, 10

    costo_totale_scorte = (cibo_acquistato * costo_cibo) + (acqua_acquistata * costo_acqua)
    
    if costo_totale_scorte > budget:
        print("I mercanti sputano a terra. Non hai le monete! Caricano a bordo ciò che puoi permetterti.")
        cibo = budget // 3
        acqua = budget // 3
        budget = 0
    else:
        cibo = cibo_acquistato
        acqua = acqua_acquistata
        budget -= costo_totale_scorte
        
    stampa_lenta(f"Le stive vengono sprangate. Parti con {cibo} razioni, {acqua} barili d'acqua e {budget} monete nascoste nel tuo farsetto.")

    # --- INIZIO VIAGGIO ---
    consumo_settimanale_cibo = sum(equipaggio.values()) * 1  
    consumo_settimanale_acqua = sum(equipaggio.values()) * 2 
    
    print("="*60)
    stampa_lenta("IL MARE APERTO! L'ancora viene strappata dal fango. Si salpa verso l'ignoto.")
    print("="*60)

    for settimana in range(1, 9):
        print(f"--- SETTIMANA {settimana} DI ANDATA ---")
        
        if settimana == 1:
            stampa_lenta("I primi giorni sono euforici, ma al quarto giorno, il mare si tinge di un nero catrame.")
            stampa_lenta("Un leviatano di nuvole cariche di fulmini avanza ruggendo verso di voi. È l'Ira del Leviatano, una tempesta spaventosa.")
            scelta_1 = input("Ordini? Attraversarla a viso aperto (T) o tentare una disperata virata per evitarla (E)? ").upper().strip()
            
            if scelta_1 == 'T':
                stampa_lenta("Il galeone si schianta contro onde alte come cattedrali. Il legno geme in agonia.")
                if equipaggio["carpentieri"] > 0 and attrezzature["attrezzi_carpentiere"]:
                    stampa_lenta("I carpentieri, armati dei loro pesanti martelli e chiodi di ferro, blindano le paratie e salvano la nave dal disastro!")
                elif equipaggio["carpentieri"] > 0 and not attrezzature["attrezzi_carpentiere"]:
                    stampa_lenta("Hai dei carpentieri, ma a mani nude possono fare poco! Cercano di bloccare le falle con i propri corpi. Perdete molte scorte.")
                    cibo -= 5
                else:
                    stampa_lenta("Lo scafo si squarcia. L'acqua salata inonda la stiva inferiore, mandando in malora preziose provviste e logorando il morale.")
                    cibo -= 8
            elif scelta_1 == 'E':
                if equipaggio["navigatori"] > 0 and attrezzature["strumenti_navigazione"]:
                    stampa_lenta("Il navigatore scruta l'astrolabio e le bussole dorate. Ordina manovre chirurgiche, facendo scivolare la nave fuori dal gorgo!")
                else:
                    stampa_lenta("Scappate alla cieca, in preda al panico. La tempesta vi morde la coda e vi spinge in rotte sconosciute. Vi perdete per giorni nel nulla.")
                    acqua -= 6

        elif settimana == 4:
            stampa_lenta("Il fetore della morte infesta il ponte inferiore. Le gengive degli uomini sanguinano, i denti cadono. È lo Scorbuto Nero.")
            if equipaggio["medici"] > 0 and attrezzature["kit_medico"]:
                stampa_lenta("Il medico di bordo apre i suoi kit: estrae bisturi puliti, erbe medicinali e potenti decotti. L'epidemia viene stroncata sul nascere!")
            elif equipaggio["medici"] > 0 and not attrezzature["kit_medico"]:
                stampa_lenta("Il medico sa cosa fare, ma non ha strumenti né erbe. Riesce solo a confortare i malati pregando per loro. Il morbo si porta via scorte e uomini.")
                cibo -= 4
                equipaggio["marinai"] = max(0, equipaggio["marinai"] - 1)
            else:
                stampa_lenta("L'ignoranza è fatale. I corpi avvolti nel sudario vengono gettati agli squali uno dopo l'altro. La disperazione dilaga.")
                ruoli_con_gente = [r for r in equipaggio if equipaggio[r] > 0]
                if ruoli_con_gente:
                    sfortunato = random.choice(ruoli_con_gente)
                    equipaggio[sfortunato] -= 1
                    print(f"Il mare si è preso un {sfortunato[:-1]}o/a.")

        else:
            stampa_lenta("La vastità dell'oceano minaccia di far impazzire la ciurma. Solo il rumore delle onde rompe il silenzio tombale.")
            
        input(" -> Premi Invio per chiudere il diario di bordo della settimana...")
        
        # Aggiornamento consumi (se qualcuno è morto)
        consumo_settimanale_cibo = sum(equipaggio.values()) * 1
        consumo_settimanale_acqua = sum(equipaggio.values()) * 2
        
        cibo -= consumo_settimanale_cibo
        acqua -= consumo_settimanale_acqua
        
        if cibo < 0 or acqua < 0:
            stampa_lenta("Le botti sono aride. La pancia è un buco nero. Nel cuore della notte, senti passi pesanti fuori dalla tua cabina.")
            stampa_lenta("La porta viene sfondata. Uomini dagli occhi spiritati ti trascinano sul ponte. L'Ammutinamento è compiuto.")
            print("=== GAME OVER ===")
            sys.exit()

    # --- 4. IL NUOVO MONDO E LA TRIBU' ---
    print("="*60)
    stampa_lenta("TERRA IN VISTA! Dalla nebbia emerge l'Isola del Sole. Una giungla verde smeraldo che trasuda umidità letale.")
    print("="*60)
    
    stampa_lenta("L'aria è soffocante, ma densa di un aroma che fa venire l'acquolina in bocca all'avidità: spezie pure e intatte.")
    stampa_lenta("Appena sbarcate sulla sabbia vulcanica, il silenzio della giungla si infrange. Centinaia di guerrieri emergono dall'ombra.")
    stampa_lenta("Hanno maschere d'osso, corpi ricoperti di pitture di guerra e impugnano pesanti mazze d'ossidiana letali.")
    stampa_lenta("Dietro di loro, immense ceste traboccano di cannella, chiodi di garofano e pepe nero. Il tesoro per cui siete venuti.")
    
    spezie = False
    
    while True:
        scelta_villaggio = input("Un passo falso e siete morti. Ordini? CONTRATTARE (C) o ATTACCARE (A)? ").upper().strip()
        
        if scelta_villaggio == 'A':
            stampa_lenta("L'avidità vince. Sguaini la spada e urli: 'UCCIDETELI TUTTI! PRENDETE LE SPEZIE!'")
            stampa_lenta("È un massacro confuso. Sabbia, sangue e urla animalesche.")
            
            forza = random.randint(1, 10) + (equipaggio["marinai"] * 2)
            if attrezzature["armi"]: forza += 5
            
            if forza > 8: 
                stampa_lenta("Il rimbombo assordante dei vostri moschetti terrorizza i selvaggi. Le vostre lame d'acciaio fanno scempio delle loro lance.")
                stampa_lenta("Li mettete in rotta. Camminando sui cadaveri, riempite brutalmente le scialuppe di spezie e tesori.")
                spezie = True
                budget += 400 
            else:
                stampa_lenta("Un massacro, ma siete voi le vittime. La loro ferocia è inumana. Vi circondano e vi spezzano le ossa.")
                stampa_lenta("Fuggite in preda al terrore verso il galeone, lasciando la spiaggia rossa del sangue dei vostri compagni.")
                for ruolo in equipaggio:
                    equipaggio[ruolo] //= 2
            break
            
        elif scelta_villaggio == 'C':
            stampa_lenta("Alzi lentamente le mani vuote. Avanzi sudando freddo, seguito da due marinai che trasportano forzieri traboccanti di doni.")
            
            diplomazia = random.randint(1, 10) + (equipaggio["navigatori"] * 2)
            
            if diplomazia > 5: 
                costo_spezie = 200
                if budget >= costo_spezie:
                    stampa_lenta(f"Il capo tribù analizza i vostri tessuti, specchi e coltelli. I suoi occhi brillano. L'accordo è sancito per l'equivalente di {costo_spezie} monete.")
                    stampa_lenta("Una pace fragile ma proficua. Svuotano le loro riserve per riempire le vostre stive. Avete il carico prezioso!")
                    budget -= costo_spezie
                    spezie = True
                else:
                    stampa_lenta("Mostri le tue misere offerte. Il capo scoppia in una risata gutturale, calcia i forzieri e ordina ai suoi di puntarvi le lance alla gola. Siete cacciati via come cani.")
            else:
                stampa_lenta("Mentre porgi un dono, un tuo marinaio starnutisce per le spezie. Il gesto viene interpretato come l'evocazione di uno spirito maligno!")
                stampa_lenta("Le lance volano. Siete fortunati a raggiungere vivi le scialuppe, senza un singolo grammo di spezie.")
            break
        else:
            print("Non balbettare, Capitano! 'C' per la pace, 'A' per il sangue.")

    consumo_settimanale_cibo = sum(equipaggio.values()) * 1
    consumo_settimanale_acqua = sum(equipaggio.values()) * 2

    # --- 5. IL VIAGGIO DI RITORNO ---
    print("="*60)
    stampa_lenta("IL RITORNO. Le stive impregnano la nave di un profumo esotico. Ma l'Oceano vi guarda ancora con fame famelica.")
    print("="*60)
    
    for settimana in range(1, 9):
        print(f"--- SETTIMANA {settimana} DI RITORNO ---")
        
        if settimana == 5 and spezie:
            stampa_lenta("Un colpo di cannone fende l'aria. Una palla di ghisa disintegra la murata di dritta in una pioggia di schegge letali!")
            stampa_lenta("Pirati della Fratellanza Oscura! Hanno fiutato l'odore della vostra ricchezza e issato la bandiera nera.")
            
            if equipaggio["marinai"] > 0 and attrezzature["armi"]:
                stampa_lenta("Ordini di rispondere al fuoco! I tuoi marinai imbracciano i moschetti e respingono i corsari con una pioggia di piombo sanguinosa. Siete salvi.")
            elif equipaggio["carpentieri"] > 0 and attrezzature["attrezzi_carpentiere"]:
                stampa_lenta("I pirati vi danneggiano gravemente prima di rinunciare all'inseguimento, ma i carpentieri riparano la nave mentre fuggite disperatamente.")
                acqua -= 4
            else:
                stampa_lenta("I bucanieri abbordano! Combattono con sciabole e asce, massacrando chi si oppone. Rubano dalle stive e appiccano piccoli fuochi prima di andarvene.")
                cibo //= 2
                acqua //= 2
                print("Le vostre fatiche vanno in fumo. Scorte dimezzate.")
                
        else:
            stampa_lenta("Le vele sono strappate, le assi marce. Gli uomini sono spettri scheletrici dagli occhi infossati. Si va avanti per inerzia.")
            
        input(" -> Premi Invio. Non c'è tempo da perdere...")
        
        cibo -= consumo_settimanale_cibo
        acqua -= consumo_settimanale_acqua
        
        if cibo < 0 or acqua < 0:
            stampa_lenta("Proprio quando l'odore della terraferma inizia a sentirsi, l'ultima goccia d'acqua scende in una gola riarsa. È la fine.")
            stampa_lenta("Il maestoso galeone diventa una gigantesca tomba di legno fluttuante, cullata dall'Oceano spietato.")
            print("=== GAME OVER ===")
            sys.exit()

    # --- 6. CONCLUSIONE ---
    print("="*60)
    stampa_lenta(f"LE CAMPANE DI SIVIGLIA! Capitano {capitano}, avete ingannato la Morte Nera in persona!")
    print("="*60)
    
    stampa_lenta("La folla ammutolisce nel vedere lo stato spettrale della vostra nave. Siete dei fantasmi ritornati dall'inferno.")
    
    if spezie:
        guadagno_spezie = 2000 
        budget += guadagno_spezie
        stampa_lenta("Ma quando gli addetti aprono le stive, il profumo esotico inonda l'intera città. I mercanti si mettono a urlare, folli di avidità.")
        stampa_lenta(f"I forzieri si riempiono di nuovo. Hai venduto il sangue e il sudore della ciurma per {guadagno_spezie} denari d'oro!")
        
    print(f"BILANCIO FINALE DELLA COMPAGNIA: {budget} denari.")
    
    if spezie and budget > 2000:
        print("👑 VITTORIA EPICA (3/3) 👑")
        stampa_lenta("Ripaghi i tuoi debiti e diventi ricco oltre ogni immaginazione. Compri ville, terre e titoli nobiliari.")
        stampa_lenta("La tua storia sarà sussurrata in ogni taverna del mondo per i secoli a venire. L'Eroe dell'Oceano.")
    elif spezie and budget <= 2000:
        print("⚖️ VITTORIA DI PIRRO (2/3) ⚖️")
        stampa_lenta("Le spezie bastano a malapena a placare le fauci dei creditori della Gilda. I tuoi debiti sono estinti.")
        stampa_lenta("Torni al porto natio da uomo libero, ma povero in canna e perseguitato dagli incubi della giungla.")
    else:
        print("💀 ROVINA TOTALE (1/3) 💀")
        stampa_lenta("Il viaggio è stato un disastro commerciale. Sei sopravvissuto, ma la Gilda no. Le guardie reali ti attendono al molo.")
        stampa_lenta("La prigione per debiti ha porte pesanti. E si chiudono alle tue spalle, per sempre.")

if __name__ == "__main__":
    inizia_gioco()