import unittest
from environment.fogg_behavioural_model import Patient


class PatientEnvironmentTest(unittest.TestCase):

    def test_patient_behaviour(self):

        test_patient = Patient(10, True)

        # test trigger
        self.assertFalse(test_patient.fogg_behaviour(5, 4, False))
        self.assertTrue(test_patient.fogg_behaviour(5, 4, True))

        # test threshold
        self.assertFalse(test_patient.fogg_behaviour(5, 2, True))
        self.assertTrue(test_patient.fogg_behaviour(4, 3, True))

    def test_patient_motivation(self):
        test_patient = Patient(4, True)
        self.assertIsNotNone(test_patient.number_of_hours_slept_last_night)
        self.assertIsNotNone(test_patient.sufficient_sleep)
        self.assertIsNotNone(test_patient.last_activity_score)
        self.assertIsNotNone(test_patient.valence)
        self.assertLessEqual(test_patient.get_motivation(), 4)
        test_patient2 = Patient(4, False)
        self.assertLessEqual(test_patient2.get_motivation(), 3)

    def test_patient_ability(self):
        test_patient = Patient(2, False)
        self.assertIsNotNone(test_patient.location)
        self.assertIsNotNone(test_patient.activity)
        self.assertIsNotNone(test_patient.cognitive_load)
        self.assertIsNotNone(test_patient.arousal)
        self.assertLessEqual(test_patient.get_ability(), 4)

    def test_trigger(self):
        test_patient = Patient(2, False)
        self.assertIsNotNone(test_patient.day_of_the_week)
        self.assertIsNotNone(test_patient.time_of_the_day)
        self.assertIsNotNone(test_patient.get_trigger())

        test_patient2 = Patient(2, False)
        test_patient2.day_of_the_week =6
        test_patient2.activity = 'stationary'
        test_patient2.time_of_the_day = 11
        self.assertTrue(test_patient2.get_trigger())

        test_patient2 = Patient(2, False)
        test_patient2.day_of_the_week = 6
        test_patient2.activity = 'sleeping'
        self.assertFalse(test_patient2.get_trigger())






if __name__ == '__main__':
    unittest.main()
