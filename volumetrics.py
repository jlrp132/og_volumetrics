'''
incluir salida de POIS en dataframe 10 50 90
incluir seleccion de Percentiles adicionales?
plots en funciones
'''

from scipy.stats import norm
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io

import streamlit as st

st.set_page_config(page_title='Volumetrics 1.0', 
                    page_icon='round-pushpin', 
                    initial_sidebar_state='collapsed', 
                    layout='wide')

# Change head title
def set_page_title(title):
    st.markdown(unsafe_allow_html=True, body=f"""
        <iframe height=0 srcdoc="<script>
            const title = window.parent.document.querySelector('title') \
                
            const oldObserver = window.parent.titleObserver
            if (oldObserver) {{
                oldObserver.disconnect()
            }} \

            const newObserver = new MutationObserver(function(mutations) {{
                const target = mutations[0].target
                if (target.text !== '{title}') {{
                    target.text = '{title}'
                }}
            }}) \

            newObserver.observe(title, {{ childList: true }})
            window.parent.titleObserver = newObserver \

            title.text = '{title}'
        </script>" />
    """)

set_page_title("Volumetrics 1.0")

# Hide Hamburguer menu
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


# local css
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# funcions
def STOIP(area, ht, phi, sw, ntg, rf, bo):
    stoip = (area*1000*ht*phi*(1-sw)*ntg*rf)/bo
    return stoip

def STGIP(area, ht, phi, sw, ntg, rf, bg):
    ogip = (area*1000*ht*phi*(1-sw)*ntg*rf)/bg
    return ogip

def POIS(area, ht, phi, sw, ntg, bo):
    pois = area*1000*ht*phi*(1-sw)*ntg/bo
    return pois

def GOIS(area, ht, phi, sw, ntg, bg):
    gois = area*1000*ht*phi*(1-sw)*ntg/bg
    return gois

# @st.cache
def plot_results():
    fig1 = sns.displot(value, kind='hist', stat='density', kde=True)
    if fluid == 'GAS':
        fig1.set(xlabel='SGIP Mm3', ylabel='Frequency')
    else:
        fig1.set(xlabel='STOIP Mm3', ylabel='Frequency')
    fig1.set(title=str(name)+' - Volume')
    st.pyplot(fig1)

    fig2 = sns.displot(value, kind='ecdf')
    if fluid == 'GAS':
        fig2.set(xlabel='SGIP Mm3', ylabel='Probability')
    else:
        fig2.set(xlabel='STOIP Mm3', ylabel='Probability')
    plt.axhline(y=0.9, label='P10', color='red', linestyle='--')
    plt.axhline(y=0.5, label='P50', color='red', linestyle=':')
    plt.axhline(y=0.1, label='P90', color='red', linestyle='-.')
    plt.legend(prop={'size':6})
    st.pyplot(fig2)

# @st.cache
def plot_properties_dist():
    fig_area = sns.displot(area, kind='hist', stat='density', kde=True)
    fig_area.set(xlabel='Surface Area (Km2)', ylabel='Probability')
    fig_area.set(title=str(name)+' - Area')
    st.pyplot(fig_area)

    fig_ht = sns.displot(ht, kind='hist', stat='density', kde=True)
    fig_ht.set(xlabel='Thickness (m)', ylabel='Probability')
    fig_ht.set(title=str(name)+' - Thickness')
    st.pyplot(fig_ht)

    fig_phi = sns.displot(phi, kind='hist', stat='density', kde=True)
    fig_phi.set(xlabel='Porosity (fr)', ylabel='Probability')
    fig_phi.set(title=str(name)+' - Porosity')
    st.pyplot(fig_phi)

    fig_ntg = sns.displot(ntg, kind='hist', stat='density', kde=True)
    fig_ntg.set(xlabel='Net-to-Gross (fr)', ylabel='Probability')
    fig_ntg.set(title=str(name)+' - Net-to-Gross')
    st.pyplot(fig_ntg)

    fig_sw = sns.displot(sw, kind='hist', stat='density', kde=True)
    fig_sw.set(xlabel='Water Saturation (fr)', ylabel='Probability')
    fig_sw.set(title=str(name)+' - Water Saturation')
    st.pyplot(fig_sw)

    fig_rf = sns.displot(rf, kind='hist', stat='density', kde=True)
    fig_rf.set(xlabel='Recovery Factor (fr)', ylabel='Probability')
    fig_rf.set(title=str(name)+' - Recovery Factor')
    st.pyplot(fig_rf)

    if fluid == 'GAS':
        fig_bg = sns.displot(bg, kind='hist', stat='density', kde=True)
        fig_bg.set(xlabel=' Gas Volumetric Factor (fr)', ylabel='Probability')
        fig_bg.set(title=str(name)+' - Bg')
        st.pyplot(fig_bg)
    else:
        fig_bo = sns.displot(bo, kind='hist', stat='density', kde=True)
        fig_bo.set(xlabel=' Oil Volumetric Factor (fr)', ylabel='Probability')
        fig_bo.set(title=str(name)+' - Bo')
        st.pyplot(fig_bo)


head_0, head_1 = st.beta_columns([7,1])
head_0.title('Volumetric Calculator')
head_1.image('thumbnail.png', width=70)

### Manual Input
with st.beta_expander('Manual Input', expanded=False):
    left_column, right_column = st.beta_columns(2)

    area_m = left_column.number_input('Area [Km2]', min_value=0.001, max_value=1000.0, step=0.1, value=1.0)
    area_sd = right_column.number_input('Std. dev [Km2]', min_value=0.01, value=0.1, key='area_sd')

    ht_m = left_column.number_input('Thickness [m]', value=5)
    ht_sd = right_column.number_input('Std. dev [m]', min_value=0.01, value=0.1, key='ht_sd')

    phi_m = left_column.number_input('Porosity []', value=0.2)
    phi_sd = right_column.number_input('Std. dev []', min_value=0.01, value=0.05, key='phi_sd')

    ntg_m = left_column.number_input('Net-to-Gross []', value=0.6)
    ntg_sd = right_column.number_input('Std. dev []', min_value=0.01, value=0.15, key='ntg_sd')

    sw_m = left_column.number_input('Water Saturation []', value=0.3)
    sw_sd = right_column.number_input('Std. dev []', min_value=0.01, value=0.05, key='sw_sd')

    rf_m = left_column.number_input('Recovery Factor []', value=0.2)
    rf_sd = right_column.number_input('Std. dev []', min_value=0.01, value=0.05, key='rf_sd')

    bo_m = left_column.number_input('Bo []', value=1.2)
    bo_sd = right_column.number_input('Std. dev []', min_value=0.01, value=0.1, key='bo_sd')

    iters_man = right_column.number_input('Iterations', value=10000, key='iters_manual')

    # Manual input calc
    if left_column.button('Compute'):
        area = norm(area_m, area_sd).rvs(iters_man)
        ht   = norm(ht_m, ht_sd).rvs(iters_man)
        phi  = norm(phi_m, phi_sd).rvs(iters_man)
        ntg  = norm(ntg_m, ntg_sd).rvs(iters_man)
        sw   = norm(sw_m, sw_sd).rvs(iters_man)
        rf   = norm(rf_m, rf_sd).rvs(iters_man)
        bo   = norm(bo_m, bo_sd).rvs(iters_man)

        value = STOIP(area, ht, phi, sw, ntg, rf, bo)
        # value = OOIP(area_m, ht_m, phi_m, sw_m,ntg_m, rf_m, bo_m) # single calc from input
        # st.write(value.mean(), 'Mm3')

        p10 = np.percentile(value,10)
        p50 = np.percentile(value,50)
        p90 = np.percentile(value,90)

        st.write('P90 : ', p10, 'Mm3')
        st.write('P50 : ', p50, 'Mm3')
        st.write('P10 : ', p90, 'Mm3')

        fig1 = sns.displot(value, kind='hist', stat='density', kde=True)
        fig1.set(xlabel='STOIP Mm3', ylabel='Frequency')
        st.pyplot(fig1)

        fig2 = sns.displot(value, kind='ecdf')
        fig2.set(xlabel='STOIP Mm3', ylabel='Probability')
        plt.axhline(y=0.9, label='P10', color='red', linestyle='--')
        plt.axhline(y=0.5, label='P50', color='red', linestyle=':')
        plt.axhline(y=0.1, label='P90', color='red', linestyle='-.')
        st.pyplot(fig2)

        st.success('Completed!')

st.markdown('***')

### File upload calculations
loaded_file = st.file_uploader('File Input',type=['xlsx'])

iters = st.number_input('Iterations', value=10000)

# Graph output selection
left_col_2, right_col_2 = st.beta_columns(2)

graph_out = left_col_2.checkbox(label='Show Graphics')
graph_prop = right_col_2.checkbox(label='Show Properties Distributions')


if loaded_file is not None:
    df = pd.read_excel(loaded_file)
    # st.dataframe(df)

    for p in range(len(df)):
        name = df['NAME'][p]
        st.subheader(name)

        # read parameters
        fluid = df['FLUID'][p]
        
        area = norm(df['AREA'][p], df['AREA_SD'][p]).rvs(iters)
        ht   = norm(df['HT'][p], df['HT_SD'][p]).rvs(iters)
        phi  = norm(df['PHI'][p], df['PHI_SD'][p]).rvs(iters)
        ntg  = norm(df['NTG'][p], df['NTG_SD'][p]).rvs(iters)
        sw   = norm(df['SW'][p], df['SW_SD'][p]).rvs(iters)
        rf   = norm(df['RF'][p], df['RF_SD'][p]).rvs(iters)
        if fluid == 'GAS':
            bg   = norm(df['BG'][p], df['BG_SD'][p]).rvs(iters) # for gas
        else:            
            bo   = norm(df['BO'][p], df['BO_SD'][p]).rvs(iters) # for oil
        
        # Drainage Area (Ha)
        d_area = df['D_AREA'][p]

        # Risk data
        pro_ts = df['TRAPSEAL'][p]/100
        pro_rr = df['RESROCK'][p]/100
        pro_sm = df['SRCMIG'][p]/100
        pro_ti = df['TIMING'][p]/100
        pro_scc = (pro_ts * pro_rr * pro_sm * pro_ti)

        # Calculate volumes (stock tank)
        if fluid == 'OIL':
            value = STOIP(area, ht, phi, sw, ntg, rf, bo)
        elif fluid == 'GAS':
            value = STGIP(area, ht, phi, sw, ntg, rf, bg)

        # POIS/GOIS
        if fluid == 'OIL':
            value_in_situ = POIS(area, ht, phi, sw, ntg, bo) 
        elif fluid == 'GAS':
            value_in_situ = GOIS(area, ht, phi, sw, ntg, bg)

        # Percentile (stock tank)
        p10 = round(np.percentile(value,10),2)
        p50 = round(np.percentile(value,50),2)
        p90 = round(np.percentile(value,90),2)

        # Percentile (in situ)
        p10_ip = round(np.percentile(value_in_situ,10),2)
        p50_ip = round(np.percentile(value_in_situ,50),2)
        p90_ip = round(np.percentile(value_in_situ,90),2)

        # number of wells in measured area
        # wells_num = area.mean()/d_area*100
        wells_num = np.percentile(area,50)/d_area*100

        # type well cummulative
        type_well_cum = p50/wells_num

        # Text Output
        col_30, col_31, col_32, col_33 = st.beta_columns(4)
        
        with col_30:
            st.write('P90 In Place: ', p10_ip, 'Mm3')
            st.write('P50 In Place: ', p50_ip, 'Mm3')
            st.write('P10 In Place: ', p90_ip, 'Mm3')

        with col_31:
            st.write('P90 : ', round(p10,1), 'Mm3')
            st.write('P50 : ', round(p50,1), 'Mm3')
            st.write('P10 : ', round(p90,1), 'Mm3')
        
        with col_32:
            st.write('Risked P90 : ', round(p10*pro_scc,1), 'Mm3')
            st.write('Risked P50 : ', round(p50*pro_scc,1), 'Mm3')
            st.write('Risked P10 : ', round(p90*pro_scc,1), 'Mm3')

        with col_33:            
            st.write('Success: ', round((pro_scc*100),3), '%')
            st.write('Number of wells: ', round(wells_num))
            st.write(fluid + ' Cum per well: ', round(type_well_cum,1), 'Mm3')

        # Plots
        if graph_out: 
            with st.beta_expander('Volume Graph'):
                plot_results()
                # fig1 = sns.displot(value, kind='hist', stat='density', kde=True)
                # if fluid == 'GAS':
                #     fig1.set(xlabel='SGIP Mm3', ylabel='Frequency')
                # else:
                #     fig1.set(xlabel='STOIP Mm3', ylabel='Frequency')
                # fig1.set(title=str(name)+' - Volume')
                # st.pyplot(fig1)

                # fig2 = sns.displot(value, kind='ecdf')
                # if fluid == 'GAS':
                #     fig2.set(xlabel='SGIP Mm3', ylabel='Probability')
                # else:
                #     fig2.set(xlabel='STOIP Mm3', ylabel='Probability')
                # plt.axhline(y=0.9, label='P10', color='red', linestyle='--')
                # plt.axhline(y=0.5, label='P50', color='red', linestyle=':')
                # plt.axhline(y=0.1, label='P90', color='red', linestyle='-.')
                # plt.legend(prop={'size':6})
                # st.pyplot(fig2)

        if graph_prop:
            with st.beta_expander('Properties Graph'):
                plot_properties_dist()

                # fig_area = sns.displot(area, kind='hist', stat='density', kde=True)
                # fig_area.set(xlabel='Surface Area (Km2)', ylabel='Probability')
                # fig_area.set(title=str(name)+' - Area')
                # st.pyplot(fig_area)

                # fig_ht = sns.displot(ht, kind='hist', stat='density', kde=True)
                # fig_ht.set(xlabel='Thickness (m)', ylabel='Probability')
                # fig_ht.set(title=str(name)+' - Thickness')
                # st.pyplot(fig_ht)

                # fig_phi = sns.displot(phi, kind='hist', stat='density', kde=True)
                # fig_phi.set(xlabel='Porosity (fr)', ylabel='Probability')
                # fig_phi.set(title=str(name)+' - Porosity')
                # st.pyplot(fig_phi)

                # fig_ntg = sns.displot(ntg, kind='hist', stat='density', kde=True)
                # fig_ntg.set(xlabel='Net-to-Gross (fr)', ylabel='Probability')
                # fig_ntg.set(title=str(name)+' - Net-to-Gross')
                # st.pyplot(fig_ntg)

                # fig_sw = sns.displot(sw, kind='hist', stat='density', kde=True)
                # fig_sw.set(xlabel='Water Saturation (fr)', ylabel='Probability')
                # fig_sw.set(title=str(name)+' - Water Saturation')
                # st.pyplot(fig_sw)

                # fig_rf = sns.displot(rf, kind='hist', stat='density', kde=True)
                # fig_rf.set(xlabel='Recovery Factor (fr)', ylabel='Probability')
                # fig_rf.set(title=str(name)+' - Recovery Factor')
                # st.pyplot(fig_rf)

                # if fluid == 'GAS':
                #     fig_bg = sns.displot(bg, kind='hist', stat='density', kde=True)
                #     fig_bg.set(xlabel=' Gas Volumetric Factor (fr)', ylabel='Probability')
                #     fig_bg.set(title=str(name)+' - Bg')
                #     st.pyplot(fig_bg)
                # else:
                #     fig_bo = sns.displot(bo, kind='hist', stat='density', kde=True)
                #     fig_bo.set(xlabel=' Oil Volumetric Factor (fr)', ylabel='Probability')
                #     fig_bo.set(title=str(name)+' - Bo')
                #     st.pyplot(fig_bo)

        # Write data in dataframe
        df.loc[p,'p90_ip_'+ fluid] = p10_ip
        df.loc[p,'p50_ip_'+ fluid] = p50_ip
        df.loc[p,'p10_ip_'+ fluid] = p90_ip
        df.loc[p,'p90_'+ fluid] = p10
        df.loc[p,'p50_'+ fluid] = p50
        df.loc[p,'p10_'+ fluid] = p90
        df.loc[p,'Rsk_p90_'+ fluid] = round(p10*pro_scc,2)
        df.loc[p,'Rsk_p50_'+ fluid] = round(p50*pro_scc,2)
        df.loc[p,'Rsk_p10_'+ fluid] = round(p90*pro_scc,2)
        df.loc[p,'Succ_PROB'] = pro_scc*100
        df.loc[p,'Wells'] = round(wells_num)
        df.loc[p,'Well_Type_'+ fluid] = round(type_well_cum,1)

    # Summary table
    st.subheader('Summary')

    hide_col = ['AREA_SD','AREA_SD','HT_SD','PHI_SD','NTG_SD','SW_SD','RF_SD','BO_SD','BG_SD',
                'TRAPSEAL','RESROCK','SRCMIG','TIMING','D_AREA',
                'HT','PHI','NTG','SW', 'RF','BO','BG','FLUID','AREA','DEPTH']

    st.dataframe(df.drop(hide_col, axis=1).set_index('NAME').fillna(value=''))

    show_input = st.checkbox(label='Show Input Data')
    if show_input:
        st.dataframe(df.set_index('NAME').fillna(value=''))
    
    if st.checkbox('Download Results'):

        iowrite = io.BytesIO()
        f = df.to_excel(iowrite, encoding='utf-8')
        iowrite.seek(0)
        dl_data = base64.b64encode(iowrite.read()).decode()
        dl_link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{dl_data}" download={"output.xlsx"}>Download Data</a>'
        st.markdown(dl_link, unsafe_allow_html=True)
    

