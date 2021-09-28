import copy
import itertools
#import graphviz
#from snakes.nets import *
#from my_nets import *
#import snakes.plugins
#snakes.plugins.load('gv', 'nets', 'my_nets')
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
       
        self._build_pn_from_alpha(self.tl, self.yl, self.ti, self.to)
       

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

        # problem: outputs eg. (('a',), ('e', 'c')) instead of ('a',), ('c', 'e'))
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
        # same for xl
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

    
    def _build_pn_from_alpha(self, tl, yl, ti, to):
        '''''
        Problem: With PM4PY i get the error: "Petri Nets are bipartit graphs" on the loop through ti
        Problem: With snakes i get the import error for my_nets
        '''''
        net = PetriNet("new_petri_net")

        source = PetriNet.Place("source")
        sink = PetriNet.Place("sink")
        net.places.add(source)
        net.places.add(sink)


        
        for (a, b) in yl:
            t_1 = PetriNet.Transition("name_1", "%s" % (a, b))
            net.transitions.add(t_1)
            for activity in a:
                p_1 = PetriNet.Place("%s" % activity)
                net.places.add(p_1)
                petri_utils.add_arc_from_to(p_1, t_1, net)
            for activity in b:
                p_1 = PetriNet.Place("%s" % activity)
                net.places.add(p_1)
                petri_utils.add_arc_from_to(t_1, p_1, net)
            

        # Add arcs
        
        for i in ti:
            p_1 = PetriNet.Place("%s" % i)
            net.places.add(p_1)
            petri_utils.add_arc_from_to(source, p_1, net)
            
        for o in to:
            p_2 = PetriNet.Place("%s" % o)
            net.places.add(p_2)
            petri_utils.add_arc_from_to(p_2, sink, net)
        
        # Adding tokens
        initial_marking = Marking()
        initial_marking[source] = 1
        final_marking = Marking()
        final_marking[sink] = 1

        
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.view(gviz)

        '''
        net = PetriNet('alpha')
        # creating source, p_1 and sink place

        for t in tl:
            net.add_transition(Transition(t))

        initial_marking = net.add_place(Place('Start', [1]))
        for i in ti:
            net.add_input('Start', i, Variable('C'))

        final_marking = net.add_place(Place('End', [0]))  
        for o in to:
            net.add_output('End', o, Variable(o))       


            i = 1
        for (a, b) in yl:
            net.add_place(Place(str(i), []))
            for activity in a:
                net.add_output(str(i), activity, Variable('C'))
            for activity in b:
                net.add_input(str(i), activity, Variable('C'))
            i += 1
        
        '''

        
        

