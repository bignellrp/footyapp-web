"""
Unit tests for the player stats calculation logic in services/get_player_data.py.

Points system under test:
  Win  – 3 points for each of the 5 players on the winning team.
  Draw – 1 point for each of the 10 players who participated.
  Loss – 0 points.
"""
import unittest
import sys
import os

## Make sure the project root is on the path when running tests directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.get_player_data import _compute_player_stats


class TestComputePlayerStats(unittest.TestCase):
    '''Tests for the _compute_player_stats helper function.'''

    ## ------------------------------------------------------------------
    ## Helpers
    ## ------------------------------------------------------------------

    def _make_game(self, team_a, team_b, score_a, score_b):
        return {
            'teamA': team_a,
            'teamB': team_b,
            'scoreTeamA': score_a,
            'scoreTeamB': score_b,
        }

    ## ------------------------------------------------------------------
    ## Win scenarios
    ## ------------------------------------------------------------------

    def test_all_5_team_a_players_get_3_points_on_win(self):
        '''All 5 players on the winning team receive 3 points each.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a=3, score_b=1)

        stats = _compute_player_stats([game])

        for player in team_a:
            self.assertEqual(stats[player]['wins'], 1,
                             f'{player} should have 1 win')
            self.assertEqual(stats[player]['draws'], 0)
            self.assertEqual(stats[player]['losses'], 0)

    def test_all_5_team_b_players_get_3_points_on_win(self):
        '''All 5 players on team B receive 3 points when team B wins.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a=1, score_b=4)

        stats = _compute_player_stats([game])

        for player in team_b:
            self.assertEqual(stats[player]['wins'], 1)

    def test_losing_team_players_get_0_points(self):
        '''Players on the losing team receive 0 points.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a=5, score_b=2)

        stats = _compute_player_stats([game])

        for player in team_b:
            self.assertEqual(stats[player]['wins'], 0)
            self.assertEqual(stats[player]['draws'], 0)
            self.assertEqual(stats[player]['losses'], 1,
                             f'{player} should have 1 loss')

    ## ------------------------------------------------------------------
    ## Draw scenario
    ## ------------------------------------------------------------------

    def test_all_10_players_get_1_point_on_draw(self):
        '''All 10 participants get 1 point each in a draw.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a=2, score_b=2)

        stats = _compute_player_stats([game])

        for player in team_a + team_b:
            self.assertEqual(stats[player]['draws'], 1,
                             f'{player} should have 1 draw')
            self.assertEqual(stats[player]['wins'], 0)
            self.assertEqual(stats[player]['losses'], 0)

    ## ------------------------------------------------------------------
    ## Score / points arithmetic
    ## ------------------------------------------------------------------

    def test_win_contributes_3_to_score(self):
        '''score = wins * 3 + draws * 1 is correctly applied.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        games = [
            self._make_game(team_a, team_b, 3, 1),  # team_a wins
            self._make_game(team_a, team_b, 2, 2),  # draw
        ]

        stats = _compute_player_stats(games)

        ## Alice: 1 win + 1 draw → score = 3 + 1 = 4
        alice = stats['Alice']
        self.assertEqual(alice['wins'], 1)
        self.assertEqual(alice['draws'], 1)
        self.assertEqual(alice['losses'], 0)
        expected_score = alice['wins'] * 3 + alice['draws']
        self.assertEqual(expected_score, 4)

    ## ------------------------------------------------------------------
    ## Games without scores should be skipped
    ## ------------------------------------------------------------------

    def test_game_without_score_is_skipped(self):
        '''Games where scores are None (not yet recorded) must be ignored.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a=None, score_b=None)

        stats = _compute_player_stats([game])

        self.assertEqual(stats, {})

    def test_game_with_only_one_score_none_is_skipped(self):
        '''A game with only one score present should also be skipped.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a=3, score_b=None)

        stats = _compute_player_stats([game])

        self.assertEqual(stats, {})

    ## ------------------------------------------------------------------
    ## Empty / edge cases
    ## ------------------------------------------------------------------

    def test_no_games_returns_empty_dict(self):
        '''No games produce an empty stats dict.'''
        stats = _compute_player_stats([])
        self.assertEqual(stats, {})

    def test_multiple_games_accumulate_correctly(self):
        '''Stats accumulate correctly across several games.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        games = [
            self._make_game(team_a, team_b, 3, 1),  # team_a wins
            self._make_game(team_a, team_b, 1, 3),  # team_b wins
            self._make_game(team_a, team_b, 2, 2),  # draw
        ]

        stats = _compute_player_stats(games)

        ## Alice: 1 win, 1 draw, 1 loss
        self.assertEqual(stats['Alice']['wins'], 1)
        self.assertEqual(stats['Alice']['draws'], 1)
        self.assertEqual(stats['Alice']['losses'], 1)

        ## Frank: 1 win, 1 draw, 1 loss
        self.assertEqual(stats['Frank']['wins'], 1)
        self.assertEqual(stats['Frank']['draws'], 1)
        self.assertEqual(stats['Frank']['losses'], 1)

    def test_score_strings_are_handled(self):
        '''Scores stored as strings (e.g. from API) are converted properly.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a='3', score_b='1')

        stats = _compute_player_stats([game])

        self.assertEqual(stats['Alice']['wins'], 1)
        self.assertEqual(stats['Frank']['losses'], 1)

    def test_invalid_score_game_is_skipped(self):
        '''A game with non-numeric scores is silently skipped.'''
        team_a = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
        team_b = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
        game = self._make_game(team_a, team_b, score_a='abc', score_b='xyz')

        stats = _compute_player_stats([game])

        self.assertEqual(stats, {})


if __name__ == '__main__':
    unittest.main()
