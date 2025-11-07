import app.utils.mi_motion as mitask
import app.utils.mi_motion2 as mitask2


def run(task_value: dict):
    message, login_token, userid, app_token, status, cache, step_count = mitask.MiMotionRunner(
        task_value).login_and_post_step()
    if not status:
        message, login_token, userid, app_token, status, cache, step_count = mitask2.MiMotion(
            check_item=task_value).main()

    print(message, status, step_count, cache, userid, app_token, login_token, )
    task_value['login_token'] = login_token or ''
    task_value['userid'] = userid or ''
    task_value['app_token'] = app_token or ''
    task_value['cache'] = cache or False
    return task_value, status, message, step_count


if __name__ == "__main__":
    print(run({
        'mi_user': '3379174616@qq.com',
        'mi_password': 'qq123456',
        'min_step': 6666,
        'max_step': 7777,
    }))
