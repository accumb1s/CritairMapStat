# -*- coding: utf-8 -*-
import socket
import pandas as pd
import os
import glob
import requests
from tqdm import tqdm

p = os.getcwd()

class Recup_Donneees_VP:
    def __init__(self):
        self.est_connecte()
        self.get_need_csv_file()
        self.Recuperation_parc_vp_commune_2022_xlsx()
        self.df_propre_final_fr()
        
    def est_connecte(self):
        try:
            socket.create_connection(("1.1.1.1", 53))
            self.connexion = True
            print (self.connexion)
        except OSError:
            pass
            self.connexion = False
            print (self.connexion)
            
    # '\France_data\parc_vp_commune_2022.xlsx'

    def fichier_existe(self,pathfichier):
        if glob.glob(p+pathfichier):
            print ('fichier exist')
            self.fichiersExistes = True
        else : self.fichiersExistes = False
        print (self.fichiersExistes)

    
    def get_csv_file(self,url,open_file,sep=","):
        self.fichier_existe(open_file)
        if not self.fichiersExistes and self.connexion:
            print(f'Récupération du fichier: {open_file} en ligne')
            url = url
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            with open(p + open_file, 'wb') as f:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
            progress_bar.close()
            df = pd.read_csv(p + open_file, sep=sep)
            self.df = df
            return self.df
        else:
            print(f"Utilisation du fichier: {open_file} déjà téléchargé")
            df = pd.read_csv(p + open_file, sep=sep)
            self.df = df
            return self.df
    
    def get_need_csv_file(self):
        url_ccicp = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/correspondance-code-insee-code-postal/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B'
        open_ccicp = r"/France_data/correspondance-code-insee-code-postal.csv"
        sep_ccicp=';'
        self.df_ccicp = self.get_csv_file(url_ccicp,open_ccicp,sep_ccicp)

        url_departements_region ='https://www.data.gouv.fr/fr/datasets/r/987227fb-dcb2-429e-96af-8979f97c9c84'
        open_departements_region = r'/France_data/departements-region.csv'
        self.df_regions = self.get_csv_file(url_departements_region,open_departements_region)

    def Recuperation_parc_vp_commune_2022_xlsx(self):
        # self.fichier_existe(p + '/France_data/*.xlsx')
        self.fichier_existe('/France_data/parc_vp_commune_2022.xlsx')

        if not self.fichiersExistes and self.connexion:
            print('Récupération du fichier:parc_vp_commune_2022.xlsx en ligne')
            url_Parc_VP_France = 'https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2022-10/parc_vp_commune_2022.xlsx'
            response = requests.get(url_Parc_VP_France, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 kilobyte
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            with open(p + r"/France_data/parc_vp_commune_2022.xlsx", "wb") as f:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
            progress_bar.close()
            df_fr_original = pd.read_excel(p + r'/France_data/parc_vp_commune_2022.xlsx', skiprows=3, header=0)
            self.df_fr_original = df_fr_original
        else:
            print("Utilisation du fichier:parc_vp_commune_2022.xlsx déjà téléchargé")
            df_fr_original = pd.read_excel(p + r'/France_data/parc_vp_commune_2022.xlsx', skiprows=3, header=0)
            self.df_fr_original = df_fr_original

    
    def renommage(self):
        # df_fr_original = pd.read_excel(p + r'/France_data/parc_vp_commune_2022.xlsx', skiprows=3, header=0)
        self.df_fr_original = self.df_fr_original.rename(columns={ 'Code commune de résidence': 'code_commune_insee_residence', 'Commune de résidence': 'commune_de_residence', 
                'Carburant': 'carburant', "Crit'Air": 'crit_air' })
        return self.df_fr_original


    def df_propre_sans_Inconnu_fr(self):
        df_fr_original = self.renommage()
        print ('df_fr_original : ',df_fr_original.shape,'\n')

        # df_fr_original = df_fr_original.drop(df_fr_original.columns[[0]], axis=1)

        print ('df_fr_original : ',df_fr_original.shape,'\n')
        print ('df_fr_original : ',df_fr_original,'\n')


        df_fr_original.drop(df_fr_original[df_fr_original['code_commune_insee_residence'].str.startswith('97')].index, inplace=True)
        # df_fr_propre_sans_Inconnu = df_fr_original[~df_fr_original["commune de résidence"].str.contains('Inconnu', na=False)]

        print ('df_fr_original: ',df_fr_original)

        df_fr_original.to_csv(p + r'/France_data/df_fr_original_utf-8.csv',encoding="utf-8")
        df_fr_propre_sans_Inconnu = df_fr_original[df_fr_original["commune_de_residence"] != 'Inconnu']

        print ('df_fr_propre_sans_Inconnu: ',df_fr_propre_sans_Inconnu)

        df_fr_propre_sans_Inconnu['commune_de_residence'] = df_fr_propre_sans_Inconnu['commune_de_residence'].str.replace('Inconnu \(', '', regex=True).str.replace('\)', '',regex=True)
        df_fr_propre_sans_Inconnu['2022'] = df_fr_propre_sans_Inconnu['2022'].round(0).astype(int)
        df_fr_propre_sans_Inconnu['code_departement_de_residence'] = df_fr_propre_sans_Inconnu['code_commune_insee_residence'].str[:2]
        colonne_a_deplacer = df_fr_propre_sans_Inconnu.pop('code_departement_de_residence')
        df_fr_propre_sans_Inconnu.insert(0, 'code_departement_de_residence', colonne_a_deplacer)

        print ('df_fr_propre_sans_Inconnu : ',df_fr_propre_sans_Inconnu.shape,'\n')

        print ('self.df_regions : ',self.df_regions.shape,'\n')

        self.df_regions['num_dep'] = self.df_regions['num_dep'].astype(str) # obligé de typer en str a cause de la corse pour faire la jointure
        df_fr_propre_sans_Inconnu['code_departement_de_residence'] = df_fr_propre_sans_Inconnu['code_departement_de_residence'].astype(str) # obligé de typer en str a cause de la corse pour faire la jointure
        df_merged_sans_Inconnu = pd.merge(df_fr_propre_sans_Inconnu, self.df_regions, left_on='code_departement_de_residence', right_on='num_dep', how='inner')

        print ('df_merged_sans_Inconnu : ',df_merged_sans_Inconnu.shape,'\n')

        df_merged_sans_Inconnu = df_merged_sans_Inconnu.rename(columns={ 'dep_name': 'departement_de_residence','region_name': 'region_de_residence'})
        
        colonne_a_deplacer = df_merged_sans_Inconnu.pop('departement_de_residence')
        df_merged_sans_Inconnu.insert(0, 'departement_de_residence', colonne_a_deplacer)
        
        colonne_a_deplacer = df_merged_sans_Inconnu.pop('region_de_residence')
        df_merged_sans_Inconnu.insert(0, 'region_de_residence', colonne_a_deplacer)
        
        df_merged_sans_Inconnu = df_merged_sans_Inconnu.iloc[:, :-1]

        print ('df_merged_sans_Inconnu : ',df_merged_sans_Inconnu.shape,'\n')

        self.df_fr_propre_sans_Inconnu = df_merged_sans_Inconnu
        return self.df_fr_propre_sans_Inconnu
    

    def merge_dfs (self,df1,df2,num):
        print(df2)
        df1['code_commune_insee_residence'] = df1['code_commune_insee_residence'].astype(str)
        df2['Code INSEE'] = df2['Code INSEE'].astype(str)
        df_ccicp_geoloc_propre_merged = pd.merge(df1, df2[['Code INSEE','Code Postal','Commune']], left_on='code_commune_insee_residence', right_on='Code Postal', how='left')
        df_ccicp_geoloc_propre_merged.loc[df_ccicp_geoloc_propre_merged['Code INSEE'].notnull(), 'code_commune_insee_residence'] = df_ccicp_geoloc_propre_merged['Code INSEE'].astype(str)
        df_ccicp_geoloc_propre_merged.loc[df_ccicp_geoloc_propre_merged['Commune'].notnull(), 'commune_de_residence'] = df_ccicp_geoloc_propre_merged['Commune']
        print ('df_ccicp_geoloc_propre_merged : ',df_ccicp_geoloc_propre_merged.shape,'\n')
        
        df_ccicp_geoloc_propre_merged.loc[df_ccicp_geoloc_propre_merged['Code Postal'].isnull(), 'code_commune_insee_residence'] = df_ccicp_geoloc_propre_merged.loc[df_ccicp_geoloc_propre_merged['Code Postal'].isnull(), 'code_commune_insee_residence'].astype(int) + num
        df_ccicp_geoloc_propre_merged = df_ccicp_geoloc_propre_merged.iloc[:, :-3]
  
        print ('df_ccicp_geoloc_propre_merged : ',df_ccicp_geoloc_propre_merged.shape,'\n')
        self.df_ccicp_geoloc_propre_merged = df_ccicp_geoloc_propre_merged
        return df_ccicp_geoloc_propre_merged
    
    # df_fr_propre_sans_Inconnu = self.df_fr_propre_sans_Inconnu

    def df_propre_final_fr(self):
        self.df_propre_sans_Inconnu_fr()
        df_fr_propre_sans_Inconnu = self.df_fr_propre_sans_Inconnu
        
        print ('df_fr_propre_sans_Inconnu : ',df_fr_propre_sans_Inconnu.shape,'\n')
    
        df_doublon = df_fr_propre_sans_Inconnu[df_fr_propre_sans_Inconnu['departement_de_residence'] == df_fr_propre_sans_Inconnu['commune_de_residence']]
        df_doublon = df_doublon[df_doublon['code_commune_insee_residence'].str.endswith('000')]
        df_doublon['code_commune_insee_residence'] = df_doublon['code_commune_insee_residence'].astype(str)
    

        print ('df_doublon : ',df_doublon.shape,'\n')
        df_doublon.to_csv(p + r'/France_data/df_doublon_utf-8.csv',encoding="utf-8")

        df_sans_doublon = df_fr_propre_sans_Inconnu.drop(df_doublon.index)
        
        print ('df_sans_doublon drop: ',df_sans_doublon.shape,'\n')
        
        # df_ccicp = pd.read_csv(p+r'/France_data/correspondance-code-insee-code-postal.csv',sep=',')#,sep=';')

        print ('df_ccicp : ',self.df_ccicp.shape,'\n')

        # df_ccicp_geoloc_propre = df_ccicp[df_ccicp['Statut'].isin(["['Préfecture']", "['Préfecture de région']",'["Capitale d\'état"]'])]
        self.df_ccicp['Code Postal'] = self.df_ccicp['Code Postal'].astype(str)
        self.df_ccicp['Code Postal'] = self.df_ccicp['Code Postal'].str[:5]
        df_ccicp_geoloc_propre = self.df_ccicp


        df_ccicp_geoloc_propre.to_csv(p + r'/France_data/df_ccicp_geoloc_propre_utf-8.csv',encoding="utf-8")

        print ('df_ccicp_geoloc_propre : ',df_ccicp_geoloc_propre,'\n')

        df_merged_pref1 = self.merge_dfs(df_doublon, df_ccicp_geoloc_propre,0)
        df_merged_pref2 = self.merge_dfs(df_merged_pref1, df_ccicp_geoloc_propre,1)
        # df_merged_pref2 = self.merge_dfs(df_merged_pref2, df_ccicp_geoloc_propre,-1)
        # df_merged_pref2 = self.merge_dfs(df_merged_pref2, df_ccicp_geoloc_propre,0)
        
        df_final = pd.concat([df_sans_doublon.astype(str), df_merged_pref2.astype(str)])
        df_final = df_final.sort_values(by='code_commune_insee_residence')
        df_final['commune_de_residence'] = df_final['commune_de_residence'].str.title()
        df_final.index += 1
        df_final.reset_index(drop=True, inplace=True)

        print ('df_final : ',df_final.shape,'\n')

        df_final.to_csv(p + r'/France_data/df_final_utf-8.csv',encoding="utf-8")

        df_final = df_final.astype(str)
        df_ccicp_geoloc_propre = df_ccicp_geoloc_propre.astype(str)
        parc_vp_propre_geoloc = pd.merge(df_final, df_ccicp_geoloc_propre[['Code INSEE','Statut','Code Département','Code Région','geo_point_2d','geo_shape','ID Geofla']], left_on='code_commune_insee_residence', right_on='Code INSEE', how='left')
        
        # Suppression des lignes où la colonne 'c' est vide
        parc_vp_propre_geoloc = parc_vp_propre_geoloc.dropna(subset=['geo_point_2d'])

        print (parc_vp_propre_geoloc)
        parc_vp_propre_geoloc.to_csv(p + r'/France_data/df_parc_vp_propre_geoloc.csv',encoding="utf-8")
        print (parc_vp_propre_geoloc.shape)


        # verif integrité des données
        # df_doublon = df_final[df_fr_propre_sans_Inconnu['departement_de_residence'] == df_final['commune_de_residence']]
        # df_doublon.to_csv(p + r'/France_data/df_doublon_utf-8.csv',encoding="utf-8")

test = Recup_Donneees_VP()

# test.Recuperation_Des_Fichiers_Italie_en_ligne()
# print ('test ',test.est_connecte())
        # html = requests.get(url).text
        # soup = BeautifulSoup(html, 'html.parser')
        # l1 = []
        # l2 = []
        # print ('Processing: '), url
        # for name in soup.find_all('a', href=re.compile('.zip$')):
        #     zipurl = name['href']
        #     outfname = p + '/Data_Loto_Fr' + '/' + zipurl.split('/')[-1]
        #     l1.append(zipurl)
        #     l2.append(outfname)
        #     r = requests.get(zipurl, stream=True)
        #     if r.status_code == requests.codes.ok:
        #         with open(outfname, 'wb') as fd:
        #             for chunk in r.iter_content(chunk_size=1024):
        #                 if chunk:
        #                     fd.write(chunk)
        #         print ('fd: ', fd)
        #         fd.close()
        # self.l2 = l2

    # def fichiers_existes(self):
    #     today = dt.datetime.now().date()
    #     if os.path.isfile(parc_vp_commune_2022.xlsx) and os.path.isfile(Csv_Loto_Fr_Chance_Op):

