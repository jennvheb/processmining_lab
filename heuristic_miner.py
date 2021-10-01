from alpha_miner import Alpha


class Heuristic():
    def __init__(self, log, thrshld_df, thrshld_dm):
        self.log = log
        self.activity_set = Alpha._build_tl_set(self.log)
        self.df = self._create_dependency_relation(self.log, self.activity_set)
        self.dm = self._create_dependency_measure(self.fm, self.activity_set)
        self.dg = self._create_dependency_graph(self.df, self.dm, thrshld_df, thrshld_dm)
        self.cn = self._create_causal_net()


    def _create_dependency_relation(self, log, activity_set):
        #todo: still need to through it
        ctr = {}
        for activitiy in activity_set:
            ctr[activitiy] = 0
        for trace in log:
            for index, value in enumerate(trace): 
                # because we are accessing +1 so we have to check for -1 so its 0
                if index != len(trace-1):
                    ctr[value][trace[index]] += 1 #need to check‚
        return ctr

    def _create_dependency_measure(self, fm, activity_set): 
        #todo: still need to go through it
        dm = {}
        for activity in activity_set:
            dm[activity] = 0
        # a follows b - b follows a / a follows b + b follows a + 1 if a not eqal b 
        # a follows a / a follows a + 1 if a equals a 
        for a in activity_set:
            for b in activity_set:
                if a != b:
                    dm[a][b] = round((fm[a][b] - fm[b][a]) / (fm[a][b] + fm[b][a]+1), 2)
                if a == b:
                    dm[a][b] = round(fm[a][b] / (fm[a][b] +1), 2)
        return dm
    
    def _create_dependency_graph(self, df, dm, thrshld_df, thrshld_dm):
        dg = set()
        for tmp in zip(df, dm):
            if tmp >= thrshld_df and tmp >= thrshld_dm:
                dg.add(tmp)
    # todo:create nodes, create edges

        
    #todo:
    #def _create_causal_net(self, A, ai, ao, D, I, O):

      
    









        