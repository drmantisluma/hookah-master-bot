from constants import DATABASE_NAME
from src.hookah_master_helper.database.database import DatabaseExecutor


def add_tobacco_to_database(request):
    with DatabaseExecutor(DATABASE_NAME) as database:
        return database.insert(table_name='tobaccos',
                               values=(request.get('brand').lower(),
                                       request.get('flavour', 'unknown').lower(),
                                       request.get('taste', 'unknown').lower()),
                               fields=('brand', 'aroma', 'taste'))

def get_tobacco_from_db():
    with DatabaseExecutor(DATABASE_NAME) as database:
        return database.fetchmany('tobaccos')

def get_all_brands():
    with DatabaseExecutor(DATABASE_NAME) as database:
        data = database.fetchall(table_name='tobaccos', fields='brand', distinct=True)
        return [row[0] for row in data]
