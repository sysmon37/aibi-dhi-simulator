from environment.fogg_behavioural_model import Patient


class PretrainingPatient(Patient):

    def step(self, action: tuple):
        # action, task_length = action
        motiovation = self.get_motivation()
        ability = self.get_ability()
        trigger = self.get_trigger()
        if self.steps < 15000:
            reward = self.pretraining_reward(action)
        else:
            reward = self.behaviour_based_reward(action, motiovation, ability, trigger)

        info = dict()
        info['motivation'] = motiovation
        info['ability'] = ability
        info['trigger'] = trigger
        info['action'] = action
        info['reward'] = reward

        self.update_state()
        self.steps += self.steps + 1
        return self._get_current_state(), reward, False, info

    def pretraining_reward(self, action):
        day_time = self._get_time_day()
        if action == 1:
            if day_time == 1:
                self.activity_performed.append(1)
                reward = 20
            else:
                self.activity_performed.append(0)
                if sum(self.activity_suggested[-24:]) < self.max_notification_tolarated:
                    reward = -1
                else:
                    reward = -5
        else:
            self.activity_suggested.append(0)
            self.activity_performed.append(0)
            reward = 0.0
        return reward

    def behaviour_based_reward(self, action,motiovation, ability, trigger):

        if action == 1:
            self.activity_suggested.append(1)
            behaviour = self.fogg_behaviour(motiovation, ability, trigger)
            if behaviour:
                self.activity_performed.append(1)
                self.last_activity_score = 1 if self.valence == 1 else 0
                reward = 20
            else:
                self.activity_performed.append(0)
                if sum(self.activity_suggested[-24:]) < self.max_notification_tolarated:
                    reward = -1
                else:
                    reward = -5
        else:
            self.activity_suggested.append(0)
            self.activity_performed.append(0)
            reward = 0.0
        return reward







