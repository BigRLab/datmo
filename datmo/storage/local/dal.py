from kids.cache import cache
from datetime import datetime

from datmo.util.i18n import get as _
from datmo.entity.model import Model
from datmo.entity.session import Session
from datmo.entity.code import Code
from datmo.entity.environment import Environment
from datmo.entity.file_collection import FileCollection
from datmo.entity.task import Task
from datmo.entity.snapshot import Snapshot
from datmo.entity.user import User
from datmo.util.exceptions import InputException


class LocalDAL():
    """
    LocalDAL is a local DAL object that stores info locally. DAL stands for 'data access layer' and serves as a storage for
    all entities.

    Attributes
    ----------
    driver : DALDriver
        DAL driver which determines the backend used for entity storage
    model
    code
    environment
    file_collection
    session
    task
    snapshot
    user

    """
    def __init__(self, driver):
        self.driver = driver

    @cache
    @property
    def model(self):
        """
        Model CRUD methods

        Returns
        -------
        ModelMethods
            Specific set of CRUD functions for model

        """
        return  ModelMethods(self.driver)

    @cache
    @property
    def code(self):
        """
        Code CRUD methods

        Returns
        -------
        CodeMethods
            Specific set of CRUD functions for code

        """
        return CodeMethods(self.driver)

    @cache
    @property
    def environment(self):
        """
        Environment CRUD methods

        Returns
        -------
        EnvironmentMethods
            Specific set of CRUD functions for environment

        """
        return EnvironmentMethods(self.driver)

    @cache
    @property
    def file_collection(self):
        """
        FileCollection CRUD methods

        Returns
        -------
        FileCollectionMethods
            Specific set of CRUD functions for file collection

        """
        return FileCollectionMethods(self.driver)

    @cache
    @property
    def session(self):
        """
        Session CRUD methods

        Returns
        -------
        SessionMethods
            Specific set of CRUD functions for session

        """
        return SessionMethods(self.driver)

    @cache
    @property
    def task(self):
        """
        Task CRUD methods

        Returns
        -------
        TaskMethods
            Specific set of CRUD functions for task

        """
        return  TaskMethods(self.driver)

    @cache
    @property
    def snapshot(self):
        """
        Snapshot CRUD methods

        Returns
        -------
        SnapshotMethods
            Specific set of CRUD functions for snapshot

        """
        return  SnapshotMethods(self.driver)

    @cache
    @property
    def user(self):
        """
        User CRUD methods

        Returns
        -------
        UserMethods
            Specific set of CRUD functions for user

        """
        return  UserMethods(self.driver)

class EntityMethodsCRUD(object):
    def __init__(self, collection, entity_class, driver):
        self.collection = collection
        self.entity_class = entity_class
        self.driver = driver

    def get_by_id(self, entity_id):
        obj = self.driver.get(self.collection, entity_id)
        return self.entity_class(obj)

    def create(self, datmo_entity):
        # translate datmo_entity to a standard dictionary (document) to be stored
        if hasattr(datmo_entity,'toDictionary'):
            dict_obj = datmo_entity.toDictionary()
        else:
            dict_obj = datmo_entity
            # set created_at if not present
            dict_obj['created_at'] = dict_obj.get('created_at',
                                                  datetime.now()).utcnow()
        response = self.driver.set(self.collection, dict_obj)
        entity_instance = self.entity_class(response)
        return entity_instance

    def update(self, datmo_entity):
        # translate datmo_entity to a standard dictionary (document) to be stored
        if hasattr(datmo_entity, 'toDictionary'):
            dict_obj = datmo_entity.toDictionary()
        else:
            if 'id' not in list(datmo_entity) or not datmo_entity['id']:
                raise InputException(_("error",
                                       "storage.local.dal.update"))
            # Aggregate original object and new object into dict_obj var
            new_dict_obj = datmo_entity
            original_datmo_entity = self.get_by_id(datmo_entity['id'])
            dict_obj = {}
            for key, value in original_datmo_entity.toDictionary().items():
                if key in list(new_dict_obj):
                    dict_obj[key] = new_dict_obj[key]
                else:
                    dict_obj[key] = getattr(original_datmo_entity, key)

            # set updated_at if not present
            dict_obj['updated_at'] = datmo_entity.get('updated_at',
                                                      datetime.now()).utcnow()
        response = self.driver.set(self.collection, dict_obj)
        entity_instance = self.entity_class(response)
        return entity_instance

    def delete(self, entity_id):
        return self.driver.delete(self.collection, entity_id)

    def query(self, query_params):
        return [self.entity_class(item) for item in
                self.driver.query(self.collection, query_params)]

#
# https://stackoverflow.com/questions/1713038/super-fails-with-error-typeerror-argument-1-must-be-type-not-classobj
#

#
# Datmo Entity methods
#
class ModelMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(ModelMethods, self).__init__(
            'model',
            Model,
            driver)

class CodeMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(CodeMethods, self).__init__(
            'code',
            Code,
            driver)

class EnvironmentMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(EnvironmentMethods, self).__init__(
            'environment',
            Environment,
            driver)

class FileCollectionMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(FileCollectionMethods, self).__init__(
            'file_collection',
            FileCollection,
            driver)

class SessionMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(SessionMethods, self).__init__(
            'session',
            Session,
            driver)

class TaskMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(TaskMethods, self).__init__(
            'task',
            Task,
            driver
        )

class SnapshotMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(SnapshotMethods, self).__init__(
            'snapshot',
            Snapshot,
            driver)

class UserMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(UserMethods, self).__init__(
            'user',
            User,
            driver)