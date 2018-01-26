import urllib
import json
import requests
import logging
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s%(levelname)10s:%(filename)15s:%(lineno)4d:%(funcName)10s: %(message)s')
ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


class Gerrit:
    def __init__(self, root_url, user, password):
        self.root_url = root_url
        self.username = user
        self.password = password
        self.api_root_url = self.root_url + "a/"
        self.api_prj_url = self.api_root_url + "projects/"
        self.api_grp_url = self.api_root_url + "groups/"
        self.gerrit_res_prefix = ")]}'\n"
        # Get Gerrit's version and check if Gerrit use HTTP "Basic" or "Digest" auth.
        get_ver_url = self.api_root_url + "config/server/version"
        get_ver_req_basic = requests.get(url=get_ver_url, auth=HTTPBasicAuth(user, password))
        get_ver_req_basic.close()
        if get_ver_req_basic.status_code != 200:
            get_ver_req_digest = requests.get(url=get_ver_url, auth=HTTPDigestAuth(user, password))
            get_ver_req_digest.close()
            if get_ver_req_digest.status_code != 200:
                raise ConnectionError("Wrong username or password:")
            else:
                self.AUTHMethod = HTTPDigestAuth
                self.version = get_ver_req_digest.text.replace(self.gerrit_res_prefix, "")
        else:
            self.AUTHMethod = HTTPBasicAuth
            self.version = get_ver_req_basic.text.replace(self.gerrit_res_prefix, "")
        logger.warning("Gerrit version: " + self.version)

    def print_info(self):
        logger.info(self.root_url)
        logger.info(self.username)
        logger.info(self.password)
        logger.info(self.api_prj_url)
        logger.info(self.api_grp_url)

    def get_group_info(self, owner_id, api_suffix=""):
        # API Link: https://gerrit-documentation.storage.googleapis.com/Documentation/2.13.9/rest-api-groups.html#get-group
        # API URI: 'GET /groups/{group-id}'
        group_url = self.api_grp_url + owner_id + api_suffix
        group_req = requests.get(url=group_url, auth=self.AUTHMethod(self.username, self.password))
        grp_info = json.loads(group_req.text.replace(self.gerrit_res_prefix, ""))
        return grp_info

    def get_project_owners(self, prj_name):
        # API Link: https://gerrit-documentation.storage.googleapis.com/Documentation/2.13.9/rest-api-projects.html#get-access
        # API URI: 'GET /projects/{project-name}/access'
        owners_info = {}
        prj_name_quoted = urllib.parse.quote(prj_name, safe="")
        prj_access_url = self.api_prj_url + prj_name_quoted + "/access"
        prj_access_req = requests.get(url=prj_access_url, auth=self.AUTHMethod(self.username, self.password))
        prj_access_req.close()
        try:
            prj_access_info = json.loads(prj_access_req.text.replace(self.gerrit_res_prefix, ""))
        except:
            logger.warning(prj_access_req.status_code)
            logger.warning(prj_access_req.text)
            return
        # "owner_of"
        #  - This field has all refspec defined in project access configuration
        #    regardless of having 'owner' permission configuration.
        #  - If there is no access configuration on web UI, "owner_of" only has "refs/*" value
        owner_of = prj_access_info["owner_of"]
        logger.debug("Owner of: {}".format(owner_of))
        for owner_refspec in owner_of:
            try:
                # Check if having 'owner' permission or not
                owners = prj_access_info["local"][owner_refspec]["permissions"]["owner"]["rules"]
            except KeyError:
                logger.error("There is no owner information in {}' refspec {}".format(prj_name, owner_refspec))
                continue
            owners_info[owner_refspec] = []
            for owner_id in owners:
                owner_info = self.get_group_info(owner_id)
                owners_info[owner_refspec].append(owner_info)
        return owners_info

    def get_members_from_group(self, grp_id, api_suffix=""):
        # API Link: https://gerrit-documentation.storage.googleapis.com/Documentation/2.13.9/rest-api-groups.html#group-members
        # API URI: 'GET /groups/{group-id}/members/'
        # If you get all included members, set api_suffix as ="?recursive"
        members_info = self.get_group_info(grp_id, api_suffix="/members/" + api_suffix)
        return members_info

    def add_member_to_group(self, grp_id, user_info):
        # API Link: https://gerrit-documentation.storage.googleapis.com/Documentation/2.13.9/rest-api-groups.html#group-members
        # API URI: 'GET /groups/{group-id}/members/'
        # If you get all included members, set api_suffix as ="?recursive"
        members_input = { "members": user_info }
        add_members_url = self.api_grp_url + grp_id + "/members/"
        res = add_members_req  = requests.post(url=add_members_url, auth=self.AUTHMethod(self.username, self.password), json=members_input)
        return json.loads(res.text.replace(self.gerrit_res_prefix, ""))


if __name__ == "__main__":
    gerrit_url = input("Gerrit Url: ")
    user_account = input("User account: ")
    user_password = input("User Password: ")
    project_name = input("Project name: ")
    g = Gerrit(gerrit_url, user_account, user_password)
    owners = g.get_project_owners(project_name)
    logger.warning("\n{}".format(owners))
