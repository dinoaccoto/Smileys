import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import os

# Imposta la pagina in modalità "wide" per avere più spazio orizzontale
st.set_page_config(layout="wide")

# Custom CSS per ridurre la spaziatura verticale tra i pulsanti
st.markdown("""
    <style>
    .stButton button {
        margin-top: -10px;
        margin-bottom: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Funzione per generare una faccina
def disegna_faccina(occhi, pbocca):
    # Crea la figura e gli assi
    fig, ax = plt.subplots()

    # Aggiungi faccina (cerchio giallo con bordo nero)
    cerchio = plt.Circle((centro_x, centro_y), raggio_smiley, color="yellow", ec="black", lw=4)
    ax.add_patch(cerchio)

    # Disegna la bocca
    gamma = pbocca
    if gamma != 0:
        raggio_bocca = 1.05 * lam / abs(gamma)  # da modificare in base a gamma
    else:
        raggio_bocca = 1e5
    ang = np.arccos(lam / raggio_bocca)
    if gamma <= 0:  # faccia triste
        angolo_iniziale = ang
        angolo_finale = np.pi - angolo_iniziale
        offset_y = -raggio_bocca
        ulteriore_offset = -raggio_smiley * 0.2
    else:  # faccia felice
        angolo_iniziale = np.pi + ang
        angolo_finale = 2 * np.pi - ang
        offset_y = raggio_bocca
        ulteriore_offset = -raggio_smiley * 0.4

    angoli = np.linspace(angolo_iniziale, angolo_finale, 100)
    x = centro_x + raggio_bocca * np.cos(angoli)
    y = centro_y + offset_y + raggio_bocca * np.sin(angoli) + ulteriore_offset
    ax.plot(x, y, color="black", lw=4)

    # Aggiungo gli occhi
    rp = 2.7
    x_factor = 0.8 * rp * lam / raggio_smiley
    occhio_sin = plt.Circle(
        (centro_x - raggio_smiley / rp * x_factor, centro_y + raggio_smiley / rp),
        raggio_smiley / 12,
        color="black",
    )
    occhio_des = plt.Circle(
        (centro_x + raggio_smiley / rp * x_factor, centro_y + raggio_smiley / rp),
        raggio_smiley / 12,
        color="black",
    )
    ax.add_patch(occhio_sin)
    ax.add_patch(occhio_des)

    # Aggiungo sopracciglia
    x0 = centro_x - raggio_smiley / rp * x_factor
    y0 = centro_y + raggio_smiley / rp + 0.6 * raggio_smiley / rp
    L = raggio_smiley / 4  # lunghezza sopracciglio

    theta_rad = np.radians(occhi)  # converto occhi in radianti
    dx = (L / 2) * np.cos(theta_rad)
    dy = (L / 2) * np.sin(theta_rad)

    x1 = x0 - dx
    y1 = y0 - dy
    x2 = x0 + dx
    y2 = y0 + dy

    ax.plot([x1, x2], [y1, y2], color="black", lw=4)
    # Sopracciglio destro (simmetrico rispetto all'asse y)
    ax.plot([-x1, -x2], [y1, y2], color="black", lw=4)

    # Imposta l'area di plottaggio come quadrata con assi uguali
    ax.set_aspect("equal")
    ax.set_xlim(-lato_figura, lato_figura)
    ax.set_ylim(-lato_figura, lato_figura)
    ax.axis("off")  # Nasconde gli assi

    return fig

# Funzione per creare la figura dal registro delle modifiche
def crea_figura_registro(registro_modifiche, occhi_values, bocca_values, espressioni):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Patch

    # Crea una mappatura dalle espressioni ai colori
    num_colors = len(espressioni)
    cmap = plt.get_cmap('tab10')  # Usa la colormap tab10 con 10 colori distinti
    colors_list = cmap.colors[:num_colors]
    expression_to_color = {expr: colors_list[idx % len(colors_list)] for idx, expr in enumerate(espressioni)}

    # Crea una matrice 2D per le espressioni
    data_matrix = np.empty((len(occhi_values), len(bocca_values)), dtype=object)

    # Mappa i valori di occhi e bocca agli indici
    occhi_to_index = {val: idx for idx, val in enumerate(sorted(occhi_values))}
    bocca_to_index = {val: idx for idx, val in enumerate(sorted(bocca_values))}

    # Riempie la matrice con le espressioni
    for entry in registro_modifiche:
        occhi = entry['occhi']
        bocca = entry['bocca']
        espressione = entry['tasto_premuto']

        i = occhi_to_index[occhi]
        j = bocca_to_index[bocca]
        data_matrix[i, j] = espressione

    # Crea una matrice di colori
    color_matrix = np.empty((len(occhi_values), len(bocca_values), 3))

    for i in range(len(occhi_values)):
        for j in range(len(bocca_values)):
            espressione = data_matrix[i, j]
            if espressione in expression_to_color:
                color_matrix[i, j] = expression_to_color[espressione]
            else:
                color_matrix[i, j] = (1, 1, 1)  # Bianco se non trovato

    # Genera la figura
    fig, ax = plt.subplots()
    ax.imshow(color_matrix, aspect='equal', origin='lower')

    # Imposta le etichette degli assi
    ax.set_xticks(np.arange(len(bocca_values)))
    ax.set_yticks(np.arange(len(occhi_values)))
    ax.set_xticklabels([str(val) for val in sorted(bocca_values)])
    ax.set_yticklabels([str(val) for val in sorted(occhi_values)])

    # Ruota le etichette dell'asse x se necessario
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Crea la legenda e spostala per evitare sovrapposizioni
    legend_elements = [Patch(facecolor=expression_to_color[expr], label=expr) for expr in espressioni]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.15, 1), borderaxespad=0)

    ax.set_xlabel('Valori Bocca')
    ax.set_ylabel('Valori Occhi')
    ax.set_title('Mappa delle espressioni')

    plt.tight_layout()
    return fig

# Inizializza lo stato per la lista, il contatore e il valore di occhi e bocca
if "i" not in st.session_state:
    st.session_state.i = 0

if "smiles_lista" not in st.session_state:
    # Parametri per generare i valori di occhi e bocca
    range_val = 9
    occhi_min = -45.0
    occhi_max = 45.0
    bocca_min = -1.0
    bocca_max = 1.0
    step_occhi = (occhi_max - occhi_min) / (range_val - 1) if range_val > 1 else 0
    step_bocca = (bocca_max - bocca_min) / (range_val - 1) if range_val > 1 else 0

    # Genera la lista di valori per occhi e bocca
    occhi_values = [occhi_min + i * step_occhi for i in range(range_val)]
    bocca_values = [bocca_min + j * step_bocca for j in range(range_val)]

    # Salva in session_state
    st.session_state.occhi_values = occhi_values
    st.session_state.bocca_values = bocca_values

    # Genera la lista di coppie di valori per occhi e bocca e poi randomizza
    st.session_state.smiles_lista = [
        (occhi_val, bocca_val)
        for occhi_val in occhi_values
        for bocca_val in bocca_values
    ]
    random.shuffle(st.session_state.smiles_lista)

# Inizializza il registro delle modifiche se non esiste
if "registro_modifiche" not in st.session_state:
    st.session_state.registro_modifiche = []

# Inizializza lo stato per il flag di log salvato
if "log_salvato" not in st.session_state:
    st.session_state.log_salvato = False

# Parametri della faccina
centro_x = 0.0
centro_y = +3.0
lato_figura = 10
raggio_smiley = 6
lam = raggio_smiley * 0.5  # Semi-larghezza della bocca

# Lista delle espressioni
espressioni = [
    "Triste",
    "Arrabbiata",
    "Preoccupata",
    "Impaurita",
    "Delusa",
    "Felice",
    "Tranquilla",
    "Decisa",
    "Minacciosa",
    "Soddisfatta",
]

# Funzione per gestire il click sul pulsante
def emotion_button_pressed(emotion):
    # Registra l'emozione associata alla faccina corrente
    occhi, bocca = st.session_state.smiles_corrente
    st.session_state.registro_modifiche.append(
        {"tasto_premuto": emotion, "occhi": occhi, "bocca": bocca}
    )
    # Incrementa l'indice per passare alla prossima faccina
    st.session_state.i += 1

# Funzione per salvare il registro su file
def salva_registro(percorso_file):
    try:
        with open(percorso_file, "w", encoding="utf-8") as f:
            for idx, modifica in enumerate(st.session_state.registro_modifiche):
                f.write(
                    f"{idx+1}. Tasto premuto: {modifica['tasto_premuto']}, Occhi: {modifica['occhi']}, Bocca: {modifica['bocca']}\n"
                )
        st.success(f"Registro salvato con successo in {percorso_file}")
        st.session_state.log_salvato = True
    except Exception as e:
        st.error(f"Errore durante il salvataggio del file: {e}")

# Funzione per salvare l'immagine su file
def salva_immagine(fig, percorso_file_img):
    try:
        fig.savefig(percorso_file_img, format='png', bbox_inches='tight')
        st.success(f"Immagine salvata con successo in {percorso_file_img}")
    except Exception as e:
        st.error(f"Errore durante il salvataggio dell'immagine: {e}")

# Controlla se ci sono ancora faccine da mostrare
if st.session_state.i < len(st.session_state.smiles_lista):
    # Ottieni i parametri della faccina corrente
    occhi, bocca = st.session_state.smiles_lista[st.session_state.i]
    st.session_state.smiles_corrente = (occhi, bocca)

    # Disegna la faccina corrente e mostra i pulsanti ai lati
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        # Colonna sinistra per i primi 5 pulsanti
        with col1:
            for espressione in espressioni[:5]:
                st.button(
                    espressione,
                    key=espressione + str(st.session_state.i),
                    on_click=emotion_button_pressed,
                    args=(espressione,),
                )

        # Colonna centrale per la faccina
        with col2:
            st.markdown(
                """
                <div style="display: flex; justify-content: center; align-items: center;">
                """,
                unsafe_allow_html=True,
            )
            fig = disegna_faccina(occhi, bocca)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)

        # Colonna destra per gli ultimi 5 pulsanti
        with col3:
            for espressione in espressioni[5:]:
                st.button(
                    espressione,
                    key=espressione + str(st.session_state.i),
                    on_click=emotion_button_pressed,
                    args=(espressione,),
                )

else:
    st.write("Hai completato tutte le faccine.")

    # Campi di input per il nome del file e il percorso
    st.markdown("### Salva il registro delle modifiche")
    nome_file = st.text_input("Inserisci il nome del file (esempio: registro.txt)", value="registro.txt")
    percorso = st.text_input("Inserisci il percorso dove salvare il file (lascia vuoto per la cartella corrente)", value="")

    # Pulsante per salvare il registro
    if st.button("Salva registro"):
        if nome_file:
            percorso_file = os.path.join(percorso, nome_file)
            salva_registro(percorso_file)
        else:
            st.error("Per favore, inserisci un nome file valido.")

    # Dopo aver salvato il registro, mostra la figura se il registro è stato salvato
    if 'log_salvato' in st.session_state and st.session_state.log_salvato:
        st.markdown("### Mappa delle espressioni")
        fig = crea_figura_registro(
            st.session_state.registro_modifiche,
            st.session_state.occhi_values,
            st.session_state.bocca_values,
            espressioni
        )
        st.pyplot(fig)

        # Campi di input per il nome del file immagine e il percorso
        st.markdown("### Salva l'immagine della mappa")
        nome_file_img = st.text_input("Inserisci il nome del file immagine (esempio: mappa.png)", value="mappa.png")
        percorso_img = st.text_input("Inserisci il percorso dove salvare l'immagine (lascia vuoto per la cartella corrente)", value="")

        # Pulsante per salvare l'immagine
        if st.button("Salva immagine"):
            if nome_file_img:
                percorso_file_img = os.path.join(percorso_img, nome_file_img)
                salva_immagine(fig, percorso_file_img)
            else:
                st.error("Per favore, inserisci un nome file immagine valido.")

# Visualizzazione del registro delle modifiche
st.markdown("### Registro delle modifiche")
for idx, modifica in enumerate(st.session_state.registro_modifiche):
    st.write(
        f"{idx+1} {modifica['tasto_premuto']}- O: {modifica['occhi']} B: {modifica['bocca']}"
    )
