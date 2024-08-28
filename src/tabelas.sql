CREATE TABLE consumer (
	user__id BIGINT,
	PRIMARY KEY(user__id)
);

CREATE TABLE label (
	id_			 BIGSERIAL,
	name			 VARCHAR(512) NOT NULL,
	address		 VARCHAR(512),
	phone			 NUMERIC(9,0),
	administrator_user__id BIGINT NOT NULL,
	PRIMARY KEY(id_)
);

CREATE TABLE song (
	ismn	 BIGSERIAL,
	title	 VARCHAR(512) NOT NULL,
	duration	 FLOAT(8) NOT NULL,
	release_date DATE,
	genre	 VARCHAR(512),
	PRIMARY KEY(ismn)
);

CREATE TABLE artist (
	artistic_name		 VARCHAR(512) NOT NULL,
	bio			 TEXT NOT NULL,
	administrator_user__id BIGINT NOT NULL,
	label_id_		 BIGINT NOT NULL,
	user__id		 BIGINT,
	PRIMARY KEY(user__id)
);

CREATE TABLE album (
	id		 BIGSERIAL,
	title	 VARCHAR(512) NOT NULL,
	release_date DATE,
	PRIMARY KEY(id)
);

CREATE TABLE playlist (
	id		 BIGSERIAL,
	title		 VARCHAR(512) NOT NULL,
	is_public	 BOOL NOT NULL,
	consumer_user__id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE comment (
	id		 BIGSERIAL,
	comment_details	 TEXT NOT NULL,
	parent_comment_id BIGINT,
	consumer_user__id BIGINT NOT NULL,
	song_ismn	 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE administrator (
	user__id BIGINT,
	PRIMARY KEY(user__id)
);

CREATE TABLE card (
	limit_date		 DATE NOT NULL,
	money			 INTEGER NOT NULL,
	card_name		 VARCHAR(512) NOT NULL,
	id			 BIGSERIAL,
	consumer_user__id	 BIGINT NOT NULL,
	administrator_user__id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE premium (
	id	 BIGSERIAL,
	begin_date DATE NOT NULL,
	end_date	 DATE NOT NULL,
	plan_type	 VARCHAR(512) NOT NULL,
	expired	 BOOL NOT NULL DEFAULT False,
	PRIMARY KEY(id)
);

CREATE TABLE user_ (
	id	 BIGSERIAL,
	name	 VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	type	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE transaction_ (
	id		 BIGSERIAL NOT NULL,
	data		 DATE NOT NULL,
	valor		 BIGINT NOT NULL,
	consumer_user__id BIGINT NOT NULL,
	premium_id	 BIGINT,
	PRIMARY KEY(premium_id)
);

CREATE TABLE album_songs (
	album_id	 BIGINT,
	song_ismn BIGINT,
	PRIMARY KEY(album_id,song_ismn)
);

CREATE TABLE consumer_premium (
	active		 BOOL NOT NULL,
	consumer_user__id BIGINT NOT NULL,
	premium_id	 BIGINT,
	PRIMARY KEY(premium_id)
);

CREATE TABLE played_songs (
	times_played	 BIGINT NOT NULL,
	song_ismn	 BIGINT NOT NULL,
	consumer_user__id BIGINT NOT NULL
);

CREATE TABLE song_history (
	play_date	 DATE NOT NULL,
	song_ismn	 BIGINT NOT NULL,
	consumer_user__id BIGINT NOT NULL
);

CREATE TABLE card_transaction (
	card_id		 BIGINT,
	transaction__premium_id BIGINT,
	PRIMARY KEY(card_id,transaction__premium_id)
);

CREATE TABLE playlist_songs (
	playlist_id BIGINT,
	song_ismn	 BIGINT,
	PRIMARY KEY(playlist_id,song_ismn)
);

CREATE TABLE comment_comment (
	comment_id	 BIGINT,
	comment_id1 BIGINT NOT NULL,
	PRIMARY KEY(comment_id)
);

CREATE TABLE album_song (
	album_id	 BIGINT NOT NULL,
	song_ismn BIGINT,
	PRIMARY KEY(song_ismn)
);

CREATE TABLE artist_album (
	artist_user__id BIGINT,
	album_id	 BIGINT,
	PRIMARY KEY(artist_user__id,album_id)
);

CREATE TABLE artist_song (
	artist_user__id BIGINT,
	song_ismn	 BIGINT,
	PRIMARY KEY(artist_user__id,song_ismn)
);

ALTER TABLE consumer ADD CONSTRAINT consumer_fk1 FOREIGN KEY (user__id) REFERENCES user_(id);
ALTER TABLE label ADD CONSTRAINT label_fk1 FOREIGN KEY (administrator_user__id) REFERENCES administrator(user__id);
ALTER TABLE artist ADD CONSTRAINT artist_fk1 FOREIGN KEY (administrator_user__id) REFERENCES administrator(user__id);
ALTER TABLE artist ADD CONSTRAINT artist_fk2 FOREIGN KEY (label_id_) REFERENCES label(id_);
ALTER TABLE artist ADD CONSTRAINT artist_fk3 FOREIGN KEY (user__id) REFERENCES user_(id);
ALTER TABLE playlist ADD CONSTRAINT playlist_fk1 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE comment ADD CONSTRAINT comment_fk1 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE comment ADD CONSTRAINT comment_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE administrator ADD CONSTRAINT administrator_fk1 FOREIGN KEY (user__id) REFERENCES user_(id);
ALTER TABLE card ADD CONSTRAINT card_fk1 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE card ADD CONSTRAINT card_fk2 FOREIGN KEY (administrator_user__id) REFERENCES administrator(user__id);
ALTER TABLE transaction_ ADD CONSTRAINT transaction__fk1 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE transaction_ ADD CONSTRAINT transaction__fk2 FOREIGN KEY (premium_id) REFERENCES premium(id);
ALTER TABLE album_songs ADD CONSTRAINT album_songs_fk1 FOREIGN KEY (album_id) REFERENCES album(id);
ALTER TABLE album_songs ADD CONSTRAINT album_songs_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE consumer_premium ADD CONSTRAINT consumer_premium_fk1 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE consumer_premium ADD CONSTRAINT consumer_premium_fk2 FOREIGN KEY (premium_id) REFERENCES premium(id);
ALTER TABLE played_songs ADD CONSTRAINT played_songs_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE played_songs ADD CONSTRAINT played_songs_fk2 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE song_history ADD CONSTRAINT song_history_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE song_history ADD CONSTRAINT song_history_fk2 FOREIGN KEY (consumer_user__id) REFERENCES consumer(user__id);
ALTER TABLE card_transaction ADD CONSTRAINT card_transaction_fk1 FOREIGN KEY (card_id) REFERENCES card(id);
ALTER TABLE playlist_songs ADD CONSTRAINT playlist_songs_fk1 FOREIGN KEY (playlist_id) REFERENCES playlist(id);
ALTER TABLE playlist_songs ADD CONSTRAINT playlist_songs_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE comment_comment ADD CONSTRAINT comment_comment_fk1 FOREIGN KEY (comment_id) REFERENCES comment(id);
ALTER TABLE comment_comment ADD CONSTRAINT comment_comment_fk2 FOREIGN KEY (comment_id1) REFERENCES comment(id);
ALTER TABLE album_song ADD CONSTRAINT album_song_fk1 FOREIGN KEY (album_id) REFERENCES album(id);
ALTER TABLE album_song ADD CONSTRAINT album_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE artist_album ADD CONSTRAINT artist_album_fk1 FOREIGN KEY (artist_user__id) REFERENCES artist(user__id);
ALTER TABLE artist_album ADD CONSTRAINT artist_album_fk2 FOREIGN KEY (album_id) REFERENCES album(id);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk1 FOREIGN KEY (artist_user__id) REFERENCES artist(user__id);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);

