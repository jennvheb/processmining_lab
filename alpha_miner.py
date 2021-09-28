import copy
import itertools
import tempfile

#from snakes.nets import *
#f
"""import snakes.plugins
snakes.plugins.load('gv', 'nets', 'my_nets')
from my_nets import *"""
import graphviz
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils





class Alpha(object):
 
    
    def __init__(self,log):
        self.log = log
        # all activites
        self.tl = self._build_tl_set(self.log)
        # directly follows
        self.df = self._build_df_set(self.log)
        # causal
        self.caus = self._build_caus_set(self.df)
        # unrelated
        self.unrel = self._build_unrel_set(self.tl, self.df)
        # parallel
        self.parallel = self._build_parallel_set(self.tl, self.df)
    
        self.xl = self._build_xl_set(self.tl, self.unrel, self.caus)
        self.yl = self._build_yl_set(self.xl)
        self.ti = self._build_ti_set(self.log)
        self.to = self._build_to_set(self.log)
       
        self._build_pn_from_alpha(self.yl, self.ti, self.to)
       

    def _build_tl_set(self, log):
        tl = set()
        for trace in log: 
            for activity in trace:
                tl.add(activity)
        return tl

    def _build_ti_set(self, log):
        ti = set()
        for trace in log:
            ti.add(trace[0])
        return ti

    def _build_to_set(self, log):
        to = set()
        for trace in log:
            to.add(trace[-1])
        return to
    
    def _build_df_set(self, log):
        # directly follows relation: x>y
        df = set()
        for trace in log:
            for i in range(0, len(trace)-1):
                df.add((trace[i], trace[i+1]))
        return df
    
    def _build_caus_set(self, ds):
        caus = set()
        for tuple in ds:
            # add tuple to causality set if the reverse tuple is not in the direct successions set
            if tuple[::-1] not in ds: 
                caus.add(tuple)
        return caus

    def _build_unrel_set(self, tl, df):
        unrel = set()
        for x in tl:
            for y in tl:
                if (x, y) not in df and (y,x) not in df:
                    unrel.add((x, y))
        print("unrel:", unrel)
        return unrel

    def _build_parallel_set(self, tl, df):

        parallel = set()
        
        for x in tl:
            for y in tl:
                    if (x, y) in df and (y,x) in df:
                        parallel.add((x, y))
        print("parallel:", parallel)
        return parallel

    def _check_set(self,A,ncs):
        for event in A:
            for event2 in A:
                if (event, event2) not in ncs:
                    return False
        return True

    def _check_outsets(self,A,B, cs):
        for event in A:
            for event2 in B:
                if (event, event2) not in cs:
                    return False
        return True


    def _build_xl_set(self, tl, unrel, caus):

        xl = set()
        subsets = set()
        for i in range(1,len(tl)):
            for s in itertools.combinations(tl, i):
                subsets.add(s)
        for a in subsets:
            reta = self._check_set(a, unrel)
            for b in subsets:
                retb = self._check_set(b, unrel)
                if reta and retb and self._check_outsets(a,b,caus):
                    xl.add((a,b))
        print("xl:", xl)
        return xl
    

    def _build_yl_set(self, xl):
        # only maximal pairs of xl should be in yl
   
        yl = copy.deepcopy(xl)
        yl = xl.copy()
        for x in xl:
            a = set(x[0])
            b = set(x[1])
            for y in xl:
                if a.issubset(y[0]) and b.issubset(y[1]):
                    if x != y:
                        yl.discard(x)
                        break
        print("yl", yl)
        return yl

    
    def _build_pn_from_alpha(self, yl, ti, to):
        #so graphics work now but the output is still crap
        #i need to read the doc properly when i find the time
        dot = graphviz.Digraph("alpha")

        il = dot.node("iL")
        for i in ti:
            dot.edge(str(il), str(i))

        ol = dot.node("oL")
        for o in to:
            dot.edge(str(o),str(ol))

        for elem in yl:
            dot.node(str(elem),str(elem), shape="circle")
                

        for (a, b) in yl:
            dot.node(str(a),str(a), shape="box")
            dot.node(str(b),str(b), shape="box")
            for activity in a:
                dot.edge(str(activity), str((a,b)), )
            for activity in b:
                dot.edge(str((a,b)), str(activity))
            
        

        #dot.format = 'svg'
        dot.view(tempfile.mktemp('.gv.svg'))
        """
        for elem in yl:
            for i in elem[0]:
                dot.edge("%s".format(i), "%s".format(elem))
                dot.node("%s".format(i), shape="box")
                dot.node("%s".format(elem), shape="circle")
                
            for i in elem[1]:
                dot.edge("%s".format(elem), "%s".format(i) )
                dot.node("%s".format(i), shape="box")
                
        for i in ti:
            dot.edge("%s".format(il), "%s".format(i))
        for o in to:
            dot.edge("%s".format(o),"%s".format(ol))

        #dot.format = 'svg'
        dot.view(tempfile.mktemp('.gv.svg'))
        """
        


        

