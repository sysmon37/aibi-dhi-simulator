from gym import Env
import numpy as np
from collections import deque
import random
from numpy import sin
from gym import error, spaces, utils


# habituation to prompts (after appox 3 weeks)
# one episode is one day


class Patient(Env):

    def __init__(self):
        self.behaviour_threshold = None
        self.has_family = None
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Discrete(13)

        # self.week_days = deque(np.arange(1, 8), maxlen=7)
        # self.hours = deque(np.arange(0, 24), maxlen=24)
        # self.reset()
        # time_of_the_day = 4  # morning, midday, evening, night
        # day_of_the_week = 2  # week day, weekend
        # activity_score = 2  # low/ high
        # location = 2  # home/ other
        # sleeping = 2  # yes/no
        # valence = 2  # positive/negative
        # arousal = 3  # low, mid, high
        # motion = 2  # stationary, walking
        # cognitive_load = 2  # low/ high
        # num time activity performed in last 24 hours, 0 less than 1, 1 if 1 , 2 or more

    def env_init(self, env_info=None):

        if env_info is None:
            env_info = {}
        self.behaviour_threshold = env_info["behaviour_threshold"]
        self.has_family = env_info["has_family"]
        self.max_notification_tolarated = 5
        self.week_days = deque(np.arange(1, 8), maxlen=7)
        self.hours = deque(np.arange(0, 24), maxlen=24)
        self.reset()

    def env_start(self):
        """The first method called when the experiment starts, called before the
        agent starts.

        Returns:
            The first state observation from the environment.
        """
        self.reset()
        return self._get_current_state()


    def reset(self):
        self.activity_suggested = [0]
        self.activity_performed = [0]
        self._start_time_randomiser()
        self.time_of_the_day = self.hours[0]
        self.day_of_the_week = self.week_days[0]  # 1 Monday, 7 Sunday
        self.motion_activity_list = random.choices(['stationary', 'walking'],
                                                   weights=(0.8, 0.2), k=24)  # in last 24 hours
        self.awake_list = random.choices(['sleeping', 'awake'], weights=(0.2, 0.8), k=24)
        self.last_activity_score = np.random.randint(0, 2)  # 0 negative, 1 positive
        self.location = 'home' if 1 < self.time_of_the_day < 7 else np.random.choice(['home', 'other'])
        self._update_emotional_state()
        self.env_steps = 0
        return self._get_current_state()

    def step(self, action: tuple):

        # action, task_length = action
        motiovation = self.get_motivation()
        ability = self.get_ability()
        trigger = self.get_trigger()
        if action == 1:
            self.activity_suggested.append(1)
            behaviour = self.fogg_behaviour(motiovation, ability, trigger)
            if behaviour:
                self.activity_performed.append(1 )
                self.last_activity_score = 1 if self.valence == 1 else 0
                reward = 20
            else:
                self.activity_performed.append(0)
                if sum(self.activity_suggested[-24:]) < 5:
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

        return reward, self._get_current_state(), info

    def _get_current_state(self):
        location = 1 if self.location == 'home' else 0
        sleeping = 1 if self.awake_list[-1] == 'sleeping' else 0
        d = dict([(y, x) for x, y in enumerate(sorted({'stationary', 'walking'}))])
        week_day = self._get_week_day()
        day_time = self._get_time_day()
        n= self._activity_in_last_day()
        t = self._time_since_last_activity()
        number_of_hours_slept = self.awake_list[-24:].count('sleeping')
        overnotified = 1 if sum(self.activity_suggested[-24:])> 5 else 0
        return np.array([day_time, week_day, self.last_activity_score,
                         location, sleeping, self.valence, self.arousal, d[self.motion_activity_list[-1]],
                         self.cognitive_load, n,t, number_of_hours_slept, overnotified])

    def _activity_in_last_day(self):
        n = sum(self.activity_performed[-24:])
        if n == 0:
            return 0
        else:
            if n <= 2:
                return 1
            else:
                return 2

    def _time_since_last_activity(self):
        n = sum(self.activity_performed[-24:])
        if n == 0:
            return 1# more than 24 hours
        else:
            return 0

    def fogg_behaviour(self, motivation: int, ability: int, trigger: bool) -> bool:
        """"
        Function that decides if the behaviour will be performed or not based on Fogg's Behavioural Model
        """
        behaviour = motivation * ability * trigger
        return behaviour > self.behaviour_threshold

    def get_motivation(self):
        """
        Factors impacting patient's motivation:
        1) Jowsey et al (2014) "What motivates Australian health service users with chronic illness to engage in
        self-management behaviour?"

         - internal factors:  valence positive(+), negative (-)
            "Remaining positive was one of the most important strategies many used for optimizing and
             controlling their health"
         - external factors: family (+), no family (-)
         - demotivators: high past activity score (+),  low (-)
            "perceiving self-management behaviour as having limited benefit"

        2) Dolsen et al (2017) "Sleep the night before and after a treatment session: A critical ingredient for
        treatment adherence?"
        Axelsson et al (2020) "Sleepiness as motivation: a potential mechanism for how sleep deprivation affects behavior"

        "sleepiness may be a central mechanism by which impaired alertness, for example, due to insufficient sleep,
        contributes to poor quality of life and adverse health. We propose that sleepiness helps organize behaviors
         toward the specific goal of assuring sufficient sleep, in competition with other needs and incentives" Axelsson

         - hours of sleep the previous night, sufficient(+), insufficient(-)

         agency and motivation (MHealth)

        """
        number_of_hours_slept = self.awake_list[-24:].count('sleeping')
        sufficient_sleep = 1 if number_of_hours_slept > 7 else 0
        return self.valence + self.has_family + self.last_activity_score + sufficient_sleep

    def get_ability(self):
        """"
        1)Chan et al (2020) "Prompto: Investigating Receptivity to Prompts Based on Cognitive Load from Memory Training
         Conversational Agent"
         "users were more receptive to prompts and memory training under low cognitive load than under high cognitive load"
        - cognitive load, high (-), low(+)


        2)self-efficacy/ confidence = positive responses rate  person who would fail in the past might be less confident
        "Bandura (1997, p. 2) has defined perceived self-efficacy as ‘the belief in one’s capabilities
        to organize and execute the courses of action required to produce given attainments.’
        Numerous studies have investigated domain-specific self-efficacy that predicts corresponding intentions,
         health behaviours, and health behaviour change (Burkert, Knoll,
        Scholz, Roigas, & Gralla, 2012; Luszczynska & Schwarzer, 2005).
        Bandura, A. (1997). Self-efficacy: The exercise of control. New York: Freeman.
        Luszczynska, A., & Schwarzer, R. (2005). Social cognitive theory. In M. Connor & P. Norman (Eds.),
        Predicting health behaviour (pp. 127–169). London: Open University Press
        "

        Other:
        task_difficulty,
        length
        sequence mining SPADE
        """

        n= self._activity_in_last_day() # 0  if the activity was already performed twice
        if n == 2:
            tired_of_repeating_the_activity = -1
        elif n == 1:
            tired_of_repeating_the_activity = 0
        else:
            tired_of_repeating_the_activity = 1

        ready = self._time_since_last_activity()
        load = 1 if self.cognitive_load == 0 else 0
        confidence = sum(self.activity_performed) / sum(self.activity_suggested) if sum(self.activity_suggested) > 0 \
            else 0

        return confidence + load + tired_of_repeating_the_activity + ready

    def get_trigger(self):
        """"
        1)Bidargadi et al. (2018) "To Prompt or Not to Prompt? A Microrandomized Trial of Time-Varying Push Notifications to
         Increase Proximal Engagement With a Mobile Health App"
        Timing!: "users are more likely to engage with the app within 24 hours when push notifications are sent at mid-day
         on weekends"
         - time of the day
         - day of the week

        2) Akker etal (2015) "Tailored motivational message generation: A model and practical framework for real-time
         physical activity coaching"

                                     #Trigger
        3) Goyal et al. (2017) users are likely to pay attention to the notifications at times of increasing arousal
        - arousal, high (+), low (-) Notice a Trigger? --> in a future shall model as a continuum and only in mid
         arousal effective

        4) Aminikhanghahi (2017) "Improving Smartphone Prompt Timing Through Activity Awareness"
            "participants did not like to respond to AL queries when they were at work but were generally responsive
             when they were relaxing " relaxing low cognitive load and positive valence

             Ho et al. (2018). Location = [Home, Work, Other] , Motion activity = [Stationary, Walking, Running, Driving]
         - home (+), other (-)
         - stationary(+), walking(-), driving (-)
         - awake (+) sleeping (-)

        """

        prompt = 1 if self.awake_list[-1] != 'sleeping' else 0  # do not prompt when patient sleep
        good_time = 1 if self._get_time_day() == 1 else 0
        good_day = 1 if self._get_week_day() == 1 else 0
        good_location = 1 if self.location == 'home' else 0
        good_motion = 1 if self.motion_activity_list[-1] == 'stationary' else 0
        good_arousal = 1 if self.arousal == 1 else 0

        return (good_arousal + good_day + good_time + good_location + good_motion) * prompt

    def update_state(self):
        self._update_time()
        self._update_awake()
        if self.awake_list[-1] == 'awake':
            self._update_motion_activity()
            self._update_location()
            self._update_emotional_state()
        else:
            self.location = 'home'
            self.motion_activity_list.append('stationary')
            self.arousal = 0
            self.cognitive_load = 0

    def _update_day(self):

        self.week_days.rotate(-1)
        self.day_of_the_week = self.week_days[0]

    def _get_week_day(self):
        if self.day_of_the_week < 6:
            return 0  # week day
        else:
            return 1  # weekend

    def _get_time_day(self):
        if 10 > self.time_of_the_day >= 6:
            return 0  # morning
        elif 16 > self.time_of_the_day >= 11:
            return 1  # midday
        elif 22 > self.time_of_the_day >= 16:
            return 2  # evening
        else:
            return 3  # night

    def _update_time(self):

        self.hours.rotate(-1)
        self.time_of_the_day = self.hours[0]
        if self.time_of_the_day == 0:
            self._update_day()

    def _start_time_randomiser(self):
        for i in range(np.random.randint(0, len(self.week_days))):
            self.week_days.rotate(-1)
        for i in range(np.random.randint(0, len(self.hours))):
            self.hours.rotate(-1)

    def _update_emotional_state(self):
        # random
        self._update_patient_stress_level() # updates arousal and valence
        self.cognitive_load = np.random.randint(0, 2)  # 0 low, 1 high

    def _update_motion_activity(self):

        if self.activity_performed[-1] == 1:
            weights = (0, 1)
        else:
            w = self.motion_activity_list.count('walking') / len(self.motion_activity_list)
            st = self.motion_activity_list.count('stationary') / len(self.motion_activity_list)
            weights = (st, w)
        self.motion_activity_list.append(random.choices(['stationary', 'walking'], weights=weights, k=1)[0])

    def _update_awake(self):

        if sum(self.activity_performed[-24:]) > 0:
            #healthy sleeping
            p = [0.2, 0.1, 0.1, 0.1, 0.3, 0.4, 0.6, 0.7, 0.8, 0.85, 0.95, 0.99, 0.99, 0.95, 0.9, 0.95, 0.8, 0.8, 0.8,
                 0.8, 0.7, 0.7, 0.45, 0.3]
        else:
            p = [0.4, 0.3, 0.3, 0.3, 0.3, 0.4, 0.6, 0.7, 0.8, 0.85, 0.95, 0.9, 0.9, 0.95, 0.9, 0.95, 0.8, 0.8, 0.8,
                 0.75, 0.7, 0.7, 0.4, 0.3]

        awake_prb = p[self.time_of_the_day]
        now_awake = random.choices(['sleeping', 'awake'], weights=(1 - awake_prb, awake_prb), k=1)
        self.awake_list.append(now_awake[0])

    def _update_location(self):
        if self.motion_activity_list[-1] == 'walking':
            self.location = 'other'
        else:
            self.location = random.choices(['home', 'other'], weights=(0.8, 0.2), k=1)[0]

    def _update_patient_stress_level(self):
        """"
        Stress = high arousal and negative valence Markova et al (2019) "arousal-valence emotion space"
        in contrast to
        Flow = high/mid arousal and positive valence//

        Peifer et al (2014) "The relation of flow-experience and physiological arousal under stress — Can u shape it?"
        "Physiological arousal during flow-experience between stress and relaxation"

        1) Yoon et al (2014) "Understanding notification stress of smartphone messenger app"
         - number of notification high (stress +), low (stress -)

        2) Zhai et al (2020) "Associations among physical activity and smartphone use with perceived stress and sleep
        quality of Chinese college students"
         - insufficient exercise (stress +), exercise in past day (stress -)
        """

        insufficient_exercise = 1 if self.activity_performed[-24:].count('walking') < 1 else 0
        annoyed = 1 if sum(self.activity_suggested[-24:]) > 4 else 0
        neg_factors = insufficient_exercise + annoyed
        if neg_factors == 2:
            self.valence = random.choices([0, 1], weights=(0.9, 0.1), k=1)[0]
        elif neg_factors == 1:
            self.valence = random.choices([0, 1], weights=(0.5, 0.5), k=1)[0]
        else:
            self.valence = 1

        if neg_factors == 2:
            self.arousal = 2
        else:
            self.arousal = np.random.randint(0, 2)  # 0 low, 1 high

    def update_patient_cognitive_load(self):
        """"

        Okoshi et al (2015)  "Attelia: Reducing User’s Cognitive Load due to Interruptive Notifications on Smart Phones"
        Okoshi et al (2017) "Attention and Engagement-Awareness in the Wild: A Large-Scale Study with Adaptive Notifications"
        "notifications at detected breakpoint timing resulted in 46% lower cognitive load compared to randomly-timed
         notifications"
        """
        self.cognitive_load = 1 if sum(self.activity_performed[-24:])/ sum(self.activity_suggested[-24:]) < 0.5 else 0



def update_patient_arousal():
    """"
    Kusserow et al (2013) "Modeling arousal phases in daily living using wearable sensors"
    "participant-specific arousal was frequently estimated during conversations and
    yielded highest intensities during office work"


    """
    pass


def update_patient_valence():
    """"
    Baglioni  et al (2010) "Sleep and emotions: A focus on insomnia"
    "interaction between sleep and emotional valence, poor sleep quality seems to
    correlate with high negative and low positive emotions, both in clinical and subclinical samples"

    - sufficient sleep (+), insufficient seep(-)

    Niedermeier et al (2021) "Acute Effects of a Single Bout of Walking on Affective
    Responses in Patients with Major Depressive Disorder"
    "positively valenced immediate response of light- to moderate-intensity walking may serve as an acute
    emotion regulation"

    Ivarsson et al (2021) "Associations between physical activity and core affects within and across days:
     a daily diary study"
     " physical activity seem to have a positive within-day association with pleasant
    core affects and a negative within-day association with unpleasant-deactivated core
    affects. There were, however, no statistically significant relations between core affects
    and physical activity across days"

    - recently walking (+),

    """
    pass


def update_patients_activity():
    """"
    Williams et al (2012) "Does Affective Valence During and Immediately Following a 10-Min Walk Predict Concurrent
     and Future Physical Activity?"
     "During-behavior affect is predictive of concurrent and future physical activity behavior"

    """
    pass


def update_patients_sleep_duration():
    """"

    Fairholme & Manber (2015) "Sleep, emotions, and emotion regulation: an overview"
    "negative valence and high arousal potentially have unique effects on sleep architecture,
    with high arousal being associated with reductions in slow-wave sleep and negative valence being associated
    with disruptions to REM sleep"
    - negative valence (-)
    - high arousal (-)

    Bisson et al (2019) "Walk to a better night of sleep: testing the relationship between physical activity and sleep"
    " on days that participants were
    more active than average, they reported better sleep quality and duration in both sexes. Results suggest
    that low-impact PA is positively related to sleep, more so in women than men"

    - walking (+)
    """
    pass

#
