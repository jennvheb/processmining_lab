from alpha_miner import Alpha


class Heuristic():
    def __init__(self, log, parameters):
        self.log = log
        self.activity_set = Alpha._build_tl_set(self.log)
        self.fm = self._create_frequency_df_relations(self.log, self.activity_set)
        self.dm = self._create_dependency_measure(self.fm, self.activity_set)
        self.cn = self._create_causal_net(self.dm, self.fm, self.activity_set, self.log, parameters)

        # NOT FINISHED
        # had some heavy bugs so i am restarting, still need to do sth about causal

    def _create_frequency_df_relations(self, log, activity_set):
        ctr = {}
        for activitiy in activity_set:
            ctr[activitiy] = 0
        for trace in log:
            for index, value in enumerate(trace): 
                # because we are accessing +1 so we have to check for -1 so its 0
                if index != len(trace-1):
                    ctr[value][trace[index]] += 1 #need to check‚
        return ctr

    def _create_dependency_measure(self, fm, activity_set): #activity_set.a?!
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

    #def _create_causal_net(self, dm, ai, ao, input_b, output_b, threshold_fm, threshold_dm):

      
    









        