import api
import unittest


class GirlsAcademyClubs(unittest.TestCase):
    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_ga_clubs(self):
        """Test to make certain the girls academy clubs returns a non-empty list."""
        result = self.app.get('/api/ga/clubs')
        self.assertGreater(len(result.json), 0)

class ECNLClubs(unittest.TestCase):
    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_ecnl_clubs(self):
        """Test to make certain the ecnl clubs returns a non-empty list."""
        result = self.app.get('/api/ecnl/clubs')
        self.assertGreater(len(result.json), 0)

class NWSLPlayers(unittest.TestCase):
    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_nwsl_players(self):
        """Test to make certain the nwsl players returns a non-empty list."""
        result = self.app.get('/api/nwsl/players')
        self.assertGreater(len(result.json), 0)

class NWSLStandings(unittest.TestCase):
    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_nwsl_standings(self):
        """Test to make certain the nwsl standings returns a non-empty list."""
        result = self.app.get('/api/nwsl/standings')
        self.assertGreater(len(result.json), 0)
