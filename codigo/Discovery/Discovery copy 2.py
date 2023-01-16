import pandas as pd
from tkinter import filedialog
import networkx as nx
import matplotlib.pyplot as plt
import PIL

icons = {
    "router": "D:/User/Desktop/vita/icons/router.png",
    "switch": "D:/User/Desktop/vita/icons/switch.png",
    "host": "D:/User/Desktop/vita/icons/host.png",
}

# Load images
images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

G = nx.Graph()
xl = pd.ExcelFile("D:\\User\\Desktop\\vita\\template-coleta.xlsx")

swt_cdp = xl.parse('swt_cdp', header=0).to_numpy()

xl.close()
attrs = {}

for i in range(len(swt_cdp)):

    G.add_edge(swt_cdp[i][1],swt_cdp[i][7],Label=swt_cdp[i][3].replace('Gigabit','Gb').replace('Ethernet','Eth')+'  -  '+swt_cdp[i][8].replace('Gigabit','Gb').replace('Ethernet','Eth'))
    attrs[swt_cdp[i][7]] = {'Hostname':swt_cdp[i][2],'Capabilities':swt_cdp[i][5]}

nx.set_node_attributes(G, attrs)

for node in G.nodes.data():

    if not(len(node[1]) <= 0 or node[1] == {}):
        if (str(node[1]['Capabilities']).__contains__('Switch')):
            G.add_node(node[0],image=images['switch'])
        elif (str(node[1]['Capabilities']).__contains__('Router')):
            G.add_node(node[0],image=images['router'])
        else:
            G.add_node(node[0],image=images['host'])
    else:
        G.add_node(node[0],image=images['host'])

fig, ax = plt.subplots()
pos = nx.spring_layout(G)
nodes = nx.draw_networkx_nodes(G, pos=pos, ax=ax,node_size=1500,node_color='White')
nx.draw_networkx_edges(G, pos=pos, ax=ax)

nx.draw_networkx_edge_labels(G, pos,edge_labels={edge[0:2]:edge[2]['Label'] for edge in G.edges.data()},font_color='blue', rotate=False,font_size=8)

annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

idx_to_node_dict = {}
for idx, node in enumerate(G.nodes):
    idx_to_node_dict[idx] = node

def update_annot(ind):
    node_idx = ind["ind"][0]
    node = idx_to_node_dict[node_idx]
    xy = pos[node]
    annot.xy = xy
    node_attr = {'node': node}
    node_attr.update(G.nodes[node])
    text = '\n'.join(f'{k}: {v}' for k, v in node_attr.items())
    text = text[0:text.index('image')-1].replace('node','IP')
    annot.set_text(text)

def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = nodes.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

# Transform from data coordinates (scaled between xlim and ylim) to display coordinates
tr_figure = ax.transData.transform
# Transform from display to figure coordinates
tr_axes = fig.transFigure.inverted().transform

# Select the size of the image (relative to the X axis)
icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
icon_center = icon_size / 2.0

# Add the respective image to each node
for n in G.nodes:
    xf, yf = tr_figure(pos[n])
    xa, ya = tr_axes((xf, yf))
    # get overlapped axes and plot icon
    a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
    a.imshow(G.nodes[n]["image"])
    a.axis("off")

plt.show()