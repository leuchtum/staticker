from staticker.database import Database, Handler
from staticker.collection import PlayerCollection
from staticker.statistic import PlayerStat
from staticker.player import Player
from staticker.game import Game
import random
from datetime import datetime

if __name__ == "__main__":
    play_games = 50
    generate_players = 10

    cases = list(range(play_games+2)) # NEW SET
    #cases.append(-1000)
    #cases = [-1] # INSPECT
    #cases = [1] # DELETE

    for case in cases:
        t1 = datetime.now().timestamp()

        if case == 1:
            db = Database()
            db.delete()
            del db

        elif case == 2:
            for _ in range(generate_players):
                h = Handler()
                p = Player()
                p.set_name(h.random_name())
                p.dump()

        elif case == 3:
            db = Database()
            all_players_store = db.player.all()

        if case >= 3:
            all_players = all_players_store.copy()
            random.shuffle(all_players)
            store = random.choice([2,3,4])
            store = all_players[:store]
            players = []
            for player in store:
                p = Player()
                p.load(player["id"])
                players.append(p)

            game = Game()

            if len(players) == 2:
                game.black.set_player([players[0]])
                game.white.set_player([players[1]])
            if len(players) == 3:
                side = random.choice(["B","W"])
                if side == "B":
                    game.black.set_player([players[0]])
                    game.white.set_player([players[1], players[2]])
                elif side == "W":
                    game.white.set_player([players[0]])
                    game.black.set_player([players[1], players[2]])
            if len(players) == 4:
                game.black.set_player([players[0], players[1]])
                game.white.set_player([players[2], players[3]])

            game.set_playto(6)
            winner = random.choices([game.black, game.white], k=4)

            while True:
                side = random.choice(winner)
                owner = random.choice([False, False, False, False, False, True])
                if side._mode == "single":
                    if owner:
                        side.single.add_owner()
                    else:
                        side.single.add_goal()
                elif side._mode == "multi":
                    pos = random.choice(["OFF","OFF","DEF"])
                    if pos == "OFF":
                        if owner:
                            side.offense.add_owner()
                        else:
                            side.offense.add_goal()
                    elif pos == "DEF":
                        if owner:
                            side.defense.add_owner()
                        else:
                            side.defense.add_goal()
                if game.is_finished():
                    break

            game.time.stop()
            game.dump()


            #game_stat_p1 = game.get_position_result(players[0].id)
            #game_stat_p2 = game.get_position_result(players[1].id)
            #players[0].add_game_stat(game_stat_p1)
            #players[1].add_game_stat(game_stat_p2)     
            players[0].add_game(game.id)   
            players[0].dump()
            players[1].add_game(game.id)   
            players[1].dump()  

            if len(players) >= 3:
                #game_stat_p3 = game.get_position_result(players[2].id)
                #players[2].add_game_stat(game_stat_p3)
                players[2].add_game(game.id)   
                players[2].dump()

            if len(players) > 3:
                #game_stat_p4 = game.get_position_result(players[3].id)            
                #players[3].add_game_stat(game_stat_p4)
                players[3].add_game(game.id)            
                players[3].dump()

        if case == -1:
            pc = PlayerCollection()
            pc.load_all()
            pc.sort()

            db = Database()
            p_id = db.player.all()[4]["id"]
            p = Player()
            p.load(p_id)
            pstat = PlayerStat(p, glob=True)
            print("")

        elif case == -1000:
            stats = players[0].get_stats()
            names = game.get_names()
            print("finish")

        t2 = datetime.now().timestamp()
        print(f"{case} {round(t2-t1, 4)}")