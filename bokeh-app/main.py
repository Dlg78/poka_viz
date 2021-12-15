from os.path import join, dirname
import datetime

# import pandas as pd
# from scipy.signal import savgol_filter

# from bokeh.io import curdoc
# from bokeh.layouts import row, column
# from bokeh.models import ColumnDataSource, DataRange1d, Select
# from bokeh.palettes import Blues4
# from bokeh.plotting import figure

import pandas as pd

from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import output_file, show, output_notebook, curdoc
from bokeh.models import HoverTool, Slider, Select, Dropdown, Div, Button, Slider, Range1d, Title, NumeralTickFormatter, Circle, Square, Asterisk, Scatter, LassoSelectTool, BoxSelectTool
from bokeh.models.widgets import Panel, Tabs, MultiChoice, Spinner, MultiSelect
from bokeh.layouts import row, column, gridplot, widgetbox, layout
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20, Spectral10, Turbo256, Turbo
# from bokeh.plotting.figure.Figure import sq

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

from bokeh.embed import file_html, server_document
from bokeh.resources import CDN

from bokeh.themes import built_in_themes,Theme

cat_columns = ['','country_category','work_station_category','production_line_category','plant_category','division_category','record_day_name','record_month_name','record_year_month','record_year']
idx_columns = ['tenant_id','record_date']
int_format = NumeralTickFormatter(format="#,##0")
global circle1
global circle2
global circle3

def get_cmap(df,fld:str):
    cat = sorted(df[fld].unique())
    cat_num = len(cat)
    if cat_num <= 11:
        return factor_cmap(field_name=fld,palette=Turbo[cat_num],factors=cat)
    else:
        color_step = int(256/len(cat))
        palette_colors=[]
        for color in range(0,255,color_step):
            palette_colors.append(Turbo256[color])
        return factor_cmap(field_name=fld,palette=palette_colors,factors=cat) #palette=Turbo256[len(cat)]

def get_source(selected_vars:list):
    df_src = pd.read_csv('bokeh-app/data/main_dataframe_head.csv',parse_dates=['record_date'])
    df_src['record_year'] = df_src['record_year'].astype(str)
    return df_src[selected_vars]

def tab1_list_df_vars(var1,var2,var3,var_cat,var_size):
    lst = idx_columns.copy()
    if var1 == '':
        lst.append(selectable_columns[1])
    else:
        lst.append(var1)

    if var2 == '':
        lst.append(selectable_columns[2])
    else:
        lst.append(var2)

    if var3 == '':
        lst.append(selectable_columns[3])
    else:
        lst.append(var3)
    
    if var_cat != '':
        lst.append(var_cat)
        
    if var_size != '':
        lst.append(var_size)

    return lst

def set_selectable_columns():
    df = pd.read_csv('bokeh-app/data/main_dataframe_head.csv',parse_dates=['record_date'])
    df['record_year'] = df['record_year'].astype(str)

    selectable_columns = df.columns.tolist()
    selectable_columns = list(set(selectable_columns) - set(idx_columns)  - set(cat_columns))
    selectable_columns.insert(0,'')
    selectable_columns.sort()
    return selectable_columns

def set_selectable_tenants():
    df = pd.read_csv('bokeh-app/data/main_dataframe_head.csv',parse_dates=['record_date'])
    df['record_year'] = df['record_year'].astype(str)
    
    selectable_tenants = sorted(df.tenant_id.unique())
    selectable_tenants.insert(0,'')
    selectable_tenants.sort()
    return selectable_tenants

def build_plot(p, df, var_x, var_y, transparency, var_cat, var_size):
        if var_size != '':
            temp = ((df[var_size] - df[var_size].min()) / (df[var_size].max() - df[var_size].min())) * 100
            df[var_size] = temp.round(0).astype(int)
        src = ColumnDataSource(df)
        if var_cat == '':
            cat_cmap = 'blue'
        else:
            cat_cmap = get_cmap(df,var_cat)
        
        p.title.text = '''Variable '{0}' contre Variable '{1}' '''.format(var_x,var_y)
        p.renderers = []
        if hasattr(p.legend,'items'):
                p.legend.items = []
        if var_cat != '' and var_size != '':
            c = p.circle(var_x,var_y,source=src,alpha=transparency,fill_color=cat_cmap,legend_field=var_cat,size=var_size,
                        hover_fill_color='black',
                        hover_line_color='black',
                        hover_alpha=1,
                        selection_fill_alpha=1,
                        selection_line_alpha=1,
                        nonselection_fill_alpha=transparency,
                        nonselection_line_alpha=transparency)
            
            hover = HoverTool(
                tooltips = [
                    ('locateur','@tenant_id'),
                    ('date','@record_date{%Y-%m-%d}'),
                    ('x-> {}'.format(var_x),'@{}'.format(var_x)),
                    ('y-> {}'.format(var_y),'@{}'.format(var_y)),
                    ('catégorie-> {}'.format(var_cat),'@{}'.format(var_cat)),
                    ('taille-> {}'.format(var_size),'@{}'.format(var_size))
                ],
                formatters={'@record_date' : 'datetime'},
                renderers = [c],
                mode = 'mouse'
            )
        elif var_cat != '' and var_size == '':
            c = p.circle(var_x,var_y,source=src,alpha=transparency,fill_color=cat_cmap,legend_field=var_cat,
                        hover_fill_color='black',
                        hover_line_color='black',
                        hover_alpha=1,
                        selection_fill_alpha=1,
                        selection_line_alpha=1,
                        nonselection_fill_alpha=transparency,
                        nonselection_line_alpha=transparency) #get_cmap(df,var_cat)

            hover = HoverTool(
                tooltips = [
                    ('locateur','@tenant_id'),
                    ('date','@record_date{%Y-%m-%d}'),
                    ('x-> {}'.format(var_x),'@{}'.format(var_x)),
                    ('y-> {}'.format(var_y),'@{}'.format(var_y)),
                    ('catégorie-> {}'.format(var_cat),'@{}'.format(var_cat))
                ],
                formatters={'@record_date' : 'datetime'},
                renderers = [c],
                mode = 'mouse'
            )
        elif var_cat == '' and var_size != '':
            c = p.circle(var_x,var_y,source=src,alpha=transparency,size=var_size,
                        hover_fill_color='black',
                        hover_line_color='black',
                        hover_alpha=1,
                        selection_fill_alpha=1,
                        selection_line_alpha=1,
                        nonselection_fill_alpha=transparency,
                        nonselection_line_alpha=transparency)

            hover = HoverTool(
                tooltips = [
                    ('locateur','@tenant_id'),
                    ('date','@record_date{%Y-%m-%d}'),
                    ('x-> {}'.format(var_x),'@{}'.format(var_x)),
                    ('y-> {}'.format(var_y),'@{}'.format(var_y)),
                    ('taille-> {}'.format(var_size),'@{}'.format(var_size))
                ],
                formatters={'@record_date' : 'datetime'},
                renderers = [c],
                mode = 'mouse'
            )
        else:
            c = p.circle(var_x,var_y,source=src,alpha=transparency,
                        hover_fill_color='black',
                        hover_line_color='black',
                        hover_alpha=1,
                        selection_fill_alpha=1,
                        selection_line_alpha=1,
                        nonselection_fill_alpha=transparency,
                        nonselection_line_alpha=transparency)

            hover = HoverTool(
                tooltips = [
                    ('locateur','@tenant_id'),
                    ('date','@record_date{%Y-%m-%d}'),
                    ('x-> {}'.format(var_x),'@{}'.format(var_x)),
                    ('y-> {}'.format(var_y),'@{}'.format(var_y))
                ],
                formatters={'@record_date' : 'datetime'},
                renderers = [c],
                mode = 'mouse'
            )
        
        lasso = LassoSelectTool(renderers = [c])
        box = BoxSelectTool(renderers = [c])
        p.add_tools(hover)
        p.add_tools(lasso)
        p.add_tools(box)
        
        p.x_range = Range1d(0, df[var_x].max())
        p.y_range = Range1d(0, df[var_y].max())
        p.xaxis.axis_label = var_x
        p.xaxis[0].formatter = int_format
        p.yaxis.axis_label = var_y
        p.yaxis[0].formatter = int_format
        p.title.align = 'center'

        return c

def select_on_change(event):
    global circle1
    global circle2
    global circle3
    
    vars_lst = tab1_list_df_vars(select_val1.value,select_val2.value,select_val3.value,select_cat.value,select_size.value)
    df_selected = get_source(vars_lst)
    
    circle1 = build_plot(plot_1, df_selected, select_val1.value, select_val2.value, alpha_slide.value, select_cat.value, select_size.value)
    circle2 = build_plot(plot_2, df_selected, select_val3.value, select_val2.value, alpha_slide.value, select_cat.value, select_size.value)
    circle3 = build_plot(plot_3, df_selected, select_val1.value, select_val3.value, alpha_slide.value, select_cat.value, select_size.value)
    
def change_transparency(attr, old, new):
    for glyph in [circle1.glyph, circle2.glyph, circle3.glyph]:
        glyph.fill_alpha = alpha_slide.value

def build_main_plot(event):
    main_plot.renderers = []
    src_col = idx_columns + [select_var_tab2.value,select_cat_tab2.value]
    df = get_source(src_col)
    df = df.loc[df[select_cat_tab2.value] == select_cat_val_tab2.value]
    l_list = []
    for tenant in select_tenant.options:
        df_src = df.loc[df['tenant_id'] == tenant].copy()
        src = ColumnDataSource(df_src)
        if tenant != select_tenant.value:
            l = main_plot.line('record_date',select_var_tab2.value,source=src,line_color='black',alpha=0.4,
                            hover_line_color='blue', hover_alpha=0.8)
            l_list.append(l)
    df_src = df.loc[df['tenant_id'] == select_tenant.value].copy()
    src = ColumnDataSource(df_src)
    main_plot.line('record_date',select_var_tab2.value,source=src,line_color='red',alpha=0.8,line_width=3)
    hover = HoverTool(
                tooltips = [
                    ('locateur','@tenant_id'),
                    ('date','@record_date{%Y-%m-%d}'),
                    ('y-> {}'.format(select_var_tab2.value),'@{}'.format(select_var_tab2.value))
                ],
                formatters={'@record_date' : 'datetime'},
                renderers = l_list,
                mode = 'mouse'
            )
    if len(main_plot.tools) > 5:
        main_plot.tools[-1] = hover
    else:
        main_plot.add_tools(hover)
    main_plot.yaxis.axis_label = select_var_tab2.value
    main_plot.xaxis.axis_label = 'Dates'
    main_plot.yaxis[0].formatter = int_format

    title1_main.text = ''''{0}' des locateurs '{1}' de la catégorie '{2}' '''.format(select_var_tab2.value,select_cat_val_tab2.value,select_cat_tab2.value)
    title2_main.text = '''focussé sur le locateur {0}'''.format(select_tenant.value)
    print('>>>')

def get_tenants_in_category(cat,val):
    src_col = idx_columns + [cat]
    df = get_source(src_col)
    tenants = df.loc[df[cat] == val,'tenant_id'].unique().tolist()
    tenants.sort()
    return tenants
    
def set_options_select_tenant(attr,old,new):
    tenants = get_tenants_in_category(select_cat_tab2.value,select_cat_val_tab2.value)
    select_tenant.options = tenants
    select_tenant.value = tenants[0]

def set_options_compare_tenants(attr,old,new):
    tenants = get_tenants_in_category(select_cat_tab2.value,select_cat_val_tab2.value)
    tenants_wo_selected = list(set(tenants) - set([select_tenant.value]))
    tenants_wo_selected.sort()
    compare_tenants.options = tenants_wo_selected
    
def set_category_values(attr,old,new):
    df = get_source([select_cat_tab2.value])
    vals = df[select_cat_tab2.value].unique().tolist()
    vals.sort()
    select_cat_val_tab2.options = vals
    select_cat_val_tab2.value = vals[0]

def get_tab2_line_graph(main_tenant,compare_tenant):
    src_col = idx_columns + [select_var_tab2.value,select_cat_tab2.value]
    df = get_source(src_col)
    df = df.loc[df[select_cat_tab2.value] == select_cat_val_tab2.value]
    fig = figure(title='Comparé à {0}'.format(compare_tenant),tools="pan,wheel_zoom,box_zoom,reset",x_axis_type='datetime',height=100,width=200)
    
    df_src = df.loc[df['tenant_id'] == compare_tenant].copy()
    src = ColumnDataSource(df_src)
    l1 = fig.line('record_date',select_var_tab2.value,source=src,line_color='blue',alpha=0.4)
    
    df_src = df.loc[df['tenant_id'] == main_tenant].copy()
    src = ColumnDataSource(df_src)
    l2 = fig.line('record_date',select_var_tab2.value,source=src,line_color='red',alpha=0.8,line_width=3)
    
    hover = HoverTool(
                tooltips = [
                    ('locateur','@tenant_id'),
                    ('date','@record_date{%Y-%m-%d}'),
                    ('y-> {}'.format(select_var_tab2.value),'@{}'.format(select_var_tab2.value))
                ],
                formatters={'@record_date' : 'datetime'},
                renderers = [l1, l2],
                mode = 'vline'
            )
    fig.add_tools(hover)

    fig.yaxis.axis_label = select_var_tab2.value
    fig.yaxis[0].formatter = int_format
    fig.xaxis.axis_label = 'Dates'
    fig.title.align = 'center'
    return fig
    
def build_tab2_gridplot_graphs(event):
    compared_tenants = compare_tenants.value
    graphs = []
    for t in compared_tenants:
        g = get_tab2_line_graph(select_tenant.value,t)
        if len(graphs) > 0:
            g.x_range = graphs[0].x_range
            g.y_range = graphs[0].y_range
        graphs.append(g)
        
    layout2.children[-1] = gridplot(graphs,ncols=nb_cols.value,merge_tools=True,sizing_mode='scale_both')
    layout2.children[-2] = Div(text='''<h3>Comparaison des '{0}' du locateur {1}</h3>'''.format(select_var_tab2.value,select_tenant.value),align='center')

selectable_columns = set_selectable_columns()
selectable_tenants = set_selectable_tenants()

# Presentation models
intro_div = Div(text="""
    <h1>Présentation du dashboard</h1>
    <h3>Contexte</h3>
    <p>Les données présentées dans ce dashboard proviennent de l'application Poka.  Cette application aide la gestion manifacturière et ces données sont donc confidentielles.</p>
    <h3>L'onglet 'Exploration des données'</h3>
    <p>Cet onglet permet un premier coup d'oeil aux données. En choisissant 3 variables numérique, celles-ci seront présentées l'une contre l'autre dans 3 graphiques de type 'nuage de points'. Ces 3 variables sont nécessaires avant de cliquer sur 'Charger les graphiques'.</p>
    <p>De plus, à ces 3 graphiques, vous pouvez aussi ajouter optionnellement une 4e variable qui sera présentée en jouant sur la taille des cercles de chaque graphique.</p>
    <p>À ces 4 possibilités de variables numériques, vous pouvez aussi sélectionner optionnellement une catégorie, qui affectera la couleur des points présentés.</p>
    <p>Finalement, la transparence des points peut aussi être changé, pour une meilleure visibilité de la dispersion des points.</p>
    <h3>L'onglet 'Analyse temporelle'</h3>
    <p>Cet onglet sert à comparer l'évolution dans le temps d'un locateur en comparant son évalotion à celles de d'autres locateurs d'une même catégorie.</p>
    <p>Pour le graphique supérieur, affichant une vue générale, il faut d'un premier temps sélectionner la catégorisation, puis la catégorie souhaitée de celle-ci. Ensuite, il faut sélectionner le locateur dont on souhaite focussé l'analyse. Enfin, il faut choisir une variable numérique, comme base de l'évolution à afficher. Après la sélection de ces 4 choix, il suffit de cliquer sur 'Afficher le graphique' pour voir le résultat.</p>
    <p>Pour la partie inférieur, il est possible de sélectionner les locateurs, dont on souhaiterait voir une comparaison isolée du locateur focus. D'abord, sélectionnez un ou plusieurs locateurs dans la liste affichée. Pour choisir plusieurs locateurs, cliquez et faites glisser pour sélectionner des locateurs côte-à-côte et/ou utilisez la touche 'control' en cliquant pour sélectionner des locateurs distancés. Une fois les locateurs choisis, déterminez sur combien de colonnes vous souhaitez voir les graphiques et cliquez finalement sur 'Afficher les graphiques'.</p>
    <h3>Terminologie</h3>
    <ul>
    <li>Locateur: <em>Pour que le client puisse utiliser l'application, celui-ci se voit r&eacute;server un espace sur un instance et un identifiant locateur lui est attribu&eacute;. Un client peut avoir un ou plusieurs identifiants locateur</em></li>
    <li>Variables num&eacute;riques
    <ul>
    <li>Pr&eacute;fixes
    <ul>
    <li>'created_': <em>Nombre de contenus cr&eacute;&eacute;s de la charact&eacute;ristique de l'application qui suit</em></li>
    <li>'modified_': <em>Nombre de contenus modifi&eacute;s de la caract&eacute;ristique de l'application qui suit</em></li>
    </ul>
    </li>
    <li>active_users: <em>Nombre d'utilisateurs uniques qui ont utilis&eacute; l'application</em></li>
    <li>activities: <em>Nombre d'activit&eacute;s effectu&eacute;es sur l'application</em></li>
    <li>connected_once: <em>Nombre d'utilisateurs qui se sont connect&eacute;s au moins une fois &agrave; l'application</em></li>
    <li>'_forms': <em>Caract&eacute;ristique formulaire de l'application</em></li>
    <li>'_news': <em>Caract&eacute;ristique de type publication de l'application</em></li>
    <li>'_problems': <em>Caract&eacute;ristique de type signalement de probl&egrave;mes de l'application</em></li>
    <li>'_skills': <em>Caract&eacute;ristique des comp&eacute;tences de l'application, pouvant &ecirc;tre associ&eacute; &agrave; un utilisateur</em></li>
    <li>'_skills_endorsement_requests': <em>Nombre de requ&ecirc;tes utilisateur pour recevoir l'approbation d'une comp&eacute;tence</em></li>
    <li>skills_endorsements: <em>Nombre de comp&eacute;tences approuv&eacute;s</em></li>
    <li>divisions: <em>Nombre de regroupements d'usines, d&eacute;termin&eacute; par le client</em></li>
    <li>form_completions: <em>Nombre de formulaires remplis</em></li>
    <li>plants: <em>Nombre d'usines associ&eacute;es au locateur</em></li>
    <li>production_lines: <em>Nombre de lignes de production associ&eacute;es au locateur</em></li>
    <li>views: <em>Nombre de contenus vu par les utilisateurs</em></li>
    <li>work_stations: <em>Nombre de postes de travail associ&eacute;s au locateur</em></li>
    <li>workinstructions: <em>Caract&eacute;ristique des instructions de travail de l'application</em></li>
    </ul>
    </li>
    <li>Variables cat&eacute;gorielles
    <ul>
    <li>Pr&eacute;fixe
    <ul>
    <li>'record_': <em>Cat&eacute;gories relatives &agrave; la date d'enregistrement des donn&eacute;es [record_date]</em></li>
    </ul>
    </li>
    <li>country_category: <em>Cat&eacute;gorisation selon le-s pays des usines du locateur</em></li>
    <li>work_station_category: <em>Cat&eacute;gorisation selon le nombre de postes de travail</em></li>
    <li>production_line_category: <em>Cat&eacute;gorisation selon le nombre de lignes de production</em></li>
    <li>plant_category: <em>Cat&eacute;gorisation selon le nombre d'usines</em></li>
    <li>division_category: <em>Cat&eacute;gorisation selon le nombre de divisions</em></li>
    <li>'_day_name': <em>Regroupement par jour de la semaine</em></li>
    <li>'_month_name': <em>Regroupement par mois</em></li>
    <li>'_year_month': <em>Regroupement par ann&eacute;e et mois</em></li>
    <li>'_year': <em>Regroupement par ann&eacute;e</em></li>
    </ul>
    </li>
    </ul>
""")
pan0 = Panel(child=intro_div,title='Présentation')
# Data exploration
    # Models
select_val1 = Select(title="Variable de l'axe des X pour les Graphiques 1 & 3",options=selectable_columns,value=selectable_columns[1])
select_val2 = Select(title="Variable de l'axe des Y pour les Graphiques 1 & 2",options=selectable_columns,value=selectable_columns[2])
select_val3 = Select(title="Variable axe X Graphique 2 & axe Y Graphique 3",options=selectable_columns,value=selectable_columns[3])
select_size = Select(title='Taille des points par',options=selectable_columns,value=None)
select_cat = Select(title='Couleur des points par',options=cat_columns,value=None)
load_graph = Button(label='Charger les graphiques',button_type='success')
alpha_slide = Slider(start=0.1,end=1,value=0.3,step=0.05,title='Transparence des points')
plot_1 = figure(tools="pan,wheel_zoom,box_zoom,reset,save") #lasso_select,
plot_2 = figure(tools="pan,wheel_zoom,box_zoom,reset,save")
plot_3 = figure(tools="pan,wheel_zoom,box_zoom,reset,save")
    # Creation & Dynamics
vars_lst = tab1_list_df_vars(select_val1.value,select_val2.value,select_val3.value,select_cat.value,select_size.value)
df_selected = get_source(vars_lst)

circle1 = build_plot(plot_1, df_selected, select_val1.value, select_val2.value, alpha_slide.value, select_cat.value, select_size.value)
circle2 = build_plot(plot_2, df_selected, select_val3.value, select_val2.value, alpha_slide.value, select_cat.value, select_size.value)
circle3 = build_plot(plot_3, df_selected, select_val1.value, select_val3.value, alpha_slide.value, select_cat.value, select_size.value)
df_selected = None

out_legend = None

plot_1.x_range = plot_3.x_range
plot_1.y_range = plot_2.y_range
plot_2.x_range = plot_3.y_range

load_graph.on_click(select_on_change)
alpha_slide.on_change('value',change_transparency)
    # Structure
page_title = Div(text='<h1>Exploration des données brutes</h1>')
widget_select_val = column(Div(),select_val1,select_val2,select_val3,select_size,select_cat,load_graph,Div(),Div(),alpha_slide)
plot_grid = gridplot([[Div(text='<h3>Graphique 1</h3>',align='center'),Div(text='<h3>Graphique 2</h3>',align='center')],
                        [plot_1,plot_2],
                        [Div(text='<h3>Graphique 3</h3>',align='center'),None],
                        [plot_3,out_legend]],
                        merge_tools=True) #,ncols=2
row_1 = row(widget_select_val,plot_grid)
layout1 = column(page_title,row_1)
pan1 = Panel(child=layout1,title='Exploration de données')

# Time analysis
    # Models
select_cat_tab2 = Select(title='Choisissez une catégorisation',options=cat_columns,value=None)
select_cat_val_tab2 = Select(title='Choisissez la catégorie',value=None)
select_tenant = Select(title='Choisissez quel locateur est le focus',options=selectable_tenants,value=None)
select_var_tab2 = Select(title='Choisissez la variable à afficher',options=selectable_columns,value=None)
compare_tenants = MultiSelect(title='Choisissez le-s locateur-s à comparer au locateur focus',options=[],value=[],width=500,height=200)
nb_rows = Spinner(title='Nombre de rangées',low=1,high= 20,value=2,step=1,sizing_mode='stretch_width',visible=False) #width=125,align=('start','center')
nb_cols = Spinner(title='Nombre de colonnes',low=1,high= 20,value=2,step=1,sizing_mode='stretch_width')
load_main_graph_tab2 = Button(label='Afficher le graphique',button_type='success',align='end')
load_graphs_tab2 = Button(label='Afficher les graphiques',button_type='success',align='start',height=80,sizing_mode='stretch_width')

main_plot = figure(tools="pan,wheel_zoom,box_zoom,reset,save",x_axis_type='datetime',sizing_mode='stretch_width') #,width=1200
title1_main = Title(text='',align='center')
title2_main = Title(text='',align='center')
    # Creation & Dynamics
main_plot.add_layout(title2_main,'above')
main_plot.add_layout(title1_main,'above')
main_plot.line([0,1],[0,1],alpha=0)

load_main_graph_tab2.on_click(build_main_plot)
select_cat_tab2.on_change('value',set_category_values)
select_cat_val_tab2.on_change('value',set_options_select_tenant)
select_tenant.on_change('value',set_options_compare_tenants)
load_graphs_tab2.on_click(build_tab2_gridplot_graphs)
    # Structure
tab2_page_title = Div(text="<h1>Analyse temporelle d'un locateur comparé à d'autres de la même catégorie</h1>",sizing_mode='stretch_width')
tab2_select_vars_main_graph = row(select_cat_tab2,select_cat_val_tab2,select_tenant,select_var_tab2,load_main_graph_tab2) #,sizing_mode='stretch_both'
tab2_graphs_size = column(nb_rows,nb_cols,load_graphs_tab2,width=200)
tab2_select_vars_graphs = row(compare_tenants,tab2_graphs_size)

layout2 = layout([
    [tab2_page_title],
    [tab2_select_vars_main_graph],
    [main_plot],
    [Div()],
    [tab2_select_vars_graphs],
    [Div()],
    [Div()]
])
pan2 = Panel(child=layout2,title='Analyse temporelle')


# city_select = Select(value=city, title='City', options=sorted(cities.keys()))
# distribution_select = Select(value=distribution, title='Distribution', options=['Discrete', 'Smoothed'])

# df = pd.read_csv(join(dirname(__file__), 'data/2015_weather.csv'))
# source = get_dataset(df, cities[city]['airport'], distribution)
# plot = make_plot(source, "Weather data for " + cities[city]['title'])

# city_select.on_change('value', update_plot)
# distribution_select.on_change('value', update_plot)

# controls = column(city_select, distribution_select)


tabs = Tabs(tabs=[pan0,pan1,pan2])
curdoc().add_root(tabs)
curdoc().title = "Poka"