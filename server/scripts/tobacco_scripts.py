from constants import DATABASE_NAME, TOBACCO_POTENCY
from database.database import DatabaseExecutor


def add_tobacco_to_database(request):
    list_of_duplicates = []
    with DatabaseExecutor(DATABASE_NAME) as database:
        for key in request:
            for entry in request[key]:
                list_of_duplicates.append(database.insert(table_name='tobaccos',
                                values=f'("{key}",'
                                       f' "{entry.get('flavour', 'unknown')}",'
                                       f' "{entry.get('aroma', 'unknown')}",'
                                       f' {TOBACCO_POTENCY.get(key, 0)})',
                                fields='mark, aroma, flavour, potency'))

    return list_of_duplicates

def get_tobacco_from_db():
    with DatabaseExecutor(DATABASE_NAME) as database:
        return database.fetchmany('tobaccos')

def get_tobacco_from_db_by_mark(mark):
    with DatabaseExecutor(DATABASE_NAME) as database:
        return database.fetchmany('tobaccos', where=f'"mark" = "{mark}"')
