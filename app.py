import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# ══════════════════════════════════════════════════════════════
# CONFIG PAGE
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SDA V4 | BNP Paribas Cardif",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background-color: #F8F9FA; }

/* Header */
.sda-header {
    background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    color: white;
}
.sda-header h1 { font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.sda-header p { font-size: 14px; opacity: 0.8; margin: 4px 0 0 0; }
.sda-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 8px;
}

/* Cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #E9ECEF;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.metric-value { font-size: 28px; font-weight: 700; color: #1F3864; }
.metric-label { font-size: 12px; color: #6C757D; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-delta-pos { color: #28A745; font-size: 13px; font-weight: 600; }
.metric-delta-neg { color: #DC3545; font-size: 13px; font-weight: 600; }

/* Section headers */
.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #1F3864;
    border-left: 4px solid #2E75B6;
    padding-left: 12px;
    margin: 24px 0 16px 0;
}

/* Jauge convention */
.jauge-container { margin-bottom: 12px; }
.jauge-label { 
    display: flex; justify-content: space-between; 
    font-size: 13px; font-weight: 500; color: #343A40;
    margin-bottom: 4px;
}
.jauge-bar-bg { 
    background: #E9ECEF; border-radius: 8px; height: 10px; 
    position: relative; overflow: hidden;
}
.jauge-bar-fill { height: 100%; border-radius: 8px; transition: width 0.3s; }
.jauge-green { background: linear-gradient(90deg, #28A745, #34CE57); }
.jauge-orange { background: linear-gradient(90deg, #FD7E14, #FFC107); }
.jauge-red { background: linear-gradient(90deg, #DC3545, #FF6B6B); }
.jauge-pct { font-size: 11px; color: #6C757D; margin-top: 2px; }

/* Narrateur */
.narrateur-box {
    background: linear-gradient(135deg, #EBF5FB 0%, #D6EAF8 100%);
    border: 1px solid #2E75B6;
    border-left: 4px solid #1F3864;
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 14px;
    line-height: 1.6;
    color: #1F3864;
    font-style: italic;
}

/* Score badge */
.score-pos { 
    background: #D4EDDA; color: #155724; 
    padding: 3px 10px; border-radius: 12px; 
    font-size: 13px; font-weight: 700;
}
.score-neg { 
    background: #F8D7DA; color: #721C24; 
    padding: 3px 10px; border-radius: 12px; 
    font-size: 13px; font-weight: 700;
}
.score-neu { 
    background: #E2E3E5; color: #383D41; 
    padding: 3px 10px; border-radius: 12px; 
    font-size: 13px; font-weight: 700;
}

/* Alert */
.alert-critique { 
    background: #F8D7DA; border-left: 4px solid #DC3545; 
    padding: 10px 16px; border-radius: 6px; margin-bottom: 8px;
    font-size: 13px; color: #721C24;
}
.alert-warning { 
    background: #FFF3CD; border-left: 4px solid #FFC107; 
    padding: 10px 16px; border-radius: 6px; margin-bottom: 8px;
    font-size: 13px; color: #856404;
}
.alert-ok { 
    background: #D4EDDA; border-left: 4px solid #28A745; 
    padding: 10px 16px; border-radius: 6px; margin-bottom: 8px;
    font-size: 13px; color: #155724;
}

div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #E9ECEF;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DONNÉES KAVIGG RÉELLES
# ══════════════════════════════════════════════════════════════

SDA_POCHES = [
    'Taux 0-10 ans','Taux 10-20 ans','Taux 20+ ans','Taux Variables & Assimilés',
    'Crédit IG','Crédit HY','Dette EM','Monétaire','Dette Privée',
    'Actions Europe','Actions US','Actions EM','Actions Monde',
    'Private Equity','Infrastructure','Convertibles & Structurés Actions',
    'Immo Résidentiel','Immo Bureaux','Immo Diversification','Foncières Cotées'
]

NOEUD = {
    'Taux 0-10 ans':'Obligations','Taux 10-20 ans':'Obligations','Taux 20+ ans':'Obligations',
    'Taux Variables & Assimilés':'Obligations','Crédit IG':'Obligations','Crédit HY':'Obligations',
    'Dette EM':'Obligations','Monétaire':'Obligations','Dette Privée':'Obligations',
    'Actions Europe':'Beta Actions','Actions US':'Beta Actions','Actions EM':'Beta Actions',
    'Actions Monde':'Beta Actions','Private Equity':'Beta Actions','Infrastructure':'Beta Actions',
    'Convertibles & Structurés Actions':'Beta Actions',
    'Immo Résidentiel':'Immobilier','Immo Bureaux':'Immobilier',
    'Immo Diversification':'Immobilier','Foncières Cotées':'Immobilier'
}

NOEUD_COLORS = {'Obligations':'#2E75B6','Beta Actions':'#E6A817','Immobilier':'#C0392B'}

# Données réelles KAVIGG 22/06/2026
data = {
    'Poche': SDA_POCHES,
    'VB_M': [11747,26234,4343,4950,27856,1004,1601,2286,2836,3446,591,294,546,2589,2164,1066,1622,2555,3417,788],
    'PMVL_M': [-958,-3146,-1453,-88,-619,156,180,210,608,1696,811,245,482,1281,527,197,1060,188,741,-15],
    'TRA': [3.2,3.5,3.8,2.9,4.2,6.5,6.0,2.5,6.5,8.0,7.5,9.0,7.8,12.0,7.0,5.5,5.5,4.0,5.0,6.0],
    'SCR': [3,8,15,2.5,8,20,22,0.5,10,39,49,49,46,49,30,25,25,25,25,39],
    'mu': [3.2,3.5,3.8,2.9,4.2,6.5,6.0,2.5,6.5,8.0,7.5,9.0,7.8,12.0,7.0,5.5,5.5,4.0,5.0,6.0],
    'sigma': [4.0,8.0,14.0,3.0,5.0,8.0,9.0,0.5,3.0,15.0,16.0,18.0,15.5,20.0,10.0,10.0,8.0,12.0,9.0,15.0],
    'epsilon': [1.2,2.4,4.0,0.8,1.5,2.4,2.7,0.1,0.9,4.5,4.8,4.0,4.0,2.0,3.0,3.0,2.0,2.0,2.0,2.0],
}

ALPHAS = {
    'Goldilocks':   [-1,-1,-1,0,+1,+2,+1,-2,+1,+2,+2,+1,+2,+1,+1,+1,+1,-1,0,+1],
    'Overheating':  [-2,-2,-2,+1,0,+1,0,-2,0,+1,+1,+1,+1,0,0,+1,0,-1,0,0],
    'Récession':    [+2,+2,+2,0,+1,-2,-1,+1,-1,-2,-2,-2,-2,-2,-1,-1,-1,-2,-1,-2],
    'Stagflation':  [-1,-1,-1,+1,-1,-2,-1,-1,-1,-1,-1,-1,-1,-1,0,-1,0,-2,-1,-1],
    'Disinflation': [+1,+2,+1,0,+2,+1,0,-1,+1,+1,+1,0,+1,0,+1,+1,+1,-1,0,+1],
    'Stress':       [+2,+2,+2,0,+1,-2,-2,+2,-1,-2,-2,-2,-2,-2,-1,-1,-1,-2,-1,-2],
}

df_data = pd.DataFrame(data)
df_data['Noeud'] = df_data['Poche'].map(NOEUD)
df_data['pct'] = df_data['VB_M'] / df_data['VB_M'].sum() * 100
df_data['sharpe'] = df_data['mu'] / df_data['sigma']
s_min,s_max = df_data['sharpe'].min(), df_data['sharpe'].max()
df_data['sharpe_norm'] = (df_data['sharpe']-s_min)/(s_max-s_min)
r_min,r_max = (df_data['mu']/df_data['SCR']).min(), (df_data['mu']/df_data['SCR']).max()
df_data['roscr_norm'] = ((df_data['mu']/df_data['SCR'])-r_min)/(r_max-r_min)
p5,p95 = -2.0524, 3.8743
df_data['delta_raw'] = df_data['PMVL_M'] / (df_data['SCR']/100 * df_data['VB_M'])
df_data['delta_star'] = ((df_data['delta_raw'].clip(p5,p95)-p5)/(p95-p5)*2-1)

VB_TOTAL = df_data['VB_M'].sum()
PMVL_TOTAL = df_data['PMVL_M'].sum()
RC_YTD = -41.4
PMVR_YTD = 253.5
BUDGET_RC = 250.0
BUDGET_PMVR = 400.0

CONTRAINTES = [
    {'name':'Sensibilité [4.0 - 6.5]','actuel':6.19,'min':4.0,'max':6.5,'unite':'','pct':95,'seuil':95},
    {'name':'Duration crédit ≤ A (max 21 ans)','actuel':19.05,'min':0,'max':21,'unite':' ans','pct':91,'seuil':90},
    {'name':'Rating ≤ A+ (max 70%)','actuel':61.5,'min':0,'max':70,'unite':'%','pct':88,'seuil':85},
    {'name':'Immobilier [4% - 11%]','actuel':9.66,'min':4,'max':11,'unite':'%','pct':88,'seuil':85},
    {'name':'PE & Infra (max 5.5%)','actuel':4.73,'min':0,'max':5.5,'unite':'%','pct':86,'seuil':80},
    {'name':'Actions [2% - 12%]','actuel':9.75,'min':2,'max':12,'unite':'%','pct':81,'seuil':80},
    {'name':'RC [±250 M€]','actuel':-41.4,'min':-250,'max':250,'unite':' M€','pct':17,'seuil':80},
    {'name':'Dérivés taux [±40 Mds€]','actuel':26,'min':-40,'max':40,'unite':' Mds€','pct':65,'seuil':80},
    {'name':'Taux Variables (max 20%)','actuel':6.93,'min':0,'max':20,'unite':'%','pct':35,'seuil':80},
    {'name':'HY total (max 4%)','actuel':0.56,'min':0,'max':4,'unite':'%','pct':14,'seuil':80},
]

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <div style="font-size:32px;">📊</div>
        <div style="font-weight:700; color:#1F3864; font-size:16px;">SDA V4</div>
        <div style="font-size:11px; color:#6C757D;">BNP Paribas Cardif</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    portefeuille = st.selectbox("📁 Portefeuille",
        ['KAVIGG','KAVINP','KREGG','KRD','KRENP'],
        index=0)
    
    scenario = st.selectbox("🌍 Scénario Macro",
        ['Goldilocks','Overheating','Récession','Stagflation','Disinflation','Stress'],
        index=4)
    
    w_s = st.slider("Poids Sharpe (w_s)", 0.0, 1.0, 0.2, 0.05)
    w_3 = st.slider("Poids Richesse (w_3)", 0.0, 1.0, 0.3, 0.05)
    w_4 = st.slider("Poids RoSCR (w_4)", 0.0, 1.0, 0.5, 0.05)
    
    st.divider()
    
    st.markdown(f"""
    <div style="font-size:12px; color:#6C757D; text-align:center;">
        Données au 22/06/2026<br>
        MyDailyAM · Blotter<br>
        <span style="color:#28A745;">● Connecté</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CALCUL SCORES
# ══════════════════════════════════════════════════════════════
alphas_sc = ALPHAS[scenario]
df_data['alpha'] = alphas_sc
df_data['score'] = (df_data['alpha'] + w_s*df_data['sharpe_norm'])*1 + w_3*df_data['delta_star'] + w_4*df_data['roscr_norm']
df_data['deviation'] = df_data['score'] / 2.7 * df_data['epsilon'] / 100

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="sda-header">
    <h1>Système de Décision d'Allocation</h1>
    <p>BNP Paribas Cardif · Direction Investissements · Investments Allocation & Optimisation</p>
    <div>
        <span class="sda-badge">📁 {portefeuille}</span>
        <span class="sda-badge" style="margin-left:8px;">🌍 {scenario}</span>
        <span class="sda-badge" style="margin-left:8px;">📅 {date.today().strftime('%d/%m/%Y')}</span>
        <span class="sda-badge" style="margin-left:8px; background:rgba(255,193,7,0.3);">⚠️ 3 alertes actives</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MÉTRIQUES CLÉS
# ══════════════════════════════════════════════════════════════
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1:
    st.metric("VB Totale", f"{VB_TOTAL:,.0f} M€", delta=None)
with c2:
    sign = "+" if PMVL_TOTAL > 0 else ""
    st.metric("Richesse Latente", f"{sign}{PMVL_TOTAL:,.0f} M€", delta="PMVL globale")
with c3:
    st.metric("Sensibilité", "6.19", delta="95% du max ⚠️", delta_color="inverse")
with c4:
    st.metric("TRA moyen", "3.42%", delta="+0bp vs hier")
with c5:
    st.metric("RC YTD", f"{RC_YTD:.1f} M€", delta=f"{abs(RC_YTD)/BUDGET_RC*100:.0f}% budget")
with c6:
    st.metric("PMVR YTD", f"+{PMVR_YTD:.0f} M€", delta=f"{PMVR_YTD/BUDGET_PMVR*100:.0f}% budget")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL — 3 colonnes
# ══════════════════════════════════════════════════════════════
col_left, col_mid, col_right = st.columns([2, 2, 1.5])

# ─── COLONNE GAUCHE — Scores SDA ─────────────────────────────
with col_left:
    st.markdown('<div class="section-title">📈 Scores SDA — ' + scenario + '</div>', unsafe_allow_html=True)
    
    df_sda = df_data.copy().sort_values('score', ascending=True)
    
    colors = []
    for s in df_sda['score']:
        if s >= 1.0: colors.append('#28A745')
        elif s >= 0.3: colors.append('#5BA85D')
        elif s >= -0.3: colors.append('#ADB5BD')
        elif s >= -1.0: colors.append('#FD7E14')
        else: colors.append('#DC3545')
    
    fig_scores = go.Figure()
    fig_scores.add_trace(go.Bar(
        y=df_sda['Poche'],
        x=df_sda['score'],
        orientation='h',
        marker_color=colors,
        marker_line_width=0,
        text=[f"{s:+.2f}" for s in df_sda['score']],
        textposition='outside',
        textfont=dict(size=11, family='Inter'),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.3f}<br>Déviation: %{customdata:.1f}%<extra></extra>',
        customdata=df_sda['deviation']*100,
    ))
    fig_scores.add_vline(x=0, line_width=1.5, line_color="#343A40")
    fig_scores.update_layout(
        height=520,
        margin=dict(l=0,r=60,t=10,b=10),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(
            gridcolor='#F0F0F0', zeroline=False,
            title=None, tickfont=dict(size=10),
            range=[-2.8, 2.8]
        ),
        yaxis=dict(gridcolor='#F0F0F0', tickfont=dict(size=11, family='Inter')),
        showlegend=False,
    )
    st.plotly_chart(fig_scores, use_container_width=True)

# ─── COLONNE MILIEU — Allocation ─────────────────────────────
with col_mid:
    st.markdown('<div class="section-title">🗂️ Allocation Actuelle</div>', unsafe_allow_html=True)
    
    # Treemap par noeud
    df_treemap = df_data[df_data['VB_M'] > 0].copy()
    df_treemap['color_val'] = df_treemap['PMVL_M']
    
    fig_tree = px.treemap(
        df_treemap,
        path=[px.Constant("KAVIGG"), 'Noeud', 'Poche'],
        values='VB_M',
        color='PMVL_M',
        color_continuous_scale=['#DC3545','#F8F9FA','#28A745'],
        color_continuous_midpoint=0,
        custom_data=['pct','PMVL_M','VB_M'],
    )
    fig_tree.update_traces(
        hovertemplate='<b>%{label}</b><br>VB: %{value:.0f} M€<br>PMVL: %{customdata[1]:+.0f} M€<br>%ptf: %{customdata[0]:.1f}%<extra></extra>',
        textfont=dict(size=11, family='Inter'),
    )
    fig_tree.update_layout(
        height=260,
        margin=dict(l=0,r=0,t=10,b=0),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_tree, use_container_width=True)
    
    # Top scores table
    st.markdown('<div class="section-title">🏆 Top Opportunités</div>', unsafe_allow_html=True)
    df_top = df_data.nlargest(5,'score')[['Poche','score','deviation','VB_M','PMVL_M']]
    
    for _,row in df_top.iterrows():
        s = row['score']
        badge = f'<span class="score-pos">+{s:.2f}</span>' if s > 0 else f'<span class="score-neg">{s:.2f}</span>'
        dev_sign = "+" if row['deviation'] > 0 else ""
        pmvl_sign = "+" if row['PMVL_M'] > 0 else ""
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; 
                    padding:10px 14px; background:white; border-radius:8px; 
                    margin-bottom:6px; border:1px solid #E9ECEF;
                    box-shadow:0 1px 4px rgba(0,0,0,0.04);">
            <div>
                <div style="font-weight:600; font-size:13px; color:#1F3864;">{row['Poche']}</div>
                <div style="font-size:11px; color:#6C757D;">{row['VB_M']:.0f} M€ · PMVL {pmvl_sign}{row['PMVL_M']:.0f} M€</div>
            </div>
            <div style="text-align:right;">
                {badge}
                <div style="font-size:11px; color:#28A745; font-weight:600; margin-top:2px;">{dev_sign}{row['deviation']*100:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── COLONNE DROITE — Convention & Budgets ───────────────────
with col_right:
    st.markdown('<div class="section-title">🛡️ Convention KAVIGG</div>', unsafe_allow_html=True)
    
    alertes_critiques = [c for c in CONTRAINTES if c['pct'] >= 90]
    alertes_warning = [c for c in CONTRAINTES if 80 <= c['pct'] < 90]
    alertes_ok = [c for c in CONTRAINTES if c['pct'] < 80]
    
    # Alertes critiques
    for c in alertes_critiques:
        st.markdown(f"""
        <div class="alert-critique">
            🔴 <b>{c['name']}</b><br>
            {c['actuel']}{c['unite']} — {c['pct']}% de limite
        </div>
        """, unsafe_allow_html=True)
    
    # Jauges détaillées
    st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
    
    for c in CONTRAINTES[:8]:
        pct = c['pct']
        if pct >= 90: cls = 'jauge-red'
        elif pct >= 80: cls = 'jauge-orange'
        else: cls = 'jauge-green'
        
        icon = '🔴' if pct >= 95 else '🟡' if pct >= 80 else '🟢'
        
        st.markdown(f"""
        <div class="jauge-container">
            <div class="jauge-label">
                <span>{icon} {c['name']}</span>
                <span style="font-weight:700; color:{'#DC3545' if pct>=90 else '#FD7E14' if pct>=80 else '#28A745'};">{pct}%</span>
            </div>
            <div class="jauge-bar-bg">
                <div class="jauge-bar-fill {cls}" style="width:{min(pct,100)}%;"></div>
            </div>
            <div class="jauge-pct">{c['actuel']}{c['unite']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Budgets RC/PMVR
    st.markdown('<div class="section-title">💰 Budgets RC / PMVR</div>', unsafe_allow_html=True)
    
    rc_pct = abs(RC_YTD)/BUDGET_RC*100
    pmvr_pct = PMVR_YTD/BUDGET_PMVR*100
    
    for label, val, budget, pct, unite in [
        ('RC Réserve Capital.', RC_YTD, BUDGET_RC, rc_pct, 'M€'),
        ('PMVR Réalisées', PMVR_YTD, BUDGET_PMVR, pmvr_pct, 'M€'),
    ]:
        cls = 'jauge-red' if pct >= 90 else 'jauge-orange' if pct >= 70 else 'jauge-green'
        sign = "+" if val > 0 else ""
        st.markdown(f"""
        <div class="jauge-container">
            <div class="jauge-label">
                <span style="font-weight:600;">{label}</span>
                <span style="font-weight:700;">{pct:.0f}%</span>
            </div>
            <div class="jauge-bar-bg">
                <div class="jauge-bar-fill {cls}" style="width:{min(pct,100)}%;"></div>
            </div>
            <div class="jauge-pct">{sign}{val:.1f} {unite} / {budget:.0f} {unite}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION BAS — Narrateur + Détail
# ══════════════════════════════════════════════════════════════
st.markdown("---")
col_narr, col_detail = st.columns([2,3])

with col_narr:
    st.markdown('<div class="section-title">📝 Narrateur Automatique</div>', unsafe_allow_html=True)
    
    top_poche = df_data.nlargest(1,'score').iloc[0]
    bot_poche = df_data.nsmallest(1,'score').iloc[0]
    
    narrateur_text = f"""En scénario <b>{scenario}</b>, le modèle SDA identifie <b>{top_poche['Poche']}</b> 
    comme la poche la plus attractive (score {top_poche['score']:+.2f}), 
    portée par un alpha tactique de {int(top_poche['alpha']):+d} et une richesse latente 
    {'positive' if top_poche['PMVL_M'] > 0 else 'négative'} de {top_poche['PMVL_M']:+.0f} M€. 
    À l'inverse, <b>{bot_poche['Poche']}</b> présente le signal le plus défavorable 
    (score {bot_poche['score']:+.2f}). 
    La contrainte de sensibilité reste tendue à <b>95% de sa limite</b> — 
    toute surpondération duration doit être compensée par une réduction ailleurs."""
    
    st.markdown(f'<div class="narrateur-box">{narrateur_text}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Décomposition du score
    st.markdown('<div class="section-title">🔬 Décomposition Score — ' + top_poche['Poche'] + '</div>', unsafe_allow_html=True)
    
    contributions = {
        'Alpha (α)': top_poche['alpha'],
        f'Sharpe (w_s×Ŝ)': w_s*top_poche['sharpe_norm'],
        f'Richesse (w_3×Δ*)': w_3*top_poche['delta_star'],
        f'RoSCR (w_4×R)': w_4*top_poche['roscr_norm'],
    }
    total = sum(contributions.values())
    
    fig_decomp = go.Figure(go.Bar(
        x=list(contributions.values()),
        y=list(contributions.keys()),
        orientation='h',
        marker_color=['#2E75B6' if v >= 0 else '#DC3545' for v in contributions.values()],
        text=[f"{v:+.3f}" for v in contributions.values()],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig_decomp.add_vline(x=0, line_color='#343A40', line_width=1)
    fig_decomp.update_layout(
        height=180, margin=dict(l=0,r=60,t=10,b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        xaxis=dict(gridcolor='#F0F0F0', zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=11)),
        showlegend=False,
    )
    st.plotly_chart(fig_decomp, use_container_width=True)

with col_detail:
    st.markdown('<div class="section-title">📋 Tableau Détaillé — Toutes les Poches</div>', unsafe_allow_html=True)
    
    df_display = df_data[df_data['Poche'].isin(SDA_POCHES)].copy()
    df_display = df_display.sort_values('score', ascending=False)
    
    # Robustesse — nb scénarios où score > 0
    robustesse = []
    for _,row in df_display.iterrows():
        p = row['Poche']
        idx = SDA_POCHES.index(p)
        count = sum(1 for sc in ALPHAS.values() if sc[idx] + w_s*row['sharpe_norm'] + w_3*row['delta_star'] + w_4*row['roscr_norm'] > 0)
        robustesse.append(f"{count}/6")
    df_display['Robustesse'] = robustesse
    
    def color_score(val):
        if val >= 1.0: return 'color: #28A745; font-weight:700'
        if val >= 0.3: return 'color: #5BA85D; font-weight:600'
        if val >= -0.3: return 'color: #6C757D'
        if val >= -1.0: return 'color: #FD7E14; font-weight:600'
        return 'color: #DC3545; font-weight:700'
    
    def color_pmvl(val):
        return 'color: #28A745' if val > 0 else 'color: #DC3545'
    
    df_show = df_display[['Poche','Noeud','VB_M','PMVL_M','pct','alpha','score','deviation','Robustesse']].copy()
    df_show.columns = ['Poche','Nœud','VB (M€)','PMVL (M€)','% ptf','Alpha','Score','Déviation','Robustesse']
    df_show['VB (M€)'] = df_show['VB (M€)'].apply(lambda x: f"{x:,.0f}")
    df_show['PMVL (M€)'] = df_show['PMVL (M€)'].apply(lambda x: f"{x:+,.0f}")
    df_show['% ptf'] = df_show['% ptf'].apply(lambda x: f"{x:.1f}%")
    df_show['Score'] = df_show['Score'].apply(lambda x: f"{x:+.2f}")
    df_show['Déviation'] = df_show['Déviation'].apply(lambda x: f"{x*100:+.1f}%")
    df_show['Alpha'] = df_show['Alpha'].apply(lambda x: f"{int(x):+d}")
    
    st.dataframe(
        df_show,
        use_container_width=True,
        height=420,
        hide_index=True,
    )

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; font-size:11px; color:#ADB5BD; padding:8px;">
    SDA V4 · BNP Paribas Cardif · Investments Allocation & Optimisation · 
    Données au 22/06/2026 · Version prototype · 
    <b style="color:#1F3864;">Confidentiel</b>
</div>
""", unsafe_allow_html=True)
