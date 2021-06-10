from environment.fogg_behavioural_model import Patient

class PretrainingPatient(Patient):

    def step(self, action: tuple):

        # action, task_length = action
        motiovation = self.get_motivation()
        ability = self.get_ability()
        trigger = self.get_trigger()
        day_time = self._get_time_day()
        if action == 1:
            if day_time == 1:
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
        info = dict()
        info['motivation'] = motiovation
        info['ability'] = ability
        info['trigger'] = trigger
        info['action'] = action
        info['reward'] = reward

        self.update_state()
        self.env_steps += self.env_steps
        return self._get_current_state(), reward, False, info









