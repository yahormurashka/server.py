""" Tests for player's rating.
"""

from server.db.map import DbMap
from tests.lib.base_test import BaseTest


class TestRatings(BaseTest):

    MAP_NAME = 'map02'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        DbMap().generate_maps(map_names=[cls.MAP_NAME, ], active_map=cls.MAP_NAME)

    @classmethod
    def tearDownClass(cls):
        DbMap().reset_db()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.player = self.login()

    def tearDown(self):
        self.logout()
        super().tearDown()

    def test_rating_on_start(self):
        ratings = self.get_ratings()
        self.assertIn(self.player['idx'], ratings)
        self.assertEqual(ratings[self.player['idx']]['idx'], self.player['idx'])
        self.assertEqual(ratings[self.player['idx']]['rating'], 0)
        self.assertEqual(ratings[self.player['idx']]['name'], self.player['name'])

    def test_rating_after_tick(self):
        self.turn()
        ratings = self.get_ratings()
        town = self.get_post(self.player['town']['idx'])
        exp_rating = town['population'] * 1000 + town['product'] + town['armor']
        self.assertIn(self.player['idx'], ratings)
        self.assertEqual(ratings[self.player['idx']]['idx'], self.player['idx'])
        self.assertEqual(ratings[self.player['idx']]['rating'], exp_rating)
        self.assertEqual(ratings[self.player['idx']]['name'], self.player['name'])

    def test_rating_after_upgrade(self):
        test_line_idx = 18
        town = self.player['town']
        train = self.player['trains'][0]

        self.move_train_until_stop(test_line_idx, train['idx'], -1)
        self.move_train_until_stop(test_line_idx, train['idx'], 1)
        armor = self.get_post(town['idx'])['armor']
        self.assertEqual(armor, town['armor'] + train['goods_capacity'])

        # Check that player have enough armor to upgrade train:
        armor_to_pay = train['next_level_price']
        self.assertGreaterEqual(armor, armor_to_pay)

        # Check rating before upgrade:
        ratings = self.get_ratings()
        town = self.get_post(self.player['town']['idx'])
        exp_rating = town['population'] * 1000 + town['product'] + town['armor']
        self.assertIn(self.player['idx'], ratings)
        self.assertEqual(ratings[self.player['idx']]['idx'], self.player['idx'])
        self.assertEqual(ratings[self.player['idx']]['rating'], exp_rating)
        self.assertEqual(ratings[self.player['idx']]['name'], self.player['name'])

        # Upgrade of the train:
        self.upgrade(trains=(train['idx'],))
        self.turn()

        # Check rating after upgrade:
        ratings = self.get_ratings()
        town = self.get_post(self.player['town']['idx'])
        exp_rating = town['population'] * 1000 + town['product'] + town['armor'] + train['next_level_price'] * 2
        self.assertIn(self.player['idx'], ratings)
        self.assertEqual(ratings[self.player['idx']]['idx'], self.player['idx'])
        self.assertEqual(ratings[self.player['idx']]['rating'], exp_rating)
        self.assertEqual(ratings[self.player['idx']]['name'], self.player['name'])
