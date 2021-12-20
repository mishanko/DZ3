from app import application
import unittest

class TestAPI(unittest.TestCase):
    """Класс для тестирования методов API
    """
    def setUp(self) -> None:
        self.client = application.test_client(self)

    def test_delete(self):
        resp = self.client.delete('/api/ml_models/1/delete', headers={"Content-Type": "application/json"}, json={"num":"0"})
        self.assertEqual(resp.status_code, 204)

        resp = self.client.delete('/api/ml_models/2/delete', headers={"Content-Type": "application/json"}, json={"num":"1"})
        self.assertEqual(resp.status_code, 204)

    def test_retrain(self):
        resp = self.client.put('/api/ml_models/1/retrain', headers={"Content-Type": "application/json"}, json={"X": [[1,2,3],[3,2,1]], "y":[0,1], "num":"0"})
        self.assertIn(b'"trained":true', resp.data)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.put('/api/ml_models/2/retrain', headers={"Content-Type": "application/json"}, json={"X": [[1,2,3],[3,2,1]], "y":[0,1], "num":"1"})
        self.assertIn(b'"trained":true', resp.data)
        self.assertEqual(resp.status_code, 200)

    def test_predict(self):
        resp = self.client.post('/api/ml_models/1/predict', headers={"Content-Type": "application/json"}, json={"X": [1,2,3], "num":"0"})
        self.assertIn(b'"Prediction"', resp.data)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/api/ml_models/2/predict', headers={"Content-Type": "application/json"}, json={"X": [1,2,3], "num":"1"})
        self.assertIn(b'"Prediction"', resp.data)
        self.assertEqual(resp.status_code, 200)

    def test_train(self):    
        resp = self.client.put('/api/ml_models/1/train', headers={"Content-Type": "application/json"}, json={"X": [[1,2,3],[3,2,1]], "y":[0,1]})
        self.assertIn(b'"trained":true', resp.data)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.put('/api/ml_models/2/train', headers={"Content-Type": "application/json"}, json={"X": [[1,2,3],[3,2,1]], "y":[0,1]})
        self.assertIn(b'"trained":true', resp.data)
        self.assertEqual(resp.status_code, 200)

    def test_get(self):
        resp = self.client.get('/api/ml_models')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/ml_models/1')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/ml_models/2')
        self.assertEqual(resp.status_code, 200)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAPI('test_get'))
    suite.addTest(TestAPI('test_train'))
    suite.addTest(TestAPI('test_predict'))
    suite.addTest(TestAPI('test_retrain'))
    suite.addTest(TestAPI('test_delete'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())