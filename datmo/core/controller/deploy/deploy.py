import os
import tempfile
import shutil

from datmo.core.controller.base import BaseController
from datmo.core.util.misc_functions import Commands
from datmo.core.controller.deploy.driver.datmo_microservice import DatmoMicroserviceDeployDriver
from datmo.config import Config


class DeployController(BaseController):
    """
    A controller for deploying a model

    Parameters
    ----------
    service_container_manager : bool
        representing to use service's container management system

    Methods
    -------
    system_setup()
        Setup the system with provider and their key and secret token
    cluster_deploy(cluster_name=None, server_type=None, size=None)
        Deploy the Servers in the cluster with the defined setup
    cluster_update(cluster_name, size)
        Scale up/down the number of servers in the cluster
    cluster_stop(cluster_name)
        Stop and remove the cluster
    cluster_ls(cluster_name='*')
        List all containers in the cluster
    system_info()
        To return the information about the System and Logging portal
    system_cost()
        To return the information about the cost due to datmo deploy from cloud systems
    model_deploy(cluster_name)
        Deploy the model after building it from the docker compose file
    service_iologs(service_path, date)
        Extract io logs for a particular service
    """

    def __init__(self, service_container_management=False):
        """Initialize the Orchestrator service"""
        super(DeployController, self).__init__()
        self.commands = Commands()
        self.config = Config()
        self.master_server_ip, self.datmo_api_key, self.datmo_end_point = self.config.remote_credentials
        self.service_container_management = service_container_management
        self.driver = DatmoMicroserviceDeployDriver(
            end_point=self.datmo_end_point, api_key=self.datmo_api_key)

    def cluster_deploy(self, cluster_name=None, server_type=None, size=None):
        """
        Deploy the Servers in the cluster with the defined setup
        """
        response = self.driver.create_cluster(
            cluster_name, server_type, count=size)
        return response

    def cluster_update(self, cluster_name, size):
        """
        Scale up/down the number of servers in the cluster

        Parameters
        ----------
        cluster_name : str
            Name of cluster
        size : str
            Number of servers
        """
        response = self.driver.update_cluster(
            count=size, cluster_name=cluster_name)
        return response

    def cluster_stop(self, cluster_name):
        """
        Stop and remove the cluster

        Parameters
        ----------
        cluster_name : str
            name of the cluster
        """
        response = self.driver.update_cluster(
            count=0, cluster_name=cluster_name)
        return response

    def cluster_ls(self, cluster_name='*'):
        """
        List all containers in the cluster

        Parameters
        ----------
        cluster_name : str
            name of the cluster
        """
        response = self.driver.get_cluster_info(cluster_name)
        return response

    def system_info(self):
        """
        To return the information about the System and Logging portal
        """
        response = self.driver.get_system_info()
        return response

    def system_cost(self):
        """
        To return the information about the cost due to datmo deploy from cloud systems
        """
        response = self.driver.get_system_cost()
        return response

    def model_deploy(self, cluster_name):
        """
        Deploy the model after building it from the docker compose file

        Parameters
        ----------
        cluster_name : str
            Name of the cluster
        """
        # Specific for datmo service logic
        tmp_dirpath = tempfile.mkdtemp()
        # copy the content for project directory to tmp folder and the environment to root location in tmp folder
        try:
            self.commands.copy(self.home, tmp_dirpath)
            environment_dirpath = os.path.join(tmp_dirpath,
                                               'datmo_environment')
            if os.path.exists(environment_dirpath):
                shutil.rmtree(os.path.join(tmp_dirpath, '.datmo'))
                self.commands.copy(environment_dirpath, tmp_dirpath)
                shutil.rmtree(os.path.join(tmp_dirpath, 'datmo_environment'))
                shutil.rmtree(os.path.join(tmp_dirpath, 'datmo_files'))
                list_dir = os.listdir(tmp_dirpath)

                for item in list_dir:
                    if item.endswith(".zip") or item.endswith(".csv"):
                        os.remove(os.path.join(tmp_dirpath, item))
        except Exception as e:
            print(e)

        model_zipfile_path = os.path.join(tmp_dirpath, 'datmo_model.zip')
        self.commands.zip_folder(tmp_dirpath, model_zipfile_path)
        response = self.driver.model_deploy(cluster_name, model_zipfile_path)
        # remove the temp directory
        shutil.rmtree(tmp_dirpath)
        return response

    def service_iologs(self, service_path, date):
        """
        Extract io logs for a particular service

        Parameters
        ----------
        service_path : str
            service route for the algorithm
        date : str
            Date for which you want to get the logs
        """
        response = self.driver.get_service_iologs(service_path, date)
        return response
