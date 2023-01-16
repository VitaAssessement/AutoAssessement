import pandas as pd
from tkinter import filedialog
import networkx as nx
import matplotlib.pyplot as plt
from bokeh.plotting import figure, curdoc, from_networkx
from bokeh.models import HoverTool
from bokeh.io import output_notebook, show, save

def nudge(pos, x_shift, y_shift):
    return {n:(x + x_shift, y + y_shift) for n,(x,y) in pos.items()}

G = nx.Graph()
xl = pd.ExcelFile("D:\\User\\Desktop\\vita\\template-coleta.xlsx")

swt_cdp = xl.parse('swt_cdp', header=0).to_numpy()
attrs = {}

for i in range(len(swt_cdp)):

    G.add_edge(swt_cdp[i][1],swt_cdp[i][7],Local_Interface=swt_cdp[i][3],Neighbor_Interface=swt_cdp[i][8])
    attrs[swt_cdp[i][1]] = {'Hostname':swt_cdp[i][0],'Capabilities':swt_cdp[i][5]}

nx.set_node_attributes(G, attrs)

pos = nx.spring_layout(G)

graph_renderer = from_networkx(G,nx.spring_layout(G))
TOOLTIPS=[("Hostname", "@Hostname"), ("Capabilities", "@Capabilities")]
plot = figure(tooltips = TOOLTIPS,x_range=(1,4), y_range=(0,3),
tools="lasso_select,pan,wheel_zoom")

hover_edges = HoverTool(
tooltips=[('Local Interface','@Local_Interface'),('Neighbor Interface','@Neighbor_Interface')],
renderers=[graph_renderer.edge_renderer], line_policy="interp"
)

plot.renderers.append(graph_renderer)
plot.add_tools(hover_edges)
show(plot)