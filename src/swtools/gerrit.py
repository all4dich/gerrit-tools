import urllib
import json
import requests
import logging
from requests.auth import HTTPBasicAuth

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s%(levelname)10s:%(filename)15s:%(lineno)4d:%(funcName)10s: %(message)s')
ch = logging.StreamHandler()
#ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


class Gerrit:
    def __init__(self,root_url, user, password, gerrit_version="2.13.8"):
        self.root_url = root_url
        self.username = user
        self.password = password
        self.version = gerrit_version
        self.api_root_url = self.root_url + "a/"
        self.api_prj_url = self.api_root_url + "projects/"
        self.api_grp_url = self.api_root_url + "groups/"
        self.gerrit_res_prefix = ")]}'\n"

    def print_info(self):
        logger.info(self.root_url)
        logger.info(self.username)
        logger.info(self.password)
        logger.info(self.api_prj_url)
        logger.info(self.api_grp_url)

    def get_group_info(self, owner_id):
        group_url = self.api_grp_url + owner_id
        group_req = requests.get(url=group_url, auth=HTTPBasicAuth(self.username, self.password))
        grp_info = json.loads(group_req.text.replace(self.gerrit_res_prefix, ""))
        return grp_info

    def get_project_owners(self, prj_name):
        owners_info = {}
        prj_name_quoted = urllib.parse.quote(prj_name, safe="")
        prj_access_url = self.api_prj_url + prj_name_quoted+ "/access"
        prj_access_req = requests.get(url=prj_access_url, auth=HTTPBasicAuth(self.username, self.password))
        prj_access_req.close()
        prj_access_info = json.loads(prj_access_req.text.replace(self.gerrit_res_prefix, ""))
        owner_of = prj_access_info["owner_of"]
        for owner_refspec in owner_of:
            owners_info[owner_refspec] = []
            owners = prj_access_info["local"]["refs/*"]["permissions"]["owner"]["rules"]
            for owner_id in owners:
                owner_info = self.get_group_info(owner_id)
                owners_info[owner_refspec].append(owner_info)
        return owners_info


if __name__ == "__main__":
    gerrit_url = input("Gerrit Url: ")
    user_account = input("User account: ")
    user_password = input("User Password: ")
    g = Gerrit(gerrit_url, user_account, user_password)
    owners = g.get_project_owners("webos-pro/audiod")
    logger.warning("\n{}".format(owners))
