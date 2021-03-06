from datetime import datetime

import requests
# Data may have too many rows, and we may want to limit the imported rows for migration
# Give import limit as -1, not to limit the rows to be imported
from requests import Response


def import_house_items(apps, schema_editor, import_limit: int, bulk_commit_size: int, file_url: str):
    """
    Method for importing houses during the migration process
    :param apps: apps container
    :param schema_editor: schema editor instance
    :param import_limit: row limit for import, -1 for limitless import(can be used during development)
    :param file_url: url to import data from
    :return: None
    """
    if import_limit != -1:
        print("Importing limited count of rows:", import_limit)
    HousePersistenceModel = apps.get_model("server_app_api", "HousePersistenceModel")
    req: Response = requests.get(file_url, stream=True)
    total_record_count: int = 0

    bulk_elements: list[HousePersistenceModel] = []
    for chunk in req.iter_lines():
        # writing one chunk at a time to db
        if chunk:
            data: str = chunk.decode("utf-8")
            fields: [str] = data.replace("\"", "").split(",")
            bulk_elements.append(HousePersistenceModel(house_uuid=fields[0].replace("{", "").replace("}", ""),
                                                       postal_code=fields[3],
                                                       primary_addressable_object_name=fields[8],
                                                       secondary_addressable_object_name=fields[10],
                                                       sell_price=int(fields[1]),
                                                       sell_date=datetime.strptime(fields[2], "%Y-%m-%d %H:%M"),
                                                       address_street=fields[9],
                                                       address_locality=fields[10],
                                                       address_town=fields[11],
                                                       address_county=fields[12],
                                                       address_city=fields[13],
                                                       house_type=fields[4],
                                                       ))
            total_record_count = total_record_count + 1
            if total_record_count % bulk_commit_size == 0:
                HousePersistenceModel.objects.bulk_create(bulk_elements)
                bulk_elements = []
                print("Importing row:", total_record_count)
                if import_limit != -1 and total_record_count > import_limit:
                    break
    # import trailing bulk
    HousePersistenceModel.objects.bulk_create(bulk_elements)
