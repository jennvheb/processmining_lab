import copy
import itertools
import tempfile
import graphviz




class Alpha(object):
 
    
    def __init__(self,log):
        self.log = log
        # all activites
        (self.tl, self.ti, self.to) = self._build_tl_ti_to_set(self.log)
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
       
        self._build_pn_from_alpha(self.tl, self.yl, self.ti, self.to)
       

    def _build_tl_ti_to_set(self, log):
        tl = set()
        ti = set()
        to = set()
        for trace in log: 
            for activity in trace:
                tl.add(activity)
                ti.add(trace[0])
                to.add(trace[-1])
        return (tl, ti, to)

   
    def _build_df_set(self, log):
        # directly follows relation: x>y
        df = set()
        for trace in log:
            for i in range(0, len(trace)-1):
                df.add((trace[i], trace[i+1]))
        return df
    
    def _build_caus_set(self, ds):
        caus = set()
        for caus_tuple in ds:
            # add tuple to causality set if the reverse tuple is not in the direct successions set
            if caus_tuple[::-1] not in ds: 
                caus.add(caus_tuple)
        return caus

    def _build_unrel_set(self, tl, df):
        unrel = set()
        for x in tl:
            for y in tl:
                if (x, y) not in df and (y,x) not in df:
                    unrel.add((x, y))
        return unrel

    def _build_parallel_set(self, tl, df):
        parallel = set()
        
        for x in tl:
            for y in tl:
                    if (x, y) in df and (y,x) in df:
                        parallel.add((x, y))
        return parallel

    def _check_never_follow(self,A,unrel):
        # check if all elements of A (B) never follow one another
        for event in A:
            for event2 in A:
                if (event, event2) not in unrel:
                    return False
        return True

    def _check_causality(self,A,B, caus):
        # check if all elements of A are causal dependencies to all elements of B
        for event in A:
            for event2 in B:
                if (event, event2) not in caus:
                    return False
        return True


    def _build_xl_set(self, tl, unrel, caus):
        xl = set()
        # make it pretty
        #create a subset containing possible combinations in tl up to the length of tl
        subsets = set()
        for i in range(1,len(tl)):
            for s in itertools.combinations(tl, i):
                subsets.add(s)
        #for each combination in the subset, check if all pairs contained in it don't follow on each other
        print("subsets", subsets)
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
        return yl

    
    def _build_pn_from_alpha(self, tl, yl, ti, to):
        dot = graphviz.Digraph("alpha")
        for elem in yl:
            dot.node(str(elem), str(elem)) 
        for elem in tl:
            dot.node(str(elem), shape="box")
            if elem in ti:
                dot.node('iL')
                dot.edge('iL', str(elem))
            if elem in to:
                dot.node('oL')
                dot.edge(str(elem), 'oL')
     
        for (a, b) in yl:
            for activity in a:
                dot.edge(str(activity), str((a,b)))
            for activity in b:
                dot.edge(str((a,b)), str(activity))

        dot.view(tempfile.mktemp('.gv.svg'))