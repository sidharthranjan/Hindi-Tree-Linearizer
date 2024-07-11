# This code generates the different possible variants of corpus reference sentences and prints them in output folder. 
# Corpus file (HUTB.dep) should be in CONLL format in order to generate variants in linearized approach (preverbal reordering only).

from nltk import *
from nltk.corpus import *
from nltk import treetransforms, bracket_parse
from copy import deepcopy
from array import * 
import numpy as np
import collections
import matplotlib.pyplot as plt
import sys,os
import math
from itertools import *
from pylab import *
from string import lower
from collections import Counter
import itertools


  
def isPunct(w,p):

    retval=False;

    if w=="(" or w=="-lrb-":
        w="-LRB-";
    elif w==")" or w=="-rrb-":
        w="-RRB-";
    
    if (p==w or p=="." or p==":" or p=="," or p=="``" or p=="''" or p.endswith("RB-") or p.endswith("CB-")) and not (p=="$"):
        retval=True;

    return retval;

def deplenGibson(nodelist,i,j):
    d=0;
    if i>j:
        k=i;i=j;j=k;
    for ind in range(i+1,j):
        node=nodelist[ind];
        #print node['tag']
        word, tag = node['word'], node['tag'];
        if isPunct(word,tag):
            continue;
        if tag.startswith("n") or tag.startswith("v"):
            d=d+1;
    return d;

def deplenTemperly(nodelist,i,j):
    d=0;
    if i>j:
        k=i;i=j;j=k;
    for ind in range(i+1,j):
        node=nodelist[ind];
        word, tag = node['word'], node['tag'];
        if not isPunct(word,tag):
            d=d+1;
    return d;

def calculateConstLen(graph, i):
    node = graph.nodelist[i]
    #if (node['tag'] == '.'):
    #    return None;
    return 1 + sum(calculateConstLen(graph, nod) for nod in node['deps']);

def swap(graph,i):
        node= graph.nodelist[i]
        if (node['tag'] == '.'):
            return 0;
        return 0

def getminconst(graph, pos):
	node = graph.nodelist[pos]
	if len(node['deps']) == 0 :
	        return node['address']
	return min( node['address'] , min(getminconst(graph, nod) for nod in node["deps"]));

def calculateDepLen(graph,sent,values): #Calculation of Dependency Length
    d1=0;
    d2=0;
    a=0;
    cons = [];
    deplen = [];
    dif = [];
    global iter
    iter += 1
    f = open(outputFolder+'/s'+str(iter) + '.txt', 'w')
    dg = 0
    for i, node in enumerate(graph.nodelist[1:]):
        word, wpos, hind, rel, wind,tag = node['word'], node['tag'], node['head'], node['rel'],node['address'],node['tag'];
        hnode=graph.nodelist[hind];
        hword,hpos=hnode['word'],hnode['tag'];
        #if hword==None or hpos==None:
            #continue;        
        if rel=="rsym" or tag=="punc" or isPunct(word,wpos) or isPunct(hword,hpos):
            continue;
        dtt = deplenTemperly(graph.nodelist,wind,hind);
        dg += dtt
    for i, node in enumerate(graph.nodelist[1:]):
    	if(node['rel'] != 'main' or node['tag'] == "CC"):
    		continue
        word, wpos, hind, rel, wind = node['word'], node['tag'], node['head'], node['rel'],node['address'];
        jj = 0
        while jj < len(node['deps']):
                j = node['deps'][jj]
                if (graph.nodelist[j]['tag'] == 'punc'):
        		node['deps'].pop(jj);
                        continue
        	conlen = calculateConstLen(graph, j)
        	condistanceLen = (wind - graph.nodelist[j]['address'])
        	if (graph.nodelist[j]['tag'] == 'SYM'):
        		node['deps'].pop(jj);
        		continue
        	if(condistanceLen < 0):
        		node['deps'].pop(jj);
        	        continue
                jj+=1

        countless = 0
        counteql = 0
        countgre = 0
        delta = []
        # generation of variants in linearized approach
        for j in itertools.islice(itertools.permutations(node['deps']), 100):
                sent = ""
                addddrel = ""
                # print each constituents
                l = 0
                deltaTemprly = 0
                sentlen = 0
                for iii in j:                                   # j e.g. (1, 6, 13, 26, 28)
                        iu = getminconst(graph, iii)            #minimum address word in a constituent
                        iuu = calculateConstLen(graph, iii)     #length of constituent
                        ik = 0
                        while ik < iuu :                        #add all constituents in order of address
                                if(graph.nodelist[ik+iu]['tag'] != 'punc'):
                                    sent += (graph.nodelist[ik+iu]['word']).encode('utf8') + " "
                                    sentlen = sentlen + 1
                                #addddrel += (graph.nodelist[ik+iu]['rel']).encode('utf8') + " "
                                if (graph.nodelist[ik+iu]['address'] == iii):
                                        deltaTemprly += iii - l - 1
                                        #print graph.nodelist[ik+iu]['word'] + "\t"+str(deltaTemprly)+"\t"+str(iii)+"\t"+ str(l)
                                l  += 1
                                ik += 1
                l = node['address']
                dependencylen = dg + deltaTemprly
                #print deltaTemprly;
                values.append(deltaTemprly)                
                while l < len(graph.nodelist):
                        if(graph.nodelist[l]['tag'] != 'punc'):
                            sent += (graph.nodelist[l]['word']).encode('utf8') + " "
                            sentlen = sentlen+1
                        l+= 1
                f.write(sent + '\n')
                print sent
                #print sentlen
                #sys.exit()
                continue
    	f.close()
    retval=[];  
    retval.append(values)
    #sys.exit()
    return retval

#Extract deplen and print it to filesent
def extractFromHUTB(hutb_root,sects):
    for sect in sects:
        depbank=DependencyCorpusReader(hutb_root,sect+".dep");
        fileid=depbank.fileids()[0];
        print "Reading dep file: "+fileid;
        graphs = depbank.parsed_sents(fileid)
        sents=depbank.sents(fileid);
        values = []
        #Iterate over sents/trees in a file
        for i in range(0, len(graphs)):
            sent=(" ".join(sents[i])).strip();
            r = calculateDepLen(graphs[i],sent,values);        
        f.close();

    	
if __name__ == '__main__':

    #HUTB sections
    hutb_root='/home/user/Desktop/HUTB_Corpus/' #Address where your hutb.dep(corpus) file exist
    outputFolder = "/home/user/Desktop/HUTB_Corpus/output" #Address where you want the variants to be generated
    sects=[];
    depbank=BracketParseCorpusReader(hutb_root,".*\.dep");
    iter=0
    for sect in depbank.fileids():
        sects.append(sect.replace(".dep",""));
        
    #Printing corpus info
    print ("\n");
    print ("Calculating dependency statistics from corpus: "+hutb_root);
    print ("Section(s): "+str(sects));
    
    #Extract data from HUTB sections
    extractFromHUTB(hutb_root,sects);
