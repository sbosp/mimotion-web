import app.utils.mi_motion2 as mitask


def run(task_value: dict):
    '''{
                'mi_user': mi_user,
                'mi_password': mi_password,
                'min_step': 100,
                'max_step': 200,
            }
            '''
    mi_motion = mitask.MiMotion(check_item=task_value)
    message, login_token, userid, app_token, status, cache = mi_motion.main()
    if status:
        task_value['login_token'] = login_token or ''
        task_value['userid'] = userid or ''
        task_value['app_token'] = app_token or ''
    task_value['cache'] = cache or False
    return task_value, status, message, mi_motion.step_count


if __name__ == "__main__":
    print(run({
        'mi_user': '3379174616@qq.com',
        'mi_password': 'qq123456',
        'min_step': 6666,
        'max_step': 7777,
    }))
