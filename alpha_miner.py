import itertools
import graphviz




class Alpha(object):
 
    
    def __init__(self,log, myuuid):
        self.log = log
        self.outputname = str(myuuid)
        # all activities
        (self.tl, self.ti, self.to) = self._build_tl_ti_to_set(self.log)
        # directly follows
        self.df = self._build_df_set(self.log)
        # causal
        self.caus = self._build_caus_set(self.df)
        # unrelated
        self.unrel = self._build_unrel_set(self.tl, self.df)
        # parallel
        self.parallel = self._build_parallel_set(self.tl, self.df)
        # determine places and their connections
        self.xl = self._build_xl_set(self.tl, self.unrel, self.caus)
        # remove non-maximal pairs from xl
        self.yl = self._build_yl_set(self.xl)
        # build the petri net
        self._build_pn_from_alpha(self.tl, self.yl, self.ti, self.to, self.outputname)
       

    def _build_tl_ti_to_set(self, log):
        # set of all activites
        tl = set()
        # set of all start activities
        ti = set()
        # set of all end activities
        to = set()
        for trace in log:
            for activity in trace:
                tl.add(activity)
                ti.add(trace[0])
                to.add(trace[-1])
        return (tl, ti, to)

   
    def _build_df_set(self, log):
        # directly follows: one activity directly follows on another one in the trace
        df = set()
        for trace in log:
            for i in range(0, len(trace)-1):
                df.add((trace[i], trace[i+1]))
        return df
    
    def _build_caus_set(self, ds):
        caus = set()
        for caus_tuple in ds:
            # add tuple to causality set if the reverse tuple is not 
            # in the directly follows set
            if caus_tuple[::-1] not in ds: 
                caus.add(caus_tuple)
        return caus

    def _build_unrel_set(self, tl, df):
        # if x does not follow y and also not the other way around
        unrel = set()
        for x in tl:
            for y in tl:
                if (x, y) not in df and (y,x) not in df:
                    unrel.add((x, y))
        return unrel

    def _build_parallel_set(self, tl, df):
        # x follows y and also the other way around
        parallel = set()
        for x in tl:
            for y in tl:
                    if (x, y) in df and (y,x) in df:
                        parallel.add((x, y))
        return parallel

    def _check_never_follow(self,A,unrel):
        # check if all activities of A (B) never follow one another
        for event in A:
            for event2 in A:
                if (event, event2) not in unrel:
                    return False
        return True

    def _check_causality(self,A,B, caus):
        # check if all elements of A are causally related to all elements of B
        for event in A:
            for event2 in B:
                if (event, event2) not in caus:
                    return False
        return True


    def _build_xl_set(self, tl, unrel, caus):
        xl = set()
        #create a subset containing possible combinations in tl up to the length of tl
        subsets = set()
        for i in range(1,len(tl)):
            for s in itertools.combinations(tl, i):
                subsets.add(s)
        #for each combination in the subset, check if all activities contained in it don't follow on each other
        for a in subsets:
            truea = self._check_never_follow(a, unrel)
            for b in subsets:
                trueb = self._check_never_follow(b, unrel)
        #if truea is unrelated and trueb is unrelated and both are causally related to each other, then add them to xl
                if truea and trueb and self._check_causality(a,b,caus):
                    xl.add((a,b))
        return xl
    

    def _build_yl_set(self, xl):
        # only maximal pairs of xl should be in yl
        yl = xl.copy()
        for x in xl:
            a = set(x[0])
            b = set(x[1])
            for y in xl:
                if a.issubset(y[0]) and b.issubset(y[1]):
                    if x != y:
                        yl.discard(x)
                        break
        return yl

    
    def _build_pn_from_alpha(self, tl, yl, ti, to, outputname):
        dot = graphviz.Digraph(name=outputname, node_attr= {'fontsize':'16', 'fontname': 'Arial'})
        
        # generate the places
        for elem in yl:
            dot.node(str(elem), str(elem), shape='oval') 
        # generate the transitions
        for elem in tl:
            dot.node(str(elem), shape="box")
            # generate ai and connect it to the start transitions
            if elem in ti:
                dot.node('iL')
                dot.edge('iL', str(elem))
            # generate ol and connect it to the end transitions
            if elem in to:
                dot.node('oL')
                dot.edge(str(elem), 'oL')

        #generate the edges between the places and transitions
        for (a, b) in yl:
            for activity in a:
                dot.edge(str(activity), str((a,b)))
            for activity in b:
                dot.edge(str((a,b)), str(activity))

        dot.render(directory='static', format='svg')