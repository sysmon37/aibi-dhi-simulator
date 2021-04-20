import unittest
from environment.fogg_behavioural_model import Patient


class PatientEnvironmentTest(unittest.TestCase):

    def test_patient_behaviour(self):

        test_patient = Patient(10)

        # test trigger
        self.assertFalse(test_patient.fogg_behaviour(5, 4, False))
        self.assertTrue(test_patient.fogg_behaviour(5, 4, True))

        # test threshold
        self.assertFalse(test_patient.fogg_behaviour(5, 2, True))
        self.assertTrue(test_patient.fogg_behaviour(4, 3, True))






if __name__ == '__main__':
    unittest.main()
