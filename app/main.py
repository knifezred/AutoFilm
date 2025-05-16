from asyncio import get_event_loop
from sys import path
from os.path import dirname
from datetime import datetime

path.append(dirname(dirname(__file__)))

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type:ignore
from apscheduler.triggers.cron import CronTrigger  # type:ignore

from app.core import settings, logger
from app.extensions import LOGO
from app.modules import Alist2Strm, Ani2Alist


def print_logo() -> None:
    """
    打印 Logo
    """

    print(LOGO)
    print(f" {settings.APP_NAME} {settings.APP_VERSION} ".center(65, "="))
    print("")


if __name__ == "__main__":
    print_logo()

    logger.info(f"AutoFilm {settings.APP_VERSION} 启动中...")
    logger.debug(f"是否开启 DEBUG 模式: {settings.DEBUG}")

    scheduler = AsyncIOScheduler()

    if settings.AlistServerList:
        logger.info("检测到 Alist2Strm 模块配置，正在添加至后台任务")
        for server in settings.AlistServerList:
            cron = server.get("cron")
            if cron:
                # 创建 CronTrigger 对象
                cornTrigger = CronTrigger.from_crontab(cron)
                scheduler.add_job(Alist2Strm(**server).run, trigger=cornTrigger)
                # 获取下一次运行时间（基于当前时间）
                next_time = cornTrigger.get_next_fire_time(None, datetime.now())
                logger.info(f"{server['id']} 已被添加至后台任务。下次运行时间：{next_time}")
            else:
                logger.warning(f"{server['id']} 未设置 cron")
    else:
        logger.warning("未检测到 Alist2Strm 模块配置")

    if settings.Ani2AlistList:
        logger.info("检测到 Ani2Alist 模块配置，正在添加至后台任务")
        for server in settings.Ani2AlistList:
            cron = server.get("cron")
            if cron:
                scheduler.add_job(
                    Ani2Alist(**server).run, trigger=CronTrigger.from_crontab(cron)
                )
                logger.info(f"{server['id']} 已被添加至后台任务")
            else:
                logger.warning(f"{server['id']} 未设置 cron")
    else:
        logger.warning("未检测到 Ani2Alist 模块配置")

    scheduler.start()
    logger.info("AutoFilm 启动完成")

    try:
        get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("AutoFilm 程序退出！")
