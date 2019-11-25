import unittest
import requests
import time

query = {'key': '0054cc3a9a904df58ad9b696adfecb3a'}
API_URL = 'http://127.0.0.1:5000/api'


class TestAPI(unittest.TestCase):
    # def test_create_event(self):
    #     res = requests.post(
    #         f'{API_URL}/create-event')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.post(
    #         f'{API_URL}/create-event', headers=query)
    #     self.assertEqual(400, res.status_code)

    #     res = requests.post(
    #         f'{API_URL}/create-event', headers=query,
    #         json={})
    #     self.assertEqual(400, res.status_code)

    #     res = requests.post(
    #         f'{API_URL}/create-event', headers=query,
    #         json={'room_name': "505"})
    #     self.assertEqual(400, res.status_code)

    #     res = requests.post(
    #         f'{API_URL}/create-event', headers=query,
    #         json={'start_time': "2019-08-21T15:00"})
    #     self.assertEqual(400, res.status_code)

        # res = requests.post(
        #     f'{API_URL}/create-event', headers=query,
        #     json={'room_name': "505", 'start_time': "2019-08-21 15:00"})
        # self.assertEqual(400, res.status_code)

        # res = requests.post(
        #     f'{API_URL}/create-event', headers=query,
        #     json={'room_name': "228", 'start_time': "2019-08-21T15:00"})
        # self.assertEqual(404, res.status_code)

        # res = requests.post(
        #     f'{API_URL}/create-event', headers=query,
        #     json={'room_name': "505", 'start_time': "2019-11-20T15:00"})
        # self.assertEqual(201, res.status_code)

        # res = requests.post(
        #     f'{API_URL}/create-event', headers=query,
        #     json={'room_name': "505", 'start_time': "2019-11-20T15:00",
        #           'end_time': "2019-11-20T15:30", 'summary': "test"})
        # self.assertEqual(201, res.status_code)

    # def test_create_room(self):

    #     res = requests.post(f'{API_URL}/rooms/test')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.post(f'{API_URL}/rooms/test',
    #                         headers=query)
    #     self.assertEqual(201, res.status_code)

    #     res = requests.post(f'{API_URL}/rooms/test',
    #                         headers=query)
    #     self.assertEqual(409, res.status_code)

    # def test_get_rooms(self):
    #     res = requests.get(f'{API_URL}/rooms/')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.get(f'{API_URL}/rooms/',
    #                        headers=query)
    #     self.assertEqual(200, res.status_code)

    # def test_get_room(self):
    #     res = requests.get(f'{API_URL}/rooms/test')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.get(f'{API_URL}/rooms/test',
    #                        headers=query)
    #     self.assertEqual(200, res.status_code)

    # def test_delete_room(self):
    #     time.sleep(60)

    #     res = requests.delete(f'{API_URL}/rooms/test')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.delete(f'{API_URL}/rooms/228',
    #                           headers=query)
    #     self.assertEqual(404, res.status_code)

    #     res = requests.delete(f'{API_URL}/rooms/test',
    #                           headers=query)
    #     self.assertEqual(200, res.status_code)

    def test_edit_room(self):
        pass

    # def test_start_rec(self):
    #     res = requests.post(f'{API_URL}/start-record/505')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.post(f'{API_URL}/start-record/',
    #                         headers=query)
    #     self.assertEqual(404, res.status_code)

    #     res = requests.post(f'{API_URL}/start-record/test',
    #                         headers=query)
    #     self.assertEqual(404, res.status_code)

    #     res = requests.post(f'{API_URL}/start-record/505',
    #                         headers=query)
    #     self.assertEqual(200, res.status_code)

    #     res = requests.post(f'{API_URL}/start-record/505',
    #                         headers=query)
    #     self.assertEqual(409, res.status_code)

    # def test_stop_rec(self):

    #     res = requests.post(f'{API_URL}/stop-record/505')
    #     self.assertEqual(401, res.status_code)

    #     res = requests.post(f'{API_URL}/stop-record',
    #                         headers=query)
    #     self.assertEqual(404, res.status_code)

    #     res = requests.post(f'{API_URL}/stop-record/test',
    #                         headers=query)
    #     self.assertEqual(404, res.status_code)

    #     res = requests.post(f'{API_URL}/stop-record/505',
    #                         headers=query)
    #     self.assertEqual(200, res.status_code)

    #     time.sleep(5)

    #     res = requests.post(f'{API_URL}/stop-record/505',
    #                         headers=query)
    #     self.assertEqual(409, res.status_code)

    def test_sound_change(self):
        res = requests.post(f'{API_URL}/sound-change')
        self.assertEqual(401, res.status_code)

    def test_tracking_manage(self):
        pass

    def test_upload_to_drive(self):
        pass


if __name__ == "__main__":
    unittest.main()
