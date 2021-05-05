import sqlite3
import numpy
import colorio

INIT = '''
create table if not exists __color (
    red unsigned int1 not null,
    green unsigned int1 not null,
    blue unsigned int1 not null,
    lightness unsigned int2 not null,
    greenred signed int2 not null,
    blueyellow signed int2 not null,
    primary key(red asc, green asc, blue asc)
) without rowid;
'''
VIEW = '''
create view if not exists color as
select red, green, blue, lightness, greenred, blueyellow, printf('#%02X%02X%02X', red, green, blue) as "hexcode" from __color;
'''
INDEX = '''
create index rgb on __color(red, green, blue);
create index light on __color(lightness);
'''
def get_conn():
    conn = sqlite3.connect('/home/ted/Sync/code/python/hyooze/oklab.db')
    conn.execute(INIT)
    conn.execute(VIEW)
    # conn.execute(INDEX)
    conn.commit()
    return conn

def insert_many(conn, rows):
    conn.executemany('''insert into __color (red, green, blue, lightness, greenred, blueyellow) values (?,?,?,?,?,?)''', rows)
    conn.commit()


if __name__ == '__main__':
    conn = get_conn()

    rgbs = numpy.array([(r, g, b) for r in range(256) for g in range(256) for b in range(256)]).T
    oklabs = colorio.cs.OKLAB().from_rgb255(rgbs)

    extremes = numpy.max([
                    oklabs.max(axis=1), 
                    abs(oklabs.min(axis=1))],
                axis=0)
    # lightness is non-negative. we want to scale that to an unsigned int2, and the others to a signed int2
    scalings = numpy.array([2**16-1, 2**15-1, 2**15-1]) / extremes

    scaled_oklabs = (scalings.reshape(3,1) * oklabs).round(0).astype(int)

    inserts = numpy.concatenate([rgbs, scaled_oklabs])
    for chunk_idx in range(256):
        chunk_start = chunk_idx * 256 * 256
        chunk_end = (chunk_idx + 1) * 256 * 256
        chunk = inserts[:,chunk_start:chunk_end]
        print(chunk_idx)
        insert_many(conn, chunk.T.tolist())
