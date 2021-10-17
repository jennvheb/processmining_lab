from alpha_miner import Alpha
import graphviz
import tempfile


class Heuristic():
    def __init__(self, log, thrshld_df, thrshld_dm):
        self.log = log
        (self.activity_set, self.ti, self.to) = Alpha._build_tl_ti_to_set(self, self.log)
        self.dr = self._create_dependency_relation(self.log) 
        self.dm = self._create_dependency_measure(self.dr, self.activity_set) 
        self.ds  = self._create_dependency_set(self.dr, self.dm, thrshld_df, thrshld_dm)
        self.cn = self._create_causal_net(self.activity_set, self.ds, self.dr, self.dm)


    def _create_dependency_relation(self, log): 
        #find the number of frequencies
        frequ = {} # dict instead of set because we need to pair the tuples (keys) with their frequencies
            # directly follows relation: x>y
            # similar to alpha's df function with additional frequencies count
        for trace in log:
            for i in range(0, len(trace)-1):
                if (trace[i], trace[i+1]) not in frequ:
                    frequ[(trace[i+1], trace[i])] = 0
                    frequ[(trace[i], trace[i+1])] = 0
                frequ[(trace[i], trace[i+1])] += 1
        return frequ


        
    def _create_dependency_measure(self, dr, activity_set): 
        dm = {}
        # a follows b - b follows a / a follows b + b follows a + 1 if a not eqal b 
        # a follows a / a follows a + 1 if a equals a 
        for a in activity_set:
            for b in activity_set:
                if a != b and (a,b) in dr and (b,a) in dr:
                    dm[(a, b)] = round((dr[(a, b)] - dr[(b, a)]) / (dr[(a, b)] + dr[(b,a)]+1), 2)
                if a == b and (a,b) in dr and (b,a) in dr:
                    dm[(a, b)] = round(dr[(a, b)] / (dr[(a,b)] +1), 2)
        return dm
        
    
    def _create_dependency_set(self, dr, dm, thrshld_df, thrshld_dm):
        # only return the df tuples that meet the dependency measure and dependency frequency thresholds
        ds = {}
        for element in dr:
            if dr[element] >= thrshld_df and dm[element] >= thrshld_dm:
                ds[element] = dr[element]
        return ds

    
    def _create_causal_net(self, tl, ds, dr, dm):
        causal_net = graphviz.Digraph("causal net")
        causal_net.node_attr['shape'] = 'box'
        causal_net.node_attr['style'] = 'rounded'
        for elem in self.ti:
            causal_net.node(str(elem))
            causal_net.edge('a_i',str(elem))
        for elem in self.to:
            causal_net.node(str(elem))
            causal_net.edge(str(elem), 'a_o')
        for elem in tl:
            causal_net.node(str(elem))
        for elem in ds:
                causal_net.edge(str(elem[0]),str(elem[1]), ' ['+str(dr[elem])+'], ('+str(dm[elem])+ ')')
        
        causal_net.view(tempfile.mktemp('.gv.svg'))

      
    





