CREATE OR REPLACE FUNCTION update_play_count()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO played_songs (consumer_user__id, song_ismn, times_played)
    VALUES (NEW.consumer_user__id, NEW.song_ismn, 1)
    ON CONFLICT (consumer_user__id, song_ismn) DO UPDATE
    SET times_played = played_songs.times_played + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_played_songs
AFTER INSERT ON song_history
FOR EACH ROW
EXECUTE PROCEDURE update_play_count();

-----------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_consumer_premium()
RETURNS TRIGGER AS $$
DECLARE
    user_id INT;
BEGIN
    -- Guarda o id do user na variável user_id
    SELECT consumer_user__id INTO user_id
    FROM consumer_premium
    WHERE premium_id = NEW.id;

    -- Apaga a entrada em consumer_premium
    DELETE FROM consumer_premium
    WHERE premium_id = NEW.id
    AND active = TRUE;

    -- Verifica se existe uma entrada em consumer_premium com consumer_user__id = user_id
    -- e muda o valor de active para 'False' se existir
    IF EXISTS (
        SELECT 1
        FROM consumer_premium
        WHERE consumer_user__id = user_id
    ) THEN
        UPDATE consumer_premium
        SET active = FALSE
        WHERE premium_id = (
            SELECT MIN(premium_id)
            FROM consumer_premium
            WHERE consumer_user__id = user_id
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_update_premium
AFTER UPDATE ON premium
FOR EACH ROW
EXECUTE FUNCTION update_consumer_premium();
;
-----------------------------------------------------------------------------------------