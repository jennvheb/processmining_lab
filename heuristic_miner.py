from alpha_miner import Alpha
import graphviz


class Heuristic():

    def __init__(self, log, thrshld_df, thrshld_dm, myuuid):
        self.log = log
        self.outputname = str(myuuid)
        (self.activity_set, self.ti, self.to) = Alpha._build_tl_ti_to_set(self, self.log)
        self.dr = self._create_dependency_relation(self.log) 
        self.dm = self._create_dependency_measure(self.dr, self.activity_set) 
        self.ds  = self._create_dependency_set(self.dr, self.dm, thrshld_df, thrshld_dm)
        self.cn = self._create_causal_net(self.activity_set, self.ds, self.dr, self.dm, self.outputname)


    def _create_dependency_relation(self, log): 
        #find the frequencies of the directly follows relation
        frequ = {} # dict instead of set because we need to pair the tuples (keys) with their frequencies
        for trace in log:
            for i in range(0, len(trace)-1):
                if (trace[i], trace[i+1]) not in frequ:
                    frequ[(trace[i+1], trace[i])] = 0
                    frequ[(trace[i], trace[i+1])] = 0
                frequ[(trace[i], trace[i+1])] += 1
        return frequ


        
    def _create_dependency_measure(self, dr, activity_set): 
        # find the relative value of the dependency relation between a and b
        dm = {}
        # a follows b - b follows a / a follows b + b follows a + 1 if a not equal b 
        # a follows a / a follows a + 1 if a equals a 
        for a in activity_set:
            for b in activity_set:
                if a != b and (a,b) in dr and (b,a) in dr:
                    dm[(a, b)] = round((dr[(a, b)] - dr[(b, a)]) / (dr[(a, b)] + dr[(b,a)]+1), 3)
                if a == b and (a,b) in dr and (b,a) in dr:
                    dm[(a, b)] = round(dr[(a, b)] / (dr[(a,b)] +1), 3)
        return dm
        
    
    def _create_dependency_set(self, dr, dm, thrshld_df, thrshld_dm):
        # only return the dependency relation tuples that meet the dependency measure and frequency thresholds
        ds = {}
        for element in dr:
            if dr[element] >= float(thrshld_df) and dm[element] >= float(thrshld_dm):
                ds[element] = dr[element]
        return ds

    
    def _create_causal_net(self, tl, ds, dr, dm, outputname):
        causal_net = graphviz.Digraph(name=outputname, node_attr= {'fontsize':'16', 'fontname': 'Arial'})
        causal_net.node_attr['shape'] = 'box'
        causal_net.node_attr['style'] = 'rounded'

        # create the start activities and connect them to ai
        for elem in self.ti:
            causal_net.node(str(elem))
            causal_net.edge('a_i',str(elem))
        # create the end activities and connect them to ao
        for elem in self.to:
            causal_net.node(str(elem))
            causal_net.edge(str(elem), 'a_o')
        # create the rest of the activities
        for elem in tl:
            causal_net.node(str(elem))
        # generates the edges along with the frequency and dependency measure values for each activity pair
        for elem in ds:
                causal_net.edge(str(elem[0]),str(elem[1]), ' ['+str(dr[elem])+'], ('+str(dm[elem])+ ')')
        
        causal_net.render(directory='static', format='svg')
      
   





