# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 16:22:22 2020
Binomial.py
Calculating European and American option value using a binomial tree
Inspired by:
http://janroman.dhis.org/stud/I2014/CRR/CRR.py and
https://github.com/saulwiggin/finance-with-python/blob/master/p4f.py
@author: Linh Ngo
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def Binomial(n, S, K, r, t, u, d, i, opt_type):
    '''
    For simplicity, volatility (v) is not taken into account
    To include v, u = np.exp(v*np.sqrt(At))
    '''

    At = t/n
    p = (np.exp((r-i)*At)-d) / (u-d)
    # Binomial price tree
    stockprice = np.zeros((n+1, n+1))
    stockprice[0, 0] = S
    for i in range(1, n+1):
        stockprice[i, 0] = stockprice[i-1, 0]*u
        for j in range(1, i+1):
            stockprice[i, j] = stockprice[i-1, j-1]*d
    # Option value at final node
    optionvalue = np.zeros((n+1, n+1))
    for j in range(n+1):
        if opt_type == "Euro_Call" or opt_type == "American_Call":
            optionvalue[n, j] = max(0, stockprice[n, j]-K)
        if opt_type == "Euro_Put" or opt_type == "American_Put":
            optionvalue[n, j] = max(0, K-stockprice[n, j])
    # Backward calculation for option price
    for i in range(n-1, -1, -1):
        for j in range(i+1):
            if opt_type == "American_Put":
                optionvalue[i, j] = max(0, K-stockprice[i, j],
                                        np.exp(-r*At)*(p*optionvalue[i+1, j] +
                                        (1-p)*optionvalue[i+1, j+1]))
            if opt_type == "Euro_Put":
                optionvalue[i, j] = max(0, np.exp(-r*At)*(p*optionvalue[i+1, j]
                                        + (1-p)*optionvalue[i+1, j+1]))
            if opt_type == "American_Call":
                optionvalue[i, j] = max(0, stockprice[i, j]-K,
                                        np.exp(-r*At)*(p*optionvalue[i+1, j] +
                                        (1-p)*optionvalue[i+1, j+1]))
            if opt_type == "Euro_Call":
                optionvalue[i, j] = max(0, np.exp(-r*At)*(p*optionvalue[i+1, j]
                                        + (1-p)*optionvalue[i+1, j+1]))    

    return np.round(optionvalue[0, 0], 4), stockprice.round(4), optionvalue.round(4)


def Price_tree(n, price_mtrx):
    G = nx.Graph()
    for i in range(0, n+1):
        for j in range(1, i+2):
            if i < n:
                G.add_edge((i, j), (i+1, j))
                G.add_edge((i, j), (i+1, j+1))
    posG = {}           # Dictionary of nodes position
    labeldict = {}      # Dictionary of nodes' labels
    for node in G.nodes():
        posG[node] = (node[0], n+2 + node[0] - 2*node[1])
        labeldict[node] = price_mtrx[node[0], node[1]-1]
    nx.draw(G, pos=posG, labels=labeldict, with_labels=True, node_size=1500,
            node_color='w')
    return posG


def Value_tree(n, value_mtrx):
    G = nx.Graph()
    for i in range(0, n+1):
        for j in range(1, i+2):
            if i < n:
                G.add_edge((i, j), (i+1, j))
                G.add_edge((i, j), (i+1, j+1))
    posG = {}           # Dictionary of nodes position
    labeldict = {}      # Dictionary of nodes' label
    for node in G.nodes():
        posG[node] = (node[0], n+2 + node[0] - 2*node[1])
        labeldict[node] = value_mtrx[node[0], node[1]-1]
    nx.draw(G, pos=posG, labels=labeldict, with_labels=True, node_size=1500,
            node_color='w')
    return posG


if __name__ == '__main__':
    # Inputs
    n = 2     # No.of binomial steps
    S = 50    # Current price of the underlying asset
    K = 52    # Strike price of the option
    r = 0.05  # Continuously compounded interest rate
    t = 2     # Maturity of the option (years)
    i = 0     # Dividend yield
    u = 1.2   # Up factor
    d = 0.8   # Down factor
    opt_type = 'American_Put'

    current_option_value = Binomial(n, S, K, r, t, u, d, i, opt_type)[0]
    price_mtrx = Binomial(n, S, K, r, t, u, d, i, opt_type)[1]
    value_mtrx = Binomial(n, S, K, r, t, u, d, i, opt_type)[2]
    print('The current value of the ' + opt_type + ' option is',
          current_option_value)

    print(price_mtrx)
    price_tree = Price_tree(n, price_mtrx)
    plt.savefig('Binomial_Price_Tree.png', dpi=300, bbox_inches='tight')
    plt.clf()

    print(value_mtrx)
    value_tree = Value_tree(n, value_mtrx)
    plt.savefig('Binomial_Value_Tree.png', dpi=300, bbox_inches='tight')
