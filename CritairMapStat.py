from get_files_and_clean import Recup_Donneees_VP
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
# en relation avec le changement d'echelle sur l'axe des y pour les barplot
from matplotlib.ticker import FuncFormatter
import gmplot
import folium
from folium.plugins import MarkerCluster
import base64
from io import BytesIO
import json
import imageio.v3 as iio

Recup_Donneees_VP()

p = os.getcwd()

# , dtype={3: str, 4: str})
df_propre = pd.read_csv(
    p + r'/France_data/df_parc_vp_propre_geoloc.csv', index_col=[0], dtype={3: str,4: str, 20: str, 22: str})
#    p + r'/France_data/parc_vp_propre_geoloc_final.csv', index_col=[0], dtype={1: str, 2: str, 20: str})
df_propre[['lattitude', 'longitude']
          ] = df_propre['geo_point_2d'].str.split(',', expand=True)
df_propre[['lattitude', 'longitude']] = df_propre[[
    'lattitude', 'longitude']].astype(float)

def carto(df_commune,file_name,model,Annees_list):

    list_location_folium = []
    list_location_gmap = []
    merged_str_png_html_list =[]
    list_gif_image = []
    html_list = []
    png_html_list = []
    html_list_gmap=[]
    popups_list_html = []
    list_html_gif_annimated = []
    list_png_image = []
    gif_html_list = []
    
    # init google map
    lat0 = df_commune.iloc[0]['lattitude']
    lon0 = df_commune.iloc[0]['longitude']

    # instanciation objets
    gmap = gmplot.GoogleMapPlotter(lat0, lon0, 13)
    m = folium.Map(location=[lat0, lon0], zoom_start=15)
 
    i = 0
    j = 0
    
    for commune in df_commune['commune_de_residence'].unique():
        # print (commune)
        df_commune_unique = df_commune[df_commune['commune_de_residence'] == commune]
        # print ('df_commune_unique',df_commune_unique)
        # df_commune_unique = df_commune[df_commune['commune_de_residence'].isin(commune)]
        # print ('for commune',df_commune)
        lat_gmap = df_commune_unique.iloc[0]['lattitude']
        lon_gmap = df_commune_unique.iloc[0]['longitude']
        
        # location
        location_gmap = lat_gmap,lon_gmap
        list_location_gmap.append(location_gmap)
        print ('list_location_gmap',list_location_gmap)

        shape_commune = df_commune_unique.iloc[0]['geo_shape']
        shape_commune_json = json.loads(shape_commune)
               
        # Récupération des coordonnées du polygone
        polygon_coords = shape_commune_json['coordinates'][0]

        # Séparation des coordonnées en deux listes: lattitudes et longitudes
        lats = [coord[1] for coord in polygon_coords]
        # print(lats)
        lngs = [coord[0] for coord in polygon_coords]
        # print(lngs)

        # Tracé du polygone sur la carte
        gmap.polygon(lats, lngs)
        folium.GeoJson(data=shape_commune_json).add_to(m)
        
        for Annee in Annees_list:
            df_commune_Annee = df_commune_unique[df_commune_unique['Annee'] == Annee]
            # print (df_commune_Annee)
            # print (df_commune_filtered['Annee'])
            #for commune in pd.unique(df_commune_Annee['commune_de_residence']):

            plt.figure(figsize=(2.5, 2.5))
            # Change the font size of the pie chart labels
            plt.rcParams['font.size'] = 8

            df_commune_Annee = df_commune_Annee.reset_index(drop=True)
            # print('df_commune_unique', df_commune_unique)

            explode_index = df_commune_Annee['proportion'].idxmax()

            # Create an "explode" array with a non-zero value for the largest percentage
            explode = [0.1 if i == explode_index else 0 for i in range(len(df_commune_Annee))]
            
            #***********************************************
            print ('df_commune_Annee',df_commune_Annee)
            #***********************************************

            plt.pie(df_commune_Annee['proportion'], labels=df_commune_Annee[model],autopct='%1.1f%%',
                    colors=df_commune_Annee['couleur'], explode=explode, textprops={'color': 'blue'})
            titre = commune+'-'+Annee
            plt.title(titre)

            # Save the plot to a BytesIO object
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            list_png_image.append(img)

            # Encode the image as a base64 string
            png_encoded = base64.b64encode(img.read()).decode()
            
            # Create an HTML img tag using the base64 string of the image contents
            html_png = f'<img src="data:image/png;base64,{png_encoded}">'
            png_html_list.append(html_png)
            html_list.append(html_png)
            
            # png to gif conversion from png img.seek(0)
            gif_image = iio.imread(img)
            list_gif_image.append(gif_image)
            html_gif = f'<img src="data:image/gif;base64,{gif_image}">'
            gif_html_list.append(html_gif)
        

            plt.cla() # clears an axis
            plt.clf() # clears the entire current figure
            plt.close() # closes a window

            lat_folium = df_commune_Annee.iloc[0]['lattitude']
            lon_folium = df_commune_Annee.iloc[0]['longitude']
        
            # location
            location_folium = lat_folium,lon_folium
            list_location_folium.append(location_folium)
            # print ('list_location_folium',list_location_folium)

        gif_annimation_from_list = iio.imwrite("<bytes>", list_gif_image, extension=".gif", duration=1000, loop=0)
        gif_encoded_annimation = base64.b64encode(gif_annimation_from_list).decode('utf-8')
        html_gif_annimated = f'<img src="data:image/gif;base64,{gif_encoded_annimation}">'
        list_html_gif_annimated.append(html_gif_annimated)
        list_gif_image = []

        # ajout du gif annimé a folium et de sa localisation avec les coordonnée de gmap(importtant)
        html_list.append(html_gif_annimated)
        list_location_folium.append((lat_gmap,lon_gmap))

        merged_str_png_html_list.append(''.join(png_html_list))
        png_html_list = []

        # merged_str_png_html_list.append(''.join(gif_html_list))
        # gif_html_list = []

    for html in html_list: 
        popup = folium.Popup(html, max_width=2650)
        popups_list_html.append(popup)
            
    # instance objet marker_cluster pour folium
    marker_cluster = MarkerCluster().add_to(m)

       
    len_popups_list_html = (len(popups_list_html))
    len_list_location_folium = (len(list_location_folium))
    len_list_location_gmap = (len(list_location_gmap))
    len_list_html_gif_annimated = (len(list_html_gif_annimated))
    len_png_html_list = (len(png_html_list))
    len_html_list_gmap = (len(html_list_gmap))
    len_merged_str_png_html_list = (len(merged_str_png_html_list))

    # type_html_list_gmap = (type(html_list_gmap[0]))
    # print ('type_html_list_gmap',type_html_list_gmap)

    len_Annees_list = (len(Annees_list))
    division = int(len_png_html_list//len_Annees_list)
    print ('len_popups_list_html',len_popups_list_html)
    print ('len_list_location_folium',len_list_location_folium)
    print ('len_list_location_gmap',len_list_location_gmap)
    print ('len_list_html_gif_annimated',len_list_html_gif_annimated)
    print ('len_png_html_list',len_png_html_list)
    print ('len_html_list_gmap',len_html_list_gmap)
    print ('len_Annees_list',len_Annees_list)
    print ('division',division)
    print ('len_merged_str_png_html_list',len_merged_str_png_html_list)


    for popup in popups_list_html:
        folium.Marker(list_location_folium[i], popup=popup).add_to(marker_cluster)
        i +=1

    for j in range(len(list_location_gmap)):
        gmap.marker(list_location_gmap[j][0], list_location_gmap[j][1], info_window=merged_str_png_html_list[j]+list_html_gif_annimated[j])

    # Save map
    m.save(file_name+'-'+'folium_map.html')
    # Draw the map to an HTML file
    gmap.draw(file_name+'-'+'google_map.html')

    # gmap sans key
    with open(file_name+'-'+'google_map.html', 'r') as f:
        lines = f.readlines()

    with open(file_name+'-'+'google_map.html', 'w') as f:
        for line in lines:
            if '<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?libraries=visualization"></script>' in line:
                # f.write('<div id="carte"><script src="https://cdn.jsdelivr.net/gh/somanchiu/Keyless-Google-Maps-API@v5.9/mapsJavaScriptAPI.js"async defer></script>')
                f.write('<div id="carte"></div> <script src="gm_keyless.js" async defer></script>')
            else:
                f.write(line)

def y_formatter(y, pos):
    return "{:,}".format(int(y)).replace(',', ' ')
    # return f'{(int(y))}'

# Afficher la variation du nb de VL par crit'air ou par carburant en fonction de la region, du departement, des communes, du type d'energie et de la plage d'annees


def sort_par_model_couleur(df_commune,model):
    if model == 'crit_air':
        model_order = {'Crit\'Air E': 0, 'Crit\'Air 1': 1, 'Crit\'Air 2': 2,
                        'Crit\'Air 3': 3, 'Crit\'Air 4': 4, 'Crit\'Air 5': 5, 'Non classé': 6, 'Inconnu': 7}
        df_commune = df_commune.sort_values(by=[model,'Annee'], key=lambda x: x.map(model_order))
        
        # Define colors for each Crit'Air category
        colors = {"Crit'Air E": 'green', "Crit'Air 1": 'purple', "Crit'Air 2": 'yellow', "Crit'Air 3": 'orange',
        "Crit'Air 4": 'maroon', "Crit'Air 5": 'gray', "Inconnu": 'black', "Non classé": 'brown'}
        
        # Add color column based on Crit'Air category
        df_commune['couleur'] = [colors[x] for x in df_commune[model]]
        return df_commune.reset_index(drop=True)
    
    elif model == 'carburant':
        model_order = {'Electrique et hydrogène': 0, 'Hybride rechargeable': 1, 'Gaz et inconnu': 2,
                        'Essence HNR': 3, 'Diesel HNR': 4, 'Essence': 5, 'Diesel': 6}
        df_commune = df_commune.sort_values(by=[model,'Annee'], key=lambda x: x.map(model_order))

        # Define colors for each Crit'Air category
        colors = {"Electrique et hydrogène": 'green', "Hybride rechargeable": 'purple', "Gaz et inconnu": 'yellow', "Essence HNR": 'orange',
        "Diesel HNR": 'maroon', "Essence": 'gray', "Diesel": 'black'}
        
        # Add color column based on Crit'Air category
        df_commune['couleur'] = [colors[x] for x in df_commune[model]]

        return df_commune.reset_index(drop=True)
    else: print ('model inconnu')


def plot_vehicule_evolution(df_commune, model, region=None, departement=None, commune=None, carburant=None, crit_air=None, depart_Annee=None, fin_Annee=None):
    
    Annees_list = [str(Annee) for Annee in range(depart_Annee, fin_Annee+1)]

    print ('Annees_list ',Annees_list)

    # Transformation du df_communeFrame en un format long en utilisant la fonction melt()
    df_commune = df_commune.melt(id_vars=['region_de_residence',
                          'departement_de_residence',
                          'commune_de_residence',
                          'carburant',
                          'crit_air',
                          'geo_point_2d',
                          'geo_shape',
                          'lattitude',
                          'longitude'],
                 value_vars=Annees_list,
                 var_name='Annee', value_name='nombre de véhicules')
    # print ('df_commune_melted',df_commune)
    # df_commune.to_csv(p + r'/France_df_commune_unique/df_commune_melted_utf-8_b.csv',encoding="utf-8")
    


    l_col = df_commune.columns
    l_Annees = []

    for element in l_col:
        if element.isdigit():
            l_Annees.append(int(element))

    # print(l_Annees)

    # Si les arguments région, département, commune ou type de carburant sont vides,
    # on leur attribue la valeur du filtre correspondant

    if region == None:
        region_str = 'toutes régions'
        list_region = df_propre['region_de_residence'].unique()
    else:
        list_region = region.split(',')
        df_commune = df_commune[df_commune['region_de_residence'].isin(list_region)]
        region_str = ",".join(list_region)
        df_legende = df_commune.iloc[0]
        departement_str = str(df_legende.loc['departement_de_residence'])
        commune_str = str(df_legende.loc['commune_de_residence'])
        
    if departement == None:
        departement_str = 'tous départements'
        list_departement = df_propre['departement_de_residence'].unique()
    else:
        list_departement = departement.split(',')
        df_commune = df_commune[df_commune['departement_de_residence'].isin(list_departement)]
        departement_str = ",".join(list_departement)
        df_legende = df_commune.iloc[0]
        region_str = str(df_legende.loc['region_de_residence'])
        commune_str = str(df_legende.loc['commune_de_residence'])
        
    if commune == None:
        commune_str = 'toutes communes'
        list_commune = df_propre['commune_de_residence'].unique()
    else:
        list_commune = commune.split(',')
        df_commune = df_commune[df_commune['commune_de_residence'].isin(list_commune)]
        commune_str = ",".join(list_commune)
        df_legende = df_commune.iloc[0]
        region_str = str(df_legende.loc['region_de_residence'])
        departement_str = str(df_legende.loc['departement_de_residence'])

    if carburant == None:
        carburant_str = 'tous carburants'
        list_carburant = df_propre['carburant'].unique()
    else:
        list_carburant = carburant.split(',')
        df_commune = df_commune[df_commune['carburant'].isin(list_carburant)]
        carburant_str = ",".join(list_carburant)

    if crit_air == None:
        crit_air_str = "tous Crit'Air"
        list_crit_air = df_propre['crit_air'].unique()
    else:
        list_crit_air = crit_air.split(',')
        df_commune = df_commune[df_commune['crit_air'].isin(list_crit_air)]
        crit_air_str = ",".join(list_crit_air)

    if depart_Annee is None and fin_Annee is None:
        depart_Annee = l_Annees[0]
        fin_Annee = l_Annees[-1]
    if depart_Annee is None:
        depart_Annee = l_Annees[0]
    if fin_Annee is None:
        fin_Annee = l_Annees[-1]

    # Conversion de la colonne Annee en entier
    # df_commune['Annee'] = df_commune['Annee'].astype(int)

    # df_commune.groupby([model])['nombre de véhicules'].sum().plot.pie(autopct='%1.1f%%')

    # df_commune = df_commune.groupby(['Annee', model, 'geo_point_2d', 'lattitude', 'longitude'])['nombre de véhicules'].sum().reset_index()
    df_commune = df_commune.groupby([ model,'Annee', 'departement_de_residence','commune_de_residence','geo_point_2d', 'geo_shape', 'lattitude', 'longitude'])[
        'nombre de véhicules'].agg(['sum', 'mean', 'min', 'max']).reset_index()
    df_commune = df_commune.rename(columns={'sum': 'nombre de véhicules'})

    df_dept = df_commune.groupby([model,'Annee'])['nombre de véhicules'].agg(['sum','max']).reset_index()
    df_dept = df_dept.rename(columns={'sum': 'nombre de véhicules'})
 
    # print(df_commune)

    # df_commune['max'] = df_commune['max'].astype(int)
    # df_legende = df_commune.dropna(subset=['max'])
    df_commune = df_commune.loc[(df_commune['max'] != 0)]
    df_dept = df_dept.loc[(df_dept['max'] != 0)]
    # print (df_dept)
    # df_commune = df_commune.drop(['commune_de_residence','geo_point_2d','geo_shape_commune','lattitude','longitude','mean', 'min', 'max'], axis=1)
    # print ('drop_com',df_commune)
    

    # Tri des données par les colonnes Annee et model
    # df_commune = df_commune.sort_values(by=['Annee', model])
    # df_commune = sort_par_model_couleur(df_commune,model)
    df_dept = sort_par_model_couleur(df_dept,model)
    # print(df_dept)

    # df_commune.to_csv(p + r'/France_df_commune/df_commune_MIN_MAX.csv', encoding="utf-8")
    # print(df_commune)

    # Agrandissement du cadre du graphique

    # fig, ax0 = plt.subplots()
    plt.figure(figsize=(15, 8.5))

    # Création d'un graphique en ligne en utilisant la bibliothèque seaborn
    # sns.lineplot(df_commune=df_commune, x='Annee', y='nombre de véhicules', hue=model)
    # sns.barplot(df_commune=df_commune, x='Annee', y='nombre de véhicules', hue=model)
    # sns.cubehelix_palette(start=2, rot=0, dark=0, light=.95, reverse=True, as_cmap=True)

    # ax = sns.barplot(df_commune=df_commune, x='Annee', y='nombre de véhicules',palette="mako", hue=model)
    # palette = ax.palette('mako').reversed()
    # inverted_palette = sns.color_palette(palette)
    # df_commune_unique0 = df_dept[df_dept[model] == model]
    # pc = df_dept['couleur']
    pc = pd.unique(df_dept['couleur'])
    # print (pc)

    sns.barplot(data=df_dept, x='Annee', y='nombre de véhicules',
                palette=pc, hue=model)
    
    # sns.barplot(df_commune_unique=df_commune, x='Annee', y='nombre de véhicules',
    #             palette=colors, hue=model)

    # sns.barplot(df_commune=df_commune, x='Annee', y='nombre de véhicules',palette="mako", hue=model)#, ax=ax0)

    # ax0.set_ylabel("Sequential")

    # ax1 = ax0.twinx()
    # sns.boxplot(df_commune=df_commune, x='Annee', y='nombre de véhicules',palette="rocket", hue=model, ax=ax1)

    # sns.barplot(df_commune=df_commune, x='Annee', y='nombre de véhicules', hue=model)

    # plt.gca().yaxis.set_ticks(range(0, 100, 10), minor = True)

    # Récupération de l'objet Axes courant
    ax = plt.gca()
    ax.yaxis.set_tick_params(direction='out', length=10, width=5,
                             color='black', labelsize=10, pad=10,
                             labelcolor='blue', right=True, left=True)
    ax.yaxis.set_label_coords(0, 0)

    # Quelle est la variation du nombre de véhicules selon le carburant par région, département, commune ?

    titre = (f"Variation du nombre de véhicules en fonction du type de " +
             f"{model} de {depart_Annee} à {fin_Annee}\n" +
             f"pour {region_str}, {departement_str} / {commune_str} / {crit_air_str}\n" +
             f"{carburant_str}")
    file_name = (f"{model}-{region_str}-{departement_str}-{commune_str}")

    plt.title(titre)

    plt.xlabel('Annee')
    # plt.ylabel('nombre de véhicules',loc='top', rotation=0, fontsize=10, labelpad=-25)
    plt.ylabel('nombre de véhicules', loc='top', rotation=0, fontsize=10)

    # Extraction de la légende du graphique et placement dans un cadre séparé
    leg = plt.legend(bbox_to_anchor=(.95, 1.15),
                     fontsize=7.5,  loc=2, borderaxespad=0)
    ax.add_artist(leg)
    # plt.gca().set_ylim(0, 1000000)

    # Définition des graduations sur l'axe des ordonnées²
    ax.yaxis.set_major_formatter(FuncFormatter(y_formatter))
    # plt.savefig('./png/'+region)
    plt.show()

    
    # Calculate percentage of vehicles in each category
    df_commune['proportion'] = df_commune.groupby('commune_de_residence')['nombre de véhicules'].apply(lambda x: x / x.sum() * 100)
    # print (df_commune)

    # Sort df_commune by Crit'Air category
    df_commune = sort_par_model_couleur(df_commune,model)
    # print (df_commune)
    # df_commune.to_csv(p + r'/France_data/df_commune_proportion.csv',encoding="utf-8")
    carto(df_commune,file_name,model,Annees_list)


plot_vehicule_evolution(df_propre, 'crit_air', None,
                         'Paris', None, None, None, 2012, 2022)

# plot_vehicule_evolution(df_propre, 'crit_air', 'Auvergne-Rhône-Alpes',
#                         'Yvelines', None, None, None, 2020, 2021)
