from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, create_engine, text
from sqlalchemy.orm import sessionmaker
from db.models.marketplace import History

class Database:
    def __init__(self,database, user='root',passwd='',host='192.168.99.114',port=35432, type="postgresql", connector="psycopg"):
        uri = f'{type}+{connector}://{user}:{passwd}@{host}:{port}/{database}'
        self.engine = create_engine(uri)
        self.session = sessionmaker(bind=self.engine)()

    def doQuery(self, query):
        with self.session.begin():
            result = self.session.execute(text(query)).fetchall()
            if result:
                for row in result:
                    salesorderid = row[0]
                    # Verificar si existe algún registro con lastmodified no siendo None para el salesorderid dado
                    existing_record = self.session.query(History).filter(
                        and_(
                            History.lastmodified.is_(None),
                            History.created > (datetime.now(timezone.utc) - timedelta(days=7)),
                            History.salesorderid == salesorderid
                        )
                    ).first()

                    if not existing_record:
                        # Si no existe un registro con lastmodified no siendo None para este salesorderid, crear uno nuevo
                        new_record = History(salesorderid=salesorderid)
                        self.session.add(new_record)

                self.session.commit()
                self.session.commit()