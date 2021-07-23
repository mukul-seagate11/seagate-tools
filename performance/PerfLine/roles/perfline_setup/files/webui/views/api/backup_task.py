# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

import os
import sys
import yaml
from os.path import isdir, join
from flask import request, make_response

from app_global_data import *


@app.route('/api/task/backup_tasks/<string:task_id_list>')
def backup_task(task_id_list):

    if len(BACKUP_ARTIFACTS_DIRS) == 0:
        err_resp = {"status": "failed",
                    "error_message": "directory for backups was not specified"}

        response = make_response(f'{err_resp}')
        return response


    backup_dir = BACKUP_ARTIFACTS_DIRS[0]

    result = dict()
    result['status'] = 'success'
    result['detailed_status'] = []

    for task_id in task_id_list.split(","):

        if not task_id:
            continue


        task_status = dict()
        result['detailed_status'].append(task_status)
        task_status['task_id'] = task_id

        if not cache.has(task_id):
            task_status['status'] = 'failed'
            task_status['error_message'] = f'task does not exist'
            result['status'] = 'failed'
        else:

            task_location = cache.get_location(task_id)
            

            origin_location = f'{task_location}/result_{task_id}'
            tmp_location = f'{task_location}/moving_{task_id}'
            new_location = f'{backup_dir}/result_{task_id}'

            os.rename(origin_location, tmp_location)

            async_worker.move_dir_async(origin_location, tmp_location, new_location)
            task_status['status'] = 'success'

    cache.update(all_artif_dirs, force = True)
    response = make_response(f'{result}')
    return response