from abc import ABC

from gym import Env
import numpy as np


# habituation to prompts (after appox 3 weeks)
# one episode is one day


class Patient(Env):

    def __init__(self, behaviour_threshold: int, has_family: bool):
        self.behaviour_threshold = behaviour_threshold
        self.has_family = has_family
        self.reset()

    def reset(self):
        self.number_of_hours_slept_last_night = np.random.randint(3, 10)
        self.sufficient_sleep = 1 if self.number_of_hours_slept_last_night > 7 else 0
        self.valence = np.random.randint(0, 2)  # 0 negative, 1 positive
        self.last_activity_score = np.random.randint(0, 2)  # 0 negative, 1 positive
        self.arousal = np.random.randint(0, 2)  # 0 low, 1 high
        self.cognitive_load = np.random.randint(0, 2)  # 0 low, 1 high
        self.time_of_the_day = np.random.randint(0, 25)
        self.day_of_the_week = np.random.randint(0, 8)  # 0 Monday, 7 Sunday
        self.location = 'home' if 1 < self.time_of_the_day < 7 else np.random.choice(['home', 'other'])
        self.activity = 'sleeping' if 1 < self.time_of_the_day < 5 else \
            np.random.choice(['stationary', 'walking', 'driving', 'sleeping'])

    def step(self, action):
        pass

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

        """
        return self.valence + self.has_family + self.last_activity_score + self.sufficient_sleep

    def get_ability(self):
        """"
        1)Chan et al (2020) "Prompto: Investigating Receptivity to Prompts Based on Cognitive Load from Memory Training
         Conversational Agent"
         "users were more receptive to prompts and memory training under low cognitive load than under high cognitive load"
        - cognitive load, high (-), low(+)

        2) Goyal et al. (2017) users are likely to pay attention to the notifications at times of increasing arousal
        - arousal, high (+), low (-)

        3) Aminikhanghahi (2017) "Improving Smartphone Prompt Timing Through Activity Awareness"
            "participants did not like to respond to AL queries when they were at work but were generally responsive
             when they were relaxing " relaxing low cognitive load and positive valence
             Ho et al. (2018). Location = [Home, Work, Other] , Motion activity = [Stationary, Walking, Running, Driving]
         - home (+), other (-)
         - stationary(+), walking(-), driving (-), sleeping (-)

        """
        load = 1 if self.cognitive_load == 0 else 0
        location = 1 if self.location == 'home' else 0
        activity = 1 if self.activity == 'stationary' else 0

        return self.arousal + load + location + activity

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

        """
        effective_prompt = True if 15 > self.time_of_the_day >= 11 or (self.day_of_the_week > 5 and
                                                                       self.activity != 'sleeping') else False

        return effective_prompt


def update_patient_stress_level():
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
    pass


def update_patient_cognitive_load():
    """"

    Okoshi et al (2015)  "Attelia: Reducing User’s Cognitive Load due to Interruptive Notifications on Smart Phones"
    Okoshi et al (2017) "Attention and Engagement-Awareness in the Wild: A Large-Scale Study with Adaptive Notifications"
    "notifications at detected breakpoint timing resulted in 46% lower cognitive load compared to randomly-timed
     notifications"
    """

    pass


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
