from datetime import datetime, timedelta
import jwt
from flask import Flask, jsonify, request, render_template, abort
import logging
import psycopg2
import hashlib
from uuid import uuid4

SECRET_KEY = "YOUR_SECRET_KEY"

users_logged_in=[]


# Flask App and Status Codes
app = Flask(__name__)

StatusCode = {
    'success': 200,
    'request_error': 400,
    'api_error': 500
}

def verify_password(password, password_verify):
    if password == password_verify:
        return 1
    else:
        return 0

def decode():
    result = request.headers.get('Authorization')
    if not result:
        return {'error': f'Missing access token'}
    token = result.split('Bearer ')[1]
    try:
        return jwt.decode(token,SECRET_KEY,algorithms='HS256')

    except Exception as e:
        return {'error': f'Invalid access token: {e}'}


# Database Connection
def conectar():
    db = psycopg2.connect(
        user='postgres',
        password='password',
        host='127.0.0.1',
        port='5432',
        database='Projeto'
    )
    return db


# Routes
@app.route('/')
def landing_page():
    return "Projeto de Base de Dados 2023<br> " \
           "Criado por:<br>" \
           "Francisco Querido  nº2021221158 <br>" \
           "Joao Paiva nº2021216669<br>" \
           "Salome Costa nº2021218601"


@app.route("/user", methods=['POST'])
def register():
    logger.info('POST /user')

    con = conectar()
    cursor = con.cursor()
    payload = request.get_json()
    logger.debug(f'POST /user - payload: {payload}')
    required_fields = ['name', 'email', 'password', 'type']
    missing_fields = [field for field in required_fields if field not in payload]

    if missing_fields:
        response = {'status': StatusCode['request_error'], 'errors': f'{", ".join(missing_fields)} value(s) not in payload'}
        return jsonify(response)

    if payload['type'] not in ['administrator', 'consumer', 'artist']:
        response = {'status': StatusCode['request_error'], 'errors': 'Invalid user type'}
        return jsonify(response)

    # hash = hash_password(payload['password'])

    try:
        cursor.execute('INSERT INTO User_ (name, email, password, type) VALUES (%s,%s,%s, %s) RETURNING id;',
                       (payload['name'], payload['email'], payload['password'], payload['type']))

        user_id = cursor.fetchone()
        print(user_id)
        if payload['type'] == 'artist':
            cursor.execute('INSERT INTO artist (artistic_name, bio, administrator_user__id, label_id_, user__id) '
                           'VALUES (%s, %s, %s, %s, %s);',
                           (payload['artistic_name'], payload['bio'], request.headers["Id"],
                            payload['label_id'], user_id))

        elif payload['type'] == 'consumer':
            cursor.execute('INSERT INTO consumer (balance, user__id) VALUES (%s, %s);', (0, user_id))

        # admin
        elif payload['type'] == 'administrator':
            cursor.execute('INSERT INTO administrator (user__id) VALUES (%s);', (user_id,))

        con.commit()
        response = {'status': StatusCode['success'], 'results': user_id}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

#N DA#################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@app.route("/login", methods=['PUT'])
def login():
    logger.info('PUT /login')
    con = conectar()
    cursor = con.cursor()
    payload = request.get_json()
    email = payload['email']
    password = payload['password']

    logger.debug(f'PUT /login - payload: {payload}')

    try:
        cursor.execute('SELECT id, password, type FROM user_ WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and verify_password(user[1], password) == 1:
            token = jwt.encode({'user_id': user[0], 'type': user[2]}, SECRET_KEY, algorithm='HS256')

            if user[2] == "consumer":
                today_date = datetime.today().date()
                cursor.execute("""
                                UPDATE premium SET expired = true 
                                WHERE end_date < %s 
                                AND id = (SELECT premium_id FROM consumer_premium WHERE consumer_user__id = %s AND active = true)
                                RETURNING end_date
                                """
                                ,(today_date, user[0]))
                
            users_logged_in.append(user[0])

            response = {'status': StatusCode['success'], 'token': token}


        else:
            response = {'status': StatusCode['request_error'], 'errors': 'Invalid credentials'}
        
        con.commit()

    except psycopg2.DatabaseError as error:
        logger.error(f'POST /login - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        con.rollback()

    finally:
        if con:
            con.close()
    
    

    return jsonify(response)

############################################################
@app.route("/song", methods=['POST'])
def add_song():
    logger.info('POST /song')
    con = conectar()
    cursor = con.cursor()
    payload = request.get_json()

    logger.debug(f'POST /song - payload: {payload}')

    required_fields = ['title', 'duration', 'release_date', 'genre']
    for field in required_fields:
        if field not in payload:
            response = {'status': StatusCode['request_error'], 'errors': f'{field} value not in payload'}
            return jsonify(response)

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Artist not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'artist':
        response = {'status': StatusCode['request_error'], 'errors': 'User not Artist'}
        return jsonify(response)

    try:
        cursor.execute("INSERT INTO song (title, duration, release_date, genre) "
                       "VALUES (%s, %s, %s, %s) RETURNING ismn;",
                       (payload['title'], payload['duration'], payload['release_date'], payload['genre']))

        ismn = cursor.fetchone()[0]

        cursor.execute('INSERT INTO artist_song (artist_user__id, song_ismn) VALUES (%s, %s);',
                       (result['user_id'], ismn))

        con.commit()
        response = {'status': StatusCode['success'], 'results': ismn}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /song - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}
        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

############################################################

@app.route("/album", methods=['POST'])
def add_album():
    logger.info('POST /album')

    con = conectar()
    cursor = con.cursor()
    payload = request.get_json()

    logger.debug(f'POST /album - payload: {payload}')

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Artist not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'artist':
        response = {'status': StatusCode['request_error'], 'errors': 'User not Artist'}
        return jsonify(response)

    required_fields = ['title', 'release_date', 'songs']

    for field in required_fields:
        if field not in payload:
            response = {'status': StatusCode['request_error'], 'errors': f'{field} value not in payload'}
            return jsonify(response)

    try:
        artist_user__id = result ['user_id']

        cursor.execute('INSERT INTO album (title, release_date) VALUES (%s, %s) RETURNING id;',
                        (payload['title'], payload['release_date']))
        
        album_id = cursor.fetchone()[0]

        cursor.execute('INSERT INTO artist_album (artist_user__id, album_id) VALUES (%s, %s);',
                       (artist_user__id, album_id,))

        for song in payload['songs']:
            if isinstance(song, str):

                cursor.execute('SELECT * FROM song WHERE ismn = %s;', (song,))
                result = cursor.fetchone()

                if result:
                    #Add an existing song to the album
                    cursor.execute('INSERT INTO album_songs (album_id, song_ismn) VALUES (%s, %s);', (album_id, song))
                    cursor.execute('UPDATE song SET album_id = %s WHERE ismn = %s;', (album_id, song))
                else:
                    # O valor não existe na tabela
                    response = {'status': StatusCode['request_error'], 'errors': f'Song {song} does not exist'}
                    return jsonify(response)


            elif isinstance(song, dict):
                # Add a new song to the album
                required_fields = ['title', 'duration', 'release_date', 'genre']
                for field in required_fields:
                    if field not in song:
                        response = {'status': StatusCode['request_error'], 'errors': f'{field} value not in payload'}
                        return jsonify(response)

                cursor.execute('INSERT INTO song (title, duration, release_date, genre, album_id) '
                            'VALUES (%s, %s, %s, %s, %s) RETURNING ismn;',
                            (song['title'], song['duration'], song['release_date'], song['genre'], album_id))

                song_ismn = cursor.fetchone()[0]

                cursor.execute('INSERT INTO artist_song (artist_user__id, song_ismn) VALUES (%s, %s);',
                            (artist_user__id, song_ismn))
                
                cursor.execute('INSERT INTO album_songs (album_id, song_ismn) VALUES (%s, %s);', (album_id, song_ismn))
                

            else:
                response = {'status': StatusCode['request_error'], 'errors': 'Invalid song format'}
                return jsonify(response)

        con.commit()
        response = {'status': StatusCode['success'], 'results': album_id}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /album - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)


@app.route("/song/<keyword>", methods=['GET'])
def search_song(keyword):
    con = conectar()
    cursor = con.cursor()
    logger.info('GET /song/<keyword>')

    logger.debug(f'keyword: {keyword}')

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'User not authenticated'}
        return jsonify(response)

    try:
        cursor.execute("""
            SELECT 
                song.title,
                ARRAY_AGG(DISTINCT artist.artistic_name) AS artists,
                ARRAY_AGG(DISTINCT album.id) AS albums
            FROM 
                song
            LEFT JOIN 
                artist_song ON song.ismn = artist_song.song_ismn
            LEFT JOIN 
                artist ON artist_song.artist_user__id = artist.user__id
            LEFT JOIN 
                album_songs ON song.ismn = album_songs.song_ismn
            LEFT JOIN 
                album ON album_songs.album_id = album.id
            WHERE 
                song.title ILIKE %s
            GROUP BY 
                song.ismn;
        """, (f'%{keyword}%',))

        rows = cursor.fetchall()

        results = [{'title': title, 'artists': artists, 'albums': albums} for title, artists, albums in rows]
        response = {'status': StatusCode['success'], 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /song/<keyword> - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

########################################################################

@app.route("/artist_info/<artist_user__id>", methods=['GET'])
def detail_artist(artist_user__id):
    logger.info('GET /artist_info/<artist_user__id>')
    logger.debug(f'artist_user__id: {artist_user__id}')

    con = conectar()
    cursor = con.cursor()

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'User not authenticated'}
        return jsonify(response)

    try:
        cursor.execute("""
            SELECT
                artist.artistic_name AS name,
                ARRAY_AGG(DISTINCT song.ismn) AS songs,
                ARRAY_AGG(DISTINCT album.id) AS albums,
                ARRAY_AGG(DISTINCT playlist.id) AS playlists
            FROM
                artist
            LEFT JOIN
                artist_song ON artist.user__id = artist_song.artist_user__id
            LEFT JOIN
                song ON artist_song.song_ismn = song.ismn
            LEFT JOIN
                album_songs ON song.ismn = album_songs.song_ismn
            LEFT JOIN
                album ON album_songs.album_id = album.id
            LEFT JOIN
                song_playlist ON song.ismn = song_playlist.song_ismn
            LEFT JOIN
                playlist ON song_playlist.playlist_id = playlist.id
            WHERE
                artist.user__id = %s
            GROUP BY
                artist.user__id;
        """, (artist_user__id,))

        results = cursor.fetchall()
        result = results[0]

        logger.debug('GET /artist_info/<artist_user__id> - parse')
        logger.debug(result)

        if result:
            name, songs, albums, playlists = result
            response = {'status': StatusCode['success'], 'results': {'name': name, 'songs': songs, 'albums': albums, 'playlists': playlists}}
        else:
            response = {'status': StatusCode['request_error'], 'errors': 'Artist not found'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /artist_info/<artist_user__id> - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}
    finally:
        if con is not None:
            con.close()

    return jsonify(response)

##################################################

@app.route('/card', methods=['POST'])
def card():

    logger.info('POST /card')
    payload = request.get_json()

    con = conectar()
    cur = con.cursor()

    logger.debug(f'POST /card - payload: {payload}')
    args = ['number_cards', 'card_price']

    card_ids = []  # to store all the inserted card_ids

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Admin not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'administrator':
        response = {'status': StatusCode['request_error'], 'errors': 'User not administrator'}
        return jsonify(response)
    
    for entry in args:
        if entry not in payload:
            response = {'status': StatusCode['request_error'], 'results': f'{entry} value not in payload'}
            return jsonify(response)

    if payload['card_price'] == '10':
        card_name = '10€'
        expiration_date = 30
    elif payload['card_price'] == '25':
        card_name = '25€'
        expiration_date = 40
    elif payload['card_price'] == '50':
        card_name = '50€'
        expiration_date = 60

    limit_date = (datetime.today() + timedelta(days=expiration_date)).date()

    try:
        for i in range (int(payload['number_cards'])):
            cur.execute('INSERT INTO card (administrator_user__id, card_name,money,limit_date,consumer_user__id) VALUES (%s, %s, %s, %s,%s) RETURNING id',
                    (result['user_id'],card_name,payload['card_price'],limit_date,payload['consumer']))

            card_id = cur.fetchone()[0]
            card_ids.append(card_id)  # add the inserted card_id to the list

        con.commit()
        response = {'status': StatusCode['success'],
                    'results': 'Inserted cards id: {}'.format(card_id)}



    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /subscription - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        # an error occurred, rollback
        con.rollback()


    if con is not None:
        con.close()

    # create the response after the for loop, sending all the card_ids
    if card_ids:  # check if the list is not empty
        response = {'status': StatusCode['success'],
                        'results': 'Inserted cards ids: {}'.format (card_ids)}
    else:
        response = {'status': StatusCode['api_error'], 'errors': 'No cards were inserted'}

    return jsonify(response)

###############################################################


@app.route('/subscription', methods=['POST'])
def premium_subscribe():
    logger.info('POST /subscription')
    payload = request.get_json()

    con = conectar()
    cur = con.cursor()

    logger.debug(f'POST /subscription - payload: {payload}')
    args = ['period', 'cards']

    used_cards=[]

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Consumer not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'consumer':
        response = {'status': StatusCode['request_error'], 'errors': 'User not consumer'}
        return jsonify(response)
    
    for i in args:
        if i not in payload:
            response = {'status': StatusCode['request_error'], 'results': f'{i} value not in payload'}
            return jsonify(response)

    user_id = result['user_id']

    if payload['period'] == 'month':
        value = 7
        duration = 30
    elif payload['period'] == 'quarter':
        value = 21
        duration = 40
    elif payload['period'] == 'semester':
        value = 42
        duration = 60

    try:
        cur.execute('SELECT end_date FROM premium WHERE id=(SELECT MAX(premium_id) FROM consumer_premium WHERE consumer_user__id = %s)', 
                    (user_id,))
        result = cur.fetchone()[0]

        if result:
            begin_date = result
        else:
            begin_date = datetime.today()

        end_date = (begin_date + timedelta(days=duration))

        #It will register the subscription, but in this state its just a processing resgister, because if the cards in the payload doesnt have the sufficient ammount it will give and error and
        #rollback, therefore not Inserting the subscription in the table
        cur.execute('INSERT INTO premium (begin_date, end_date, plan_type, expired) VALUES (%s, %s, %s,false) RETURNING id', 
                    (begin_date, end_date, payload['period'],))

        subs_id = cur.fetchone()[0]
        if result:
            cur.execute('INSERT INTO consumer_premium (consumer_user__id,premium_id,active) VALUES (%s, %s,false)',
                        (user_id,subs_id))
        else:
            cur.execute('INSERT INTO consumer_premium (consumer_user__id,premium_id,active) VALUES (%s, %s,true)',
                        (user_id,subs_id))

        cards = [int(card_id) for card_id in payload['cards']]

        total = 0

        # Somar o saldo de todos os cartões
        for card in cards:
            cur.execute('SELECT money, consumer_user__id FROM card WHERE id = %s', (card,))
            
            result = cur.fetchone()
            
            if result:
                total += result[0]
                if result[1] != int(user_id):
                    raise Exception('Card {} does not belong to user {}'.format(card,user_id))
            
            else:
                raise Exception('Card {} not found'.format(card))


        if total < value:
            raise Exception('Saldo de {}€ não chega para pagar o valor da Subscrição: {}€'.format(total, value))

        current_money = 0

        for card in cards:
            used_cards.append(card)
        
            # Get the money from the card
            cur.execute('SELECT money FROM card WHERE id = %s',
                         (card,))

            current_money += cur.fetchone()[0]

            #Case where the money in the card is not enough to pay the subscription cost
            if value > current_money:
                #Update the money value in pre_paid_card table to 0 because all the money will be used
                cur.execute('UPDATE card SET money = 0 WHERE id = %s', (card,))

            elif value <= current_money:
                #update the money value in card table
                cur.execute("""
                            UPDATE card SET money = money - %s WHERE id = %s;
                            INSERT INTO transaction_ (data, valor,consumer_user__id, premium_id) 
                            VALUES (%s, %s,%s, %s) RETURNING id
                            """, 
                            (current_money-value,card,begin_date, value,user_id,subs_id,))

                transaction_id = cur.fetchone()[0]
                break
        
        for card in used_cards:
            cur.execute('INSERT INTO card_transaction (card_id, transaction__premium_id) VALUES (%s,%s)',
                        (card,transaction_id,))
            

        # commit the transaction
        con.commit()
        response = {'status': StatusCode['success'],
                        'results': 'Inserted premium subscription id: {}'.format(subs_id)}



    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /subscription - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        # an error occurred, rollback
        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

########################################################################################################

@app.route('/comments/<song_id>', methods=['POST'])
@app.route('/comments/<song_id>/<parent_comment_id>', methods=['POST'])
def comments(song_id, parent_comment_id = None):
    logger.info(f'POST /comments/{song_id}')
    payload = request.get_json()
    logger.debug(f'POST /comments/<song_id>/<parent_comment_id> - payload:  {payload}')
    args = ['comentario']

    con = conectar()
    cur = con.cursor()

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Consumer not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'consumer':
        response = {'status': StatusCode['request_error'], 'errors': 'User not consumer'}
        return jsonify(response)

    for entry in args:
        if entry not in payload:
            response = {'status': StatusCode['request_error'], 'results': f'{entry} value not in payload'}
            return jsonify(response)

    try:
        author_id = result['user_id']

        # Check if song exists
        cur.execute('SELECT song.ismn FROM song WHERE song.ismn = %s', (song_id,))
        results = cur.fetchone()

        if results is None:
            response = {'status': StatusCode['not_found'], 'results': 'Song not found'}
            return jsonify(response)


        # Check if parent comment exists
        if parent_comment_id:
            cur.execute('SELECT comment.id FROM comment WHERE comment.id = %s', (parent_comment_id,))
            results = cur.fetchone()

            if results is None:
                response = {'status': StatusCode['not_found'], 'results': 'Parent comment not found'}
                raise Exception(response)
            

        if parent_comment_id:
            cur.execute('INSERT INTO comment (parent_comment_id, consumer_user__id, comment_details, song_ismn) VALUES (%s, %s, %s, %s) RETURNING id',
                         (parent_comment_id, author_id, payload['comentario'], song_id))
            
        else:
            cur.execute('INSERT INTO comment (consumer_user__id, comment_details, song_ismn) VALUES (%s, %s, %s) RETURNING id',
                         (author_id, payload['comentario'], song_id))
            
        comment_id = cur.fetchone()[0]

        con.commit()
        response = {
            'status': StatusCode['success'],
            'results': 'Inserted comment id: {}'.format(comment_id)
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /comment - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        # an error occurred, rollback
        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)
#################################################################################################

@app.route("/play_song/<song_ismn>", methods=['PUT'])
def play_song(song_ismn):
    logger.info(f'PUT /comments/{song_ismn}')

    con = conectar()
    cursor = con.cursor()

    logger.debug(f'PUT /play_song/{song_ismn}')

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Consumer not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'consumer':
        response = {'status': StatusCode['request_error'], 'errors': 'User not consumer'}
        return jsonify(response)

    try:
        today = datetime.today().date()

        cursor.execute("""
            WITH genre_query AS (
                SELECT genre
                FROM song
                WHERE ismn = %s
            )
            INSERT INTO song_history (song_ismn, consumer_user__id, play_date, genre)
            SELECT %s, %s, %s, genre
            FROM genre_query;
        """, 
        (song_ismn, song_ismn, result['user_id'], today))

   
        con.commit()
        response = {'status': StatusCode['success'], 'errors': None}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCode['api_error'], 'errors': str(error)}
        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

###########################################################################


@app.route("/top_10", methods=['GET'])
def get_top_10_music():
    con = conectar()
    cursor = con.cursor()

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Consumer not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'consumer':
        response = {'status': StatusCode['request_error'], 'errors': 'User not consumer'}
        return jsonify(response)


    try:
        cursor.execute("""
                    SELECT song_ismn, times_played 
                    FROM played_songs 
                    WHERE consumer_user__id = %s 
                    ORDER BY times_played DESC 
                    LIMIT 10;
                """, (result['user_id'],))

        results = cursor.fetchall()
        if results:
            # Format the results into the desired response structure
            report = []
            for result in results:
                song_ismn, times_played = result
                report.append({
                    'song_ismn': song_ismn,
                    'times played': times_played,
                })

            # Prepare the response
            response = {
                'status': StatusCode['success'],
                'errors': None,
                'results': report
            }
        else:
            response = {
                'status': StatusCode['success'],
                'errors': None,
                'results': "No records found to show"
            }
            return jsonify(response)


    except (Exception, psycopg2.DatabaseError) as error:
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

################################################################~


@app.route("/report/<year_month>", methods=['GET'])
def monthly_report(year_month):
    logger.info('GET /report/<year_month>')

    logger.debug(f'year_month: {year_month}')

    con = conectar()
    cursor = con.cursor()

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Consumer not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'consumer':
        response = {'status': StatusCode['request_error'], 'errors': 'User not consumer'}
        return jsonify(response)

    try:
        # Extract the year and month from the URL parameter
        year, month = map(int, year_month.split('_'))

        # Calculate the start and end dates for the selected month
        date = datetime(year, month, 1)

        # Execute the SQL query to obtain the monthly report
        cursor.execute("""
                SELECT EXTRACT(MONTH FROM play_date) AS month, genre, COUNT(*) AS number_of_songs
                FROM song_history
                WHERE play_date >= %s - INTERVAL '12 months' AND play_date <= %s AND consumer_user__id = %s
                GROUP BY month, genre;
            """, (date, date, result['user_id']))


        # Fetch all the results
        results = cursor.fetchall()

        logger.debug('GET /report/<year_month> - parse')
        logger.debug(results)

        if results:
            # Format the results into the desired response structure
            report = []
            for result in results:
                month, genre, playbacks = result
                report.append({
                    'month': month,
                    'genre': genre,
                    'playbacks': playbacks
                })

            # Prepare the response
            response = {
                'status': StatusCode['success'],
                'errors': None,
                'results': report
            }
        else:
            response = {
                'status': StatusCode['success'],
                'errors': None,
                'results': "No records found in the requested time range"
            }
            return jsonify(response)

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /report/<year_month> - error: {error}')
        response = {
            'status': StatusCode['api_error'],
            'errors': str(error),
            'results': None
        }
    finally:
        if con is not None:
            con.close()

    return jsonify(response)

#########################################################################

@app.route("/playlist", methods=['POST'])
def create_playlist():
    logger.info('POST /playlist')
    con = conectar()
    cursor = con.cursor()

    payload = request.get_json()

    logger.debug(f'POST /playlist - payload: {payload}')
    args = ['playlist_name', 'visibility','songs']

    result = decode()
    if 'user_id' not in result:
        return jsonify(result)
    
    if result['user_id'] not in users_logged_in:
        response = {'status': StatusCode['request_error'], 'errors': 'Consumer not authenticated'}
        return jsonify(response)
    
    elif result['type'] != 'consumer':
        response = {'status': StatusCode['request_error'], 'errors': 'User not consumer'}
        return jsonify(response)
    

    for entry in args:
        if entry not in payload:
            response = {'status': StatusCode['request_error'], 'results': f'{entry} value not in payload'}
            return jsonify(response)
    
    cursor.execute("""
                    SELECT premium_id
                    FROM consumer_premium
                    WHERE consumer_user__id = %s;
                    """,
                    (result['user_id'],))
    
    if cursor.fetchone() is None:
        response = {'status': StatusCode['api_error'], 'results': 'Consumer is not premium '}
        return jsonify(response)
    
    try:
        consumer_user__id = result ['user_id']
        visibility = payload['visibility']

        if visibility == 'public':
            is_public = True
        elif visibility == 'private':
            is_public = False
        else:
            response = {'status': StatusCode['request_error'], 'errors': f'Visibility value {visibility} not valid'}
            return jsonify(response)

        cursor.execute('INSERT INTO playlist (title, is_public,consumer_user__id) VALUES (%s, %s,%s) RETURNING id;',
                        (payload['playlist_name'], is_public,consumer_user__id))
        
        playlist_id = cursor.fetchone()[0]

        for song in payload['songs']:
            cursor.execute('SELECT * FROM song WHERE ismn = %s;', (song,))
            result = cursor.fetchone()

            if result:
                # Add an existing song to the playlist
                cursor.execute('INSERT INTO playlist_songs (playlist_id, song_ismn) VALUES (%s, %s);', (playlist_id, song))
            else:
                # Song does not exist
                response = f'Song {song} does not exist'
                raise Exception(response)

        con.commit()
        response = {'status': StatusCode['success'], 'results': playlist_id}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /playlist - error: {error}')
        response = {'status': StatusCode['api_error'], 'errors': str(error)}

        con.rollback()

    finally:
        if con is not None:
            con.close()

    return jsonify(response)

#######################################################################
if __name__ == '__main__':
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')

